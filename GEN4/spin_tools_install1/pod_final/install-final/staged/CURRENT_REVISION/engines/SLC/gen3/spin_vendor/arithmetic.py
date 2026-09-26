"""Unchanged conditioning/index-cache definitions with installed-relative imports."""
import time
from types import SimpleNamespace
import numpy as np
from .util import digest
from .compat import exact

def templates(source, plan):
    fixed=plan['selected']['cutset'];ports=plan['ports'];n=source['N']
    sites=[i for i in range(n) if i not in fixed];remap={v:i for i,v in enumerate(sites)}
    out=[]
    for branch in range(1<<len(fixed)):
        assigned={v:1 if (branch>>i)&1 else -1 for i,v in enumerate(fixed)}
        fields=[source['fields'][v] for v in sites]
        constant=-sum(source['fields'][v]*s for v,s in assigned.items());edges=[]
        for u,v,j in source['edges']:
            if [u,v,j] in plan['glue']:continue
            if u in assigned and v in assigned:constant-=j*assigned[u]*assigned[v]
            elif u in assigned:fields[remap[v]]+=j*assigned[u]
            elif v in assigned:fields[remap[u]]+=j*assigned[v]
            else:edges.append([remap[u],remap[v],j])
        bound=sum(map(abs,fields))+sum(abs(e[2]) for e in edges)
        shift=plan['local_bound']+constant-bound
        assert shift>=0 and shift%2==0
        out.append(SimpleNamespace(local_instance=dict(N=len(sites),fields=fields,edges=edges,energy_bound_B=bound),
                   elimination_order=tuple(remap[v] for v in plan['selected']['order']),
                   port_order=tuple(remap[v] for v in ports),z_degree_shift=shift))
    return out

class IndexCache:
    def __init__(self):self.values={};self.recipes={}
    def acquire(self, width, positions):
        recipe=dict(width=width,positions=positions);key=digest(recipe)
        hit=key in self.values;t=time.perf_counter_ns()
        if not hit:
            rows=np.arange(1<<width,dtype=np.uint32);value=np.zeros(len(rows),dtype=np.uint32)
            for bit,position in enumerate(positions):
                if position>=0:value|=((rows>>position)&1)<<bit
            value.flags.writeable=False;self.values[key]=value;self.recipes[key]=recipe
        return key,self.values[key],hit,time.perf_counter_ns()-t
    def compile(self, template):
        fs=[tuple(f.scope) for f in exact._initial_factors(template.local_instance,np.array([1],dtype=np.int64),998244353)]
        initial=digest([list(s) for s in fs]);steps=[];maps=[];keys=[];hits=misses=avoided_bytes=0;t=time.perf_counter_ns()
        for vertex in template.elimination_order:
            selected=[s for s in fs if vertex in s];fs=[s for s in fs if vertex not in s]
            scope=tuple(sorted(set().union(*map(set,selected))-{vertex}))
            group=[];gkeys=[];records=[]
            for factor in selected:
                positions=[-1 if v==vertex else scope.index(v) for v in factor]
                key,value,hit,_=self.acquire(len(scope),positions)
                group.append(value);gkeys.append(key);hits+=hit;misses+=not hit
                if hit:avoided_bytes+=value.nbytes
                records.append(dict(factor_scope=list(factor),eliminated_factor_bit=1<<factor.index(vertex),recipe_sha256=key))
            steps.append(dict(vertex=vertex,output_scope=list(scope),output_count=1<<len(scope),maps=records))
            maps.append(group);keys.append(gkeys);fs.append(scope)
        assert all(set(s)<=set(template.port_order) for s in fs)
        desc=dict(initial_factor_scope_sha256=initial,steps=steps,port_order=list(template.port_order))
        return desc,SimpleNamespace(maps=maps,keys=keys),dict(hits=hits,misses=misses,avoided_map_bytes=avoided_bytes,compile_ns=time.perf_counter_ns()-t)
