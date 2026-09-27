"""Native pod qualification, topology measurements, bounded exact production."""
import argparse,concurrent.futures,fcntl,json,math,multiprocessing,os
from pathlib import Path
import shutil,signal,subprocess,sys,time,traceback
from engine import ROOT,RAM,C,P,atomic,sha,source,read_binary,initialize,job
from math_core import j,x
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION import runtime


def resources():
    cg=Path('/sys/fs/cgroup');quota,period=(cg/'cpu.max').read_text().split()
    cpus=min(len(os.sched_getaffinity(0)),float(quota)/int(period) if quota!='max' else 128,C['maximum_cpu_equivalents'])
    limit=(cg/'memory.max').read_text().strip()
    memory=int(limit) if limit!='max' else int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
    return dict(cpu_equivalents=cpus,affinity=sorted(os.sched_getaffinity(0)),memory_limit_bytes=memory,
                memory_current_bytes=int((cg/'memory.current').read_text()),ram_staging_free_bytes=shutil.disk_usage(RAM).free,
                disk_free_bytes=shutil.disk_usage(ROOT).free,cgroup_cpu_stat=(cg/'cpu.stat').read_text(),
                cgroup_memory_events=(cg/'memory.events').read_text())


def batch(jobs,workers,threads,output):
    context=multiprocessing.get_context('spawn');flush=context.Semaphore(2);start=time.perf_counter();before=resources();results=[]
    directory=ROOT/output;directory.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=context,initializer=initialize,initargs=(threads,flush)) as pool:
        pending={pool.submit(job,p):p for p in jobs}
        for future in concurrent.futures.as_completed(pending):
            result=future.result();results.append(result)
            tag=x.digest(result['payload'])[:16];atomic(directory/f'job_{tag}.json',result)
            atomic(directory/'PROGRESS.json',dict(completed_jobs=len(results),total_jobs=len(jobs),workers=workers,threads=threads,elapsed=time.perf_counter()-start,resources=resources()))
            print('JOB_COMPLETE',len(results),len(jobs),result['payload']['family'],result['payload']['fill'],result['payload']['orientation'],result['computed_rows'],flush=True)
            if (ROOT/'STOP').exists():
                for f in pending:f.cancel()
                break
    after=resources();wall=time.perf_counter()-start
    return dict(status='PASS' if len(results)==len(jobs) else 'CHECKPOINTED',workers=workers,threads=threads,jobs=results,
                seconds=wall,cpu_seconds=sum(v['cpu_seconds'] for v in results),
                peak_worker_rss_kib=max((v['peak_rss_kib'] for v in results),default=0),before=before,after=after)


def qualification():
    initialize(1,None);checks=[]
    for n in (12,30):
        for family in C['families']:
            for fill in (1,-1):
                c,_=source(family,n,fill);expected=None;previous=None
                for orientation in ('K_MAJOR','T_MAJOR'):
                    p=dict(family=family,N=n,fill=fill,orientation=orientation,states=list(range(1<<len(c['ports']))),output='qualification')
                    r=job(p);folder=ROOT/'qualification'/f'N{n:06d}'/f'{family}_{fill:+d}'/orientation
                    actual={row['state']:sorted(read_binary(folder/row['file'])) for row in r['rows']}
                    if n==12:
                        if expected is None:expected=j.ve_rows(j.full_source(c['source'],fill),c['ports'],j.limits({}))[0]
                        if actual!=expected:raise ArithmeticError('Independent direct joint VE differs')
                    else:
                        from math_core import b,o
                        plan=b.plan(c,fill);tables={p['table_key']:b.cpu_local(p) for p in plan['pieces']}
                        parts=o.components(plan,tables,orientation=='K_MAJOR');expected={}
                        def sink(pl,state,entries):
                            expected[state]=sorted((ec-fill*((2*k-n)**2-n)//2,2*k-n,count) for k,ec,count in entries)
                        o.global_spectra(plan,parts,orientation,sink)
                        if actual!=expected:raise ArithmeticError('Uncompressed component reference differs')
                    if previous is not None:
                        if [a['joint_row_sha256'] for a in previous]!=[a['joint_row_sha256'] for a in r['rows']]:raise ArithmeticError('Binary canonical encoding digest differs')
                    previous=r['rows'];checks.append(dict(N=n,family=family,fill=fill,orientation=orientation,rows=len(r['rows'])))
    # Truncation is rejected by the consumer, not silently accepted as a shorter table.
    path=ROOT/'qualification/truncated.bin';original=next((ROOT/'qualification/N000012').rglob('*.bin')).read_bytes();path.write_bytes(original[:-1])
    try:list(read_binary(path))
    except ValueError:checks.append(dict(truncated_binary_rejected=True))
    else:raise ArithmeticError('Truncated binary accepted')
    return dict(status='PASS',checks=checks,runtime=runtime.verify(),resources=resources(),implementation_sha256=sha(P/'engine.py'),math_core_sha256=sha(P/'math_core.py'))


def gpu_prepare():
    processes=[]
    for gpu in (0,1):
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),N2000_GPU_INDEX=str(gpu))
        processes.append(subprocess.Popen([sys.executable,str(P/'gpu_probe.py')],env=env))
    for process in processes:
        if process.wait()!=0:raise RuntimeError('GPU local preparation failed')
    results=[json.loads((ROOT/f'GPU_{gpu}.json').read_text()) for gpu in (0,1)]
    catalog={r['table_key']:r for d in results for r in d['tables']};atomic(ROOT/'GPU_TABLES.json',catalog)
    return dict(status='PASS',results=results,tables=len(catalog))


