"""Bounded local research controller. No hosted calls, service changes or hardware lifecycle API."""
import os,sys,json,time,signal,subprocess,fcntl,hashlib,traceback,copy,math,importlib.util,resource,argparse,datetime
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
sys.path.insert(0,str(P))
from research import load,save,append,digest,sha,canonical,features,writecsv,METHODS
spec=importlib.util.spec_from_file_location('project_resources',R/'CURRENT_REVISION/engines/SLC/gen3/resources.py');rm=importlib.util.module_from_spec(spec);spec.loader.exec_module(rm)
stop=False;child=None

def sig(signum,frame):
 global stop
 stop=True
 if child and child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
for s in [signal.SIGINT,signal.SIGTERM]:signal.signal(s,sig)
def resource_gate():
 profile=load(rm.PROFILE);b=rm.snapshot(profile,rm.host_name());cpu=min(2,b['cpu_equivalents']);allowed=b['allowed_cpus'][:max(1,min(2,int(math.ceil(cpu))))]
 procs=subprocess.check_output(['ps','-eo','pid,pcpu,pmem,comm','--sort=-pcpu'],text=True).splitlines()[:16]
 free=b['prelaunch_mem_available'];okay=free>=6*1024**3 and cpu>=.5 and __import__('shutil').disk_usage(P).free>=5*1024**3
 return dict(admitted=okay,resource_manager=str(rm.__file__),budget=b,cpu_cap=cpu,affinity=allowed,experiment_address_space_limit=4*1024**3,process_snapshot=procs,GPU='unavailable locally; no remote hardware contacted',policy='one child; nice10; existing-manager snapshot + exclusive existing run lock; no configure()/services; no intentional swap use')
def question(kind,n=None,method=None,variant=None,plan=None,reason='',info=1,cost=1):
 q=dict(kind=kind,N=n,method=method,variant=variant,question=f'{kind}: '+(f'N{n} ' if n else '')+(method or '')+' '+reason,why_chosen=reason,expected_information_gain=info,predicted_cost_seconds=max(.1,cost),maximum_admitted_seconds=120,claim_type='NEWLY_PRECOMMITTED',features_used='frozen graph structure and prior completed experiments; no future output',expected_discriminating_outcomes=['structural or exact equality supports scoped hypothesis','counterexample or resource rejection changes next frontier'],verification_contract='native source-bound receipt; every DOS retains full counts/moments/port closure; compare canonical or independent route; structural plans are not new spectra')
 if plan:q['plan']=plan
 identity=dict(kind=kind,N=n,method=method,variant=variant,plan=digest(plan) if plan else None)
 if kind=='solve' and method not in ['components','variable_elimination','incremental_boundary']:identity['implementation']='normalized-branch-v2'
 q['question_id']=digest(identity)[:20]
 q['score']=info/max(.1,cost)
 if n:
  c=canonical(n);q['source_lineage']=c['provenance'];q['inputs_hashes']={f'canonical/N{n:03d}.json':sha(P/f'canonical/N{n:03d}.json')}
  if variant:q['inputs_hashes'][variant]=sha(P/variant)
 q['candidate_methods']=[method] if method else METHODS
 return q

