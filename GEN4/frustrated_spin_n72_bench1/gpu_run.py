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
DEVICES=int(sys.argv[2]);BATCH=int(sys.argv[3]);assert 1<=DEVICES<=14 and BATCH>0
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
import multiprocessing as mp
ctx=mp.get_context('fork')
barrier=ctx.Barrier(DEVICES)
TASKS=[(pi,lo,min(512,lo+BATCH)) for pi in range(len(plan['primes'])) for lo in range(0,512,BATCH)]
def worker(device):
    worker_start=time.perf_counter();cpu_start=time.process_time();profile=[]
    with cp.cuda.Device(device):
        kernel=cp.RawKernel(CUDA,'step')
        maps=[[cp.asarray(m,dtype=cp.uint32) for m in group] for group in cache.maps]
        bits=[cp.asarray([x['eliminated_factor_bit'] for x in s['maps']],dtype=cp.uint32) for s in desc['steps']]
        map_ptr=[cp.asarray([m.data.ptr for m in group],dtype=cp.uint64) for group in maps]
        kernel.compile()
        cp.cuda.get_current_stream().synchronize()
        device_setup=time.perf_counter()-worker_start
        barrier.wait(timeout=120)
        results=[];start=time.perf_counter();batches=0
        for ti,(pi,lo,hi) in enumerate(TASKS):
            if ti % DEVICES != device:continue
            prime=plan['primes'][pi];batch=hi-lo
            batch_started=time.perf_counter()
            factors=[(tuple(f.scope),cp.asarray(f.values,dtype=cp.uint32)) for f in exact._initial_factors(local,engine._zeta_points(prime,512,lo,hi),prime)]
            assert b.canonical_sha256([list(s) for s,v in factors])==desc['initial_factor_scope_sha256']
            prep_seconds=time.perf_counter()-batch_started
            begin=cp.cuda.Event();end=cp.cuda.Event();begin.record()
            for si,s in enumerate(desc['steps']):
                selected=[f for f in factors if s['vertex'] in f[0]]
                factors=[f for f in factors if s['vertex'] not in f[0]]
                assert [list(f[0]) for f in selected]==[x['factor_scope'] for x in s['maps']]
                shape=(1<<len(s['output_scope']),batch)
                out=cp.empty(shape,dtype=cp.uint32)
                ptr=cp.asarray([v.data.ptr for _,v in selected],dtype=cp.uint64)
                n=out.size
                kernel(((n+255)//256,),(256,),(ptr,map_ptr[si],bits[si],out,np.uint64(n),np.int32(batch),np.int32(len(selected)),np.uint32(prime),np.uint64((1<<64)//prime)))
                factors.append((tuple(s['output_scope']),out))
            end.record()
            terminal=cp.ones((16,batch),dtype=cp.uint64)
            for scope,values in factors:
                idx=engine._project_indices(np.arange(16,dtype=np.uint64),ports,scope)
                terminal=(terminal*values[cp.asarray(idx)].astype(cp.uint64))%prime
            results.append((pi,lo,hi,cp.asnumpy(terminal).tolist()));batches+=1
            profile.append({'prime_index':pi,'lo':lo,'hi':hi,'prepare_seconds':prep_seconds,'elimination_stream_ms':cp.cuda.get_elapsed_time(begin,end),'batch_seconds':time.perf_counter()-batch_started,'device_pool_bytes':cp.get_default_memory_pool().total_bytes()})
        return results,{'gpu':device,'device_setup_seconds':device_setup,'cpu_seconds':time.process_time()-cpu_start,'host_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'profile':profile,'seconds':time.perf_counter()-start,'roots':sum(x[2]-x[1] for x in results),'batches':batches,'name':cp.cuda.runtime.getDeviceProperties(device)['name'].decode(),'pool_peak_bytes':cp.get_default_memory_pool().total_bytes()}
event(event='GPU_WORKERS_START',source_instance=binding['source_instance'],devices=DEVICES,batch=BATCH)
with concurrent.futures.ProcessPoolExecutor(max_workers=DEVICES,mp_context=ctx) as pool:
    lanes=list(pool.map(worker,range(DEVICES)))
gpu_wall=time.perf_counter()-t0
assembled=[np.zeros((16,512),dtype=np.int64) for _ in plan['primes']]
coverage=np.zeros((len(plan['primes']),512),dtype=np.int64)
for rows,metrics in lanes:
    for pi,lo,hi,values in rows:
        assembled[pi][:,lo:hi]=np.array(values,dtype=np.int64);coverage[pi,lo:hi]+=1
assert np.all(coverage==1)
save('COVERAGE.json',{'roots':int(coverage.size),'minimum':int(coverage.min()),'maximum':int(coverage.max()),'workers':[x[1] for x in lanes]})
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
reconstruction_seconds=time.perf_counter()-t0-gpu_wall
fiber_started=time.perf_counter()
h=r.load_h14d_module();inherited,w10=h.t18_compatibility()
opened,routing=h.h14.fiber_engine.build_open_port_attachment(w10)
closed=h.h14.fiber_engine.build_closed_n72_attachment(op,recovery['fixed_coefficients'],routing)
save('T18.json',{'inherited':inherited,'open':opened,'closed':closed})
result={'status':'EXACT_N72_GPU_COMPLETE','devices':DEVICES,'batch':BATCH,'source_setup_seconds':source_setup_seconds,'reconstruction_seconds':reconstruction_seconds,'fiber_seconds':time.perf_counter()-fiber_started,'source_instance':binding['source_instance'],'total_seconds':time.perf_counter()-t0,'through_gpu_seconds':gpu_wall,'workers':[x[1] for x in lanes],'prime_hashes':checks,'fixed_coefficient_sha256':recovery['fixed_coefficient_sha256'],'configuration_count':recovery['observed_configuration_count'],'bins':recovery['occupied_energy_bins'],'t18_checks_passed':inherited['all_checks_passed'],'backend':'source-bound H14F successor; GPU elimination; CPU NTT CRT T18'}
save('RESULT.json',result);event(**result)
cache.close()
cache_path.unlink()
