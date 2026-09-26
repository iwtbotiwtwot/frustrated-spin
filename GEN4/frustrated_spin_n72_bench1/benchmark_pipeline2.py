"""GEN4 domain benchmark: exact GPU N72, CPU fiber, RAM-first checkpoints."""
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
  if operation!='GEN4_N72_DEMAND_PIPELINE_BENCHMARK':return self.base.execute(operation,payload)
  assert payload['source_instance']=='396778a771378af50f7f6cbe594d93245fb0b653aef3f7a91b142c1e51fe450b'
  run=self.ram/payload['run'];assert not run.exists();t=time.perf_counter()
  monitor=Monitor().start()
  with (self.ram/(payload['run']+'.log')).open('x') as log:
   subprocess.run([sys.executable,str(P/'gpu_pipeline2.py'),str(run),str(payload['workers']),str(payload['batch']),'4'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
  monitor.stop(self.ram/(payload['run']+'-telemetry.json'))
  v=json.loads((run/'RESULT.json').read_text());v['startup_inclusive_seconds']=time.perf_counter()-t
  v['adapter_sha256']=sha(P/'gpu_pipeline2.py');v['ram_result']=str(run);return v

def checkpoint(ram,durable,name):
 t=time.perf_counter();dest=durable/(name+'.tar.gz');tmp=dest.with_suffix('.part')
 with tarfile.open(tmp,'w:gz',compresslevel=1) as f:f.add(ram,arcname='ram_results')
 with tmp.open('rb') as f:os.fsync(f.fileno())
 tmp.rename(dest)
 fd=os.open(durable,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 v={'archive':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest),'flush_seconds':time.perf_counter()-t}
 save(durable/(name+'.json'),v);return v

def main():
 a=argparse.ArgumentParser();a.add_argument('--ram',type=Path,required=True);a.add_argument('--durable',type=Path,required=True);a.add_argument('--runs',default='14:16');args=a.parse_args()
 args.ram.mkdir(parents=True,exist_ok=False);args.durable.mkdir(parents=True,exist_ok=True)
 os.environ['GEN4_N72_BULK']=str(args.ram);os.environ['CUPY_CACHE_DIR']=str(args.ram/'cupy-cache')
 memory_limit=int(Path('/sys/fs/cgroup/memory.max').read_text());assert memory_limit>16*1024**3
 preflight={'memory_limit_bytes':memory_limit,'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'storage':'tmpfs RAM for active state; compressed durable checkpoint after each complete run','source_instance':'396778a771378af50f7f6cbe594d93245fb0b653aef3f7a91b142c1e51fe450b'}
 save(args.ram/'PREFLIGHT.json',preflight)
 s=DomainSession.start('MATTER_SEARCH',objective='Benchmark exact N72 with GPU workers and CPU directional fiber on the 14-MIG pod',output_root=args.ram/'sessions',receipt_storage='gzip')
 print(json.dumps(s.manifest),flush=True);assert s.manifest['global_slc']=='SLC-GEN4-P1';s.consumer=Spin(s.consumer,args.ram)
 rows=[]
 try:
  for i,config in enumerate(args.runs.split(',')):
   workers,batch=map(int,config.split(':'));name=f'run{i+1:02d}_w{workers}_b{batch}'
   v=s.execute('GEN4_N72_DEMAND_PIPELINE_BENCHMARK',{'source_instance':preflight['source_instance'],'run':name,'workers':workers,'batch':batch},purpose='Fresh exact N72 benchmark; preserve GPU root arithmetic and CPU T18 fiber')
   rows.append(v);save(args.ram/'BENCHMARK.json',rows)
   flush=checkpoint(args.ram,args.durable,name);print(json.dumps({'run':name,'result':v,'checkpoint':flush}),flush=True)
  save(args.ram/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Retain benchmark session native state'))
 finally:s.close()
 save(args.ram/'COMPLETE.json',{'status':'COMPLETE','runs':len(rows),'session':str(s.directory)})
 print(json.dumps(checkpoint(args.ram,args.durable,'complete')),flush=True)
if __name__=='__main__':main()
