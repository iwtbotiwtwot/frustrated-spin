import json, os, re, shutil, subprocess
from pathlib import Path
import cupy as cp

expected = 20
inventory = subprocess.check_output(['nvidia-smi', '-L'], text=True)
mig = re.findall(r'UUID: (MIG-[^)]+)', inventory)
visible = cp.cuda.runtime.getDeviceCount()
assert len(mig) >= expected, (len(mig), 'MIG instances in nvidia-smi -L')
assert visible >= expected, (visible, 'CUDA devices visible to CuPy')
for i in range(expected):
    with cp.cuda.Device(i):
        free, total = cp.cuda.runtime.memGetInfo()
        assert free > 4 * 1024**3, (i, free, total)

cpu_quota = Path('/sys/fs/cgroup/cpu.max').read_text().strip()
memory_limit = Path('/sys/fs/cgroup/memory.max').read_text().strip()
memory_current = int(Path('/sys/fs/cgroup/memory.current').read_text())
shm = shutil.disk_usage('/dev/shm')
assert memory_limit == 'max' or int(memory_limit) - memory_current > 8 * 1024**3
assert shm.free > 8 * 1024**3

durable = Path('/workspace/gen4/runs/frustrated-spin-n96-h14t18-20gpu-test1')
durable.mkdir(parents=True, exist_ok=True)
probe = durable / '.write_probe'
with probe.open('wb') as f:
    f.write(b'GEN4 N96 H14F/T18 durable checkpoint probe\n')
    f.flush(); os.fsync(f.fileno())
probe.unlink()

print(json.dumps({
    'status':'PASS', 'requested_workers':expected,
    'mig_instances':len(mig), 'cuda_visible_devices':visible,
    'free_vram_bytes_by_device':[int(cp.cuda.Device(i).mem_info[0]) for i in range(expected)],
    'cpu_max':cpu_quota, 'memory_limit_bytes':memory_limit,
    'memory_current_bytes':memory_current,
    'dev_shm_free_bytes':shm.free, 'durable_volume_write_probe':'PASS',
    'source_instance':'625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d'
}, indent=2))
