"""Bounded additive dense solver qualification and detached test controller."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import sys,json,gzip,time,signal,subprocess,datetime,shutil,resource,traceback,copy,fcntl
from pathlib import Path
from baseline import *
from optimized import solve
from cuda_tables import CUDA,KERNEL
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION import runtime
from gen4 import resources
P=Path(__file__).resolve().parent
FOLLOWER=Path('/opt/gen4-spin-dense-follower1/project/graphs')
MIRROR=Path('/workspace/gen4/runs/frustrated-spin-magnetization3')
STOP=False

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.part')
    with temp.open('w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    temp.replace(path)
def append(name,row):
    with (P/name).open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def write_result(path,result):
    path.parent.mkdir(exist_ok=True,parents=True);tmp=path.with_suffix('.part')
    with gzip.open(tmp,'wt') as f:json.dump(result,f,separators=(',',':'))
    tmp.replace(path)
def stop(*_):
    global STOP
    STOP=True

def source_snapshot(n,family,fill):
    directory=f'N{n:06d}';name=f'{family}_N{n:06d}_fill_{"plus" if fill==1 else "minus"}.json'
    src=FOLLOWER/directory/name;d=json.loads(src.read_text());dst=P/'inputs'/directory
    dst.mkdir(parents=True,exist_ok=True)
    for file in [name,d['couplings_file'],d['parent_record']]:
        target=dst/file
        if target.exists():assert sha(target)==sha(src.parent/file)
        else:shutil.copyfile(src.parent/file,target)
    return dst/name

def check_code():
    manifest=json.loads((P/'CODE_MANIFEST.json').read_text())
    for name,h in manifest.items():assert sha(P/name)==h,name
    return sha(P/'CODE_MANIFEST.json')

def profile():
    original=resources.command
    resources.command=lambda args:None if args[0]=='nvidia-smi' else original(args)
    try:p=resources.inspect(scratch=P,persistent_root='/workspace/gen4')
    finally:resources.command=original
    p['gpu_telemetry']='GPU checked independently through CUDA driver; host MIG memory telemetry is permission-limited'
    assert p['enforced_cpu_capacity']>=4,'CPU_RESOURCE_GATE'
    assert shutil.disk_usage(P).free>=200*1024**3,'DISK_RESOURCE_GATE'
    # Add an explicit project-local cache-aware admission estimate; preserve the
    # manager's original observation. Inactive clean disk cache is reclaimable.
    cg=Path('/sys/fs/cgroup');ms=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
    reclaim=max(0,int(ms['inactive_file'])-int(ms['file_dirty'])-int(ms['file_writeback']))
    cap=int((cg/'memory.max').read_text());used=int((cg/'memory.current').read_text())
    host_available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
    p['inactive_clean_cache_bytes']=reclaim
    p['project_cache_aware_admission_bytes']=max(0,min(host_available,cap-used+reclaim)-max(8*1024**3,cap//12))
    assert p['project_cache_aware_admission_bytes']>=8*1024**3,'RESOURCE_MANAGER_MEMORY_GATE'
    return p

class Adapter:
    def __init__(self,base,cuda):self.base=base;self.cuda=cuda
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_DENSE_COMPONENT_POWER_CONTROLS':
            assert check_code()==payload['code_manifest_sha256']
            return controls(self.cuda)
        if op!='GEN4_DENSE_COMPONENT_POWER_EXACT':return self.base.execute(op,payload)
        assert check_code()==payload['code_manifest_sha256']
        c,fill,source,identity=load_bound(P/payload['manifest'])
        assert identity==payload['source_identity']
        result=solve(c,fill,source,self.cuda)
        golden=payload.get('golden')
        if golden:
            assert sha(Path(golden['path']))==golden['sha256']
            old=json.load(gzip.open(golden['path'],'rt'))
            assert result['answer']==old['answer'] and result['joint_spectrum_hash']==old['joint_spectrum_hash'],'RETAINED_FULL_SPECTRUM_MISMATCH'
            result['retained_baseline_seconds']=old['timing']['total_solve_and_verification_seconds']
            result['retained_baseline_peak_rss_kib']=old['peak_rss_kib']
        if c['N']==300 and c['family']=='signed_packet_chain' and fill==-1:
            import baseline
            old=baseline.solve(c,fill,source,self.cuda)
            assert old['answer']==result['answer'] and old['joint_spectrum_hash']==result['joint_spectrum_hash']
            result['matched_baseline_timing']=old['timing']
        result.update(source_identity=identity,cuda_identity=self.cuda.identity,
            cuda_initialization_seconds=self.cuda.initialization_seconds,code_manifest_sha256=payload['code_manifest_sha256'],
            runtime_identity_sha256=payload['runtime_identity_sha256'])
        return result

def controls(cuda):
    path=source_snapshot(12,'signed_packet_chain',1);c,fill,s,identity=load_bound(path)
    failures=[]
    # Wrong inherited coupling must be rejected by source binding.
    d=json.loads(path.read_text());raw=bytearray(gzip.decompress((path.parent/d['couplings_file']).read_bytes()))
    u,v,_=c['source']['edges'][0];i=dense_format.index(c['N'],u,v);raw[i//8]^=1<<(i%8)
    try:dense_format.validate(raw,c['N'],c['source']['edges'],fill)
    except AssertionError:failures.append('MUTATED_INHERITED_COUPLING_REJECTED')
    # Dropping declared chain bridges must never silently remove their energy.
    wrong=copy.deepcopy(c);assert wrong['bridges'];wrong['bridges']=[]
    try:plan(wrong,fill)
    except AssertionError:failures.append('OMITTED_CROSS_EDGE_REJECTED')
    # Nonzero fields exercise a branch that cannot use spin-flip invariance.
    variant=copy.deepcopy(c);variant['source']['fields'][0]=1;variant['source']['fields'][-1]=-2
    vs=exact.validate_source(dict(N=s['N'],edges=s['edges'],fields=variant['source']['fields'],parent_vertices=s['parent_vertices'],family='DENSE_SOLVER1_FIELD_CONTROL'))
    result=solve(variant,fill,vs,cuda)
    hist={i:{e:int(count) for e,count in row['dos']} for i,row in enumerate(result['answer']['port_rows'])}
    bad=copy.deepcopy(hist);energy=next(iter(bad[0]));bad[0][energy]+=1
    try:exact.finalize_answer(vs,variant['ports'],bad)
    except ArithmeticError:failures.append('WRONG_DENSITY_COEFFICIENT_REJECTED')
    shifted={state:{energy+1:count for energy,count in row.items()} for state,row in hist.items()}
    if shifted!=direct_dense(vs,variant['ports']):failures.append('WRONG_GLOBAL_ENERGY_SHIFT_REJECTED')
    assert len(failures)==4
    return dict(status='PASS',wrong_controls=failures,nonzero_field_exact_control=result['answer']['spectrum_sha256'],
        nonzero_field_direct_enumeration=True)

def case(payload_file):
    payload=json.loads(Path(payload_file).read_text());check_code();start=time.perf_counter();cuda=None
    try:
        cuda=CUDA()
        with DomainSession.start('MATTER_SEARCH',objective='Exact complete-graph DOS from joint magnetization and source-correction tables; GPU integer enumeration with independent exact replay',output_root=P/'sessions',receipt_storage='gzip') as session:
            print(session.announcement(),flush=True);session.consumer=Adapter(session.consumer,cuda)
            result=session.execute('GEN4_DENSE_COMPONENT_POWER_EXACT',payload,
                purpose='Compute full scalar and ordered conditional dense spectra using CUDA local integer tables and FLINT exact composition; verify all coefficients via independent local enumeration and global replay')
            result['session']=str(session.directory)
            if payload.get('run_controls'):
                result['controls']=session.execute('GEN4_DENSE_COMPONENT_POWER_CONTROLS',payload,
                    purpose='Explicit inherited-coupling/cross-edge/count/shift wrong controls and an exact nonzero-field dense source variant')
        result['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result['whole_process_work_seconds']=time.perf_counter()-start
        write_result(P/payload['result'],result)
        receipt=dict(status=result['status'],N=result['N'],family=result['family'],fill_coupling=result['fill_coupling'],
            result=payload['result'],sha256=sha(P/payload['result']),timing=result['timing'],
            cuda_initialization_seconds=result['cuda_initialization_seconds'],cuda_identity=result['cuda_identity'],
            peak_rss_kib=result['peak_rss_kib'],plan_hash=result['plan_hash'],source_identity=result['source_identity'],
            spectrum_sha256=result['answer']['spectrum_sha256'],session=result['session'],controls=result.get('controls'),
            reductions=result['reductions'],matched_baseline_timing=result.get('matched_baseline_timing'),
            retained_baseline_seconds=result.get('retained_baseline_seconds'))
        atomic(P/payload['receipt'],receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['source_identity','timing','cuda_identity']}),flush=True)
    except Exception:
        atomic(P/payload['receipt'],dict(status='FAILED',error=traceback.format_exc()));raise
    finally:
        if cuda:cuda.close()

def mirror():
    MIRROR.mkdir(parents=True,exist_ok=True)
    for name in ['README.md','STATUS.json','QUALIFICATION.json','RUNTIME_IDENTITY.json','CODE_MANIFEST.json','CATALOG.jsonl','SUMMARY.md']:
        if (P/name).exists():
            target=MIRROR/(name+'.part');shutil.copyfile(P/name,target);target.replace(MIRROR/name)

def execute_case(n,family,fill,phase,identity_hash,controls_flag=False):
    check_code();res=profile();path=source_snapshot(n,family,fill)
    c,j,s,binding=load_bound(path);pl=plan(c,j);key=f'{phase}_{family}_N{n:06d}_{fill:+d}'
    relative=f'results/{key}.json.gz';receipt=f'receipts/{key}.json'
    if (P/receipt).exists():
        old=json.loads((P/receipt).read_text())
        if old['status']=='EXACT_DENSE_VERIFIED':
            assert sha(P/old['result'])==old['sha256'];return old
        raise RuntimeError('A prior failed experiment is retained; use a successor attempt rather than overwriting')
    payload=dict(manifest=str(path.relative_to(P)),source_identity=binding,code_manifest_sha256=check_code(),
        runtime_identity_sha256=identity_hash,result=relative,receipt=receipt,run_controls=controls_flag)
    old_phase='qualification' if n<=18 else 'production'
    golden=Path('/opt/gen4-spin-dense-solver1/project/results')/f'{old_phase}_{family}_N{n:06d}_{fill:+d}.json.gz'
    if golden.exists():payload['golden']=dict(path=str(golden),sha256=sha(golden))
    precommit=dict(timestamp=now(),question_id=key,phase=phase,
        question='Does exact correction-component factoring, repeated-component powers, and streamed port readout reduce CPU time and RAM while preserving the full dense joint spectrum?',
        methods=['ZERO_CORRECTION_BRIDGE_COMPONENTS_POWERS_K_MAJOR','FORWARD_COMPONENT_REPLAY_POWERS_T_MAJOR'],
        source_identity=binding,plan_hash=digest(pl),maximum_polynomial_degree=pl['maximum_degree'],
        resource_profile=res,maximum_case_seconds=900,maximum_host_rss_bytes=8*1024**3,
        local_GPU_assignment_limit=1<<18,maximum_N=1050,
        verification='CPU/GPU equality for every local joint coefficient; different global encoding and contraction direction; binomial magnetization marginals; full/conditional counts and first/second moments; independent direct dense enumeration at N<=18',
        expected_outcomes=['Full equality permits the next bounded case','Mismatch stops qualification or campaign','Capacity/deadline stops without promoting a result'],payload=payload)
    atomic(P/'precommits'/f'{key}.json',precommit);append('EVENTS.jsonl',dict(event='PRECOMMIT',**precommit))
    atomic(P/'payloads'/f'{key}.json',payload)
    with (P/'logs'/f'{key}.log').open('w') as log:
        process=subprocess.Popen([sys.executable,str(P/'run.py'),'--case',str(P/'payloads'/f'{key}.json')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        started=time.monotonic();reason=None
        while process.poll() is None:
            if time.monotonic()-started>900:reason='CASE_TIME_GATE'
            try:
                status=Path(f'/proc/{process.pid}/status').read_text()
                rss=int(next(x.split()[1] for x in status.splitlines() if x.startswith('VmRSS:')))*1024
                if rss>8*1024**3:reason='CASE_RSS_GATE'
            except (FileNotFoundError,StopIteration):pass
            if reason:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                break
            time.sleep(.5)
        if process.returncode!=0 or reason:
            failure=dict(status='FAILED',question_id=key,reason=reason,returncode=process.returncode,receipt=receipt)
            append('EVENTS.jsonl',dict(event='FAILED',timestamp=now(),**failure));raise RuntimeError(json.dumps(failure))
    row=json.loads((P/receipt).read_text());assert row['status']=='EXACT_DENSE_VERIFIED'
    append('CATALOG.jsonl',dict(question_id=key,phase=phase,**row));append('EVENTS.jsonl',dict(event='COMPLETED',timestamp=now(),question_id=key,receipt=receipt,sha256=row['sha256']))
    return row

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--case');ap.add_argument('--qualify',action='store_true');ap.add_argument('--smoke',action='store_true');ap.add_argument('--minutes',type=float,default=60);a=ap.parse_args()
    if a.case:return case(a.case)
    for folder in ['logs','receipts','payloads','results','precommits']:(P/folder).mkdir(exist_ok=True)
    lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);os.nice(10);check_code()
    identity=dict(runtime=runtime.verify(),resources=profile(),python=sys.version,flint=__import__('flint').__version__,
        numpy=np.__version__,code_manifest_sha256=check_code(),kernel_sha256=digest(KERNEL),backend='CUDA_LOCAL_INTEGER_TABLES_CPU_COMPONENT_POWERS_STREAMED_PORTS')
    atomic(P/'RUNTIME_IDENTITY.json',identity);ih=digest(identity);atomic(P/'identities'/f'{ih}.json',identity)
    start=time.time();deadline=start+a.minutes*60
    state=dict(status='QUALIFYING' if a.qualify else 'RUNNING',pid=os.getpid(),start_utc=now(),deadline_utc=datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat(),
        cpu_workers=1,GPU_workers=1,maximum_case_seconds=900,maximum_host_rss_bytes=8*1024**3,
        safe_stop=f'touch {P}/STOP',other_campaigns_modified=False,completed_this_invocation=[])
    atomic(P/'STATUS.json',state);mirror()
    phase='qualification' if a.qualify else 'production'
    ns=[12,18] if a.qualify else ([300] if a.smoke else [750,900,1050])
    try:
        if not a.qualify:assert json.loads((P/'QUALIFICATION.json').read_text())['status']=='PASS'
        for n in ns:
            for family in ['packet','signed_packet','signed_packet_chain']:
                for fill in [1,-1]:
                    if STOP or (P/'STOP').exists():state['status']='STOPPED';raise StopIteration
                    # Keep the entire admitted case inside the bounded window.
                    if time.time()+900>deadline:state['status']='DEADLINE_ADMISSION_STOP';raise StopIteration
                    state['current_case']=dict(N=n,family=family,fill=fill);state['heartbeat_utc']=now();atomic(P/'STATUS.json',state);mirror()
                    print('ADMIT',state['current_case'],flush=True)
                    row=execute_case(n,family,fill,phase,ih,controls_flag=a.qualify and n==12 and family=='signed_packet_chain' and fill==1)
                    state['completed_this_invocation'].append(dict(N=n,family=family,fill=fill,seconds=row['timing']['total_solve_and_verification_seconds'],peak_rss_kib=row['peak_rss_kib']))
                    state['last_completed']=state['current_case'];atomic(P/'STATUS.json',state);mirror()
                    print('COMPLETE',state['completed_this_invocation'][-1],flush=True)
        state['status']='QUALIFIED' if a.qualify else 'COMPLETED'
        if a.qualify:
            atomic(P/'QUALIFICATION.json',dict(status='PASS',timestamp=now(),cases=state['completed_this_invocation'],
                all_direct_dense_enumeration=True,wrong_controls=4,nonzero_field_control=True,code_manifest_sha256=check_code()))
    except StopIteration:pass
    except Exception:
        state['status']='FAILED';state['error']=traceback.format_exc();print(state['error'],flush=True)
    finally:
        state['finished_utc']=now();atomic(P/'STATUS.json',state)
        (P/'SUMMARY.md').write_text('# Dense solver bounded test\n\nStatus: '+state['status']+'\n\n'+json.dumps(state['completed_this_invocation'],indent=2)+'\n\nExisting packet and graph-generation campaigns were not modified. Full outputs and exact certificates remain under results/.\n')
        mirror()
    if state['status']=='FAILED':sys.exit(1)
if __name__=='__main__':main()
