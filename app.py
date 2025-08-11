import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np

# Optional OpenAI embeddings
try:
    import openai
except Exception:
    openai = None

# TF-IDF fallback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'laws.db')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

app = Flask(__name__, static_folder='static', template_folder='templates')

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Base = declarative_base()

class Law(Base):
    __tablename__ = 'laws'
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    section = Column(String(100))
    act = Column(String(250))
    text = Column(Text)
    summary_en = Column(Text)
    summary_hi = Column(Text)
    summary_mr = Column(Text)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Helper: load documents
def load_documents():
    docs = session.query(Law).all()
    texts = [ (d.id, (d.title or '') + ' ' + (d.section or '') + ' ' + (d.act or '') + ' ' + (d.text or '') + ' ' + (d.summary_en or '')) for d in docs ]
    return docs, texts

# Build TF-IDF model
def build_tfidf(texts):
    ids = [t[0] for t in texts]
    corpus = [t[1] for t in texts]
    if len(corpus) == 0:
        return None, ids, None
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(corpus)
    return vectorizer, ids, X

vectorizer = None; doc_ids = []; X = None
def refresh_index():
    global vectorizer, doc_ids, X
    docs, texts = load_documents()
    vectorizer, doc_ids, X = build_tfidf(texts)

refresh_index()

def openai_embed(text):
    key = os.getenv('OPENAI_API_KEY')
    if not key or openai is None:
        return None
    try:
        openai.api_key = key
        resp = openai.Embedding.create(model='text-embedding-3-small', input=text)
        emb = resp['data'][0]['embedding']
        return np.array(emb, dtype=float)
    except Exception as e:
        print('OpenAI embed failed:', e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json or {}
    query = data.get('query','').strip()
    lang = data.get('lang','en')
    if not query:
        return jsonify({'error':'query required'}), 400
    # Try OpenAI embeddings first
    q_emb = openai_embed(query)
    docs, texts = load_documents()
    results = []
    if q_emb is not None and len(texts) > 0:
        # get embeddings for docs? We don't store doc embeddings here; fallback to TF-IDF if not present.
        pass
    # TF-IDF fallback
    global vectorizer, doc_ids, X
    if vectorizer is None or X is None:
        refresh_index()
    if vectorizer is None or X is None:
        return jsonify({'results':[]})
    qv = vectorizer.transform([query])
    cosine_similarities = linear_kernel(qv, X).flatten()
    top_idx = np.argsort(-cosine_similarities)[:6]
    for idx in top_idx:
        score = float(cosine_similarities[idx])
        doc_id = doc_ids[idx]
        law = session.query(Law).get(doc_id)
        if not law:
            continue
        summary = law.summary_en
        if lang == 'hi' and law.summary_hi:
            summary = law.summary_hi
        if lang == 'mr' and law.summary_mr:
            summary = law.summary_mr
        results.append({'id':law.id,'title':law.title,'section':law.section,'act':law.act,'score':score,'summary':summary})
    return jsonify({'results':results})

@app.route('/admin', methods=['GET','POST'])
def admin_page():
    from flask import request, render_template, redirect, url_for
    if request.method == 'GET':
        return render_template('admin.html')
    # POST: simple password check
    pw = request.form.get('password','')
    if pw != ADMIN_PASSWORD:
        return render_template('admin.html', error='Invalid password')
    return render_template('admin_panel.html')

@app.route('/admin/add', methods=['POST'])
def admin_add():
    data = request.form or request.json or {}
    pw = data.get('password') or request.form.get('password')
    if pw != ADMIN_PASSWORD:
        return jsonify({'error':'unauthorized'}), 401
    title = data.get('title')
    section = data.get('section')
    act = data.get('act')
    text = data.get('text') or ''
    summary_en = data.get('summary_en') or ''
    summary_hi = data.get('summary_hi') or ''
    summary_mr = data.get('summary_mr') or ''
    law = Law(title=title, section=section, act=act, text=text, summary_en=summary_en, summary_hi=summary_hi, summary_mr=summary_mr)
    session.add(law)
    session.commit()
    refresh_index()
    return jsonify({'ok':True,'id':law.id})

@app.route('/api/law/<int:law_id>')
def get_law(law_id):
    law = session.query(Law).get(law_id)
    if not law:
        return jsonify({'error':'not found'}), 404
    return jsonify({'id':law.id,'title':law.title,'section':law.section,'act':law.act,'text':law.text,'summary_en':law.summary_en})

# Static files
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=True)
