"""Research adapter to the restored original focused/frontier exact engines."""
import os,sys,json,time,math,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent

def execute(base,q):
 from research import canonical,load,compare_answer
 from operations import ports
 sys.path[:0]=['/opt/gen4/spin-focused1','/opt/gen4/spin-training1','/opt/gen4/spin-catalog1']
 from run_fast import Focus
 from arithmetic import templates,IndexCache
 from planning import structure,digest
 import engine
 s=load(ROOT/q['variant'])['source'] if q.get('variant') else canonical(q['N'])['source'];ps=ports(q)
 assert 1<=s['N']<=120
 if q.get('variant'):raise RuntimeError('Variant GPU admission needs a source-specific independent reference; retained for CPU paired verification')
 # Preserve original source binding. Explicit research alternatives are distinct plans.
 selected=q.get('restored_plan')
 if selected is None and not q.get('explicit_cutset'):
  selected=canonical(q['N'])['plan'] if s['N']>96 else base.execute('GEN3_SPIN_PLAN',dict(source=s,previous_N=max(1,s['N']-1)))['plan']
 if selected is None:
  fixed=sorted(set(v for v in q.get('candidate_cutset',[]) if v not in ps));glue=[e for e in s['edges'] if e[0] in ps and e[1] in ps]
  st=structure(s['N'],[e for e in s['edges'] if e not in glue],ps,fixed);bound=s['energy_bound_B']-sum(abs(e[2]) for e in glue);length=1<<bound.bit_length();primes=[];prod=1
  for prime in [998244353,1004535809,469762049,167772161,1224736769]:
   if (prime-1)%(2*length)==0:primes.append(prime);prod*=prime
   if prod>1<<s['N']:break
  assert prod>1<<s['N']
  selected=dict(N=s['N'],source_sha256=s['source_sha256'],ports=ps,glue=glue,local_bound=bound,root_count=length,primes=primes,selected=dict(**st,cutset=fixed,branches=1<<len(fixed),weighted_entries=st['output_entries']*(1<<len(fixed))))
  selected['mathematical_plan_sha256']=digest(selected)
 p=selected
 assert p['source_sha256']==s['source_sha256'] and p['ports']==ps
 # Keep original measured memory envelope until a source-specific larger route is admitted.
 if p['selected']['width']>22 or p['selected']['branches']>2048:raise RuntimeError('Source requires a separately admitted larger exact plan')
 ram=Path(q['checkpoint_dir']).parent/'restored_work';ram.mkdir(parents=True,exist_ok=True);os.environ['CUPY_CACHE_DIR']='/opt/gen4/restore14/research-cuda-cache'
 (ram/'SOURCE.json').write_text(json.dumps(s));(ram/'PLAN.json').write_text(json.dumps(p));cache=IndexCache();t=time.monotonic();ts=templates(s,p);desc,maps,stats=cache.compile(ts[0]);preparation=time.monotonic()-t
 class Borrowed:
  def execute(self,*a,**kw):return base.execute(*a,**kw)
  def close(self):pass
 cases=[(s,p,ts,desc,maps,stats)];branch=p['selected']['branches']>32
 if branch:
  spec=importlib.util.spec_from_file_location('restored_frontier','/opt/gen4/spin-n120-frontier1/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  # Index 1 preserves original case-0 N30 qualification semantics.
  adapter=mod.Frontier(Borrowed(),ram,[cases[0],cases[0]],cache,deadline=time.time()+q.get('gpu_seconds',7000));adapter.durable=ram/'compact';adapter.durable.mkdir(exist_ok=True)
 else:adapter=Focus(Borrowed(),ram,cases,cache)
 rows=[];r=None;t=time.monotonic()
 try:
  for i in range(1 if branch else q.get('repeats',3)):
   if branch:
    r=adapter.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=1,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256']))
    if r['status']!='EXACT':raise RuntimeError('Partial exact residues retained; no completed answer')
   else:r=adapter.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=0,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256'],repeat=i))
   if q.get('variant'):raise RuntimeError('Variant requires independent exact reference before acceptance')
   compare_answer(r['answer'],canonical(q['N'])['spectrum']);assert all(r['answer']['checks'].values())
   rows.append(dict(repeat=i,execution=r['execution'],readout_ns=r['answer']['reconstruction_ns']))
 finally:adapter.close()
 return dict(status='EXACT',N=s['N'],source_hash=s['source_sha256'],seconds=time.monotonic()-t,answer=r['answer'],execution=r['execution'],full_density_equal=True,root_batch=r['execution'].get('batch'),repetitions=rows,source_preparation_seconds=preparation,restored_backend=True,plan=p)