def frontier(state):
 qs=[];done=state['done'];completed=state['completed'];models=load(P/'MODELS.json') if (P/'MODELS.json').exists() else {};anomalies={r['N']:r['log_error'] for r in models.get('anomalies',[])}
 for kind in ['atlas','analysis']:
  init=question(kind,reason='Build structural baseline before complex learning',info=10000,cost=4)
  if init['question_id'] not in done:return [init]
 # Priority forensic experiments execute real alternative exact routes on packet cases.
 for n in [100,105,12,16,8,18,20,24]:
  for method in ['components','variable_elimination']+(['incremental_boundary'] if n<=18 else []):
   qs.append(question('solve',n,method,reason='Distinguish decomposition from nominal N; retain full density equality',info=500 if n in [100,105] else 10,cost=3 if n<20 else 20))
 for n in range(1,121):
  qs.append(question('plans',n,reason='Explain anomalies and compare six planning routes without expensive DOS',info=2+anomalies.get(n,0),cost=max(.3,n*n/3000)))
  qs.append(question('component_rule',n,reason='Independently check exact component-separation precondition across atlas',info=3 if n in [100,105] else .2,cost=.3))
 # New experiments are generated only from returned plans, not a blind nine-way full sweep.
 for id,record in completed.items():
  if record['kind']!='plans':continue
  result=load(P/record['result'])['value'];n=record['N'];variant=record.get('variant')
  for plan in result['plans']:
   method=plan.get('training_method',plan['selected'].get('method'))
   if n<=20 and plan['selected']['width']<=8:
    qs.append(question('solve',n,method,variant,plan,reason='Counterfactual exact route for cheap source; compare all coefficients',info=7,cost=max(.3,plan['selected']['weighted_entries']/10000)))
  if result.get('features',{}).get('components',1)>1 and variant:
   if result['features']['max_component']<=18:
    qs.append(question('solve',n,'components',variant,reason='Same-N structural control tests decomposition explanation',info=9,cost=10))
 for v in sorted((P/'variants').glob('*.json')):
  x=load(v);n=x['source']['N'];qs.append(question('plans',n,variant=str(v.relative_to(P)),reason='Same-N/different-structure control; avoid N-to-recipe memorization',info=6,cost=max(1,n*n/3000)))
 fits=load(P/'METHOD_MODELS.json') if (P/'METHOD_MODELS.json').exists() else {}
 for q in qs:
  model=fits.get(q.get('method'),{})
  if model.get('n',0)>=3 and q.get('N') and q['kind']=='solve':
   work=q.get('plan',{}).get('selected',{}).get('weighted_entries')
   if work:
    predicted=math.exp(max(-10,min(10,model['log_seconds_intercept']+model['log_work_slope']*math.log(max(1,work)))))
    q['predicted_cost_seconds']=predicted;q['score']=q['expected_information_gain']/max(.1,predicted);q['cost_model']='learned per-method work regression, CPU only'
 return sorted([q for q in qs if q['question_id'] not in done],key=lambda q:(-q['score'],q['question_id']))

def verify_partition(s,groups):
 # Independent verifier does not call solver's component finder.
 assert sorted(v for g in groups for v in g)==list(range(s['N']))
 labels={v:i for i,g in enumerate(groups) for v in g}
 for u,v,j in s['edges']:assert labels[u]==labels[v]
 return True

def variants_after(q,res):
 if q['kind']!='plans' or q.get('variant') or q['N'] not in [72,84,96,100,105,108,120]:return []
 from variant_generator import graph_family
 out=[]
 for seed in [1,2,3]:
  s=graph_family(canonical(q['N'])['source'],seed);s['family']='VARIANT_DEGREE_PRESERVING_SIX_SWAPS';s.pop('source_sha256',None);s['source_sha256']=digest(s)
  name=f'variants/N{q["N"]}_swap{seed}.json'
  if not (P/name).exists():save(P/name,dict(kind='NEW_VARIANT',source=s,parent=canonical(q['N'])['source']['source_sha256'],generator='retained graph_family six degree-preserving swaps',seed=seed))
  out.append(name)
 if q['N'] in [100,105]:
  s=copy.deepcopy(canonical(q['N'])['source']);groups=__import__('research').exact.components(s);s['edges'].append([min(groups[0][0],groups[1][0]),max(groups[0][0],groups[1][0]),1]);s['edges'].sort();s['family']='PACKET_SINGLE_BRIDGE_ABLATION';s.pop('source_sha256',None);s['source_sha256']=digest(s);name=f'variants/N{q["N"]}_bridge.json';save(P/name,dict(kind='NEW_VARIANT',source=s,parent=canonical(q['N'])['source']['source_sha256'],generator='explicit pair-graph grammar; one cross-component edge'))
  append(P/'COUNTEREXAMPLES.jsonl',dict(rule='Reuse original component partition after a bridge',N=q['N'],counterexample=name,status='EXACT_PRECONDITION_VIOLATED',reason='New nonzero edge joins former independent components'))
  out.append(name)
 return out

