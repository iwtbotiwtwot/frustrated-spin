"""Portable, source-bound N2000 reproduction and retained-record checks."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent

def load(path):
    return json.loads(Path(path).read_text())

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def verify_record():
    config = load(HERE/'CONFIG.json')
    for name, digest in config['source_files'].items():
        if sha(HERE/'inputs/N002000'/name) != digest:
            raise ValueError('Input hash mismatch: '+name)
    cases = sorted((HERE/'reference/results/N002000').glob('*/MANIFEST.json'))
    if len(cases) != 6:
        raise ValueError('Expected six scientific manifests')
    total = 0
    for path in cases:
        manifest = load(path)
        if manifest['status'] != 'EXACT_JOINT_VERIFIED' or len(manifest['rows']) != 16:
            raise ValueError('Incomplete retained case')
        if {r['state'] for r in manifest['rows']} != set(range(16)):
            raise ValueError('Incomplete boundary coverage')
        for row in manifest['rows']:
            for orientation, field in (('K_MAJOR','primary'),('T_MAJOR','reference')):
                receipt = load(path.parent/orientation/f"boundary_{row['state']:04d}.json")
                for key in ('joint_row_sha256','records','moments'):
                    if receipt[key] != row[key]:
                        raise ValueError('Retained encoding disagreement')
                if receipt['sha256'] != row[field+'_sha256']:
                    raise ValueError('Retained binary hash disagreement')
                if int(receipt['moments'][0]) != 1 << 1996:
                    raise ValueError('Conditional configuration count')
            total += row['records']
        if sum(int(row['moments'][0]) for row in manifest['rows']) != 1 << 2000:
            raise ValueError('Global configuration count')
    print(json.dumps(dict(status='PASS',cases=6,boundaries=96,independent_encoding_rows=192,
                          primary_records=total,bulk_files_read=0)))

def verify_results(work, output='results'):
    checked = 0
    for path in sorted((work/output/'N002000').glob('*/*/boundary_*.json')):
        reference = HERE/'reference/results/N002000'/path.relative_to(work/output/'N002000')
        expected, actual = load(reference), load(path)
        for key in ('sha256','joint_row_sha256','records','bytes','moments','source_identity','plan_sha256'):
            if actual[key] != expected[key]:
                raise ValueError(f'Reproduction differs: {path}: {key}')
        if sha(path.with_suffix('.bin')) != expected['sha256']:
            raise ValueError('Reproduced binary differs: '+str(path))
        checked += 1
    target = 32 if output == 'smoke' else 192
    if checked != target:
        raise ValueError(f'Expected {target} rows; verified {checked}')
    print(json.dumps(dict(status='PASS',reproduced_rows=checked,binary_sha256_matches=True)))

def fetch_runtime(destination):
    record = load(HERE/'RUNTIME.json')['assets'][0]
    destination.mkdir(parents=True,exist_ok=True)
    archive = destination/record['filename']
    if not archive.exists() or sha(archive) != record['sha256']:
        partial = archive.with_suffix(archive.suffix+'.part')
        subprocess.run(['curl','--fail','--location','--retry','3',record['url'],'--output',str(partial)],check=True)
        if sha(partial) != record['sha256']:
            raise ValueError('Released runtime SHA256 mismatch')
        partial.replace(archive)
    if (destination/'runtime').exists():
        raise ValueError('Runtime directory already exists; use a fresh destination')
    with tarfile.open(archive) as stream:
        stream.extractall(destination,filter='data')
    supplement_runtime(destination/'runtime')
    print(destination/'runtime')

def install_runtime_licenses(root):
    """Carry the scoped open grant with the otherwise unchanged frozen runtime."""
    target = Path(root)/'PUBLIC_LICENSES'
    for record in load(HERE/'LICENSE_BUNDLE.json')['files']:
        source = HERE/record['source']
        if sha(source) != record['sha256']:
            raise ValueError('Runtime license bundle hash mismatch')
        target.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target/record['filename'])


def supplement_runtime(root):
    install_runtime_licenses(root)
    for record in load(HERE/'RUNTIME_SUPPLEMENT.json')['files']:
        source=HERE/record['path'];target=root/record['destination']
        if sha(source)!=record['sha256']:
            raise ValueError('Runtime supplement source hash mismatch')
        if target.exists():
            if sha(target)!=record['sha256']:
                raise ValueError('Existing runtime foundation differs; use a fresh runtime')
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('verify-record','fetch-runtime','prepare','qualify','smoke','pilot','produce','verify-results'))
    parser.add_argument('--runtime',type=Path)
    parser.add_argument('--work-dir',type=Path,default=Path('runs/n2000'))
    parser.add_argument('--ram-dir',type=Path,default=Path('/dev/shm/spin-n2000'))
    parser.add_argument('--destination',type=Path,default=Path('runs/n2000-runtime'))
    parser.add_argument('--workers',type=int,default=0,help='Production workers; zero chooses from measured pilot memory')
    parser.add_argument('--threads',type=int,default=2)
    args=parser.parse_args()
    if args.action=='verify-record':
        return verify_record()
    if args.action=='fetch-runtime':
        return fetch_runtime(args.destination.resolve())
    work=args.work_dir.resolve()
    if args.action=='verify-results':
        return verify_results(work)
    if not args.runtime or not (args.runtime/'CURRENT_REVISION/runtime.py').is_file():
        parser.error('--runtime must name the extracted public runtime directory')
    supplement_runtime(args.runtime.resolve())
    if args.workers<0 or args.threads<1:
        parser.error('workers must be nonnegative and threads must be positive')
    if work.is_relative_to(HERE):
        parser.error('Use a separate work directory outside the published reproduction record')
    ram=args.ram_dir.resolve()
    for key,value in dict(SPIN_WORK=str(work),SPIN_RAM=str(ram),SPIN_RUNTIME=str(args.runtime.resolve()),
                          SPIN_WORKERS=str(args.workers),SPIN_THREADS=str(args.threads),
                          OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1').items():
        os.environ[key]=value
    work.mkdir(parents=True,exist_ok=True);ram.mkdir(parents=True,exist_ok=True)
    lock=(work/'controller.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (work/'STOP').exists():
        raise ValueError('STOP exists. Remove it deliberately before resuming.')
    import controller as c
    from SAM_PROJECT.session import DomainSession
    from CURRENT_REVISION import runtime
    runtime.verify()
    signal.signal(signal.SIGTERM,lambda *_:(work/'STOP').touch())
    signal.signal(signal.SIGINT,lambda *_:(work/'STOP').touch())
    action='gpu_prepare' if args.action=='prepare' else args.action
    if args.action in ('pilot','produce'):
        limits=c.resources()
        if limits['memory_available_bytes'] < 28*1024**3:
            raise RuntimeError('N2000 pilot measured about 19 GiB per worker; allow at least 28 GiB available for its 1.5x admission estimate')
        if limits['ram_staging_free_bytes'] < 3*1024**3:
            raise RuntimeError('At least 3 GiB of RAM staging is required for the pilot')
    if args.action=='produce' and not (work/'GPU_TABLES.json').exists():
        raise ValueError('Run prepare first to bind exact local tables')
    with DomainSession.start('MATTER_SEARCH',objective='Reproduce exact published N2000 g(E,M,b) from frozen graph sources',
                             output_root=work/'sessions',receipt_storage='gzip') as session:
        print(session.announcement(),flush=True)
        session.consumer=c.Adapter(session.consumer)
        if args.action=='smoke':
            jobs=[dict(family='packet',N=2000,fill=1,orientation=o,states=list(range(16)),output='smoke') for o in ('K_MAJOR','T_MAJOR')]
            result=session.execute('GEN4_N2000_POD_BATCH',dict(jobs=jobs,workers=1,threads=1,output='smoke'),purpose='Fresh exact N2000 packet/+1 computation against published binary hashes')
            verify_results(work,'smoke')
        else:
            result=session.execute('GEN4_N2000_POD_'+action.upper(),{},purpose='Source-bound exact portable N2000 reproduction')
        result['session']=str(session.directory)
        c.atomic(work/(args.action.upper()+'.json'),result)
        print(json.dumps(dict(action=args.action,status=result['status'],session=result['session'])),flush=True)
    if args.action=='produce' and result['status']=='COMPLETE':
        verify_results(work)

if __name__=='__main__':
    main()
