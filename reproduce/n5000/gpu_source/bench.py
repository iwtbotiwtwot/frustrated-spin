"""Bounded exact qualification, matched GPU tuning and N4000 pilot."""
import argparse,hashlib,json,os,time
from pathlib import Path
import cupy as cp
from flint import fmpz_poly
from gpu import Backend
from gpu_baseline import Backend as Baseline
from output import write
HERE=Path(__file__).resolve().parent
FILES=['gpu.py','gpu_baseline.py','kernels.cu','output.py','output.cpp','bench.py','INPUTS.json','N3000_REFERENCE.json']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
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
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['qualify','bench','pilot4000','peak4000','peak5000'],required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 source=json.loads((HERE/'INPUTS.json').read_text());out=HERE/Path(a.output).stem;out.mkdir(exist_ok=True);start=time.perf_counter();files={n:sha(HERE/n) for n in FILES};rows=[]
 ref={(r['case']['family'],r['case']['fill'],r['case']['orientation'],r['state']):r for r in json.loads((HERE/'N3000_REFERENCE.json').read_text())['rows']}
 def solve(backend,c,state,label):
  t=time.perf_counter();actual,timing=backend.solve(factors(c,state),c['N']);arithmetic=time.perf_counter()-t
  path=out/f'{label}_{c["N"]}_{c["family"]}_{c["fill"]}_{c["orientation"]}_{state}.bin';gd=write(actual,c,state,path);del actual
  assert gd['moments']==c['expected_moments'][str(state)]
  if c['N']==3000:
   expected=ref[c['family'],c['fill'],c['orientation'],state]['gpu']
   for k in ['joint_row_sha256','binary_data_sha256','records','bytes','moments']:assert gd[k]==expected[k],k
  row=dict(label=label,case={k:v for k,v in c.items() if k not in ['factors','roots','expected_moments']},state=state,gpu=gd,timing=timing,arithmetic_seconds=arithmetic,total_seconds=time.perf_counter()-t,file=str(path.relative_to(HERE)))
  rows.append(row);print('ROW',label,c['N'],c['family'],c['orientation'],state,arithmetic,row['total_seconds'],timing.get('cache_hit'),flush=True);return row
 if a.mode=='qualify':
  backend=Backend();checks=0
  for bits in [3000,4000,5000]:
   fs=[({0:1,1:1},bits)];actual,t=backend.solve(fs,bits);assert ints(actual)==cpu(fs);del actual;checks+=1
  for c in source['cases']:
   if c['N']>30:continue
   states=sorted(map(int,c['roots']))
   for state in sorted(set([states[0],states[len(states)//3],states[-1]])):
    fs=factors(c,state);actual,t=backend.solve(fs,c['N']);assert ints(actual)==cpu(fs);del actual;checks+=1
  backend.clear();result=dict(status='PASS',checks=checks)
 elif a.mode=='bench':
  c=next(c for c in source['cases'] if c['N']==3000 and c['family']=='signed_packet_chain' and c['fill']==-1 and c['orientation']=='T_MAJOR')
  baseline=Baseline();solve(baseline,c,0,'baseline');del baseline;cp.get_default_memory_pool().free_all_blocks()
  tuned=Backend()
  for state in [0,1,2]:solve(tuned,c,state,'cached')
  tuned.clear()
  # Check the cache path in all source families and both encodings against saved rows.
  for family,fill in [('packet',-1),('signed_packet',1),('signed_packet_chain',1)]:
   for orientation in ['K_MAJOR','T_MAJOR']:
    c=next(c for c in source['cases'] if c['N']==3000 and c['family']==family and c['fill']==fill and c['orientation']==orientation)
    solve(tuned,c,0,'coverage');tuned.clear()
  result=dict(status='PASS',rows=rows)
 else:
  backend=Backend();states=[15] if a.mode in ['peak4000','peak5000'] else [0,1];family='packet' if a.mode in ['peak4000','peak5000'] else 'signed_packet_chain'
  for orientation in ['T_MAJOR','K_MAJOR']:
   c=next(c for c in source['cases'] if c['N']==(5000 if a.mode=='peak5000' else 4000) and c['family']==family and c['fill']==-1 and c['orientation']==orientation)
   for state in states:solve(backend,c,state,'pilot')
   backend.clear()
  for state in states:
   pair=[r for r in rows if r['state']==state]
   for key in ['joint_row_sha256','records','moments']:assert pair[0]['gpu'][key]==pair[1]['gpu'][key],key
  result=dict(status='PASS',paired_boundaries=len(states),rows=rows)
 result.update(files=files,seconds=time.perf_counter()-start,gpu=cp.cuda.runtime.getDeviceProperties(0)['name'].decode());(HERE/a.output).write_text(json.dumps(result,indent=2)+'\n');print('FINISHED',a.mode,result['status'],result['seconds'],flush=True)
if __name__=='__main__':main()
