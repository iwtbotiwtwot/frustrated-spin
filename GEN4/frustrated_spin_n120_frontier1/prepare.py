"""Source-bound N120 degree-preserving extension and structural plan search.

Agent construction: preserve 228/240 parent couplings and all parent fields;
replace twelve disjoint old edges with 24 old/new links, and add a four-regular
24-site graph. No energy or numerical spectrum selects the source.
"""
import os,sys,json,hashlib,time,random,math
from pathlib import Path
sys.path.insert(0,'/opt/gen4/spin-focused1')
from planning import ladder,digest
from SAM_PROJECT.session import DomainSession

HERE=Path(__file__).resolve().parent
PRIMES=[998244353,1004535809,469762049,167772161,1224736769]
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def rank(tag,v):return hashlib.sha256(f'N120-FRONTIER1|{tag}|{v}'.encode()).digest()
def source():
    parent=ladder()[0][-1];edges={tuple(e[:2]):e[2] for e in parent['edges']};removed=[];used=set(range(4))
    protected={tuple(sorted((parent['parent_vertices'].index(a),parent['parent_vertices'].index(b)))) for a in [0,1,2] for b in [12,13,14]}
    for uv in sorted(edges,key=lambda uv:rank('old-edge',uv)):
        if uv in protected or used.intersection(uv):continue
        removed.append([*uv,edges.pop(uv)]);used.update(uv)
        if len(removed)==12:break
    assert len(removed)==12
    small={tuple(sorted((i,(i+d)%24))) for i in range(24) for d in [1,5]};rng=random.Random(12020260924);swaps=0
    while swaps<240:
        a,b=rng.choice(sorted(small));c,d=rng.choice(sorted(small))
        if rng.randrange(2):c,d=d,c
        x=tuple(sorted((a,d)));y=tuple(sorted((c,b)))
        if len({a,b,c,d})<4 or x in small or y in small:continue
        small.remove(tuple(sorted((a,b))));small.remove(tuple(sorted((c,d))));small.update([x,y]);swaps+=1
    weights=[-3,-2,-1,1,2,3]
    for u,v in sorted(small):edges[(u+96,v+96)]=weights[int.from_bytes(rank('new-weight',(u,v))[:4],'big')%6]
    new=list(range(96,120));new.sort(key=lambda v:rank('matching',v));stubs=[v for u,v,j in []]
    stubs=[v for e in removed for v in e[:2]]
    for old,newv in zip(stubs,new):edges[(old,newv)]=weights[int.from_bytes(rank('cross-weight',(old,newv))[:4],'big')%6]
    fields=parent['fields']+[int.from_bytes(rank('field',v)[:4],'big')%5-2 for v in range(96,120)]
    degree=[0]*120;adj=[set() for _ in range(120)]
    for u,v in edges:degree[u]+=1;degree[v]+=1;adj[u].add(v);adj[v].add(u)
    seen={0};todo=[0]
    while todo:
        for v in adj[todo.pop()]-seen:seen.add(v);todo.append(v)
    assert degree==[5]*120 and len(seen)==120 and len(edges)==300
    # Signed-cycle frustration witness, independent of fields or solver.
    signs={0:1};stack=[0];contradictions=[]
    while stack:
        u=stack.pop()
        for v in sorted(adj[u]):
            wanted=signs[u]*(1 if edges[tuple(sorted((u,v)))]>0 else -1)
            if v not in signs:signs[v]=wanted;stack.append(v)
            elif signs[v]!=wanted:contradictions.append([u,v])
    assert contradictions
    s=dict(N=120,fields=fields,edges=[[*uv,j] for uv,j in sorted(edges.items())],parent_vertices=parent['parent_vertices']+list(range(96,120)),parent_instance_sha256=parent['parent_instance_sha256'],parent_source_sha256=parent['source_sha256'],family='N120_FIVE_REGULAR_DEGREE_PRESERVING_N96_EXTENSION_V1',construction=dict(removed_parent_edges=removed,retained_parent_edges=228,new_internal_edges=48,new_cross_edges=24,new_graph_switches=240,agent_design=True),topology_checks=dict(five_regular=True,connected=True,frustrated_signed_cycles=True,frustration_conflicts=contradictions))
    s['energy_bound_B']=sum(map(abs,fields))+sum(abs(j) for j in edges.values());s['source_sha256']=digest(s);return s

def structural(s,ports,fixed,priority):
    n=s['N'];adj=[0]*n;mask=((1<<n)-1)^sum(1<<v for v in fixed)
    for u,v,j in s['edges']:
        if mask>>u&1 and mask>>v&1:adj[u]|=1<<v;adj[v]|=1<<u
    remain=mask^sum(1<<v for v in ports);order=[];width=work=0;peak=[];ranks={v:i for i,v in enumerate(priority)}
    def bits(a):
        while a:
            bit=a&-a;yield bit.bit_length()-1;a^=bit
    while remain:
        def score(v):
            ns=adj[v];degree=ns.bit_count();twice=sum((ns&~adj[w]).bit_count()-1 for w in bits(ns))
            return twice//2,degree,ranks[v],v
        v=min(bits(remain),key=score);ns=adj[v];w=ns.bit_count()
        if w>width:width=w;peak=list(bits(ns))
        work+=1<<w
        for u in bits(ns):adj[u]=(adj[u]|ns)&~((1<<u)|(1<<v))
        adj[v]=0;remain^=1<<v;order.append(v)
    return dict(order=order,width=width,output_entries=work,cutset=sorted(fixed),branches=1<<len(fixed),weighted_entries=work*(1<<len(fixed)),peak=peak)

