import concurrent.futures,json,os,time
from pathlib import Path
import cupy as cp

def worker(i):
 with cp.cuda.Device(i):
  p=cp.cuda.runtime.getDeviceProperties(i);a=cp.arange(1024,dtype=cp.int64);v=int(cp.sum(a*a).get());assert v==sum(j*j for j in range(1024))
  free,total=cp.cuda.runtime.memGetInfo();return {'device':i,'name':p['name'].decode(),'bytes':total,'free_bytes':free,'multiprocessors':p['multiProcessorCount'],'compute':[p['major'],p['minor']],'exact_check':v}
if __name__=='__main__':
 n=cp.cuda.runtime.getDeviceCount();assert n==14
 with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:rows=list(pool.map(worker,range(n)))
 result={'devices':rows,'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_max_bytes':int(Path('/sys/fs/cgroup/memory.max').read_text()),'memory_current_bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'cpu_model':next(s for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'gpu_template':'14 MIG slices; CPU retains mathematical directional fiber','status':'PASS'}
 Path('/workspace/gen4/runs/n72-benchmark1/HARDWARE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
