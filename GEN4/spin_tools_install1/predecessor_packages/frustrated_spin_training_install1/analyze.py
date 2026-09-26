"""Read completed training measurements and evidence; no new spin calculations."""
from pathlib import Path
import json,gzip,datetime,hashlib,sys,statistics
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'frustrated_spin_n72_bench1'))
from concurrency import summary
folders={k:P.parent/n/'results/ram' for k,n in [('ladder','frustrated_spin_training1'),('small','frustrated_spin_n1_30_training1'),('full96','frustrated_spin_full96_training1')]}
def read(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
out={}
for key,f in folders.items():
 c=read(f/'COMPLETE.json');m=read(f/'MEASUREMENTS.json');g=read(f/'GROUPED_EXPERIENCE.json');t=read(f/'TELEMETRY.json');session=next((f/'sessions').iterdir());receipts=list(session.rglob('RECEIPT.json'));native=[]
 for path in receipts:
  r=read(path);native.append(r)
  for name in ['INPUT','OUTPUT']:
   descriptor=path.parent/(name+'.json');d=read(descriptor)
   assert hashlib.sha256(descriptor.read_bytes()).hexdigest()==r[name.lower()+'_sha256']
   z=(path.parent/(name+'.json.gz')).read_bytes();assert hashlib.sha256(z).hexdigest()==d['compressed_sha256']
   assert hashlib.sha256(gzip.decompress(z)).hexdigest()==r[name.lower()+'_logical_sha256']
 best=[min([v for v in g if v['N']==n],key=lambda v:v.get('median_ns',v.get('median_total_ns'))) for n in sorted({v['N'] for v in g})]
 model=read(f/('FROZEN_POLICIES.json' if key=='ladder' else 'FROZEN_MODELS.json'));model=model['fits'] if key=='ladder' else model
 out[key]=dict(calculations=len(m),receipt_count=len(receipts),complete=c,session=read(session/'SESSION.json'),measurement_seconds=sum(v['total_ns'] for v in m)/1e9,telemetry_seconds=t[-1]['time']-t[0]['time'],peak_host_GiB=max(int(v['memory.current']) for v in t)/2**30,best=best,models={k:dict(depth=v['fit']['depth'],training=v['fit']['training']['balanced_accuracy'],development=v['fit']['development']['balanced_accuracy']) for k,v in model.items()})
 print(key,'calcs',len(m),'seconds',out[key]['measurement_seconds'],'telemetry seconds',out[key]['telemetry_seconds'],'receipts',len(receipts),flush=True)
f=folders['full96'];case=read(f/'case133_r1.json.gz');e=case['execution'];lo=e['ready_ns']/1e9;hi=e['gpu_done_ns']/1e9;kernels={};records=0
for path in f.glob('GPU*_KERNELS.csv'):
 rows=[];count=0
 with path.open() as stream:
  header=json.loads(next(stream));assert header['dropped']==0;offset=header['offset_ns']
  for line in stream:
   count+=1;a,b,_,_=map(int,line.split(','));a=(a+offset)/1e9;b=(b+offset)/1e9
   if b>lo and a<hi:rows.append((a,b))
 assert count==header['records'];records+=count;kernels[int(path.name[3:].split('_')[0])]=rows
out['full96']['kernel_records']=records;out['full96']['N96_activity']=dict(full=summary(kernels,lo,hi),steady=summary(kernels,lo+1,hi-1))
(P/'ANALYSIS.json').write_text(json.dumps(out,indent=2)+'\n');print('activity',out['full96']['N96_activity'],flush=True)
