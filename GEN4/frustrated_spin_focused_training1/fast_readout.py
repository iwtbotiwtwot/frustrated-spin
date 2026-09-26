"""Exact batched inverse NTT and precomputed CRT reconstruction successor.

NumPy int64 products remain below (1,004,535,809-1)^2 < 2^63; CRT uses
Python arbitrary-precision integers. Source checks match the retained readout.
"""
import time
from functools import lru_cache
from collections import Counter
import numpy as np
from planning import digest

@lru_cache(maxsize=64)
def factors(length,prime):
    if length<1 or length&(length-1) or (prime-1)%length:raise ValueError('Invalid NTT length')
    bits=length.bit_length()-1
    indices=np.arange(length,dtype=np.int64);rev=np.zeros(length,dtype=np.int64)
    for bit in range(bits):rev|=((indices>>bit)&1)<<(bits-1-bit)
    stages=[];block=2
    while block<=length:
        root=pow(pow(3,(prime-1)//block,prime),prime-2,prime);twiddle=np.array([pow(root,k,prime) for k in range(block//2)],dtype=np.int64);stages.append((block,twiddle));block*=2
    return rev,stages,pow(length,prime-2,prime)

def batched_inverse_ntt(values,prime):
    a=np.asarray(values,dtype=np.int64);rev,stages,inv=factors(a.shape[1],prime);a=(a[:,rev]%prime).copy()
    for block,twiddle in stages:
        view=a.reshape(a.shape[0],-1,block);half=block//2;even=view[:,:,:half].copy();odd=(view[:,:,half:]*twiddle)%prime
        view[:,:,:half]=(even+odd)%prime;view[:,:,half:]=(even-odd)%prime
    return (a*inv)%prime

def reconstruct(source,plan,values):
    start=time.perf_counter_ns();primes=plan['primes'];length=plan['root_count'];ports=plan['ports']
    residues=[batched_inverse_ntt(vals,p).tolist() for p,vals in zip(primes,values)]
    modulus=1
    for prime in primes:modulus*=prime
    weights=[(modulus//prime)*pow(modulus//prime,-1,prime) for prime in primes]
    operator=[];conditional=[];total=Counter();b=plan['local_bound']
    for state in range(1<<len(ports)):
        coefficients=[sum(r[state][k]*w for r,w in zip(residues,weights))%modulus for k in range(length)]
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
