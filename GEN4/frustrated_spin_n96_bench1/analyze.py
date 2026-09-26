from pathlib import Path
import sys,json,tarfile,hashlib,collections,statistics
P=Path(__file__).parent
NAME=sys.argv[1] if len(sys.argv)>1 else 'graph1'
RUN='run01_w14_b8' if NAME=='graph1' else 'run01_w14_b16'
BATCH=8 if NAME=='graph1' else 16
EXPECTED_JOBS=4096//BATCH
sys.path.insert(0,str(P.parent/'frustrated_spin_n72_bench1'))
from concurrency import summary
r=json.loads((P/NAME/'complete.json').read_text());archive=P/NAME/r['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['sha256']
out=P/'analysis'/NAME;out.mkdir(exist_ok=True)
with tarfile.open(archive) as t:t.extractall(out,filter='data')
ram=out/'ram_results';result=json.loads((ram/'BENCHMARK.json').read_text())[0];root=ram/RUN;profiles=json.loads((root/'BATCH_PROFILES.json').read_text())
assert int(result['configuration_count'])==2**96 and all(result['checks'].values()) and len(profiles)==EXPECTED_JOBS
seen=set();counts=collections.Counter();host=collections.defaultdict(list)
for p in profiles:
 pi,lo,hi=p['task'];assert (pi,lo,hi) not in seen;seen.add((pi,lo,hi));counts[p['gpu']]+=hi-lo;host[p['gpu']].append((p['started_at'],p['ended_at']))
assert len(seen)==EXPECTED_JOBS and sum(counts.values())==4096 and len(counts)==14
lo=min(a for x in host.values() for a,b in x);hi=max(b for x in host.values() for a,b in x)
kernels={};records=0
for p in root.glob('GPU*_KERNELS.csv'):
 lines=p.read_text().splitlines();meta=json.loads(lines[0]);assert meta['dropped']==0 and meta['records']==len(lines)-1
 d=int(p.name[3:].split('_')[0]);offset=meta['offset_ns'];kernels[d]=[];records+=meta['records']
 for line in lines[1:]:
  start,end,device,stream=map(int,line.split(','));kernels[d].append(((start+offset)/1e9,(end+offset)/1e9))
assert len(kernels)==14 and records==EXPECTED_JOBS*32*88
telemetry=json.loads((ram/(RUN+'-telemetry.json')).read_text());first,last=telemetry[0],telemetry[-1]
def stat(s):return {k:int(v) for k,v in (x.split() for x in s.splitlines())}
def io(s):return {x.split()[0]:{k:int(v) for k,v in (y.split('=') for y in x.split()[1:])} for x in s.splitlines()}
st0,st1=stat(first['cpu.stat']),stat(last['cpu.stat']);i0,i1=io(first['io.stat']),io(last['io.stat'])
maxmem=max(int(x['memory.current']) for x in telemetry);assert 880000000000-maxmem>1024**3
summary_result={'status':'EXACT_N96_ANALYZED','source_instance':result['source_instance'],'fresh_roots':4096,'cutset_branches':32,'configuration_count':str(2**96),'checks':result['checks'],'independent_retained_coverage_check':True,'independent_telemetry_memory_reserve_check':True,'answer_seconds':result['answer_seconds'],'initialization_seconds':result['initialization_seconds'],'ready_to_answer_seconds':result['ready_to_answer_seconds'],'fiber_seconds':result['fiber_seconds'],'lifecycle_seconds':result['lifecycle_seconds'],'startup_inclusive_seconds':result['startup_inclusive_seconds'],'roots_per_gpu':dict(counts),'peak_host_GiB':maxmem/1024**3,'peak_worker_device_pool_GiB':max(p['pool_bytes'] for p in profiles)/1024**3,'kernel_records':records,'zero_dropped_kernel_records':True,'actual_kernel_activity':summary(kernels,lo,hi),'steady_actual_kernel_activity':summary(kernels,lo+1,hi-1),'host_service':summary(host,lo,hi),'cpu_seconds':(st1['usage_usec']-st0['usage_usec'])/1e6,'mean_cpu_cores':(st1['usage_usec']-st0['usage_usec'])/1e6/(last['monotonic']-first['monotonic']),'throttled_periods':st1['nr_throttled']-st0['nr_throttled'],'block_io_delta_by_device':{d:{k:i1[d][k]-row[k] for k in row} for d,row in i0.items()},'first_checkpoint':json.loads((P/NAME/(RUN+'.json')).read_text()),'custody':r}
(P/(NAME+'_ANALYSIS.json')).write_text(json.dumps(summary_result,indent=2)+'\n')
print({k:summary_result[k] for k in ['answer_seconds','ready_to_answer_seconds','lifecycle_seconds','peak_host_GiB','peak_worker_device_pool_GiB','mean_cpu_cores','kernel_records','throttled_periods']})
for k in ['actual_kernel_activity','steady_actual_kernel_activity']:print(k,{x:summary_result[k][x] for x in ['window_seconds','mean_active_gpus','mean_gpu_busy_fraction','all14_busy_fraction','atleast13_busy_fraction']})
print('checkpoint',summary_result['first_checkpoint'])
