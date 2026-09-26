"""Controlled planning-method portfolio on the same explicit catalog sources."""
import hashlib
import time
from copy import deepcopy
from .spin_planning import plan, structure, digest

METHODS=['fresh_min_fill','transition_priority','parent_plan','repair_transfer','tie_portfolio']

def generate(source,frozen,previous):
    base=plan(source,frozen,previous);n=source['N'];edges=[e for e in source['edges'] if e not in base['glue']]
    variants=[]
    for method in METHODS[:3]:
        candidates=[c for c in base['candidates'] if c['method']==method and c['width']<=22]
        chosen=min(candidates,key=lambda c:c['weighted_entries']) if candidates else base['selected']
        variants.append((method,deepcopy(chosen)))
    start=time.perf_counter_ns();best=deepcopy(variants[1][1]);evaluated=0
    for sweep in range(2):
        changed=False
        for i in range(max(0,len(best['order'])-1)):
            order=best['order'].copy();order[i],order[i+1]=order[i+1],order[i]
            s=structure(n,edges,base['ports'],best['cutset'],order=order);evaluated+=1
            if s['width']<=22 and s['output_entries']<best['output_entries']:
                best.update(s,weighted_entries=s['output_entries']*best['branches']);changed=True
        if not changed:break
    best.update(method='repair_transfer',planning_ns=time.perf_counter_ns()-start,repair_candidates=evaluated)
    variants.append(('repair_transfer',best))
    start=time.perf_counter_ns();best=deepcopy(base['selected']);tested=0
    cutsets=[[]]
    inherited=[source['parent_vertices'].index(v) for v in frozen['cutset_sites_in_order'] if v in source['parent_vertices']]
    if inherited:cutsets.append(inherited)
    for seed in range(6):
        priority=sorted(range(n),key=lambda v:hashlib.sha256(f'SPIN-TRANSITION-PORTFOLIO1|{seed}|{source["parent_vertices"][v]}'.encode()).digest())
        for fixed in cutsets:
            s=structure(n,edges,base['ports'],fixed,priority=priority);tested+=1
            cost=s['output_entries']*(1<<len(fixed))
            if s['width']<=22 and cost<best['weighted_entries']:
                best=dict(**s,cutset=fixed,branches=1<<len(fixed),weighted_entries=cost)
    best.update(method='tie_portfolio',planning_ns=time.perf_counter_ns()-start,portfolio_candidates=tested)
    variants.append(('tie_portfolio',best))
    out=[]
    for method,choice in variants:
        p=deepcopy(base);p['selected']=choice;p['parent_elimination_order']=[source['parent_vertices'][v] for v in choice['order']]
        p['training_method']=method
        p['mathematical_plan_sha256']=digest(dict(source=source['source_sha256'],order=choice['order'],cutset=choice['cutset'],ports=p['ports'],glue=p['glue']))
        out.append(p)
    return out

def features(source,previous,previous_plan,p):
    n=source['N'];oldn=previous['N'] if previous else 0
    oldverts=set(previous['parent_vertices']) if previous else set()
    def edgekeys(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v]))) for u,v,_ in s['edges']}
    newedges=edgekeys(source)-(edgekeys(previous) if previous else set())
    boundary={v for e in newedges for v in e if v in oldverts}
    c=p['selected'];old=previous_plan['selected'] if previous_plan else dict(width=0,branches=1,weighted_entries=0)
    structural=[n,len(source['edges']),c['width'],c['branches'],c['weighted_entries'],p['root_count'],len(p['primes'])]
    transition=[oldn,n-oldn,len(newedges),len(boundary),old['width'],old['branches'],c['width']-old['width'],c['branches'],c['weighted_entries'],old['weighted_entries']]
    return dict(structural=structural,transition=transition,combined=structural+transition)
