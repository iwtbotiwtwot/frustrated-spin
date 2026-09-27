"""Shared exact packet compiler and conditional-equality specialization."""
import time,collections,heapq
from flint import fmpz_poly
from . import spin_exact as exact
digest=exact.digest
def norm(n,edges,fields,family):
 return exact.validate_source(dict(N=n,edges=sorted(edges),fields=fields,parent_vertices=list(range(n)),family=family))
def compile_source(c):
    """Verify the full edge partition before permitting packet reduction."""
    s=c['source'];assert 1<=s['N']<=100000  # campaign engineering admission; no change to historical code
    blocks=c['blocks'];assert sorted(v for b in blocks for v in b)==list(range(s['N']))
    labels={v:i for i,b in enumerate(blocks) for v in b};cross=sorted([e for e in s['edges'] if labels[e[0]]!=labels[e[1]]])
    assert cross==sorted([[min(u,v),max(u,v),j] for u,v,j in c['bridges']]),'UNACCOUNTED_INTERPACKET_INTERACTION'
    assert all(v in blocks[0] for v in c['ports'])
    if c['bridges']:
        assert len(c['bridges'])==len(blocks)-1
        assert all([u,v]==[blocks[i][0],blocks[i+1][0]] for i,(u,v,j) in enumerate(c['bridges']))
    pieces=[]
    for i,b in enumerate(blocks):
        index={v:k for k,v in enumerate(b)};ports=[v for v in c['ports'] if v in index]
        if c['bridges'] and b[0] not in ports:ports.append(b[0])
        sub=norm(len(b),[[min(index[u],index[v]),max(index[u],index[v]),j] for u,v,j in s['edges'] if u in index and v in index],[s['fields'][v] for v in b],'EXACT_PACKET_LOCAL')
        localports=[index[v] for v in ports];key=digest(dict(edges=sub['edges'],fields=sub['fields'],ports=localports))
        pieces.append(dict(source=sub,ports=localports,global_ports=ports,key=key,vertices=b))
    return dict(source_hash=s['source_sha256'],ordered_ports_hash=digest(c['ports']),source_record_hash=digest(c),pieces=pieces,bridges=c['bridges'],bound=s['energy_bound_B'])

def balanced_product(polys):
    if not polys:return fmpz_poly([1])
    queue=[(len(x),i,x) for i,x in enumerate(polys)];heapq.heapify(queue);serial=len(queue)
    while len(queue)>1:
        _,_,a=heapq.heappop(queue);_,_,b=heapq.heappop(queue);x=a*b;heapq.heappush(queue,(len(x),serial,x));serial+=1
    return queue[0][2]

def packet_solve(c,plan,cache):
    assert plan['source_record_hash']==digest(c),'SOURCE_PLAN_BINDING_CHANGED'
    misses=hits=0;tables=[];prep=time.perf_counter()
    for piece in plan['pieces']:
        key=piece['key']
        if key not in cache:
            a=exact.solve_cpu(piece['source'],piece['ports'],dict(method='variable_elimination'))['answer'];bound=piece['source']['energy_bound_B'];table={}
            for row in a['port_rows']:
                coeff=[0]*(bound+1)
                for e,count in row['dos']:
                    assert (e+bound)%2==0;coeff[(e+bound)//2]=int(count)
                table[tuple(row['state'])]=fmpz_poly(coeff)
            cache[key]=table;misses+=1
        else:hits+=1
        tables.append(cache[key])
    populate=time.perf_counter()-prep;start=time.perf_counter();rows={}
    if not c['bridges']:
        # Repeated identical scalar packets become polynomial powers, then a balanced product.
        scalar=collections.Counter(piece['key'] for piece in plan['pieces'][1:])
        aggregate=balanced_product([cache[k][()]**count for k,count in scalar.items()])
        for state,poly in tables[0].items():rows[state]=poly*aggregate
    else:
        # Exact two-state boundary messages retain every interpacket interaction.
        message={-1:fmpz_poly([1]),1:fmpz_poly([1])}
        for i in range(len(tables)-1,0,-1):
            j=c['bridges'][i-1][2];next_message={}
            for left in [-1,1]:
                terms=[]
                for right in [-1,1]:
                    shift=(abs(j)-j*left*right)//2
                    terms.append((tables[i][(right,)]*message[right]).left_shift(shift))
                next_message[left]=terms[0]+terms[1]
            message=next_message
        for state,poly in tables[0].items():
            gateway=c['blocks'][0][0];local=plan['pieces'][0]['global_ports'];z=state[local.index(gateway)]
            rows[tuple(state[local.index(v)] for v in c['ports'])]=poly*message[z]
    compose=time.perf_counter()-start;start=time.perf_counter();hist={}
    for state,poly in rows.items():
        mask=sum(1<<i for i,z in enumerate(state) if z==1);hist[mask]={2*k-plan['bound']:int(v) for k,v in enumerate(poly) if v}
    answer=exact.finalize_answer(c['source'],c['ports'],hist)
    return dict(answer=answer,execution=dict(cache_hits=hits,cache_misses=misses,packet_population_seconds=populate,composition_seconds=compose,readout_and_checks_seconds=time.perf_counter()-start,local_packets=len(tables),distinct_packet_tables=len(set(p['key'] for p in plan['pieces'])),recomputed_global_spectrum=True,retained_complete_result_lookup=False))


def collapse(c,plan,cache):
    assert digest(c)==plan['source_record_hash']
    if not c['bridges']:return packet_solve(c,plan,cache)
    tables=[cache[p['key']] for p in plan['pieces']]
    if not all(t[(-1,)]==t[(1,)] for t in tables[1:]):
        r=packet_solve(c,plan,cache);r['execution']['reduction']='NOT_ADMITTED_BOUNDARY_SPECTRA_DIFFER';return r
    start=time.perf_counter();counts=collections.Counter(p['key'] for p in plan['pieces'][1:]);powers=[cache[key][(-1,)]**count for key,count in counts.items()]
    for magnitude,count in collections.Counter(abs(j) for u,v,j in c['bridges']).items():
        coeff=[0]*(magnitude+1);coeff[0]=coeff[-1]=1;powers.append(fmpz_poly(coeff)**count)
    common=balanced_product(powers);hist={}
    for state,poly in tables[0].items():
        result=poly*common;mask=sum(1<<i for i,z in enumerate(state) if z==1);hist[mask]={2*k-plan['bound']:int(v) for k,v in enumerate(result) if v}
    a=exact.finalize_answer(c['source'],c['ports'],hist)
    return dict(answer=a,execution=dict(reduction='EXACT_EQUAL_BOUNDARY_SPECTRA',conditional_tables_compared=len(tables)-1,bridge_factors=len(c['bridges']),seconds=time.perf_counter()-start,cache_hits=len(tables),cache_misses=0,recomputed_global_spectrum=True))

