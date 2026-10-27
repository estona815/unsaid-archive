let extractor, entries, vectors, documentKey;
async function encode(texts){
 for(const text of texts){
  const tokens=await extractor.tokenizer(text,{truncation:false,padding:false});
  if(tokens.input_ids.size>256)throw Error('Split long questions or source lines: maximum 256 model tokens.');
 }
 const output=await extractor(texts,{pooling:'mean',normalize:true});
 return output.tolist();
}
export async function searchArchive(documents,query,progress=()=>{}){
 if(typeof query!=='string'||!query.trim())throw Error('Enter a question.');
 if(query.length>1200)throw Error('Please shorten the question to 1200 characters.');
 if(!extractor){
  progress('Loading MiniLM in your browser… The first download can take a minute.');
  const {pipeline,env}=await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2');
  env.allowLocalModels=false;
  env.backends.onnx.wasm.numThreads=1;
  extractor=await pipeline('feature-extraction','Xenova/all-MiniLM-L6-v2',{quantized:true});
 }
 const key=JSON.stringify(documents);
 if(!entries||key!==documentKey){
  progress('Indexing the fictional letters locally…');
  const pending=[];
  for(const d of documents){
   const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(d.text));
   const sha=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
   for(const m of d.text.matchAll(/[^\n]+/g))if(m[0].trim()){
    const start=Array.from(d.text.slice(0,m.index)).length;
    pending.push({document:d.id,start,end:start+Array.from(m[0]).length,quote:m[0],source_sha256:sha});
   }
  }
  const encoded=await encode(pending.map(p=>p.quote));
  vectors=encoded;entries=pending;documentKey=key;
 }
 progress('Comparing the question with source passages…');
 const [q]=await encode([query]);
 const matches=entries.map((item,i)=>({...item,score:q.reduce((sum,v,j)=>sum+v*vectors[i][j],0)})).sort((a,b)=>b.score-a.score).slice(0,3);
 return {status:matches[0].score>=.4?'related_passages':'no_close_match',matches,model:'Xenova/all-MiniLM-L6-v2',threshold:.4};
}
