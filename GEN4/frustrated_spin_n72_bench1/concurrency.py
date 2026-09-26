"""Actual concurrent-kernel activity; not SM occupancy or sampled NVML utilization."""
from pathlib import Path
import json,tarfile,collections
P=Path(__file__).parent

def merge(spans):
 out=[]
 for a,b in sorted(spans):
  if out and a<=out[-1][1]:out[-1]=(out[-1][0],max(b,out[-1][1]))
  else:out.append((a,b))
 return out

def summary(spans,lo,hi):
 events=[];duties={}
 for d,rows in spans.items():
  rows=merge([(max(a,lo),min(b,hi)) for a,b in rows if a<hi and b>lo]);duties[d]=sum(b-a for a,b in rows)/(hi-lo)
  for a,b in rows:events.extend([(a,1),(b,-1)])
 hist=collections.Counter();active=0;prev=lo
 for t,delta in sorted(events):hist[active]+=t-prev;active+=delta;prev=t
 hist[active]+=hi-prev
 return {'window_seconds':hi-lo,'mean_active_gpus':sum(k*v for k,v in hist.items())/(hi-lo),'mean_gpu_busy_fraction':sum(duties.values())/14,'all14_busy_fraction':hist[14]/(hi-lo),'atleast13_busy_fraction':sum(v for k,v in hist.items() if k>=13)/(hi-lo),'busy_fraction_by_worker':duties,'active_count_seconds':dict(sorted(hist.items()))}

def analyze(name):
 out=P/'analysis'/name;out.mkdir(parents=True,exist_ok=True)
 with tarfile.open(P/name/'complete.tar.gz') as t:t.extractall(out,filter='data')
 root=out/'ram_results';r=next(root.glob('run*/RESULT.json'));v=json.loads(r.read_text());host=collections.defaultdict(list)
 for trial in v['trials']:
  for w in trial['workers']:host[w['gpu']].append((w['started_at'],w['ended_at']))
 lo=min(a for rows in host.values() for a,b in rows);hi=max(b for rows in host.values() for a,b in rows)
 kernels={};records=0
 for path in r.parent.glob('GPU*_KERNELS.csv'):
  lines=path.read_text().splitlines();meta=json.loads(lines[0]);assert meta['dropped']==0 and meta['records']==len(lines)-1
  d=int(path.name[3:].split('_')[0]);offset=meta['offset_ns'];kernels[d]=[];records+=meta['records']
  for line in lines[1:]:
   start,end,device,stream=map(int,line.split(','));kernels[d].append(((start+offset)/1e9,(end+offset)/1e9))
 assert len(kernels)==14
 midlo=min(w['started_at'] for t in v['trials'][2:-1] for w in t['workers']);midhi=max(w['ended_at'] for t in v['trials'][2:-1] for w in t['workers'])
 result={'name':name,'kernel_records':records,'zero_dropped_records':True,'host_service':summary(host,lo,hi),'actual_kernel_activity':summary(kernels,lo,hi),'steady_actual_kernel_activity':summary(kernels,midlo,midhi),'warm_pipeline_seconds':v['warm_pipeline_seconds'],'fresh_exact_solves':len(v['trials']),'scope':'Time fraction with at least one kernel executing on a worker; not SM occupancy. CUPTI timestamps aligned to host monotonic time per process.'}
 (P/(name+'_CONCURRENCY.json')).write_text(json.dumps(result,indent=2)+'\n')
 for k in ['host_service','actual_kernel_activity','steady_actual_kernel_activity']:
  print(name,k,{x:result[k][x] for x in ['window_seconds','mean_active_gpus','mean_gpu_busy_fraction','all14_busy_fraction','atleast13_busy_fraction']})
 return result
if __name__=='__main__':
 import sys
 analyze(sys.argv[1] if len(sys.argv)>1 else 'trace1')
