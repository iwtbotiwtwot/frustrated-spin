import os,sys,time,resource
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P),str(P/'runtime')]
from research import load,save,sha
from blind_engine import Campaign
from SAM_PROJECT.session import DomainSession
q=load(sys.argv[1]);out=Path(sys.argv[2]);assert all(sha(P/k)==v for k,v in q.get('inputs_hashes',{}).items())
# GPU owner children inherit the shared host allocation, not per-GPU CPU quotas.
if q['kind']!='gpu_compare':resource.setrlimit(resource.RLIMIT_AS,(32*1024**3,32*1024**3))
t=time.monotonic()
with DomainSession.start('MATTER_SEARCH',objective=q['question'],output_root=out/'sessions',receipt_storage='gzip') as s:
 s.consumer=Campaign(s.consumer,out);save(out/'RUNTIME.json',dict(announcement=s.announcement(),session=str(s.directory)))
 r=s.execute('GEN4_BLIND_RESEARCH',dict(question=q,code_sha256=sha(P/'blind_engine.py')),purpose=q['question']);cp=s.execute('GEN3_CHECKPOINT',{},purpose='Retain fresh blinded research result and exact receipts')
 save(out/'RESULT.json',dict(value=r,seconds=time.monotonic()-t,checkpoint=cp,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
