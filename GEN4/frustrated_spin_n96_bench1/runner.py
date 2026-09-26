"""Exact N96 source-bound successor: 14 RAM-first graph workers, CPU fiber."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import sys,json,time,ctypes,queue,multiprocessing as mp,traceback,concurrent.futures
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ORIGINAL=Path(os.environ['GEN4_N96_SOURCE'])/'SAM_REVIEW/campaigns/GEN3_POD_N96_H100X8_PREP1'
sys.path.insert(0,str(ORIGINAL));import run as old
sys.path.insert(0,str(HERE))
from gpu_graph import GPUWorker
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False);BATCH=int(sys.argv[2]);DEVICES=14
start=time.perf_counter();manifest=old.verify_sources();authority,templates,branches,desc=old.source();a=old.a

def save(name,v):(OUT/name).write_text(json.dumps(v,indent=2)+'\n')

def event(**v):v['elapsed_seconds']=time.perf_counter()-start;save('STATUS.json',v);print(json.dumps(v),flush=True)

save('SOURCE.json',{'manifest':manifest,'source':authority[0]['instance_sha256'],'branches':32,'roots':4096,'workers':14,'batch':BATCH,'RAM_first':True});save('GRAPH.json',desc)
cache_path=OUT.parent/'projection.bin';save('CACHE.json',a.build_cache_file(cache_path,desc));cache=a.open_cache_file(cache_path,desc)
ctx=mp.get_context('fork');jobs=ctx.Queue();answers=ctx.Queue();gate=ctx.Event();shutdown=ctx.Event();roster=old.tasks(BATCH)
for job in roster:jobs.put(job)
for _ in range(DEVICES):jobs.put(None)

def worker(device):
 try:
  trace=ctypes.CDLL('/opt/gen4/n72-benchmark1/activity.so');trace.trace_end.argtypes=[ctypes.c_char_p];assert trace.trace_begin()==0
  t=time.perf_counter();gpu=GPUWorker(device,a,templates,desc,cache,BATCH)
  answers.put(('READY',device,{'seconds':time.perf_counter()-t,'pool_bytes':gpu.cp.get_default_memory_pool().total_bytes()}));gate.wait()
  def demand():
   began=time.perf_counter();job=jobs.get()
   if job is None:return None
   prepared=gpu.prepare(job);return prepared,began,time.perf_counter()
  current=demand()
  while current:
   prepared,demand_start,prepared_at=current;t=time.perf_counter();events=gpu.launch(prepared)
   following=demand();values,ms=gpu.result(prepared,events);end=time.perf_counter()
   answers.put(('BATCH',device,{'task':prepared[0],'values':values.tolist(),'demand_start':demand_start,'prepared_at':prepared_at,'started_at':t,'ended_at':end,'graph_stream_ms':ms,'pool_bytes':gpu.cp.get_default_memory_pool().total_bytes()}));current=following
  assert trace.trace_end(str(OUT/('GPU'+str(device)+'_KERNELS.csv')).encode())==0
  answers.put(('DONE',device,None));shutdown.wait(timeout=600)
 except BaseException:
  answers.put(('ERROR',device,traceback.format_exc()));raise

processes=[ctx.Process(target=worker,args=(i,)) for i in range(DEVICES)]
seen=set();values=[np.zeros((16,1024),dtype=np.int64) for _ in range(4)];coverage=np.zeros((4,1024),dtype=np.uint8);counts=[0]*14;profiles=[];boot=[];done=0

def receive():
 try:msg=answers.get(timeout=2)
 except queue.Empty:
  failed=[(i,p.exitcode) for i,p in enumerate(processes) if p.exitcode is not None]
  if failed:raise RuntimeError(('WORKER_EXIT',failed))
  return None
 if msg[0]=='ERROR':raise RuntimeError(msg[2])
 return msg

try:
 for p in processes:p.start()
 event(status='INITIALIZING_14_GRAPH_WORKERS')
 while len(boot)<14:
  msg=receive()
  if msg is None:continue
  assert msg[0]=='READY';boot.append({'gpu':msg[1],**msg[2]});event(status='WORKER_READY',ready=len(boot))
 ready_at=time.perf_counter();gate.set();last_report=ready_at
 lane_futures={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as cpu:
  while done<14:
   msg=receive()
   if msg is None:continue
   kind,device,data=msg
   if kind=='DONE':done+=1;continue
   assert kind=='BATCH';pi,lo,hi=data['task'];assert (pi,lo,hi) not in seen;seen.add((pi,lo,hi))
   values[pi][:,lo:hi]=data.pop('values');coverage[pi,lo:hi]+=1;counts[device]+=hi-lo;data['gpu']=device;profiles.append(data)
   if np.all(coverage[pi]==1) and pi not in lane_futures:
    lane_futures[pi]=cpu.submit(old.lane_from_values,pi,values[pi],fresh=True,workers_active=True,reserve_ok=True)
   if time.perf_counter()-last_report>2:
    event(status='GPU_ROOTS',completed_roots=sum(counts),total_roots=4096,roots_per_gpu=counts);last_report=time.perf_counter()
  assert np.all(coverage==1) and len(seen)==len(roster) and all(counts)
  gpu_done=time.perf_counter();lanes=[lane_futures[i].result() for i in range(4)]
 for i,lane in enumerate(lanes):save('PRIME_'+str(i)+'.json',lane)
 fiber_start=time.perf_counter();op,checks=old.assemble(authority,lanes,OUT);assert all(checks.values())
 finished=time.perf_counter();save('BATCH_PROFILES.json',profiles)
 result={'status':'EXACT_N96_COMPLETE','source_instance':authority[0]['instance_sha256'],'configuration_count':str(1<<96),'checks':checks,'workers':14,'roots_per_gpu':counts,'fresh_roots':4096,'cutset_branches':32,'initialization_seconds':ready_at-start,'ready_to_answer_seconds':finished-ready_at,'through_gpu_seconds':gpu_done-ready_at,'fiber_seconds':finished-fiber_start,'answer_seconds':finished-start,'worker_boot':boot,'batch':BATCH,'storage':'RAM working set; checkpoint after native return','backend':'14 resident CUDA graph workers; packed CPU factors; two VRAM banks; original N96 NTT/CRT/directional fiber'}
 shutdown.set()
 for p in processes:p.join(timeout=30);assert p.exitcode==0
 result['lifecycle_seconds']=time.perf_counter()-start;save('RESULT.json',result);event(**result)
finally:
 shutdown.set()
 for p in processes:
  if p.is_alive():p.terminate()
 for p in processes:
  if p.pid is not None:p.join(timeout=5)
 cache.close()
 if cache_path.exists():cache_path.unlink()
