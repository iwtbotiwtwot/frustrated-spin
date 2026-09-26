"""Every N1..96, source-bound adaptive method comparisons and frozen learning."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
from fractions import Fraction
import gzip
import json
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE'])
import planning
planning.SIZES=list(range(1,97))
from planning import ladder,plan,digest
from arithmetic import templates,IndexCache,cpu_values,reconstruct,brute,original
import catalog_run
from catalog_run import Catalog,save,compressed,emit,flush,Monitor
from catalog_gpu import GPUWorker
sys.path.insert(0,os.environ['GEN4_SPIN_TRAINING_CODE'])
from methods import generate,features
from SAM_PROJECT.session import DomainSession

class BoundedGPU(GPUWorker):
    def __init__(self,device,a,templates,desc,cache,batch,plan,resident):
        import cupy as cp
        cp.cuda.Device(device).use();needed={k for row in cache.keys for k in row}
        total=sum(v.nbytes for v in resident.values())
        for key in list(resident):
            if total<=2*(1<<30):break
            if key not in needed:total-=resident[key].nbytes;del resident[key]
        cp.get_default_memory_pool().free_all_blocks()
        super().__init__(device,a,templates,desc,cache,batch,plan,resident)

catalog_run.GPUWorker=BoundedGPU

class Full(Catalog):
    def execute(self,operation,payload):
        if operation=='GEN4_SPIN_FULL96_SOLVE':
            ci=payload['case'];source,p,ts,_,_,stats=self.cases[ci]
            assert source['source_sha256']==payload['source_sha256'] and p['mathematical_plan_sha256']==payload['plan_sha256']
            if source['N']<=30:
                start=time.perf_counter_ns();values=cpu_values(ts,p);arithmetic_ns=time.perf_counter_ns()-start
                answer=reconstruct(source,p,values)
                result=dict(answer=answer,execution=dict(total_ns=time.perf_counter_ns()-start,arithmetic_ns=arithmetic_ns,prepare_ns=0,backend='CPU_EXACT_RETAINED_FACTORS'),plan=p,index_cache=stats)
            else:result=self.solve(ci,'warm')
            compressed(self.ram/f'case{ci:03d}_r{payload["repeat"]}.json.gz',result)
            return result
        return self.base.execute(operation,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);args=ap.parse_args()
    ram=args.ram;durable=args.durable;ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True)
    os.environ['CUPY_CACHE_DIR']=str(ram/'cupy-cache')
    sources,frozen=ladder();cache=IndexCache();cases=[];specs=[];roster={};previous=None;previous_plan=None
    s=DomainSession.start('MATTER_SEARCH',objective='Train every integer N1..96 with fresh exact solves, deduplicated method comparisons and adaptive repeats',output_root=ram/'sessions',receipt_storage='gzip')
    emit(session=s.manifest,path=str(s.directory));assert s.manifest['global_slc']=='SLC-GEN4-P1'
    prior=json.loads((Path(os.environ['GEN4_SPIN_LARGE_RESULTS'])/'FROZEN_POLICIES.json').read_text())['fits']['combined']
    starter='spin-full96-start-combined-v1'
    s.execute('GEN3_TREE_FIT',dict(name=starter,rows=prior['rows'],source_binding=prior['binding']),purpose='Reconstitute the retained native starting policy from its exact prior training rows')
    for source in sources:
        variants=generate(source,frozen,previous_plan)
        fs=[features(source,previous,previous_plan,p) for p in variants]
        pred=s.execute('GEN3_TREE_PREDICT',dict(name=starter,rows=[dict(id=str(i),features=f['combined']) for i,f in enumerate(fs)],source_binding=prior['binding']),purpose='Use retained native transition learning to nominate a plan for this next integer size')
        probs={int(x['id']):Fraction(x['probability']) for x in pred['predictions']}
        preferred=min(range(5),key=lambda i:(-probs[i],variants[i]['selected']['weighted_entries'],i))
        cheapest=min(range(5),key=lambda i:variants[i]['selected']['weighted_entries'])
        # Fresh baseline plus cost/learned nominees; identical exact plans run once.
        chosen=[];seen=set()
        for i in [0,cheapest,preferred]:
            key=variants[i]['mathematical_plan_sha256']
            if key not in seen:chosen.append(i);seen.add(key)
        roster[source['N']]=[]
        for i in chosen:
            p=variants[i];ts=templates(source,p);desc,maps,stats=cache.compile(ts[0]);ci=len(cases)
            cases.append((source,p,ts,desc,maps,stats));roster[source['N']].append(ci)
            specs.append(dict(case=ci,N=source['N'],method=p['training_method'],plan=p,features=fs[i],
                              aliases=[v['training_method'] for v in variants if v['mathematical_plan_sha256']==p['mathematical_plan_sha256']],
                              all_candidate_costs=[dict(method=v['training_method'],width=v['selected']['width'],branches=v['selected']['branches'],work=v['selected']['weighted_entries']) for v in variants],
                              starting_policy_prediction=pred,starting_policy_preferred=variants[preferred]['training_method']))
        previous=source;previous_plan=variants[cheapest]
        emit(prepared_N=source['N'],executed_unique_plans=len(chosen),preferred=variants[preferred]['training_method'],cheapest=variants[cheapest]['training_method'])
    save(ram/'SOURCES.json',sources);save(ram/'SPECIFICATIONS.json',specs);save(ram/'SOURCE_BINDING.json',original.verify_sources())
    adapter=Full(s.consumer,ram,cases,cache);s.consumer=adapter;monitor=Monitor().start()
    observations=[];groups=[];answers={};models={};predictions={}
    oldsmall=json.loads((Path(os.environ['GEN4_SPIN_SMALL_RESULTS'])/'EXACT_SPECTRA.json').read_text())
    binding=dict(campaign='GEN4_SPIN_ALL_INTEGER_1_96_TRAINING1',roster=digest(sources),training_N=[1,64],development_N=[65,80],reserved_N=[81,96],sampling='one per unique nominated plan; two extra repetitions if initial times within15percent')
    try:
        for source in sources:
            n=source['N'];indices=roster[n]
            if n==81:
                for family in ['structural','transition','combined']:
                    rows=[dict(features=specs[g['case']]['features'][family],label=g['beats_fresh'],split=0 if g['N']<=64 else 1,witness=f'N{g["N"]}/{g["method"]}/{g["plan_sha256"]}') for g in groups]
                    name='spin-all96-'+family+'-v1';mb=dict(**binding,feature_family=family)
                    fit=s.execute('GEN3_TREE_FIT',dict(name=name,rows=rows,source_binding=mb),purpose='Learn from all integer transitions through N64, select depth through N80, exclude N81..96 labels')
                    export=s.execute('GEN3_TREE_EXPORT',dict(name=name),purpose='Freeze full-range native policy before new reserved frontier measurements')
                    models[family]=dict(fit=fit,model=export,binding=mb,rows=rows)
                    ids=[ci for k in range(81,97) for ci in roster[k]]
                    pred=s.execute('GEN3_TREE_PREDICT',dict(name=name,rows=[dict(id=str(ci),features=specs[ci]['features'][family]) for ci in ids],source_binding=mb),purpose='Commit all N81..96 method preferences before their reserved timings')
                    predictions[family]=pred
                save(ram/'FROZEN_MODELS.json',models);save(ram/'RESERVED_PREDICTIONS.json',predictions);flush(ram,durable,'FROZEN_BEFORE_N81')
            if n==31:
                ci=indices[0];p=specs[ci]['plan']
                warm=s.execute('GEN4_SPIN_FULL96_SOLVE',dict(case=ci,repeat=0,source_sha256=source['source_sha256'],plan_sha256=p['mathematical_plan_sha256']),purpose='Initialize fourteen GPU workers separately from method-training timings')
                answers[n]=warm['answer']
            order=list(reversed(indices)) if n%2 else indices
            for repeat in range(3):
                if repeat and len(indices)<2:break
                for ci in order:
                    spec=specs[ci];p=spec['plan'];emit(status='SOLVING',N=n,method=spec['method'],repeat=repeat+1)
                    result=s.execute('GEN4_SPIN_FULL96_SOLVE',dict(case=ci,repeat=repeat+1,source_sha256=source['source_sha256'],plan_sha256=p['mathematical_plan_sha256']),purpose='Fresh exact calculation at this integer size using a nominated transition method')
                    answer=result['answer'];reference=answers.setdefault(n,answer)
                    assert answer['scalar_dos']==reference['scalar_dos'] and answer['open_y_operator']==reference['open_y_operator'] and answer['closed_port_rows']==reference['closed_port_rows']
                    if str(n) in oldsmall:assert answer['scalar_dos']==oldsmall[str(n)]['scalar_dos'] and answer['closed_port_rows']==oldsmall[str(n)]['closed_port_rows']
                    e=result['execution'];observations.append(dict(case=ci,N=n,method=spec['method'],repeat=repeat+1,plan_sha256=p['mathematical_plan_sha256'],total_ns=e['total_ns'],arithmetic_ns=e['arithmetic_ns'],prepare_ns=e.get('prepare_ns',0),reconstruction_ns=answer['reconstruction_ns'],exact=True))
                    emit(status='EXACT',**observations[-1]);save(ram/'PROGRESS.json',dict(N=n,completed_calculations=len(observations),source_sizes_completed=n-1))
                if repeat==0:
                    times=[r['total_ns'] for r in observations if r['N']==n]
                    if max(times)*100>min(times)*115:break
                order=list(reversed(order))
            rows=[r for r in observations if r['N']==n];baseline=indices[0]
            medians={ci:int(statistics.median(r['total_ns'] for r in rows if r['case']==ci)) for ci in indices}
            for ci in indices:
                groups.append(dict(case=ci,N=n,method=specs[ci]['method'],aliases=specs[ci]['aliases'],plan_sha256=specs[ci]['plan']['mathematical_plan_sha256'],median_ns=medians[ci],beats_fresh=int(medians[ci]<medians[baseline]),repetitions=sum(r['case']==ci for r in rows)))
            save(ram/'MEASUREMENTS.json',observations);save(ram/'GROUPED_EXPERIENCE.json',groups)
            emit(status='SIZE_COMPLETE',N=n,best=min([g for g in groups if g['N']==n],key=lambda g:g['median_ns']))
            if n%16==0:flush(ram,durable,f'N{n}')
        evaluation={}
        for family,pred in predictions.items():
            probability={int(r['id']):Fraction(r['probability']) for r in pred['predictions']}
            for n in range(81,97):
                indices=roster[n];ci=min(indices,key=lambda i:(-probability[i],specs[i]['plan']['selected']['weighted_entries'],i))
                rows=[g for g in groups if g['N']==n];best=min(g['median_ns'] for g in rows);chosen=next(g for g in rows if g['case']==ci)
                evaluation[f'{n}:{family}']=dict(selected_method=specs[ci]['method'],selected_ns=chosen['median_ns'],best_ns=best,excess_ns=chosen['median_ns']-best)
        save(ram/'EVALUATION.json',evaluation);compressed(ram/'EXACT_SPECTRA.json.gz',answers)
        pub=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(sources=sources,groups=groups,measurements=observations,evaluation=evaluation),source_binding=binding,provenance=dict(operation='GEN4_SPIN_FULL96_SOLVE',session=str(s.directory),source_family='same retained N96 induced prefixes',all96integer_sizes=True)),purpose='Retain every integer source, observed transition choice and frozen policy evaluation')
        compressed(ram/'TRAINING_BUNDLE.json.gz',s.execute('GEN3_RESULT_EXPORT',dict(roots=[pub['result_ref']]),purpose='Export all-integer N1..96 transition training for installed reuse'))
        save(ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint learned native policies and complete integer-size training experience'))
        save(ram/'COMPLETE.json',dict(status='COMPLETE',sizes=list(range(1,97)),fresh_training_solves=len(observations),gpu_warmups=1,unique_plan_cases=len(cases),experience_ref=pub['result_ref'],session=str(s.directory),evaluation=evaluation))
    finally:s.close();monitor.stop(ram/'TELEMETRY.json')
    flush(ram,durable,'COMPLETE');emit(status='COMPLETE',workers_stopped=all(not p.is_alive() for p in adapter.workers))

if __name__=='__main__':main()
