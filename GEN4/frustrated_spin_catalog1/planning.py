"""Source-explicit nested spin ladder and measured transition planning.

Agent implementation: inherited N96 graph, induced vertex prefixes. Vertex labels
remain the parent's labels in every transition; no claim of five-regularity for
proper induced subgraphs. Energy is -sum J*s_u*s_v - sum h*s_u.
"""
import hashlib
import json
import time
from pathlib import Path

SIZES = [2, 8, 12, 18, 24, 36, 48, 60, 72, 84, 96]
HERE = Path(__file__).resolve().parent

def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def ladder():
    parent = json.loads((HERE/'parent.json').read_text())
    frozen = json.loads((HERE/'parent_plan.json').read_text())
    seed = [6, 55, 11, 78, 0, 12, 1, 13, 2, 14, 5, 17]
    vertices = seed + [v for v in range(96) if v not in seed]
    rows = []
    for n in SIZES:
        selected = vertices[:n]
        lookup = {v:i for i,v in enumerate(selected)}
        edges = sorted([*sorted([lookup[u],lookup[v]]),j] for u,v,j in parent['edges'] if u in lookup and v in lookup)
        fields = [parent['fields'][v] for v in selected]
        source = dict(N=n, fields=fields, edges=edges,
                      energy_bound_B=sum(map(abs,fields))+sum(abs(e[2]) for e in edges),
                      parent_vertices=selected, parent_instance_sha256=parent['instance_sha256'],
                      family='N96_INDUCED_TRANSITION_LADDER_V1')
        source['source_sha256'] = digest(source)
        rows.append(source)
    return rows, frozen

def structure(n, edges, ports, fixed, order=None, priority=None):
    adj = {v:set() for v in range(n) if v not in fixed}
    for u,v,_ in edges:
        if u in adj and v in adj: adj[u].add(v); adj[v].add(u)
    remaining = set(adj)-set(ports)
    out=[]; width=0; work=0
    rank = {v:i for i,v in enumerate(priority or [])}
    while remaining:
        if order is not None: v=order[len(out)]
        else:
            def score(v):
                ns=adj[v]; missing=sum(len(ns-adj[w]-{w}) for w in ns)//2
                return missing,len(ns),rank.get(v,n+v),v
            v=min(remaining,key=score)
        ns=adj[v]; width=max(width,len(ns)); work+=1<<len(ns)
        for w in ns:adj[w].update(ns-{w});adj[w].discard(v)
        del adj[v];remaining.remove(v);out.append(v)
    return dict(order=out,width=width,output_entries=work)

def plan(source, frozen, previous=None):
    started=time.perf_counter_ns();n=source['N'];verts=source['parent_vertices'];lookup={v:i for i,v in enumerate(verts)}
    ports=list(range(min(n,4)))
    cuts=[lookup[v] for v in frozen['cutset_sites_in_order'] if v in lookup]
    glue=[e for e in source['edges'] if e[:2] in ([0,1],[2,3])]
    edges=[e for e in source['edges'] if e not in glue]
    inherited=[lookup[v] for v in frozen['selected_order'] if v in lookup and lookup[v] not in cuts+ports]
    prior_order=[] if previous is None else [lookup[v] for v in previous['parent_elimination_order'] if v in lookup]
    candidates=[]
    for fixed in [[], cuts] if cuts else [[]]:
        for method in ['fresh_min_fill','transition_priority','parent_plan']:
            if method=='transition_priority' and previous is None:continue
            if method=='parent_plan' and fixed!=cuts:continue
            t=time.perf_counter_ns()
            order=inherited if method=='parent_plan' else None
            s=structure(n,edges,ports,fixed,order=order,priority=prior_order if method=='transition_priority' else None)
            candidates.append(dict(method=method,cutset=fixed,branches=1<<len(fixed),**s,
                                   weighted_entries=s['output_entries']*(1<<len(fixed)),planning_ns=time.perf_counter_ns()-t))
    best=min(candidates,key=lambda c:(c['weighted_entries'],c['width'],c['branches'],c['method']))
    # A bounded GPU memory policy selects among computed exact plans, not sources.
    admitted=[c for c in candidates if c['width']<=22]
    if admitted:best=min(admitted,key=lambda c:(c['weighted_entries'],c['width'],c['branches'],c['method']))
    assert best['width']<=22
    bound=source['energy_bound_B']-sum(abs(e[2]) for e in glue)
    length=1<<max(0,bound.bit_length())
    primes=[];product=1
    for p in [998244353,1004535809,469762049,167772161]:
        primes.append(p);product*=p
        if product>(1<<n):break
    assert product>(1<<n)
    return dict(N=n,source_sha256=source['source_sha256'],ports=ports,glue=glue,
                local_bound=bound,root_count=length,primes=primes,selected=best,candidates=candidates,
                parent_elimination_order=[verts[v] for v in best['order']],
                planning_ns=time.perf_counter_ns()-started)

if __name__=='__main__':
    sources,frozen=ladder();previous=None
    for source in sources:
        p=plan(source,frozen,previous);previous=p
        print(json.dumps({k:p[k] for k in ['N','root_count','selected','planning_ns']}))
