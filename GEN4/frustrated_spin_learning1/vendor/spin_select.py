"""Explicit source-bound structural/cached/focused native plan selection."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import time

OPS = ('GEN3_SPIN_SELECT',)
HERE = Path(__file__).resolve().parent/'spin_data'


def components(source):
    adjacency = [set() for _ in range(source['N'])]
    for u,v,j in source['edges']:
        if j: adjacency[u].add(v); adjacency[v].add(u)
    unseen=set(range(source['N'])); groups=[]
    while unseen:
        stack=[min(unseen)]; unseen.remove(stack[0]); group=[]
        while stack:
            vertex=stack.pop();group.append(vertex)
            for other in sorted(adjacency[vertex]&unseen):unseen.remove(other);stack.append(other)
        groups.append(sorted(group))
    return groups


def hardware():
    """Observe a signature; timing calibration is never inferred from GPU count alone."""
    result={'visible_devices':0,'devices':[],'matches_retained_signature':False}
    try:
        import cupy as cp
        count=int(cp.cuda.runtime.getDeviceCount()); result['visible_devices']=count
        for index in range(count):
            p=cp.cuda.runtime.getDeviceProperties(index);name=p.get('name',b'')
            result['devices'].append({'name':name.decode() if isinstance(name,bytes) else str(name),
                                      'multiprocessors':int(p['multiProcessorCount']),
                                      'total_bytes':int(p['totalGlobalMem'])})
        result['matches_retained_signature']=count==14 and all(
            d['multiprocessors']==46 and 22*(1<<30)<=d['total_bytes']<=25*(1<<30)
            and ('6000' in d['name'] or 'Blackwell' in d['name']) for d in result['devices'])
    except (ImportError,RuntimeError) as exc:result['probe_note']=type(exc).__name__
    return result


def dispatch(runtime, operation, payload):
    if operation not in OPS: raise ValueError('Unknown spin selector operation')
    from . import retained
    from .spin_catalog import validate_source, entry
    from .spin_planning import digest
    from .spin_focus import metadata, cached, features
    from .spin_gpu import prepare_plan
    retained.fields(payload,('source',),('previous_N','policy','backend','search','ports','execution_backend'))
    started=time.perf_counter_ns();source=validate_source(payload['source'])
    policy=payload.get('policy','auto');backend=payload.get('backend','batched')
    search=payload.get('search','standard');execution_backend=payload.get('execution_backend','auto')
    if policy not in ('auto','structural','focused_pairwise'):raise ValueError('Unknown spin selection policy')
    if backend not in ('batched','retained'):raise ValueError('Unknown focused readout backend')
    if search not in ('standard','expanded'):raise ValueError('Unknown spin plan search')
    if execution_backend not in ('auto','cpu','gpu'):raise ValueError('Unknown requested execution backend')
    ports=payload.get('ports',list(range(min(source['N'],4))))
    if not isinstance(ports,list) or len(set(ports))!=len(ports) or any(type(v) is not int or not 0<=v<source['N'] for v in ports):raise ValueError('Invalid selector ports')
    groups=components(source); maximum=max(map(len,groups)); focused=metadata()
    scope={'retained_hardware':focused['hardware'],'readout_backend':backend,
           'timing_forecast_used':False,'models_select_plans_only':True}
    if execution_backend=='cpu' or (execution_backend=='auto' and maximum<=20):
        plan={'schema':'GEN3_COMPONENT_SPIN_PLAN_V1','source_sha256':source['source_sha256'],
              'N':source['N'],'ports':ports,'backend':'CPU_EXACT_COMPONENT_POLYNOMIAL',
              'components':groups,'component_sizes':list(map(len,groups)),
              'largest_component':maximum,'enumeration_assignments':sum(1<<len(g) for g in groups),
              'component_enumeration_admitted':maximum<=20 and sum(1<<len(g) for g in groups)<=2000000,
              'execution_admitted':True if maximum<=20 and sum(1<<len(g) for g in groups)<=2000000 else None,
              'resource_admission':'CPU executor checks the actual supplied limits before arithmetic',
              'route':'component_exact' if maximum<=20 and sum(1<<len(g) for g in groups)<=2000000 else 'bounded_polynomial_elimination'}
        plan['mathematical_plan_sha256']=digest(plan)
        return {'source':source,'plan':plan,'execution_backend':'cpu','requested_policy':policy,
                'selected_policy':'component_structure','model_applied':False,'hardware_scope':scope,
                'selection_reason':'Independent component contraction avoids expanding the full2^N assignment space',
                'elapsed_ns':time.perf_counter_ns()-started,'result_boundary':'Plan only; no spectrum recomputed'}
    previous_n=payload.get('previous_N',96)
    previous_ref,previous=entry(runtime.machine,previous_n)
    anchor_note=None
    old_plan=previous['plan']
    if old_plan.get('generic_cutset_plan') is False or not isinstance(old_plan.get('selected'),dict) or not {'order','cutset','weighted_entries'}<=set(old_plan.get('selected',{})) or 'parent_elimination_order' not in old_plan:
        previous_ref,previous=entry(runtime.machine,96)
        anchor_note='Requested predecessor has component-route metadata; N96 supplies the retained ordering/features anchor only'
    known=cached(runtime.machine,source['source_sha256'])
    if known and known['plan'].get('ports')==ports and policy=='auto':
        plan=deepcopy(known['plan']);plan=prepare_plan(source,plan,{'ports':ports})
        return {'source':source,'plan':plan,'execution_backend':'gpu','requested_policy':policy,
                'selected_policy':'identical_source_cache','model_applied':False,
                'retained_plan_ref':known['result_ref'],'measurement_kind':known.get('measurement_kind','three_repeat_median'),
                'hardware_scope':scope,'cache_role':'Reuse exact mathematical plan; previous observed runtime is not a forecast on this device',
                'elapsed_ns':time.perf_counter_ns()-started,'result_boundary':'Plan only; no spectrum recomputed'}
    default_ports=list(range(min(source['N'],4)))
    if ports!=default_ports:
        if policy=='focused_pairwise':raise ValueError('Focused model was trained on the declared default port convention; use structural selection for custom ports')
        variants=[prepare_plan(source,None,{'ports':ports})]
        variants[0]['training_method']='fresh_min_fill_custom_ports'
    else:
        frozen=json.loads((HERE/'PARENT_PLAN.json').read_text())
        # Inherited conditioning vertices may not consume requested open ports.
        frozen['cutset_sites_in_order']=[v for v in frozen['cutset_sites_in_order'] if v not in {source['parent_vertices'][p] for p in ports}]
        if search=='expanded':
            from .spin_expanded import expanded
            variants=expanded(source,frozen,previous['plan'])
        else:
            from .spin_methods import generate
            variants=generate(source,frozen,previous['plan'])
        if known and known['plan'].get('ports')==ports:
            extra=deepcopy(known['plan']);extra['training_method']='retained_measured_plan';variants.append(extra)
    candidates=[];seen=set();rejected=[]
    for v in variants:
        try:p=prepare_plan(source,v,{'ports':ports})
        except ValueError as exc:
            rejected.append({'method':v.get('training_method'),'reason':str(exc)});continue
        key=digest({'cutset':p['selected']['cutset'],'order':p['selected']['order'],'ports':p['ports'],'glue':p['glue']})
        if key not in seen:seen.add(key);candidates.append(p)
    if not candidates:raise ValueError('No structurally admitted GPU candidate: '+str(rejected))
    observed=hardware() if policy in ('auto','focused_pairwise') else None
    applied=policy=='focused_pairwise' or (policy=='auto' and observed['matches_retained_signature'] and ports==default_ports)
    probabilities={};prediction=None;record=None
    if applied:
        name='spin-focused-fast-pairwise-v1' if backend=='batched' else 'spin-focused-pairwise-v1'
        records=json.loads((HERE/'FOCUSED_NATIVE_MODELS.json').read_text())
        if name not in records:raise ValueError('Requested focused model is not installed: '+name)
        record=records[name]
        vectors=[features(source,previous['source'],previous['plan'],p) for p in candidates]
        rows=[{'id':str(i)+':'+str(j),'features':[x-y for x,y in zip(vectors[i],vectors[j])]+vectors[i]+vectors[j]}
              for i in range(len(candidates)) for j in range(len(candidates)) if i!=j]
        if rows:
            prediction=runtime.execute('GEN3_TREE_PREDICT',{'name':name,'rows':rows,'source_binding':record['source_binding']})
            probabilities={r['id']:Fraction(r['probability']) for r in prediction['predictions']}
        wins={i:sum((probabilities.get(str(i)+':'+str(j),Fraction(0)) for j in range(len(candidates)) if i!=j),Fraction(0)) for i in range(len(candidates))}
        selected=min(range(len(candidates)),key=lambda i:(-wins[i],candidates[i]['selected']['weighted_entries'],i))
    else:
        wins={};selected=min(range(len(candidates)),key=lambda i:(candidates[i]['selected']['weighted_entries'],candidates[i]['selected']['width'],i))
    scope.update(observed_hardware=observed,explicit_transfer=policy=='focused_pairwise' and not observed['matches_retained_signature'] if observed else False,
                 model_training_scope='Six topology families sharing the retained N96 ancestor; pairwise ranking, not universal runtime calibration')
    return {'source':source,'plan':candidates[selected],'execution_backend':'gpu','requested_policy':policy,
            'selected_policy':'focused_pairwise' if applied else 'structural','model_applied':applied,
            'native_model':record['name'] if record else None,'model_prediction':prediction,
            'model_source_binding':record['source_binding'] if record else None,
            'candidate_comparison':[{'index':i,'method':p.get('training_method',p['selected'].get('method')),
                'weighted_entries':p['selected']['weighted_entries'],'width':p['selected']['width'],
                'branches':p['selected']['branches'],'pairwise_score':str(wins[i]) if i in wins else None,
                'execution_plan_sha256':p['execution_plan_sha256']} for i,p in enumerate(candidates)],
            'rejected_candidates':rejected,'previous_ref':previous_ref,'anchor_note':anchor_note,
            'hardware_scope':scope,'elapsed_ns':time.perf_counter_ns()-started,
            'result_boundary':'Plan selection only; exact source and requested spectrum are unchanged'}
