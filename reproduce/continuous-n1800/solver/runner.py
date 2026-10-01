"""Exact RAM-only joint tables with compact evidence, reductions and chosen milestones."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import argparse,collections,concurrent.futures,gzip,hashlib,itertools,json,math,platform,resource,struct,sys,threading,time
from pathlib import Path
from flint import fmpz_poly,arb,ctx
import flint
import baseline as b
import optimized as opt
from common import digest
import numpy as np
import fast_cpu
from dense_format import generate as graph_bits,validate as check_graph_bits
assert sys.byteorder=="little" and sys.version_info[:2]==(3,12)
HERE=Path(__file__).resolve().parent
MAGIC=b'SAM_GEMB_CANON_V1\0'
TABLES={};SOURCES={};SOURCE_INDEX={};CONFIG={};BUILD={};OUT=None;GPU=None;USE_GPU=os.environ.get("SPIN_BACKEND")=="GPU";GPU_PEAK=0

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj,compressed=False):
 start=time.perf_counter();raw=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode();p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix(p.suffix+'.part')
 data=gzip.compress(raw,compresslevel=3,mtime=0) if compressed else raw
 with temp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 temp.replace(p);return time.perf_counter()-start,p.stat().st_size

def mem():
 d={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/self/status').read_text().splitlines() if x.startswith(('VmRSS:','VmHWM:')))}
 return d
class Sampler:
 def __init__(self):self.stop=threading.Event();self.peak=0;self.samples=0;self.thread=threading.Thread(target=self.loop,daemon=True)
 def loop(self):
  while not self.stop.is_set():self.peak=max(self.peak,mem().get('VmRSS',0));self.samples+=1;self.stop.wait(CONFIG['rss_sampling_seconds'])
 def __enter__(self):self.before=mem();self.thread.start();return self
 def __exit__(self,*args):self.stop.set();self.thread.join();self.after=mem();self.peak=max(self.peak,self.after.get('VmRSS',0),self.before.get('VmRSS',0))
 def result(self):return dict(worker_pid=os.getpid(),worker_lifetime_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,worker_lifetime_peak_scope='OS ru_maxrss from worker creation, including earlier sizes and reusable table cache; not a per-N allocation measurement',per_N_sampled_peak_rss_bytes=self.peak,per_N_sampling_interval_seconds=CONFIG['rss_sampling_seconds'],samples=self.samples,rss_before=self.before.get('VmRSS'),rss_after=self.after.get('VmRSS'),gpu_allocation_bytes=GPU_PEAK,gpu_scope='Maximum backend estimated working allocation plus cache; not device observed peak' if USE_GPU else 'CPU-only worker')

def header(n,ports):
 raw=json.dumps(dict(schema='SAM_GEMB_CANON_V1',N=n,ordered_ports=ports,order='boundary ascending; E ascending; M ascending',integer_format='int64_le_E,int64_le_M,unsigned_fixed_width_le_count',count_bytes=(n+8)//8),sort_keys=True,separators=(',',':')).encode()
 return MAGIC+struct.pack('<I',len(raw))+raw

def canonical_row(n,state,entries):return fast_cpu.canonical(n,state,entries)

def expected_moments(c,fill,state):
 n=c['N'];ports=c['ports'];fixed={v:1 if state&(1<<i) else -1 for i,v in enumerate(ports)};weights={(u,v):j for u,v,j in c['source']['edges']};fields=c['source']['fields']
 def j(u,v):return weights.get((min(u,v),max(u,v)),fill)
 constant=-sum(fields[v]*s for v,s in fixed.items())-sum(j(u,v)*fixed[u]*fixed[v] for u,v in itertools.combinations(ports,2));free=[v for v in range(n) if v not in fixed]
 variance=sum((fields[v]+sum(j(v,p)*s for p,s in fixed.items()))**2 for v in free)+len(free)*(len(free)-1)//2*fill*fill+sum(q*q-fill*fill for u,v,q in c['source']['edges'] if u not in fixed and v not in fixed)
 count=1<<len(free);return [count,count*constant,count*(constant*constant+variance)]

def graph_identity(c,fill):
 n=c['N'];raw=graph_bits(n,c['source']['edges'],fill);check_graph_bits(raw,n,c['source']['edges'],fill);rawhash=hashlib.sha256(raw).hexdigest()
 return dict(N=n,fill=fill,pair_count=n*(n-1)//2,raw_couplings_sha256=rawhash,graph_sha256=digest(dict(N=n,fields=c['source']['fields'],raw_couplings_sha256=rawhash)),pair_bit_order='lexicographic u<v; least significant bit first; positive coupling=1')

def direct(c,fill):
 n=c['N'];weights={(u,v):j for u,v,j in c['source']['edges']};out=collections.defaultdict(collections.Counter)
 for bits in range(1<<n):
  spins=[1 if bits>>i&1 else -1 for i in range(n)];state=sum((1<<i) for i,v in enumerate(c['ports']) if spins[v]==1)
  e=-sum(weights.get((u,v),fill)*spins[u]*spins[v] for u in range(n) for v in range(u+1,n))-sum(h*s for h,s in zip(c['source']['fields'],spins));out[state][e,sum(spins)]+=1
 return {state:sorted((e,m,count) for (e,m),count in rows.items()) for state,rows in out.items()}

def reduce_row(entries,n,weights):return fast_cpu.reduce_row(entries,n,weights,CONFIG)

def case(c,fill,n):
 global GPU,GPU_PEAK
 if USE_GPU and GPU is None:
  from gpu import Backend
  GPU=Backend()
 wall=time.perf_counter();timing=collections.Counter();ports=c['ports'];prefix=header(n,ports);milestone=n in CONFIG['full_output_milestones'];tick=time.perf_counter();exact_check=direct(c,fill) if n<=CONFIG['direct_enumeration_through_N'] else None;timing['independent_direct_enumeration_seconds']=time.perf_counter()-tick
 tick=time.perf_counter();plan=b.plan(c,fill);timing['plan_seconds']+=time.perf_counter()-tick
 tick=time.perf_counter();misses=0
 for piece in plan['pieces']:
  if piece['table_key'] not in TABLES:TABLES[piece['table_key']]=b.cpu_local(piece);misses+=1
 timing['local_enumeration_seconds']+=time.perf_counter()-tick
 receipts={};checks={};total_support=0;readouts=[];boundary_f=[];weights={};streams=[];milestone_file=None;write_seconds=0
 for orientation in CONFIG['encodings']:
  tick=time.perf_counter();parts=opt.components(plan,TABLES,orientation=='K_MAJOR');timing['component_contraction_seconds']+=time.perf_counter()-tick
  tick=time.perf_counter();counts=collections.Counter(key for key,p in parts[1:]);bykey=dict(parts);scalar=None if USE_GPU else opt.balanced([b.encode(bykey[key]['rows'],n,plan['correction_bound'],orientation)[0]**count for key,count in counts.items()]);timing['scalar_polynomial_seconds']+=time.perf_counter()-tick
  whole=hashlib.sha256(prefix);rows=[];writer=None
  if milestone and orientation=='K_MAJOR':
   milestone_file=OUT/'milestones'/f'N{n:06d}'/f'{c["family"]}_{fill:+d}.gemb';milestone_file.parent.mkdir(parents=True,exist_ok=True);tick=time.perf_counter();writer=milestone_file.with_suffix('.part').open('wb');writer.write(prefix);write_seconds+=time.perf_counter()-tick
  for state,coefficients in sorted(parts[0][1]['rows'].items()):
   tick=time.perf_counter()
   if USE_GPU:
    def sparse(row):return {(k*(plan['correction_bound']+1)+t if orientation=='K_MAJOR' else t*(n+1)+k):v for (k,t),v in row.items()}
    factors=[(sparse(bykey[key]['rows'][0]),count) for key,count in counts.items()]+[(sparse(coefficients),1)]
    poly,stats=GPU.solve(factors,n);assert 'pipeline_roundtrip_seconds' in stats;GPU_PEAK=max(GPU_PEAK,stats['estimated_gpu_bytes'])
    for metric in ['transform_seconds','crt_seconds','transfer_seconds','compact_seconds']:timing['gpu_'+metric]+=stats[metric]
    timing['gpu_cache_hits']+=int(stats['cache_hit'])
   else:
    root=b.encode({state:coefficients},n,plan['correction_bound'],orientation)[state];poly=root*scalar;del root
   timing['boundary_polynomial_seconds']+=time.perf_counter()-tick
   tick=time.perf_counter();entries=[];marginal=collections.Counter();mom=[0,0,0];magmom=[0,0,0]
   assert USE_GPU
   compact=hasattr(poly,'indices');indices=poly.indices if compact else np.empty(0,dtype=np.int64)
   entries,marginal,mom,magmom=fast_cpu.decode(poly.data,indices,compact,n,plan['correction_bound'],fill,orientation=='K_MAJOR')
   del indices
   if hasattr(poly,'release'):poly.release()
   del poly
   expected={k+state.bit_count():math.comb(n-len(ports),k) for k in range(n-len(ports)+1)};assert dict(marginal)==expected;assert mom==expected_moments(c,fill,state)
   if exact_check is not None:assert entries==exact_check[state]
   raw=canonical_row(n,state,entries);rowhash=hashlib.sha256(prefix+raw).hexdigest();whole.update(raw)
   row=dict(state=state,exact_record_count=len(entries),joint_support_size=len(entries),configuration_count=str(mom[0]),configuration_expected=str(1<<(n-len(ports))),configuration_closure=True,conditional_magnetization_closure=True,magnetization_marginal_sha256=digest([[2*k-n,str(v)] for k,v in sorted(marginal.items())]),energy_moments=list(map(str,mom)),magnetization_sum=str(magmom[0]),magnetization_square_sum=str(magmom[1]),energy_magnetization_sum=str(magmom[2]),canonical_sha256=rowhash,would_materialize_headerless_bytes=len(entries)*(8+(n+8)//8),canonical_row_bytes=len(raw),direct_enumeration_agreement=True if exact_check is not None else None)
   timing['decode_verification_digest_seconds']+=time.perf_counter()-tick
   if orientation=='K_MAJOR':
    checks[state]=row;total_support+=len(entries);tick=time.perf_counter();values,fs=reduce_row(entries,n,weights);readouts.append(dict(state=state,**values));boundary_f.append(fs);timing['volii_reduction_seconds']+=time.perf_counter()-tick
    if writer:
     tick=time.perf_counter();writer.write(raw);write_seconds+=time.perf_counter()-tick
   else:assert row==checks[state]
   rows.append(row);del entries,raw
  if writer:
   tick=time.perf_counter();writer.flush();os.fsync(writer.fileno());writer.close();milestone_file.with_suffix('.part').replace(milestone_file);write_seconds+=time.perf_counter()-tick
   tick=time.perf_counter();assert sha(milestone_file)==whole.hexdigest();timing['milestone_readback_seconds']+=time.perf_counter()-tick
  receipts[orientation]=dict(canonical_sha256=whole.hexdigest(),rows=rows)
  del scalar,parts
 assert receipts['K_MAJOR']==receipts['T_MAJOR']
 walsh=[];tick=time.perf_counter()
 for j,numerator in enumerate(CONFIG['thermal_beta_numerators_over_N']):
  terms=[]
  for mask in range(1<<len(ports)):
   value=arb(0)
   for state,fs in enumerate(boundary_f):
    sign=(-1)**((mask.bit_count()-(state&mask).bit_count())%2);value+=sign*fs[j]
   value/=len(boundary_f);terms.append(dict(port_subset=[v for i,v in enumerate(ports) if mask>>i&1],free_energy_coefficient_interval=value.str(40)))
  walsh.append(dict(beta=f'{numerator}/{n}',precision_bits=ctx.prec,terms=terms))
 timing['volii_reduction_seconds']+=time.perf_counter()-tick
 timing['milestone_write_fsync_seconds']=write_seconds;timing['case_wall_seconds']=time.perf_counter()-wall
 return dict(N=n,family=c['family'],fill=fill,source_sha256=c['source']['source_sha256'],source_record_sha256=digest(c),graph_identity=graph_identity(c,fill),ordered_ports=ports,plan_sha256=digest(plan),regeneration_plan=plan,correction_bound=plan['correction_bound'],component_statistics=dict(pieces=len(plan['pieces']),unique_piece_tables=len({x['table_key'] for x in plan['pieces']}),new_local_enumerations=misses,max_piece_vertices=max(x['n'] for x in plan['pieces']),connected_correction_groups=len(opt.groups(plan))),exact_record_count_per_encoding=total_support,joint_support_size=total_support,configuration_count=str(1<<n),configuration_closure_all_boundaries=sum(int(x['configuration_count']) for x in checks.values())==1<<n,conditional_magnetization_closure=True,energy_moments=[str(sum(int(x['energy_moments'][j]) for x in checks.values())) for j in range(3)],encoding_agreement=True,canonical_sha256=receipts['K_MAJOR']['canonical_sha256'],encoding_results=receipts,volume_ii=dict(boundaries=readouts,effective_boundary_interactions=walsh,ground_response_identity='E(h,g,b)=E0-h*M-g*(M*M-N)/2-sum_i(boundary_field_i*s_i)',thermal_parameter_scope='h=0,g=0,beta=1/N and4/N; formal source units'),would_materialize_bytes_both_encodings=2*sum(x['would_materialize_headerless_bytes'] for x in checks.values()),hypothetical_output_format='headerless int32_le E,M followed by unsigned count of floor(N/8)+1bytes, both encodings',milestone_file=str(milestone_file.relative_to(OUT)) if milestone_file else None,full_output_disk_bytes=milestone_file.stat().st_size if milestone_file else 0,nonmilestone_full_output_disk_bytes=0,timing=dict(timing))

def init(out):
 global CONFIG,SOURCES,SOURCE_INDEX,BUILD,OUT
 OUT=Path(out);CONFIG=json.loads((HERE/'CONFIG.json').read_text());BUILD=json.loads((HERE/'BUILD_ID.json').read_text());SOURCE_INDEX=json.loads((HERE/'SOURCE_INDEX.json').read_text());ctx.threads=1;ctx.prec=CONFIG['thermal_precision_bits']
 if not USE_GPU:resource.setrlimit(resource.RLIMIT_AS,(CONFIG['worker_address_space_limit_bytes'],CONFIG['worker_address_space_limit_bytes']))

def work(n):
 started=time.perf_counter();SOURCES.clear()
 for family in CONFIG['families']:
  key=f'{family}_N{n:03d}';item=SOURCE_INDEX[key];path=HERE/item['file'];assert sha(path)==item['sha256']
  c=json.loads(gzip.decompress(path.read_bytes()));assert c['N']==n and c['source']['source_sha256']==item['source_sha256'];SOURCES[key]=c
 with Sampler() as sampler:
  cases=[case(SOURCES[f'{f}_N{n:03d}'],fill,n) for f in CONFIG['families'] for fill in CONFIG['fills']]
 peak=sampler.result();record=dict(schema='SPIN_RAM_N_RECORD_V1',N=n,implementation=BUILD,runtime=dict(python=sys.version,python_flint=flint.__version__,platform=platform.platform(),backend='GPU_SERVICE_COMPILED_CPU_RAM_PIPELINE' if USE_GPU else 'CPU_FLINT_EXACT',native_controller='MATTER_SEARCH/SLC-GEN3-R4/SLC-GEN3-CEV1-R4/GEN3-R4',arb_precision_bits=ctx.prec),cases=cases,peak_memory=peak,wall_before_compact_write_seconds=time.perf_counter()-started,canonical_size_digest=digest([dict(family=c['family'],fill=c['fill'],sha256=c['canonical_sha256']) for c in cases]))
 folder=OUT/'records'/f'N{n:06d}';path=folder/'RECORD.json.gz';write_seconds,size=save(path,record,True)
 receipt=dict(status='PASS',N=n,record_file=str(path.relative_to(OUT)),record_sha256=sha(path),record_bytes=size,compact_record_write_fsync_seconds=write_seconds,milestone_write_fsync_seconds=sum(c['timing']['milestone_write_fsync_seconds'] for c in cases),compute_seconds=sum(sum(c['timing'].get(k,0) for k in ['plan_seconds','local_enumeration_seconds','component_contraction_seconds','scalar_polynomial_seconds','boundary_polynomial_seconds']) for c in cases),verification_digest_seconds=sum(c['timing']['decode_verification_digest_seconds'] for c in cases),volii_reduction_seconds=sum(c['timing']['volii_reduction_seconds'] for c in cases),wall_seconds=time.perf_counter()-started,peak_memory=peak,encoding_agreement=True,configuration_closure=True,conditional_magnetization_closure=True,canonical_size_digest=record['canonical_size_digest'],exact_record_count_one_encoding=sum(c['joint_support_size'] for c in cases),would_materialize_bytes_both_encodings=sum(c['would_materialize_bytes_both_encodings'] for c in cases),full_output_disk_bytes=sum(c['full_output_disk_bytes'] for c in cases),nonmilestone_full_output_disk_bytes=0,receipt_write_timing_scope='Durable compact RECORD and milestone writes measured separately; this small receipt self-write is excluded')
 save(folder/'RECEIPT.json',receipt);return receipt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--min-N',type=int,default=500);ap.add_argument('--max-N',type=int,default=500);ap.add_argument('--workers',type=int);a=ap.parse_args();init(a.out);assert CONFIG['min_N']<=a.min_N<=a.max_N<=CONFIG['max_N'];OUT.mkdir(parents=True,exist_ok=True)
 for name,h in BUILD['files'].items():assert sha(HERE/name)==h,name
 assert int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('SwapTotal:')))==0,'No-swap bulk policy requires swap disabled'
 started=time.perf_counter();rows=[];workers=a.workers or CONFIG['workers'];state=dict(status='RUNNING',max_N=a.max_N,completed_sizes=0,workers=workers)
 save(OUT/'STATUS.json',state)
 try:
  from pipeline import Service,init_worker
  service=Service(workers,CONFIG['gpu_cache_budget_bytes'])
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=service.ctx,initializer=init_worker,initargs=(str(OUT),service.clients,service.counter)) as pool:
   futures=[pool.submit(work,n) for n in range(a.min_N,a.max_N+1)]
   for f in concurrent.futures.as_completed(futures):
    r=f.result();rows.append(r);state.update(completed_sizes=len(rows),latest_N=r['N'],seconds=time.perf_counter()-started);save(OUT/'STATUS.json',state);print('N_COMPLETE',r['N'],r['wall_seconds'],r['record_bytes'],flush=True)
  service.close()
  assert service.solves.value==192*(a.max_N-a.min_N+1),service.solves.value
  rows.sort(key=lambda r:r['N']);assert [r['N'] for r in rows]==list(range(a.min_N,a.max_N+1))
  files=[dict(file=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['STATUS.json','RESULT.json']]
  actual_full=list(OUT.rglob('*.gemb'));assert all(int(p.parent.name[1:]) in CONFIG['full_output_milestones'] for p in actual_full)
  assert len(actual_full)==6*sum(a.min_N<=n<=a.max_N for n in CONFIG['full_output_milestones'])
  assert not list(OUT.rglob('*.part'))
  result=dict(gpu_service_solve_count=service.solves.value,status='PASS',min_N=a.min_N,max_N=a.max_N,sizes=len(rows),cases=len(rows)*6,seconds=time.perf_counter()-started,workers=workers,implementation=BUILD,rows=rows,files=files,retained_bytes=sum(p['bytes'] for p in files),would_materialize_bytes_both_encodings=sum(r['would_materialize_bytes_both_encodings'] for r in rows),full_output_disk_bytes=sum(r['full_output_disk_bytes'] for r in rows),all_nonmilestone_full_output_disk_bytes=0,peak_worker_lifetime_rss_bytes=max(r['peak_memory']['worker_lifetime_peak_rss_bytes'] for r in rows),swap_used_bytes=int(Path('/sys/fs/cgroup/memory.swap.current').read_text()),retained_milestone_sizes=[n for n in CONFIG['full_output_milestones'] if a.min_N<=n<=a.max_N])
  assert result['swap_used_bytes']==0
  save(OUT/'RESULT.json',result);save(OUT/'STATUS.json',{k:v for k,v in result.items() if k not in ['rows','files','implementation']});print('PASS',result['sizes'],result['seconds'],result['retained_bytes'],flush=True)
 except BaseException as e:
  if 'service' in locals():service.close()
  state.update(status='FAILED',error=repr(e));save(OUT/'STATUS.json',state);raise
if __name__=='__main__':main()
