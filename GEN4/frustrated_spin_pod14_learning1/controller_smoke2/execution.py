"""Source-bound exact operations on the unmodified restored production engines."""
import os,sys,time,json,copy,pickle,math,importlib.util,subprocess,statistics
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P),str(P/'runtime'),'/opt/gen4/spin-focused1','/opt/gen4/spin-training1','/opt/gen4/spin-catalog1']
from source_ops import load,save,sha,digest,features,canonical,compare_answer,exact
from cpu_routes import component_reuse,conditioned,remaining_groups,normalize
from SAM_PROJECT.session import DomainSession
from run_fast import Focus
from arithmetic import templates,IndexCache
import fast_readout
import resource_manager as rm

def frontier_class():
    spec=importlib.util.spec_from_file_location('pod14_original_frontier','/opt/gen4/spin-n120-frontier1/run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def resource_snapshot():
    cpus=sorted(os.sched_getaffinity(0));r=rm.snapshot({'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.9,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}},'pod')
    cg=Path('/sys/fs/cgroup');r['cgroup_cpu']= (cg/'cpu.max').read_text().strip();r['cgroup_memory_max']=int((cg/'memory.max').read_text());r['cgroup_memory_current']=int((cg/'memory.current').read_text());r['memory_available']=min(r['prelaunch_mem_available'],r['cgroup_memory_max']-r['cgroup_memory_current'])
    import shutil
    r['disk_free']=shutil.disk_usage(P).free;r['processes']=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,rss,comm','--sort=-pcpu'],text=True).splitlines()[:25]
    r['admitted']=r['memory_available']>48*1024**3 and r['disk_free']>15*1024**3
    return r

def gpu_inventory():
    # CUDA interrogation is isolated so the parent can safely fork original owners.
    code="""import cupy as c,json
rows=[]
for d in range(c.cuda.runtime.getDeviceCount()):
 with c.cuda.Device(d):
  free,total=c.cuda.runtime.memGetInfo();p=c.cuda.runtime.getDeviceProperties(d)
  rows.append(dict(index=d,name=p['name'].decode(),free=free,total=total))
print(json.dumps(rows))"""
    rows=json.loads(subprocess.check_output([sys.executable,'-c',code],text=True,timeout=45))
    text=subprocess.check_output(['nvidia-smi','-L'],text=True)
    import re
    uuids=re.findall(r'MIG 1g\.24gb\s+Device\s+\d+: \(UUID: ([^)]+)\)',text)
    assert len(rows)==len(uuids)==14,(len(rows),len(uuids))
    assert all('RTX PRO 6000 Blackwell' in r['name'] and r['total']>23*1024**3 for r in rows)
    assert all(r['free']>8*1024**3 for r in rows),'GPU memory is occupied'
    return dict(devices=rows,mig_uuids=uuids,mig_profile='1g.24gb',nvidia_smi_L=text,count=14)

def runtime_identity():
    from CURRENT_REVISION import runtime
    verified=runtime.verify()
    import importlib.metadata as md
    packages={k:md.version(k) for k in ['numpy','cupy-cuda12x','python-flint']}
    files={}
    for folder in ['/opt/gen4/spin-focused1','/opt/gen4/spin-catalog1','/opt/gen4/spin-n120-frontier1','/opt/gen4/spin-training1']:
        for f in Path(folder).glob('*.py'):files[str(f)]=sha(f)
    for f in [P/'runtime/CURRENT_REVISION/REGISTRY.json',P/'runtime/SLC/18_SAM_NATIVE_QC/CURRENT_SLC_REVISION.json',P/'runtime/requirements.lock']:
        if f.exists():files[str(f.resolve())]=sha(f)
    identity=dict(binding_verification=verified,packages=packages,solver_runtime_hashes=files,python=sys.version)
    identity['runtime_package_hash']=digest(identity)
    identity['topology_id']=digest(dict(gpus=14,owners=14,shared_work_queue=True,experiment_slots=1,cpu_role='shared preparation/readout/verification; no independent CPU pool'))
    return identity

def plan_identity(p):
    return digest({k:p[k] for k in ['source_sha256','ports','glue','root_count','primes','local_bound']}|{'order':p['selected']['order'],'cutset':p['selected']['cutset'],'branches':p['selected']['branches'],'width':p['selected']['width'],'weighted_entries':p['selected']['weighted_entries'],**({'cpu_method':p['cpu_method']} if 'cpu_method' in p else {})})

def get_case(key):
    return load(P/'sources'/f'{key}.json')

def prepare_sources():
    (P/'sources').mkdir(exist_ok=True);manifest={};rows=[]
    for n in range(1,121):
        c=canonical(n);s=c['source'];f=features(s);key=f'N{n:03d}'
        record=dict(key=key,source=s,reference=c['spectrum'],features=f,plan=c['plan'],source_lineage=s.get('family'),canonical=True)
        if n==96:record['plan']=load(P/'N96_SPEC.json')['plan']
        save(P/'sources'/f'{key}.json',record);manifest[key]=sha(P/'canonical'/f'N{n:03d}.json');rows.append(dict(key=key,**f))
    for n in [100,105]:
        import gzip
        d=Path('/opt/gen4/spin-gap-97-119-1')/f'N{n}'
        s=load(d/'SOURCE.json');pl=load(d/'PLAN.json')
        # The full canonical gap reference is retained in the immutable source atlas.
        refpath=P/'inputs'/f'N{n}_RESULT1.json.gz'
        if not refpath.exists():refpath=Path('/opt/gen4-learning/GEN4/frustrated_spin_learning1/inputs/spin-gap-97-119-1')/f'N{n}'/'RESULT1.json.gz'
        r=json.load(gzip.open(refpath,'rt'))['answer'];f=features(s);key=f'N{n:03d}_prefix'
        save(P/'sources'/f'{key}.json',dict(key=key,source=s,reference=r,features=f,plan=pl,source_lineage=s['family'],canonical=False,inherited_variant=True));rows.append(dict(key=key,**f))
    save(P/'ATLAS_MANIFEST.json',dict(canonical_count=120,hashes=manifest,holdouts='SOURCE_UNDEFINED',imported_training_observations=0))
    save(P/'SOURCE_FEATURES.json',rows)
    save(P/'FEATURE_SCHEMA.json',dict(pre_execution=list(rows[0]),identity=['source_hash','graph_hash','source_lineage','ordered_ports_hash','plan_hash','method','backend_id','worker_topology_id','cache_state','timing_scope','root_batch','CRT_prime_count','branch_count','retained_width','weighted_entries','runtime_package_hash','readout_backend'],post_execution=['timings','exact_verification_hash','peak_memory','measured_work'],missing='null; never imputed as a measured zero',training='Only fresh fully bound warm observations; no historical timing, cold initialization, output coefficient or selected historical winner is a predictive input'))

def select_plans(c,alternate=False):
    s=c['source'];p=c['plan'];start=time.monotonic()
    if c['key']=='N096':
        ps=[load(P/'N96_SPEC.json')['plan']]
        if alternate:ps.append(load(P/'N96_OLD_PLAN.json'))
    elif all(k in p for k in ['selected','ports','glue','root_count','primes','mathematical_plan_sha256']):ps=[copy.deepcopy(p)]
    else:
        from vendor.spin_expanded import expanded
        frozen=load(P/'runtime/CURRENT_REVISION/engines/SLC/gen3/spin_data/PARENT_PLAN.json')
        candidates=expanded(s,frozen,canonical(min(96,max(1,s['N']-1)))['plan'])
        candidates=[p for p in candidates if p['selected']['width']<=22]
        ps=[min(candidates,key=lambda p:p['selected']['weighted_entries'])]
    if alternate and c['key']!='N096':
        from vendor.spin_methods import generate
        frozen=load(P/'runtime/CURRENT_REVISION/engines/SLC/gen3/spin_data/PARENT_PLAN.json')
        cs=generate(s,frozen,canonical(min(96,max(1,s['N']-1)))['plan'])
        cs=[p for p in cs if p['selected']['width']<=22 and p['selected']['branches']<=2048 and plan_identity(p)!=plan_identity(ps[0]) and p['selected']['weighted_entries']<=2*ps[0]['selected']['weighted_entries']]
        if cs:ps.append(min(cs,key=lambda p:p['selected']['weighted_entries']))
    for p in ps:
        assert p['source_sha256']==s['source_sha256']
        assert p['selected']['width']<=22 and p['selected']['branches']<=2048
        assert math.prod(p['primes'])>1<<s['N']
    return ps,time.monotonic()-start

def verify_answer(a,reference,s,p=None):
    start=time.monotonic();compare_answer(a,reference)
    assert int(a['configuration_count'])==1<<s['N']
    dos={int(e):int(c) for e,c in a['scalar_dos']};assert sum(dos.values())==1<<s['N']
    assert sum(e*c for e,c in dos.items())==0
    assert sum(e*e*c for e,c in dos.items())==(sum(h*h for h in s['fields'])+sum(j*j for _,_,j in s['edges']))*(1<<s['N'])
    if p is not None:assert all(a['checks'].values())
    check=dict(scalar=digest(a['scalar_dos']),configuration_count=a['configuration_count'],source_hash=s['source_sha256'],moments=True,closed_ports=True)
    if p is not None:
        assert a['source_sha256']==s['source_sha256']
        # Independently reconstruct expected open operator from exact closed rows and declared glue.
        if 'port_rows' in reference:
            lookup={tuple(row['state']):row['dos'] for row in reference['port_rows']}
            closed=[lookup[tuple(1 if mask>>i&1 else -1 for i in range(len(p['ports'])))] for mask in range(1<<len(p['ports']))]
        else:closed=reference['closed_port_rows']
        expected=[]
        for mask,row in enumerate(closed):
            spin={v:1 if mask>>i&1 else -1 for i,v in enumerate(p['ports'])};glue=-sum(j*spin[u]*spin[v] for u,v,j in p['glue']);rr=[]
            for e,count in (row['dos'] if isinstance(row,dict) else row):
                y=int(e)-glue+p['local_bound'];assert y%2==0;rr.append([y//2,str(count)])
            expected.append(rr)
        assert a['open_y_operator']==expected
        check.update(open_ports=digest(a['open_y_operator']),closed_port_hash=digest(a['closed_port_rows']),plan_hash=plan_identity(p))
    check['verification_hash']=digest(check);return check,time.monotonic()-start

class Cases:
    """Atomic local case files allow original forked owners to receive new cases."""
    def __init__(self,folder):self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.cached={}
    def add(self,case):
        ci=len(list(self.folder.glob('*.pickle')))+1;path=self.folder/f'{ci}.pickle'
        with path.with_suffix('.part').open('wb') as f:pickle.dump(case,f,protocol=5)
        path.with_suffix('.part').replace(path);self.cached={ci:case};return ci
    def __getitem__(self,ci):
        if ci not in self.cached:
            with (self.folder/f'{ci}.pickle').open('rb') as f:case=pickle.load(f)
            self.cached={ci:case}
        return self.cached[ci]

class Borrowed:
    def __init__(self,base):self.base=base
    def execute(self,*a,**k):return self.base.execute(*a,**k)
    def close(self):pass

class Production:
    def __init__(self,base,root):
        self.base=base;self.root=root;root.mkdir(parents=True,exist_ok=True);self.cases=Cases(root/'cases');self.cache=IndexCache();self.adapter=None;self.mode=None;self.last=None;self.identity=load(P/'RUNTIME_IDENTITY.json');self.active_out=None
    def close(self):
        if self.adapter:self.adapter.close();self.adapter=None
    def gpu(self,q,c):
        s=c['source'];plans,planning=select_plans(c,q.get('alternate',False));mode='branch' if max(p['selected']['branches'] for p in plans)>32 else 'focused'
        if mode!=self.mode:
            self.close();self.mode=mode;self.last=None
            if mode=='focused':self.adapter=Focus(Borrowed(self.base),self.root,self.cases,self.cache)
            else:
                self.adapter=frontier_class().Frontier(Borrowed(self.base),self.root,self.cases,self.cache,deadline=q['deadline']);self.adapter.durable=self.root/'residues';self.adapter.durable.mkdir(exist_ok=True)
        self.adapter.base=Borrowed(self.base)
        if mode=='branch':self.adapter.deadline=q['deadline']-15
        prep=time.monotonic();indices=[];mapbytes=[]
        for p in plans:
            cache=IndexCache();ts=templates(s,p);desc,maps,stats=cache.compile(ts[0]);indices.append(self.cases.add((s,p,ts,desc,maps,stats)));mapbytes.append(sum(v.nbytes for v in cache.values.values()))
        source_prep=time.monotonic()-prep;rows=[]
        # First pass measures source/plan loading; each plan then gets three steady warm repetitions.
        for rep in range(1+q.get('repeats',3)):
            for pi in (range(len(plans)) if rep%2==0 else reversed(range(len(plans)))):
                p=plans[pi];ci=indices[pi];identity=(s['source_sha256'],plan_identity(p));cold=not self.adapter.workers
                state='COLD' if cold else 'WARM_SAME_SOURCE' if self.last==identity else 'WARM_NEW_PLAN' if self.last and self.last[0]==identity[0] else 'WARM_NEW_SOURCE'
                # Fresh arithmetic on every repetition; partial residues are recovery evidence, never warm timing.
                for name in [f'RESIDUES{ci}.npz',f'PROFILES{ci}.json']:
                    f=self.root/name
                    if f.exists():f.rename(self.active_out/(f'plan{pi}_prior_rep{rep}_'+name))
                inv=[0.0];orig=fast_readout.batched_inverse_ntt
                def timed(*args,**kw):
                    t=time.monotonic();v=orig(*args,**kw);inv[0]+=time.monotonic()-t;return v
                fast_readout.batched_inverse_ntt=timed
                try:
                    if mode=='branch':r=self.adapter.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=ci,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256']));assert r['status']=='EXACT','PARTIAL_EXACT_TASKS_ONLY'
                    else:r=self.adapter.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=ci,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256'],repeat=rep))
                finally:fast_readout.batched_inverse_ntt=orig
                a=r['answer'];x=r['execution'];counts=x.get('roots_per_gpu',x.get('tasks_per_gpu'));assert len(counts)==14 and all(counts),'NOT_ALL_14_OWNERS_PARTICIPATED'
                artifact=self.root/(f'RESULT{ci}.json.gz' if mode=='branch' else f'case{ci:03d}_r{rep}.json.gz')
                if artifact.exists():artifact.replace(self.active_out/f'plan{pi}_repeat{rep}_EXACT.json.gz')
                assert len(self.adapter.workers)==14 and all(w.is_alive() for w in self.adapter.workers)
                verification,vt=verify_answer(a,c['reference'],s,p);self.last=identity
                readout=a['reconstruction_ns']/1e9
                stages=dict(structural_planning_seconds=planning,source_preparation_seconds=source_prep,worker_preparation_seconds=x['prepare_ns']/1e9,modular_gpu_seconds=x['arithmetic_ns']/1e9,readout_seconds=inv[0],crt_reconstruction_seconds=max(0,readout-inv[0]),verification_seconds=vt,end_to_end_solve_seconds=x['total_ns']/1e9,process_startup_seconds=0.0)
                row=observation(c,p,p.get('training_method',p['selected']['method']),'COOP14_MIG_BRANCH_GROUP',state,stages,self.identity,q,rep)
                row.update(map_bytes=mapbytes[pi],worker_pids=[w.pid for w in self.adapter.workers],participation=counts,exact_verification=verification,worker_preparation_kind='COLD_WORKER_INITIALIZATION' if cold else state,repeat=rep,warm_training_eligible=not cold and rep>0,measured_memory_bytes=max(b['pool_bytes'] for b in x['boot']),engine_mode=mode)
                rows.append(row);save(self.active_out/'PARTIAL_OBSERVATIONS.json',rows);save(P/'EXECUTOR_LIVE.json',dict(pid=os.getpid(),question_id=q['question_id'],worker_pids=row['worker_pids'],topology='COOP14_MIG_BRANCH_GROUP',last_verified_repeat=rep,updated=time.time()))
        return dict(status='EXACT',observations=rows,full_density_verified=True,plan_summaries=[{k:p['selected'][k] for k in ['method','width','branches','weighted_entries']} for p in plans])
    def cpu(self,q,c):
        s=c['source'];ps=c['reference'].get('retained_ports',c['reference'].get('ports',list(range(min(4,s['N'])))));f=c['features'];methods=q['methods'];cache={};rows=[]
        assert f['minfill_width']<=14,'CPU_WIDTH_CAPACITY'
        if any(m in methods for m in ['components','memo_components','warm_components']):assert f['max_component']<=18 and f['local_assignments']<=400000,'CPU_COMPONENT_CAPACITY'
        from vendor.spin_planning import structure
        start=time.monotonic();st=structure(s['N'],s['edges'],ps,[]);planning=time.monotonic()-start
        if 'conditional_components' in methods:
            # Match verifier capacity to this source before asking it to execute.
            candidates=[(max(map(len,remaining_groups(s,{v})),default=0),v) for v in range(s['N']) if v not in ps]
            assert candidates and min(candidates)[0]<=18,'CONDITIONAL_CAPACITY_REQUIRES_TARGETED_DIAGNOSIS'
        for rep in range(q.get('repeats',3)):
            for method in (methods if rep%2==0 else reversed(methods)):
                p=dict(source_sha256=s['source_sha256'],ports=ps,glue=[],root_count=0,primes=[],local_bound=f['energy_bound'],selected=dict(order=st['order'],cutset=[],branches=1,width=st['width'],weighted_entries=st['output_entries']),cpu_method=method)
                if method in ['components','memo_components','warm_components']:
                    p['selected'].update(order=[],width=f['max_component']-1,weighted_entries=f['local_assignments'])
                elif method=='conditional_components':
                    options=[]
                    for v in range(s['N']):
                        if v in ps:continue
                        gs=remaining_groups(s,{v});options.append((max(map(len,gs),default=0),sum(1<<len(g) for g in gs),v))
                    largest,work,v=min(options);p['selected'].update(order=[],cutset=[v],branches=2,width=largest-1,weighted_entries=2*work)
                start=time.monotonic()
                if method in ['components','variable_elimination']:
                    opts=dict(method=method,max_seconds=min(120,max(1,q['deadline']-time.time()-15)),max_component_size=18,max_assignments=400000,max_factor_work=4000000,max_intermediate_entries=65536)
                    if method=='variable_elimination':opts['elimination_order']=st['order']
                    r=exact.solve_cpu(s,ps,opts);a=r['answer'];meta=r['execution']
                elif method in ['memo_components','warm_components']:a,meta=component_reuse(s,ps,cache if method=='warm_components' else {})
                elif method=='conditional_components':a,meta=conditioned(s,ps)
                else:raise ValueError(method)
                elapsed=time.monotonic()-start;verification,vt=verify_answer(a,c['reference'],s)
                if rep==0:
                    import gzip
                    with gzip.open(self.active_out/f'{method}_EXACT.json.gz','wt') as out:json.dump(a,out)
                state='CACHE_REUSE' if method=='warm_components' and meta.get('cache_misses')==0 else 'WARM_SAME_SOURCE' if rep else 'WARM_NEW_SOURCE'
                stages=dict(structural_planning_seconds=planning,source_preparation_seconds=0.,worker_preparation_seconds=0.,modular_gpu_seconds=0.,readout_seconds=None,crt_reconstruction_seconds=0.,verification_seconds=vt,end_to_end_solve_seconds=elapsed,cpu_exact_seconds=elapsed,process_startup_seconds=0.)
                row=observation(c,p,method,'LOCAL_FLINT_CPU',state,stages,self.identity,q,rep)
                row.update(exact_verification=verification,warm_training_eligible=True,measured_work=meta.get('arithmetic_work_units'),cache_hits=meta.get('cache_hits',0),cache_misses=meta.get('cache_misses',0),timing_note='CPU exact route includes its native polynomial readout/count checks; independently timed external verification excluded; no subprocess startup',cpu_plan_kind='deterministic retained-port-aware elimination or explicit component enumeration',measured_memory_bytes=None)
                rows.append(row);save(self.active_out/'PARTIAL_OBSERVATIONS.json',rows)
        return dict(status='EXACT',observations=rows,full_density_verified=True)

def observation(c,p,method,backend,state,stages,identity,q,rep):
    f=c['features'];sel=p['selected'];gpu=backend=='COOP14_MIG_BRANCH_GROUP'
    return dict(question_id=q['question_id'],source_key=c['key'],source_hash=c['source']['source_sha256'],graph_hash=f['graph_hash'],source_lineage=c['source_lineage'],ordered_ports_hash=digest(p['ports']),ordered_ports=p['ports'],plan_hash=plan_identity(p),retained_plan_hash=p.get('mathematical_plan_sha256'),method=method,backend_id=backend,worker_topology_id=identity['topology_id'] if gpu else 'LOCAL_SINGLE_COORDINATOR_FLINT_CPU',cache_state=state,timing_scope='FRESH_EXACT_SOLVE_WITH_INTERNAL_CHECKS_EXCLUDES_EXTERNAL_VERIFICATION',root_batch=16 if gpu else 0,root_count=p['root_count'],CRT_prime_count=len(p['primes']),branch_count=sel['branches'],retained_width=sel['width'],weighted_entries=sel['weighted_entries'],estimated_factor_peak_entries=1<<max(0,sel['width']),runtime_package_hash=identity['runtime_package_hash'],readout_backend='NUMPY_BATCHED_INVERSE_NTT_INTEGER_CRT' if gpu else 'FLINT_EXACT_POLYNOMIAL',features=f,timings=stages,repeat=rep,cost_context='COMPLETE',status='OBSERVED_PATTERN')

class Adapter:
    def __init__(self,base,production):self.base=base;self.production=production
    def close(self):self.production.close();self.base.close()
    def execute(self,op,payload):
        if op!='GEN4_POD14_RESEARCH':return self.base.execute(op,payload)
        assert payload['code_sha256']==sha(__file__);q=payload['question'];c=get_case(q['source_key']);assert 1<=c['source']['N']<=120
        self.production.active_out=P/'experiments'/q['question_id'];self.production.active_out.mkdir(parents=True,exist_ok=True)
        if q['kind']=='gpu':return self.production.gpu(q,c)
        if q['kind']=='cpu':return self.production.cpu(q,c)
        if q['kind']=='diagnostic':
            f=c['features'];return dict(status='OBSERVED_PATTERN',finding='Use source-bound admitted verifier; no unconditional component fallback',features=f,admissible_cpu=f['minfill_width']<=14,component_admissible=f['max_component']<=18,one_targeted_followup=True)
        if q['kind']=='rule':return rule_probe(q,c)
        if q['kind']=='variant':return variant_probe(q,c)
        raise ValueError(q['kind'])

def rule_probe(q,c):
    s=c['source'];groups=exact.components(s);mapping={v:i for i,g in enumerate(groups) for v in g}
    assert sorted(mapping)==list(range(s['N'])) and all(mapping[u]==mapping[v] for u,v,j in s['edges'])
    supports=[];counterexamples=[]
    for n in range(1,121):
        cc=canonical(n);gg=exact.components(cc['source'])
        if len(gg)>1:supports.append(dict(N=n,source_hash=cc['source']['source_sha256']))
    # Adversarial control is an explicit cross-component interaction violating the old partition.
    if len(groups)>1:
        u,v=groups[0][0],groups[1][0];assert mapping[u]!=mapping[v];counterexamples.append(dict(source_hash=s['source_sha256'],added_edge=[u,v,1],result='OLD_PARTITION_PRECONDITION_VIOLATED'))
    return dict(status='EXACT_RULE_CANDIDATE',rule='SOURCE_BOUND_COMPONENT_PARTITION',source_hash=s['source_sha256'],precise_statement='If every interaction lies within one block of a disjoint partition, its exact port-conditioned generating function is the product of the block generating functions.',derivation='Disjoint spin assignments form a Cartesian product and energies add; distribute the finite sum over that product.',groups=groups,supporting_canonical_cases=supports,counterexample_search=counterexamples,beneficial=len(groups)>1,independent_verifier_required=True)

def variant_probe(q,c):
    s=copy.deepcopy(c['source']);ps=c['reference'].get('retained_ports',list(range(4)));mode=q.get('intervention','gauge')
    if mode=='gauge':
        signs=[1 if i in ps else (-1 if i%3 else 1) for i in range(s['N'])]
        s['fields']=[h*signs[i] for i,h in enumerate(s['fields'])];s['edges']=[[u,v,j*signs[u]*signs[v]] for u,v,j in s['edges']]
        # Independent inverse check before inheriting the exact reference target.
        assert [h*signs[i] for i,h in enumerate(s['fields'])]==c['source']['fields']
        assert [[u,v,j*signs[u]*signs[v]] for u,v,j in s['edges']]==c['source']['edges']
        s['family']='POD14_GAUGE_VARIANT';s.pop('source_sha256',None);s['source_sha256']=digest(s)
        key=q['source_key']+'_gauge';record=dict(key=key,source=s,reference=c['reference'],features=features(s),plan={},source_lineage=c['source_lineage']+' -> explicit gauge',canonical=False,certificate=dict(signs=signs,parent_hash=c['source']['source_sha256'],ports_fixed=ps))
        save(P/'sources'/f'{key}.json',record)
        return dict(status='EXACT_RULE_CANDIDATE',rule='EXPLICIT_GAUGE_BIJECTION',variant_key=key,certificate=record['certificate'],source_hash=s['source_sha256'],precise_statement='Explicit signs map every configuration energy and fix every retained port.',derivation='Each spin sign squares to one; each transformed field and pair interaction restores the original term.',supporting_canonical_cases=[dict(N=s['N'],source_hash=c['source']['source_sha256'])],counterexample_search='Non-unit sign rejected by inverse sign check; all coefficients checked',independent_verifier_required=True)
    raise ValueError(mode)
