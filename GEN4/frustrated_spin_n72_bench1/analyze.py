"""Read retained outputs; verify custody and summarize monitored phase intervals."""
from pathlib import Path
import json,tarfile,hashlib,statistics,collections
P=Path(__file__).parent

def merge(xs):
 out=[]
 for a,b in sorted(xs):
  if out and a<=out[-1][1]:out[-1]=(out[-1][0],max(b,out[-1][1]))
  else:out.append((a,b))
 return out

def length(xs):return sum(b-a for a,b in merge(xs))
def intersect(a,b):return sum(max(0,min(y,v)-max(x,u)) for x,y in merge(a) for u,v in merge(b))
def stat(s):return {k:int(v) for k,v in (x.split() for x in s.splitlines())}
def io(s):return {x.split()[0]:{k:int(v) for k,v in (y.split('=') for y in x.split()[1:])} for x in s.splitlines()}
report={};all_hashes=set();solves=0;receipts=[]
for name in ['baseline1','pipeline1','pipeline2','pipeline3-b32','trace1','graph1']:
 checkpoint=P/name/'complete.json';custody=json.loads(checkpoint.read_text());archive=P/name/custody['archive']
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==custody['sha256']
 target=P/'analysis'/name;target.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive) as t:t.extractall(target,filter='data')
 root=target/'ram_results';v=json.loads((root/'BENCHMARK.json').read_text())[0]
 telemetry=json.loads(next(root.glob('*-telemetry.json')).read_text());a,b=telemetry[0],telemetry[-1]
 st0,st1=stat(a['cpu.stat']),stat(b['cpu.stat']);dt=b['monotonic']-a['monotonic'];i0,i1=io(a['io.stat']),io(b['io.stat'])
 row={'fresh_solves':len(v.get('trials',[v])),'outer_seconds':v['startup_inclusive_seconds'],'timed_solver_seconds':v['total_seconds'],'samples':len(telemetry),'cpu_seconds':(st1['usage_usec']-st0['usage_usec'])/1e6,'mean_cpu_cores':(st1['usage_usec']-st0['usage_usec'])/1e6/dt,'peak_host_GiB':max(int(x['memory.current']) for x in telemetry)/1024**3,'cpu_throttled_periods':st1['nr_throttled']-st0['nr_throttled'],'memory_event_delta':{k:stat(b['memory.events'])[k]-stat(a['memory.events'])[k] for k in stat(a['memory.events'])},'block_io_delta_by_device':{d:{k:i1[d][k]-r[k] for k in r} for d,r in i0.items()},'checkpoint':custody,'first_flush':json.loads(next((P/name).glob('run*.json')).read_text())}
 trials=v.get('trials',[v]);solves+=len(trials)
 for t in trials:
  assert t['configuration_count']==2**72 and t['bins']==263 and t['t18_checks_passed'];all_hashes.add(t['fixed_coefficient_sha256'])
 if name=='baseline1':
  row.update(source_setup_seconds=v['source_setup_seconds'],cpu_reconstruction_seconds=v['reconstruction_seconds'],fiber_seconds=v['fiber_seconds'],worker_setup_seconds=[min(w['device_setup_seconds'] for w in v['workers']),max(w['device_setup_seconds'] for w in v['workers'])],worker_active_seconds=[min(w['seconds'] for w in v['workers']),max(w['seconds'] for w in v['workers'])],peak_device_pool_GiB=max(w['pool_peak_bytes'] for w in v['workers'])/1024**3)
 else:
  gpu=[(w['started_at'],w['ended_at']) for t in trials for w in t['workers']];cpu=[(t['assembly_started'],t['assembly_finished']) for t in trials];origin=min(a for a,b in gpu)
  counts=collections.Counter(w['gpu'] for t in trials for w in t['workers']);assert set(counts)==set(range(14))
  idle=[]
  for d in counts:
   work=sorted((w['started_at'],w['ended_at']) for t in trials for w in t['workers'] if w['gpu']==d)
   idle.extend(max(0,work[i+1][0]-work[i][1]) for i in range(len(work)-1))
  row.update(initialization_seconds=v['initialization_seconds'],warm_all_results_seconds=v['warm_pipeline_seconds'],steady_latency_seconds=[t['total_seconds'] for t in trials[1:]],steady_latency_median=statistics.median(t['total_seconds'] for t in trials[1:]),input_bank_bytes=v['input_bank_bytes'],input_prepare_seconds=v['input_prepare_seconds'],fiber_prepare_seconds=v['fiber_prepare_seconds'],gpu_batch_counts=dict(counts),peak_device_pool_GiB=max(w['pool_bytes'] for t in trials for w in t['workers'])/1024**3,median_interbatch_gap_ms=1000*statistics.median(idle),max_interbatch_gap_ms=1000*max(idle),cpu_assembly_overlapped_by_gpu_service_fraction=intersect(gpu,cpu)/length(cpu),timeline=[{'trial':t['trial'],'gpu_start':min(w['started_at'] for w in t['workers'])-origin,'gpu_end':max(w['ended_at'] for w in t['workers'])-origin,'cpu_start':t['assembly_started']-origin,'cpu_end':t['assembly_finished']-origin} for t in trials])
 for r in root.glob('sessions/*/calls/*/RECEIPT.json'):
  rec=json.loads(r.read_text());assert rec['status']=='RETURNED';receipts.append({'path':str(r.relative_to(P)),'operation':rec['operation']})
 report[name]=row
assert len(all_hashes)==1
result={'solves':solves,'receipt_count':len(receipts),'receipts':receipts,'coefficient_sha256':all_hashes.pop(),'source_instance':'396778a771378af50f7f6cbe594d93245fb0b653aef3f7a91b142c1e51fe450b','runs':report,'recommended':'14 persistent GPU processes; batch32; 69-node exact CUDA graphs with two VRAM banks; demand queue; RAM factors; overlapping CPU reconstruction/fiber; defer shutdown until answer collection','measurement_scope':'CUDA stream event spans and host service intervals; these include launch gaps and are not hardware SM utilization percentages. Cgroup counters include the otherwise quiet container. Block devices may be layers of the same I/O; do not sum them.'}
(P/'ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
for name,row in report.items():print(name,json.dumps({k:row[k] for k in ['timed_solver_seconds','outer_seconds','peak_host_GiB','mean_cpu_cores','peak_device_pool_GiB']},indent=None));print('warm',row.get('warm_all_results_seconds'),'median',row.get('steady_latency_median'),'overlap',row.get('cpu_assembly_overlapped_by_gpu_service_fraction'),'idle_ms',row.get('median_interbatch_gap_ms'),'flush',row['first_flush']['flush_seconds'])
print('exact solves',solves,'receipts',len(receipts))