def search(s,seconds):
    start=time.monotonic();ports=list(range(4));glue=[e for e in s['edges'] if e[:2] in [[0,1],[2,3]]];local=dict(s,edges=[e for e in s['edges'] if e not in glue]);bound=s['energy_bound_B']-sum(abs(e[2]) for e in glue);best=None;records=[];tested=0
    inherited=[s['parent_vertices'].index(v) for v in ladder()[1]['cutset_sites_in_order']]
    for seed in range(256):
        if time.monotonic()-start>seconds:break
        priority=sorted(range(120),key=lambda v:rank(f'plan-{seed}',v));fixed=[] if seed%2==0 else inherited[:]
        while len(fixed)<=12:
            c=structural(local,ports,fixed,priority);tested+=1
            if c['width']<=22:
                if best is None or c['weighted_entries']<best['weighted_entries']:
                    best=c;save(HERE/'BEST.json',dict(**best,seed=seed,elapsed_seconds=time.monotonic()-start));print(json.dumps(dict(status='BETTER_PLAN',seed=seed,width=c['width'],branches=c['branches'],weighted_entries=c['weighted_entries'],seconds=time.monotonic()-start)),flush=True)
                # One extra conditioning level may lower total work.
                if len(fixed)>=10:break
            candidates=[v for v in c['peak'] if v not in ports+fixed]
            if not candidates:break
            options=[]
            for v in candidates:
                nxt=structural(local,ports,fixed+[v],priority);tested+=1
                options.append(nxt)
            if not options:break
            choice=min(options,key=lambda x:(x['weighted_entries'],x['width'],x['cutset']))
            records.append(dict(seed=seed,cutset=c['cutset'],width=c['width'],weighted_entries=c['weighted_entries'],next_cutset=choice['cutset']))
            fixed=choice['cutset']
            if best and (1<<len(fixed))>max(1024,best['branches']*8):break
            if time.monotonic()-start>seconds:break
    save(HERE/'SEARCH.json',dict(tested=tested,records=records,elapsed_seconds=time.monotonic()-start))
    assert best is not None,'No width22 plan found in search budget'
    p=dict(N=120,source_sha256=s['source_sha256'],ports=ports,glue=glue,local_bound=bound,root_count=1<<bound.bit_length(),primes=PRIMES,selected=best,execution_admitted=True,prime_product_sufficient=math.prod(PRIMES)>1<<120,parent_elimination_order=[s['parent_vertices'][v] for v in best['order']],planning_ns=round((time.monotonic()-start)*1e9))
    p['mathematical_plan_sha256']=digest(dict(source=s['source_sha256'],order=best['order'],cutset=best['cutset'],ports=ports,glue=glue));return p

def primes_check():
    proofs=[]
    for p in PRIMES:
        assert all(p%d for d in range(2,math.isqrt(p)+1));q=p-1;factors=[];d=2
        while d*d<=q:
            if q%d==0:
                factors.append(d)
                while q%d==0:q//=d
            d+=1
        if q>1:factors.append(q)
        assert all(pow(3,(p-1)//d,p)!=1 for d in factors) and (p-1)%1024==0 and (p-1)**2+(p-1)<1<<63
        proofs.append(dict(prime=p,primitive_root=3,factors_p_minus_1=factors,prime_trial_division=True,int64_products_safe=True,root1024_exact_order=pow(pow(3,(p-1)//1024,p),512,p)!=1))
    assert math.prod(PRIMES)>1<<120
    return dict(proofs=proofs,product=str(math.prod(PRIMES)),count=str(1<<120),capacity=True)

class Prepare:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_N120_SOURCE':return source()
        if op=='GEN4_N120_PRIMES':return primes_check()
        if op=='GEN4_N120_PLAN':return search(payload['source'],payload['seconds'])
        return self.base.execute(op,payload)
if __name__=='__main__':
    with DomainSession.start('MATTER_SEARCH',objective='Construct and plan a fresh five-regular frustrated N120 extension for tonight, preserving N96 ancestry',output_root=HERE/'preparation_sessions',receipt_storage='gzip') as session:
        session.consumer=Prepare(session.consumer);print(session.manifest,session.directory,flush=True)
        s=session.execute('GEN4_N120_SOURCE',{},purpose='Freeze source before solver search; no spectrum-dependent selection');save(HERE/'SOURCE.json',s)
        save(HERE/'PRIMES.json',session.execute('GEN4_N120_PRIMES',{},purpose='Prove fifth-prime capacity, roots and exact integer arithmetic bounds'))
        p=session.execute('GEN4_N120_PLAN',dict(source=s,seconds=300),purpose='CPU structural search over cutsets and elimination orders; minimize work subject to qualified width22 memory envelope');save(HERE/'PLAN.json',p)
        save(HERE/'CHECKPOINT.json',session.execute('GEN3_CHECKPOINT',{},purpose='Retain source and plan preparation'));print('PREPARED',s['source_sha256'],p['selected'],flush=True)
