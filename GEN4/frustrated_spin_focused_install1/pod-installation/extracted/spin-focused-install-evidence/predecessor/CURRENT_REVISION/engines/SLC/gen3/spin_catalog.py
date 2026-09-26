"""Installed source-bound spin catalog, transition memory and frontier planner."""
from pathlib import Path
import json
from . import retained
from .spin_planning import plan, digest
from .spin_methods import generate, features
from fractions import Fraction

HERE=Path(__file__).resolve().parent/'spin_data'
OPS=tuple('GEN3_SPIN_'+x for x in ['CATALOG','ENTRY','TRANSITION','PLAN','LEARNING'])

def metadata():return json.loads((HERE/'CATALOG.json').read_text())

def entry(machine,n):
    meta=metadata();ref=meta['entries'].get(str(n))
    if ref is None:raise ValueError('N is not in the installed source roster')
    obj=retained.get(machine,ref,kind='mathematical_result')
    return ref,obj['value']

def validate_source(raw):
    if not isinstance(raw,dict):raise ValueError('Supply an explicit source graph')
    n=raw.get('N')
    if type(n) is not int or n<1:raise ValueError('N must be a positive integer')
    fields=raw.get('fields');vertices=raw.get('parent_vertices')
    if not isinstance(fields,list) or len(fields)!=n or any(type(x) is not int for x in fields):raise ValueError('One integer field per vertex required')
    if not isinstance(vertices,list) or len(vertices)!=n or any(type(x) is not int for x in vertices) or len(set(vertices))!=n:raise ValueError('Distinct stable parent vertex labels required')
    edges=[];seen=set()
    for e in raw.get('edges',[]):
        if not isinstance(e,list) or len(e)!=3 or any(type(x) is not int for x in e):raise ValueError('Each edge is [u,v,J] with integer entries')
        u,v,j=e
        if not 0<=u<n or not 0<=v<n or u==v:raise ValueError('Invalid edge vertices')
        pair=tuple(sorted((u,v)))
        if pair in seen:raise ValueError('Duplicate graph edge')
        seen.add(pair);edges.append([*pair,j])
    source=dict(N=n,fields=fields,edges=sorted(edges),parent_vertices=vertices,
                parent_instance_sha256=raw.get('parent_instance_sha256'),family=raw.get('family','CALLER_DECLARED_SPIN_GRAPH'),
                energy_bound_B=sum(map(abs,fields))+sum(abs(e[2]) for e in edges))
    source['source_sha256']=digest(source)
    if raw.get('source_sha256',source['source_sha256'])!=source['source_sha256']:raise ValueError('Source hash differs from supplied graph')
    return source

def dispatch(runtime,operation,payload):
    machine=runtime.machine;meta=metadata()
    if operation=='GEN3_SPIN_CATALOG':
        retained.fields(payload)
        return dict(**meta,recomputed=False,arithmetic_calls=0)
    if operation=='GEN3_SPIN_LEARNING':
        retained.fields(payload)
        return dict(models=meta['models'],experiences=meta['training_experience_refs'],active_model=meta['native_model'],note=meta['learning_note'],recomputed=False)
    if operation=='GEN3_SPIN_ENTRY':
        retained.fields(payload,('N',),('source_sha256',))
        ref,value=entry(machine,payload['N'])
        if payload.get('source_sha256',value['source']['source_sha256'])!=value['source']['source_sha256']:raise ValueError('Requested source differs from catalog entry')
        return dict(result_ref=ref,**value,recomputed=False,arithmetic_calls=0)
    if operation=='GEN3_SPIN_TRANSITION':
        retained.fields(payload,('from_N','to_N'))
        key=f'{payload["from_N"]}->{payload["to_N"]}'
        if key not in meta['transitions']:raise ValueError('Transition has no executed catalog receipt')
        ref=meta['transitions'][key];obj=retained.get(machine,ref,kind='mathematical_result')
        return dict(result_ref=ref,transition=obj['value'],recomputed=False,arithmetic_calls=0)
    if operation=='GEN3_SPIN_PLAN':
        retained.fields(payload,('source','previous_N'))
        source=validate_source(payload['source']);previous_ref,previous=entry(machine,payload['previous_N'])
        frozen=json.loads((HERE/'PARENT_PLAN.json').read_text())
        variants=generate(source,frozen,previous['plan'])
        feature_rows=[features(source,previous['source'],previous['plan'],p)['combined'] for p in variants]
        prediction=runtime.execute('GEN3_TREE_PREDICT',dict(name=meta['native_model'],rows=[dict(id=str(i),features=f) for i,f in enumerate(feature_rows)],source_binding=meta['active_model_binding']))
        scores={int(row['id']):Fraction(row['probability']) for row in prediction['predictions']}
        admitted=[i for i,p in enumerate(variants) if p['selected']['width']<=22 and p['prime_product_sufficient']]
        selected=min(admitted or range(len(variants)),key=lambda i:(-scores[i],variants[i]['selected']['weighted_entries'],i))
        result=variants[selected];result['execution_admitted']=selected in admitted
        result['method_comparison']=[dict(method=p['training_method'],plan_sha256=p['mathematical_plan_sha256'],width=p['selected']['width'],branches=p['selected']['branches'],weighted_entries=p['selected']['weighted_entries'],learned_probability=str(scores[i])) for i,p in enumerate(variants)]
        oldverts=set(previous['source']['parent_vertices']);newverts=set(source['parent_vertices'])
        def edges(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v])))+(j,) for u,v,j in s['edges']}
        before=edges(previous['source']);after=edges(source);added=after-before;removed=before-after
        boundary=sorted({v for e in added|removed for v in e[:2] if v in oldverts})
        oldfields=dict(zip(previous['source']['parent_vertices'],previous['source']['fields']));newfields=dict(zip(source['parent_vertices'],source['fields']))
        changed_fields=sorted(v for v in oldverts&newverts if oldfields[v]!=newfields[v])
        boundary=sorted(set(boundary)|set(changed_fields))
        retained_vertices=set(previous['spectrum']['parent_port_vertices'])
        return dict(source=source,previous_ref=previous_ref,plan=result,added_edges=len(added),removed_edges=len(removed),
                    changed_field_vertices=changed_fields,previous_boundary_touched=boundary,
                    previous_spectrum_sufficient=oldverts<=newverts and set(boundary)<=retained_vertices,
                    model_prediction=prediction,model_role=meta['model_role'],
                    reuse=dict(index_recipe_catalog=str(HERE/'INDEX_RECIPES.json'),previous_parent_order=previous['plan']['parent_elimination_order']),
                    result_boundary='Execution plan only; no new spectrum computed')
    raise ValueError('Unknown spin catalog operation')
