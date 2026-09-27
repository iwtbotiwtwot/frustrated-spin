"""Lossless joint g(E,M,b) storage and exact rational-field readout."""
import json,gzip,hashlib,os,math,collections,time
from fractions import Fraction
from pathlib import Path

OUTPUT=None;IDENTITY=None;ROWS=[];START=None
def configure(path,identity):
 global OUTPUT,IDENTITY,ROWS,START
 OUTPUT=Path(path);OUTPUT.mkdir(parents=True,exist_ok=True);IDENTITY=identity;ROWS=[];START=time.perf_counter()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(path,value):
 p=Path(path);tmp=p.with_name(p.name+'.part');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)
def write_row(plan,state,entries):
 assert OUTPUT is not None,'JOINT_EXPORT_NOT_CONFIGURED'
 filename=f'boundary_{state:04d}.jsonl.gz';p=OUTPUT/filename;assert not p.exists(),'Never overwrite a joint row'
 total=0
 with (OUTPUT/(filename+'.part')).open('wb') as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=1,mtime=0) as z:
   for k,ec,count in sorted(entries):
    m=2*k-plan['N'];energy=ec-plan['fill']*((m*m-plan['N'])//2)
    z.write((json.dumps([energy,m,str(count)],separators=(',',':'))+'\n').encode());total+=count
  raw.flush();os.fsync(raw.fileno())
 (OUTPUT/(filename+'.part')).replace(p)
 ROWS.append(dict(boundary_state=state,file=filename,sha256=sha(p),records=len(entries),configurations=str(total),bytes=p.stat().st_size))

def decode_row(folder,row):
 p=folder/row['file'];assert sha(p)==row['sha256'],'JOINT_FILE_HASH_MISMATCH'
 with gzip.open(p,'rt') as f:
  for line in f:
   e,m,c=json.loads(line);assert type(e) is int and type(m) is int and isinstance(c,str)
   c=int(c);assert c>0;yield e,m,c

def finish(plan,dos,expected_joint_hash,source=None):
 n=plan['N'];ports=plan['ports'];h=hashlib.sha256();total=0
 assert sorted(r['boundary_state'] for r in ROWS)==list(range(1<<len(ports)))
 direct=None
 if source is not None and n<=12:
  # Independent full dense Gray-code enumeration, retaining magnetization too.
  import baseline as b
  bound=sum(abs(j) for u,v,j in source['edges'])+sum(map(abs,source['fields']))
  direct=b.cpu_local(dict(n=n,edges=source['edges'],fields=source['fields'],ports=ports,bound=bound))
 for row in sorted(ROWS,key=lambda r:r['boundary_state']):
  state=row['boundary_state'];hist=collections.Counter();marg=collections.Counter();canonical=[];direct_row={};count=0
  for e,m,c in decode_row(OUTPUT,row):
   assert (m+n)%2==0 and -n<=m<=n
   k=(m+n)//2;ec=e+plan['fill']*((m*m-n)//2)
   hist[e]+=c;marg[k]+=c;canonical.append((k,ec,c));count+=1
   if direct is not None:direct_row[k,(e+bound)//2]=c
  assert count==row['records'] and dict(hist)==dos[state],'JOINT_DOS_PROJECTION_MISMATCH'
  assert dict(marg)=={k+state.bit_count():math.comb(n-len(ports),k) for k in range(n-len(ports)+1)},'JOINT_MAGNETIZATION_MARGINAL'
  assert str(sum(hist.values()))==row['configurations'];total+=sum(hist.values())
  if direct is not None:assert direct_row==direct[state],'DIRECT_DENSE_JOINT_MISMATCH'
  h.update(json.dumps([state,sorted(canonical)],separators=(',',':')).encode())
 assert total==1<<n and h.hexdigest()==expected_joint_hash
 result=dict(schema='GEN4_JOINT_ENERGY_MAGNETIZATION_BOUNDARY_V1',status='EXACT_JOINT_VERIFIED',N=n,fill_coupling=plan['fill'],
  ordered_ports=ports,boundary_encoding='bit i corresponds to ordered_ports[i]; 1 is spin +1 and 0 is spin -1',
  row_columns=['energy','magnetization','configuration_count_decimal_string'],energy_convention='E=-sum_(u<v) Juv*su*sv-sum_i hi*si',
  magnetization_convention='M=sum_i si',field_extension='E_h=E-h*M; h exact rational; original couplings and fields fixed',
  correction_energy_recovery='Ecorr=E+J0*(M*M-N)/2',source_identity=IDENTITY,plan_sha256=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
  joint_spectrum_sha256=h.hexdigest(),configurations=str(total),shards=ROWS,
  verification=dict(full_DOS_projection=True,all_boundary_magnetization_binomials=True,independent_global_joint_hash=True,direct_dense_joint=n<=12),
  stored_bytes=sum(r['bytes'] for r in ROWS))
 atomic(OUTPUT/'MANIFEST.json',result);return dict(manifest=str(OUTPUT/'MANIFEST.json'),sha256=sha(OUTPUT/'MANIFEST.json'),stored_bytes=result['stored_bytes'],records=sum(r['records'] for r in ROWS),verification=result['verification'])

def query(manifest,field='0',boundary=None):
 path=Path(manifest);d=json.loads(path.read_text());assert d['status']=='EXACT_JOINT_VERIFIED';h=Fraction(field)
 p=len(d['ordered_ports']);boundary=[None]*p if boundary is None else boundary
 assert len(boundary)==p and all(x is None or x in [-1,1] for x in boundary)
 selected=[r for r in d['shards'] if all(v is None or (1 if r['boundary_state']&(1<<i) else -1)==v for i,v in enumerate(boundary))]
 total=0;first=Fraction(0);second=Fraction(0);ground=None;degeneracy=0;ground_M=collections.Counter();minima={}
 for row in selected:
  for e,m,c in decode_row(path.parent,row):
   energy=Fraction(e)-h*m;total+=c;first+=energy*c;second+=energy*energy*c
   if ground is None or energy<ground:ground=energy;degeneracy=c;ground_M=collections.Counter({m:c})
   elif energy==ground:degeneracy+=c;ground_M[m]+=c
   if m not in minima or e<minima[m][0]:minima[m]=[e,c]
   elif e==minima[m][0]:minima[m][1]+=c
 assert total==1<<(d['N']-sum(x is not None for x in boundary))
 # Lower convex envelope of E_min(M). Slopes are exact crossing fields.
 hull=[]
 for m,(e,c) in sorted(minima.items()):
  while len(hull)>1:
   a,b=hull[-2:]
   if (b[1]-a[1])*(m-b[0]) >= (e-b[1])*(b[0]-a[0]):hull.pop()
   else:break
  hull.append((m,e))
 crossings=[]
 for a,b in zip(hull,hull[1:]):
  x=Fraction(b[1]-a[1],b[0]-a[0]);g=Fraction(a[1])-x*a[0]
  coexist=[dict(M=m,degeneracy=str(c)) for m,(e,c) in sorted(minima.items()) if Fraction(e)-x*m==g]
  crossings.append(dict(field=str(x),coexisting_magnetizations=coexist))
 return dict(schema='GEN4_EXACT_JOINT_FIELD_BOUNDARY_QUERY_V1',manifest_sha256=sha(path),N=d['N'],ordered_ports=d['ordered_ports'],boundary=boundary,
  uniform_field=str(h),configurations=str(total),ground_energy=str(ground),ground_degeneracy=str(degeneracy),ground_magnetization_counts={str(k):str(v) for k,v in sorted(ground_M.items())},
  energy_sum=str(first),energy_square_sum=str(second),ground_state_crossing_fields=crossings,arithmetic='EXACT_INTEGER_COUNTS_AND_RATIONAL_FIELD',fresh_spin_enumeration=False)
