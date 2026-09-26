"""Fresh interpretable models and bounded outcome-driven research policy."""
import math,time,statistics,collections
from pathlib import Path
import numpy as np
from source_ops import load,save,digest,append,writecsv
P=Path(__file__).resolve().parent
REQUIRED=['source_hash','graph_hash','source_lineage','ordered_ports_hash','plan_hash','method','backend_id','worker_topology_id','cache_state','timing_scope','root_batch','CRT_prime_count','branch_count','retained_width','weighted_entries','runtime_package_hash','readout_backend']

def question(key,kind,theme,methods=None,alternate=False,parent=None,reason='',repeat_round=0):
    c=load(P/'sources'/f'{key}.json');f=c['features'];plan=c.get('plan',{}).get('selected',{})
    bucket=[f['components']>1, f['minfill_width']//5, int(math.log2(max(1,plan.get('branches',1))))//2]
    family=digest([c['source_lineage'].split(' -> ')[0],theme,bucket])[:16]
    identity=dict(source_hash=c['source']['source_sha256'],source_family=c['source_lineage'],intervention_class=theme,ordered_ports=c['reference'].get('retained_ports',c['reference'].get('ports',[])),method_pair=methods or ['cooperative_gpu'],plan_family='alternate' if alternate else 'source_selected',structural_feature_bucket=bucket,repeat_round=repeat_round)
    qid=digest(identity|dict(kind=kind))[:24]
    text={'cpu':'Which admitted exact CPU method is cheapest for this source and cache state?', 'gpu':'What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs?', 'rule':'Can this source decomposition become an independently verified reusable exact rule?', 'variant':'Does a port-preserving gauge-related source retain the measured route/cost behavior?', 'diagnostic':'Which concrete source or verifier capacity condition explains this failure?'}[kind]
    if alternate:text='Which PRE plan features explain the measured cost difference between distinct exact plans on the same cooperative14 backend?'
    return dict(question_id=qid,kind=kind,source_key=key,N=c['source']['N'],theme=theme,narrow_family=family,novelty_fingerprint=identity,question=text,parent_question=parent,why_chosen=reason or 'Diverse source/backend calibration',methods=methods or [],alternate=alternate,repeats=3,repeat_round=repeat_round,predicted_seconds=estimate_raw(c,kind,alternate),maximum_seconds=2400 if kind=='gpu' else 360,expected_information_gain=3.,expected_discriminating_outcomes=['Backend/method ranking changes with source structure','Work-to-time residual points to preparation, factors or readout','Exact reduction survives or fails its explicit source preconditions'],verification_contract='All scalar coefficients and ordered port rows, count and first/second moments; GPU open and closed operators; canonical or independently derived exact reference; no unadmitted fallback verifier',claim_type='NEWLY_PRECOMMITTED',features_used=list(f),inputs_hashes=dict(source=c['source']['source_sha256'],source_record=digest(c)))

def estimate_raw(c,kind,alternate=False):
    if kind in ['diagnostic','rule','variant']:return 3.
    if kind=='cpu':return 15.
    p=c.get('plan',{});sel=p.get('selected',{});work=sel.get('weighted_entries',c['features']['minfill_work'])*p.get('root_count',c['features']['root_bound'])*len(p.get('primes',[1]*c['features']['crt_primes']))
    return min(2200.,max(20.,work/2.5e11*4+20))*(1.4 if alternate else 1)

def initialize():
    specs=[('N100','cpu','packet_placement',['components','variable_elimination','memo_components','warm_components']),('N096','gpu','plan_discrimination',None),('N105','cpu','packet_placement',['components','variable_elimination','memo_components','warm_components']),('N072','gpu','source_calibration',None),('N100','gpu','packet_placement',None),('N084','gpu','source_calibration',None),('N105','gpu','packet_placement',None),('N090','gpu','transition_calibration',None),('N100_prefix','gpu','prefix_calibration',None),('N105_prefix','gpu','prefix_calibration',None),('N108','gpu','branch_calibration',None),('N112','gpu','branch_calibration',None),('N119','gpu','high_cost_calibration',None),('N030','gpu','low_width_calibration',None),('N024','cpu','low_width_calibration',['components','variable_elimination'])]
    specs=[x for x in specs if x[0]!='N030']
    return [question(k,t,theme,m,alternate=k=='N096') for k,t,theme,m in specs]

def fit_models(observations):
    groups=collections.defaultdict(list);excluded=[]
    for o in observations:
        if any(o.get(k) is None for k in REQUIRED):o['cost_context']='INCOMPLETE_COST_CONTEXT';excluded.append(dict(question=o['question_id'],reason='INCOMPLETE_COST_CONTEXT'));continue
        if not o.get('warm_training_eligible'):excluded.append(dict(question=o['question_id'],reason='COLD_OR_INITIAL_LOADING_MEASUREMENT'));continue
        groups[(o['backend_id'],o['method'],o['cache_state'],o['readout_backend'],o['worker_topology_id'])].append(o)
    models={};residuals=[]
    for group,rs in groups.items():
        by=collections.defaultdict(list)
        for o in rs:by[(o['source_hash'],o['plan_hash'])].append(o)
        samples=[]
        for key,rr in by.items():
            o=rr[0];x=math.log(max(1,o['weighted_entries']*max(1,o['CRT_prime_count'])*max(1,o.get('root_count',o['features']['root_bound']) if group[0]!='LOCAL_FLINT_CPU' else 1)))
            samples.append((key,x,rr))
        targets=['end_to_end_solve_seconds','worker_preparation_seconds','crt_reconstruction_seconds','cpu_exact_seconds' if group[0]=='LOCAL_FLINT_CPU' else 'modular_gpu_seconds']
        fitted={}
        for target in targets:
            valid=[r for r in samples if any(o['timings'].get(target,0)>0 for o in r[2])]
            if not valid:continue
            xs=np.array([r[1] for r in valid]);ys=np.log([statistics.median(o['timings'][target] for o in r[2] if o['timings'].get(target,0)>0) for r in valid]);X=np.stack([np.ones(len(xs)),xs],axis=1)
            if len(xs)>=4 and np.std(xs)>.15:
                b=np.linalg.lstsq(X,ys,rcond=None)[0];scope='LOG_LINEAR_PRE_WORK';pred=X@b
            else:b=np.array([float(np.median(ys)),0.]);scope='LOCAL_MEDIAN_PENDING_DIVERSE_SOURCES';pred=X@b
            errors=ys-pred;loo=[]
            if len(xs)>=5:
                for i in range(len(xs)):
                    keep=np.arange(len(xs))!=i;bb=np.linalg.lstsq(X[keep],ys[keep],rcond=None)[0];loo.append(float(abs(X[i]@bb-ys[i])))
            fitted[target]=dict(intercept=float(b[0]),log_work_slope=float(b[1]),log_residual_sd=float(np.std(errors)),leave_one_source_plan_out_log_MAE=float(np.mean(loo)) if loo else None,independent_source_plans=len(valid),fit=scope)
            if target=='end_to_end_solve_seconds':
                for i,r in enumerate(valid):residuals.append(dict(source_hash=r[0][0],plan_hash=r[0][1],backend=group[0],method=group[1],cache_state=group[2],log_residual=float(errors[i]),observed_seconds=float(np.exp(ys[i]))))
        models['|'.join(group)]=dict(backend=group[0],method=group[1],cache_state=group[2],readout_backend=group[3],topology=group[4],independent_sources=len({r[0][0] for r in samples}),targets=fitted,status='LEARNED_HEURISTIC',features=['PRE weighted factor entries','PRE roots','PRE prime count'],conditioning=['backend','method','topology','cache state','readout'],plan_identity='Every sample grouped by source and exact plan hash; held-out source/plan grouping used for error',memory_model='Observed allocations retained; no fitted memory forecast until multiple matched measurements')
    return models,excluded,sorted(residuals,key=lambda x:-abs(x['log_residual']))

def follow(state,q,result,error=None):
    children=[]
    if error:
        if q['kind']!='diagnostic':children.append(question(q['source_key'],'diagnostic','capacity_diagnosis',parent=q['question_id'],reason='One targeted follow-up for this failed attempt'))
        state['blocked_sources'][q['source_key']+'|'+q['kind']]=str(error)[-300:]
        return children
    if q['kind'] in ['cpu','gpu']:
        obs=result.get('observations',[]);by=collections.defaultdict(list)
        for o in obs:
            if o.get('warm_training_eligible'):by[(o['method'],o['plan_hash'],o['cache_state'])].append(o['timings']['end_to_end_solve_seconds'])
        cvs=[statistics.pstdev(v)/max(statistics.mean(v),1e-9) for v in by.values() if len(v)>=3];med=[statistics.median(v) for v in by.values()]
        tie=len(med)>1 and max(med)/min(med)<1.15
        if q.get('repeat_round',0)==0 and ((cvs and max(cvs)>.15) or tie):
            children.append(question(q['source_key'],q['kind'],q['theme'],q.get('methods'),q.get('alternate'),q['question_id'],'One additional three-repeat block: measured variance or a close route tie',1))
        if q['source_key'] in ['N100','N105'] and q['kind']=='cpu':children.append(question(q['source_key'],'rule','component_rule',parent=q['question_id'],reason='Measured packet routes motivate an exact reusable partition rule'))
        if q['source_key'] in ['N072','N084','N096','N100','N105'] and q.get('repeat_round',0)==0:
            children.append(question(q['source_key'],'variant','gauge_transfer',parent=q['question_id'],reason='One source-preserving intervention tests whether the route cost follows topology or coefficient representation'))
        informative=(max(cvs,default=0)<.15 and (len(med)==1 or max(med)/min(med)>1.15))
        state['low_information'][q['narrow_family']]=0 if informative else state['low_information'].get(q['narrow_family'],0)+1
    elif q['kind']=='variant' and result.get('variant_key'):
        key=result['variant_key'];c=load(P/'sources'/f'{key}.json')
        if c['features']['minfill_width']<=14 and c['features']['max_component']<=18:
            children.append(question(key,'cpu','same_N_transfer',['components','variable_elimination'],parent=q['question_id'],reason='Fresh exact comparison after independent gauge inverse verification'))
        elif c['source']['N']<=96:children.append(question(key,'gpu','same_N_transfer',parent=q['question_id'],reason='Fresh cooperative solve of explicit port-preserving gauge source'))
    return children[:2]

def add_candidates(state,qs):
    for q in qs:
        if q['question_id'] in state['seen'] or state['low_information'].get(q['narrow_family'],0)>=3:continue
        if len(state['candidates'])>=40:break
        if sum(x['narrow_family']==q['narrow_family'] for x in state['candidates'])>=8:continue
        state['seen'].append(q['question_id']);q['enqueued_step']=state['steps'];state['candidates'].append(q)

def refill(state):
    if len(state['candidates'])>=30 and len({q['narrow_family'] for q in state['candidates']})>=5:return
    measured={o['source_key'] for o in state['observations']};donekeys={r['question']['source_key'] for r in state['completed'].values()}
    choices=[]
    for f in load(P/'SOURCE_FEATURES.json'):
        key=f['key']
        if key in measured or key+'|gpu' in state['blocked_sources'] or key+'|cpu' in state['blocked_sources']:continue
        if f['N']==120 and len(measured)<20:continue
        kind='cpu' if f['minfill_width']<=12 else 'gpu'
        if kind=='gpu' and f['N']<25:continue
        methods=['variable_elimination']
        if f['max_component']<=18 and f['local_assignments']<400000:methods.append('components')
        q=question(key,kind,'unmeasured_regime',methods if kind=='cpu' else None,reason='Unmeasured structural regime chosen from fresh model coverage')
        # Source structure, not size, drives novelty; prefer distance from measured feature support.
        others=[o['features'] for o in state['observations']]
        distance=min((abs(f['minfill_width']-o['minfill_width'])+abs(math.log2(max(1,f['local_assignments']))-math.log2(max(1,o['local_assignments'])))/10+abs(f['crt_primes']-o['crt_primes']) for o in others),default=10)
        q['expected_information_gain']=3+distance;choices.append(q)
    # Residual-driven matched plan investigations: one bounded alternate per source.
    for r in state.get('residuals',[])[:8]:
        if r['backend']!='COOP14_MIG_BRANCH_GROUP' or abs(r['log_residual'])<.3:continue
        o=next((o for o in state['observations'] if o['source_hash']==r['source_hash']),None)
        if o and o['features']['N']<=96:choices.append(question(o['source_key'],'gpu','residual_plan',alternate=True,reason='Large fresh cost residual motivates a materially different exact plan'))
    choices.sort(key=lambda q:-score(state,q))
    # Round-robin structural families prevents a cheap sibling backlog filling every slot.
    buckets=collections.defaultdict(list)
    for q in choices:
        if q['question_id'] not in state['seen']:buckets[q['narrow_family']].append(q)
    ordered=[]
    while any(buckets.values()):
        for qs in buckets.values():
            if qs:ordered.append(qs.pop(0))
    add_candidates(state,ordered)

def score(state,q):
    family_count=sum(r['question']['narrow_family']==q['narrow_family'] for r in state['completed'].values())
    age=state['steps']-q.get('enqueued_step',state['steps'])
    backend='COOP14_MIG_BRANCH_GROUP' if q['kind']=='gpu' else 'LOCAL_FLINT_CPU'
    c=load(P/'sources'/f'{q["source_key"]}.json');p=c.get('plan',{});f=c['features'];sel=p.get('selected',{})
    work=max(1,sel.get('weighted_entries',f['minfill_work'])*max(1,p.get('root_count',f['root_bound']) if q['kind']=='gpu' else 1)*max(1,len(p.get('primes',[])) if q['kind']=='gpu' else 1))
    predictions=[];uncertainty=0.
    for model in state.get('models',{}).values():
        if model['backend']!=backend or model['cache_state']=='CACHE_REUSE':continue
        fit=model['targets'].get('end_to_end_solve_seconds')
        if not fit or fit['independent_source_plans']<4:continue
        predictions.append(math.exp(max(-20,min(12,fit['intercept']+fit['log_work_slope']*math.log(work)))))
        uncertainty=max(uncertainty,fit['log_residual_sd'])
    if predictions and q['kind'] in ['cpu','gpu']:
        q['predicted_seconds']=max(5.,min(q['maximum_seconds'],statistics.median(predictions)*4+10));q['prediction_origin']='FRESH_BACKEND_MODEL';q['model_disagreement_ratio']=max(predictions)/max(min(predictions),1e-9)
    return (q['expected_information_gain']+uncertainty+2/(1+family_count))/math.sqrt(max(1,q['predicted_seconds']))+min(age,50)*.1

def frontier(state):
    groups=collections.defaultdict(list)
    for q in state['candidates']:
        if state['low_information'].get(q['narrow_family'],0)<3:groups[q['narrow_family']].append(q)
    for qs in groups.values():qs.sort(key=lambda q:-score(state,q))
    ordered=sorted(groups,key=lambda k:-score(state,groups[k][0]));active=[]
    # Strict <=20% per narrow family. Fewer than five distinct families cannot meet that rule.
    if len(ordered)<5:return []
    active=[groups[k][0] for k in ordered[:25]]
    while len(active)<25:
        added=False
        for k in ordered:
            used=sum(q['narrow_family']==k for q in active)
            if used<len(groups[k]) and (used+1)*5<=len(active)+1:
                active.append(groups[k][used]);added=True
                if len(active)==25:break
        if not added:break
    assert max(collections.Counter(q['narrow_family'] for q in active).values())*5<=len(active)
    return sorted(active,key=lambda q:-score(state,q))

def choose(state):
    if state['calibration']:
        # Deliberate diverse calibration is ordered, never displaced by descendants.
        return state['calibration'].pop(0)
    refill(state);active=frontier(state)
    if not active:return None
    # No starvation: at most two CPU/analysis questions while admissible GPU work waits.
    gpu=[q for q in active if q['kind']=='gpu']
    q=gpu[0] if gpu and state['non_gpu_streak']>=2 else active[0]
    state['candidates']=[r for r in state['candidates'] if r['question_id']!=q['question_id']]
    return q
