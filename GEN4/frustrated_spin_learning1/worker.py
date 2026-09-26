import sys,json,time,resource,os
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P/'runtime'))
from research import Research,sha,save,load
from SAM_PROJECT.session import DomainSession
q=load(sys.argv[1]);out=Path(sys.argv[2]);t=time.monotonic();cpu=time.process_time()
assert all(sha(P/f)==h for f,h in q.get('inputs_hashes',{}).items())
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(130,135))
with DomainSession.start('MATTER_SEARCH',objective=q['question'],output_root=out/'sessions',receipt_storage='gzip') as s:
 s.consumer=Research(s.consumer)
 save(out/'RUNTIME.json',dict(announcement=s.announcement(),session=str(s.directory),manifest=s.manifest))
 value=s.execute('GEN4_FRUSTRATED_LEARN1',dict(code_sha256=sha(P/'research.py'),question=q),purpose=q['question'])
 check=s.execute('GEN3_CHECKPOINT',{},purpose='Retain completed learning experiment and native state')
 save(out/'RESULT.json',dict(question_id=q['question_id'],value=value,seconds=time.monotonic()-t,session=str(s.directory),checkpoint=check,cpu_seconds=time.process_time()-cpu,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_hashes_verified=True))
