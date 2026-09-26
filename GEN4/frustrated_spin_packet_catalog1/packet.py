"""Source-bound packet polynomial compiler; additive research adapter only."""
import sys,json,hashlib,itertools,time,collections,heapq
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'runtime'))
from vendor import spin_exact as exact
from flint import fmpz_poly

def digest(x):return exact.digest(x)
def load(p):return json.loads(Path(p).read_text())
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.part');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(n,edges,fields,family):return exact.validate_source(dict(N=n,edges=sorted(edges),fields=fields,parent_vertices=list(range(n)),family=family))

def recover_grammar():
    a=load(P/'anchors/N100.json')['source'];b=load(P/'anchors/N105.json')['source']
    assert a['edges']==[e for e in b['edges'] if max(e[:2])<100] and a['fields']==b['fields'][:100]
    edges={tuple(e[:2]):e[2] for e in b['edges']};packets=[]
    for group in exact.components(b):
        cliques=[list(c) for c in itertools.combinations(group,5) if all(tuple(sorted(e)) in edges for e in itertools.combinations(c,2))]
        assert len(cliques)*5==len(group) and sorted(v for c in cliques for v in c)==group
        adj={i:[] for i in range(len(cliques))}
        for i in adj:
            for j in range(i):
                cross=[(u,v) for u in cliques[i] for v in cliques[j] if tuple(sorted((u,v))) in edges]
                if cross:
                    assert len(cross)==5 and len({u for u,v in cross})==len({v for u,v in cross})==5
                    adj[i].append(j);adj[j].append(i)
        assert max(map(len,adj.values()),default=0)<=2
        current=min((i for i in adj if len(adj[i])<=1),key=lambda i:cliques[i]);order=[];prev=None
        while current is not None:
            layer=sorted(cliques[current]) if not order else [next(v for v in cliques[current] if tuple(sorted((u,v))) in edges) for u in order[-1]]
            order.append(layer);nxt=[i for i in adj[current] if i!=prev];prev,current=current,nxt[0] if nxt else None
        assert len(order)==len(cliques);packets.append(order)
    master=[list(e) for e in b['edges']];n=105;extensions=[]
    for layers in packets:
        if len(layers)!=2:continue
        new=list(range(n,n+5));n+=5
        added=[[u,v,1] for u,v in itertools.combinations(new,2)]+[[u,v,1] for u,v in zip(layers[-1],new)]
        master.extend(added);extensions.append(dict(from_N=n-5,to_N=n,previous_layer=layers[-1],new_layer=new,added_edges=added));layers.append(new)
    assert n==120 and len(master)==320
    return dict(master_edges=sorted(master),packets=packets,extensions=extensions,anchor_hashes={str(n):sha(P/f'anchors/N{n}.json') for n in [100,105]},rule='K5 layers connected by a perfect matching; three layers per full packet; eight packets at N120')

def make_sources():
    grammar=recover_grammar();save(P/'GRAMMAR.json',grammar);records=[]
    for family in ['packet','signed_packet','signed_packet_chain']:
        for n in range(1,121):
            edges=[e.copy() for e in grammar['master_edges'] if max(e[:2])<n]
            if family!='packet':
                negatives={tuple(sorted(layer[:2])) for block in grammar['packets'] for layer in block}
                edges=[[u,v,-j if (u,v) in negatives else j] for u,v,j in edges]
            blocks=[[v for layer in block for v in layer if v<n] for block in grammar['packets']];blocks=[b for b in blocks if b]
            bridges=[]
            if family=='signed_packet_chain':
                bridges=[[a[0],b[0],-1 if i%2 else 1] for i,(a,b) in enumerate(zip(blocks,blocks[1:]))]
                edges.extend([[min(u,v),max(u,v),j] for u,v,j in bridges])
            source=norm(n,edges,[0]*n,'PACKET_EXTENSION1_'+family.upper())
            if family=='packet' and n in [100,105]:
                old=load(P/f'anchors/N{n}.json')['source'];assert old['edges']==source['edges'] and old['fields']==source['fields'];source=old
            ports=[v for v in [0,1,60,61] if v<n]
            emap={tuple(e[:2]):e[2] for e in source['edges']};witness=[]
            for block in grammar['packets']:
                for layer in block:
                    tri=layer[:3]
                    if max(tri)<n and all(tuple(sorted(e)) in emap for e in itertools.combinations(tri,2)):
                        prod=1
                        for e in itertools.combinations(tri,2):prod*=emap[tuple(sorted(e))]
                        if prod<0:witness.append(tri)
            key=f'{family}_N{n:03d}'
            c=dict(key=key,family=family,N=n,source=source,ports=ports,blocks=blocks,bridges=bridges,frustrated_triangles=witness,claim_type='INHERITED_ANCHOR' if family=='packet' and n in [100,105] else 'NEWLY_GENERATED',canonical_replacement=False)
            save(P/'sources'/f'{key}.json',c);records.append(dict(key=key,family=family,N=n,source_hash=source['source_sha256'],record_hash=digest(c),components=len(exact.components(source)),edges=len(source['edges']),largest_packet=max(map(len,blocks)),frustrated_triangles=len(witness)))
    save(P/'SOURCE_MANIFEST.json',records);return records

