"""Source-bound experimental successor: H14F graph on two persistent CUDA workers.
CPU retains exact NTT/CRT and the source T18 open/closed attachments.
No installed binding or frozen campaign is modified.
"""
import os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,time,hashlib,importlib.util,concurrent.futures,threading
from pathlib import Path
import resource
import numpy as np
import cupy as cp
ROOT=Path(os.environ['GEN4_N72_SOURCE'])
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('retained',ROOT/'SAM_REVIEW/campaigns/GEN2_R4_EXACT_DENSE_N72_1/candidate/retained_runner.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
b=r.base
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False)
DEVICES=int(sys.argv[2]);BATCH=int(sys.argv[3]);TRIALS=int(sys.argv[4]);assert 1<=DEVICES<=14 and BATCH>0
t0=time.perf_counter()
def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def event(**data):
    data['elapsed_seconds']=time.perf_counter()-t0
    print(json.dumps(data),flush=True);save('STATUS.json',data)
binding=b.load_json(ROOT/'CURRENT_REVISION/engines/SLC/gen2/DENSE_N72_BINDING.json')
for f in binding['files']:
    assert b.sha256_file(ROOT/f['path'])==f['sha256'],f['path']
save('SOURCE_BINDING.json',binding)
engine=b.load_engine(b.ENGINE_PATH,'n72_gpu_source')
instance=b.load_json(b.INSTANCE_PATH);engine.validate_n72_instance(instance)
ownership=engine.factor_ownership(instance);local=engine._local_instance(instance,ownership)
plan=r.build_plan(b.load_json(r.H14D_PLAN),b.load_json(r.U32_RESULT),'GPU1')
ports=tuple(plan['port_order']);exact=engine._modules()[1]
desc=b.compile_descriptor(engine,local,plan['conditional_order'],ports)
cache_path=Path(os.environ['GEN4_N72_BULK'])/(OUT.name+'-projection.bin');cache_receipt=b.build_cache_file(cache_path,desc)
cache=b.open_cache_file(cache_path,desc)
save('GRAPH.json',desc)
save('CACHE_RECEIPT.json',cache_receipt)
source_setup_seconds=time.perf_counter()-t0
h14e=b.load_json(r.H14E_RESULT)
CUDA=r'''
extern "C" __global__ void step(const unsigned long long* fs,const unsigned long long* ms,const unsigned int* bits,unsigned int* out,unsigned long long n,int batch,int nf,unsigned int p,unsigned long long reciprocal){
 unsigned long long i=(unsigned long long)blockIdx.x*blockDim.x+threadIdx.x;
 if(i>=n)return;
 unsigned long long row=i/batch;unsigned int root=i%batch;unsigned long long a=1,b=1;
 for(int k=0;k<nf;k++){
 const unsigned int* f=(const unsigned int*)fs[k];const unsigned int* m=(const unsigned int*)ms[k];
 unsigned long long z=m[row],o=z|bits[k];
 unsigned long long v=a*f[z*batch+root],q=__umul64hi(v,reciprocal);a=v-q*p;if(a>=p)a-=p;
 v=b*f[o*batch+root];q=__umul64hi(v,reciprocal);b=v-q*p;if(b>=p)b-=p;
 }
 unsigned long long s=a+b;out[i]=(unsigned int)(s>=p?s-p:s);
}
'''
(OUT/'kernel.cu').write_text(CUDA)

import multiprocessing as mp,queue,ctypes
ctx=mp.get_context('fork')
prep_started=time.perf_counter()
INPUTS={}
for pi,prime in enumerate(plan['primes']):
 for lo in range(0,512,BATCH):
  hi=min(512,lo+BATCH)
  INPUTS[pi,lo]=[(tuple(f.scope),np.asarray(f.values,dtype=np.uint32)) for f in exact._initial_factors(local,engine._zeta_points(prime,512,lo,hi),prime)]
