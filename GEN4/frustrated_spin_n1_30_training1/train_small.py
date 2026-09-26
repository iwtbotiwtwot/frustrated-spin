"""Every N1..30: exact CPU method training and add-one-spin boundary reuse."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import json
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE'])
import planning
planning.SIZES=list(range(1,31))
from planning import ladder,plan,digest
from arithmetic import templates,cpu_values,reconstruct,brute,original
from catalog_run import save,compressed,emit,flush,Monitor
sys.path.insert(0,os.environ['GEN4_SPIN_TRAINING_CODE'])
from methods import generate,features,METHODS
from SAM_PROJECT.session import DomainSession

class Frontier:
    """Exact transfer over a declared finite-horizon graph, retaining future-facing spins."""
    def __init__(self,future):
        self.future=future;self.n=0;self.frontier=[];self.counts=Counter({(0,0):1})
    def step(self,source):
        n=source['N'];assert n==self.n+1;v=n-1;started=time.perf_counter_ns()
        assert source['parent_vertices']==self.future['parent_vertices'][:n]
        frontier=sorted(set(range(min(n,4)))|{u for u,w,j in self.future['edges'] if u<n<=w})
        neighbors=[(u,j) for u,w,j in source['edges'] if w==v]
        assert all(u in self.frontier for u,j in neighbors)
        new=Counter()
        for (state,energy),count in self.counts.items():
            oldspin={u:1 if (state>>i)&1 else -1 for i,u in enumerate(self.frontier)}
            interaction=source['fields'][v]+sum(j*oldspin[u] for u,j in neighbors)
            for bit in [0,1]:
                spin=2*bit-1;target=0
                for i,u in enumerate(frontier):target|=(bit if u==v else int(oldspin[u]>0))<<i
                new[target,energy-spin*interaction]+=count
        self.counts=new;self.frontier=frontier;self.n=n
        portrows=[Counter() for _ in range(1<<min(n,4))]
        for (state,energy),count in new.items():
            ports=sum(((state>>frontier.index(v))&1)<<v for v in range(min(n,4)))
            portrows[ports][energy]+=count
        total=Counter()
        for row in portrows:total.update(row)
        assert sum(total.values())==1<<n
        return dict(source_sha256=source['source_sha256'],N=n,closed_port_rows=[[[e,str(c)] for e,c in sorted(row.items())] for row in portrows],
                    scalar_dos=[[e,str(c)] for e,c in sorted(total.items())],configuration_count=str(1<<n),
                    frontier_vertices=frontier,retained_cells=len(new),future_horizon_N=self.future['N'],future_source_sha256=self.future['source_sha256'],
                    total_ns=time.perf_counter_ns()-started,prior_counts_reused=True)

class Small:
    def __init__(self,base,sources,cases,ram):
        self.base=base;self.sources=sources;self.cases=cases;self.ram=ram;self.frontiers=[Frontier(sources[-1]) for _ in range(3)]
    def close(self):self.base.close()
    def execute(self,operation,payload):
        if operation=='GEN4_SPIN_SMALL_SOLVE':
            source,p,ts=self.cases[payload['case']];assert source['source_sha256']==payload['source_sha256']
            start=time.perf_counter_ns();values=cpu_values(ts,p);arithmetic_ns=time.perf_counter_ns()-start
            answer=reconstruct(source,p,values);result=dict(answer=answer,total_ns=time.perf_counter_ns()-start,arithmetic_ns=arithmetic_ns,reconstruction_ns=answer['reconstruction_ns'])
            compressed(self.ram/f'case{payload["case"]:03d}_r{payload["repeat"]}.json.gz',result)
            return result
        if operation=='GEN4_SPIN_INCREMENTAL_STEP':
            source=self.sources[payload['N']-1];assert source['source_sha256']==payload['source_sha256']
            result=self.frontiers[payload['repeat']-1].step(source)
            compressed(self.ram/f'incremental_N{source["N"]}_r{payload["repeat"]}.json.gz',result)
            return result
        return self.base.execute(operation,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);args=ap.parse_args()
    ram=args.ram;durable=args.durable;ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True)
    sources,frozen=ladder();cases=[];specs=[];previous=None;previous_plan=None
    for source in sources:
        for p in generate(source,frozen,previous_plan):
            ci=len(cases);cases.append((source,p,templates(source,p)))
            fs=features(source,previous,previous_plan,p)
            fs={k:v+[0] for k,v in fs.items()}
            specs.append(dict(case=ci,N=source['N'],method=p['training_method'],plan_key=p['mathematical_plan_sha256'],features=fs,plan=p))
        previous=source;previous_plan=plan(source,frozen,previous_plan)
    save(ram/'SOURCES.json',sources);save(ram/'SPECIFICATIONS.json',specs);save(ram/'SOURCE_BINDING.json',original.verify_sources())
    binding=dict(campaign='GEN4_SPIN_N1_30_TRANSITION_TRAINING1',roster=digest(sources),training_N=[1,22],development_N=[23,26],reserved_N=[27,30],incremental_horizon_source=sources[-1]['source_sha256'])
    s=DomainSession.start('MATTER_SEARCH',objective='Train every integer N1..30, including exact add-one-spin boundary transfer and native policy comparison',output_root=ram/'sessions',receipt_storage='gzip')
    emit(session=s.manifest,path=str(s.directory));assert s.manifest['global_slc']=='SLC-GEN4-P1'
    adapter=Small(s.consumer,sources,cases,ram);s.consumer=adapter;monitor=Monitor().start()
    measurements=[];groups=[];learned={};predictions={};expected_by_n={};incremental_specs={}
    try:
        for source in sources:
            n=source['N'];indices=list(range((n-1)*5,n*5));base=specs[indices[0]]
            # Incremental feature declares the retained boundary and reuse mode before timing.
            boundary=sorted(set(range(min(n,4)))|{u for u,w,j in sources[-1]['edges'] if u<n<=w})
            incfeatures={k:v[:-1]+[1] for k,v in base['features'].items()}
            incfeatures['structural'][2]=len(boundary);incfeatures['structural'][3]=1
            incfeatures['structural'][4]=1<<len(boundary)
            incfeatures['combined']=incfeatures['structural'][:-1]+incfeatures['transition'][:-1]+[1]
            incspec=dict(case='incremental',N=n,method='incremental_boundary',plan_key='incremental:'+source['source_sha256'],features=incfeatures)
            incremental_specs[n]=incspec
            if n==27:
                for family in ['structural','transition','combined']:
                    rows=[dict(features=g['features'][family],label=g['best_label'],split=0 if g['N']<=22 else 1,witness=f'N{g["N"]}/{g["method"]}/{g["plan_key"]}') for g in groups]
                    name='spin-n1-30-'+family+'-v1';model_binding=dict(**binding,feature_family=family)
                    fit=s.execute('GEN3_TREE_FIT',dict(name=name,rows=rows,source_binding=model_binding),purpose='Learn fastest exact restart/transition method; reserve all N27..30 outcomes')
                    model=s.execute('GEN3_TREE_EXPORT',dict(name=name),purpose='Freeze native all-integer transition policy before reserved sizes')
                    learned[family]=dict(fit=fit,model=model,binding=model_binding,rows=rows)
                save(ram/'FROZEN_MODELS.json',learned);flush(ram,durable,'FROZEN_BEFORE_N27')
            if n>=27:
                for family,m in learned.items():
                    pred=s.execute('GEN3_TREE_PREDICT',dict(name=m['model']['record']['name'],rows=[dict(id=specs[ci]['method'],features=specs[ci]['features'][family]) for ci in indices]+[dict(id='incremental_boundary',features=incfeatures[family])],source_binding=m['binding']),purpose='Freeze method prediction before the reserved integer-size timings')
                    predictions[f'{n}:{family}']=pred
                save(ram/'RESERVED_PREDICTIONS.json',predictions)
            for repeat in range(3):
                for ci in indices[repeat:]+indices[:repeat]:
                    spec=specs[ci]
                    result=s.execute('GEN4_SPIN_SMALL_SOLVE',dict(case=ci,repeat=repeat+1,source_sha256=source['source_sha256']),purpose='Fresh exact CPU spectrum with one of five transition/restart plans')
                    answer=result['answer'];reference=expected_by_n.setdefault(n,answer)
                    assert answer['scalar_dos']==reference['scalar_dos'] and answer['closed_port_rows']==reference['closed_port_rows']
                    if repeat==0 and ci==indices[0] and n<=18:assert answer['closed_port_rows']==brute(source,cases[ci][1]['ports'])
                    measurements.append(dict(case=ci,N=n,method=spec['method'],plan_key=spec['plan_key'],repeat=repeat+1,total_ns=result['total_ns'],exact=True))
                inc=s.execute('GEN4_SPIN_INCREMENTAL_STEP',dict(N=n,repeat=repeat+1,source_sha256=source['source_sha256']),purpose='Advance exact retained boundary counts by one spin using the declared N30 horizon')
                assert inc['scalar_dos']==expected_by_n[n]['scalar_dos'] and inc['closed_port_rows']==expected_by_n[n]['closed_port_rows']
                measurements.append(dict(case='incremental',N=n,method='incremental_boundary',plan_key=incspec['plan_key'],repeat=repeat+1,total_ns=inc['total_ns'],exact=True,frontier_bits=len(inc['frontier_vertices']),retained_cells=inc['retained_cells']))
            local=[r for r in measurements if r['N']==n];bykey={key:[r for r in local if r['plan_key']==key] for key in {r['plan_key'] for r in local}}
            medians={key:int(statistics.median(r['total_ns'] for r in rows)) for key,rows in bykey.items()};best=min(medians.values())
            for key,rows in bykey.items():
                spec=incspec if rows[0]['case']=='incremental' else specs[min(r['case'] for r in rows)]
                groups.append(dict(N=n,method=spec['method'],plan_key=key,features=spec['features'],aliases=sorted({r['method'] for r in rows}),median_ns=medians[key],best_label=int(medians[key]==best),repetitions=len(rows)))
            save(ram/'GROUPED_EXPERIENCE.json',groups);save(ram/'MEASUREMENTS.json',measurements)
            save(ram/'PROGRESS.json',dict(completed_N=n,completed_calculations=len(measurements),total_calculations=540))
            emit(status='SIZE_COMPLETE',N=n,calculations=len(measurements),best=min([g for g in groups if g['N']==n],key=lambda g:g['median_ns']),incremental_ns=medians[incspec['plan_key']],fresh_ns=medians[base['plan_key']])
            if n in [10,20,26,30]:flush(ram,durable,f'N{n}')
        save(ram/'EXACT_SPECTRA.json',expected_by_n)
        transfer_states=[dict(N=f.n,frontier=f.frontier,counts=[[state,e,str(c)] for (state,e),c in sorted(f.counts.items())]) for f in adapter.frontiers]
        save(ram/'TRANSFER_STATES.json',transfer_states)
        evaluation={}
        for n in range(27,31):
            choices=[g for g in groups if g['N']==n];best=min(g['median_ns'] for g in choices)
            bymethod={m:g for g in choices for m in g['aliases']}
            for family in learned:
                pred=predictions[f'{n}:{family}']['predictions'];prob={r['id']:Fraction(r['probability']) for r in pred}
                winners=[m for m,p in prob.items() if p==max(prob.values())]
                evaluation[f'{n}:{family}']=dict(predicted_tied_methods=sorted(winners),best_median_ns=best,
                                                selected_median_range_ns=[min(bymethod[m]['median_ns'] for m in winners),max(bymethod[m]['median_ns'] for m in winners)],
                                                fastest_in_top_tie=any(bymethod[m]['median_ns']==best for m in winners))
        save(ram/'EVALUATION.json',evaluation)
        obj=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(sources=sources,groups=groups,measurements=measurements,evaluation=evaluation,transfer_states=transfer_states),source_binding=binding,provenance=dict(method='Exact CPU NTT restarts compared with source-bound boundary-count transfer; three repetitions',session=str(s.directory))),purpose='Retain every integer source, 29transitions, exact execution experience and reusable finite-horizon boundary state')
        compressed(ram/'TRAINING_BUNDLE.json.gz',s.execute('GEN3_RESULT_EXPORT',dict(roots=[obj['result_ref']]),purpose='Export exact all-integer transition-training experience'))
        save(ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Retain three native learned policies and N1..30 transition experience'))
        save(ram/'COMPLETE.json',dict(status='COMPLETE',sizes=list(range(1,31)),methods=METHODS+['incremental_boundary'],repeats=3,exact_calculations=len(measurements),session=str(s.directory),experience_ref=obj['result_ref'],evaluation=evaluation))
    finally:s.close();monitor.stop(ram/'TELEMETRY.json')
    flush(ram,durable,'COMPLETE');emit(status='COMPLETE')

if __name__=='__main__':main()
