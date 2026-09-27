"""Exact component factoring of the magnetization/correction generating function."""
import time,json,heapq,collections,hashlib,math
from flint import fmpz_poly
from . import baseline as b

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

def global_spectra(plan,parts,orientation,sink=None):
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
        if sink is not None:sink(plan,state,entries)
        del poly,entries;decode_seconds+=time.perf_counter()-t0
    return dos,joint_hash.hexdigest(),dict(scalar_power_product_seconds=scalar_time,port_row_multiply_seconds=multiply_seconds,decode_seconds=decode_seconds)

