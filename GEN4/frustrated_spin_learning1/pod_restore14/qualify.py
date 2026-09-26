"""Qualify the retained focused and frontier engines without modifying either."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ.update(GEN4_SPIN_SOURCE='/opt/gen4/n96-benchmark1/source',GEN4_SPIN_CATALOG_CODE='/opt/gen4/spin-catalog1',GEN4_SPIN_TRAINING_CODE='/opt/gen4/spin-training1')
import sys,json,time,statistics,subprocess,importlib.util
from pathlib import Path
sys.path[:0]=['/opt/gen4/current','/opt/gen4/spin-focused1','/opt/gen4/spin-training1','/opt/gen4/spin-catalog1']
from run_fast import Focus
from arithmetic import templates,IndexCache
from SAM_PROJECT.session import DomainSession
P=Path('/opt/gen4/restore14'); ram=Path('/dev/shm/gen4-restore14-qualification');ram.mkdir(exist_ok=False)
os.environ['CUPY_CACHE_DIR']=str(ram/'cuda-cache')
spec=json.loads((P/'N96_SPEC.json').read_text());ref=json.loads((P/'N96_REFERENCE.json').read_text());source=spec['source'];plan=spec['plan'];cache=IndexCache();t=time.monotonic();ts=templates(source,plan);desc,maps,stats=cache.compile(ts[0]);prep=time.monotonic()-t
assert plan['selected']['branches']==16 and plan['selected']['width']==21
rows=[]
with DomainSession.start('MATTER_SEARCH',objective='Restore original fourteen-worker focused and frontier spin execution configuration',output_root=ram/'sessions',receipt_storage='gzip') as session:
 print(json.dumps(session.announcement()),flush=True)
 adapter=Focus(session.consumer,ram,[(source,plan,ts,desc,maps,stats)],cache);session.consumer=adapter
 cached=session.execute('GEN3_SPIN_PLAN',dict(source=source,previous_N=95),purpose='Confirm installed identical-source expanded plan cache')
 assert cached['plan']['mathematical_plan_sha256']==plan['mathematical_plan_sha256']
 for repeat in range(4):
  r=session.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=0,source_sha256=source['source_sha256'],plan_sha256=plan['mathematical_plan_sha256'],repeat=repeat),purpose='Fresh exact N96 calculation using restored original focused backend')
  a=r['answer'];e=r['execution']
  assert all(a[k]==ref[k] for k in ['scalar_dos','closed_port_rows','open_y_operator','configuration_count'])
  assert all(a['checks'].values()) and e['workers']==14 and all(e['roots_per_gpu'])
  rows.append(dict(repeat=repeat,scope='cold_worker_start' if repeat==0 else 'warm_persistent_workers',solve_seconds=e['total_ns']/1e9,prepare_seconds=e['prepare_ns']/1e9,gpu_seconds=e['arithmetic_ns']/1e9,readout_seconds=a['reconstruction_ns']/1e9,roots_per_gpu=e['roots_per_gpu'],exact_equal=True))
  print(json.dumps(rows[-1]),flush=True)
 session.execute('GEN3_CHECKPOINT',{},purpose='Retain exact restoration qualification')
assert all(not p.is_alive() for p in adapter.workers)
# Execute the original branch-group/five-prime qualification, without N120 replay.
f=importlib.util.spec_from_file_location('restored_frontier','/opt/gen4/spin-n120-frontier1/run.py');front=importlib.util.module_from_spec(f);f.loader.exec_module(front)
q=json.loads((front.HERE/'QUALIFICATION_N30.json').read_text());s=q['source'];p=q['plan'];p['primes']=json.loads((front.HERE/'PLAN.json').read_text())['primes'];fixed=list(range(4,9));st=front.structure(30,[e for e in s['edges'] if e not in p['glue']],p['ports'],fixed);p['selected']=dict(**st,cutset=fixed,branches=32,weighted_entries=st['output_entries']*32,method='branch_group_scheduler_qualification');p['mathematical_plan_sha256']=front.digest(p)
cache=IndexCache();ts=templates(s,p);desc,maps,stats=cache.compile(ts[0]);br=ram/'branch';br.mkdir();dur=P/'branch-checkpoints';dur.mkdir(exist_ok=True)
with DomainSession.start('MATTER_SEARCH',objective='Verify restored N1–120 branch-group and five-prime execution',output_root=br/'sessions',receipt_storage='gzip') as session:
 adapter=front.Frontier(session.consumer,br,[(s,p,ts,desc,maps,stats)],cache,deadline=time.time()+300);adapter.durable=dur;session.consumer=adapter
 crt=session.execute('GEN4_N120_CRT_CHECK',dict(primes=p['primes']),purpose='Verify retained fifth-prime reconstruction capacity')
 r=session.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=0,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256']),purpose='Fresh N30 exact test through original N120 branch-group engine')
 assert r['status']=='EXACT' and all(r['answer']['checks'].values()) and r['execution']['resumed_tasks']==0
 session.execute('GEN3_CHECKPOINT',{},purpose='Retain branch-group restoration qualification')
result=dict(status='PASS',N96_source_sha256=source['source_sha256'],plan_sha256=plan['mathematical_plan_sha256'],source_preparation_seconds=prep,N96_runs=rows,N96_warm_median_seconds=statistics.median(x['solve_seconds'] for x in rows[1:]),historical_median_seconds=3.257604178,branch_group_execution=r['execution'],five_prime_check=crt,workers_stopped=all(not p.is_alive() for p in adapter.workers),ram=str(ram))
(P/'QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
