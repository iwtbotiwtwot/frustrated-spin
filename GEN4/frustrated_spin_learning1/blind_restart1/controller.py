"""Fresh eight-hour first-campaign restart with evidence-driven self-follow-up."""
import os,sys,time,json,signal,subprocess,fcntl,traceback,shutil,tarfile,datetime,math
from pathlib import Path
P=Path(__file__).resolve().parent
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
sys.path[:0]=[str(P),str(P/'runtime')]
from research import load,save,append,sha,canonical,writecsv
import questions as policy
import resource_manager as rm
stop=False;child=None
def stopping(*args):
 global stop
 stop=True
 if child and child.poll() is None:
  try:os.killpg(child.pid,signal.SIGTERM)
  except ProcessLookupError:pass
for signum in [signal.SIGTERM,signal.SIGINT]:signal.signal(signum,stopping)
def stamp(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
def resource_gate(gpu=False):
 cpus=sorted(os.sched_getaffinity(0));b=rm.snapshot({'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.95,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}},'pod');cg=Path('/sys/fs/cgroup');quota=(cg/'cpu.max').read_text().split();limit=len(cpus) if quota[0]=='max' else int(quota[0])/int(quota[1]);mem=(cg/'memory.max').read_text().strip();avail=b['prelaunch_mem_available'] if mem=='max' else min(b['prelaunch_mem_available'],int(mem)-int((cg/'memory.current').read_text()));b.update(cpu_quota=limit,available_ram=avail,available_disk=shutil.disk_usage(P).free,process_snapshot=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,rss,comm','--sort=-pcpu'],text=True).splitlines()[:18])
 if gpu:
  # Separate preflight process avoids creating a parent CUDA context before the solver forks.
  code='import cupy as c,json; n=c.cuda.runtime.getDeviceCount(); a=[]\nfor d in range(n):\n with c.cuda.Device(d):a.append(c.cuda.runtime.memGetInfo())\nprint(json.dumps(a))'
  b['gpu_memory']=json.loads(subprocess.check_output([sys.executable,'-c',code],text=True,timeout=30));b['gpu_ready']=len(b['gpu_memory'])==14 and all(x[0]>8*1024**3 for x in b['gpu_memory'])
 b['admitted']=avail>(48 if gpu else 8)*1024**3 and b['available_disk']>10*1024**3 and limit>=2 and b.get('gpu_ready',True);return b

def independent_rule(q,v):
 if q['kind']=='component_rule':
  groups=v['certificate']['groups'];s=canonical(q['N'])['source'];assert sorted(x for g in groups for x in g)==list(range(s['N']));labels={x:i for i,g in enumerate(groups) for x in g};assert all(labels[u]==labels[w] for u,w,j in s['edges'])
 elif q['kind']=='ports':
  from collections import Counter
  c=canonical(q['N'])['spectrum'];rows=c.get('closed_port_rows');assert rows is not None
  summed=Counter()
  for row in v['answer']['port_rows']:
   for e,count in row['dos']:summed[int(e)]+=int(count)
  assert dict(summed)=={int(e):int(c) for e,c in c['scalar_dos']}
 elif q['kind']=='symmetry':
  record=load(P/q['variant']);s=record['source'];a=canonical(q['N'])['source'];pr=record['proof']
  if pr['kind']=='EXPLICIT_GAUGE_BIJECTION':
   g=pr['signs'];assert all(z in [-1,1] for z in g);assert [h*g[i] for i,h in enumerate(s['fields'])]==a['fields'];assert sorted([[u,w,j*g[u]*g[w]] for u,w,j in s['edges']])==sorted(a['edges'])
  else:
   inv={int(v):int(k) for k,v in pr['mapping'].items()};assert len(inv)==s['N'];assert sorted([[*sorted([inv[u],inv[w]]),j] for u,w,j in s['edges']])==sorted(a['edges']);assert all(s['fields'][i]==a['fields'][inv[i]] for i in inv)
  ports=a.get('retained_ports',canonical(q['N'])['spectrum'].get('retained_ports',list(range(min(4,q['N'])))))
  assert all(pr['signs'][v]==1 for v in ports) if pr['kind']=='EXPLICIT_GAUGE_BIJECTION' else all(int(pr['mapping'][str(v)])==v for v in ports)
 else:return None
 return dict(question_id=q['question_id'],status='CERTIFIED_EXACT_RULE',rule=v.get('rule',v.get('proof',{}).get('kind','DISCONNECTED_COMPONENT_CONVOLUTION')),N=q['N'],scope='Explicit source/partition or bijection; established finite-sum identity, not a theorem inferred from timings',independent_verification=True)

