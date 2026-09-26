"""GEN4 catalog campaign: fresh exact entries, native transition learning.

One warm DomainSession owns the computation; source-bound successor operations
run CPU preparation/reconstruction and persistent GPU graph workers. The native
retained-result and CART interfaces store reusable knowledge and portable state.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
import ctypes
import gzip
import hashlib
import json
import multiprocessing as mp
import queue
import sys
import tarfile
import time
import traceback
from pathlib import Path
import numpy as np
from planning import SIZES,ladder,plan,digest
from arithmetic import a,original,templates,IndexCache,cpu_values,reconstruct,brute
from catalog_gpu import GPUWorker
from SAM_PROJECT.session import DomainSession
from monitor import Monitor

HERE=Path(__file__).resolve().parent

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')

def compressed(path,value):
    with gzip.open(path,'wt',compresslevel=6) as f:json.dump(value,f,sort_keys=True,separators=(',',':'))

def emit(**value):print(json.dumps(value),flush=True)

def flush(ram,durable,label):
    began=time.perf_counter_ns();path=durable/'checkpoint.tar.gz';tmp=durable/'checkpoint.part'
    with tarfile.open(tmp,'w:gz',compresslevel=1) as archive:archive.add(ram,arcname='ram')
    with tmp.open('rb') as f:os.fsync(f.fileno())
    tmp.replace(path)
    fd=os.open(durable,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    receipt=dict(label=label,archive=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),flush_ns=time.perf_counter_ns()-began)
    save(durable/'CHECKPOINT.json',receipt);emit(checkpoint=receipt)

class Catalog:
    def __init__(self,base,ram,cases,index_cache):
        self.base=base;self.ram=ram;self.cases=cases;self.index_cache=index_cache;self.workers=[]
        self.ctx=mp.get_context('fork');self.jobs=self.ctx.Queue();self.answers=self.ctx.Queue()
        self.controls=[self.ctx.Queue() for _ in range(14)]
    def close(self):
        for c in self.controls:c.put(('STOP',))
        for p in self.workers:
            p.join(30)
            if p.is_alive():p.terminate();p.join(5)
        self.base.close()
    def worker(self,device):
        try:
            import cupy as cp
            cp.cuda.Device(device).use();resident={}
            trace=ctypes.CDLL('/opt/gen4/n72-benchmark1/activity.so');trace.trace_end.argtypes=[ctypes.c_char_p]
            assert trace.trace_begin()==0
            while True:
                command=self.controls[device].get()
                if command[0]=='STOP':break
                _,ci,batch,cache_mode=command;case=self.cases[ci];s,p,ts,desc,cache,stats=case
                if cache_mode=='cold':resident.clear();cp.get_default_memory_pool().free_all_blocks()
                started=time.perf_counter_ns();gpu=GPUWorker(device,a,ts,desc,cache,batch,p,resident)
                self.answers.put(('READY',device,dict(init_ns=time.perf_counter_ns()-started,map_hits=gpu.map_hits,map_misses=gpu.map_misses,pool_bytes=cp.get_default_memory_pool().total_bytes())))
                assert self.controls[device].get()[0]=='GO'
                def demand():
                    job=self.jobs.get()
                    return None if job is None else gpu.prepare(job)
                following=None;current=demand()
                while current:
                    t=time.perf_counter_ns();events=gpu.launch(current);following=demand()
                    values,ms=gpu.result(current,events)
                    self.answers.put(('BATCH',device,dict(task=current[0],values=values.tolist(),started_ns=t,ended_ns=time.perf_counter_ns(),stream_ns=round(ms*1e6))))
                    current=following
                self.answers.put(('DONE',device,None));del gpu,current,following
            assert trace.trace_end(str(self.ram/f'GPU{device}_KERNELS.csv').encode())==0
        except BaseException:self.answers.put(('ERROR',device,traceback.format_exc()));raise
    def receive(self):
        while True:
            try:
                msg=self.answers.get(timeout=2)
                if msg[0]=='ERROR':raise RuntimeError(msg[2])
                return msg
            except queue.Empty:
                failed=[(i,p.exitcode) for i,p in enumerate(self.workers) if p.exitcode is not None]
                if failed:raise RuntimeError(('worker exited',failed))
    def solve(self,ci,mode='warm'):
        source,p,ts,desc,cache,stats=self.cases[ci];start=time.perf_counter_ns()
        if source['N']<=24:
            values=cpu_values(ts,p);execution=dict(backend='CPU_EXACT_RETAINED_FACTORS',arithmetic_ns=time.perf_counter_ns()-start,workers=0)
        else:
            if not self.workers:
                self.workers=[self.ctx.Process(target=self.worker,args=(d,)) for d in range(14)]
                for worker in self.workers:worker.start()
            batch=min(16,max(1,p['root_count']//16));boot=[]
            for c in self.controls:c.put(('LOAD',ci,batch,mode))
            while len(boot)<14:
                kind,d,data=self.receive();assert kind=='READY';boot.append(dict(gpu=d,**data))
            roster=[(pi,lo,lo+batch) for lo in range(0,p['root_count'],batch) for pi in range(len(p['primes']))]
            for task in roster:self.jobs.put(task)
            for _ in self.workers:self.jobs.put(None)
            ready=time.perf_counter_ns()
            for c in self.controls:c.put(('GO',))
            values=[np.zeros((1<<len(p['ports']),p['root_count']),dtype=np.int64) for _ in p['primes']]
            coverage=np.zeros((len(values),p['root_count']),dtype=np.uint8);counts=[0]*14;done=0;profiles=[]
            while done<14:
                kind,d,data=self.receive()
                if kind=='DONE':done+=1;continue
                assert kind=='BATCH';pi,lo,hi=data['task'];values[pi][:,lo:hi]=data.pop('values')
                coverage[pi,lo:hi]+=1;counts[d]+=hi-lo;profiles.append(dict(gpu=d,**data))
                limit=int(Path('/sys/fs/cgroup/memory.max').read_text());current=int(Path('/sys/fs/cgroup/memory.current').read_text())
                assert current < limit-8*(1<<30),'memory reserve exhausted'
            assert np.all(coverage==1)
            end=time.perf_counter_ns()
            execution=dict(backend='14_PERSISTENT_CUDA_GRAPH_WORKERS',workers=14,batch=batch,mode=mode,
                           prepare_ns=ready-start,arithmetic_ns=end-ready,ready_ns=ready,gpu_done_ns=end,
                           roots_per_gpu=counts,boot=boot,profiles=profiles)
        answer=reconstruct(source,p,values)
        if source['N']<=18:assert answer['closed_port_rows']==brute(source,p['ports']);answer['checks']['independent_enumeration']=True
        if source['N']==96 and source.get('family')=='N96_INDUCED_TRANSITION_LADDER_V1':
            # Same graph as the original N96, vertex-renumbered; use retained scalar DOS.
            authority=original.source()[0]
            reference=authority[4]
            glue=a.n96_engine.glue_y_degrees(reference['cut_edges'],reference['port_order'])
            expected=a.n96_engine.close_one_cell(reference['w_coefficients'],glue,
                       local_bound=reference['local_y_bound'],total_bound=source['energy_bound_B'])
            old_dos=[[k-source['energy_bound_B'],str(c)] for k,c in enumerate(expected['fixed_coefficients']) if c]
            assert answer['scalar_dos']==old_dos
            answer['checks']['original_N96_exact_reference']=True
        execution['total_ns']=time.perf_counter_ns()-start
        return dict(answer=answer,execution=execution,index_cache=stats,plan=p)
    def execute(self,operation,payload):
        if operation=='GEN4_SPIN_CATALOG_SOLVE':
            ci=SIZES.index(payload['N']);assert payload['source_sha256']==self.cases[ci][0]['source_sha256']
            result=self.solve(ci,payload.get('cache_mode','warm'))
            compressed(self.ram/f'N{payload["N"]}_{payload.get("cache_mode","warm")}.json.gz',result)
            return result
        return self.base.execute(operation,payload)
