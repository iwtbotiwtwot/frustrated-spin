"""GEN4 domain benchmark: exact GPU N96, CPU fiber, RAM-first checkpoints."""
import argparse,hashlib,json,os,subprocess,sys,time,tarfile,shutil
from pathlib import Path
from SAM_PROJECT.session import DomainSession
from monitor import Monitor
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

class Spin:
 def __init__(self,base,ram):self.base=base;self.ram=ram
 def close(self):self.base.close()
 def execute(self,operation,payload):
  if operation!='GEN4_N96_GPU_FIBER_BENCHMARK':return self.base.execute(operation,payload)
  assert payload['source_instance']=='625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d'
  run=self.ram/payload['run'];assert not run.exists();t=time.perf_counter()
  monitor=Monitor().start()
  with (self.ram/(payload['run']+'.log')).open('x') as log:
   subprocess.run([sys.executable,str(P/'runner.py'),str(run),str(payload['batch']),str(payload['workers']),str(payload['visible_cuda_devices'])],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
  monitor.stop(self.ram/(payload['run']+'-telemetry.json'))
  v=json.loads((run/'RESULT.json').read_text());v['startup_inclusive_seconds']=time.perf_counter()-t
  v['adapter_sha256']=sha(P/'runner.py');v['ram_result']=str(run);return v

def checkpoint(ram,durable,name):
 t=time.perf_counter();dest=durable/(name+'.tar.gz');tmp=dest.with_suffix('.part')
 with tarfile.open(tmp,'w:gz',compresslevel=1) as f:f.add(ram,arcname='ram_results')
 with tmp.open('rb') as f:os.fsync(f.fileno())
 tmp.rename(dest)
 fd=os.open(durable,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 v={'archive':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest),'flush_seconds':time.perf_counter()-t}
 save(durable/(name+'.json'),v);return v

def main():
 a=argparse.ArgumentParser();a.add_argument('--ram',type=Path,required=True);a.add_argument('--durable',type=Path,required=True);a.add_argument('--runs',default='20:16');args=a.parse_args()
 args.ram.mkdir(parents=True,exist_ok=False);args.durable.mkdir(parents=True,exist_ok=True)
 prior_failure=os.environ.get('GEN4_N96_PRIOR_FAILURE')
 if prior_failure and Path(prior_failure).is_file():shutil.copy2(prior_failure,args.ram/'PRIOR_ATTEMPT_FAILURE.json')
 os.environ['GEN4_N96_BULK']=str(args.ram);os.environ['CUPY_CACHE_DIR']=str(args.ram/'cupy-cache')
 memory_limit=int(Path('/sys/fs/cgroup/memory.max').read_text());assert memory_limit>16*1024**3
 import cupy as cp
 visible=cp.cuda.runtime.getDeviceCount()
 requested=max(int(x.split(':')[0]) for x in args.runs.split(','))
 assert visible>=requested,(visible,requested)
 preflight={'memory_limit_bytes':memory_limit,'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'visible_cuda_devices':visible,'requested_gpu_workers':requested,'storage':'tmpfs RAM for active state; one compressed durable checkpoint after the exact run','source_instance':'625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d','atlas_lineage':'separate source-bound historical dense N96 instance; not substituted for current canonical N96'}
 save(args.ram/'PREFLIGHT.json',preflight)
 s=DomainSession.start('MATTER_SEARCH',objective='Fresh exact source-bound N96 H14F/T18 run: one worker on each of 20 visible GPU devices; CPU NTT/CRT and directional-fiber closure',output_root=args.ram/'sessions',receipt_storage='gzip')
 print(json.dumps(s.manifest),flush=True);assert s.manifest['global_slc']=='SLC-GEN4-P1';s.consumer=Spin(s.consumer,args.ram)
 rows=[]
 try:
  for i,config in enumerate(args.runs.split(',')):
   workers,batch=map(int,config.split(':'));name=f'run{i+1:02d}_w{workers}_b{batch}'
   v=s.execute('GEN4_N96_GPU_FIBER_BENCHMARK',{'source_instance':preflight['source_instance'],'run':name,'workers':workers,'batch':batch,'visible_cuda_devices':visible},purpose='Fresh exact N96 benchmark; preserve GPU root arithmetic and CPU T18 fiber')
   rows.append(v);save(args.ram/'BENCHMARK.json',rows)
   print(json.dumps({'run':name,'result':v}),flush=True)
  save(args.ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Retain benchmark session native state'))
 finally:s.close()
 save(args.ram/'COMPLETE.json',{'status':'COMPLETE','runs':len(rows),'session':str(s.directory)})
 final_checkpoint=checkpoint(args.ram,args.durable,'complete')
 save(args.durable/'COMPLETE.json',{'status':'COMPLETE','runs':len(rows),'session':str(s.directory),'archive':final_checkpoint})
 print(json.dumps({'complete':True,'checkpoint':final_checkpoint}),flush=True)
if __name__=='__main__':main()
