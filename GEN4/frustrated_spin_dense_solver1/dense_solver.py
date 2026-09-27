"""Exact uniform-completion DOS using a joint magnetization/correction polynomial."""
import os,sys,json,gzip,math,time,hashlib,collections,itertools
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,os.environ.get('GEN4_DENSE_RUNTIME','/opt/gen4-spin-continuation1/runtime'))
from vendor import spin_exact as exact
from flint import fmpz_poly
import numpy as np
import dense_format

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha(p):return dense_format.filehash(p)

def load_bound(manifest):
    path=Path(manifest);d=json.loads(path.read_text());family=d['key'].split('_N')[0]
    parent_path=path.parent/(family+'.parent.json.gz');c=json.load(gzip.open(parent_path,'rt'))
    raw=gzip.decompress((path.parent/d['couplings_file']).read_bytes())
    assert dense_format.sha(raw)==d['raw_couplings_sha256']
    fill=d['fill_coupling'];s=c['source']
    assert exact.validate_source(s)['source_sha256']==s['source_sha256']==d['parent_source_sha256']
    assert d['graph_sha256']==digest(dict(N=s['N'],fields=s['fields'],raw_couplings_sha256=d['raw_couplings_sha256']))
    dense_format.validate(raw,s['N'],s['edges'],fill)
    assert d['fields']==s['fields'] and d['parent_vertices']==s['parent_vertices']
    assert d['ordered_ports']==c['ports']
    source=exact.validate_source(dict(N=s['N'],edges=list(dense_format.iter_edges(s['N'],raw)),
        fields=s['fields'],parent_vertices=s['parent_vertices'],family='DENSE_SOLVER1_'+d['key']))
    return c,fill,source,dict(manifest=str(path),manifest_sha256=sha(path),parent_sha256=sha(parent_path),
        raw_couplings_sha256=d['raw_couplings_sha256'],graph_sha256=d['graph_sha256'],
        dense_source_sha256=source['source_sha256'],parent_source_sha256=s['source_sha256'],ordered_ports_hash=digest(c['ports']))

def plan(c,fill):
    s=c['source'];n=s['N'];blocks=c['blocks'];labels={v:i for i,b in enumerate(blocks) for v in b}
    assert sorted(v for b in blocks for v in b)==list(range(n)),'BAD_PARTITION'
    assert all(v in blocks[0] for v in c['ports']),'PORTS_OUTSIDE_FIRST_PACKET'
    seen=set()
    for u,v,j in s['edges']:
        assert 0<=u<v<n and (u,v) not in seen and j in (-1,1);seen.add((u,v))
    cross=sorted(e for e in s['edges'] if labels[e[0]]!=labels[e[1]])
    assert cross==sorted([min(u,v),max(u,v),j] for u,v,j in c['bridges']),'UNACCOUNTED_CROSS_EDGE'
    if c['bridges']:
        assert len(c['bridges'])==len(blocks)-1
        assert all([u,v]==[blocks[i][0],blocks[i+1][0]] for i,(u,v,j) in enumerate(c['bridges']))
    bridges=[j-fill for u,v,j in c['bridges']]
    pieces=[]
    for bi,b in enumerate(blocks):
        mp={v:i for i,v in enumerate(b)};ports=[v for v in c['ports'] if v in mp]
        if c['bridges'] and b[0] not in ports:ports.append(b[0])
        edges=[[mp[u],mp[v],j-fill] for u,v,j in s['edges'] if u in mp and v in mp and j!=fill]
        fields=[s['fields'][v] for v in b];bound=sum(abs(e[2]) for e in edges)+sum(map(abs,fields))
        piece=dict(n=len(b),edges=edges,fields=fields,ports=[mp[v] for v in ports],bound=bound,
            global_ports=ports,gateway_index=ports.index(b[0]) if c['bridges'] else None)
        piece['table_key']=digest({k:piece[k] for k in ['n','edges','fields','ports','bound']});pieces.append(piece)
    bound=sum(p['bound'] for p in pieces)+sum(map(abs,bridges))
    return dict(N=n,fill=fill,ports=c['ports'],pieces=pieces,bridges=bridges,correction_bound=bound,
        identity='E=2*t-B-J0*((2*k-N)^2-N)/2; polynomial encodes k=number of positive spins and t=(correction_energy+B)/2',
        maximum_degree=(n+1)*(bound+1)-1)

