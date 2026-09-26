"""Outcome-driven research using one restored fourteen-GPU team and shared CPU host."""
import os,sys,time,json,signal,subprocess,datetime,fcntl,traceback,shutil,tarfile,re
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
sys.path[:0]=[str(P),str(ROOT)]
import questions as qlib
from operations import load,save,sha,canonical
from research import append
import resource_manager as rm
stop=False
def stopped(*a):
 global stop
 stop=True
signal.signal(signal.SIGTERM,stopped);signal.signal(signal.SIGINT,stopped)
def stamp(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
def gate():
 cpus=sorted(os.sched_getaffinity(0));profile={'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.95,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}}
 b=rm.snapshot(profile,'pod');cg=Path('/sys/fs/cgroup');quota=(cg/'cpu.max').read_text().split();limit=len(cpus) if quota[0]=='max' else int(quota[0])/int(quota[1]);mem=(cg/'memory.max').read_text().strip();avail=b['prelaunch_mem_available'] if mem=='max' else min(b['prelaunch_mem_available'],int(mem)-int((cg/'memory.current').read_text()))
 devices=re.findall(r'UUID: (MIG-[^)]+)',subprocess.check_output(['nvidia-smi','-L'],text=True));assert len(devices)==14
 b.update(cgroup_cpu=limit,cgroup_available_ram=avail,gpu_workers=14,experiment_slots=1,shared_cpu=True,admitted=avail>48*1024**3 and shutil.disk_usage(P).free>10*1024**3 and limit>=14,process_snapshot=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,rss,comm','--sort=-pcpu'],text=True).splitlines()[:20]);return b

def main():
 lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 pool=Path('/opt/gen4/restore14/research-pool.lock').open('a');fcntl.flock(pool,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert load('/opt/gen4/restore14/QUALIFICATION.json')['status']=='PASS'
 state=load(P/'STATE.json');active=None;lastsync=0;lastsummary=0
 for q in state.pop('inflight',[]):
  if q.get('restoration_retry',0)<1:
   q['restoration_retry']=1;state['queue'].insert(0,q)
  else:state['done'][q['question_id']]=dict(status='INTERRUPTED',error='Single restored-route recovery exhausted')
 def checkpoint(status):
  state.update(status=status,updated=time.time(),inflight=[] if active is None else [active['q']]);save(P/'STATE.json',state)
  save(P/'STATUS.json',dict(status=status,pid=os.getpid(),started_utc=stamp(state['started']),deadline_utc=stamp(state['deadline']),completed_this_run=len(state['completed']),inherited_completed=state.get('inherited_completed',0),pending=len(state['queue']),gpu_worker_limit=14,experiment_slots=1,cpu_role='shared preparation, direction/fiber readout, exact reconstruction; no eight-CPU worker pool',active_question=None if active is None else active['q']['question'],active_kind=None if active is None else active['q']['kind'],worker_pid=None if active is None else active['proc'].pid,hosted_calls=0,stop_command=f'kill -TERM {os.getpid()}',restored_runtime='/opt/gen4/current',resource_policy='Original fourteen persistent GPU owners per exact GPU experiment, batched exact readout, RAM/container scratch; resource-manager admission; original campaign deadline; no N121+'))
 def sync():
  # One compact archive, no recursive network-volume tree walk.
  tmp=P/'checkpoint.part';target=P/'checkpoint.tar.gz'
  with tarfile.open(tmp,'w:gz',compresslevel=1) as tar:
   for path in P.iterdir():
    if path.is_file() and path.suffix in ['.json','.jsonl','.md','.csv','.py']:tar.add(path,arcname=path.name)
   if active:
    root=P/'experiments'/active['q']['question_id']/'restored_work'
    if root.exists():
     for f in root.iterdir():
      if f.is_file() and (f.name.startswith(('RESIDUES','PROFILES')) or f.name in ['SOURCE.json','PLAN.json','PROGRESS.json']):tar.add(f,arcname=str(f.relative_to(P)))
   for rec in state['completed'].values():
    d=P/rec['result'];tar.add(d,arcname=str(d.relative_to(P)));pre=d.parent/'PRECOMMIT.json'
    if pre.exists():tar.add(pre,arcname=str(pre.relative_to(P)))
  tmp.replace(target)
  mirror=Path('/workspace/gen4/runs/frustrated-spin-learning-podrun3');mirror.mkdir(parents=True,exist_ok=True)
  try:
   subprocess.run(['timeout','45','cp',str(target),str(mirror/'checkpoint.new.tar.gz')],check=True)
   (mirror/'checkpoint.new.tar.gz').replace(mirror/'checkpoint.tar.gz');shutil.copyfile(P/'STATUS.json',mirror/'STATUS.json')
  except Exception as e:append(P/'SYNC_FAILURES.jsonl',dict(time=time.time(),error=str(e)))
 try:
  checkpoint('RUNNING')
  while not stop and not (P/'STOP').exists() and time.time()<state['deadline']-10:
   state['queue']=[q for q in state['queue'] if q['question_id'] not in state['done']]
   if not state['queue']:checkpoint('SEARCH_SATURATED');break
   budget=gate()
   if not budget['admitted']:state['resource_gate']=budget;checkpoint('RESOURCE_GATE');break
   state['queue'].sort(key=lambda q:-q['expected_information_gain']/max(.1,q['predicted_cost_seconds']));q=state['queue'].pop(0);qid=q['question_id'];out=P/'experiments'/qid;out.mkdir(parents=True,exist_ok=True)
   q['checkpoint_dir']=str(out/'gpu_checkpoint');q['maximum_admitted_seconds']=min(q.get('maximum_admitted_seconds',7200),int(state['deadline']-time.time()-10));q['gpu_seconds']=max(1,q['maximum_admitted_seconds']-20)
   pre=dict(**q,timestamp=stamp(time.time()),resource_gate=budget,execution_configuration='RESTORED_ORIGINAL_14_WORKER_TEAM',code_sha256=sha(P/'operations.py'))
   save(out/'PRECOMMIT.json',pre);append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',**pre));log=(out/'EXECUTION.log').open('a')
   env=dict(os.environ,PYTHONPATH='/opt/gen4/current',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',GEN4_SPIN_SOURCE='/opt/gen4/n96-benchmark1/source',GEN4_SPIN_CATALOG_CODE='/opt/gen4/spin-catalog1',GEN4_SPIN_TRAINING_CODE='/opt/gen4/spin-training1')
   proc=subprocess.Popen([sys.executable,str(P/'worker.py'),str(out/'PRECOMMIT.json'),str(out)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);active=dict(q=q,proc=proc);began=time.time();checkpoint('RUNNING')
   while proc.poll() is None:
    if stop or (P/'STOP').exists() or time.time()>=state['deadline']-10 or time.time()-began>q['maximum_admitted_seconds']:
     os.killpg(proc.pid,signal.SIGTERM)
     try:proc.wait(timeout=5)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
     break
    if time.time()-lastsync>300:checkpoint('RUNNING');sync();lastsync=time.time()
    time.sleep(1)
   log.close();kids=[];error=None
   try:
    if proc.returncode:raise RuntimeError((out/'EXECUTION.log').read_text()[-2200:])
    result=load(out/'RESULT.json');v=result['value']
    if q['kind']=='gpu_test':
     assert v['status']=='EXACT' and v['full_density_equal'] and v['restored_backend']
     alt=q.get('followup_plan')
     if alt:
      child=qlib.qmake('gpu_test',q['N'],why='Does the retained alternative elimination plan explain the cost difference under the restored identical backend?',parent=qid,priority=2000);child.update(restored_plan=alt,repeats=3);qlib.enqueue(state,child);kids.append(child['question_id'])
    else:kids=qlib.follow(state,q,result)
    if q['kind']=='planning' and not q.get('variant'):
     child=qlib.qmake('gpu_test',q['N'],why='Measure exact source-plan cost with the restored persistent GPU team after structural planning',parent=qid,priority=75);qlib.enqueue(state,child);kids.append(child['question_id'])
    state['completed'][qid]=dict(id=qid,result=str((out/'RESULT.json').relative_to(P)),question=q)
    bundle=P/(qid+'.tar.gz')
    with tarfile.open(bundle,'w:gz',compresslevel=1) as archive:archive.add(out,arcname=qid)
    mirror=Path('/workspace/gen4/runs/frustrated-spin-learning-podrun3/experiments');mirror.mkdir(parents=True,exist_ok=True)
    try:subprocess.run(['timeout','45','cp',str(bundle),str(mirror/bundle.name)],check=True)
    except Exception as e:append(P/'SYNC_FAILURES.jsonl',dict(time=time.time(),bundle=str(bundle),error=str(e)))
   except Exception:error=traceback.format_exc();append(P/'COUNTEREXAMPLES.jsonl',dict(question=qid,error=error,meaning='Execution/capacity finding; not a mathematical counterexample'))
   state['done'][qid]=dict(status='COMPLETE' if error is None else 'FAILED_OR_CAPACITY_BOUND',seconds=time.time()-began,error=error,next_questions=kids);append(P/'QUESTION_LEDGER.jsonl',dict(event='RESULT',question_id=qid,**state['done'][qid]));active=None;checkpoint('RUNNING')
   if time.time()-lastsummary>120:
    qlib.summary(state);lastsummary=time.time()
   sync();lastsync=time.time()
  if state['status']=='RUNNING':checkpoint('DEADLINE' if time.time()>=state['deadline']-10 else 'STOPPED')
 except BaseException:
  state['controller_failure']=traceback.format_exc();checkpoint('FAILED');raise
 finally:
  if active and active['proc'].poll() is None:
   os.killpg(active['proc'].pid,signal.SIGTERM)
   try:active['proc'].wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(active['proc'].pid,signal.SIGKILL);active['proc'].wait()
  checkpoint(state['status']);qlib.summary(state);sync()
if __name__=='__main__':main()
