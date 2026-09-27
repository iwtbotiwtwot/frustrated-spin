"""Shared packet compilation, joint exact spectra, and retained response readout.

Extends GEN3_SPIN_SELECT/SOURCE/SOLVE/READOUT; no domain-local runtime.
Counts use FLINT integers. A result's closure lives in the existing native Store.
"""
import base64
import collections
import gzip
import itertools
import json
import math
import time
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from flint import fmpz_poly
from . import spin_exact as x, retained

VERSION = 'SHARED_SPIN_JOINT_V1'
SCHEMA = 'SLC_JOINT_ENERGY_MAGNETIZATION_BOUNDARY_V1'
FAMILIES = ('packet', 'signed_packet', 'signed_packet_chain')
DATA = Path(__file__).parent/'spin_data'


def catalog():
    return json.loads((DATA/'JOINT_CATALOG.json').read_text())


def source_recipe(spec):
    retained.fields(spec, ('family', 'N'))
    n = x.integer(spec['N'], 'N'); family = spec['family']
    if family not in FAMILIES or not 1 <= n <= 1408:
        raise ValueError('Installed packet recipes cover the three named families, N1..1408')
    if n <= 120:
        return json.load(gzip.open(DATA/'PACKET_SOURCES_1_120.json.gz','rt'))[f'{family}_N{n:03d}']
    c = json.loads((DATA/f'{family}_N120.json').read_text())
    first = c['blocks'][0]; mp = {v:i for i,v in enumerate(first)}
    motif = [[mp[u],mp[v],j] for u,v,j in c['source']['edges'] if u in mp and v in mp]
    edges = c['source']['edges']
    for start in range(120,n,15):
        block = list(range(start,min(start+15,n))); previous=c['blocks'][-1]; i=len(c['blocks'])-1
        c['blocks'].append(block)
        edges.extend([[min(block[u],block[v]),max(block[u],block[v]),j] for u,v,j in motif if max(u,v)<len(block)])
        if family == 'signed_packet_chain':
            e=[previous[0],block[0],-1 if i%2 else 1];c['bridges'].append(e)
            edges.append([min(e[:2]),max(e[:2]),e[2]])
    c.update(N=n,key=f'{family}_N{n:06d}',canonical_replacement=False,
             claim_type='RECONSTRUCTED_COMPLETED_PACKET_SOURCE')
    c['source']=x.validate_source(dict(N=n,edges=edges,fields=[0]*n,parent_vertices=list(range(n)),
                                      family='PACKET_CONTINUATION1_'+family.upper()))
    return c


def inputs(payload):
    p=deepcopy(payload)
    if 'source_recipe' in p:
        if 'source' in p or 'decomposition' in p:
            raise ValueError('Choose a source recipe or an explicit source/decomposition')
        c=source_recipe(p.pop('source_recipe'));p['source']=c['source']
        p.setdefault('ports',c['ports']);p['decomposition']={k:c[k] for k in ('blocks','bridges')}
    source=x.validate_source(p['source']);ports=p.get('ports',list(range(min(4,source['N']))))
    x.check_ports(source,ports,{'max_port_states':256})
    return p,source,ports


def limits(options):
    defaults=dict(max_component_size=20,max_assignments=2000000,max_degree=6500000,
                  max_seconds=120,max_output_records=4000000,max_factor_work=10000000,
                  max_intermediate_entries=1000000,max_polynomial_bytes=2147483648)
    retained.fields(options, (), tuple(defaults))
    for k,v in options.items():
        if x.integer(v,k)<1:raise ValueError('Limits must be positive integers')
    return dict(defaults,**options)


