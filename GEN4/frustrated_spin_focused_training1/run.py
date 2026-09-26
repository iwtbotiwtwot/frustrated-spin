import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,json,sys,time,statistics,traceback
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE']);sys.path.insert(0,os.environ['GEN4_SPIN_TRAINING_CODE'])
# Unique successor engine owns arbitrary source checks and unchanged arithmetic.
sys.path.insert(0,str(Path(__file__).resolve().parent))
import engine
from engine import Catalog,save,compressed,emit,flush,Monitor
from arithmetic import templates,IndexCache,original
import planning
planning.SIZES=list(range(1,97))
from planning import ladder,plan,digest
from design import graph_family,prefix,expanded,features,FEATURES
import cost
from SAM_PROJECT.session import DomainSession

BaseGPU=engine.GPUWorker
class BoundedGPU(BaseGPU):
    def __init__(self,device,a,ts,desc,cache,batch,p,resident):
        import cupy as cp
        cp.cuda.Device(device).use();needed={k for row in cache.keys for k in row};total=sum(v.nbytes for v in resident.values())
        for key in list(resident):
            if total<=2*(1<<30):break
            if key not in needed:total-=resident[key].nbytes;del resident[key]
        cp.get_default_memory_pool().free_all_blocks();super().__init__(device,a,ts,desc,cache,batch,p,resident)
engine.GPUWorker=BoundedGPU

