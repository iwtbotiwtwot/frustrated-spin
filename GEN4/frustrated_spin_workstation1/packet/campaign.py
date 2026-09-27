"""Consecutive source-bound exact packet-family calculations, with bounded resources."""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
import argparse, copy, csv, datetime, fcntl, gzip, json, math, multiprocessing
import resource, shutil, signal, statistics, sys, time, traceback
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from packet import *
from refine import collapse
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION import runtime
from gen4 import resources

sys.set_int_max_str_digits(0)
FAMILIES=('packet','signed_packet','signed_packet_chain')
STOP=False
SESSION=None
CACHE={}
CONFIG={}

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def stop_signal(*_):
    global STOP
    STOP=True
def atomic(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.part')
    with tmp.open('w') as f:
        json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)
def append(path,obj):
    with Path(path).open('a') as f:
        f.write(json.dumps(obj,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def write_gz(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.part')
    with tmp.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as z:
            z.write(json.dumps(obj,separators=(',',':')).encode())
        raw.flush();os.fsync(raw.fileno())
    tmp.replace(path)

def source(family,n):
    old=load(P/'inputs'/f'{family}_N120.json')
    if n==120:return old
    assert 121<=n<=100000
    c=copy.deepcopy(old);first=c['blocks'][0];mp={v:i for i,v in enumerate(first)}
    motif=[[mp[u],mp[v],j] for u,v,j in c['source']['edges'] if u in mp and v in mp]
    edges=c['source']['edges']
    for start in range(120,n,15):
        block=list(range(start,min(start+15,n)));previous=c['blocks'][-1];i=len(c['blocks'])-1
        c['blocks'].append(block)
        edges.extend([[min(block[u],block[v]),max(block[u],block[v]),j] for u,v,j in motif if max(u,v)<len(block)])
        if family=='signed_packet_chain':
            e=[previous[0],block[0],-1 if i%2 else 1];c['bridges'].append(e);edges.append([min(e[:2]),max(e[:2]),e[2]])
    c.update(N=n,key=f'{family}_N{n:06d}',claim_type='RETROSPECTIVE_GRAPH_REPLAY' if n==300 else 'NEWLY_GENERATED_SOURCE',canonical_replacement=False)
    c['source']=norm(n,edges,[0]*n,'PACKET_CONTINUATION1_'+family.upper())
    assert [e for e in c['source']['edges'] if max(e[:2])<120]==old['source']['edges']
    # Recover complete signed-triangle witnesses for each actual source, including partial packets.
    witnesses=[];emap={tuple(e[:2]):e[2] for e in c['source']['edges']}
    for b in c['blocks']:
        for i in (0,5,10):
            tri=b[i:i+3]
            if len(tri)==3 and all(tuple(sorted(e)) in emap for e in itertools.combinations(tri,2)):
                if math.prod(emap[tuple(sorted(e))] for e in itertools.combinations(tri,2))<0:witnesses.append(tri)
    c['frustrated_triangles']=witnesses
    if n==300:
        prior=load(P/'inputs'/f'{family}_N300_PRIOR.json')
        assert c['source']['edges']==prior['source']['edges'] and c['source']['fields']==prior['source']['fields'] and c['ports']==prior['ports']
    return c

class ContinuationAdapter:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op!='GEN4_PACKET_CONTINUATION_EXACT':return self.base.execute(op,payload)
        c=load(P/payload['source_path']);assert digest(c)==payload['source_record_hash']
        assert CONFIG['code_manifest_hash']==payload['code_manifest_hash']
        t=time.perf_counter();plan=compile_source(c);planning=time.perf_counter()-t
        missing=[x for x in plan['pieces'] if x['key'] not in CACHE]
        t=time.perf_counter()
        # Populate only the missing exact local tables; global output is always freshly computed.
        for piece in missing:
            if piece['key'] in CACHE:continue
            a=exact.solve_cpu(piece['source'],piece['ports'],{'method':'variable_elimination'})['answer']
            bound=piece['source']['energy_bound_B'];table={}
            for row in a['port_rows']:
                coeff=[0]*(bound+1)
                for e,count in row['dos']:coeff[(e+bound)//2]=int(count)
                table[tuple(row['state'])]=fmpz_poly(coeff)
            CACHE[piece['key']]=table
        preparation=time.perf_counter()-t;times=[];answer=None
        for repeat in range(3):
            t=time.perf_counter()
            result=collapse(c,plan,CACHE) if c['bridges'] else packet_solve(c,plan,CACHE)
            times.append(time.perf_counter()-t)
            if answer is None:answer=result['answer']
            else:compare(answer,result['answer'])
        t=time.perf_counter()
        ref=exact.solve_cpu(c['source'],c['ports'],dict(method='variable_elimination',max_seconds=CONFIG['experiment_seconds'],
            max_factor_work=100000000,max_intermediate_entries=2000000,max_output_rows=2000000,max_energy_span=1000000))
        reference_seconds=time.perf_counter()-t;t=time.perf_counter();vh=compare(answer,ref['answer']);comparison=time.perf_counter()-t
        if c['N']==120:
            retained=json.load(gzip.open(P/'inputs'/f"{c['family']}_N120_REFERENCE.json.gz",'rt'))['answers']['variable_elimination']
            compare(answer,retained)
        bound=c['source']['energy_bound_B']
        return dict(status='EXACT_VERIFIED',N=c['N'],family=c['family'],source_hash=c['source']['source_sha256'],
            graph_hash=digest(dict(N=c['N'],edges=c['source']['edges'],fields=c['source']['fields'])),source_record_hash=digest(c),
            ordered_ports_hash=digest(c['ports']),plan_hash=digest(plan),backend_id='LOCAL_FLINT_CPU',
            topology_id=CONFIG['topology_id'],runtime_identity_hash=CONFIG['runtime_identity_hash'],cache_state='WARM_LOCAL_TABLES_FRESH_GLOBAL_SOLVE',
            mathematical_method=result['execution'].get('reduction','EXACT_PACKET_POLYNOMIAL_PRODUCT'),
            preparation_cache_misses=len({p['key'] for p in missing}),local_packets=len(c['blocks']),
            timing=dict(planning_seconds=planning,preparation_seconds=preparation,warm_solve_seconds=times,
                warm_median_ms=statistics.median(times)*1000,independent_full_graph_VE_seconds=reference_seconds,
                full_comparison_seconds=comparison),answer=answer,independent_reference=ref,
            open_operator=dict(bound=bound,ordered_ports=c['ports'],glue=[],rows=[[[ (e+bound)//2,count] for e,count in row['dos']] for row in answer['port_rows']]),
            verification_hash=vh,full_density_verified=True,configuration_count_verified=True,moments_verified=True,
            ordered_conditional_spectra_verified=True,peak_worker_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

def worker_init(config):
    global SESSION,CACHE,CONFIG
    CONFIG=config
    resource.setrlimit(resource.RLIMIT_AS,(config['per_worker_memory_bytes'],config['per_worker_memory_bytes']))
    signal.signal(signal.SIGTERM,signal.SIG_DFL)
    def alarm(*_):raise TimeoutError('Per-experiment wall-time resource gate')
    signal.signal(signal.SIGALRM,alarm)
    assert sha(P/'inputs/PACKET_TABLES.json.gz')==load(P/'inputs/PACKET_TABLES_MANIFEST.json')['sha256']
    raw=json.load(gzip.open(P/'inputs/PACKET_TABLES.json.gz','rt'))
    CACHE={key:{tuple(row['state']):fmpz_poly([int(v) for v in row['coefficients']]) for row in rows} for key,rows in raw.items()}
    SESSION=DomainSession.start('MATTER_SEARCH',objective='Consecutive exact packet-family continuation from N121; full independent verification',output_root=P/'sessions',receipt_storage='gzip')
    SESSION.consumer=ContinuationAdapter(SESSION.consumer)
    print(SESSION.announcement(), 'worker',os.getpid(),flush=True)

def work(payload):
    start=time.perf_counter();signal.alarm(CONFIG['experiment_seconds']+30)
    try:
        result=SESSION.execute('GEN4_PACKET_CONTINUATION_EXACT',payload,purpose='Compile complete source partition, solve full ordered spectrum using exact packet reductions, compare every coefficient with independent full-graph variable elimination')
        rel=f"results/{result['family']}_N{result['N']:06d}.json.gz";write_gz(P/rel,result)
        return dict(status='EXACT_VERIFIED',N=result['N'],family=result['family'],artifact=rel,sha256=sha(P/rel),
            source_hash=result['source_hash'],plan_hash=result['plan_hash'],timing=result['timing'],
            worker_pid=os.getpid(),session=str(SESSION.directory),wall_seconds=time.perf_counter()-start,
            peak_worker_rss_kib=result['peak_worker_rss_kib'],verification_hash=result['verification_hash'])
    except Exception as e:
        return dict(status='FAILED',source_path=payload['source_path'],error=str(e),traceback=traceback.format_exc(),worker_pid=os.getpid(),wall_seconds=time.perf_counter()-start)
    finally:signal.alarm(0)

def mirror(status):
    root=Path(CONFIG['mirror']);root.mkdir(parents=True,exist_ok=True)
    for name in ('STATUS.json','CONFIG.json','CODE_MANIFEST.json','UPSTREAM.json','README.md','QUALIFICATION.json','RUNTIME_IDENTITY.json','SUMMARY.md'):
        if (P/name).exists():
            tmp=root/(name+'.part');shutil.copyfile(P/name,tmp);tmp.replace(root/name)
    # No growing full-results stream on the network volume; all full data stays on container storage.
    if (P/'CATALOG.jsonl').exists():
        tmp=root/'CATALOG.jsonl.part';shutil.copyfile(P/'CATALOG.jsonl',tmp);tmp.replace(root/'CATALOG.jsonl')

def main():
    global CONFIG
    ap=argparse.ArgumentParser();ap.add_argument('--hours',type=float,default=8);ap.add_argument('--steps',type=int);ap.add_argument('--qualify',action='store_true');args=ap.parse_args()
    lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM,stop_signal);signal.signal(signal.SIGINT,stop_signal)
    for path,h in load(P/'CODE_MANIFEST.json').items():assert sha(P/path)==h,path
    # CPU-only campaign: this host denies GPU telemetry. Keep the manager's CPU/cgroup/RAM/storage checks.
    original_command=resources.command
    resources.command=lambda args: None if args[0]=='nvidia-smi' else original_command(args)
    try:profile=resources.inspect(scratch=P,persistent_root=str(P/'persistent'))
    finally:resources.command=original_command
    profile['gpu_probe']='SKIPPED_CPU_ONLY_BACKEND_GPU_TELEMETRY_PERMISSION_DENIED'
    workers=max(1,min(3,int(profile['enforced_cpu_capacity'])-1))
    memory=min(8*1024**3,int(profile['memory_admission_bytes']*.65/workers));assert memory>=1024**3
    identity=dict(verified_binding=runtime.verify(),resources=profile,backend='LOCAL_FLINT_CPU',numpy=__import__('numpy').__version__,python_flint=__import__('flint').__version__,python=sys.version,host=__import__('platform').node())
    atomic(P/'RUNTIME_IDENTITY.json',identity)
    atomic(P/'identities'/('runtime_'+digest(identity)+'.json'),identity)
    CONFIG=dict(workers=workers,per_worker_memory_bytes=memory,experiment_seconds=180,
        topology_id=f'SERIAL_FLINT_PER_EXPERIMENT_{workers}_CPU_PROCESSES',runtime_identity_hash=digest(identity),
        code_manifest_hash=sha(P/'CODE_MANIFEST.json'),mirror=str(P/'persistent/run'),
        disk_reserve_bytes=20*1024**3,maximum_N_admission=100000,wall_hours=args.hours,
        mathematical_stop_N=None,full_independent_VE_every_source=True,automatic_hardware_stop=False)
    atomic(P/'CONFIG.json',CONFIG)
    atomic(P/'identities'/('config_'+digest(CONFIG)+'.json'),CONFIG)
    old=load(P/'STATUS.json') if (P/'STATUS.json').exists() else {}
    completed=old.get('last_completed_N',120);done={}
    if (P/'CATALOG.jsonl').exists():
        for line in (P/'CATALOG.jsonl').read_text().splitlines():
            row=json.loads(line)
            if row.get('status')=='EXACT_VERIFIED':done[(row['N'],row['family'])]=row
    # Recovery verifies the last committed batch rather than trusting a bare numeric counter.
    if completed>120:
        for family in FAMILIES:
            row=done[(completed,family)];assert sha(P/row['artifact'])==row['sha256']
    while all((completed+1,f) in done for f in FAMILIES):
        for family in FAMILIES:
            row=done[(completed+1,family)];assert sha(P/row['artifact'])==row['sha256']
        completed+=1
    start=time.time();deadline=start+args.hours*3600
    status=dict(status='QUALIFYING' if args.qualify else 'RUNNING',pid=os.getpid(),start_utc=now(),deadline_utc=datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat(),last_completed_N=completed,next_N=completed+1,completed_source_cases=sum(1 for k in done if k[0]>=121),workers=workers,project_path=str(P),mirror=CONFIG['mirror'],safe_stop=f'touch {P}/STOP',stop_signal=f'kill -TERM {os.getpid()}',fresh_window=True,resumed_after_N=completed)
    atomic(P/'STATUS.json',status);mirror(status)
    pool=ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),initializer=worker_init,initargs=(CONFIG,))
    submitted=0;last_mirror=0;failed=False
    try:
        if not args.qualify:assert load(P/'QUALIFICATION.json')['status']=='PASS','Qualify before continuation'
        n=120 if args.qualify else completed+1
        while n<=CONFIG['maximum_N_admission']:
            if STOP or (P/'STOP').exists():status['status']='STOPPED';break
            if time.time()>=deadline:status['status']='DEADLINE';break
            free=shutil.disk_usage(P).free;available=resources.live_memory_available(profile)
            if free<CONFIG['disk_reserve_bytes'] or available<workers*512*1024**2:
                status.update(status='RESOURCE_GATE',disk_free_bytes=free,memory_available_bytes=available);break
            if deadline-time.time()<CONFIG['experiment_seconds']+30:
                status['status']='DEADLINE_ADMISSION_GATE';break
            status.update(current_N=n,last_heartbeat_utc=now(),disk_free_bytes=free,memory_available_bytes=available)
            atomic(P/'STATUS.json',status)
            futures={};rows=[]
            for family in FAMILIES:
                if not args.qualify and (n,family) in done:
                    row=done[(n,family)];assert sha(P/row['artifact'])==row['sha256'];rows.append(row);continue
                c=source(family,n);rel=f'sources/{family}_N{n:06d}.json';atomic(P/rel,c)
                payload=dict(source_path=rel,source_record_hash=digest(c),code_manifest_hash=CONFIG['code_manifest_hash'])
                pre=dict(event='PRECOMMIT',utc=now(),N=n,family=family,payload=payload,source_hash=c['source']['source_sha256'],
                    ordered_ports=c['ports'],source_lineage='N100/N105 packet grammar through N120; fifteen-vertex motif continuation',
                    claim_type=c['claim_type'],expected_method='Exact packet product or certified equal-boundary bridge collapse',
                    maximum_wall_seconds=CONFIG['experiment_seconds']+30,resource_snapshot=dict(free_disk_bytes=free,memory_available_bytes=available),
                    verification='Independent full-graph variable elimination; full scalar and ordered-port coefficient equality; exact count and first/second moments',
                    prospective_timing_prediction=None)
                append(P/'EVENTS.jsonl',pre);futures[pool.submit(work,payload)]=family
            remaining=set(futures);iteration_start=time.time();heartbeat=0
            while remaining:
                finished,remaining=wait(remaining,timeout=1,return_when=FIRST_COMPLETED)
                if time.time()-heartbeat>=15:
                    status['last_heartbeat_utc']=now();atomic(P/'STATUS.json',status);heartbeat=time.time()
                for future in finished:
                    row=future.result();append(P/'EVENTS.jsonl',dict(event='RESULT',utc=now(),N=n,family=futures[future],result=row));rows.append(row)
                    if row['status']=='EXACT_VERIFIED':
                        append(P/'CATALOG.jsonl',row);done[(n,futures[future])]=row
                    else:failed=True
                if time.time()-iteration_start>CONFIG['experiment_seconds']+90:
                    for proc in pool._processes.values():proc.terminate()
                    raise TimeoutError('Owned worker exceeded hard batch timeout; completed artifacts retained')
            if failed:status['status']='EXPERIMENT_FAILED';break
            if args.qualify:
                checks=[]
                for family in FAMILIES:
                    c=source(family,300);prior=load(P/'inputs'/f'{family}_N300_PRIOR.json')
                    assert c['source']['edges']==prior['source']['edges'];checks.append(family)
                bad=source('packet',120);bad=copy.deepcopy(bad);u=bad['blocks'][0][0];v=bad['blocks'][1][0]
                bad['source']=norm(120,bad['source']['edges']+[[min(u,v),max(u,v),1]],bad['source']['fields'],'EXTRA_EDGE_CONTROL')
                try:compile_source(bad)
                except AssertionError as e:assert str(e)=='UNACCOUNTED_INTERPACKET_INTERACTION'
                else:raise AssertionError('Partition wrong control accepted')
                atomic(P/'QUALIFICATION.json',dict(status='PASS',utc=now(),N120_full_reference_checks=rows,N300_structure_matches=checks,extra_cross_edge_rejected=True,runtime_identity_hash=CONFIG['runtime_identity_hash']))
                status['status']='QUALIFIED';break
            completed=n;status.update(last_completed_N=n,next_N=n+1,completed_source_cases=sum(1 for k in done if k[0]>=121),last_completed_utc=now(),last_timings={r['family']:r['timing'] for r in rows})
            atomic(P/'STATUS.json',status)
            atomic(P/'CHECKPOINT.json',dict(last_completed_N=n,latest_artifacts=rows,utc=now()))
            (P/'SUMMARY.md').write_text(f'# Consecutive packet-family continuation\n\nOwner: Sean Brady.\n\nAll N121–{n} completed in three families with full independent verification.\n\nLast batch: '+json.dumps(status['last_timings'],indent=2)+'\n')
            if time.time()-last_mirror>=60:mirror(status);last_mirror=time.time()
            print('COMPLETE',n,{r['family']:round(r['timing']['warm_median_ms'],3) for r in rows},flush=True)
            submitted+=1
            if args.steps and submitted>=args.steps:status['status']='BOUNDED_CYCLE_COMPLETE';break
            n+=1
        else:status['status']='SOURCE_SIZE_ENGINEERING_GATE'
    except Exception as e:
        status.update(status='FAILED',error=str(e),traceback=traceback.format_exc());traceback.print_exc()
    finally:
        pool.shutdown(wait=True,cancel_futures=True)
        status.update(finished_utc=now(),last_completed_N=completed,next_N=completed+1,last_heartbeat_utc=now())
        atomic(P/'STATUS.json',status);mirror(status)
        print(json.dumps({k:v for k,v in status.items() if k!='last_timings'},indent=2),flush=True)
    return 1 if status['status'] in ('FAILED','EXPERIMENT_FAILED') else 0

if __name__=='__main__':raise SystemExit(main())