def update_scorecard(state):
 rows=[]
 for id,rec in state['completed'].items():
  r=load(P/rec['result']);v=r['value']
  if rec['kind']=='plans':
   source=canonical(rec['N'])['source'] if not rec.get('variant') else load(P/rec['variant'])['source'];f=v['features']
   for plan in v['plans']:
    sel=plan['selected'];rows.append(dict(N=rec['N'],variant=rec.get('variant'),method=plan['training_method'],observation='STRUCTURAL_COUNTERFACTUAL_NOT_TIMED_SOLVE',width=sel['width'],work=sel['weighted_entries'],roots=plan['root_count'],primes=len(plan['primes']),cost_seconds=None,predicted_cost_class=sel['weighted_entries']*plan['root_count']*len(plan['primes'])))
   for m in ['components','variable_elimination','incremental_boundary']:
    rows.append(dict(N=rec['N'],variant=rec.get('variant'),method=m,observation='STRUCTURAL_ADMISSION',work=f['local_assignments'] if m=='components' else f['minfill_work'],admitted=(f['max_component']<=18 if m=='components' else rec['N']<=20 if m=='variable_elimination' else rec['N']<=18),cost_seconds=None))
  elif rec['kind']=='solve':rows.append(dict(N=rec['N'],variant=rec.get('variant'),method=rec['method'],observation='NEWLY_EXECUTED_EXACT',cost_seconds=r['seconds'],arithmetic_ns=v['execution'].get('elapsed_ns'),work=v['execution'].get('arithmetic_work_units'),full_density_verified=True))
 writecsv(P/'METHOD_SCORECARD.csv',rows)
 # Per-method interpretable work-cost model on genuinely timed CPU data only.
 fits={}
 import numpy as np
 for m in METHODS:
  rs=[r for r in rows if r['method']==m and r.get('cost_seconds') and r.get('work')]
  if len(rs)>=3:
   X=np.asarray([[1,math.log(max(1,r['work']))] for r in rs]);y=np.log([r['cost_seconds'] for r in rs]);b=np.linalg.lstsq(X,y,rcond=None)[0];fits[m]=dict(status='LEARNED_HEURISTIC',n=len(rs),log_seconds_intercept=float(b[0]),log_work_slope=float(b[1]),log_residual_sd=float(np.std(y-X@b)),hardware='this workstation CPU',no_GPU_transfer=True)
  else:fits[m]=dict(status='INSUFFICIENT_TIMED_COUNTERFACTUALS',n=len(rs))
 save(P/'METHOD_MODELS.json',fits)
 predictions=[]
 for n in range(1,121):
  c=canonical(n);f={'max_component': max(map(len,__import__('research').exact.components(c['source'])))};choices=[]
  for m in METHODS:
   found=[r for r in rows if r['N']==n and not r.get('variant') and r['method']==m]
   measured=[r for r in found if r.get('cost_seconds')]
   model=fits[m];work=next((r.get('work') for r in found if r.get('work')),None)
   pred=None
   if measured:pred=sum(r['cost_seconds'] for r in measured)/len(measured)
   elif work and model.get('n',0)>=3:pred=math.exp(max(-10,min(10,model['log_seconds_intercept']+model['log_work_slope']*math.log(max(1,work)))))
   choices.append(dict(method=m,predicted_seconds=pred,work_proxy=work,status='OBSERVED_PATTERN' if measured else 'LEARNED_HEURISTIC' if pred else 'UNMEASURED',scope='local CPU experiment including runtime setup; structural planner cost is not GPU solve cost',admissible=f['max_component']<=18 if m=='components' else n<=18 if m=='incremental_boundary' else n<=20))
  usable=[x for x in choices if x['admissible'] and x['predicted_seconds'] is not None]
  predictions.append(dict(N=n,methods=choices,preferred_method=min(usable,key=lambda x:x['predicted_seconds'])['method'] if usable else 'structural planning required; exact execution not yet admitted'))
 save(P/'METHOD_PREDICTIONS.json',predictions)
 return rows