input_prepare_seconds=time.perf_counter()-prep_started
fiber_prep_started=time.perf_counter()
h=r.load_h14d_module();inherited,w10=h.t18_compatibility()
opened,routing=h.h14.fiber_engine.build_open_port_attachment(w10)
fiber_prepare_seconds=time.perf_counter()-fiber_prep_started
jobs=ctx.Queue();answers=ctx.Queue();ready=ctx.Event();shutdown=ctx.Event()
for trial in range(TRIALS):
 for pi in range(len(plan['primes'])):
  for lo in range(0,512,BATCH):jobs.put((trial,pi,lo,min(512,lo+BATCH)))
for _ in range(DEVICES):jobs.put(None)

TERMINAL_CUDA=r"""
extern "C" __global__ void finish(const unsigned long long* fs,const unsigned long long* maps,unsigned long long* out,int nf,int batch,unsigned int prime){
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=16*batch)return;
 int state=i/batch,root=i%batch;unsigned long long value=1;
 for(int f=0;f<nf;f++){const unsigned int* values=(const unsigned int*)fs[f];const unsigned int* idx=(const unsigned int*)maps[f];value=(value*values[idx[state]*batch+root])%prime;}
 out[i]=value;
}
"""
def worker(device):
 with cp.cuda.Device(device):
  trace=ctypes.CDLL('/opt/gen4/n72-benchmark1/activity.so');trace.trace_end.argtypes=[ctypes.c_char_p]
  assert trace.trace_begin()==0
  started=time.perf_counter();kernel=cp.RawKernel(CUDA,'step');kernel.compile();finish=cp.RawKernel(TERMINAL_CUDA,'finish');finish.compile()
  maps=[[cp.asarray(m,dtype=cp.uint32) for m in group] for group in cache.maps]
  bits=[cp.asarray([x['eliminated_factor_bit'] for x in step['maps']],dtype=cp.uint32) for step in desc['steps']]
  map_ptr=[cp.asarray([m.data.ptr for m in group],dtype=cp.uint64) for group in maps]
  banks=[]
  for bankid in range(2):
   initial=[(scope,cp.asarray(values)) for scope,values in INPUTS[0,0]]
   factors=initial.copy();keep=[];steps=[]
   for si,step in enumerate(desc['steps']):
    selected=[f for f in factors if step['vertex'] in f[0]];factors=[f for f in factors if step['vertex'] not in f[0]]
    assert [list(f[0]) for f in selected]==[x['factor_scope'] for x in step['maps']]
    out=cp.empty((1<<len(step['output_scope']),BATCH),dtype=cp.uint32)
    ptr=cp.asarray([v.data.ptr for _,v in selected],dtype=cp.uint64);keep.extend([out,ptr]);steps.append((si,out,ptr,len(selected)))
    factors.append((tuple(step['output_scope']),out))
   indices=[cp.asarray(engine._project_indices(np.arange(16,dtype=np.uint64),ports,scope),dtype=cp.uint32) for scope,_ in factors]
   final_ptr=cp.asarray([v.data.ptr for _,v in factors],dtype=cp.uint64);index_ptr=cp.asarray([v.data.ptr for v in indices],dtype=cp.uint64)
   terminal=cp.empty((16,BATCH),dtype=cp.uint64);graphs=[];capture=cp.cuda.Stream(non_blocking=True)
   cp.cuda.get_current_stream().synchronize()
   for prime in plan['primes']:
    with capture:
     capture.begin_capture()
     for si,out,ptr,nf in steps:
      n=out.size;kernel(((n+255)//256,),(256,),(ptr,map_ptr[si],bits[si],out,np.uint64(n),np.int32(BATCH),np.int32(nf),np.uint32(prime),np.uint64((1<<64)//prime)))
     finish(((terminal.size+255)//256,),(256,),(final_ptr,index_ptr,terminal,np.int32(len(factors)),np.int32(BATCH),np.uint32(prime)))
     graphs.append(capture.end_capture())
   banks.append({'initial':initial,'graphs':graphs,'terminal':terminal,'keep':keep,'indices':indices,'final_ptr':final_ptr,'index_ptr':index_ptr})
  cp.cuda.get_current_stream().synchronize()
  answers.put(('READY',device,time.perf_counter()-started));ready.wait()
  copy_stream=cp.cuda.Stream(non_blocking=True);nextbank=0
  def demand():
   nonlocal nextbank
   demand_at=time.perf_counter();job=jobs.get()
   if job is None:return None
   trial,pi,lo,hi=job;assert hi-lo==BATCH
   bank=banks[nextbank];nextbank=1-nextbank
   with copy_stream:
    for (scope,target),(source_scope,values) in zip(bank['initial'],INPUTS[pi,lo]):
     assert scope==source_scope;target.set(values,stream=copy_stream)
    copied=cp.cuda.Event();copied.record()
   return job,bank,copied,demand_at,time.perf_counter()
  current=demand()
  while current is not None:
   (trial,pi,lo,hi),bank,copied,demand_at,prepared_at=current
   stream=cp.cuda.get_current_stream();stream.wait_event(copied)
   batch_started=time.perf_counter();cpu_start=time.process_time();begin=cp.cuda.Event();end=cp.cuda.Event();begin.record()
   bank['graphs'][pi].launch(stream)
   end.record();next_item=demand();values=cp.asnumpy(bank['terminal']).tolist();ended=time.perf_counter()
   answers.put(('BATCH',device,trial,pi,lo,hi,values,{'demand_at':demand_at,'prepared_at':prepared_at,'started_at':batch_started,'ended_at':ended,'seconds':ended-batch_started,'cpu_seconds':time.process_time()-cpu_start,'elimination_stream_ms':cp.cuda.get_elapsed_time(begin,end),'pool_bytes':cp.get_default_memory_pool().total_bytes(),'cuda_graph_nodes':69}))
   current=next_item
  cp.cuda.get_current_stream().synchronize()
  assert trace.trace_end(str(OUT/('GPU'+str(device)+'_KERNELS.csv')).encode())==0
  answers.put(('DONE',device,time.perf_counter()));shutdown.wait(timeout=180)

def reconstruct(trial,assembled,metrics,trial_start,gpu_wall):
 assembly_start=time.perf_counter();out=OUT/('trial'+str(trial));out.mkdir()
 def save(name,data):(out/name).write_text(json.dumps(data,indent=2)+'\n')
 def event(**data):pass
 mods=[];checks=[]
 for pi,prime in enumerate(plan['primes']):
     values=assembled[pi].tolist()
     save('PRIME_'+str(pi)+'.json',{'prime':int(prime),'evaluations':values})
     sha=b.canonical_sha256(values);assert sha==h14e['prime_lanes'][pi]['evaluation_sha256'],(pi,sha)
     checks.append(sha)
     mods.append([[int(v) for v in exact._inverse_ntt(row,prime)] for row in values])
     event(event='PRIME_EXACT_MATCH',prime=int(prime),evaluation_sha256=sha)
 w=[]
 for state in range(16):
     row=[int(exact._crt([m[state][j] for m in mods],plan['primes'])) for j in range(512)]
     assert not any(row[engine.LOCAL_BOUND+1:])
     row=row[:engine.LOCAL_BOUND+1];assert sum(row)==1<<(72-len(ports));w.append(row)
 assert b.canonical_sha256(w)==h14e['operator_w_sha256']
 glue=engine.glue_y_degrees(ownership['cut_edges'],ports)
 op={'schema':'SLCX032_N72_OPERATOR_V1','source_validation':engine.validate_n72_instance(instance),'source_instance_id':instance['instance_id'],'source_instance_sha256':instance['instance_sha256'],'port_freeze_sha256':engine.load_port_freeze()['freeze_sha256'],'port_order':list(ports),'cut_edges':ownership['cut_edges'],'orientation':[list(e) for e in engine.CUT_ENDPOINTS],'factor_ownership':ownership,'w_coefficients':w,'w_sha256':b.canonical_sha256(w),'local_y_degree':engine.LOCAL_BOUND,'expected_row_sum':1<<68,'row_sums':[sum(x) for x in w],'glue_y_degrees':glue,'glue_y_degrees_sha256':b.canonical_sha256(glue),'metrics':{'y_ntt_length':512,'selected_primes':plan['primes'],'conditional_induced_width':plan['conditional_induced_width']}}
 recovery=engine.recover_n72_one_cell(op)
 assert recovery['fixed_coefficient_sha256']==h14e['linked_fixed_coefficient_sha256']
 save('OPERATOR.json',op);save('RECOVERY.json',recovery)
 reconstruction_seconds=time.perf_counter()-assembly_start
 fiber_started=time.perf_counter()
 closed=h.h14.fiber_engine.build_closed_n72_attachment(op,recovery['fixed_coefficients'],routing)
 save('T18.json',{'inherited':inherited,'open':opened,'closed':closed})
 result={'status':'EXACT_N72_GPU_COMPLETE','devices':DEVICES,'batch':BATCH,'source_setup_seconds':source_setup_seconds,'reconstruction_seconds':reconstruction_seconds,'fiber_seconds':time.perf_counter()-fiber_started,'source_instance':binding['source_instance'],'total_seconds':time.perf_counter()-trial_start,'through_gpu_seconds':gpu_wall,'workers':metrics,'prime_hashes':checks,'fixed_coefficient_sha256':recovery['fixed_coefficient_sha256'],'configuration_count':recovery['observed_configuration_count'],'bins':recovery['occupied_energy_bins'],'t18_checks_passed':inherited['all_checks_passed'],'backend':'source-bound H14F successor; GPU elimination; CPU NTT CRT T18'}
 result.update(trial=trial,assembly_started=assembly_start,assembly_finished=time.perf_counter(),fresh_roots=1536,source_factors_reused=True,fiber_structure_reused=True)
 save('RESULT.json',result)
 return result

pool=[ctx.Process(target=worker,args=(i,)) for i in range(DEVICES)]
for process in pool:process.start()
boot=[]
for _ in range(DEVICES):
 msg=answers.get(timeout=120);assert msg[0]=='READY';boot.append(msg)
warm_ready=time.perf_counter();ready.set()
assembled=[ [np.zeros((16,512),dtype=np.int64) for _ in plan['primes']] for _ in range(TRIALS)]
coverage=[np.zeros((3,512),dtype=np.int64) for _ in range(TRIALS)]
metrics=[[] for _ in range(TRIALS)];starts=[None]*TRIALS;done=0;futures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as cpu:
 while done<DEVICES:
  msg=answers.get(timeout=120)
  if msg[0]=='DONE':done+=1;continue
  _,device,trial,pi,lo,hi,values,profile=msg
  assembled[trial][pi][:,lo:hi]=values;coverage[trial][pi,lo:hi]+=1
  assert np.all(coverage[trial]<=1)
  profile.update(gpu=device,prime_index=pi,lo=lo,hi=hi);metrics[trial].append(profile)
  starts[trial]=min(starts[trial] or profile['started_at'],profile['started_at'])
  if np.all(coverage[trial]==1):
   gpu_wall=max(x['ended_at'] for x in metrics[trial])-starts[trial]
   futures.append(cpu.submit(reconstruct,trial,assembled[trial],metrics[trial],starts[trial],gpu_wall))
 results=[f.result() for f in futures]
all_answers_at=time.perf_counter()
shutdown.set()
for process in pool:
 process.join(timeout=30);assert process.exitcode==0
save('COVERAGE.json',{'trials':TRIALS,'fresh_roots':1536*TRIALS,'each_root_exactly_once':all(np.all(c==1) for c in coverage)})
result={'status':'EXACT_N72_PIPELINE_COMPLETE','devices':DEVICES,'batch':BATCH,'trials':results,'initialization_seconds':warm_ready-t0,'warm_pipeline_seconds':all_answers_at-warm_ready,'total_seconds':time.perf_counter()-t0,'input_prepare_seconds':input_prepare_seconds,'fiber_prepare_seconds':fiber_prepare_seconds,'input_bank_bytes':sum(v.nbytes for fs in INPUTS.values() for _,v in fs),'device_boot':boot,'source_instance':binding['source_instance'],'fixed_coefficient_sha256':results[0]['fixed_coefficient_sha256'],'configuration_count':results[0]['configuration_count'],'source_setup_seconds':source_setup_seconds,'t18_checks_passed':all(x['t18_checks_passed'] for x in results),'scheduling':'CUDA graph of 68 exact eliminations plus terminal contraction; double-buffered VRAM banks; persistent demand queue; overlapping CPU reconstruction'}
save('RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='trials'}),flush=True)
cache.close();cache_path.unlink()
