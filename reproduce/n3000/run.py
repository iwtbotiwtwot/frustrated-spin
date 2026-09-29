"""Verify all retained N3000 rows; cheaply recompute packet/+1 on CPU."""
import argparse, fcntl, hashlib, importlib.util, json, os, struct, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def reference():return load(HERE/'reference/PRODUCE.json')
def verify_record():
    config=load(HERE/'CONFIG.json')
    for name,digest in config['source_files'].items():
        if sha(HERE/'inputs/N003000'/name)!=digest:raise ValueError('Source hash: '+name)
    for name,digest in load(HERE/'RECORD_SHA256.json').items():
        if sha(HERE/name)!=digest:raise ValueError('Retained record hash: '+name)
    result=reference()
    if result['status']!='PASS' or result['reason']!='COMPLETE':raise ValueError('Incomplete result')
    rows={(r['case']['family'],r['case']['fill'],r['state'],r['case']['orientation']):r for r in result['rows']}
    expected={(f,s,b,o) for f in config['families'] for s in [-1,1] for b in range(16) for o in ['K_MAJOR','T_MAJOR']}
    if len(result['rows'])!=192 or set(rows)!=expected:raise ValueError('Coverage')
    total=0
    for family in config['families']:
        for fill in [-1,1]:
            manifest=load(HERE/'inputs/N003000'/f'{family}_N003000_fill_{"plus" if fill==1 else "minus"}.json')
            for state in range(16):
                a,b=(rows[family,fill,state,o] for o in ['K_MAJOR','T_MAJOR'])
                for row in (a,b):
                    if row['case']['source_sha256']!=manifest['parent_source_sha256'] or row['case']['ports']!=manifest['ordered_ports']:raise ValueError('Source binding')
                    for name,digest in result['files'].items():
                        if sha(HERE/'gpu_source'/name)!=digest:raise ValueError('Production code binding')
                    if row['binding']['files']!=result['files']:raise ValueError('Row binding')
                    if int(row['gpu']['moments'][0])!=1<<2996:raise ValueError('Configuration count')
                    if row['gpu']['bytes']!=row['gpu']['records']*384:raise ValueError('Record width')
                for key in ['joint_row_sha256','records','moments']:
                    if a['gpu'][key]!=b['gpu'][key]:raise ValueError('Independent encoding mismatch')
                if a['case']['plan_sha256']!=b['case']['plan_sha256']:raise ValueError('Plan binding')
                total+=a['gpu']['records']
    answer=dict(status='PASS',source_files=len(config['source_files']),cases=6,boundaries=96,independent_encoding_rows=192,primary_records=total,bulk_files_read=0)
    print(json.dumps(answer),flush=True);return answer

def runtime_helper():
    spec=importlib.util.spec_from_file_location('n2000_runtime',HERE.parent/'n2000/run.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def verify_smoke(work):
    refs={(r['case']['orientation'],r['state']):r for r in reference()['rows'] if r['case']['family']=='packet' and r['case']['fill']==1}
    paths=sorted((work/'smoke/N003000/packet_+1').glob('*/boundary_*.json'))
    if len(paths)!=32:raise ValueError('Expected 32 fresh rows')
    for p in paths:
        actual=load(p);expected=refs[p.parent.name,actual['state']];g=expected['gpu']
        for key in ['joint_row_sha256','records','moments']:
            if actual[key]!=g[key]:raise ValueError(f'Replay mismatch {p}: {key}')
        if actual['plan_sha256']!=expected['case']['plan_sha256']:raise ValueError('Replay plan')
        if actual['source_identity']['parent_source_sha256']!=expected['case']['source_sha256']:raise ValueError('Replay source')
        binary=p.with_suffix('.bin')
        if sha(binary)!=actual['sha256']:raise ValueError('Replay file checksum')
        with binary.open('rb') as f:
            if f.read(8)!=b'GEMB001\n':raise ValueError('Replay header')
            length=struct.unpack('<I',f.read(4))[0];header=json.loads(f.read(length))
            if header['count_bytes']!=376:raise ValueError('Count width')
            if hashlib.file_digest(f,'sha256').hexdigest()!=g['binary_data_sha256']:raise ValueError('Raw records differ from GPU')
    return dict(status='PASS',reproduced_rows=32,case='packet/+1',canonical_and_raw_record_hashes_match=True)

def clean(v):
    if isinstance(v,float):return format(v,'.17g')
    if isinstance(v,list):return [clean(x) for x in v]
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    return v

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['verify-record','fetch-runtime','smoke','verify-results'])
    ap.add_argument('--runtime',type=Path);ap.add_argument('--work-dir',type=Path,default=Path('runs/n3000'));ap.add_argument('--destination',type=Path,default=Path('runs/n2000-runtime'))
    a=ap.parse_args()
    if a.action=='verify-record':return verify_record()
    if a.action=='fetch-runtime':return runtime_helper().fetch_runtime(a.destination.resolve())
    work=a.work_dir.resolve()
    if a.action=='verify-results':print(json.dumps(verify_smoke(work)));return
    verify_record()
    if not a.runtime or not (a.runtime/'CURRENT_REVISION/runtime.py').is_file():ap.error('--runtime must name the public runtime')
    if work.is_relative_to(HERE):ap.error('Use a separate work directory')
    runtime_helper().supplement_runtime(a.runtime.resolve())
    for k,v in dict(SPIN_RUNTIME=str(a.runtime.resolve()),SPIN_WORK=str(work),SPIN_RAM=str(work/'staging'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1').items():os.environ[k]=v
    work.mkdir(parents=True,exist_ok=True);lock=(work/'controller.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (work/'smoke').exists():ap.error('Use a fresh work directory for the measured replay')
    import engine
    from SAM_PROJECT.session import DomainSession
    from CURRENT_REVISION import runtime
    from CURRENT_REVISION.engines.SLC.gen3 import retained
    verified=runtime.verify();engine.initialize(1,None)
    binding={name:sha(HERE/name) for name in ['run.py','engine.py','math_core.py','CONFIG.json','RECORD_SHA256.json']}
    class Adapter:
        def __init__(self,base):self.base=base
        def close(self):self.base.close()
        def execute(self,op,payload):
            if op!='N3000_CHEAP_REPLAY':return self.base.execute(op,payload)
            if payload!=binding:raise ValueError('Adapter source binding')
            start=time.perf_counter()
            jobs=[engine.job(dict(family='packet',N=3000,fill=1,orientation=o,states=list(range(16)),output='smoke')) for o in ['K_MAJOR','T_MAJOR']]
            seconds=time.perf_counter()-start;check=verify_smoke(work)
            result=dict(**check,compute_seconds=seconds,jobs=jobs,runtime=verified,binding=binding)
            rt=self.base.ce.runtime_for('MATTER_SEARCH');ref=retained.put(rt.machine,'mathematical_result',clean(result),{'campaign':'n3000_cheap_replay'},{'origin':'SOURCE_BOUND_ADAPTER','request':payload},[])
            return dict(result_ref=ref,result=clean(result))
    with DomainSession.start('MATTER_SEARCH',objective='Fresh exact N3000 packet/+1 CPU replay against completed GPU results',output_root=work/'sessions',receipt_storage='gzip') as session:
        print(session.announcement(),flush=True);session.consumer=Adapter(session.consumer)
        result=session.execute('N3000_CHEAP_REPLAY',binding,purpose='Recompute all 16 boundaries in both encodings and compare exact records with N3000 production')
        engine.atomic(work/'SMOKE.json',result)
        print(json.dumps({k:v for k,v in result['result'].items() if k!='jobs'}),flush=True)

if __name__=='__main__':main()