def benchmark():
    trials=[]
    for workers,threads in ((7,4),(14,2),(28,1)):
        jobs=[];output=f'benchmark/w{workers}_t{threads}'
        # Identical 28 row calculations in every topology, distinct checkpoint names.
        for i in range(28):
            jobs.append(dict(family='signed_packet',N=750,fill=-1,orientation='K_MAJOR' if i%2 else 'T_MAJOR',states=[i%16],output=f'{output}/job{i:02d}'))
        result=batch(jobs,workers,threads,output);trials.append(result)
        atomic(ROOT/'BENCHMARK_PROGRESS.json',trials)
    signatures=[]
    for trial in trials:
        signature={}
        for result in trial['jobs']:
            for row in result['rows']:
                key=(result['payload']['orientation'],row['state'])
                if key in signature and signature[key]!=row['joint_row_sha256']:raise ArithmeticError('Repeated benchmark row differs')
                signature[key]=row['joint_row_sha256']
        signatures.append(signature)
    if any(s!=signatures[0] for s in signatures[1:]):raise ArithmeticError('Topology changes exact rows')
    winner=min(trials,key=lambda r:r['seconds'])
    return dict(status='PASS',trials=trials,selected=dict(workers=winner['workers'],threads=winner['threads']),
                note='Source-derived N750 full row staging/flush panel; confirm memory with N2000 pilot')


def pilot():
    jobs=[dict(family='signed_packet',N=2000,fill=-1,orientation=o,states=[0],output='pilot') for o in ('K_MAJOR','T_MAJOR')]
    result=batch(jobs,2,1,'pilot')
    a,b=result['jobs']
    if a['rows'][0]['joint_row_sha256']!=b['rows'][0]['joint_row_sha256']:raise ArithmeticError('N2000 pilot encodings differ')
    return result


def assemble():
    manifests=[]
    for family in C['families']:
        for fill in (1,-1):
            c,identity=source(family,2000,fill);folder=ROOT/'results/N002000'/f'{family}_{fill:+d}';rows=[]
            for state in range(1<<len(c['ports'])):
                pair=[]
                for orientation in ('K_MAJOR','T_MAJOR'):
                    p=folder/orientation/f'boundary_{state:04d}.json'
                    if not p.exists():return dict(status='CHECKPOINTED',completed_manifests=manifests,missing=str(p))
                    row=json.loads(p.read_text())
                    if row['source_identity']!=identity or row['implementation_sha256']!=sha(P/'engine.py') or row['math_core_sha256']!=sha(P/'math_core.py'):
                        raise ValueError('Row source or implementation binding differs')
                    if (folder/orientation/row['file']).stat().st_size!=row['bytes']:raise ValueError('Row size differs')
                    pair.append(row)
                for key in ('joint_row_sha256','records','moments','plan_sha256'):
                    if pair[0][key]!=pair[1][key]:raise ArithmeticError('Independent exact encodings disagree: '+key)
                rows.append(dict(state=state,primary='K_MAJOR/'+pair[0]['file'],reference='T_MAJOR/'+pair[1]['file'],
                    primary_sha256=pair[0]['sha256'],reference_sha256=pair[1]['sha256'],
                    joint_row_sha256=pair[0]['joint_row_sha256'],records=pair[0]['records'],moments=pair[0]['moments']))
            moments=[sum(int(r['moments'][k]) for r in rows) for k in range(3)]
            s=c['source'];n=s['N'];square_sum=n*(n-1)//2*fill*fill+sum(q*q-fill*fill for u,v,q in s['edges'])+sum(h*h for h in s['fields'])
            if moments!=[1<<n,0,(1<<n)*square_sum]:raise ArithmeticError('Global density/moment closure')
            manifest=dict(schema='EXACT_JOINT_BINARY_MANIFEST_V1',status='EXACT_JOINT_VERIFIED',N=n,family=family,fill=fill,
                ordered_ports=c['ports'],source_identity=identity,rows=rows,count_bytes=(n+8)//8,
                energy_convention='E=-sum Juv*su*sv-sum hi*si',magnetization_convention='M=sum si',
                binary_reader='project/engine.py:read_binary',configuration_count=str(1<<n),energy_moments=[str(m) for m in moments],
                canonical_digest='SHA256(N,state, concatenated k-bucket SHA256 of Ec:int64LE,count:unsignedLE)',
                verification=dict(independent_global_encodings=True,conditional_magnetization_binomials=True,
                    conditional_and_global_energy_moments=True,ram_to_container_sha256_readback=True),
                local_table_provenance=dict(gpu_verified_tables=sha(ROOT/'GPU_TABLES.json')))
            atomic(folder/'MANIFEST.json',manifest);manifests.append(dict(path=str(folder/'MANIFEST.json'),sha256=sha(folder/'MANIFEST.json')))
    return dict(status='COMPLETE',manifests=manifests,exact_joint_cases=len(manifests))


