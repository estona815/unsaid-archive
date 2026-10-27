import { searchArchive } from './search.js';
const $=id=>document.getElementById(id);
let letters=[];
let ready=fetch('./fictional-letters.json').then(r=>{if(!r.ok)throw Error('Could not load the archive');return r.json()}).then(x=>letters=x);
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
 $('submit').disabled=true;$('query').disabled=true;$('file').disabled=true;$('reset').disabled=true;$('status').textContent='Reading the archive locally…';$('matches').replaceChildren();$('source-text').replaceChildren();$('source-id').textContent='Select a passage to see its context.';$('provenance').textContent='';
 try{
  await ready;
  const data=await searchArchive(letters,$('query').value, message=>{$('status').textContent=message;});
  $('status').textContent=data.status==='no_close_match'?'No close match at the provisional threshold. These are the nearest passages; they may not answer your question.':'Related passages found. Read the source before drawing a conclusion.';
  for(const [i,m] of data.matches.entries()){
   const b=document.createElement('button');b.className='match';b.type='button';b.setAttribute('aria-pressed','false');
   const meta=document.createElement('span');meta.className='meta';meta.textContent=`${i+1} · ${m.document} · cosine similarity ${m.score.toFixed(3)}`;
   const quote=document.createElement('blockquote');quote.textContent=m.quote;
   b.append(meta,quote);b.addEventListener('click',()=>showSource(m,b));$('matches').append(b);
   if(i===0)showSource(m,b);
  }
 }catch(error){$('status').textContent=error.message;}finally{$('submit').disabled=false;$('query').disabled=false;$('file').disabled=false;$('reset').disabled=false;}
}
$('search').addEventListener('submit',search);
for(const b of document.querySelectorAll('[data-query]'))b.addEventListener('click',()=>{if($('submit').disabled)return;$('query').value=b.dataset.query;search();});

function clearResults(){
 $('matches').replaceChildren();$('source-text').replaceChildren();$('provenance').textContent='';$('source-id').textContent='Select a passage to see its context.';
}
$('file').addEventListener('change',async()=>{
 if($('submit').disabled){$('file').value='';return;}
 const file=$('file').files[0];if(!file)return;
 clearResults();
 try{
  if(file.size>20000)throw Error('Choose a text file no larger than 20 KB.');
  const text=await file.text();
  if(!text.trim())throw Error('The text file is empty.');
  if(text.split('\n').filter(x=>x.trim()).length>200)throw Error('Use at most 200 nonempty lines.');
  letters=[{id:file.name,text}];ready=Promise.resolve();
  $('archive-label').textContent=`Reading ${file.name} on this device. The text is not uploaded. The example questions still refer to the fictional letters.`;
  $('status').textContent='Text loaded. Search to build its local index.';
 }catch(e){$('status').textContent=e.message;}
});
$('reset').addEventListener('click',async()=>{
 if($('submit').disabled)return;
 clearResults();$('file').value='';
 ready=fetch('./fictional-letters.json').then(r=>r.json()).then(x=>letters=x);await ready;
 $('archive-label').textContent='Reading three fictional letters. Each nonempty line becomes a passage.';
 $('status').textContent='Fictional letters restored. Search again.';
});

$('query').addEventListener('input',()=>{clearResults();$('status').textContent='Question changed. Search again to see matching passages.';});
