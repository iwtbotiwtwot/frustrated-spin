"""Retained focused plans and explicitly hardware-bound execution-cost learning."""
from pathlib import Path
import json,math
from . import retained
from .spin_planning import digest
from .spin_cost import predict
HERE=Path(__file__).resolve().parent/'spin_data'

def metadata():return json.loads((HERE/'FOCUSED.json').read_text())
def decode(x):
    if isinstance(x,dict):
        if set(x)=={'__float64_hex__'}:return float.fromhex(x['__float64_hex__'])
        return {k:decode(v) for k,v in x.items()}
    if isinstance(x,list):return [decode(v) for v in x]
    return x

def data(machine):return decode(retained.get(machine,metadata()['experience_ref'],kind='mathematical_result')['value'])
def cached(machine,source_sha256):
    meta=metadata();row=meta['sources'].get(source_sha256)
    if row is None:return None
    value=retained.get(machine,row['result_ref'],kind='mathematical_result')['value']
    return dict(**value,result_ref=row['result_ref'])
def lg(x):return round(math.log2(max(1,int(x)))*1024)

def features(source,previous,previous_plan,p):
    """Exact normalized projection-map sizes without materializing the maps."""
    c=p['selected'];fixed=set(c['cutset']);fs=[(v,) for v in range(source['N']) if v not in fixed]
    fs += [(u,v) for u,v,j in source['edges'] if u not in fixed and v not in fixed and [u,v,j] not in p['glue']]
    recipes=set();factor_work=0
    for vertex in c['order']:
        selected=[f for f in fs if vertex in f];fs=[f for f in fs if vertex not in f];scope=tuple(sorted(set().union(*map(set,selected))-{vertex}));width=len(scope);factor_work+=(1<<width)*len(selected)
        for factor in selected:recipes.add((width,tuple(-1 if v==vertex else scope.index(v) for v in factor)))
        fs.append(scope)
    roots=p['root_count'];primes=len(p['primes']);work=c['weighted_entries'];factor_work*=c['branches']
    def edges(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v]))) for u,v,_ in s['edges']}
    new=edges(source)-edges(previous);old=set(previous['parent_vertices']);boundary={v for e in new for v in e if v in old}
    return [source['N'],len(source['edges']),c['width'],lg(c['branches']),lg(work),lg(work*roots*primes),lg(sum(4*(1<<w) for w,_ in recipes)),roots,primes,p['local_bound'],lg(factor_work*roots*primes),previous_plan['selected']['width'],lg(previous_plan['selected']['weighted_entries']),len(new),len(boundary)]

def dispatch(runtime,operation,payload):
    meta=metadata()
    if operation=='GEN3_SPIN_FOCUSED':
        retained.fields(payload);return dict(**meta,recomputed=False)
    if operation=='GEN3_SPIN_COST':
        retained.fields(payload,('source','previous_N'),('backend','search'))
        from .spin_catalog import validate_source,entry
        from .spin_methods import generate
        source=validate_source(payload['source']);_,previous=entry(runtime.machine,payload['previous_N']);backend=payload.get('backend','batched')
        if backend not in meta['cost_models']:raise ValueError('Unknown execution backend for timing model')
        observed=cached(runtime.machine,source['source_sha256'])
        if observed and observed.get('measurement_kind')=='single_exact_execution':
            return dict(source_sha256=source['source_sha256'],backend=backend,hardware=meta['hardware'],estimates=[],known_best=observed,estimated=False,
                        observed_nanoseconds=observed['measured_execution_ns'] if backend=='batched' else None,
                        measurement_kind='single_exact_execution',result_boundary='Retained frontier execution timing; no extrapolated N1..96 cost forecast for this new branch-group backend')
        record=meta['cost_models'][backend];value=decode(retained.get(runtime.machine,record['experience_ref'],kind='mathematical_result')['value']);model=value['models']['cost']['selected']
        frozen=json.loads((HERE/'PARENT_PLAN.json').read_text());search=payload.get('search','standard')
        if search not in ('standard','expanded'):raise ValueError('Unknown planning search')
        if search=='expanded':
            from .spin_expanded import expanded
            plans=expanded(source,frozen,previous['plan'])
        else:plans=generate(source,frozen,previous['plan'])
        vectors=[features(source,previous['source'],previous['plan'],p) for p in plans];times=predict(model,[dict(features=f) for f in vectors]);cached_row=cached(runtime.machine,source['source_sha256'])
        return dict(source_sha256=source['source_sha256'],backend=backend,hardware=meta['hardware'],model_ref=record['experience_ref'],estimates=[dict(method=p['training_method'],plan_sha256=p['mathematical_plan_sha256'],predicted_nanoseconds=round(t),predicted_seconds=format(t/1e9,".9f"),execution_admitted=p['selected']['width']<=22 and p['prime_product_sufficient']) for p,t in zip(plans,times)],known_best=cached_row,estimated=True,arithmetic_backend='NUMPY_CPU_TIMING_REGRESSION',result_boundary='Estimated pod execution cost, not a newly computed spectrum; source-plan preparation excluded')
    raise ValueError('Unknown focused operation')
