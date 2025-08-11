# Seed the SQLite DB with example laws and summaries.
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'laws.db')
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
s = Session()

examples = [
    {
        'title':'Unpaid Salary / Wages',
        'section':'Various',
        'act':'Payment of Wages Act / Industrial Disputes Act',
        'text':'Employer not paying salary for months. Remedies include complaint to labour commissioner, conciliation, and claim under Industrial Disputes Act.',
        'summary_en':'If your employer has not paid salary, you can file a complaint with the Labour Commissioner, collect pay slips and bank statements, and approach labour court or labour commissioner for recovery. Consider statutory claims under Payment of Wages Act and Industrial Disputes Act.',
        'summary_hi':'यदि नियोक्ता वेतन नहीं दे रहा है, तो आप श्रम आयुक्त को शिकायत दर्ज कर सकते हैं...',
        'summary_mr':'जर नोकरीदार पगार देत नसेल तर तुम्ही श्रम आयुक्त कडे तक्रार करू शकता...'
    },
    {
        'title':'Landlord not returning deposit',
        'section':'Rent/Tenancy',
        'act':'Rent Control / Agreement Law',
        'text':'Landlord refuses to return security deposit after tenancy ends. Possible remedies: demand notice, consumer forum, civil suit for recovery.',
        'summary_en':'If landlord refuses to return deposit, serve a written demand, keep records, and file a claim in consumer court or civil suit for recovery. Check local rent control laws for caps on security deposit.',
        'summary_hi':'यदि मकानमालिक जमा राशि वापस नहीं कर रहा है, तो लिखित नोटिस दें...',
        'summary_mr':'जर भाडेकरूचा ठेवीचा पैसा परत नसेल तर लेखी मागणी करा...'
    },
    {
        'title':'Consumer product defect / refund',
        'section':'Consumer Protection',
        'act':'Consumer Protection Act',
        'text':'Defective product or service; seller refuses refund/replacement. Remedies include complaint to consumer forum with invoice, warranty, and communication record.',
        'summary_en':'For defective goods, approach the seller first, then file complaint in the Consumer Forum with invoice, warranty, and proof of defect. You can claim replacement, refund, or compensation.',
        'summary_hi':'खराब उत्पाद मिलने पर पहले विक्रेता से संपर्क करें...',
        'summary_mr':'खराब वस्तू मिळाल्यास विक्रेत्याशी संपर्क करा...'
    },
    {
        'title':'Domestic violence / protection',
        'section':'Family Law',
        'act':'Protection of Women from Domestic Violence Act, 2005',
        'text':'Physical, emotional or economic abuse by a partner or family member. Remedies include protection orders, maintenance, and police complaint.',
        'summary_en':'If facing domestic violence, you can approach the police, file for protection orders and maintenance under the Domestic Violence Act, and seek shelter services. Keep records and medical reports.',
        'summary_hi':'घरेलू हिंसा का सामना कर रहे हैं तो पुलिस से संपर्क करें...',
        'summary_mr':'घरेलू हिंसेला सामोरे जात असाल तर पोलिसांना कळवा...'
    },
    {
        'title':'FIR / Criminal complaint basics',
        'section':'Criminal Procedure',
        'act':'Indian Penal Code / CrPC (overview)',
        'text':'How to file FIR, evidence collection, and victims rights. If police refuses, file complaint with higher officer or approach magistrate for directions.',
        'summary_en':'To file an FIR, go to the police station and provide a written complaint. Keep a copy of the FIR. If police refuse, approach the Superintendent of Police or file a private complaint before a magistrate.',
        'summary_hi':'एफआईआर दर्ज कराने के लिए थाने जाएं...',
        'summary_mr':'एफआयआर नोंदवण्यासाठी स्थानकाला जा...'
    }
]

for ex in examples:
    law = Law(title=ex['title'], section=ex['section'], act=ex['act'], text=ex['text'], summary_en=ex['summary_en'], summary_hi=ex['summary_hi'], summary_mr=ex['summary_mr'])
    s.add(law)
s.commit()
print('Seeded DB with example laws.')        
