from pathlib import Path
import subprocess,json,os,hashlib,datetime
import cupy as cp,numpy,flint
P=Path('/opt/gen4/restore14');n=cp.cuda.runtime.getDeviceCount();assert n==14
vram=[]
for d in range(n):
 with cp.cuda.Device(d):free,total=cp.cuda.runtime.memGetInfo();assert free>20*1024**3;vram.append(dict(device=d,free=free,total=total))
source_checks={}
for n in range(97,120):
 for f in ['SOURCE.json','PLAN.json']:
  a=Path(f'/opt/gen4/spin-gap-97-119-1/N{n}/{f}');b=Path(f'/opt/gen4/spin-atlas/inputs/spin-gap-97-119-1/frozen_sources/N{n}/{f}');source_checks[f'N{n}/{f}']=json.loads(a.read_text())==json.loads(b.read_text())
assert all(source_checks.values())
canonical={f.name:hashlib.file_digest(f.open('rb'),'sha256').hexdigest() for f in Path('/opt/gen4/spin-atlas/canonical').glob('N*.json')};assert len(canonical)==120
files={}
for folder in ['/opt/gen4/spin-focused1','/opt/gen4/spin-catalog1','/opt/gen4/spin-n120-frontier1']:
 for f in Path(folder).glob('*.py'):files[str(f)]=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
config=dict(status='RESTORED_AND_QUALIFIED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtime='/opt/gen4/current',gpu_workers=14,cpu_role='shared coordinator, preparation and exact batched reconstruction',cpu_threads_per_library=1,cpu_quota=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),memory_max_bytes=int(Path('/sys/fs/cgroup/memory.max').read_text()),historical_cpu_equivalents=47.6,historical_memory_bytes=880000000000,hardware_allocation_identical=False,hardware_difference='Current 95.2 CPU equivalents/439 GB RAM; prior 47.6/880 GB. Same GPU class and 14 MIG worker count.',vram=vram,versions=dict(cupy=cp.__version__,numpy=numpy.__version__,flint=flint.__version__),gap_source_plan_checks=source_checks,canonical_hashes=canonical,engine_hashes=files,qualification=json.loads((P/'QUALIFICATION.json').read_text()),process_policy='One exact experiment owns all14 GPUs. Original shared task queue, persistent per-device owners, cached maps, 16-root batches, batched NTT/CRT. No eight-CPU-job pool.',storage='Container code; RAM/VRAM arithmetic; compact durable archives; no repeated full-tree volume rsync.',research_controller='/opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun3/controller.py')
(P/'CONFIGURATION.json').write_text(json.dumps(config,indent=2)+'\n');print(json.dumps(dict(status=config['status'],canonical_entries=len(canonical),gap_checks=len(source_checks),gpu_workers=14)))
