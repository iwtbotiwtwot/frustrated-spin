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
 cpus=sorted(os.sched_getaffinity(0));profile={'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.7,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}}
 b=rm.snapshot(profile,'pod');cg=Path('/sys/fs/cgroup');quota=(cg/'cpu.max').read_text().split();limit=len(cpus) if quota[0]=='max' else int(quota[0])/int(quota[1]);mem=(cg/'memory.max').read_text().strip();available=b['prelaunch_mem_available'] if mem=='max' else min(b['prelaunch_mem_available'],int(mem)-int((cg/'memory.current').read_text()))
 b.update(cgroup_cpu=limit,cgroup_available_ram=available,admitted=available>20*1024**3 and shutil.disk_usage(P).free>10*1024**3 and limit>=2)
 b['process_snapshot']=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,rss,comm','--sort=-pcpu'],text=True).splitlines()[:20]
 b['gpu_processes']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory','--format=csv,noheader'],text=True).strip()
 b['slots']=min(10,max(1,int(min(limit*.7,b['cpu_equivalents']))));return b

def campaign_summary(state):
 qlib.summary(state)
 gpu=[]
 for rec in state['completed'].values():
  if rec['question']['kind']=='gpu_test':
   v=load(P/rec['result'])['value'];gpu.append(dict(question_id=rec['id'],N=v['N'],seconds=v['seconds'],root_batch=v['root_batch'],full_density_equal=v['full_density_equal'],execution=v.get('execution')))
 save(P/'GPU_SCORECARD.json',gpu)
 (P/'SUMMARY.md').open('a').write('\nGPU comparisons: '+str(len(gpu))+' completed, full densities verified. See GPU_SCORECARD.json for stage costs.\nLarger separator findings: see SEPARATOR_FINDINGS.jsonl.\nTen worker ceiling; exact answers remain source-bound. No N121+ execution.\n')

def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--test',type=int,default=0);args=ap.parse_args();lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);os.nice(10)
 devices=re.findall(r'UUID: (MIG-[^)]+)',subprocess.check_output(['nvidia-smi','-L'],text=True));assert len(devices)>=10
 for f in ['QUESTION_LEDGER.jsonl','RULE_CANDIDATES.jsonl','CERTIFICATES.jsonl','STRUCTURAL_DISCOVERIES.jsonl','COUNTEREXAMPLES.jsonl']:(P/f).touch(exist_ok=True)
 if (P/'STATE.json').exists():
  state=load(P/'STATE.json')
  for q in state.pop('inflight',[]):
   state['done'][q['question_id']]=dict(status='INTERRUPTED',seconds=0,error='Recovered interrupted attempt; retained artifacts, no silent retry')
 else:
  state=dict(started=time.time(),deadline=time.time()+8*3600,status='STARTING',queue=[],done={},completed={},seen_structure={},next_seed={},generated=0)
  # The previous failures supply actual parent-question IDs and frozen sources.
  prior=load(ROOT/'followup1/STATE.json');qs={}
  for line in (ROOT/'followup1/QUESTION_LEDGER.jsonl').read_text().splitlines():
   r=json.loads(line)
   if r.get('event')=='PRECOMMIT':qs[r['question_id']]=r
  seen=set()
  for id,r in prior['done'].items():
   old=qs.get(id)
   if r['status']=='COMPLETE' or not old:continue
   key=(old['N'],old.get('variant'))
   if key in seen:continue
   seen.add(key);q=qlib.qmake('separator_frontier',old['N'],variant=old.get('variant'),why='Can separators beyond two spins explain and resolve the previous exact-route capacity boundary?',parent=id,priority=60,max_cutset=12);qlib.enqueue(state,q)
  for n in [96,120,99,100,101,104,105,106,72,84,108]:
   q=qlib.qmake('planning',n,why='Which exact plan best matches this source on the ten-worker pod?',priority=80,seed=512,neutral=3);qlib.enqueue(state,q)
  q=qlib.qmake('gpu_test',12,why='Qualify exact CUDA full-density agreement before larger GPU comparisons',priority=10000);q['plan']=None;q['maximum_admitted_seconds']=660;qlib.enqueue(state,q)
  for n in [72,84,96,100,105,108,120]:
   path,_=qlib.variant(n,'swap',129);qlib.enqueue(state,qlib.qmake('planning',n,variant=path,why='Extend previously saturated structural regimes using new source controls',priority=15,seed=129,neutral=0))
  state['gpu_qualified']=False
 active={};finished=0;lastsync=0;lastsummary=0
 def checkpoint(status):
  state.update(status=status,updated=time.time(),inflight=[v['q'] for v in active.values()]);save(P/'STATE.json',state)
  save(P/'STATUS.json',dict(status=status,pid=os.getpid(),started_utc=stamp(state['started']),deadline_utc=stamp(state['deadline']),completed=len(state['completed']),attempted=len(state['done']),pending=len(state['queue']),active_workers=len(active),worker_limit=10,worker_pids=[x['proc'].pid for x in active.values()],generated_from_results=state['generated'],hosted_calls=0,gpu_qualified=state.get('gpu_qualified'),stop_command=f'kill -TERM {os.getpid()}',resource_policy='existing SLC snapshot with pod profile; cgroup-aware cap; ten workers; one MIG device each; no intentional swap; container scratch; volume checkpoint mirror',current_questions=[v['q']['question'] for v in active.values()]))
 def sync():
  mirror=Path('/workspace/gen4/runs/frustrated-spin-learning-podrun1');mirror.mkdir(parents=True,exist_ok=True)
  subprocess.run(['rsync','-r','--checksum','--exclude','__pycache__','--exclude','cuda_cache','--exclude','*.tmp','--exclude','controller.lock']+['--exclude=experiments/'+v['q']['question_id'] for v in active.values()]+[str(P)+'/',str(mirror)+'/'],check=True,stdout=subprocess.DEVNULL)
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
      elif q.get('root_batch',16)==16:
       child=qlib.qmake('gpu_test',q['N'],why='Does a larger root batch reduce the measured bottleneck on the same exact source and plan?',parent=id,priority=35);child.update(plan=q.get('plan'),root_batch=32,maximum_admitted_seconds=660);qlib.enqueue(state,child);kids.append(child['question_id'])
     elif q['kind']=='separator_frontier':
      sep=v['separator']
      if sep['admit_exact']:
       child=qlib.qmake('paired',q['N'],['variable_elimination','conditional_components'],q.get('variant'),why='Does the newly admitted larger separator improve exact cost against elimination?',parent=id,priority=70);qlib.enqueue(state,child);kids.append(child['question_id'])
      append(P/'SEPARATOR_FINDINGS.jsonl',dict(question_id=id,parent=q.get('parent_question'),N=q['N'],**sep))
     else:
      kids=qlib.follow(state,q,r)
      if q['kind']=='planning' and not q.get('variant'):
       plans=sorted(v['plans'],key=lambda x:x['selected']['weighted_entries']);chosen=[]
       for plan in plans:
        sig=(tuple(plan['selected']['cutset']),tuple(plan['selected']['order']))
        if sig in chosen:continue
        chosen.append(sig);child=qlib.qmake('gpu_test',q['N'],why='Measure structurally distinct exact GPU plans chosen by predicted arithmetic work',parent=id,priority=55);child.update(plan=plan,maximum_admitted_seconds=660);child['question_id']=qlib.digest(dict(parent=id,plan=plan))[:24];qlib.enqueue(state,child);kids.append(child['question_id'])
        if len(chosen)==2:break
     state['completed'][id]=dict(id=id,result=str((out/'RESULT.json').relative_to(P)),question=q);ok=True
    except Exception:error=traceback.format_exc()
    state['done'][id]=dict(status='COMPLETE' if ok else 'FAILED_OR_CAPACITY_BOUND',seconds=elapsed,error=error,next_questions=kids)
    if not ok:append(P/'COUNTEREXAMPLES.jsonl',dict(question=id,error=error,meaning='route capacity or execution failure; not a mathematical counterexample'))
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
   for slot in range(min(10,budget['slots'])):
    if slot in active or (args.test and finished+len(active)>=args.test):continue
    eligible=[q for q in state['queue'] if q['kind']!='gpu_test' or state.get('gpu_qualified') or q['N']==12]
    if not eligible:break
    q=eligible[0];state['queue'].remove(q);id=q['question_id'];out=P/'experiments'/id;out.mkdir(parents=True,exist_ok=True)
    q['checkpoint_dir']=str(out/'gpu_checkpoint');save(out/'PRECOMMIT.json',dict(**q,timestamp=stamp(now),resource_gate=budget,worker_slot=slot,gpu_uuid=devices[slot],code_sha256=sha(P/'operations.py')));append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',**q))
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=devices[slot],CUPY_CACHE_DIR=str(P/'cuda_cache'/str(slot)),PYTHONDONTWRITEBYTECODE='1');log=(out/'EXECUTION.log').open('a');proc=subprocess.Popen([sys.executable,str(P/'worker.py'),str(out/'PRECOMMIT.json'),str(out)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
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
