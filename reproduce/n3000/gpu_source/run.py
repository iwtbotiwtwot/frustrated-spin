"""N3000 exact GPU production, paired encodings and durable row checkpoints."""
import argparse,fcntl,hashlib,json,math,os,random,signal,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cupy as cp
from flint import fmpz_poly
from gpu import Backend
from output import write
HERE=Path(__file__).resolve().parent
FILES=['gpu.py','kernels.cu','output.py','output.cpp','run.py','INPUTS.json','PRIOR_REFERENCE.json']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,value):
 p=Path(p);temp=p.with_suffix('.tmp')
 with temp.open('w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 temp.replace(p);fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def factors(c,state):return [(dict(f['row']),f['exponent']) for f in c['factors']]+[(dict(c['roots'][str(state)]),1)]
def cpu(fs):
 result=fmpz_poly([1])
 for r,e in fs:
  a=[0]*(max(r)+1)
  for i,v in r.items():a[i]=v
  result*=fmpz_poly(a)**e
 return list(map(int,result))
def ints(a):return [int.from_bytes(row.tobytes(),'little') for row in a]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['qualify','pilot','produce'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--seconds',type=int,default=3600);a=ap.parse_args()
 root=HERE/'run';root.mkdir(exist_ok=True)
 lock=(root/'LOCK').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 files={n:sha(HERE/n) for n in FILES};binding=dict(files=files,schema='N3000_GPU_JOINT_V1')
 source=json.loads((HERE/'INPUTS.json').read_text());backend=Backend();start=time.perf_counter();rows=[]
 if a.mode=='qualify':
  fs=[({0:1,1:1},3000)];actual,t=backend.solve(fs,3000);assert ints(actual)==cpu(fs);del actual
  count=1
  for c in source['cases']:
   if c['N']>30:continue
   states=sorted(map(int,c['roots']))
   for state in sorted(set([states[0],states[len(states)//3],states[-1]])):
    fs=factors(c,state);actual,t=backend.solve(fs,c['N']);assert ints(actual)==cpu(fs);del actual;count+=1
  result=dict(status='PASS',checks=count,files=files,seconds=time.perf_counter()-start)
  atomic(HERE/a.output,result);print(json.dumps(result),flush=True);return
 if (root/'STOP').exists():raise RuntimeError('Deliberate STOP exists; owner resume required')
 stop=[False]
 def stop_signal(*_):stop[0]=True
 signal.signal(signal.SIGTERM,stop_signal);signal.signal(signal.SIGINT,stop_signal)
 references={r['path']:r for r in json.loads((HERE/'PRIOR_REFERENCE.json').read_text())}
 def commit(actual,c,state,path,timing,arithmetic,t0):
  gd=write(actual,c,state,path)
  assert gd['moments']==c['expected_moments'][str(state)],'Independent source moments differ'
  key=f"results/N003000/{c['family']}_{c['fill']:+d}/{c['orientation']}/boundary_{state:04d}.json"
  previous=references.get(key)
  if previous:
   for k in ['joint_row_sha256','records']:assert gd[k]==previous[k],('Prior exact row differs',key,k)
  row=dict(case={k:c[k] for k in ['N','family','fill','orientation','source_sha256','plan_sha256','ports','bound','step']},state=state,gpu=gd,gpu_timing=timing,gpu_arithmetic_seconds=arithmetic,row_seconds=time.perf_counter()-t0,binding=binding,file=path.name,prior_reference_match=bool(previous),count_bytes=376,record_format='int32_le_E,int32_le_M,unsigned376_le_count_no_header')
  atomic(path.with_suffix('.json'),row);return row
 pairs={};paired=0
 def accept(row):
  nonlocal paired
  c=row['case'];key=(c['family'],c['fill'],row['state'])
  if key in pairs:
   other=pairs[key];assert other['case']['orientation']!=c['orientation']
   for k in ['joint_row_sha256','records','moments']:assert row['gpu'][k]==other['gpu'][k],('Encoding mismatch',key,k)
   paired+=1
  else:pairs[key]=row
  rows.append(row)
  progress=dict(status='RUNNING',mode=a.mode,completed_rows=len(rows),paired_boundaries=paired,target_rows=2 if a.mode=='pilot' else 192,seconds=time.perf_counter()-start,saved_bytes=sum(r['gpu']['bytes'] for r in rows),last_case=c,last_state=row['state'],utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
  atomic(root/'STATUS.json',progress);print(json.dumps(progress),flush=True)
 pending=[];reason='COMPLETE';reused=0
 # Pair encodings per boundary, so comparisons complete incrementally.
 cases={(c['family'],c['fill'],c['orientation']):c for c in source['cases'] if c['N']==3000}
 jobs=[]
 for family in ['packet','signed_packet','signed_packet_chain']:
  for fill in [1,-1]:
   for state in range(16):
    for orientation in ['T_MAJOR','K_MAJOR']:
     if a.mode=='pilot' and (family!='packet' or fill!=-1 or state!=0):continue
     jobs.append((cases[family,fill,orientation],state))
 if a.mode=='produce' and __import__('shutil').disk_usage(root).free<500*10**9:
  raise RuntimeError('Full production admission requires500GB free including output and reserve')
 with ThreadPoolExecutor(max_workers=2) as writers:
  for c,state in jobs:
   if stop[0] or (root/'STOP').exists():reason='OWNER_STOP';break
   if time.perf_counter()-start>=a.seconds:reason='TIME_BUDGET';break
   path=root/f"{c['family']}_{c['fill']}_{c['orientation']}_{state}.bin";receipt=path.with_suffix('.json')
   if receipt.exists():
    row=json.loads(receipt.read_text());assert row['binding']==binding and sha(path)==row['gpu']['binary_data_sha256'];accept(row);reused+=1;continue
   if len(pending)>=2:accept(pending.pop(0).result())
   t0=time.perf_counter();actual,timing=backend.solve(factors(c,state),3000);arithmetic=time.perf_counter()-t0
   pending.append(writers.submit(commit,actual,c,state,path,timing,arithmetic,t0));del actual
   if not rows:accept(pending.pop(0).result()) # load native writer before concurrent calls
   cp.get_default_memory_pool().free_all_blocks()
  for future in pending:accept(future.result())
 complete=len(rows)==len(jobs);status='PASS' if complete else 'CHECKPOINTED'
 if complete:assert paired==len(jobs)//2
 result=dict(status=status,reason=reason,mode=a.mode,rows=rows,paired_boundaries=paired,reused_rows=reused,computed_rows=len(rows)-reused,seconds=time.perf_counter()-start,files=files)
 atomic(HERE/a.output,result)
 atomic(root/'STATUS.json',dict(status='COMPLETE' if complete else 'STOPPED',reason=reason,mode=a.mode,completed_rows=len(rows),paired_boundaries=paired,seconds=result['seconds'],saved_bytes=sum(r['gpu']['bytes'] for r in rows),result_file=a.output))
 print('FINISHED',status,len(rows),result['seconds'],flush=True)
if __name__=='__main__':main()
