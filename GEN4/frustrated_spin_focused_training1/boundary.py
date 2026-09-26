"""Focused boundary reuse: incoming state features and held topology evaluation."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,hashlib,json,sys,time,statistics,traceback
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE']);sys.path.insert(0,str(Path(__file__).resolve().parent))
from planning import ladder,plan,digest
from arithmetic import templates,cpu_values,reconstruct,brute
from engine import save,compressed,emit,flush,Monitor
from design import prefix,integer_log
import cost
from SAM_PROJECT.session import DomainSession

class Frontier:
    def __init__(self,future):self.future=future;self.n=0;self.frontier=[];self.counts=Counter({(0,0):1})
    def step(self,source):
        n=source['N'];assert n==self.n+1;v=n-1;started=time.perf_counter_ns();assert source['parent_vertices']==self.future['parent_vertices'][:n]
        frontier=sorted(set(range(min(n,4)))|{u for u,w,j in self.future['edges'] if u<n<=w});neighbors=[(u,j) for u,w,j in source['edges'] if w==v];assert all(u in self.frontier for u,j in neighbors);new=Counter();input_cells=len(self.counts)
        for (state,energy),count in self.counts.items():
            oldspin={u:1 if (state>>i)&1 else -1 for i,u in enumerate(self.frontier)};interaction=source['fields'][v]+sum(j*oldspin[u] for u,j in neighbors)
            for bit in [0,1]:
                spin=2*bit-1;target=0
                for i,u in enumerate(frontier):target|=(bit if u==v else int(oldspin[u]>0))<<i
                new[target,energy-spin*interaction]+=count
        self.counts=new;self.frontier=frontier;self.n=n;portrows=[Counter() for _ in range(1<<min(n,4))]
        for (state,energy),count in new.items():
            ports=sum(((state>>frontier.index(v))&1)<<v for v in range(min(n,4)));portrows[ports][energy]+=count
        total=Counter()
        for row in portrows:total.update(row)
        assert sum(total.values())==1<<n
        return dict(source_sha256=source['source_sha256'],N=n,closed_port_rows=[[[e,str(c)] for e,c in sorted(row.items())] for row in portrows],scalar_dos=[[e,str(c)] for e,c in sorted(total.items())],configuration_count=str(1<<n),input_cells=input_cells,retained_cells=len(new),frontier_vertices=frontier,future_source_sha256=self.future['source_sha256'],total_ns=time.perf_counter_ns()-started)

def variant(parent,seed):
    result=deepcopy(parent)
    if seed:
        edges={(u,v):j for u,v,j in parent['edges']};done=attempt=0
        while done<2:
            pairs=sorted(edges);h=hashlib.sha256(f'FOCUSED-SMALL-TWO-SWAPS|{seed}|{attempt}'.encode()).digest();attempt+=1;a,b=pairs[int.from_bytes(h[:4],'big')%len(pairs)];c,d=pairs[int.from_bytes(h[4:8],'big')%len(pairs)]
            if len({a,b,c,d})<4 or (a,b) in [(0,1),(2,3)] or (c,d) in [(0,1),(2,3)]:continue
            x,y=tuple(sorted((a,d))),tuple(sorted((c,b)))
            if x in edges or y in edges or x in [(0,1),(2,3)] or y in [(0,1),(2,3)]:continue
            j,k=edges.pop((a,b)),edges.pop((c,d));edges[x]=j;edges[y]=k;done+=1
        result['edges']=[[*e,j] for e,j in sorted(edges.items())];result['family']=f'FOCUSED_N30_TWO_SWAPS_V1_SEED{seed}'
    result.pop('source_sha256',None);result['source_sha256']=digest(result);return result

class Adapter:
    def __init__(self,base,ram,configs):self.base=base;self.ram=ram;self.configs=configs;self.states={}
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_BOUNDARY_FRESH':
            source,p,ts=self.configs[payload['case']];assert source['source_sha256']==payload['source_sha256'];started=time.perf_counter_ns();values=cpu_values(ts,p);mid=time.perf_counter_ns();ans=reconstruct(source,p,values);return dict(answer=ans,total_ns=time.perf_counter_ns()-started,prepare_ns=0,arithmetic_ns=mid-started,reconstruction_ns=ans['reconstruction_ns'])
        if op=='GEN4_BOUNDARY_ADVANCE':
            state=self.states[payload['state']];source=self.configs[payload['case']][0];assert source['source_sha256']==payload['source_sha256'];return state.step(source)
        if op=='GEN4_BOUNDARY_COST_FIT':return cost.choose(payload['training'],payload['development'])
        if op=='GEN4_BOUNDARY_COST_PREDICT':return dict(predicted_ns=cost.predict(payload['model'],payload['rows']))
        return self.base.execute(op,payload)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);a=ap.parse_args();ram=a.ram;durable=a.durable;ram.mkdir(parents=True,exist_ok=False);durable.mkdir(parents=True,exist_ok=True)
    parent=prefix(ladder()[0][-1],30);frozen=ladder()[1];configs=[];specs=[];sources=[]
    for seed in range(6):
        future=variant(parent,seed);sources.append(future);prev=None
        for n in range(1,31):
            source=prefix(future,n);p=plan(source,frozen,prev);configs.append((source,p,templates(source,p)));specs.append(dict(seed=seed,N=n,source=source,plan=p));prev=p
    save(ram/'SPECIFICATIONS.json',specs);save(ram/'FUTURE_SOURCES.json',sources)
    s=DomainSession.start('MATTER_SEARCH',objective='Learn when exact boundary advancement beats restart using incoming state size; reserve new small graph topologies',output_root=ram/'sessions',receipt_storage='gzip');emit(session=s.manifest,path=str(s.directory));adapter=Adapter(s.consumer,ram,configs);s.consumer=adapter;monitor=Monitor().start();measurements=[];groups=[];predictions={};models=None;expected={}
    binding=dict(campaign='GEN4_FOCUSED_BOUNDARY1',source_roster=digest(sources),training_topologies=[0,1,2],development_topologies=[3],reserved_topologies=[4,5],horizon=30,feature_names=['N','input_cells_log','input_bits','output_bits','dropped_bits','new_neighbors','bound','root_count','primes','restart_work_log','reuse'])
    try:
        for seed,future in enumerate(sources):
            if seed==4:
                train=[r for r in groups if r['split']=='train'];dev=[r for r in groups if r['split']=='development'];models=s.execute('GEN4_BOUNDARY_COST_FIT',dict(training=train,development=dev),purpose='Learn actual reuse/restart costs with incoming state size and select using development topology only');save(ram/'FROZEN_MODEL.json',models);flush(ram,durable,'FROZEN_BEFORE_RESERVED')
            for repeat in range(3):
                statekey=f'{seed}:{repeat}';frontier=Frontier(future);adapter.states[statekey]=frontier
                for n in range(1,31):
                    ci=seed*30+n-1;source,p,_=configs[ci];outbits=sorted(set(range(min(n,4)))|{u for u,v,j in future['edges'] if u<n<=v});common=[n,integer_log(len(frontier.counts)),len(frontier.frontier),len(outbits),len(set(frontier.frontier)-set(outbits)),sum(v==n-1 for u,v,j in source['edges']),source['energy_bound_B'],p['root_count'],len(p['primes']),integer_log(p['selected']['weighted_entries'])];gid=f'G{seed}-N{n}';split='train' if seed<=2 else 'development' if seed==3 else 'test'
                    if models and repeat==0 and n>=18:
                        prediction=s.execute('GEN4_BOUNDARY_COST_PREDICT',dict(model=models['selected'],rows=[dict(features=common+[0]),dict(features=common+[1])]),purpose='Predict restart versus boundary advancement before measuring this reserved step');predictions[gid]=dict(predicted_ns=prediction['predicted_ns'],selected='restart' if prediction['predicted_ns'][0]<=prediction['predicted_ns'][1] else 'incremental',features=common);save(ram/'RESERVED_PREDICTIONS.json',predictions)
                    # Alternate immediate restart/advance timing order.
                    operations=['restart','incremental'] if (n+repeat)%2 else ['incremental','restart']
                    for method in operations:
                        if method=='restart' and n<18:continue
                        if method=='restart':
                            result=s.execute('GEN4_BOUNDARY_FRESH',dict(case=ci,source_sha256=source['source_sha256']),purpose='Fresh exact CPU comparison for this focused transition');answer=result['answer'];times={k:result[k] for k in ['total_ns','prepare_ns','arithmetic_ns','reconstruction_ns']}
                        else:
                            answer=s.execute('GEN4_BOUNDARY_ADVANCE',dict(case=ci,state=statekey,source_sha256=source['source_sha256']),purpose='Advance actual incoming exact boundary state under the declared future source');times=dict(total_ns=answer['total_ns'],prepare_ns=0,arithmetic_ns=answer['total_ns'],reconstruction_ns=0)
                        ref=expected.setdefault(gid,answer);assert answer['scalar_dos']==ref['scalar_dos'] and answer['closed_port_rows']==ref['closed_port_rows']
                        if n==18 and repeat==0 and method=='restart':assert answer['closed_port_rows']==brute(source,p['ports'])
                        if n>=18:measurements.append(dict(group=gid,seed=seed,N=n,method=method,split=split,repeat=repeat+1,features=common+[int(method=='incremental')],**times))
                    if n>=18:emit(status='STEP',seed=seed,repeat=repeat+1,N=n,input_cells=1<<(common[1]//1024),output_cells=len(frontier.counts))
                compressed(ram/f'FINAL_STATE_G{seed}_r{repeat+1}.json.gz',dict(future=future,frontier=frontier.frontier,N=30,counts=[[state,e,str(c)] for (state,e),c in sorted(frontier.counts.items())]));del adapter.states[statekey]
            for n in range(18,31):
                for method in ['restart','incremental']:
                    rr=[r for r in measurements if r['seed']==seed and r['N']==n and r['method']==method];assert all(r['features']==rr[0]['features'] for r in rr)
                    groups.append(dict(group=f'G{seed}-N{n}',seed=seed,N=n,method=method,split=rr[0]['split'],features=rr[0]['features'],**{k:int(statistics.median(r[k] for r in rr)) for k in ['total_ns','prepare_ns','arithmetic_ns','reconstruction_ns']}))
            save(ram/'MEASUREMENTS.json',measurements);save(ram/'GROUPED_EXPERIENCE.json',groups);compressed(ram/'EXACT_SPECTRA.json.gz',expected);flush(ram,durable,f'G{seed}')
        evaluation={}
        for gid,pred in predictions.items():
            rr={r['method']:r['total_ns'] for r in groups if r['group']==gid};evaluation[gid]=dict(**pred,observed_ns=rr,excess_ns=rr[pred['selected']]-min(rr.values()))
        save(ram/'EVALUATION.json',evaluation)
        pub=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(binding=binding,groups=groups,models=models,evaluation=evaluation),source_binding=binding,provenance=dict(session=str(s.directory),backend='Python exact integer boundary transfer and CPU modular restarts; NumPy timing regression')),purpose='Retain focused incoming-state cost learning and held topology results');compressed(ram/'TRAINING_BUNDLE.json.gz',s.execute('GEN3_RESULT_EXPORT',dict(roots=[pub['result_ref']]),purpose='Export learned boundary timing model and examples'));save(ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Retain boundary research'));save(ram/'COMPLETE.json',dict(status='COMPLETE',timed_calculations=len(measurements),exact_advances=540,fresh_restarts=234,session=str(s.directory),experience_ref=pub['result_ref']))
    except BaseException:save(ram/'FAILURE.json',dict(traceback=traceback.format_exc()));raise
    finally:s.close();monitor.stop(ram/'TELEMETRY.json');flush(ram,durable,'FINAL')
    emit(status='COMPLETE')
if __name__=='__main__':main()
