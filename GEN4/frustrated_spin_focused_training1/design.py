"""Agent-designed focused training; deterministic topology splits and plan search."""
import hashlib,json,time,math
from copy import deepcopy
from pathlib import Path
from planning import ladder,plan,structure,digest
from methods import generate

FEATURES=['N','edges','width','log2_branches','log2_work','log2_kernel_work','log2_map_bytes','roots','prime_count','local_bound','log2_factor_work','previous_width','previous_log2_work','new_edges','touched_boundary']

def graph_family(parent,seed):
    if seed==0:return deepcopy(parent)
    result=deepcopy(parent);edge={(u,v):j for u,v,j in result['edges']};done=0;attempt=0;swaps=[]
    while done<6:
        pairs=sorted(edge);h=hashlib.sha256(f'SPIN-FOCUSED-TOPOLOGY-V1|{seed}|{attempt}'.encode()).digest();attempt+=1
        a,b=pairs[int.from_bytes(h[:4],'big')%len(pairs)];c,d=pairs[int.from_bytes(h[4:8],'big')%len(pairs)]
        if len({a,b,c,d})<4:continue
        # Preserve the two retained-port glue edges and all degrees.
        if (a,b) in [(0,1),(2,3)] or (c,d) in [(0,1),(2,3)]:continue
        x=tuple(sorted((a,d)));y=tuple(sorted((c,b)))
        if x in edge or y in edge or x in [(0,1),(2,3)] or y in [(0,1),(2,3)]:continue
        j,k=edge.pop((a,b)),edge.pop((c,d));edge[x]=j;edge[y]=k;swaps.append([[a,b],[c,d],list(x),list(y)]);done+=1
    result['edges']=[[*uv,j] for uv,j in sorted(edge.items())];result['family']=f'N96_SIX_DEGREE_PRESERVING_SWAPS_V1_SEED{seed}';result.pop('source_sha256',None);result['source_sha256']=digest(result)
    return result

def prefix(parent,n):
    result={k:deepcopy(parent[k]) for k in ['parent_instance_sha256','family']};result.update(N=n,fields=parent['fields'][:n],edges=[e for e in parent['edges'] if e[1]<n],parent_vertices=parent['parent_vertices'][:n]);result['energy_bound_B']=sum(map(abs,result['fields']))+sum(abs(e[2]) for e in result['edges']);result['source_sha256']=digest(result);return result

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

def integer_log(x):return round(math.log2(max(1,int(x)))*1024)
def features(source,previous,previous_plan,p,desc,cache):
    c=p['selected'];work=c['weighted_entries'];roots=p['root_count'];primes=len(p['primes']);keys={k for row in cache.keys for k in row};maps={k:v for ks,vs in zip(cache.keys,cache.maps) for k,v in zip(ks,vs)}
    factor_work=c['branches']*sum(st['output_count']*len(st['maps']) for st in desc['steps'])
    def edges(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v]))) for u,v,_ in s['edges']}
    new=edges(source)-edges(previous);old=set(previous['parent_vertices']);boundary={v for e in new for v in e if v in old}
    return [source['N'],len(source['edges']),c['width'],integer_log(c['branches']),integer_log(work),integer_log(work*roots*primes),integer_log(sum(maps[k].nbytes for k in keys)),roots,primes,p['local_bound'],integer_log(factor_work*roots*primes),previous_plan['selected']['width'],integer_log(previous_plan['selected']['weighted_entries']),len(new),len(boundary)]