def reports(state):
 rows=[]
 for rec in state['completed'].values():
  q=rec['question'];r=load(P/rec['result']);v=r['value']
  if q['kind']=='gpu_compare':
   for m in v['measurements']:rows.append(dict(N=q['N'],variant=q.get('variant'),method=m['method'],seconds=m['seconds'],hardware=v['backend'],cold_workers=m['cold_workers'],question_id=q['question_id'],verified=True))
  elif q['kind']=='solve':rows.append(dict(N=q['N'],variant=q.get('variant'),method=q['method'],seconds=r['seconds'],hardware='CPU_NATIVE_EXACT',question_id=q['question_id'],verified=True))
 writecsv(P/'METHOD_SCORECARD.csv',rows)
 import numpy as np
 groups={}
 for obs in state['observations']:
  for method,seconds in obs['methods'].items():
   key=obs['backend']+'|'+method;source=obs['features']['source_hash'];groups.setdefault(key,{})[source]=(obs['work_by_method'].get(method,1),seconds,obs['backend'],method)
 models={}
 for key,by_source in groups.items():
  rs=list(by_source.values());x=np.log([max(1,r[0]) for r in rs]);y=np.log([max(1e-9,r[1]) for r in rs]);count=len(rs)
  if count>=3 and float(np.std(x))>.1:
   X=np.stack([np.ones(count),x],axis=1);b=np.linalg.lstsq(X,y,rcond=None)[0];intercept,slope=map(float,b);fit='LOG_LINEAR_WORK'
  else:intercept=float(np.median(y-x));slope=1.;fit='PROVISIONAL_WORK_RATE'
  models[key]=dict(status='LEARNED_HEURISTIC',backend=rs[0][2],method=rs[0][3],independent_sources=count,intercept=intercept,slope=slope,fit=fit,training_sources=list(by_source),scope='Only fresh measurements; structural work is pre-execution; provisional rates are not held-out performance claims')
 state['cost_models']=models
 save(P/'METHOD_MODELS.json',dict(status='LEARNED_HEURISTIC' if rows else 'UNMEASURED',models=models,fresh_observations=state['observations'],scope='Fresh campaign only; methods and backends kept separate'))
 nexts=sorted(state['queue'],key=lambda q:-policy.score(state,q))[:5]
 save(P/'FRONTIER.json',dict(formula='(information_gain + unvisited_theme_bonus) / sqrt(predicted_cost) / (1 + completed_in_theme)^0.35 + bounded_waiting_age',questions=state['queue'],next_questions=nexts,branch_neutral_counts=state['neutral'],coverage=state['theme_counts'],saturation_policy='Two neutral outcomes close an intervention branch; then inspect unvisited source regimes and intervention classes; finish only on deadline, stop, resource gate or no novel admissible questions'))
 failed=[v for v in state['done'].values() if v['status']!='COMPLETE'];rules=load(P/'CERTIFIED_RULES.json')
 lines=['# Fresh blind research progress','',f"Status: {state['status']}; completed {len(state['completed'])}; failures/capacity findings {len(failed)}; pending {len(state['queue'])}.",'','Initial state contained no previous campaign question queue, fitted model, conclusion or certificate. Canonical atlas/historical measurements and verified solver code are explicit retained inputs. New result-derived children: '+str(state['result_children'])+'.','', 'Research coverage: '+json.dumps(state['theme_counts']), '', 'Exact source-specific rules independently verified: '+str(len(rules))+'. These are established finite-sum identities applied to explicit inputs; none installed globally.','','## Highest-value next questions']
 lines += ['- '+q['question'] for q in nexts]
 lines += ['','## Findings and remaining questions','See MODEL_SUMMARY.md and STRUCTURAL_REGIMES.md for freshly recomputed structural baselines, N100_N105_FORENSIC.md for retrospective packet-family comparisons, and N96_N120_SCALING.md for the distinct frustrated-source extension. METHOD_SCORECARD.csv contains actual new exact costs. QUESTION_LEDGER.jsonl records each hypothesis, result, failure and generated follow-up.','', 'N121–144 remain unexecuted. PREDICTIONS_121_144.json gives conditional pre-execution predictions where future graphs are not defined. Discuss source-family definitions, the strongest measured structural predictors, counterexamples and candidate exact reductions before another frontier run.']
 (P/'OVERNIGHT_SUMMARY.md').write_text('\n'.join(lines)+'\n')