def compile_plan(source,ports,decomposition,fill,lim):
    from .spin_joint_core.baseline import plan
    if decomposition is None:
        blocks=x.components(source)
        # The component method retains all requested ports in the first factor.
        roots=[b for b in blocks if set(b)&set(ports)]
        first=sorted(v for b in roots for v in b)
        blocks=([first] if first else [blocks[0]])+[b for b in blocks if b not in roots and (first or b!=blocks[0])]
        decomposition=dict(blocks=blocks,bridges=[])
    retained.fields(decomposition,('blocks','bridges'))
    c=dict(source=source,ports=ports,family=source['family'],**decomposition)
    try: pl=plan(c,fill)
    except (AssertionError,KeyError,IndexError,TypeError) as error:
        raise ValueError('Source decomposition is not an exact supported packet/chain partition: '+str(error)) from error
    unique={v['table_key']:v for v in pl['pieces']}
    work=sum(1<<v['n'] for v in unique.values())
    if max(v['n'] for v in unique.values())>lim['max_component_size'] or work>lim['max_assignments']:
        raise x.CapacityError('Component enumeration exceeds admitted work; use joint variable elimination or a finer exact decomposition')
    if pl['maximum_degree']>lim['max_degree']:
        raise x.CapacityError('Joint polynomial exceeds max_degree')
    # Conservative coefficient envelope for simultaneous primary/reference workspace.
    estimated=(pl['maximum_degree']+1)*(64+(source['N']+7)//8)*8
    if estimated>lim['max_polynomial_bytes']:
        raise x.CapacityError('Joint polynomial workspace exceeds max_polynomial_bytes')
    return c,pl,dict(local_assignments=work,unique_local_tables=len(unique),
                    estimated_polynomial_workspace_bytes=estimated)


def full_source(parent,fill):
    if fill is None:return parent
    weights={(u,v):j for u,v,j in parent['edges']}
    return x.validate_source(dict(N=parent['N'],fields=parent['fields'],parent_vertices=parent['parent_vertices'],
        family='UNIFORM_COMPLETION_'+parent['family'],parent_source_sha256=parent['source_sha256'],
        construction=dict(uniform_fill_coupling=fill,parent_interactions_preserved=True),
        edges=[[u,v,weights.get((u,v),fill)] for u in range(parent['N']) for v in range(u+1,parent['N'])]))


def select(payload):
    retained.fields(payload,(),('source','source_recipe','ports','decomposition','dense_fill','joint','backend','options','mode','result_ref','plan'))
    p,s,ports=inputs(payload);lim=limits(p.get('options',{}));fill=p.get('dense_fill')
    if fill is not None:x.integer(fill,'dense_fill')
    joint=p.get('joint',False) or fill is not None
    method='PACKET_POLYNOMIAL' if not joint and 'decomposition' in p else 'JOINT_COMPONENT_POWERS'
    if method=='PACKET_POLYNOMIAL':
        from .spin_packet import compile_source
        pl=compile_source(dict(source=s,ports=ports,family=s['family'],**p['decomposition']))
        binding=dict(source_sha256=s['source_sha256'],ports=ports,method=method,plan=pl)
        return dict(schema=VERSION,source=s,ports=ports,method=method,plan=pl,
            plan_sha256=x.digest(binding),binding=binding,execution_backend='cpu',joint=False,
            limits=lim,estimates=dict(local_packets=len(pl['pieces']),distinct_local_operators=len({v['key'] for v in pl['pieces']})),
            recomputed=False,arithmetic_calls=0)
    try:
        c,pl,est=compile_plan(s,ports,p.get('decomposition'),fill or 0,lim)
    except x.CapacityError:
        if 'decomposition' in p:raise
        if fill is not None:raise
        method='JOINT_VARIABLE_ELIMINATION';c=None;pl=dict(source_sha256=s['source_sha256'],ports=ports,
            maximum_degree=(s['energy_bound_B']+1)*(s['N']+1)-1)
        if pl['maximum_degree']>lim['max_degree']:raise x.CapacityError('Joint VE exceeds max_degree')
        est=dict(component_route_admitted=False)
    binding=dict(source_sha256=s['source_sha256'],ordered_ports=ports,dense_fill=fill,
                 decomposition=p.get('decomposition'),method=method,plan=pl)
    return dict(schema=VERSION,source=s,ports=ports,method=method,plan=pl,plan_sha256=x.digest(binding),
                binding=binding,estimates=est,execution_backend=p.get('backend','cpu'),
                joint=joint,limits=lim,recomputed=False,arithmetic_calls=0)


def ve_rows(source,ports,lim,orientation='K_MAJOR'):
    n=source['N'];bound=source['energy_bound_B'];stride=bound+1
    if (bound+1)*(n+1)-1>lim['max_degree']:raise x.CapacityError('Joint VE polynomial degree limit')
    opt=x.options_checked({k:lim[k] for k in ('max_seconds','max_factor_work','max_intermediate_entries')})
    opt['max_output_rows']=lim['max_output_records'];budget=x.Budget(opt)
    def mono(k,t):return fmpz_poly([1]).left_shift(k*stride+t if orientation=='K_MAJOR' else t*(n+1)+k)
    factors=[dict(scope=(v,),table=[mono(0,(abs(h)+h)//2),mono(1,(abs(h)-h)//2)]) for v,h in enumerate(source['fields'])]
    for u,v,j in source['edges']:
        factors.append(dict(scope=(u,v),table=[mono(0,(abs(j)-j)//2),mono(0,(abs(j)+j)//2),
                                              mono(0,(abs(j)+j)//2),mono(0,(abs(j)-j)//2)]))
    table,order=x._contract(factors,dict.fromkeys(range(n),2),ports,opt,budget,fmpz_poly(),fmpz_poly([1]))
    rows={}
    for state,poly in zip(itertools.product(range(2),repeat=len(ports)),table):
        mask=sum(bit<<i for i,bit in enumerate(state));row=[]
        for index,v in enumerate(poly):
            if v:
                k,t=divmod(index,stride) if orientation=='K_MAJOR' else tuple(reversed(divmod(index,n+1)))
                row.append((2*t-bound,2*k-n,int(v)))
        rows[mask]=sorted(row)
    return rows,dict(elimination_order=order,arithmetic_work=budget.work)


def exact_metadata(value):
    if isinstance(value,float):return {"float64_hex":value.hex()}
    if isinstance(value,dict):return {k:exact_metadata(v) for k,v in value.items()}
    if isinstance(value,list):return [exact_metadata(v) for v in value]
    return value


def keep(runtime,value,binding,dependencies=()):
    return retained.put(runtime.machine,'mathematical_result',value,binding,
                        dict(origin='SHARED_NATIVE_SPIN_JOINT',implementation=VERSION),dependencies)


def chunk(runtime,rows,source,ports,state):
    records=[[e,m,str(c)] for e,m,c in sorted(rows)]
    raw=json.dumps(records,separators=(',',':')).encode()
    value=dict(schema=SCHEMA+'_CHUNK',encoding='GZIP_BASE64_JSON_EM_COUNT',records=len(records),
               data=base64.b64encode(gzip.compress(raw,mtime=0)).decode())
    ref=keep(runtime,value,dict(source_sha256=source['source_sha256'],ordered_ports=ports,boundary_state=state))
    return dict(state=state,result_ref=ref,records=len(records),configurations=str(sum(c for e,m,c in rows)))


def unpack(machine,row,source_hash,ports):
    value=retained.get(machine,row['result_ref'],'mathematical_result',
        dict(source_sha256=source_hash,ordered_ports=ports,boundary_state=row['state']))['value']
    if value['schema']!=SCHEMA+'_CHUNK':raise ValueError('Expected a joint spectrum chunk')
    records=json.loads(gzip.decompress(base64.b64decode(value['data'],validate=True)))
    if len(records)!=row['records']:raise ValueError('Joint row count differs')
    seen=set();total=0
    for e,m,count in records:
        x.integer(e);x.integer(m);c=int(x.coefficient(count))
        if c<=0 or (e,m) in seen:raise ValueError('Joint records must be positive and unique')
        seen.add((e,m));total+=c;yield e,m,c
    if str(total)!=row['configurations']:raise ValueError('Joint configuration closure differs')


def verify_rows(source,ports,rows):
    n=source['N'];dos={}
    if set(rows)!=set(range(1<<len(ports))):raise ArithmeticError('Incomplete boundary table')
    for state,entries in rows.items():
        marginal=collections.Counter();hist=collections.Counter()
        for e,m,c in entries:
            if c<=0 or not -n<=m<=n or (m+n)%2:raise ArithmeticError('Invalid joint coefficient')
            marginal[(m+n)//2]+=c;hist[e]+=c
        expected={k+state.bit_count():math.comb(n-len(ports),k) for k in range(n-len(ports)+1)}
        if dict(marginal)!=expected:raise ArithmeticError('Joint magnetization/binomial closure differs')
        dos[state]=hist
    return x.finalize_answer(source,ports,dos)


def solve(runtime,payload):
    allowed=('source','source_recipe','ports','decomposition','dense_fill','joint','backend','options','mode','result_ref','plan')
    retained.fields(payload,(),allowed)
    p,parent,ports=inputs(payload);fill=p.get('dense_fill');joint=p.get('joint',False) or fill is not None
    if type(p.get('joint',False)) is not bool:raise ValueError('joint must be boolean')
    if fill is not None:x.integer(fill,'dense_fill')
    s=full_source(parent,fill)
    if p.get('mode','fresh')=='recover':
        old=x._get(runtime,p['result_ref'])
        if (old.get('operation')!='GEN3_SPIN_SOLVE' or old['answer']['source_sha256']!=s['source_sha256']
            or old['answer']['ports']!=ports or bool(old.get('joint'))!=joint):
            raise ValueError('Recovery source, ports or readout dimensions differ')
        return dict(old,result_ref=p['result_ref'],recomputed=False,arithmetic_calls=0)
    if p.get('mode','fresh')!='fresh' or 'result_ref' in p:raise ValueError('Fresh solve cannot use a result reference')
    start=time.perf_counter_ns();selected=select(p);lim=selected['limits'];planning=time.perf_counter_ns()-start
    if 'plan' in p and p['plan']!=selected['plan']:raise ValueError('Supplied source-bound plan differs')
    backend=p.get('backend','cpu')
    if backend not in ('auto','cpu','gpu'):raise ValueError('backend must be auto, cpu or gpu')
    # Auto prefers native CPU for small local tables; explicit GPU uses integer CUDA.
    backend='cpu' if backend=='auto' else backend
    rows=[];details={};local_time=0;reference_time=0;cache_hits=0
    if not joint:
        from .spin_packet import compile_source,packet_solve,collapse
        c=dict(source=parent,ports=ports,family=parent['family'],**p['decomposition'])
        pl=compile_source(c);cache=getattr(runtime,'_spin_packet_cache',{})
        runtime._spin_packet_cache=cache
        # Populate/verify exact local operators, then test boundary equality before contraction.
        t=time.perf_counter_ns();first=packet_solve(c,pl,cache);local_time=time.perf_counter_ns()-t
        r=collapse(c,pl,cache) if c['bridges'] else first
        if r['answer']!=first['answer']:raise ArithmeticError('Boundary specialization changed the full result')
        answer=r['answer'];details=r['execution'];cache_hits=details.get('cache_hits',0)
        backend_id='CPU_FLINT_PACKET_POLYNOMIAL'
    elif selected['method']=='JOINT_VARIABLE_ELIMINATION':
        if backend=='gpu':raise ValueError('Joint VE is a CPU backend; CUDA uses an exact component decomposition')
        t=time.perf_counter_ns();primary,details=ve_rows(parent,ports,lim);local_time=time.perf_counter_ns()-t
        t=time.perf_counter_ns();reference,_=ve_rows(parent,ports,lim,'T_MAJOR');reference_time=time.perf_counter_ns()-t
        if primary!=reference:raise ArithmeticError('Independent joint encodings differ')
        answer=verify_rows(s,ports,primary)
        if sum(map(len,primary.values()))>lim['max_output_records']:raise x.CapacityError('Joint output record limit')
        rows=[chunk(runtime,v,s,ports,k) for k,v in sorted(primary.items())]
        backend_id='CPU_FLINT_JOINT_VARIABLE_ELIMINATION'
    else:
        from .spin_joint_core import baseline as b,optimized as o
        pl=selected['plan'];primary={};reference={};cache=getattr(runtime,'_spin_joint_local_cache',{})
        runtime._spin_joint_local_cache=cache;cuda=None
        if backend=='gpu':
            from .spin_joint_core.cuda_tables import CUDA
            cuda=CUDA()
        t=time.perf_counter_ns()
        for piece in pl['pieces']:
            key=piece['table_key']
            if key in primary:continue
            cache_key=(backend,key)
            if cache_key in cache:g,r=cache[cache_key];cache_hits+=1
            else:
                r=b.cpu_local(piece)
                if cuda is not None:g,_=cuda.enumerate(piece['n'],piece['edges'],piece['fields'],piece['ports'])
                else:
                    local=x.validate_source(dict(N=piece['n'],edges=piece['edges'],fields=piece['fields'],
                        parent_vertices=list(range(piece['n'])),family='JOINT_LOCAL_CORRECTION'))
                    g0,_=ve_rows(local,piece['ports'],lim)
                    g={state:{((m+piece['n'])//2,(e+piece['bound'])//2):c for e,m,c in entries} for state,entries in g0.items()}
                if g!=r:raise ArithmeticError('Independent local joint tables differ')
                cache[cache_key]=(g,r)
            primary[key]=g;reference[key]=r
        if cuda is not None:cuda.close()
        local_time=time.perf_counter_ns()-t
        left=o.components(pl,primary,True);right=o.components(pl,reference,False)
        if left!=right:raise ArithmeticError('Forward/backward component results differ')
        record_count=0
        def sink(plan,state,entries):
            nonlocal record_count
            record_count+=len(entries)
            if record_count>lim['max_output_records']:raise x.CapacityError('Joint output record limit')
            vals=[(ec-plan['fill']*((2*k-plan['N'])**2-plan['N'])//2,2*k-plan['N'],c) for k,ec,c in entries]
            rows.append(chunk(runtime,vals,s,ports,state))
            if time.perf_counter_ns()-start>lim['max_seconds']*10**9:raise x.CapacityError('Joint execution deadline')
        dos,jhash,stages=o.global_spectra(pl,left,'K_MAJOR',sink)
        t=time.perf_counter_ns();ref_dos,ref_hash,ref_stages=o.global_spectra(pl,right,'T_MAJOR');reference_time=time.perf_counter_ns()-t
        if dos!=ref_dos or jhash!=ref_hash:raise ArithmeticError('Independent global joint encodings differ')
        answer=x.finalize_answer(s,ports,dos)
        details=dict(correction_components=len(left),distinct_components=len({key for key,c in left}),
            zero_correction_bridges=sum(v==0 for v in pl['bridges']),joint_hash=jhash,
            primary_stages_ns={k:int(v*10**9) for k,v in stages.items()},
            reference_stages_ns={k:int(v*10**9) for k,v in ref_stages.items()})
        backend_id='CUDA_LOCAL_INTEGER_CPU_FLINT_JOINT' if backend=='gpu' else 'CPU_FLINT_COMPONENT_JOINT'
    details=exact_metadata(details)
    value=dict(operation='GEN3_SPIN_SOLVE',status='EXACT',source=s,answer=answer,
        selection=selected,execution=dict(backend=backend_id,cache_hits=cache_hits,planning_ns=planning,
            local_preparation_and_checks_ns=local_time,reference_ns=reference_time,
            total_solve_ns=time.perf_counter_ns()-start,details=details,retained_complete_result_lookup=False))
    if joint:value['joint']=dict(schema=SCHEMA,N=s['N'],ports=ports,source_sha256=s['source_sha256'],rows=rows,
        verification=dict(full_density=True,count_first_second_moments=True,magnetization_binomials=True,independent_encoding=True))
    deps=[r['result_ref'] for r in rows]
    ref=keep(runtime,value,dict(capability=VERSION,source_sha256=s['source_sha256'],ordered_ports=ports,
                                plan_sha256=selected['plan_sha256']),deps)
    runtime.execute('GEN3_CHECKPOINT',{})
    return dict(value,result_ref=ref,recomputed=True)


def readout(runtime,payload):
    retained.fields(payload,('result_ref',),('uniform_field','boundary','collective_coupling','boundary_fields','magnetization','include_spectrum'))
    original=x._get(runtime,payload['result_ref']);j=original.get('joint')
    if not j or j['schema']!=SCHEMA:raise ValueError('Readout requires a retained joint energy/magnetization/boundary result')
    n=j['N'];ports=j['ports'];p=len(ports)
    def rat(v):return Fraction(str(x.rational(v)))
    h=rat(payload.get('uniform_field','0'));g=rat(payload.get('collective_coupling','0'))
    boundary=payload.get('boundary',[None]*p);fields=payload.get('boundary_fields',['0']*p)
    if not isinstance(boundary,list) or len(boundary)!=p or any(v is not None and (type(v) is not int or v not in (-1,1)) for v in boundary):
        raise ValueError('boundary lists +/-1 or null in retained port order')
    if not isinstance(fields,list) or len(fields)!=p:raise ValueError('boundary_fields must follow the ordered ports')
    fields=list(map(rat,fields));mag=payload.get('magnetization')
    if mag is not None and (type(mag) is not int or abs(mag)>n or (mag+n)%2):raise ValueError('Invalid total magnetization')
    include=payload.get('include_spectrum',False)
    if type(include) is not bool:raise ValueError('include_spectrum must be boolean')
    scale=math.lcm(h.denominator,g.denominator,*(f.denominator for f in fields))
    hi=int(h*scale);gi=int(g*scale);fi=[int(f*scale) for f in fields]
    count=first=second=msum=msq=em=0;ground=None;deg=0;ground_m=collections.Counter();minima={};density=collections.Counter()
    for row in j['rows']:
        state=[1 if row['state']&(1<<i) else -1 for i in range(p)]
        if any(v is not None and v!=state[i] for i,v in enumerate(boundary)):continue
        offset=-sum(a*b for a,b in zip(fi,state))
        for e,m,c in unpack(runtime.machine,row,j['source_sha256'],ports):
            if mag is not None and m!=mag:continue
            base=e*scale-gi*((m*m-n)//2)+offset;energy=base-hi*m
            count+=c;first+=energy*c;second+=energy*energy*c;msum+=m*c;msq+=m*m*c;em+=energy*m*c
            if ground is None or energy<ground:ground=energy;deg=c;ground_m=collections.Counter({m:c})
            elif energy==ground:deg+=c;ground_m[m]+=c
            if m not in minima or base<minima[m][0]:minima[m]=[base,c]
            elif base==minima[m][0]:minima[m][1]+=c
            if include:density[energy]+=c
    free=n-sum(v is not None for v in boundary);fixed=sum(v or 0 for v in boundary)
    plus=(mag-fixed+free)//2 if mag is not None else None
    expected=(math.comb(free,plus) if 0<=plus<=free else 0) if mag is not None else 1<<free
    if count!=expected:raise ArithmeticError('Conditioned joint count differs')
    hull=[]
    for m,(e,c) in sorted(minima.items()):
        while len(hull)>1:
            a,b=hull[-2:]
            if (b[1]-a[1])*(m-b[0])>=(e-b[1])*(b[0]-a[0]):hull.pop()
            else:break
        hull.append((m,e))
    crossings=[]
    for a,b in zip(hull,hull[1:]):
        slope=Fraction(b[1]-a[1],b[0]-a[0]);level=a[1]-slope*a[0]
        crossings.append(dict(field=str(slope/scale),coexisting_magnetizations=[dict(M=m,degeneracy=str(c))
            for m,(e,c) in sorted(minima.items()) if e-slope*m==level]))
    answer=dict(schema=SCHEMA+'_READOUT',source_sha256=j['source_sha256'],N=n,ports=ports,boundary=boundary,
        uniform_field=str(h),collective_coupling=str(g),boundary_fields=list(map(str,fields)),magnetization=mag,
        configuration_count=str(count),ground_energy=str(Fraction(ground,scale)) if ground is not None else None,
        ground_degeneracy=str(deg),ground_magnetization_counts={str(k):str(v) for k,v in sorted(ground_m.items())},
        energy_sum=str(Fraction(first,scale)),energy_square_sum=str(Fraction(second,scale*scale)),
        magnetization_sum=str(msum),magnetization_square_sum=str(msq),energy_magnetization_sum=str(Fraction(em,scale)),
        ground_state_crossing_fields=crossings,arithmetic='EXACT_INTEGER_COUNTS_RATIONAL_PARAMETERS',
        energy_transformation='E - h*M - g*(M*M-N)/2 - sum(boundary_field_i*s_port_i)',fresh_spin_enumeration=False)
    if include:answer['density']=[[str(Fraction(e,scale)),str(c)] for e,c in sorted(density.items())]
    if count:
        answer['energy_magnetization_covariance']=str(Fraction(em,scale*count)-Fraction(first*msum,scale*count*count))
        answer['magnetization_variance']=str(Fraction(msq,count)-Fraction(msum*msum,count*count))
    value=dict(operation='GEN3_SPIN_READOUT',answer=answer,input_result_ref=payload['result_ref'],spectrum_recomputed=False)
    ref=keep(runtime,value,dict(capability=VERSION,request_sha256=x.digest(payload)),[payload['result_ref']])
    runtime.execute('GEN3_CHECKPOINT',{})
    return dict(value,result_ref=ref,recomputed=True,spectrum_recomputed=False)


def source(runtime,payload):
    if 'source_recipe' in payload:
        retained.fields(payload,('source_recipe',))
        c=source_recipe(payload['source_recipe'])
        return dict(source=c['source'],ports=c['ports'],decomposition={k:c[k] for k in ('blocks','bridges')},
                    canonical_replacement=False,source_constructed=True,spectrum_computed=False,
                    source_lineage='PACKET_EXTENSION',arithmetic_calls=0)
    retained.fields(payload,('joint_key',))
    row=catalog()['retained_joint_results'].get(payload['joint_key'])
    if row is None:raise ValueError('No installed joint result with this key')
    value=retained.get(runtime.machine,row['result_ref'],'mathematical_result')['value']
    return dict(value,result_ref=row['result_ref'],recomputed=False,arithmetic_calls=0)
