async function doSearch(){
  const q = document.getElementById('query').value;
  const lang = document.getElementById('lang').value;
  const resDiv = document.getElementById('results');
  resDiv.innerHTML = '<p>Searching...</p>';
  const resp = await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q,lang:lang})});
  const j = await resp.json();
  if(!j.results || j.results.length===0){ resDiv.innerHTML='<p>No results found.</p>'; return; }
  resDiv.innerHTML='';
  j.results.forEach(r=>{
    const el = document.createElement('div'); el.className='card';
    el.innerHTML = `<h3>${r.title} <small style="color:#666">(${r.act} ${r.section||''})</small></h3>
                    <p>${r.summary || r.summary_en || ''}</p>
                    <p style="font-size:12px;color:#666">Score: ${r.score.toFixed(3)}</p>`;
    resDiv.appendChild(el);
  });
}
document.getElementById('searchBtn').addEventListener('click', doSearch);
document.getElementById('query').addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); doSearch(); } });
