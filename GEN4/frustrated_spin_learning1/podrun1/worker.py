import sys,time,resource
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P),str(P.parent),str(P.parent/'runtime')]
from operations import Followup,load,save,sha
from SAM_PROJECT.session import DomainSession
q=load(sys.argv[1]);out=Path(sys.argv[2]);assert all(sha(P.parent/f)==h for f,h in q['inputs_hashes'].items())
resource.setrlimit(resource.RLIMIT_CPU,(900,910));
if q['kind']!='gpu_test':resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
t=time.monotonic()
with DomainSession.start('MATTER_SEARCH',objective=q['question'],output_root=out/'sessions',receipt_storage='gzip') as s:
 s.consumer=Followup(s.consumer);save(out/'RUNTIME.json',dict(announcement=s.announcement(),session=str(s.directory)))
 r=s.execute('GEN4_SPIN_FOLLOWUP1',dict(code_sha256=sha(P/'operations.py'),question=q),purpose=q['question']);cp=s.execute('GEN3_CHECKPOINT',{},purpose='Retain follow-up exact results and learned evidence')
 save(out/'RESULT.json',dict(value=r,seconds=time.monotonic()-t,session=str(s.directory),checkpoint=cp,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