def cpu_local(p):
    """Independent Gray-code exact enumeration; GPU uses direct binary evaluation."""
    n=p['n'];adj=[[] for _ in range(n)]
    for u,v,j in p['edges']:adj[u].append((v,j));adj[v].append((u,j))
    spins=[-1]*n;energy=-sum(j for u,v,j in p['edges'])+sum(p['fields'])
    port_index={v:i for i,v in enumerate(p['ports'])};mask=0;k=0;rows={}
    for step in range(1<<n):
        assert (energy+p['bound'])%2==0
        key=(k,(energy+p['bound'])//2);r=rows.setdefault(mask,{})
        r[key]=r.get(key,0)+1
        if step+1==(1<<n):break
        flip=((step+1)&-(step+1)).bit_length()-1
        energy+=2*spins[flip]*(p['fields'][flip]+sum(j*spins[v] for v,j in adj[flip]))
        k-=spins[flip];spins[flip]*=-1
        if flip in port_index:mask^=1<<port_index[flip]
    return rows

def local_tables(plan,cuda):
    gpu={};cpu={};timings=[]
    for p in plan['pieces']:
        key=p['table_key']
        if key in gpu:continue
        g,tm=cuda.enumerate(p['n'],p['edges'],p['fields'],p['ports'])
        t=time.perf_counter();r=cpu_local(p);tm['cpu_independent_seconds']=time.perf_counter()-t
        assert g==r,'GPU_LOCAL_JOINT_TABLE_MISMATCH'
        assert sum(sum(row.values()) for row in g.values())==1<<p['n']
        gpu[key]=g;cpu[key]=r;timings.append(dict(table_key=key,**tm))
    return gpu,cpu,timings

def encode(rows,n,bound,orientation):
    out={}
    for state,row in rows.items():
        entries={(k*(bound+1)+t if orientation=='K_MAJOR' else t*(n+1)+k):v for (k,t),v in row.items()}
        coeff=[0]*(max(entries)+1)
        for index,count in entries.items():coeff[index]=count
        out[state]=fmpz_poly(coeff)
    return out

def primary_compose(pl,tables):
    """Backward gateway contraction; k-major no-carry Kronecker substitution."""
    n,b=pl['N'],pl['correction_bound'];pieces=pl['pieces']
    encoded={k:encode(v,n,b,'K_MAJOR') for k,v in tables.items()}
    if not pl['bridges']:
        multiplicities=collections.Counter(p['table_key'] for p in pieces[1:]);acc=fmpz_poly([1])
        for key,count in multiplicities.items():acc*=encoded[key][0]**count
        return {state:poly*acc for state,poly in encoded[pieces[0]['table_key']].items()}
    message={-1:fmpz_poly([1]),1:fmpz_poly([1])}
    for i in range(len(pieces)-1,0,-1):
        delta=pl['bridges'][i-1];local=encoded[pieces[i]['table_key']];new={}
        for left in [-1,1]:
            new[left]=sum(((local[(right+1)//2]*message[right]).left_shift((abs(delta)-delta*left*right)//2)
                for right in [-1,1]),fmpz_poly())
        message=new
    result={};piece=pieces[0]
    for state,poly in encoded[piece['table_key']].items():
        gateway=1 if state&(1<<piece['gateway_index']) else -1
        retained=state&((1<<len(pl['ports']))-1)
        result[retained]=result.get(retained,fmpz_poly())+poly*message[gateway]
    return result

def reference_compose(pl,tables):
    """Forward gateway contraction; t-major encoding independently prevents carries."""
    n,b=pl['N'],pl['correction_bound'];pieces=pl['pieces']
    encoded={k:encode(v,n,b,'T_MAJOR') for k,v in tables.items()}
    first=pieces[0];mask=(1<<len(pl['ports']))-1;state={}
    for row,poly in encoded[first['table_key']].items():
        gate=(1 if row&(1<<first['gateway_index']) else -1) if pl['bridges'] else 0
        key=(row&mask,gate);state[key]=state.get(key,fmpz_poly())+poly
    for i,piece in enumerate(pieces[1:],1):
        new={};local=encoded[piece['table_key']]
        if pl['bridges']:
            delta=pl['bridges'][i-1]
            for (ports,left),poly in state.items():
                for right in [-1,1]:
                    shift=((abs(delta)-delta*left*right)//2)*(n+1)
                    key=(ports,right);term=(poly*local[(right+1)//2]).left_shift(shift)
                    new[key]=new.get(key,fmpz_poly())+term
        else:
            new={key:poly*local[0] for key,poly in state.items()}
        state=new
    result={}
    for (ports,gate),poly in state.items():result[ports]=result.get(ports,fmpz_poly())+poly
    return result

def decode(pl,polys,orientation):
    n,b=pl['N'],pl['correction_bound'];dos={};joint={};joint_hash=hashlib.sha256()
    for state,poly in sorted(polys.items()):
        row={};marginal=collections.Counter();entries=[]
        for index,value in enumerate(poly):
            if not value:continue
            if orientation=='K_MAJOR':k,t=divmod(index,b+1)
            else:t,k=divmod(index,n+1)
            assert 0<=k<=n and 0<=t<=b and value>0
            count=int(value);ec=2*t-b;m=2*k-n;energy=ec-pl['fill']*((m*m-n)//2)
            row[energy]=row.get(energy,0)+count;marginal[k]+=count;entries.append((k,ec,count))
        fixed_plus=state.bit_count();free=n-len(pl['ports'])
        assert dict(marginal)=={k+fixed_plus:math.comb(free,k) for k in range(free+1)},'MAGNETIZATION_MARGINAL_FAILED'
        # Hash canonical joint rows, independent of the polynomial orientation.
        joint_hash.update(json.dumps([state,sorted(entries)],separators=(',',':')).encode())
        dos[state]=row
    return dos,joint_hash.hexdigest()

def conditional_checks(source,ports,dos):
    """All partial assignments of ordered ports: exact closure, count and two moments."""
    checked=0;records=[];n=source['N']
    for assignment in itertools.product((-1,0,1),repeat=len(ports)):
        fixed={v:s for v,s in zip(ports,assignment) if s};hist=collections.Counter()
        for mask,row in dos.items():
            if all(not s or (1 if mask&(1<<i) else -1)==s for i,s in enumerate(assignment)):hist.update(row)
        const=-sum(source['fields'][v]*s for v,s in fixed.items())
        linear={v:-h for v,h in enumerate(source['fields']) if v not in fixed};square=0
        for u,v,j in source['edges']:
            if u in fixed and v in fixed:const-=j*fixed[u]*fixed[v]
            elif u in fixed:linear[v]-=j*fixed[u]
            elif v in fixed:linear[u]-=j*fixed[v]
            else:square+=j*j
        total=1<<(n-len(fixed));expected=[total,total*const,total*(const*const+square+sum(x*x for x in linear.values()))]
        actual=[sum((e**k)*v for e,v in hist.items()) for k in range(3)]
        assert actual==expected,'CONDITIONAL_MOMENT_FAILED'
        records.append(dict(state=assignment,moments=list(map(str,actual)),spectrum_hash=digest(sorted(hist.items()))));checked+=1
    return dict(conditional_spectra_checked=checked,records=records)

def direct_dense(source,ports):
    """Independent exhaustive dense-edge enumeration, bounded to N<=18."""
    n=source['N'];assert n<=18;hist={s:collections.Counter() for s in range(1<<len(ports))}
    for start in range(0,1<<n,4096):
        ids=np.arange(start,min(start+4096,1<<n),dtype=np.uint32)
        spins=2*((ids[:,None]>>np.arange(n,dtype=np.uint32))&1).astype(np.int64)-1
        energies=-(spins@np.asarray(source['fields'],dtype=np.int64))
        for u,v,j in source['edges']:energies-=j*spins[:,u]*spins[:,v]
        masks=sum((((ids>>v)&1)<<i for i,v in enumerate(ports)),np.zeros(len(ids),dtype=np.uint32))
        for state in hist:
            vals,counts=np.unique(energies[masks==state],return_counts=True)
            hist[state].update({int(e):int(c) for e,c in zip(vals,counts)})
    return {s:dict(row) for s,row in hist.items()}

def solve(c,fill,source,cuda):
    start=time.perf_counter();pl=plan(c,fill);planning=time.perf_counter()-start
    assert pl['N']<=300 and pl['maximum_degree']<=600000,'BOUNDED_PILOT_CAPACITY_GATE'
    t=time.perf_counter();gpu,cpu,local_timing=local_tables(pl,cuda);local_seconds=time.perf_counter()-t
    t=time.perf_counter();primary=primary_compose(pl,gpu);composition=time.perf_counter()-t
    t=time.perf_counter();dos,joint=decode(pl,primary,'K_MAJOR');readout=time.perf_counter()-t
    del primary
    t=time.perf_counter();reference=reference_compose(pl,cpu);reference_composition=time.perf_counter()-t
    t=time.perf_counter();reference_dos,reference_joint=decode(pl,reference,'T_MAJOR');del reference
    assert joint==reference_joint and dos==reference_dos,'INDEPENDENT_GLOBAL_REPLAY_FAILED'
    reference_readout=time.perf_counter()-t
    direct_seconds=None
    if pl['N']<=18:
        t=time.perf_counter();assert dos==direct_dense(source,c['ports']),'DIRECT_DENSE_ENUMERATION_FAILED';direct_seconds=time.perf_counter()-t
    t=time.perf_counter();answer=exact.finalize_answer(source,c['ports'],dos)
    conditionals=conditional_checks(source,c['ports'],dos);verification=time.perf_counter()-t
    # Full ordered rows are the open boundary operator. Closing any subset is a sum of these rows.
    table_certificate=[dict(key=key,rows=[dict(state=state,coefficients=[[k,t,str(v)] for (k,t),v in sorted(row.items())])
        for state,row in sorted(rows.items())]) for key,rows in sorted(gpu.items())]
    return dict(status='EXACT_DENSE_VERIFIED',N=pl['N'],family=c['family'],fill_coupling=fill,
        backend_id='CUDA_INTEGER_LOCAL_TABLES_FLINT_EXACT_GLOBAL',plan=pl,plan_hash=digest(pl),answer=answer,
        local_table_certificate=table_certificate,joint_spectrum_hash=joint,reference_joint_spectrum_hash=reference_joint,
        verification=dict(gpu_cpu_local_tables_equal=True,independent_forward_reverse_global_replay_equal=True,
            direct_dense_enumeration=pl['N']<=18,magnetization_marginals_exact=True,full_density=True,
            ordered_ports=c['ports'],**conditionals),
        timing=dict(planning_seconds=planning,local_tables_and_verification_seconds=local_seconds,
            local_stages=local_timing,cpu_primary_composition_seconds=composition,primary_readout_seconds=readout,
            cpu_reference_composition_seconds=reference_composition,reference_readout_seconds=reference_readout,
            direct_dense_enumeration_seconds=direct_seconds,final_verification_seconds=verification,
            total_solve_and_verification_seconds=time.perf_counter()-start))
