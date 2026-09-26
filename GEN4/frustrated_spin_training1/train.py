"""Repeated exact transition training through GEN4 and native C++ CART."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import argparse
from fractions import Fraction
import gzip
import json
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE'])
from catalog_run import Catalog,save,compressed,emit,flush,Monitor
from arithmetic import original,templates,IndexCache
from planning import SIZES,ladder,plan,digest
from SAM_PROJECT.session import DomainSession
sys.path.insert(0,str(Path(__file__).resolve().parent))
from methods import METHODS,generate,features

class Training(Catalog):
    def execute(self,operation,payload):
        if operation=='GEN4_SPIN_TRAIN_SOLVE':
            ci=payload['case'];source,p,*_=self.cases[ci]
            assert payload['source_sha256']==source['source_sha256']
            result=self.solve(ci,'warm')
            compressed(self.ram/f'case{ci:02d}_repeat{payload["repeat"]}.json.gz',result)
            return result
        return self.base.execute(operation,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);args=ap.parse_args()
    ram=args.ram;durable=args.durable;ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True)
    os.environ['CUPY_CACHE_DIR']=str(ram/'cupy-cache')
    sources,frozen=ladder();cases=[];index_cache=IndexCache();previous=None;previous_plan=None;specs=[]
    for si,source in enumerate(sources):
        baseline=plan(source,frozen,previous_plan)
        for variant in generate(source,frozen,previous_plan):
            ts=templates(source,variant);desc,cache,stats=index_cache.compile(ts[0]);ci=len(cases)
            cases.append((source,variant,ts,desc,cache,stats))
            specs.append(dict(case=ci,N=source['N'],method=variant['training_method'],plan_key=variant['mathematical_plan_sha256'],
                              features=features(source,previous,previous_plan,variant),plan=variant))
        previous=source;previous_plan=baseline
        emit(prepared_N=source['N'],plans=[dict(method=x['method'],width=x['plan']['selected']['width'],branches=x['plan']['selected']['branches'],work=x['plan']['selected']['weighted_entries']) for x in specs[-5:]])
    save(ram/'SPECIFICATIONS.json',specs);save(ram/'SOURCES.json',sources);save(ram/'SOURCE_BINDING.json',original.verify_sources())
    binding=dict(campaign='GEN4_SPIN_TRANSITION_TRAINING1',catalog_source_roster=digest(sources),method_roster=METHODS,training_max_N=72,development_N=84,reserved_N=96)
    session=DomainSession.start('MATTER_SEARCH',objective='Train and compare repeated exact transition methods, then evaluate frozen policies on N96',output_root=ram/'sessions',receipt_storage='gzip')
    emit(session=session.manifest,path=str(session.directory));assert session.manifest['global_slc']=='SLC-GEN4-P1'
    adapter=Training(session.consumer,ram,cases,index_cache);session.consumer=adapter
    monitor=Monitor().start();measurements=[];groups=[];fit_records={};prediction_records={};test_choices={}
    expected_root=Path(os.environ['GEN4_SPIN_CATALOG_RESULTS'])
    try:
        for si,source in enumerate(sources):
            n=source['N'];indices=list(range(si*5,si*5+5))
            if n==96:
                # Fit and freeze every learned policy before collecting reserved outcomes.
                for family in ['structural','transition','combined']:
                    rows=[]
                    for g in groups:
                        spec=specs[g['case']]
                        rows.append(dict(features=spec['features'][family],label=g['beats_fresh'],split=0 if g['N']<=72 else 1,witness=f'N{g["N"]}/{g["method"]}:{g["plan_key"]}'))
                    name='spin-transition-'+family+'-v2'
                    model_binding=dict(**binding,features=family)
                    fit=session.execute('GEN3_TREE_FIT',dict(name=name,rows=rows,source_binding=model_binding),purpose='Learn transition choices from measured repeated solves; N96 excluded from fit and depth selection')
                    export=session.execute('GEN3_TREE_EXPORT',dict(name=name),purpose='Freeze native transition policy and source ancestry before reserved measurements')
                    pred=session.execute('GEN3_TREE_PREDICT',dict(name=name,rows=[dict(id=str(ci),features=specs[ci]['features'][family]) for ci in indices],source_binding=model_binding),purpose='Commit learned method preferences before the reserved N96 method timings')
                    probs={int(x['id']):Fraction(x['probability']) for x in pred['predictions']}
                    selected=min(indices,key=lambda ci:(-probs[ci],specs[ci]['plan']['selected']['weighted_entries'],ci))
                    test_choices[family]=selected;fit_records[family]=dict(fit=fit,export=export,binding=model_binding,rows=rows);prediction_records[family]=pred
                test_choices['exact_structural_cost']=min(indices,key=lambda ci:specs[ci]['plan']['selected']['weighted_entries'])
                test_choices['fresh_baseline']=indices[0]
                # Source-level nearest experience; scale dimensions from training sources only.
                train=[g for g in groups if g['N']<=72];source_winners=[]
                for oldn in sorted({g['N'] for g in train}):
                    choices=[g for g in train if g['N']==oldn];source_winners.append(min(choices,key=lambda g:g['median_total_ns']))
                vectors=[specs[g['case']]['features']['transition'][:6] for g in source_winners]
                target=specs[indices[0]]['features']['transition'][:6]
                ranges=[max(1,max(v[i] for v in vectors)-min(v[i] for v in vectors)) for i in range(6)]
                nearest=min(zip(source_winners,vectors),key=lambda pair:sum(Fraction(abs(x-y),scale) for x,y,scale in zip(pair[1],target,ranges)))[0]
                test_choices['nearest_experience']=next(ci for ci in indices if specs[ci]['method']==nearest['method'])
                save(ram/'FROZEN_POLICIES.json',dict(fits=fit_records,predictions=prediction_records,choices=test_choices,nearest_training_source_N=nearest['N'],frozen_before_reserved_measurements=True))
                flush(ram,durable,'POLICIES_FROZEN_BEFORE_N96')
            expected=json.load(gzip.open(expected_root/f'N{n}_warm.json.gz','rt'))['answer']
            # Rotated order counters a fixed first/last method placement across repeats.
            for repeat in range(3):
                order=indices[repeat:]+indices[:repeat]
                for ci in order:
                    spec=specs[ci];emit(status='TRAINING_SOLVE',N=n,method=spec['method'],repeat=repeat+1)
                    result=session.execute('GEN4_SPIN_TRAIN_SOLVE',dict(case=ci,repeat=repeat+1,source_sha256=source['source_sha256']),purpose='Fresh exact alternative-method solve with measured timing and retained transition identity')
                    answer=result['answer'];assert answer['scalar_dos']==expected['scalar_dos'] and answer['open_y_operator']==expected['open_y_operator'] and answer['closed_port_rows']==expected['closed_port_rows']
                    e=result['execution'];record=dict(case=ci,N=n,method=spec['method'],plan_key=spec['plan_key'],repeat=repeat+1,total_ns=e['total_ns'],prepare_ns=e.get('prepare_ns',0),arithmetic_ns=e['arithmetic_ns'],reconstruction_ns=answer['reconstruction_ns'],exact=True)
                    measurements.append(record);emit(status='EXACT',**record)
                    save(ram/'PROGRESS.json',dict(completed=len(measurements),total=165,N=n,method=spec['method'],repeat=repeat+1))
            local=[x for x in measurements if x['N']==n];fresh_key=specs[indices[0]]['plan_key']
            bykey={key:[r for r in local if r['plan_key']==key] for key in {r['plan_key'] for r in local}}
            medians={key:int(statistics.median(r['total_ns'] for r in rows)) for key,rows in bykey.items()}
            for key,rows in bykey.items():
                ci=min(r['case'] for r in rows);g=dict(case=ci,N=n,method=specs[ci]['method'],plan_key=key,aliases=sorted({r['method'] for r in rows}),repetitions=len(rows),median_total_ns=medians[key],median_arithmetic_ns=int(statistics.median(r['arithmetic_ns'] for r in rows)),beats_fresh=int(medians[key]<medians[fresh_key]))
                groups.append(g)
            save(ram/'MEASUREMENTS.json',measurements);save(ram/'GROUPED_EXPERIENCE.json',groups)
            emit(status='SIZE_COMPLETE',N=n,best=min([g for g in groups if g['N']==n],key=lambda g:g['median_total_ns']))
            flush(ram,durable,f'N{n}')
        reserved={g['plan_key']:g for g in groups if g['N']==96};best=min(g['median_total_ns'] for g in reserved.values())
        evaluation={policy:dict(method=specs[ci]['method'],median_total_ns=reserved[specs[ci]['plan_key']]['median_total_ns'],excess_ns=reserved[specs[ci]['plan_key']]['median_total_ns']-best) for policy,ci in test_choices.items()}
        save(ram/'EVALUATION.json',dict(reserved_N=96,frozen_choices=evaluation,best_observed_median_ns=best))
        evidence=dict(binding=binding,groups=groups,measurements=measurements,policy_evaluation=evaluation)
        published=session.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=evidence,source_binding=binding,provenance=dict(operation='GEN4_SPIN_TRAIN_SOLVE',session=str(session.directory),method='three rotated-order repetitions; identical plans grouped; native policies frozen before N96')),purpose='Retain executable transition experience and held-out method comparison')
        bundle=session.execute('GEN3_RESULT_EXPORT',dict(roots=[published['result_ref']]),purpose='Export exact transition-training experience for GEN3/GEN4 installation')
        compressed(ram/'TRAINING_BUNDLE.json.gz',bundle)
        save(ram/'CHECKPOINT.json',session.execute('GEN3_CHECKPOINT',{},purpose='Preserve learned native models, observed transitions and exact calculation history'))
        save(ram/'COMPLETE.json',dict(status='COMPLETE',fresh_exact_solves=len(measurements),source_sizes=SIZES,methods=METHODS,repeats=3,session=str(session.directory),experience_ref=published['result_ref'],evaluation=evaluation))
    finally:
        session.close();monitor.stop(ram/'TELEMETRY.json')
    flush(ram,durable,'COMPLETE');emit(status='COMPLETE',workers_stopped=all(not p.is_alive() for p in adapter.workers))

if __name__=='__main__':main()