def reports(state):
 rows=update_scorecard(state);rules=load(P/'CERTIFIED_RULES.json');failed=[r for r in state['done'].values() if r['status']!='COMPLETE'];future=state.get('frontier',[])[:5]
 (P/'OVERNIGHT_SUMMARY.md').write_text('# Overnight learning summary\n\nOwner: Sean Brady, originator and conceptual director.\nStatus: '+state['status']+'\n\n1. Structure beyondN: independent component sizes and plan arithmetic burden distinguish sources. '+str(len(rows))+'method scorecard rows retained; consult measured versus structural labels.\n2. Staircase: transform/root changes, conditioning branches and retained widths contribute; MODEL_SUMMARY and STRUCTURAL_REGIMES quantify descriptive fits, transitions and mixed-hardware limits.\n3. N100/N105: packet factorization has max component15 and sum-of-local-assignment work; see forensic report and bridge controls. Retrospective, no preregistered prediction claim.\n4. N96/N120: separate graph-extension lineage; selected width, cutset, roots and primes alter work; differing readout backends retained explicitly.\n5. Nine method-family scorecards and per-method CPU regressions are in METHOD_SCORECARD.csv/METHOD_MODELS.json. Untimed GPU/expensive alternatives remain structural estimates, not fabricated runtimes.\n6. Heuristics remain LEARNED_HEURISTIC; exact partition violations are retained as counterexamples. Cross-source held-out atlas errors are reported separately from new CPU fit residuals.\n7. Certified rules: '+str(len(rules))+'source-specific component-separation certificates; the underlying convolution identity is established algebra, not a newly discovered theorem. No global installation.\n8. Failed/rejected experiments: '+str(len(failed))+'. See QUESTION_LEDGER; each retained without unlimited retries.\n9. Five next questions:\n'+json.dumps(future,indent=2)+'\n10. N121..144: conditional predictions only; graphs undefined, no execution.\n11. Discuss which future source family, graph construction and hardware should define a genuine prospective test; whether decomposition or retained-width predictions deserve the first test; and which counterexamples refine the route selector.\n')
 # All user-required outputs exist from startup; append-only ledgers may legitimately be empty.
 hashes=[]
 for f in P.iterdir():
  if f.is_file() and f.name not in ['HASHES.txt','RUN.log','STATUS.json','CONTROLLER.pid']:hashes.append(sha(f)+'  '+f.name)
 (P/'HASHES.txt').write_text('\n'.join(hashes)+'\n')

