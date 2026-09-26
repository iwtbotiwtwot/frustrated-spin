"""N120 exact frontier: reusable branch graphs, 14 workers, resumable residues.

The conditioned cutset is summed in branch groups. Every (prime, roots, group)
task contributes exactly once; partial modular sums and coverage are checkpointed.
All research operations execute through a source-bound DomainSession adapter.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import sys,time,json,traceback,ctypes,argparse,math,hashlib,gzip
from pathlib import Path
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE'])
sys.path.insert(0,'/opt/gen4/spin-focused1')
import numpy as np
import engine,fast_readout
from engine import Catalog,save,compressed,emit,Monitor
from arithmetic import a,templates,IndexCache,original,exact
from catalog_gpu import GPUWorker
from planning import digest,ladder,plan,structure
from SAM_PROJECT.session import DomainSession

engine.reconstruct=fast_readout.reconstruct
HERE=Path(__file__).resolve().parent

class Frontier(Catalog):
    def __init__(self,*args,deadline,**kwargs):super().__init__(*args,**kwargs);self.deadline=deadline
    def worker(self,device):
        trace=None
        try:
            import cupy as cp
            cp.cuda.Device(device).use();resident={}
            trace=ctypes.CDLL('/opt/gen4/n72-benchmark1/activity.so');trace.trace_end.argtypes=[ctypes.c_char_p]
            assert trace.trace_begin()==0
            while True:
                command=self.controls[device].get()
                if command[0]=='STOP':break
                _,ci,batch,chunk=command;source,p,ts,desc,cache,stats=self.cases[ci]
                resident.clear();cp.get_default_memory_pool().free_all_blocks();started=time.perf_counter_ns()
                gpu=GPUWorker(device,a,ts[:chunk],desc,cache,batch,p,resident)
                self.answers.put(('READY',device,dict(init_ns=time.perf_counter_ns()-started,pool_bytes=cp.get_default_memory_pool().total_bytes())))
                assert self.controls[device].get()[0]=='GO'
                def demand():
                    task=self.jobs.get()
                    if task is None:return None
                    pi,lo,hi,branchlo=task;gpu.templates=ts[branchlo:branchlo+chunk]
                    prepared=gpu.prepare((pi,lo,hi));return task,prepared
                current=demand()
                while current:
                    task,prepared=current;t=time.perf_counter_ns();events=gpu.launch(prepared);following=demand()
                    values,ms=gpu.result(prepared,events)
                    self.answers.put(('BATCH',device,dict(task=task,values=values.tolist(),started_ns=t,ended_ns=time.perf_counter_ns(),stream_ns=round(ms*1e6))))
                    current=following
                self.answers.put(('DONE',device,None));del gpu,current
        except BaseException:self.answers.put(('ERROR',device,traceback.format_exc()));raise
        finally:
            if trace:trace.trace_end(str(self.ram/f'GPU{device}_KERNELS.csv').encode())

    def checkpoint(self,ci,values,coverage,profiles):
        t=time.perf_counter_ns();tmp=self.ram/f'residues{ci}.part'
        with tmp.open('wb') as f:np.savez(f,values=np.asarray(values),coverage=coverage)
        tmp.replace(self.ram/f'RESIDUES{ci}.npz');save(self.ram/f'PROFILES{ci}.json',profiles)
        # Compact flush; traces and sessions are archived at solve boundaries.
        for name in [f'RESIDUES{ci}.npz',f'PROFILES{ci}.json','PROGRESS.json']:
            src=self.ram/name
            if src.exists():
                dst=self.durable/name;stage=dst.with_suffix(dst.suffix+'.part');stage.write_bytes(src.read_bytes());stage.replace(dst)
        return time.perf_counter_ns()-t

    def solve_chunked(self,ci):
        source,p,ts,desc,cache,stats=self.cases[ci];start=time.perf_counter_ns();batch=16;chunk=min(16,len(ts));assert len(ts)%chunk==0
        if not self.workers:
            self.workers=[self.ctx.Process(target=self.worker,args=(d,)) for d in range(14)]
            for w in self.workers:w.start()
        boot=[]
        for c in self.controls:c.put(('LOAD',ci,batch,chunk))
        while len(boot)<14:
            kind,d,data=self.receive();assert kind=='READY';boot.append(dict(gpu=d,**data))
        ng=len(ts)//chunk;nb=p['root_count']//batch;coverage=np.zeros((ng,len(p['primes']),nb),dtype=np.uint8)
        values=[np.zeros((1<<len(p['ports']),p['root_count']),dtype=np.int64) for _ in p['primes']];profiles=[]
        if (self.ram/f'RESIDUES{ci}.npz').exists():
            old=np.load(self.ram/f'RESIDUES{ci}.npz');coverage=old['coverage'];values=list(old['values']);profiles=json.loads((self.ram/f'PROFILES{ci}.json').read_text());assert coverage.shape==(ng,len(p['primes']),nb)
        roster=[(pi,lo,lo+batch,branchlo) for branchlo in range(0,len(ts),chunk) for lo in range(0,p['root_count'],batch) for pi in range(len(p['primes'])) if not coverage[branchlo//chunk,pi,lo//batch]]
        ready=time.perf_counter_ns();total=ng*len(p['primes'])*nb;completed=int(coverage.sum());prior_completed=completed;sent=0;received=0;stop=False
        # Bounded queue permits a time-reserve stop with complete-task checkpoints.
        for task in roster[:56]:self.jobs.put(task);sent+=1
        if sent==len(roster):
            for _ in self.workers:self.jobs.put(None)
            stop=True
        for c in self.controls:c.put(('GO',))
        done=0;last_checkpoint=time.monotonic();counts=[0]*14
        while done<14:
            kind,d,data=self.receive()
            if kind=='DONE':done+=1;continue
            assert kind=='BATCH';pi,lo,hi,branchlo=data['task'];g=branchlo//chunk
            assert coverage[g,pi,lo//batch]==0
            values[pi][:,lo:hi]=(values[pi][:,lo:hi]+np.asarray(data.pop('values'),dtype=np.int64))%p['primes'][pi]
            coverage[g,pi,lo//batch]=1;completed+=1;received+=1;counts[d]+=1;profiles.append(dict(gpu=d,**data))
            if not stop:
                if time.time()>self.deadline or sent==len(roster):
                    for _ in self.workers:self.jobs.put(None)
                    stop=True
                else:self.jobs.put(roster[sent]);sent+=1
            if time.monotonic()-last_checkpoint>=30 or completed==total:
                elapsed=(time.perf_counter_ns()-ready)/1e9;rate=received/max(elapsed,1e-9);progress=dict(N=source['N'],case=ci,completed_tasks=completed,total_tasks=total,elapsed_seconds=elapsed,estimated_remaining_seconds=(total-completed)/max(rate,1e-9),roots_batch=batch,branches_per_task=chunk,workers=14,time_budget_stop=stop and sent<len(roster))
                save(self.ram/'PROGRESS.json',progress);emit(**progress);self.checkpoint(ci,values,coverage,profiles);last_checkpoint=time.monotonic()
        self.checkpoint(ci,values,coverage,profiles);end=time.perf_counter_ns()
        if not np.all(coverage==1):return dict(status='CHECKPOINTED_TIME_RESERVE',completed_tasks=completed,total_tasks=total)
        answer=fast_readout.reconstruct(source,p,values)
        if ci==0:
            expected=json.loads((HERE/'QUALIFICATION_N30.json').read_text())['answer']
            assert answer['scalar_dos']==expected['scalar_dos'] and answer['closed_port_rows']==expected['closed_port_rows'];answer['checks']['retained_N30_five_prime_GPU_match']=True
        return dict(status='EXACT',answer=answer,execution=dict(backend='14_PERSISTENT_CUDA_BRANCH_GROUP_WORKERS',prepare_ns=ready-start,arithmetic_ns=end-ready,total_ns=time.perf_counter_ns()-start,ready_ns=ready,gpu_done_ns=end,branches=len(ts),branches_per_task=chunk,batch=batch,tasks=total,tasks_per_gpu=counts,boot=boot,resumed_tasks=prior_completed,readout_backend='NUMPY_INT64_BATCHED_INVERSE_NTT_PRECOMPUTED_PYTHON_INTEGER_CRT'))

    def execute(self,op,payload):
        if op=='GEN4_N120_CHUNKED_SOLVE':
            ci=payload['case'];assert self.cases[ci][0]['source_sha256']==payload['source_sha256'];assert self.cases[ci][1]['mathematical_plan_sha256']==payload['plan_sha256'];r=self.solve_chunked(ci);compressed(self.ram/f'RESULT{ci}.json.gz',r);return r
        if op=='GEN4_N120_CRT_CHECK':
            primes=payload['primes'];length=1024;coeff=np.zeros((16,length),dtype=object)
            for row in range(16):
                for k in range(117):coeff[row,k]=math.comb(116,k)
            values=[]
            for prime in primes:
                transformed=[]
                for row in coeff:
                    old=exact._inverse_ntt([int(c)%prime for c in row],prime);transformed.append([old[-k%length]*length%prime for k in range(length)])
                inv=fast_readout.batched_inverse_ntt(transformed,prime);assert inv.tolist()==[[int(c)%prime for c in row] for row in coeff];values.append(inv)
            modulus=math.prod(primes);weights=[modulus//p*pow(modulus//p,-1,p) for p in primes]
            for row in range(16):
                for k in range(length):assert sum(int(v[row,k])*w for v,w in zip(values,weights))%modulus==coeff[row,k]
            # Scalar central coefficient exercises the fifth modulus capacity.
            central=math.comb(120,60);assert central>math.prod(primes[:4]);assert sum((central%p)*w for p,w in zip(primes,weights))%modulus==central
            return dict(exact=True,coefficient_count=16*length,scalar_coefficient=str(central),fifth_prime_capacity_exercised=True)
        return self.base.execute(op,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--deadline',type=float,required=True);ap.add_argument('--skip-training-wait',action='store_true');args=ap.parse_args();ram=Path('/dev/shm/gen4-spin-n120-frontier1');durable=Path('/workspace/gen4/runs/spin-n120-frontier1');ram.mkdir(exist_ok=True);durable.mkdir(parents=True,exist_ok=True);os.environ['CUPY_CACHE_DIR']=str(ram/'cupy-cache')
    source=json.loads((HERE/'SOURCE.json').read_text());p=json.loads((HERE/'PLAN.json').read_text());primes=json.loads((HERE/'PRIMES.json').read_text());assert primes['capacity']
    # Existing exact N30 source supplies the end-to-end fifth-prime check.
    qual=json.loads((HERE/'QUALIFICATION_N30.json').read_text());small=qual['source'];sp=dict(qual['plan'],primes=p['primes'])
    # Thirty-two conditioned branches exercise reuse across two branch groups.
    # The saved exact N30 spectrum is unchanged by the qualification plan.
    fixed=list(range(4,9));ss=structure(30,[e for e in small['edges'] if e not in sp['glue']],sp['ports'],fixed)
    sp['selected']=dict(**ss,cutset=fixed,branches=32,weighted_entries=ss['output_entries']*32,method='branch_group_scheduler_qualification')
    sp['mathematical_plan_sha256']=digest(sp)
    session=DomainSession.start('MATTER_SEARCH',objective='Execute fresh N120 exact frustrated-spin DOS with learned planning, branch-group scheduling and five-prime reconstruction',output_root=ram/'sessions',receipt_storage='gzip');emit(announcement=session.announcement(),session=str(session.directory))
    cache=IndexCache();cases=[]
    for s,pl in [(small,sp),(source,p)]:
        t=time.perf_counter_ns();ts=templates(s,pl);desc,maps,stats=cache.compile(ts[0]);cases.append((s,pl,ts,desc,maps,stats));emit(status='RAM_PREPARED',N=s['N'],branches=len(ts),width=pl['selected']['width'],prepare_ns=time.perf_counter_ns()-t,map_bytes=sum(v.nbytes for v in cache.values.values()))
    if (ram/'SOURCE.json').exists():
        assert json.loads((ram/'SOURCE.json').read_text())['source_sha256']==source['source_sha256']
        assert json.loads((ram/'PLAN.json').read_text())['mathematical_plan_sha256']==p['mathematical_plan_sha256']
    save(ram/'SOURCE.json',source);save(ram/'PLAN.json',p);save(ram/'QUALIFICATION_PLAN.json',sp);save(ram/'PRIMES.json',primes);save(ram/'SOURCE_BINDING.json',dict(retained=original.verify_sources(),campaign_sources={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in HERE.glob('*.py')}))
    adapter=Frontier(session.consumer,ram,cases,cache,deadline=args.deadline);adapter.durable=durable;session.consumer=adapter;monitor=Monitor().start()
    try:
        save(ram/'CRT_CHECK.json',session.execute('GEN4_N120_CRT_CHECK',dict(primes=p['primes']),purpose='Verify fifth-prime inverse transform and coefficients beyond four-prime capacity'))
        if not args.skip_training_wait:
            emit(status='WAITING_FOR_TRAINING_GPU_RELEASE')
            while 'FAST_RETURN_CODE' not in Path('/opt/gen4/spin-focused1/continue.log').read_text():time.sleep(5)
            assert 'FAST_RETURN_CODE 0' in Path('/opt/gen4/spin-focused1/continue.log').read_text(),'Training successor must be preserved before using its GPU workers'
        for ci,(s,pl,*_) in enumerate(cases):
            emit(status='SOLVING',N=s['N'],branches=pl['selected']['branches'])
            result=session.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=ci,source_sha256=s['source_sha256'],plan_sha256=pl['mathematical_plan_sha256']),purpose='Check all five GPU primes against retained N30, then compute every N120 port polynomial and exact spectrum' if ci==0 else 'Sum each conditioned branch exactly once across every prime and root; reconstruct full N120 DOS and retained port operators')
            if result['status']!='EXACT':save(ram/'PAUSED.json',result);break
            emit(status='EXACT',N=s['N'],ground_energy=result['answer']['ground_energy'],ground_degeneracy=result['answer']['ground_degeneracy'],configuration_count=result['answer']['configuration_count'],execution=result['execution'])
            if ci==1:
                pub=session.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=result,source_binding=dict(campaign='GEN4_N120_FRONTIER1',source_sha256=s['source_sha256'],plan_sha256=pl['mathematical_plan_sha256']),provenance=dict(session=str(session.directory),backend=result['execution']['backend'])),purpose='Retain exact N120 result and reusable source-bound operator')
                compressed(ram/'RESULT_BUNDLE.json.gz',session.execute('GEN3_RESULT_EXPORT',dict(roots=[pub['result_ref']]),purpose='Save portable exact N120 retained result'));save(ram/'COMPLETE.json',dict(status='COMPLETE',result_ref=pub['result_ref'],session=str(session.directory),execution=result['execution']))
        save(ram/'CHECKPOINT.json',session.execute('GEN3_CHECKPOINT',{},purpose='Retain N120 exact results or resumable attempt'))
    except BaseException:save(ram/'FAILURE.json',dict(traceback=traceback.format_exc()));raise
    finally:
        session.close();monitor.stop(ram/'TELEMETRY.json');engine.flush(ram,durable,'FINAL');emit(status='STOPPED',workers_stopped=all(not w.is_alive() for w in adapter.workers))
if __name__=='__main__':main()
