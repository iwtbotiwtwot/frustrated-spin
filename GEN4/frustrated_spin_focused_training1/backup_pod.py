"""Checkpoint portable runtime/source dependencies without touching running jobs."""
from pathlib import Path
import tarfile,json,hashlib,subprocess,os
out=Path('/workspace/gen4/runs/spin-focused1/restart');out.mkdir(parents=True,exist_ok=True)
roster={'runtime-predecessor.tar.gz':('/opt/gen4/current','runtime'),'exact-source.tar.gz':('/opt/gen4/n96-benchmark1/source','source'),'catalog-code.tar.gz':('/opt/gen4/spin-catalog1','catalog-code'),'training-code.tar.gz':('/opt/gen4/spin-training1','training-code')}
records={}
for name,(folder,arcname) in roster.items():
    path=out/name
    with tarfile.open(path,'w:gz',compresslevel=1) as archive:
        archive.add(Path(folder).resolve(),arcname=arcname,filter=lambda info:None if '__pycache__' in info.name or info.name.endswith('.tar.gz') else info)
    with path.open('rb') as f:os.fsync(f.fileno())
    records[name]=dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest());print(name,records[name],flush=True)
(out/'ENVIRONMENT.txt').write_text(subprocess.check_output(['/opt/gen4/venv/bin/python','-m','pip','freeze'],text=True))
trace=Path('/opt/gen4/n72-benchmark1/activity.so');(out/'activity.so').write_bytes(trace.read_bytes());records['activity.so']=dict(bytes=trace.stat().st_size,sha256=hashlib.sha256(trace.read_bytes()).hexdigest())
(out/'MANIFEST.json').write_text(json.dumps(records,indent=2)+'\n')
