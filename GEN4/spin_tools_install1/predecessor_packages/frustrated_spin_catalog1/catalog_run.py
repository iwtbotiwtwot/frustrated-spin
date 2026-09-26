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
        if source['N']==96:
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

def transition(previous,current,prevplan,curplan):
    old=set(previous['parent_vertices']);new=set(current['parent_vertices'])
    def weighted(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v])))+(j,) for u,v,j in s['edges']}
    before=weighted(previous);after=weighted(current);added=sorted(after-before)
    boundary=sorted({v for edge in added for v in edge[:2] if v in old})
    retained={previous['parent_vertices'][p] for p in prevplan['ports']}
    return dict(from_N=previous['N'],to_N=current['N'],from_source=previous['source_sha256'],to_source=current['source_sha256'],
                added_parent_vertices=sorted(new-old),added_parent_edges=[list(e) for e in added],removed_edges=[list(e) for e in sorted(before-after)],
                previous_boundary_touched=boundary,retained_boundary_sufficient=set(boundary)<=retained,
                exact_spectrum_extension_available=set(boundary)<=retained,
                learned_use='Elimination-order priority and normalized projection recipes; scalar spectra are not substituted for unresolved boundary correlations',
                previous_plan=prevplan['selected'],next_plan=curplan['selected'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ram',type=Path,required=True);parser.add_argument('--durable',type=Path,required=True);args=parser.parse_args()
    ram=args.ram;durable=args.durable;ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True)
    os.environ['CUPY_CACHE_DIR']=str(ram/'cupy-cache')
    source_manifest=original.verify_sources();save(ram/'SOURCE_BINDING.json',source_manifest)
    sources,frozen=ladder();cases=[];cache=IndexCache();previous=None
    for source in sources:
        p=plan(source,frozen,previous);ts=templates(source,p)
        desc,index,stats=cache.compile(ts[0])
        cases.append((source,p,ts,desc,index,stats));previous=p
        emit(prepared_N=source['N'],selected=p['selected']['method'],width=p['selected']['width'],branches=p['selected']['branches'],cache=stats)
    save(ram/'SOURCES.json',sources);save(ram/'PLANS.json',[c[1] for c in cases]);save(ram/'INDEX_RECIPES.json',cache.recipes)
    s=DomainSession.start('MATTER_SEARCH',objective='Fresh exact spin catalog N2-96; learn source-bound growth transitions, plans and reusable index recipes',output_root=ram/'sessions',receipt_storage='gzip')
    emit(session=s.manifest,path=str(s.directory));assert s.manifest['global_slc']=='SLC-GEN4-P1'
    adapter=Catalog(s.consumer,ram,cases,cache);s.consumer=adapter
    monitor=Monitor().start()
    refs=[];entryrefs=[];results=[];transitions=[];lessons=[]
    binding=dict(catalog='GEN4_SPIN_TRANSITION_CATALOG_V1',parent_instance_sha256=sources[-1]['parent_instance_sha256'],source_roster_sha256=digest(sources))
    try:
        for i,source in enumerate(sources):
            emit(status='RUNNING',N=source['N'])
            result=s.execute('GEN4_SPIN_CATALOG_SOLVE',dict(N=source['N'],source_sha256=source['source_sha256']),purpose='Fresh exact source spectrum, retained boundary rows, selected transition plan')
            answer=result['answer'];results.append(result)
            publish=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(source=source,spectrum=answer,plan=cases[i][1]),
                          source_binding=dict(**binding,N=source['N'],source_sha256=source['source_sha256']),
                          provenance=dict(operation='GEN4_SPIN_CATALOG_SOLVE',session=str(s.directory),adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())),purpose='Retain exact catalog entry with its source and actual calculation ancestry')
            refs.append(publish['result_ref']);entryrefs.append(publish['result_ref'])
            if i:
                tr=transition(sources[i-1],source,cases[i-1][1],cases[i][1]);tr['index_cache']=result['index_cache'];tr['execution']=result['execution'];transitions.append(tr)
                candidates=cases[i][1]['candidates'];fresh=min((c for c in candidates if c['method']=='fresh_min_fill'),key=lambda c:c['weighted_entries'])
                transfer=min((c for c in candidates if c['method']=='transition_priority'),key=lambda c:c['weighted_entries'])
                # Native classification target: exact symbolic elimination-work saving.
                features=[sources[i-1]['N'],source['N']-sources[i-1]['N'],len(tr['added_parent_edges']),len(tr['previous_boundary_touched']),cases[i-1][1]['selected']['width'],cases[i-1][1]['selected']['branches']]
                split=0 if source['N']<=72 else (1 if source['N']==84 else 2)
                lessons.append(dict(features=features,label=int(transfer['weighted_entries']<fresh['weighted_entries']),split=split,
                                    witness=f'N{sources[i-1]["N"]}->N{source["N"]}:fresh={fresh["weighted_entries"]};transfer={transfer["weighted_entries"]}'))
                trref=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=tr,source_binding=dict(**binding,from_N=tr['from_N'],to_N=tr['to_N']),
                                provenance=dict(method='Measured exact transition planning and executed GPU/CPU source calculation'),dependencies=entryrefs[-2:]),purpose='Retain reusable transition, mathematical boundary requirements and measured execution')
                refs.append(trref['result_ref'])
            emit(status='EXACT_COMPLETE',N=source['N'],ground=answer['ground_energy'],occupied_bins=len(answer['scalar_dos']),seconds=result['execution']['total_ns']/1e9)
            save(ram/'PROGRESS.json',dict(completed=[r['answer']['N'] for r in results],session=str(s.directory)))
            if source['N'] in (24,72,96):flush(ram,durable,f'N{source["N"]}')
        save(ram/'TRANSITIONS.json',transitions);save(ram/'LESSONS.json',lessons)
        fit=s.execute('GEN3_TREE_FIT',dict(name='spin-transition-plan-v1',rows=lessons,source_binding=binding),purpose='Learn when inherited order priority reduces exact elimination work; N84 development, N96 reserved')
        model=s.execute('GEN3_TREE_EXPORT',dict(name='spin-transition-plan-v1'),purpose='Retain native transition policy with exact source binding')
        predictions=s.execute('GEN3_TREE_PREDICT',dict(name='spin-transition-plan-v1',rows=[dict(id=str(i),features=r['features']) for i,r in enumerate(lessons)],source_binding=binding),purpose='Read advisory transition choices without using reserved labels in fitting')
        save(ram/'NATIVE_LEARNING.json',dict(fit=fit,model=model,predictions=predictions,binding=binding))
        # A matched N96 replay directly measures materialized map reuse in the warm workers.
        replay=s.execute('GEN4_SPIN_CATALOG_SOLVE',dict(N=96,source_sha256=sources[-1]['source_sha256'],cache_mode='replay'),purpose='Measure actual reuse of resident transition index maps on a fresh N96 solve')
        assert replay['answer']['scalar_dos']==results[-1]['answer']['scalar_dos']
        bundle=s.execute('GEN3_RESULT_EXPORT',dict(roots=refs),purpose='Export a compressed GEN3/GEN4 portable catalog and transition closure')
        compressed(ram/'CATALOG_BUNDLE.json.gz',bundle)
        save(ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint native transition model and exact retained catalog'))
        save(ram/'COMPLETE.json',dict(status='COMPLETE',sizes=SIZES,entries=len(results),transitions=len(transitions),native_model='spin-transition-plan-v1',session=str(s.directory),roots=refs,binding=binding))
    finally:
        s.close();monitor.stop(ram/'TELEMETRY.json')
    flush(ram,durable,'COMPLETE')
    emit(status='COMPLETE',workers_stopped=all(not p.is_alive() for p in adapter.workers))

if __name__=='__main__':main()