def compile_source(c):
    """Verify the full edge partition before permitting packet reduction."""
    s=c['source'];assert 1<=s['N']<=120
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

def compare(a,b):
    assert a['scalar_dos']==b['scalar_dos']
    if 'port_rows' in b:
        assert {tuple(r['state']):r['dos'] for r in a['port_rows']}=={tuple(r['state']):r['dos'] for r in b['port_rows']}
    else:
        assert [r['dos'] for r in a['port_rows']]==b['closed_port_rows']
    assert a['configuration_count']==b['configuration_count']
    return digest(dict(scalar=a['scalar_dos'],port_rows=a['port_rows'],count=a['configuration_count'],moments=a['energy_moments']))

class Adapter:
    def __init__(self,base):self.base=base;self.cache={}
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_PACKET_FRESH_SOLVE':
            assert payload['code_hash']==sha(__file__)
            c=load(P/'sources'/f"{payload['key']}.json");assert c['source']['source_sha256']==payload['source_hash']
            t=time.perf_counter();plan=compile_source(c);planning=time.perf_counter()-t
            t=time.perf_counter();r=packet_solve(c,plan,self.cache);elapsed=time.perf_counter()-t
            r.update(status='EXACT',fresh_global_calculation=True,solve_seconds=elapsed,planning_seconds=planning,plan_hash=digest(plan));return r
        if op!='GEN4_PACKET_CATALOG_SOLVE':return self.base.execute(op,payload)
        assert payload['code_hash']==sha(__file__)
        c=load(P/'sources'/f"{payload['key']}.json");assert payload['source_hash']==c['source']['source_sha256']
        start=time.perf_counter();plan=compile_source(c);planning=time.perf_counter()-start
        rows=[];reference=None;answers={}
        for method in ['variable_elimination','packet_cold','packet_warm']:
            for repeat in range(3):
                start=time.perf_counter()
                if method=='variable_elimination':r=exact.solve_cpu(c['source'],c['ports'],dict(method='variable_elimination',max_seconds=60))
                else:r=packet_solve(c,plan,{} if method=='packet_cold' else self.cache)
                elapsed=time.perf_counter()-start;a=r['answer'];verify_start=time.perf_counter()
                if reference is None:reference=a
                verification=compare(a,reference)
                if c['family']=='packet' and c['N'] in [100,105]:compare(a,load(P/f"anchors/N{c['N']}.json")['spectrum'])
                verification_seconds=time.perf_counter()-verify_start
                state='FRESH_CALCULATION' if method=='variable_elimination' else 'EMPTY_PACKET_CACHE' if method=='packet_cold' else 'CACHE_REUSE' if r['execution']['cache_misses']==0 else 'PARTIAL_OR_EMPTY_CACHE'
                rows.append(dict(method=method,repeat=repeat,seconds=elapsed,planning_seconds=planning,verification_seconds=verification_seconds,cache_state=state,verification_hash=verification,execution=r['execution']))
                if repeat==0:answers[method]=a
        # Open operator has no removed glue for this compiler; retain all coefficients explicitly.
        bound=c['source']['energy_bound_B'];open_rows=[[[ (int(e)+bound)//2,count] for e,count in r['dos']] for r in reference['port_rows']]
        return dict(status='EXACT',source_hash=c['source']['source_sha256'],plan_hash=digest(plan),ordered_ports=c['ports'],observations=rows,answers=answers,open_operator=dict(local_bound=bound,glue=[],ordered_ports=c['ports'],rows=open_rows),certificate=dict(partition=c['blocks'],bridges=c['bridges'],local_packet_keys=[p['key'] for p in plan['pieces']],source_bound_edge_partition=True,rule='Finite sum over disjoint packet assignments; exact polynomial multiplication for independent packets, sum over both boundary spins for every signed bridge'),full_density_verified=True)
