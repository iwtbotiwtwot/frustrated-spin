"""Qualified expanded search:32tie orders with cutset-member removal."""
import hashlib,time
from copy import deepcopy
from .spin_planning import structure,digest
from .spin_methods import generate

def expanded(source,frozen,previous):
    started=time.perf_counter_ns();variants=generate(source,frozen,previous);base=deepcopy(variants[-1]);best=deepcopy(base['selected']);n=source['N'];edges=[e for e in source['edges'] if e not in base['glue']]
    inherited=[source['parent_vertices'].index(v) for v in frozen['cutset_sites_in_order'] if v in source['parent_vertices']]
    cuts=[[],inherited]+[inherited[:i]+inherited[i+1:] for i in range(len(inherited))]
    tested=0
    for seed in range(32):
        priority=sorted(range(n),key=lambda v:hashlib.sha256(f'SPIN-FOCUSED-PORTFOLIO1|{seed}|{source["parent_vertices"][v]}'.encode()).digest())
        for fixed in cuts:
            s=structure(n,edges,base['ports'],fixed,priority=priority);cost=s['output_entries']*(1<<len(fixed));tested+=1
            if s['width']<=22 and (best['width']>22 or cost<best['weighted_entries']):best=dict(**s,cutset=fixed,branches=1<<len(fixed),weighted_entries=cost)
    best.update(method='expanded_portfolio',portfolio_candidates=tested,planning_ns=time.perf_counter_ns()-started)
    base['selected']=best;base['training_method']='expanded_portfolio';base['parent_elimination_order']=[source['parent_vertices'][v] for v in best['order']];base['mathematical_plan_sha256']=digest(dict(source=source['source_sha256'],order=best['order'],cutset=best['cutset'],ports=base['ports'],glue=base['glue']));variants.append(base)
    return variants