def main():
 global child
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--hours',type=float,default=8);ap.add_argument('--max-experiments',type=int);args=ap.parse_args()
 lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);pool=Path('/opt/gen4/restore14/research-pool.lock').open('a');fcntl.flock(pool,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (P/'STATE.json').exists():state=load(P/'STATE.json')
 else:
  state=dict(started=time.time(),deadline=time.time()+args.hours*3600,status='STARTING',done={},completed={},queue=[],seen=[],generated=0,steps=0,result_children=0,neutral={},observations=[],theme_counts={},completed_questions=[],blind_initialization=True,prior_research_results_loaded=0);policy.initial(state)
 for f in ['QUESTION_LEDGER.jsonl','RULE_CANDIDATES.jsonl','COUNTEREXAMPLES.jsonl']:(P/f).touch(exist_ok=True)
 if not (P/'CERTIFIED_RULES.json').exists():save(P/'CERTIFIED_RULES.json',[])
 current=None;lastsync=0;finished_this_start=0
 def checkpoint(status):
  state.update(status=status,updated=time.time(),current=current);save(P/'STATE.json',state);save(P/'STATUS.json',dict(status=status,pid=os.getpid(),worker_pid=child.pid if child and child.poll() is None else None,start_utc=stamp(state['started']),deadline_utc=stamp(state['deadline']),completed=len(state['completed']),attempted=len(state['done']),pending=len(state['queue']),generated_followups=state['result_children'],active_question=None if current is None else current['question'],active_theme=None if current is None else current['theme'],GPU_workers=14,CPU_role='shared preparation and exact reconstruction for GPU work; one bounded research question at a time',hosted_calls=0,blind_initialization=True,prior_research_results_loaded=0,stop_command=f'kill -TERM {os.getpid()}',holdouts_untouched=True))
 def sync():
  mirror=Path(os.environ.get('BLIND_DURABLE','/workspace/gen4/runs/spin-blind-restart1'));mirror.mkdir(parents=True,exist_ok=True);archive=P/'checkpoint.tar.gz';tmp=P/'checkpoint.part'
  with tarfile.open(tmp,'w:gz',compresslevel=1) as tar:
   for f in P.iterdir():
    if f.is_file() and f.suffix in ['.json','.jsonl','.csv','.md','.py']:tar.add(f,arcname=f.name)
   tar.add(P/'variants',arcname='variants')
   if current:
    work=P/'experiments'/current['question_id']/'gpu_work'
    if work.exists():
     for f in work.iterdir():
      if f.is_file() and f.name.startswith(('RESIDUES','PROFILES')):tar.add(f,arcname=str(f.relative_to(P)))
  tmp.replace(archive)
  try:
   subprocess.run(['timeout','45','cp',str(archive),str(mirror/'checkpoint.new.tar.gz')],check=True);(mirror/'checkpoint.new.tar.gz').replace(mirror/'checkpoint.tar.gz');shutil.copyfile(P/'STATUS.json',mirror/'STATUS.json')
  except Exception as e:append(P/'SYNC_ERRORS.jsonl',dict(time=time.time(),error=str(e)))
 if state.get('current'):
  q=state['current'];state['done'][q['question_id']]=dict(status='INTERRUPTED',error='Preserved prior precommit; follow-up generated without repeating its exact attempt');policy.follow(state,q,None,error='interrupted')
 checkpoint('RUNNING')
 try:
  while not stop and not (P/'STOP').exists() and time.time()<state['deadline']-10:
   if not state['queue']:
    added=policy.refill(state);append(P/'QUESTION_LEDGER.jsonl',dict(event='FRONTIER_REVIEW',added=added,time=time.time()))
    if not added:checkpoint('NO_NOVEL_ADMISSIBLE_QUESTION');break
   state['queue'].sort(key=lambda q:-policy.score(state,q));q=state['queue'].pop(0);current=q;qid=q['question_id'];out=P/'experiments'/qid;out.mkdir(parents=True,exist_ok=True)
   gate=resource_gate(q['kind']=='gpu_compare')
   if not gate['admitted']:state['queue'].insert(0,q);state['last_gate']=gate;current=None;checkpoint('RESOURCE_GATE');break
   limit=min(q['maximum_admitted_seconds'],max(1,int(state['deadline']-time.time()-10)));q['maximum_admitted_seconds']=limit
   pre=dict(**q,timestamp=stamp(time.time()),resource_gate=gate,code_hashes={name:sha(P/name) for name in ['blind_engine.py','questions.py','research.py','worker.py']})
   if (out/'PRECOMMIT.json').exists():raise RuntimeError('Refusing to overwrite prior experiment precommit')
   save(out/'PRECOMMIT.json',pre);append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',**pre));checkpoint('RUNNING');t=time.monotonic();log=(out/'EXECUTION.log').open('a')
   child=subprocess.Popen([sys.executable,str(P/'worker.py'),str(out/'PRECOMMIT.json'),str(out)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);checkpoint('RUNNING')
   while child.poll() is None:
    if stop or (P/'STOP').exists() or time.monotonic()-t>limit:
     try:os.killpg(child.pid,signal.SIGTERM)
     except ProcessLookupError:pass
     try:child.wait(timeout=5)
     except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
     break
    if time.time()-lastsync>300:checkpoint('RUNNING');sync();lastsync=time.time()
    time.sleep(.5)
   rc=child.returncode;child=None;log.close();elapsed=time.monotonic()-t;error=None;r=None;children=[]
   try:
    if rc:raise RuntimeError((out/'EXECUTION.log').read_text()[-2000:])
    r=load(out/'RESULT.json');v=r['value'];rule=independent_rule(q,v)
    if rule:
     rules=load(P/'CERTIFIED_RULES.json');rules.append(rule);save(P/'CERTIFIED_RULES.json',rules)
    children=policy.follow(state,q,r);state['completed'][qid]=dict(question=q,result=str((out/'RESULT.json').relative_to(P)));state['completed_questions'].append(q)
   except Exception:
    error=traceback.format_exc();children=policy.follow(state,q,r,error=error);append(P/'COUNTEREXAMPLES.jsonl',dict(question_id=qid,error=error,meaning='Execution or resource finding unless an explicit mathematical counterexample is supplied'))
   outcome=dict(status='COMPLETE' if error is None else 'FAILED_OR_CAPACITY',elapsed_seconds=elapsed,predicted_seconds=q['predicted_cost_seconds'],prediction_error_seconds=elapsed-q['predicted_cost_seconds'],error=error,next_questions_generated=children)
   state['done'][qid]=outcome;state['result_children']+=len(children);state['steps']+=1;state['theme_counts'][q['theme']]=state['theme_counts'].get(q['theme'],0)+1;append(P/'QUESTION_LEDGER.jsonl',dict(event='RESULT',question_id=qid,**outcome));append(P/'RULE_CANDIDATES.jsonl',dict(question_id=qid,status='OBSERVED_PATTERN' if error is None else 'FAILED_EXPERIMENT',theme=q['theme'],N=q.get('N')))
   current=None;checkpoint('RUNNING');reports(state)
   # Keep each native receipt/result once, separate from small periodic state checkpoints.
   bundle=P/(qid+'.tar.gz')
   with tarfile.open(bundle,'w:gz',compresslevel=1) as tar:tar.add(out,arcname=qid)
   mirror=Path(os.environ.get('BLIND_DURABLE','/workspace/gen4/runs/spin-blind-restart1'))/'experiments';mirror.mkdir(parents=True,exist_ok=True)
   try:subprocess.run(['timeout','45','cp',str(bundle),str(mirror/bundle.name)],check=True)
   except Exception as e:append(P/'SYNC_ERRORS.jsonl',dict(time=time.time(),bundle=str(bundle),error=str(e)))
   sync();lastsync=time.time();finished_this_start+=1
   if args.max_experiments and finished_this_start>=args.max_experiments:checkpoint('BOUNDED_CHECK_COMPLETE');break
  if stop or (P/'STOP').exists():checkpoint('STOPPED')
  elif time.time()>=state['deadline']-10:checkpoint('DEADLINE')
 except BaseException:
  state['controller_failure']=traceback.format_exc();checkpoint('FAILED');raise
 finally:
  if child and child.poll() is None:stopping();child.wait(timeout=10)
  reports(state);checkpoint(state['status']);sync()
if __name__=='__main__':main()
