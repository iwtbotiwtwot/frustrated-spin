"""Ten-worker bounded outcome-driven campaign. No hosted calls or hardware management."""
import os,sys,time,json,signal,subprocess,datetime,fcntl,traceback,shutil,re
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
sys.path[:0]=[str(P),str(ROOT)]
import questions as qlib
from operations import load,save,sha,canonical
from research import append
import resource_manager as rm
stop=False

def stopped(*args):
 global stop
 stop=True
signal.signal(signal.SIGINT,stopped);signal.signal(signal.SIGTERM,stopped)
def stamp(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
def gate():
 cpus=sorted(os.sched_getaffinity(0));profile={'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.95,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}}
 b=rm.snapshot(profile,'pod');cg=Path('/sys/fs/cgroup');quota=(cg/'cpu.max').read_text().split();limit=len(cpus) if quota[0]=='max' else int(quota[0])/int(quota[1]);mem=(cg/'memory.max').read_text().strip();available=b['prelaunch_mem_available'] if mem=='max' else min(b['prelaunch_mem_available'],int(mem)-int((cg/'memory.current').read_text()))
 b.update(cgroup_cpu=limit,cgroup_available_ram=available,admitted=available>64*1024**3 and shutil.disk_usage(P).free>10*1024**3 and limit>=8)
 b['process_snapshot']=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,rss,comm','--sort=-pcpu'],text=True).splitlines()[:20]
 b['gpu_processes']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory','--format=csv,noheader'],text=True).strip()
 b['gpu_slots']=min(20,len(re.findall(r'UUID: (MIG-[^)]+)',subprocess.check_output(['nvidia-smi','-L'],text=True))))
 b['cpu_slots']=min(8,max(1,int(min(limit*.95,b['cpu_equivalents']))))
 b['slots']=b['gpu_slots']+b['cpu_slots'];b['worker_ram_cap_bytes']=min(20*1024**3,available//max(1,b['slots']))
 return b

def campaign_summary(state):
 qlib.summary(state)
 gpu=[]
 for rec in state['completed'].values():
  if rec['question']['kind']=='gpu_test':
   v=load(P/rec['result'])['value'];gpu.append(dict(question_id=rec['id'],N=v['N'],seconds=v['seconds'],root_batch=v['root_batch'],full_density_equal=v['full_density_equal'],execution=v.get('execution')))
 save(P/'GPU_SCORECARD.json',gpu)
 (P/'SUMMARY.md').open('a').write('\nGPU comparisons: '+str(len(gpu))+' completed, full densities verified. See GPU_SCORECARD.json for stage costs.\nLarger separator findings: see SEPARATOR_FINDINGS.jsonl.\nTwenty MIG GPU and eight CPU worker ceilings; adaptive CPU/RAM limits; exact answers remain source-bound. No N121+ execution.\n')

def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--test',type=int,default=0);args=ap.parse_args();lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);os.nice(10)
 devices=re.findall(r'UUID: (MIG-[^)]+)',subprocess.check_output(['nvidia-smi','-L'],text=True));assert len(devices)>=20
 for f in ['QUESTION_LEDGER.jsonl','RULE_CANDIDATES.jsonl','CERTIFICATES.jsonl','STRUCTURAL_DISCOVERIES.jsonl','COUNTEREXAMPLES.jsonl']:(P/f).touch(exist_ok=True)
 if (P/'STATE.json').exists():
  state=load(P/'STATE.json');interrupted=state.pop('inflight',[]);recover=[]
  def recover_once(oldq,parent,reason):
   if oldq.get('recovery_generation',0)>=1:return
   child=qlib.qmake(oldq['kind'],oldq.get('N'),oldq.get('methods'),oldq.get('variant'),why='Follow up once on '+reason,parent=parent,priority=110)
   for key in ['candidate_cutset','max_cutset','max_exact_assignments','max_component_size','max_exact_seconds','gpu_seconds','root_batch','gpu_route','plan','requested_ports']:
    if key in oldq:child[key]=oldq[key]
   child['maximum_admitted_seconds']=7200;child['recovery_generation']=1
   if oldq['kind']=='paired':
    child['cutset_port_repair']=True;ports=canonical(oldq['N'])['spectrum'].get('retained_ports',list(range(min(4,oldq['N']))));child['candidate_cutset']=[v for v in child.get('candidate_cutset',[]) if v not in ports]
   if oldq['kind']=='gpu_test' and oldq.get('checkpoint_dir'):child['resume_checkpoint_dir']=oldq['checkpoint_dir']
   child['question_id']=qlib.digest(dict(parent=parent,reason=reason,source=oldq.get('variant'),kind=oldq['kind']))[:24];qlib.enqueue(state,child)
  for q in interrupted:
   state['done'][q['question_id']]=dict(status='INTERRUPTED',seconds=0,error='Controller update checkpoint; original precommit and partial output retained')
   recover.append((q,q['question_id'],'interrupted while installing retained-port-safe separator search'))
  for id,r in list(state['done'].items()):
   if r.get('status')=='FAILED_OR_CAPACITY_BOUND' and 'KeyError' in str(r.get('error')):
    pre=P/'experiments'/id/'PRECOMMIT.json'
    if pre.exists():recover.append((load(pre),id,'retained-port-safe separator correction'))
  for item in recover:recover_once(*item)
 else:
  state=dict(started=time.time(),deadline=time.time()+8*3600,status='STARTING',queue=[],done={},completed={},seen_structure={},next_seed={},generated=0)
  prior=load(ROOT/'podrun1/STATE.json');qs={}
  for line in (ROOT/'podrun1/QUESTION_LEDGER.jsonl').read_text().splitlines():
   try:
    r=json.loads(line)
    if r.get('event')=='PRECOMMIT':qs[r['question_id']]=r
   except json.JSONDecodeError:pass
  seen=set()
  # Re-open the six dozen source-specific separator frontiers that were admitted by structure but hit the old work ceiling.
  sepmap={}
  for line in (ROOT/'podrun1/SEPARATOR_FINDINGS.jsonl').read_text().splitlines():
   try:sepmap[json.loads(line)['question_id']]=json.loads(line)
   except (json.JSONDecodeError,KeyError):pass
  for id,sep in sepmap.items():
   old=qs.get(id)
   if not old:continue
   key=('pair',old.get('N'),old.get('variant'),tuple(sep.get('cutset',[])))
   if key in seen:continue
   seen.add(key);q=qlib.qmake('separator_frontier',old['N'],variant=old.get('variant'),why="Search deeper than the previous cutset depth for a source-bound separator admitted by this pod's larger exact-work budget",parent=id,priority=95)
   q.update(max_cutset=20,max_exact_assignments=100000000,max_component_size=26,maximum_admitted_seconds=7200);qlib.enqueue(state,q)
  # Repair failed GPU cases using the original source, new port-matched plan reconstruction and larger root batches.
  for id,r in prior['done'].items():
   old=qs.get(id)
   if r['status']!='FAILED_OR_CAPACITY_BOUND' or not old or old.get('kind')!='gpu_test':continue
   key=('gpu',old.get('N'),old.get('variant'))
   if key in seen:continue
   seen.add(key);plan=old.get('plan') or {};q=qlib.qmake('gpu_test',old['N'],variant=old.get('variant'),why='Recompute exact GPU arithmetic after rebuilding the route for this source and retained-port order',parent=id,priority=100)
   q.update(plan=None,candidate_cutset=plan.get('selected',{}).get('cutset',[]),gpu_route='source_replanned',root_batch=64,maximum_admitted_seconds=7200,gpu_seconds=7000);qlib.enqueue(state,q)
  # Add structurally diverse canonical anchors, keeping same-N source changes as separate variants.
  for n in [72,84,90,96,99,100,101,104,105,106,108,112,116,120]:
   row=next(x for x in load(ROOT/'ATLAS_ROWS.json') if x['N']==n)
   if row['pre_minfill_width']<=30 or n in [96,100,105,120]:
    for cut in [[],[v for v in range(n) if v not in canonical(n)['spectrum'].get('retained_ports',[])][:4]]:
     q=qlib.qmake('gpu_test',n,why='Compare full exact GPU transforms on a source-bound plan admitted under the larger pod budget',priority=80)
     q.update(plan=None,candidate_cutset=cut,gpu_route='minfill' if not cut else 'separator_control',root_batch=64,maximum_admitted_seconds=7200,gpu_seconds=7000);qlib.enqueue(state,q)
    q=qlib.qmake('planning',n,why='Generate additional same-N structural alternatives and compare their exact work predictions',priority=55,seed=512,neutral=0);qlib.enqueue(state,q)
  # Higher root-batch experiments follow qualification; all prior full-density checks remain intact.
  q=qlib.qmake('gpu_test',12,why='Re-qualify the upgraded CUDA route at root batch128 on an independent exact small source',priority=1000)
  q.update(plan=None,candidate_cutset=[],gpu_route='minfill',root_batch=128,maximum_admitted_seconds=7200,gpu_seconds=7000);qlib.enqueue(state,q)
  state['gpu_qualified']=False
  state['gpu_qualified']=False
 active={};finished=0;lastsync=0;lastsummary=0
 def checkpoint(status):
  state.update(status=status,updated=time.time(),inflight=[v['q'] for v in active.values()]);save(P/'STATE.json',state)
  save(P/'STATUS.json',dict(status=status,pid=os.getpid(),started_utc=stamp(state['started']),deadline_utc=stamp(state['deadline']),completed=len(state['completed']),attempted=len(state['done']),pending=len(state['queue']),active_workers=len(active),worker_limit=28,gpu_worker_limit=20,cpu_worker_limit=8,worker_pids=[x['proc'].pid for x in active.values()],generated_from_results=state['generated'],hosted_calls=0,gpu_qualified=state.get('gpu_qualified'),stop_command=f'kill -TERM {os.getpid()}',resource_policy='pod resource-manager snapshot; cgroup-aware 20-MIG GPU + 8-CPU ceiling; up to20GiB perCPU worker; device VRAM queried at admission; no intentional swap; local-container scratch; separate volume checkpoint mirror',current_questions=[v['q']['question'] for v in active.values()]))
 def sync():
  mirror=Path('/workspace/gen4/runs/frustrated-spin-learning-podrun2');mirror.mkdir(parents=True,exist_ok=True)
  subprocess.run(['rsync','-r','--size-only','--exclude','__pycache__','--exclude','cuda_cache','--exclude','*.tmp','--exclude','controller.lock']+['--exclude=experiments/'+v['q']['question_id'] for v in active.values()]+[str(P)+'/',str(mirror)+'/'],check=True,stdout=subprocess.DEVNULL)
  for name in ['STATE.json','STATUS.json','QUESTION_LEDGER.jsonl','COUNTEREXAMPLES.jsonl','RULE_CANDIDATES.jsonl','CERTIFICATES.jsonl','STRUCTURAL_DISCOVERIES.jsonl','SEPARATOR_FINDINGS.jsonl','GPU_SCORECARD.json','METHOD_SCORECARD.csv','METHOD_MODELS.json','SUMMARY.md','FRONTIER.json','NEXT_QUESTIONS.json','RUN.log']:
   src=P/name
   if src.exists():
    tmp=mirror/(name+'.sync.tmp');shutil.copyfile(src,tmp);tmp.replace(mirror/name)
 checkpoint('RUNNING')
 try:
  while True:
   now=time.time()
   for slot,item in list(active.items()):
    proc=item['proc'];q=item['q'];out=item['out'];id=q['question_id'];elapsed=now-item['start'];rc=proc.poll()
    if rc is None and (stop or now>=state['deadline']-10 or elapsed>q['maximum_admitted_seconds']):
     os.killpg(proc.pid,signal.SIGTERM)
     try:proc.wait(timeout=5)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
     rc=proc.returncode
    if rc is None:continue
    item['log'].close();kids=[];error=None;ok=False
    try:
     if rc:raise RuntimeError((out/'EXECUTION.log').read_text()[-1800:])
     r=load(out/'RESULT.json');v=r['value']
     if q['kind']=='gpu_test':
      if v['status']!='EXACT':raise RuntimeError('GPU checkpoint retained without full exact completion')
      if q['N']==12:state['gpu_qualified']=True
      elif q.get('root_batch',64)<128:
       child=qlib.qmake('gpu_test',q['N'],why='Does a larger root batch reduce the measured bottleneck on the same exact source and plan?',parent=id,priority=35);child.update(plan=None,candidate_cutset=(q.get('plan') or {}).get('selected',{}).get('cutset',[]),root_batch=128,maximum_admitted_seconds=7200);qlib.enqueue(state,child);kids.append(child['question_id'])
     elif q['kind']=='separator_frontier':
      sep=v['separator']
      if sep['admit_exact']:
       child=qlib.qmake('paired',q['N'],['variable_elimination','conditional_components'],q.get('variant'),why='Does the newly admitted larger separator improve exact cost against elimination?',parent=id,priority=70);child.update(candidate_cutset=sep['cutset'],max_cutset=20,max_exact_assignments=100000000,max_component_size=26,max_exact_seconds=7000,maximum_admitted_seconds=7200,repeats=2);qlib.enqueue(state,child);kids.append(child['question_id'])
      append(P/'SEPARATOR_FINDINGS.jsonl',dict(question_id=id,parent=q.get('parent_question'),N=q['N'],**sep))
     else:
      kids=qlib.follow(state,q,r)
      if q['kind']=='planning' and not q.get('variant'):
       plans=sorted(v['plans'],key=lambda x:x['selected']['weighted_entries']);chosen=[]
       for plan in plans:
        sig=(tuple(plan['selected']['cutset']),tuple(plan['selected']['order']))
        if sig in chosen:continue
        chosen.append(sig);child=qlib.qmake('gpu_test',q['N'],why='Measure structurally distinct exact GPU plans chosen by predicted arithmetic work',parent=id,priority=55);child.update(plan=None,candidate_cutset=plan['selected'].get('cutset',[]),maximum_admitted_seconds=7200,root_batch=64);child['question_id']=qlib.digest(dict(parent=id,plan=plan))[:24];qlib.enqueue(state,child);kids.append(child['question_id'])
        if len(chosen)==3:break
     state['completed'][id]=dict(id=id,result=str((out/'RESULT.json').relative_to(P)),question=q);ok=True
    except Exception:error=traceback.format_exc()
    state['done'][id]=dict(status='COMPLETE' if ok else 'FAILED_OR_CAPACITY_BOUND',seconds=elapsed,error=error,next_questions=kids)
    if not ok:
     append(P/'COUNTEREXAMPLES.jsonl',dict(question=id,error=error,meaning='route capacity or execution failure; not a mathematical counterexample'))
     # The beam-search port exclusion correction licenses one explicitly linked rerun, never an automatic retry loop.
     if q['kind']=='paired' and not q.get('cutset_port_repair') and error and 'KeyError' in error:
      ports=canonical(q['N'])['spectrum'].get('retained_ports',list(range(min(4,q['N']))));candidate=[v for v in q.get('candidate_cutset',[]) if v not in ports]
      child=qlib.qmake('paired',q['N'],q['methods'],q.get('variant'),why='Repeat the admitted exact comparison with the separator search excluding retained-port vertices',parent=id,priority=95)
      child.update(candidate_cutset=candidate,cutset_port_repair=True,max_cutset=20,max_exact_assignments=100000000,max_component_size=26,max_exact_seconds=7000,maximum_admitted_seconds=7200,repeats=1)
      child['question_id']=qlib.digest(dict(parent=id,question=child['question'],cutset=candidate,repair='exclude-retained-ports'))[:24];qlib.enqueue(state,child);kids.append(child['question_id'])
    append(P/'QUESTION_LEDGER.jsonl',dict(event='RESULT',question_id=id,**state['done'][id]));del active[slot];finished+=1;checkpoint('RUNNING')
   if stop or (P/'STOP').exists() or now>=state['deadline']-10:
    stop_requested=True
    if not active:checkpoint('DEADLINE' if now>=state['deadline']-10 else 'STOPPED');break
    stopped();continue
   if args.test and finished>=args.test:
    if not active:checkpoint('BOUNDED_TEST_COMPLETE');break
    continue
   budget=gate()
   if not budget['admitted']:
    stopped();state['resource_failure']=budget;continue
   state['queue']=[q for q in state['queue'] if q['question_id'] not in state['done'] and all(q['question_id']!=v['q']['question_id'] for v in active.values())]
   state['queue'].sort(key=lambda q:-q['expected_information_gain']/max(.1,q['predicted_cost_seconds']))
   for slot in range(min(28,budget['slots'])):
    if slot in active or (args.test and finished+len(active)>=args.test):continue
    gpu_active=sum(1 for v in active.values() if v['q']['kind']=='gpu_test');cpu_active=len(active)-gpu_active
    eligible=[q for q in state['queue'] if (q['kind']=='gpu_test' and gpu_active<budget['gpu_slots']) or (q['kind']!='gpu_test' and cpu_active<budget['cpu_slots'])]
    if not eligible:break
    q=eligible[0];state['queue'].remove(q);id=q['question_id'];out=P/'experiments'/id;out.mkdir(parents=True,exist_ok=True)
    q['checkpoint_dir']=q.pop('resume_checkpoint_dir',str(out/'gpu_checkpoint'));q.setdefault('maximum_admitted_seconds',7200);q.setdefault('max_cutset',20);q.setdefault('max_exact_assignments',100000000);q.setdefault('max_component_size',26);q.setdefault('max_exact_seconds',7000);q.setdefault('gpu_seconds',7000);q.setdefault('root_batch',64);save(out/'PRECOMMIT.json',dict(**q,timestamp=stamp(now),resource_gate=budget,worker_slot=slot,gpu_uuid=(devices[gpu_active] if q['kind']=='gpu_test' else None),worker_ram_cap_bytes=budget['worker_ram_cap_bytes'],code_sha256=sha(P/'operations.py')));append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',**q))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=devices[gpu_active if q['kind']=='gpu_test' else 0],CUPY_CACHE_DIR=str(P/'cuda_cache'/str(slot)),PYTHONDONTWRITEBYTECODE='1');log=(out/'EXECUTION.log').open('a');proc=subprocess.Popen([sys.executable,str(P/'worker.py'),str(out/'PRECOMMIT.json'),str(out)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    active[slot]=dict(proc=proc,q=q,out=out,log=log,start=now);checkpoint('RUNNING')
   if not active and not state['queue']:checkpoint('SEARCH_SATURATED');break
   if not active and state['queue'] and not state.get('gpu_qualified') and all(q['kind']=='gpu_test' and q['N']!=12 for q in state['queue']):checkpoint('GPU_QUALIFICATION_BLOCKED');break
   if now-lastsummary>120:campaign_summary(state);lastsummary=now
   if now-lastsync>300:sync();lastsync=now
   time.sleep(1)
 finally:
  for item in active.values():
   if item['proc'].poll() is None:
    os.killpg(item['proc'].pid,signal.SIGTERM)
    try:item['proc'].wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(item['proc'].pid,signal.SIGKILL);item['proc'].wait()
  checkpoint(state['status']);campaign_summary(state);sync()
if __name__=='__main__':main()
