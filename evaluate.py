import argparse,json,socket,time
from pathlib import Path
from archive import Archive

def denied(*args,**kwargs): raise RuntimeError('Network disabled during evaluation')
socket.socket.connect=denied
p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--output',required=True);args=p.parse_args()
a=Archive(json.loads(Path(__file__).with_name('fictional-letters.json').read_text()),args.cache)
cases=[('How did she wait for someone to come home?','invented-letter-01'),('Keeping a light on and reheating dinner while waiting','invented-letter-01'),('What happened after losing a job?','invented-letter-02'),('How was music remembered after moving house?','invented-letter-03'),('What was the bank account password?',None),('What were her last words?',None)]
rows=[]
for query,expected in cases:
 start=time.monotonic();r=a.search(query)
 rows.append({'expected_document':expected,'latency_seconds':time.monotonic()-start,'result':r})
report={'network_connect_blocked':True,'model_revision':a.revision,'fixture':'Fictional development cases; not independent evaluation','cases':rows,'limitations':'Threshold 0.4 is not calibrated; retrieval is not entailment or absence detection.'}
with Path(args.output).open('x') as f:json.dump(report,f,indent=2)
for row in rows:print(row['result']['query'],row['result']['status'],row['result']['matches'][0]['document'],round(row['result']['matches'][0]['score'],3))