def production():
    qualified=json.loads((ROOT/'QUALIFY.json').read_text());pilot_result=json.loads((ROOT/'PILOT.json').read_text())
    if qualified['status']!='PASS' or qualified['implementation_sha256']!=sha(P/'engine.py') or qualified['math_core_sha256']!=sha(P/'math_core.py'):
        raise ValueError('Current implementation qualification required')
    if pilot_result['status']!='PASS':raise ValueError('N2000 memory pilot required')
    measurements=json.loads((ROOT/'BENCHMARK.json').read_text());r=resources()
    worker_estimate=max(2*1024**3,int(pilot_result['peak_worker_rss_kib']*1024*1.5))
    memory_budget=int(r['memory_limit_bytes']*C['memory_fraction'])-r['memory_current_bytes']
    eligible=[trial for trial in measurements['trials'] if trial['workers']*worker_estimate<=memory_budget
              and trial['workers']*trial['threads']<=math.ceil(r['cpu_equivalents'])]
    if not eligible:raise RuntimeError('No measured topology fits N2000 worker memory')
    winner=min(eligible,key=lambda trial:trial['seconds'])
    selected={k:winner[k] for k in ('workers','threads')}
    workers=selected['workers']
    if workers<1:raise RuntimeError('No admitted worker memory')
    policy=dict(workers=workers,threads=selected['threads'],measured_topology=selected,
        per_worker_estimate_bytes=worker_estimate,resources=r,rows_per_job=2,storage='RAM_THEN_CONTAINER_DISK_ONLY')
    atomic(ROOT/'PRODUCTION_POLICY.json',policy)
    jobs=[]
    # Larger correction sources first, leaving inexpensive cases to fill the tail.
    for fill in (-1,1):
        for family in C['families']:
            c,_=source(family,2000,fill)
            for begin in range(0,1<<len(c['ports']),2):
                for orientation in ('K_MAJOR','T_MAJOR'):
                    jobs.append(dict(family=family,N=2000,fill=fill,orientation=orientation,
                        states=list(range(begin,min(begin+2,1<<len(c['ports'])))),output='results'))
    # Import completed binary pilot rows by authenticated file copy within this
    # container, avoiding repeat arithmetic. Their original receipts remain.
    pilot_root=ROOT/'pilot/N002000/signed_packet_-1'
    for orientation in ('K_MAJOR','T_MAJOR'):
        target=ROOT/'results/N002000/signed_packet_-1'/orientation;target.mkdir(parents=True,exist_ok=True)
        for name in ('boundary_0000.bin','boundary_0000.json'):
            src=pilot_root/orientation/name;dst=target/name
            if not dst.exists():os.link(src,dst)
    result=batch(jobs,workers,selected['threads'],'results')
    result.update(policy=policy,assembly=assemble())
    result['status']=result['assembly']['status']
    return result


class Adapter:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_N2000_POD_GPU_PREPARE':return gpu_prepare()
        if op=='GEN4_N2000_POD_QUALIFY':return qualification()
        if op=='GEN4_N2000_POD_BENCHMARK':return benchmark()
        if op=='GEN4_N2000_POD_PILOT':return pilot()
        if op=='GEN4_N2000_POD_PRODUCE':return production()
        if op=='GEN4_N2000_POD_BATCH':return batch(**payload)
        return self.base.execute(op,payload)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['gpu_prepare','qualify','benchmark','pilot','produce']);a=ap.parse_args()
    ROOT.mkdir(parents=True,exist_ok=True);RAM.mkdir(parents=True,exist_ok=True)
    lock=(ROOT/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if a.action=='produce':
        def stop(*_):(ROOT/'STOP').touch()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    with DomainSession.start('MATTER_SEARCH',objective='N2000 exact joint spectra: CPU process topology, verified CUDA local operators, RAM-staged binary container custody',output_root=ROOT/'sessions',receipt_storage='gzip') as session:
        print(session.announcement(),flush=True);session.consumer=Adapter(session.consumer)
        result=session.execute('GEN4_N2000_POD_'+a.action.upper(),{},purpose='Qualify and measure the actual source-bound exact pipeline on this pod')
        result['session']=str(session.directory);atomic(ROOT/f'{a.action.upper()}.json',result)
        print(json.dumps(dict(action=a.action,status=result['status'],session=result['session'])),flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        atomic(ROOT/f'FAILURE_{time.time_ns()}.json',dict(traceback=traceback.format_exc()));raise
