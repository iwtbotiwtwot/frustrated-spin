"""Exact grouped-boundary production: cached GPU factors and bounded output overlap."""
import argparse,collections,fcntl,hashlib,json,os,signal,struct,time,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cupy as cp
from gpu import Backend
from output import write
HERE=Path(__file__).resolve().parent
FILES=['gpu.py','gpu_baseline.py','kernels.cu','output.py','output.cpp','bench.py','production.py','INPUTS.json','N3000_REFERENCE.json']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,d):
 tmp=p.with_suffix('.tmp')
 with tmp.open('w') as f:json.dump(d,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 tmp.replace(p)
def factors(c,state):return [(dict(f['row']),f['exponent']) for f in c['factors']]+[(dict(c['roots'][str(state)]),1)]
def canonical(n,state,buckets):return hashlib.sha256(struct.pack('<II',n,state)+b''.join(bytes.fromhex(h) for h in buckets)).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['pipeline','produce'],required=True);ap.add_argument('--N',type=int,choices=[3000,4000],default=4000);ap.add_argument('--workers',type=int,default=0);ap.add_argument('--seconds',type=int,default=7200);ap.add_argument('--output',required=True);ap.add_argument('--root',type=Path);a=ap.parse_args()
 root=a.root or HERE/Path(a.output).stem;root.mkdir(exist_ok=True);lock=(root/'LOCK').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (root/'STOP').exists():raise RuntimeError('STOP exists; deliberate resume required')
 stop=[False];signal.signal(signal.SIGTERM,lambda *_:stop.__setitem__(0,True));signal.signal(signal.SIGINT,lambda *_:stop.__setitem__(0,True))
 source=json.loads((HERE/'INPUTS.json').read_text());cases=[c for c in source['cases'] if c['N']==a.N and (a.mode=='produce' or (c['family']=='packet' and c['fill']==-1))]
 jobs=[];maxhost=0
 for c in cases:
  groups=collections.defaultdict(list)
  for state,row in c['roots'].items():groups[(json.dumps(row,separators=(',',':')),int(state).bit_count())].append(int(state))
  for group in groups.values():
   group.sort();degree=sum(max(r)*e for r,e in factors(c,group[0]));maxhost=max(maxhost,(degree+1)*((a.N+64)//64)*8);jobs.append((c,group))
 cg=Path('/sys/fs/cgroup');rawlimit=(cg/'memory.max').read_text().strip();memory=int(rawlimit) if rawlimit!='max' else int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cpu=(cg/'cpu.max').read_text().split();cores=float(cpu[0])/int(cpu[1]) if cpu[0]!='max' else len(os.sched_getaffinity(0))
 admitted=max(1,min(6,int(memory*.70//maxhost)-1,int(cores*.5)));workers=a.workers or admitted
 if not 1<=workers<=admitted:raise ValueError(f'Requested {workers} writers exceeds admitted {admitted}')
 if a.mode=='produce' and shutil.disk_usage(root).free<750*10**9:raise RuntimeError('Full N4000 output admission requires750GB free')
 binding={n:sha(HERE/n) for n in FILES};backend=Backend();start=time.perf_counter();rows=[];pairs={};pending=[];computed=0;reused=0;reason='COMPLETE';target=sum(len(g) for c,g in jobs)
 references={(r['case']['family'],r['case']['fill'],r['case']['orientation'],r['state']):r for r in json.loads((HERE/'N3000_REFERENCE.json').read_text())['rows']}
 def path(c,state):return root/f'N{a.N}_{c["family"]}_{c["fill"]}_{c["orientation"]}_{state}.bin'
 def validate(row):
  c=row['case'];state=row['state']
  if a.N==3000:
   expected=references[c['family'],c['fill'],c['orientation'],state]['gpu']
   for k in ['joint_row_sha256','binary_data_sha256','records','bytes','moments']:assert row['gpu'][k]==expected[k],('N3000 reference',k,state)
 def commit(data,c,group,timing,arithmetic,t0):
  first=group[0];p=path(c,first);gd=write(data,c,first,p);buckets=gd.pop('bucket_sha256');assert len(buckets)==a.N+1
  result=[]
  for state in group:
   assert c['roots'][str(state)]==c['roots'][str(first)] and state.bit_count()==first.bit_count()
   assert gd['moments']==c['expected_moments'][str(state)]
   value=dict(gd,joint_row_sha256=canonical(a.N,state,buckets))
   if state==first:assert value['joint_row_sha256']==gd['joint_row_sha256']
   else:
    alias=path(c,state)
    if alias.exists():
     if not os.path.samefile(p,alias):
      if sha(alias)!=gd['binary_data_sha256']:raise ValueError('Existing alias bytes differ')
      alias.unlink();os.link(p,alias)
    else:os.link(p,alias)
   row=dict(case={k:c[k] for k in ['N','family','fill','orientation','source_sha256','plan_sha256','ports','bound','step']},state=state,gpu=value,timing=timing,arithmetic_seconds=arithmetic if state==first else 0,source_polynomial_state=first,exact_duplicate_reuse=state!=first,file=path(c,state).name,binding=binding,count_bytes=(a.N+8)//8)
   validate(row);atomic(path(c,state).with_suffix('.json'),row);result.append(row)
  fd=os.open(root,os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
  return result
 def accept(group):
  for row in group:
   validate(row);rows.append(row);c=row['case'];key=(c['family'],c['fill'],row['state']);pair=pairs.setdefault(key,[]);pair.append(row)
   if len(pair)==2:
    assert pair[0]['case']['orientation']!=pair[1]['case']['orientation']
    for k in ['joint_row_sha256','records','moments']:assert pair[0]['gpu'][k]==pair[1]['gpu'][k],('Independent encodings',key,k)
  state=dict(status='RUNNING',N=a.N,rows=len(rows),target_rows=target,paired_boundaries=sum(len(v)==2 for v in pairs.values()),seconds=time.perf_counter()-start,workers=workers,logical_bytes=sum(r['gpu']['bytes'] for r in rows),unique_bytes=sum(r['gpu']['bytes'] for r in rows if not r['exact_duplicate_reuse']))
  atomic(root/'STATUS.json',state);print('PROGRESS',len(rows),target,state['paired_boundaries'],state['seconds'],flush=True)
 with ThreadPoolExecutor(max_workers=workers) as pool:
  for c,group in jobs:
   if stop[0] or (root/'STOP').exists():reason='OWNER_STOP';break
   if time.perf_counter()-start>=a.seconds:reason='TIME_BUDGET';break
   if all(path(c,s).with_suffix('.json').exists() for s in group):
    loaded=[]
    for s in group:
     r=json.loads(path(c,s).with_suffix('.json').read_text());assert r['binding']==binding and sha(path(c,s))==r['gpu']['binary_data_sha256'];loaded.append(r)
    accept(loaded);reused+=1;continue
   while len(pending)>=workers:accept(pending.pop(0).result())
   t0=time.perf_counter();data,timing=backend.solve(factors(c,group[0]),a.N);arithmetic=time.perf_counter()-t0
   pending.append(pool.submit(commit,data,c,group,timing,arithmetic,t0));computed+=1;del data
   if computed==1:accept(pending.pop(0).result()) # initialize native writer before threads
  for future in pending:accept(future.result())
 backend.clear();complete=len(rows)==target
 result=dict(status='PASS' if complete else 'CHECKPOINTED',reason=reason,mode=a.mode,N=a.N,rows=rows,paired_boundaries=sum(len(v)==2 for v in pairs.values()),computed_polynomials=computed,reused_checkpoint_groups=reused,duplicate_boundary_rows=sum(r['exact_duplicate_reuse'] for r in rows),workers=workers,max_host_array_bytes=maxhost,seconds=time.perf_counter()-start,files=binding,logical_bytes=sum(r['gpu']['bytes'] for r in rows),unique_bytes=sum(r['gpu']['bytes'] for r in rows if not r['exact_duplicate_reuse']))
 atomic(HERE/a.output,result);atomic(root/'STATUS.json',{k:v for k,v in result.items() if k not in ['rows','files']});print('FINISHED',result['status'],len(rows),result['seconds'],flush=True)
if __name__=='__main__':main()
