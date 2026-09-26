"""General-size successor to the retained N96 cutset/NTT arithmetic.

Frozen modules supply exact initial factors, inverse NTT and CRT. This adapter
supplies arbitrary-N conditioning, a reusable index recipe cache and readout.
"""
import os
import sys
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from planning import digest

ROOT=Path(os.environ['GEN4_SPIN_SOURCE'])
sys.path.insert(0,str(ROOT/'SAM_REVIEW/campaigns/GEN3_POD_N96_H100X8_PREP1'))
import run as original
a=original.a
engine=a.n96_engine
exact=engine.retained_engine._modules()[1]

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

def cpu_values(ts,plan):
    """Exact retained CPU kernel for tiny graphs; same modular polynomial as GPU."""
    out=[]
    for prime in plan['primes']:
        points=engine.zeta_points(prime,plan['root_count'],0,plan['root_count'])
        total=np.zeros((1<<len(plan['ports']),len(points)),dtype=np.int64)
        for t in ts:
            fs=[(tuple(f.scope),f.values) for f in exact._initial_factors(t.local_instance,points,prime)]
            for vertex in t.elimination_order:
                selected=[f for f in fs if vertex in f[0]];fs=[f for f in fs if vertex not in f[0]]
                scope=tuple(sorted(set().union(*(set(s) for s,_ in selected))-{vertex}))
                assignments=np.arange(1<<len(scope),dtype=np.uint64)
                result=np.zeros((len(assignments),len(points)),dtype=np.int64)
                for bit in (0,1):
                    product=np.ones_like(result)
                    for factor,table in selected:
                        idx=np.zeros(len(assignments),dtype=np.uint64)
                        for i,v in enumerate(factor):
                            idx|=(np.full(len(idx),bit,dtype=np.uint64) if v==vertex else (assignments>>scope.index(v))&1)<<i
                        product=product*table[idx.astype(np.intp)]%prime
                    result=(result+product)%prime
                fs.append((scope,result))
            values=np.ones_like(total);assignments=np.arange(len(total),dtype=np.uint64)
            for scope,table in fs:
                idx=engine.retained_engine._project_indices(assignments,t.port_order,scope)
                values=values*table[idx]%prime
            shift=np.asarray([pow(int(x),t.z_degree_shift,prime) for x in points],dtype=np.int64)
            total=(total+values*shift[None,:])%prime
        out.append(total)
    return out

def reconstruct(source,plan,values):
    start=time.perf_counter_ns();primes=plan['primes'];length=plan['root_count'];ports=plan['ports']
    residues=[[engine.inverse_ntt(row,p) for row in vals.tolist()] for p,vals in zip(primes,values)]
    operator=[];conditional=[];total=Counter();b=plan['local_bound']
    for state in range(1<<len(ports)):
        coefficients=[engine.crt([r[state][k] for r in residues],primes) for k in range(length)]
        assert not any(coefficients[b+1:])
        coefficients=coefficients[:b+1];assert sum(coefficients)==1<<(source['N']-len(ports))
        operator.append([[k,str(c)] for k,c in enumerate(coefficients) if c])
        spin={v:1 if (state>>i)&1 else -1 for i,v in enumerate(ports)}
        glue=-sum(j*spin[u]*spin[v] for u,v,j in plan['glue'])
        row={2*k-b+glue:c for k,c in enumerate(coefficients) if c};total.update(row)
        conditional.append([[e,str(c)] for e,c in sorted(row.items())])
    count=sum(total.values());assert count==1<<source['N']
    assert sum(e*c for e,c in total.items())==0
    second=(sum(h*h for h in source['fields'])+sum(j*j for _,_,j in source['edges']))*count
    assert sum(e*e*c for e,c in total.items())==second
    answer=dict(source_sha256=source['source_sha256'],N=source['N'],energy_convention='E=-sum(J*s_u*s_v)-sum(h*s_u); spin bit 0=-1,1=+1',
                retained_ports=ports,parent_port_vertices=[source['parent_vertices'][v] for v in ports],
                removed_glue_edges=plan['glue'],local_energy_bound=b,open_y_operator=operator,
                closed_port_rows=conditional,scalar_dos=[[e,str(c)] for e,c in sorted(total.items())],
                configuration_count=str(count),ground_energy=min(total),ground_degeneracy=str(total[min(total)]),
                checks=dict(count=True,first_moment=True,second_moment=True,port_counts=True,polynomial_support=True))
    answer['spectrum_sha256']=digest(answer['scalar_dos']);answer['reconstruction_ns']=time.perf_counter_ns()-start
    return answer

def brute(source,ports):
    n=source['N'];b=source['energy_bound_B'];counts=np.zeros((1<<len(ports),2*b+1),dtype=np.int64)
    for start in range(0,1<<n,65536):
        masks=np.arange(start,min(start+65536,1<<n),dtype=np.uint32);energy=np.zeros(len(masks),dtype=np.int64);state=np.zeros(len(masks),dtype=np.int64)
        for u,v,j in source['edges']:energy+=(2*(((masks>>u)^(masks>>v))&1).astype(np.int64)-1)*j
        for v,h in enumerate(source['fields']):energy-=(2*((masks>>v)&1).astype(np.int64)-1)*h
        for i,v in enumerate(ports):state|=((masks>>v)&1).astype(np.int64)<<i
        counts+=np.bincount(state*(2*b+1)+energy+b,minlength=counts.size).reshape(counts.shape)
    return [[[i-b,str(int(c))] for i,c in enumerate(row) if c] for row in counts]