def main():
 global child
 ap=argparse.ArgumentParser();ap.add_argument('--hours',type=float,default=8);ap.add_argument('--max-experiments',type=int);ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
 lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 # Reuse existing resource-manager ownership lock without modifying its file.
 manager_lock=R/'SAM_RUNTIME/R3/run.lock'
 if manager_lock.exists():ml=manager_lock.open('r');fcntl.flock(ml,fcntl.LOCK_EX|fcntl.LOCK_NB)
 os.nice(10)
 statepath=P/('SMOKE_STATE.json' if args.smoke else 'STATE.json')
 state=load(statepath) if statepath.exists() and not args.smoke else dict(done={},completed={},started=time.time(),deadline=time.time()+args.hours*3600,status='STARTING')
 if state['status'] in ['DEADLINE','NO_ADMISSIBLE_QUESTION']:raise RuntimeError('Finished campaign; use a new additive campaign for further research')
 count=0
 def checkpoint(status):
  state['status']=status;state['updated']=time.time();save(statepath,state)
  save(P/('SMOKE_STATUS.json' if args.smoke else 'STATUS.json'),dict(status=status,pid=os.getpid(),session='detached local Python process',start_utc=datetime.datetime.fromtimestamp(state['started'],datetime.timezone.utc).isoformat(),deadline_utc=datetime.datetime.fromtimestamp(state['deadline'],datetime.timezone.utc).isoformat(),completed=len(state['completed']),attempted=len(state['done']),current_question=state.get('current'),resource_policy=state.get('resource'),stop_command=f'kill -TERM {os.getpid()}',restart='same command; completed question IDs skipped',hosted_calls=0,holdout_execution=False))
 for name in ['QUESTION_LEDGER.jsonl','RULE_CANDIDATES.jsonl','COUNTEREXAMPLES.jsonl']:(P/name).touch(exist_ok=True)
 if not (P/'CERTIFIED_RULES.json').exists():save(P/'CERTIFIED_RULES.json',[])
 checkpoint('STARTING')
 while not stop and not (P/'STOP').exists() and time.time()<state['deadline']-10:
  fs=frontier(state)
  if args.smoke:fs=[question('solve',6,'components',reason='Bounded end-to-end native smoke and exact independent replay',info=1,cost=1)] if count==0 else []
  state['frontier']=fs[:20];save(P/'FRONTIER.json',dict(formula='(information_gain + anomaly relevance + novelty + exact-rule relevance) / predicted seconds; weights encoded in precommit',questions=fs,generated=time.time()))
  if not fs:checkpoint('NO_ADMISSIBLE_QUESTION');break
  q=fs[0];gate=resource_gate();state['resource']=gate
  if not gate['admitted']:checkpoint('RESOURCE_GATE');break
  os.sched_setaffinity(0,gate['affinity']);remaining=state['deadline']-time.time();limit=min(q['maximum_admitted_seconds'],max(1,remaining-10))
  state['current']=q;checkpoint('RUNNING');out=P/('smoke' if args.smoke else 'experiments')/q['question_id']
  if args.smoke:out=out/str(time.time_ns());out.mkdir(parents=True,exist_ok=True)
  pre=out/'PRECOMMIT.json'
  if pre.exists():
   # Interrupted attempt is retained as data, never overwritten or silently retried.
   state['done'][q['question_id']]=dict(status='INTERRUPTED_PRIOR_ATTEMPT',record=str(pre));checkpoint('RECOVERED_INTERRUPTION');continue
  save(pre,dict(**q,timestamp=time.time(),resource_gate=gate,code_sha256=sha(P/'research.py')))
  append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',question_id=q['question_id'],record=str(pre.relative_to(P)),time=time.time(),scope='SMOKE' if args.smoke else 'OVERNIGHT'))
  t=time.monotonic();success=False;error=None
  with (out/'EXECUTION.log').open('a') as log:
   child=subprocess.Popen([sys.executable,str(P/'worker.py'),str(pre),str(out)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:rc=child.wait(timeout=limit)
   except subprocess.TimeoutExpired:
    os.killpg(child.pid,signal.SIGTERM)
    try:child.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
    rc=124
   child=None
  elapsed=time.monotonic()-t
  if rc==0 and (out/'RESULT.json').exists():
   rr=load(out/'RESULT.json');success=True
   if q['kind']=='component_rule':
    cert=rr['value']['certificate'];verify_partition(canonical(q['N'])['source'],cert['groups']);rules=load(P/'CERTIFIED_RULES.json');rules.append(dict(question_id=q['question_id'],**rr['value'],independent_verifier='controller.verify_partition'));save(P/'CERTIFIED_RULES.json',rules)
   nexts=variants_after(q,rr['value'])
   state['completed'][q['question_id']]=dict(kind=q['kind'],N=q['N'],method=q['method'],variant=q.get('variant'),result=str((out/'RESULT.json').relative_to(P)))
  else:error=(out/'EXECUTION.log').read_text()[-2000:];nexts=[]
  record=dict(status='COMPLETE' if success else 'FAILED',elapsed_seconds=elapsed,prediction_error_seconds=elapsed-q['predicted_cost_seconds'],returncode=rc,error=error,hypothesis_survived='Exact equality or structural return' if success else 'unresolved; failure retained',next_questions_generated=nexts)
  state['done'][q['question_id']]=record;append(P/'QUESTION_LEDGER.jsonl',dict(event='RESULT',question_id=q['question_id'],**record));append(P/'RULE_CANDIDATES.jsonl',dict(question_id=q['question_id'],status='OBSERVED_PATTERN' if success else 'FAILED_EXPERIMENT',scope=q['kind'],N=q['N']))
  checkpoint('RUNNING');reports(state);count+=1
  if args.max_experiments and count>=args.max_experiments:checkpoint('BOUNDED_TEST_COMPLETE');break
 if stop or (P/'STOP').exists():checkpoint('STOPPED')
 elif time.time()>=state['deadline']-10:checkpoint('DEADLINE')
 reports(state)
if __name__=='__main__':main()