class Focus(Catalog):
    def execute(self,op,payload):
        if op=='GEN4_SPIN_FOCUSED_SOLVE':
            ci=payload['case'];source,p,*_=self.cases[ci];assert source['source_sha256']==payload['source_sha256'];assert p['mathematical_plan_sha256']==payload['plan_sha256']
            result=self.solve(ci);compressed(self.ram/f'case{ci:03d}_r{payload["repeat"]}.json.gz',result);return result
        if op=='GEN4_SPIN_COST_FIT':return cost.choose(payload['training'],payload['development'])
        if op=='GEN4_SPIN_COST_PREDICT':return dict(predicted_ns=cost.predict(payload['model'],payload['rows']),backend='NUMPY_CPU_TIMING_REGRESSION')
        return self.base.execute(op,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);ap.add_argument('--deadline',type=float,required=True);args=ap.parse_args();ram=args.ram;durable=args.durable
    ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True);os.environ['CUPY_CACHE_DIR']=str(ram/'cupy-cache')
    allsources,frozen=ladder();parent=allsources[-1];cache=IndexCache();cases=[];specs=[];roster=[];unadmitted=[]
    session=DomainSession.start('MATTER_SEARCH',objective='Focused execution-cost and transition training, repeated exact comparisons, unseen rewired topology holdouts',output_root=ram/'sessions',receipt_storage='gzip');emit(session=session.manifest,path=str(session.directory))
    # Only source topology IDs determine the split. All their sizes stay together.
    schedules={0:[80,84,85,86,87,88,89,90,91,92,93,94,95,96],1:[84,88,91,92,96],2:[84,88,91,92,96],3:[84,88,91,92,96],4:[84,88,91,92,96],5:[84,88,91,92,96]}
    for seed,ns in schedules.items():
        parent_variant=graph_family(parent,seed)
        for n in ns:
            source=prefix(parent_variant,n);previous=prefix(parent_variant,n-1);previous_plan=plan(previous,frozen);started=time.perf_counter_ns();variants=expanded(source,frozen,previous_plan);seen=set();indices=[]
            # Qualify all distinct plans of five routes; adjacent repair is retained
            # in the candidate record but only contributes when structurally cheapest.
            chosen=[variants[i] for i in [0,1,4,5]]
            if variants[3]['selected']['weighted_entries']<min(p['selected']['weighted_entries'] for p in chosen):chosen.append(variants[3])
            for p in chosen:
                key=p['mathematical_plan_sha256']
                if key in seen:continue
                seen.add(key)
                if p['selected']['width']>22 or not p['prime_product_sufficient']:
                    unadmitted.append(dict(seed=seed,N=n,method=p['training_method'],plan=p,reason='current qualified backend width/CRT capacity'));continue
                # A per-plan scheduling ceiling reserves the owner's two-hour pod
                # window; skipped plans stay explicit, never mathematical exclusions.
                proxy=p['selected']['weighted_entries']*p['root_count']*len(p['primes'])
                if proxy>12_000_000_000_000:
                    unadmitted.append(dict(seed=seed,N=n,method=p['training_method'],plan=p,reason='campaign time budget; structural proxy above ~60s plan'));continue
                ts=templates(source,p);desc,maps,stats=cache.compile(ts[0]);ci=len(cases);cases.append((source,p,ts,desc,maps,stats));indices.append(ci)
                specs.append(dict(case=ci,group=f'G{seed}-N{n}',seed=seed,N=n,split='train' if seed<=2 else 'development' if seed==3 else 'test',method=p['training_method'],plan=p,features=features(source,previous,previous_plan,p,desc,maps),source=source,previous_source=previous['source_sha256']))
            if indices:roster.append(dict(seed=seed,N=n,indices=indices))
            emit(status='PREPARED',seed=seed,N=n,cases=indices,best_work=min(p['selected']['weighted_entries'] for p in variants),planning_seconds=(time.perf_counter_ns()-started)/1e9)
    save(ram/'SPECIFICATIONS.json',specs);save(ram/'SCHEDULE.json',roster);save(ram/'UNADMITTED.json',unadmitted);save(ram/'SOURCE_BINDING.json',original.verify_sources())
    binding=dict(campaign='GEN4_SPIN_FOCUSED_TRAINING1',sources=digest([s['source'] for s in specs]),features=FEATURES,training_topologies=[0,1,2],development_topologies=[3],reserved_topologies=[4,5],common_ancestor=parent['source_sha256'])
    adapter=Focus(session.consumer,ram,cases,cache);session.consumer=adapter;monitor=Monitor().start();measurements=[];groups=[];answers={};models=None;predictions={};skipped=[];first=True
    try:
        for task in roster:
            seed,n=task['seed'],task['N'];indices=task['indices'];group=specs[indices[0]]['group']
            if time.time()>args.deadline:
                skipped.append(dict(group=group,reason='owner pod time reserve'));continue
            if seed>=4 and models is None:
                train=[r for r in groups if r['split']=='train'];dev=[r for r in groups if r['split']=='development']
                fitted=session.execute('GEN4_SPIN_COST_FIT',dict(training=train,development=dev),purpose='Fit execution-component time models and select on development topology only')
                pairrows=[]
                for gid in sorted({r['group'] for r in train+dev}):
                    rr=[r for r in train+dev if r['group']==gid]
                    for a in rr:
                        for b in rr:
                            if a['case']==b['case']:continue
                            pairrows.append(dict(features=a['features']+b['features'],label=int(a['total_ns']<b['total_ns']),split=0 if a['split']=='train' else 1,witness=f'{gid}:{a["case"]}<{b["case"]}'))
                pairname='spin-focused-pairwise-v1';fit=session.execute('GEN3_TREE_FIT',dict(name=pairname,rows=pairrows,source_binding=binding),purpose='Learn pairwise plan ranking with both orientations, grouped by source topology')
                export=session.execute('GEN3_TREE_EXPORT',dict(name=pairname),purpose='Freeze native pairwise policy before unseen topology execution')
                models=dict(cost=fitted,pairwise=dict(fit=fit,export=export,rows=pairrows,binding=binding));save(ram/'FROZEN_MODELS.json',models)
                for reserved in [r for r in roster if r['seed']>=4]:
                    ix=reserved['indices'];rr=[specs[i] for i in ix];cp=session.execute('GEN4_SPIN_COST_PREDICT',dict(model=fitted['selected'],rows=rr),purpose='Freeze time predictions for all reserved topology cases before their timings');pairs=[(a,b) for a in ix for b in ix if a!=b]
                    pp=session.execute('GEN3_TREE_PREDICT',dict(name=pairname,rows=[dict(id=f'{a}:{b}',features=specs[a]['features']+specs[b]['features']) for a,b in pairs],source_binding=binding),purpose='Freeze native pairwise preferences for unmeasured topology cases') if pairs else dict(predictions=[])
                    probabilities={r['id']:Fraction(r['probability']) for r in pp['predictions']};wins={a:sum(probabilities.get(f'{a}:{b}',0) for b in ix if a!=b) for a in ix}
                    predictions[rr[0]['group']]=dict(cost_ns=cp['predicted_ns'],indices=ix,pairwise=pp,choices=dict(cost=ix[min(range(len(ix)),key=lambda i:cp['predicted_ns'][i])],pairwise=min(ix,key=lambda i:(-wins[i],specs[i]['plan']['selected']['weighted_entries'])),structural=min(ix,key=lambda i:specs[i]['plan']['selected']['weighted_entries']),fresh=next((i for i in ix if specs[i]['method']=='fresh_min_fill'),None)))
                save(ram/'RESERVED_PREDICTIONS.json',predictions);flush(ram,durable,'FROZEN_BEFORE_RESERVED')
            if first:
                ci=indices[0];sp=specs[ci];session.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=ci,repeat=0,source_sha256=sp['source']['source_sha256'],plan_sha256=sp['plan']['mathematical_plan_sha256']),purpose='Warm fourteen GPU owners outside training timings');first=False
            for repeat in range(3):
                order=indices[repeat%len(indices):]+indices[:repeat%len(indices)]
                if (seed+n)%2:order=list(reversed(order))
                for ci in order:
                    sp=specs[ci];emit(status='SOLVING',group=group,method=sp['method'],repeat=repeat+1)
                    result=session.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=ci,repeat=repeat+1,source_sha256=sp['source']['source_sha256'],plan_sha256=sp['plan']['mathematical_plan_sha256']),purpose='Fresh exact solve under a distinct source-bound plan; compare complete operators across methods')
                    ans=result['answer'];ref=answers.setdefault(group,ans);assert ans['scalar_dos']==ref['scalar_dos'] and ans['open_y_operator']==ref['open_y_operator'] and ans['closed_port_rows']==ref['closed_port_rows']
                    e=result['execution'];row=dict(case=ci,group=group,seed=seed,N=n,method=sp['method'],repeat=repeat+1,total_ns=e['total_ns'],prepare_ns=e['prepare_ns'],arithmetic_ns=e['arithmetic_ns'],reconstruction_ns=ans['reconstruction_ns'],exact=True);measurements.append(row);emit(status='EXACT',**row);save(ram/'PROGRESS.json',dict(group=group,completed_solves=len(measurements),planned_solves=len(cases)*3,deadline=args.deadline))
            for ci in indices:
                rr=[r for r in measurements if r['case']==ci];sp=specs[ci];groups.append(dict(case=ci,group=group,seed=seed,N=n,method=sp['method'],split=sp['split'],features=sp['features'],repetitions=len(rr),**{k:int(statistics.median(r[k] for r in rr)) for k in ['total_ns','prepare_ns','arithmetic_ns','reconstruction_ns']}))
            save(ram/'MEASUREMENTS.json',measurements);save(ram/'GROUPED_EXPERIENCE.json',groups);compressed(ram/'EXACT_SPECTRA.json.gz',answers);flush(ram,durable,group)
        evaluation={}
        for group,pred in predictions.items():
            rr={r['case']:r for r in groups if r['group']==group}
            if not rr:continue
            oracle=min(r['total_ns'] for r in rr.values());evaluation[group]=dict(oracle_ns=oracle,choices={method:dict(case=ci,total_ns=rr[ci]['total_ns'],excess_ns=rr[ci]['total_ns']-oracle) for method,ci in pred['choices'].items() if ci in rr},cost_predictions=pred['cost_ns'])
        save(ram/'EVALUATION.json',evaluation);save(ram/'SKIPPED.json',skipped)
        pub=session.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(binding=binding,groups=groups,measurements=measurements,evaluation=evaluation,models=models),source_binding=binding,provenance=dict(session=str(session.directory),operations=['GEN4_SPIN_FOCUSED_SOLVE','GEN4_SPIN_COST_FIT','GEN3_TREE_FIT'],backend='Exact CPU/CUDA spin arithmetic; NumPy timing regression; native C++/GMP pairwise CART')),purpose='Retain focused transition/cost learning and unseen topology evaluation')
        compressed(ram/'TRAINING_BUNDLE.json.gz',session.execute('GEN3_RESULT_EXPORT',dict(roots=[pub['result_ref']]),purpose='Export focused training and learned cost models for reuse'))
        save(ram/'CHECKPOINT.json',session.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint completed focused models and source-bound experience'))
        save(ram/'COMPLETE.json',dict(status='COMPLETE' if not skipped else 'TIME_BUDGET_COMPLETE_WITH_SKIPS',solves=len(measurements),source_groups=len(answers),experience_ref=pub['result_ref'],session=str(session.directory),skipped=skipped))
    except BaseException:
        save(ram/'FAILURE.json',dict(traceback=traceback.format_exc()));raise
    finally:
        session.close();monitor.stop(ram/'TELEMETRY.json');flush(ram,durable,'FINAL')
    emit(status='COMPLETE',workers_stopped=all(not p.is_alive() for p in adapter.workers))

if __name__=='__main__':main()
