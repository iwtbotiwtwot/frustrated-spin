"""Exact component factoring of the magnetization/correction generating function."""
import time,json,heapq,collections,hashlib,math
from flint import fmpz_poly
import baseline as b

def groups(plan):
    # A zero bridge is literally absent from the correction Hamiltonian.
    ranges=[];start=0
    for i,delta in enumerate(plan['bridges']):
        if delta==0:ranges.append((start,i+1));start=i+1
    if plan['bridges']:ranges.append((start,len(plan['pieces'])))
    else:ranges=[(i,i+1) for i in range(len(plan['pieces']))]
    assert [j for a,z in ranges for j in range(a,z)]==list(range(len(plan['pieces'])))
    assert all(a==0 or not plan['bridges'] or plan['bridges'][a-1]==0 for a,z in ranges)
    return ranges

def component(plan,a,z,tables,reverse):
    pieces=plan['pieces'][a:z];edges=plan['bridges'][a:z-1] if plan['bridges'] else []
    n=sum(p['n'] for p in pieces);bound=sum(p['bound'] for p in pieces)+sum(map(abs,edges))
    encoded=[b.encode(tables[p['table_key']],n,bound,'K_MAJOR' if reverse else 'T_MAJOR') for p in pieces]
    stride=1 if reverse else n+1;keep=len(plan['ports']) if a==0 else 0;keep_mask=(1<<keep)-1
    rows={}
    if not edges:
        for state,poly in encoded[0].items():rows[state&keep_mask]=rows.get(state&keep_mask,fmpz_poly())+poly
    elif reverse:
        message={-1:fmpz_poly([1]),1:fmpz_poly([1])}
        for i in range(len(pieces)-1,0,-1):
            delta=edges[i-1];local=encoded[i]
            message={left:sum(((local[(right+1)//2]*message[right]).left_shift((abs(delta)-delta*left*right)//2)
                for right in [-1,1]),fmpz_poly()) for left in [-1,1]}
        for state,poly in encoded[0].items():
            gate=1 if state&(1<<pieces[0]['gateway_index']) else -1
            key=state&keep_mask;rows[key]=rows.get(key,fmpz_poly())+poly*message[gate]
    else:
        state={}
        for mask,poly in encoded[0].items():
            gate=1 if mask&(1<<pieces[0]['gateway_index']) else -1
            key=(mask&keep_mask,gate);state[key]=state.get(key,fmpz_poly())+poly
        for i,piece in enumerate(pieces[1:],1):
            delta=edges[i-1];new={}
            for (ports,left),poly in state.items():
                for right in [-1,1]:
                    key=(ports,right);term=(poly*encoded[i][(right+1)//2]).left_shift(((abs(delta)-delta*left*right)//2)*stride)
                    new[key]=new.get(key,fmpz_poly())+term
            state=new
        for (ports,gate),poly in state.items():rows[ports]=rows.get(ports,fmpz_poly())+poly
    result={}
    for state,poly in rows.items():
        values={};marginal=collections.Counter()
        for index,value in enumerate(poly):
            if not value:continue
            if reverse:k,t=divmod(index,bound+1)
            else:t,k=divmod(index,n+1)
            values[(k,t)]=int(value);marginal[k]+=int(value)
        assert dict(marginal)=={k+state.bit_count():math.comb(n-keep,k) for k in range(n-keep+1)}
        result[state]=values
    return dict(n=n,bound=bound,rows=result)

def components(plan,tables,reverse):
    cache={};result=[]
    for a,z in groups(plan):
        key=b.digest(dict(pieces=[p['table_key'] for p in plan['pieces'][a:z]],
            bridges=plan['bridges'][a:z-1] if plan['bridges'] else [],retained_ports=len(plan['ports']) if a==0 else 0))
        if key not in cache:cache[key]=component(plan,a,z,tables,reverse)
        result.append((key,cache[key]))
    return result

def balanced(polys):
    queue=[(len(p),i,p) for i,p in enumerate(polys)];heapq.heapify(queue);counter=len(queue)
    if not queue:return fmpz_poly([1])
    while len(queue)>1:
        _,_,a=heapq.heappop(queue);_,_,c=heapq.heappop(queue);product=a*c
        heapq.heappush(queue,(len(product),counter,product));counter+=1
    return queue[0][2]

def global_spectra(plan,parts,orientation):
    """Materialize and decode one port row at a time; no 16-row polynomial cache."""
    n,bound=plan['N'],plan['correction_bound'];cache={};start=time.perf_counter()
    multiplicity=collections.Counter(key for key,c in parts[1:])
    by_key=dict(parts)
    for key in multiplicity:cache[key]=b.encode(by_key[key]['rows'],n,bound,orientation)[0]
    factors=[cache[key]**count for key,count in multiplicity.items()]
    scalar=balanced(factors);del factors,cache
    scalar_time=time.perf_counter()-start;dos={};joint_hash=hashlib.sha256();multiply_seconds=0;decode_seconds=0
    for state,coefficients in sorted(parts[0][1]['rows'].items()):
        t0=time.perf_counter();root=b.encode({state:coefficients},n,bound,orientation)[state];poly=root*scalar
        multiply_seconds+=time.perf_counter()-t0;del root
        t0=time.perf_counter();row={};marginal=collections.Counter();entries=[]
        for index,value in enumerate(poly):
            if not value:continue
            if orientation=='K_MAJOR':k,t=divmod(index,bound+1)
            else:t,k=divmod(index,n+1)
            assert 0<=k<=n and 0<=t<=bound and value>0
            count=int(value);ec=2*t-bound;m=2*k-n;energy=ec-plan['fill']*((m*m-n)//2)
            row[energy]=row.get(energy,0)+count;marginal[k]+=count;entries.append((k,ec,count))
        assert dict(marginal)=={k+state.bit_count():math.comb(n-len(plan['ports']),k) for k in range(n-len(plan['ports'])+1)}
        joint_hash.update(json.dumps([state,sorted(entries)],separators=(',',':')).encode());dos[state]=row
        del poly,entries;decode_seconds+=time.perf_counter()-t0
    return dos,joint_hash.hexdigest(),dict(scalar_power_product_seconds=scalar_time,port_row_multiply_seconds=multiply_seconds,decode_seconds=decode_seconds)

def solve(c,fill,source,cuda):
    start=time.perf_counter();plan=b.plan(c,fill)
    assert plan['N']<=600 and plan['maximum_degree']<=2100000,'PILOT_CAPACITY_GATE'
    t=time.perf_counter();gpu,cpu,local_times=b.local_tables(plan,cuda);local_seconds=time.perf_counter()-t
    t=time.perf_counter();primary=components(plan,gpu,True);reference=components(plan,cpu,False)
    assert primary==reference,'LOCAL_COMPONENT_REPLAY_MISMATCH';component_seconds=time.perf_counter()-t
    t=time.perf_counter();dos,joint,primary_stages=global_spectra(plan,primary,'K_MAJOR');primary_seconds=time.perf_counter()-t
    t=time.perf_counter();ref_dos,ref_joint,reference_stages=global_spectra(plan,reference,'T_MAJOR');reference_seconds=time.perf_counter()-t
    assert dos==ref_dos and joint==ref_joint,'GLOBAL_REPLAY_MISMATCH'
    t=time.perf_counter()
    if plan['N']<=18:assert dos==b.direct_dense(source,c['ports']),'DIRECT_ENUMERATION_MISMATCH'
    answer=b.exact.finalize_answer(source,c['ports'],dos);conditional=b.conditional_checks(source,c['ports'],dos)
    verification_seconds=time.perf_counter()-t
    return dict(status='EXACT_DENSE_VERIFIED',N=plan['N'],family=c['family'],fill_coupling=fill,answer=answer,
        joint_spectrum_hash=joint,reference_joint_spectrum_hash=ref_joint,plan_hash=b.digest(plan),plan=plan,
        backend_id='CUDA_LOCAL_INTEGER_TABLES_CPU_COMPONENT_POWERS_STREAMED_PORTS',
        reductions=dict(zero_correction_bridges=sum(x==0 for x in plan['bridges']),correction_components=len(primary),
            component_sizes=[x['n'] for key,x in primary],distinct_component_tables=len({key for key,x in primary}),
            port_polynomials_materialized_simultaneously=1,exact_reuse='Repeated component polynomials raised to their integer multiplicity'),
        verification=dict(local_GPU_CPU_equality=True,forward_reverse_component_equality=True,independent_global_encoding_equality=True,
            full_joint_hash_equality=True,full_conditional_density=True,direct_dense_enumeration=plan['N']<=18,**conditional),
        timing=dict(local_seconds=local_seconds,local_stages=local_times,component_seconds=component_seconds,
            primary_seconds=primary_seconds,reference_seconds=reference_seconds,primary_stages=primary_stages,reference_stages=reference_stages,
            verification_seconds=verification_seconds,total_solve_and_verification_seconds=time.perf_counter()-start))
