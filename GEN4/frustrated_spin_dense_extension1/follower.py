"""Detached, bounded source-generation follower for verified packet results."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,datetime,fcntl,gzip,json,multiprocessing,resource,shutil,signal,sys,time,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from dense_format import *

P=Path(__file__).resolve().parent
RUNTIME=Path(os.environ.get('GEN4_DENSE_RUNTIME','/opt/gen4-spin-continuation1/runtime'))
sys.path.insert(0,str(RUNTIME))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION import runtime
from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import validate_source
from gen4 import resources
FAMILIES=('packet','signed_packet','signed_packet_chain')
STOP=False;CONFIG={};SESSION=None

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.part')
    with tmp.open('w') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)
def append(path,obj):
    with Path(path).open('a') as f:f.write(json.dumps(obj,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def gz(path,data):
    tmp=path.with_name(path.name+'.part')
    with tmp.open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',compresslevel=3,mtime=0) as z:z.write(data)
        f.flush();os.fsync(f.fileno())
    tmp.replace(path)
def load(path):return json.loads(Path(path).read_text())
def handler(*_):
    global STOP
    STOP=True

def parent_files(n,family,receipt=None):
    if n<=120:
        root=Path(CONFIG['seed']);base=f'{family}_N{n:03d}'
    else:
        root=Path(CONFIG['producer']);base=f'{family}_N{n:06d}'
    src=root/'sources'/(base+'.json');result=root/'results'/(base+'.json.gz')
    c=load(src);normalized=validate_source(c['source']);assert normalized['source_sha256']==c['source']['source_sha256']
    result_hash=filehash(result)
    if n<=120:
        proof=json.load(gzip.open(result,'rt'))
        assert proof['status']=='EXACT' and proof['full_density_verified'] and proof['source_hash']==c['source']['source_sha256']
    else:
        assert receipt['status']=='EXACT_VERIFIED' and receipt['N']==n and receipt['family']==family
        assert result_hash==receipt['sha256'] and receipt['source_hash']==c['source']['source_sha256']
    return c,dict(source_path=str(src),source_file_sha256=filehash(src),parent_source_sha256=c['source']['source_sha256'],
        verified_result_path=str(result),verified_result_file_sha256=result_hash,receipt=receipt)

def completion_valid(folder):
    complete=load(folder/'COMPLETE.json')
    for r in complete['variants']:
        assert filehash(folder/r['manifest'])==r['manifest_sha256']
        assert filehash(folder/r['couplings'])==r['couplings_sha256']
    for r in complete['parents']:assert filehash(folder/r['file'])==r['sha256']
    return complete

class Adapter:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op!='GEN4_DENSE_FOLLOWER_GENERATE':return self.base.execute(op,payload)
        n=payload['N'];assert payload['code_manifest_sha256']==CONFIG['code_manifest_sha256']
        folder=P/CONFIG['output_dir']/f'N{n:06d}';folder.mkdir(parents=True,exist_ok=True)
        if (folder/'COMPLETE.json').exists():
            out=completion_valid(folder);out['recovered_existing_complete']=True;return out
        started=time.perf_counter();variants=[];parents=[]
        for family in FAMILIES:
            c,proof=parent_files(n,family,payload['receipts'].get(family))
            assert c['N']==n and all(j in (-1,1) for u,v,j in c['source']['edges'])
            parent_name=family+'.parent.json.gz';gz(folder/parent_name,json.dumps(c,separators=(',',':')).encode())
            parents.append(dict(family=family,file=parent_name,sha256=filehash(folder/parent_name),provenance=proof))
            for fill in (1,-1):
                tick=time.perf_counter();raw=generate(n,c['source']['edges'],fill)
                key=f"{family}_N{n:06d}_fill_{'plus' if fill==1 else 'minus'}";couplings=key+'.couplings.bits.gz'
                gz(folder/couplings,raw);expected=sha(raw);del raw
                raw=gzip.decompress((folder/couplings).read_bytes());assert sha(raw)==expected
                checked=validate(raw,n,c['source']['edges'],fill)
                d=dict(schema='GEN4_COMPLETE_SIGNED_GRAPH_BITS_V1',status='SOURCE_GENERATED_NOT_DOS_SOLVED',key=key,N=n,
                    pair_count=n*(n-1)//2,couplings_file=couplings,raw_couplings_sha256=expected,
                    raw_coupling_bytes=len(raw),encoding='Lexicographic unordered pairs (u,v), u<v; least-significant bit first in each byte; 1 means J=+1, 0 means J=-1; zero unused padding',
                    pair_index_formula='u*(2*N-u-1)//2 + v-u-1',fields=c['source']['fields'],parent_vertices=c['source']['parent_vertices'],ordered_ports=c['ports'],
                    parent_record=parent_name,parent_source_sha256=c['source']['source_sha256'],parent_provenance=proof,
                    fill_coupling=fill,checks=checked,full_density_solved=False,
                    graph_sha256=digest(dict(N=n,fields=c['source']['fields'],raw_couplings_sha256=expected)),
                    exact_representation='Every pair coupling is explicitly stored as one bit; this is not an omitted-edge recipe',
                    energy_identity='E=-J0*(M^2-N)/2-sum_parent((Juv-J0)*su*sv)-sum_i(hi*si)',
                    generation_and_readback_seconds=time.perf_counter()-tick,code_manifest_sha256=CONFIG['code_manifest_sha256'])
                if CONFIG['qualification']:
                    # Decoder walks pairs independently of the producer's offset formula.
                    original={tuple(e[:2]):e[2] for e in c['source']['edges']}
                    for u,v,j in iter_edges(n,raw):assert j==original.get((u,v),fill)
                    if n==300:
                        ref=next(x for x in load(P/'N300_REFERENCES.json') if x['family']==family and x['fill_coupling']==fill)
                        assert expected==ref['raw_bits_sha256'];d['matches_prior_explicit_N300_graph']=True
                manifest=key+'.json';atomic(folder/manifest,d)
                variants.append(dict(key=key,manifest=manifest,manifest_sha256=filehash(folder/manifest),couplings=couplings,
                    couplings_sha256=filehash(folder/couplings),raw_bytes=len(raw),stored_bytes=(folder/couplings).stat().st_size,
                    generation_seconds=d['generation_and_readback_seconds']))
        complete=dict(status='SIX_COMPLETE_GRAPHS_VERIFIED',N=n,utc=now(),variants=variants,parents=parents,
            full_DOS_solves=0,seconds=time.perf_counter()-started,code_manifest_sha256=CONFIG['code_manifest_sha256'])
        atomic(folder/'COMPLETE.json',complete);return complete

def initializer(config):
    global CONFIG,SESSION
    CONFIG=config;resource.setrlimit(resource.RLIMIT_AS,(config['worker_memory_bytes'],config['worker_memory_bytes']))
    signal.signal(signal.SIGTERM,signal.SIG_DFL)
    def alarm(*_):raise TimeoutError('Dense follower task wall-time gate')
    signal.signal(signal.SIGALRM,alarm)
    SESSION=DomainSession.start('MATTER_SEARCH',objective='Generate exact complete signed graph sources behind verified packet results; no dense DOS solves',output_root=P/'sessions',receipt_storage='gzip')
    SESSION.consumer=Adapter(SESSION.consumer);print(SESSION.announcement(),'worker',os.getpid(),flush=True)
def work(payload):
    signal.alarm(180)
    try:return SESSION.execute('GEN4_DENSE_FOLLOWER_GENERATE',payload,purpose='Bind the verified parent, explicitly generate every pair coupling, independently read back the compressed graph and verify all inherited and added interactions')
    finally:signal.alarm(0)

def refresh_receipts(path,offset,rows):
    with Path(path).open() as f:
        f.seek(offset)
        while True:
            pos=f.tell();line=f.readline()
            if not line or not line.endswith('\n'):return pos
            r=json.loads(line)
            if r.get('status')=='EXACT_VERIFIED':rows[(r['N'],r['family'])]=r

def wrong_controls():
    n=6;edges=[[0,1,-1],[2,3,1]];good=generate(n,edges,1)
    for tag,k in [('parent',index(n,0,1)),('missing',index(n,0,2))]:
        bad=bytearray(good);bad[k//8]^=1<<(k%8)
        try:validate(bad,n,edges,1)
        except AssertionError:pass
        else:raise AssertionError('Wrong control accepted: '+tag)
    bad=bytearray(good);bad[-1]|=128
    try:validate(bad,n,edges,1)
    except AssertionError:pass
    else:raise AssertionError('Padding control accepted')
    return ['changed inherited coupling rejected','changed newly added coupling rejected','invalid padding rejected']

def mirror():
    dest=Path(CONFIG['mirror']);dest.mkdir(parents=True,exist_ok=True)
    for name in ('STATUS.json','CONFIG.json','RUNTIME_IDENTITY.json','QUALIFICATION.json','CODE_MANIFEST.json','README.md','INDEX.jsonl'):
        if (P/name).exists():
            tmp=dest/(name+'.part');shutil.copyfile(P/name,tmp);tmp.replace(dest/name)

def main():
    global CONFIG
    ap=argparse.ArgumentParser();ap.add_argument('--qualify',action='store_true');ap.add_argument('--steps',type=int);args=ap.parse_args()
    lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM,handler);signal.signal(signal.SIGINT,handler)
    for name,h in load(P/'CODE_MANIFEST.json').items():assert filehash(P/name)==h
    producer=Path('/opt/gen4-spin-continuation1/project');producer_state=load(producer/'STATUS.json')
    old_command=resources.command;resources.command=lambda a:None if a[0]=='nvidia-smi' else old_command(a)
    try:profile=resources.inspect(scratch=P,persistent_root='/workspace/gen4')
    finally:resources.command=old_command
    worker_count=max(1,min(2,int(profile['enforced_cpu_capacity'])-int(producer_state['workers'])-1))
    identity=dict(runtime=runtime.verify(),resource_profile=profile,producer_pid=producer_state['pid'],cpu_only=True)
    atomic(P/'RUNTIME_IDENTITY.json',identity);atomic(P/'identities'/('runtime_'+digest(identity)+'.json'),identity)
    CONFIG=dict(producer=str(producer),seed='/opt/gen4-spin-dense-follower1/seed_catalog',workers=worker_count,
        worker_memory_bytes=min(4*1024**3,int(profile['memory_admission_bytes']*.25/worker_count)),
        qualification=args.qualify,output_dir='qualification' if args.qualify else 'graphs',
        mirror='/workspace/gen4/runs/frustrated-spin-dense-follower1',disk_reserve_bytes=200*1024**3,
        code_manifest_sha256=filehash(P/'CODE_MANIFEST.json'),runtime_identity_sha256=digest(identity),full_DOS_solves=False)
    assert CONFIG['worker_memory_bytes']>=1024**3
    atomic(P/'CONFIG.json',CONFIG);atomic(P/'identities'/('config_'+digest(CONFIG)+'.json'),CONFIG)
    deadline=datetime.datetime.fromisoformat(producer_state['deadline_utc']).timestamp()+300
    done={}
    if not args.qualify and (P/'INDEX.jsonl').exists():
        for line in (P/'INDEX.jsonl').read_text().splitlines():r=json.loads(line);done[r['N']]=r
    contiguous=0
    while contiguous+1 in done:contiguous+=1
    if contiguous:completion_valid(P/'graphs'/f'N{contiguous:06d}')
    state=dict(status='QUALIFYING' if args.qualify else 'RUNNING',pid=os.getpid(),start_utc=now(),last_contiguous_N=contiguous,
        completed_N_count=len(done),generated_graphs=len(done)*6,producer_last_completed_N=producer_state['last_completed_N'],
        workers=worker_count,deadline_utc=datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat(),
        safe_stop=f'touch {P}/STOP',project_path=str(P),full_DOS_solves=0,resumed_after_N=contiguous)
    atomic(P/'STATUS.json',state)
    if not args.qualify:assert load(P/'QUALIFICATION.json')['status']=='PASS'
    receipts={};offset=0;pending={};next_n=1;batch_done=0;last_mirror=0
    qualification_targets=iter((1,2,12,120,121,300))
    pool=ProcessPoolExecutor(max_workers=worker_count,mp_context=multiprocessing.get_context('spawn'),initializer=initializer,initargs=(CONFIG,))
    try:
        while True:
            producer_state=load(producer/'STATUS.json');limit=producer_state['last_completed_N']
            offset=refresh_receipts(producer/'CATALOG.jsonl',offset,receipts)
            free=shutil.disk_usage(P).free;available=resources.live_memory_available(profile)
            if STOP or (P/'STOP').exists():state['status']='STOPPING'
            elif time.time()>=deadline:state['status']='DEADLINE'
            elif free<CONFIG['disk_reserve_bytes'] or available<1024**3:state['status']='RESOURCE_GATE'
            while len(pending)<worker_count and state['status'] in ('RUNNING','QUALIFYING'):
                if args.steps and batch_done+len(pending)>=args.steps:break
                if args.qualify:
                    try:n=next(qualification_targets)
                    except StopIteration:break
                else:
                    while next_n in done:next_n+=1
                    n=next_n
                if n>limit:break
                if n>120 and not all((n,f) in receipts for f in FAMILIES):break
                pair_bytes=(n*(n-1)//2+7)//8
                if 4*pair_bytes+512*1024**2>CONFIG['worker_memory_bytes']:
                    state['status']='GRAPH_MEMORY_GATE';break
                parent_receipts={f:receipts[(n,f)] for f in FAMILIES} if n>120 else {}
                payload=dict(N=n,receipts=parent_receipts,producer_verified_through_N=limit,code_manifest_sha256=CONFIG['code_manifest_sha256'])
                append(P/'EVENTS.jsonl',dict(event='PRECOMMIT',utc=now(),payload=payload,task='Six complete graph constructions; no dense density solve'))
                pending[pool.submit(work,payload)]=dict(N=n,submitted=time.time());next_n=n+1
            if pending:
                finished,_=wait(pending,timeout=1,return_when=FIRST_COMPLETED)
                for future in finished:
                    job=pending.pop(future);result=future.result();n=result['N']
                    append(P/'EVENTS.jsonl',dict(event='COMPLETED',utc=now(),N=n,variants=6,seconds=result['seconds']))
                    index_row=dict(N=n,status=result['status'],variants=6,seconds=result['seconds'],complete=f"{CONFIG['output_dir']}/N{n:06d}/COMPLETE.json",complete_sha256=filehash(P/CONFIG['output_dir']/f'N{n:06d}'/'COMPLETE.json'),bytes=sum(r['stored_bytes'] for r in result['variants']))
                    if args.qualify:done[n]=index_row
                    else:append(P/'INDEX.jsonl',index_row);done[n]=index_row
                    batch_done+=1
                    while contiguous+1 in done:contiguous+=1
                    print('COMPLETE_DENSE',n,'six graphs',round(result['seconds'],3),'seconds',flush=True)
                if any(time.time()-r['submitted']>240 for r in pending.values()):
                    for proc in pool._processes.values():proc.terminate()
                    raise TimeoutError('Follower-owned task exceeded hard deadline')
            else:
                if args.qualify:
                    assert set(done)=={1,2,12,120,121,300}
                    atomic(P/'QUALIFICATION.json',dict(status='PASS',utc=now(),tested_N=sorted(done),graph_variants=36,
                        all_pair_decoding_verified=True,N300_matches_prior_explicit_graphs=True,wrong_controls=wrong_controls(),runtime_identity_sha256=digest(identity)))
                    state['status']='QUALIFIED';break
                if state['status'] not in ('RUNNING','QUALIFYING'):break
                if args.steps and batch_done>=args.steps:state['status']='BOUNDED_CYCLE_COMPLETE';break
                if contiguous>=limit and producer_state['status'] not in ('RUNNING','QUALIFYING'):
                    state['status']='CAUGHT_UP_PRODUCER_FINISHED';break
                time.sleep(2)
            state.update(last_contiguous_N=contiguous,completed_N_count=len(done),generated_graphs=len(done)*6,
                producer_last_completed_N=limit,backlog_N=max(0,limit-contiguous),in_flight=[r['N'] for r in pending.values()],
                last_heartbeat_utc=now(),disk_free_bytes=free,memory_headroom_bytes=available)
            atomic(P/'STATUS.json',state)
            if time.time()-last_mirror>=60:mirror();last_mirror=time.time()
            if state['status'] not in ('RUNNING','QUALIFYING') and not pending:break
    except Exception as e:
        state.update(status='FAILED',error=str(e),traceback=traceback.format_exc());traceback.print_exc()
    finally:
        pool.shutdown(wait=True,cancel_futures=True)
        if state['status']=='STOPPING':state['status']='STOPPED'
        state.update(last_contiguous_N=contiguous,completed_N_count=len(done),generated_graphs=len(done)*6,finished_utc=now())
        atomic(P/'STATUS.json',state);mirror();print(json.dumps(state,indent=2),flush=True)
    return 1 if state['status']=='FAILED' else 0

if __name__=='__main__':raise SystemExit(main())
