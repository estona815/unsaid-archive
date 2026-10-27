'use strict';
const $=id=>document.getElementById(id);
let letters=[];
const ready=fetch('/letters').then(r=>{if(!r.ok)throw Error('Could not load the archive');return r.json()}).then(x=>letters=x);
function showSource(match,button){
 for(const b of document.querySelectorAll('.match'))b.setAttribute('aria-pressed',String(b===button));
 const doc=letters.find(d=>d.id===match.document);
 $('source-id').textContent=match.document;
 const mark=document.createElement('mark');
 // Python offsets count Unicode code points, as does Array.from in JavaScript.
 const chars=Array.from(doc.text);
 mark.textContent=chars.slice(match.start,match.end).join('');
 $('source-text').replaceChildren(document.createTextNode(chars.slice(0,match.start).join('')),mark,document.createTextNode(chars.slice(match.end).join('')));
 $('provenance').textContent=`Source characters ${match.start}–${match.end}. SHA-256 ${match.source_sha256}`;
}
async function search(event){
 event?.preventDefault();if($('submit').disabled)return;
 $('submit').disabled=true;$('status').textContent='Reading the archive locally…';$('matches').replaceChildren();$('source-text').replaceChildren();$('source-id').textContent='Select a passage to see its context.';$('provenance').textContent='';
 try{
  await ready;
  const r=await fetch('/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:$('query').value})});
  const data=await r.json();if(!r.ok)throw Error(data.error||'Search failed');
  $('status').textContent=data.status==='no_close_match'?'No close match at the provisional threshold. These are the nearest passages; they may not answer your question.':'Related passages found. Read the source before drawing a conclusion.';
  for(const [i,m] of data.matches.entries()){
   const b=document.createElement('button');b.className='match';b.type='button';b.setAttribute('aria-pressed','false');
   const meta=document.createElement('span');meta.className='meta';meta.textContent=`${i+1} · ${m.document} · cosine similarity ${m.score.toFixed(3)}`;
   const quote=document.createElement('blockquote');quote.textContent=m.quote;
   b.append(meta,quote);b.addEventListener('click',()=>showSource(m,b));$('matches').append(b);
   if(i===0)showSource(m,b);
  }
 }catch(error){$('status').textContent=error.message;}finally{$('submit').disabled=false;}
}
$('search').addEventListener('submit',search);
for(const b of document.querySelectorAll('[data-query]'))b.addEventListener('click',()=>{if($('submit').disabled)return;$('query').value=b.dataset.query;search();});
