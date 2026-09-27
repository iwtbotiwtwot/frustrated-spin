"""Transactional additive installation of shared packet/joint spin capabilities."""
import argparse,fcntl,gzip,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--evidence',type=Path,required=True);a=ap.parse_args()
R=a.root.resolve();E=a.evidence.resolve();E.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(R))
from CURRENT_REVISION.engines.SLC.gen3.machine import implementation_binding
from CURRENT_REVISION.engines.SLC.gen2.exact import canonical_bytes,digest
from CURRENT_REVISION.engines.SLC.gen3.retained import validate
SLC='CURRENT_REVISION/engines/SLC/';stage={}
sha=lambda b:hashlib.sha256(b).hexdigest()
def raw(n):return stage[n] if n in stage else (R/n).read_bytes()
def read(n):return json.loads(raw(n))
def put(n,v):stage[n]=v if isinstance(v,bytes) else (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def ref(n):return dict(path=n,sha256=sha(raw(n)))
def verify():
 r=subprocess.run([sys.executable,'-B',str(R/'CURRENT_REVISION/current.py'),'--verify'],cwd=R,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return json.loads(r.stdout)
def atomic(f,b,mode=0o644):
 f.parent.mkdir(parents=True,exist_ok=True);tmp=f.with_name(f.name+'.spin-tools.tmp')
 with tmp.open('wb') as s:s.write(b);s.flush();os.fsync(s.fileno())
 os.chmod(tmp,mode);tmp.replace(f)
def replace(n,old,new):
 s=raw(n).decode();assert s.count(old)==1,(n,old);put(n,s.replace(old,new).encode())
before_verify=verify();baseline=implementation_binding()
meta=json.loads((P/'package/spin_data/CATALOG.json').read_text())
sources=json.loads((P/'package/spin_data/SOURCES.json').read_text())
assert meta['sizes']==list(range(1,121))
prior=read(SLC+'gen3/spin_data/CATALOG.json')
assert all(meta['entries'][k]==v for k,v in prior['entries'].items())
bundle=json.load(gzip.open(P/'COLLECTION.json.gz','rt'));assert digest(bundle['bundle'])==bundle['sha256']
index=read(SLC+'mathematical_library/INDEX.json');oldobjects=dict(index['objects'])
prerequisites=json.load(gzip.open(P/'PREREQUISITES.json.gz','rt'))
for key,obj in dict(prerequisites,**bundle['bundle']['objects']).items():
 validate(obj);data=canonical_bytes(obj);assert sha(data)==key
 name=SLC+'mathematical_library/objects/'+key[:2]+'/'+key[2:]
 if (R/name).exists():assert (R/name).read_bytes()==data
 put(name,data);index['objects'].setdefault(key,dict(kind=obj['kind'],source_binding=obj['source_binding'],label='Exact source-bound spin input'))
assert all(index['objects'][k]==v for k,v in oldobjects.items())
index['collections']['spin_transitions']=meta;index['collections']['spin_sources']=sources
index['collections']['spin_joint']=json.loads((P/'package/spin_data/JOINT_CATALOG.json').read_text())
put(SLC+'mathematical_library/INDEX.json',canonical_bytes(index))
for f in sorted((P/'package').rglob('*')):
 if f.is_file() and '__pycache__' not in f.parts:put(SLC+'gen3/'+str(f.relative_to(P/'package')),f.read_bytes())
n=SLC+'gen3/retained.py';s,count=re.subn(r"LIBRARY_INDEX_SHA256 = '[0-9a-f]+'",'LIBRARY_INDEX_SHA256 = '+repr(sha(raw(SLC+'mathematical_library/INDEX.json'))),raw(n).decode());assert count==1;put(n,s.encode())
put(SLC+'SPIN_JOINT.md',(P/'GUIDE.md').read_bytes())
put(SLC+'SPIN_TOOLS.md',(raw(SLC+'SPIN_TOOLS.md') if (R/(SLC+'SPIN_TOOLS.md')).exists() else (P/'BASE_GUIDE.md').read_bytes())+b'\nShared extension: [packet compilation and joint readout](SPIN_JOINT.md), SHARED_SPIN_JOINT_V1.\n')
for old,new in [('from .gen3.spin_catalog import dispatch','from .gen3.spin_tools import dispatch'),('from .gen3.spin_catalog import OPS as spin_ops','from .gen3.spin_tools import OPS as spin_ops')]:
 if old in raw(SLC+'gen3_runtime.py').decode():replace(SLC+'gen3_runtime.py',old,new)
 else:assert raw(SLC+'gen3_runtime.py').decode().count(new)==1
interface=read(SLC+'INTERFACE.json')
for op in ['TOOLS','SOURCES','SOURCE','SELECT','SOLVE','READOUT']:
 interface['operations']['GEN3_SPIN_'+op]='Source-aware exact spin tool, including packet/joint extension; see SPIN_TOOLS.md and SPIN_JOINT.md'
put(SLC+'INTERFACE.json',interface)
m=read(SLC+'gen3/CAPABILITY_MIGRATIONS.json')
if baseline not in m['predecessor_bindings']:m['predecessor_bindings'].insert(0,baseline)
put(SLC+'gen3/CAPABILITY_MIGRATIONS.json',m)
registry=read('CURRENT_REVISION/REGISTRY.json');extra=[n for n in stage if n.startswith('CURRENT_REVISION/') and '/mathematical_library/objects/' not in n]
for group in ['engines','domains']:
 for name,record in registry[group].items():
  row=read(record['path']);paths={x['path'] for x in row.get('binding_sources',[])}
  if name=='SLC':paths.update(extra)
  row['binding_sources']=[ref(n) for n in sorted(paths)]
  if row.get('runtime_path'):row['runtime_sha256']=ref(row['runtime_path'])['sha256']
  put(record['path'],row)
for group in ['engines','domains']:registry[group]={k:ref(v['path']) for k,v in registry[group].items()}
registry['control_plane']=[ref(x['path']) for x in registry['control_plane']];put('CURRENT_REVISION/REGISTRY.json',registry)
g=read('CURRENT_REVISION/GENERATION.json');g.update(engines=registry['engines'],domains=registry['domains'],control_plane=registry['control_plane']);put('CURRENT_REVISION/GENERATION.json',g)
slc=read(registry['engines']['SLC']['path']);selector=read('SLC/18_SAM_NATIVE_QC/CURRENT_SLC_REVISION.json')
selector.update(native_runtime_sha256=slc['runtime_sha256'],current_registry_file_sha256=ref('CURRENT_REVISION/REGISTRY.json')['sha256'],generation_manifest_sha256=ref('CURRENT_REVISION/GENERATION.json')['sha256'])
put('SLC/18_SAM_NATIVE_QC/CURRENT_SLC_REVISION.json',selector);put(SLC+'selection.json',selector)
if (R/'RELEASE.json').exists():
 rel=read('RELEASE.json');rel['predecessor_content_sha256']=rel['content_sha256']
 for n in stage:rel['files'][n]=ref(n)['sha256']
 rel['content_sha256']=sha(canonical_bytes(rel['files']));rel['additive_spin_joint']='SHARED_SPIN_JOINT_V1';put('RELEASE.json',rel)
stage={n:b for n,b in stage.items() if not (R/n).exists() or (R/n).read_bytes()!=b}
before={n:sha((R/n).read_bytes()) for n in stage if (R/n).exists()};new=[n for n in stage if not (R/n).exists()]
for n in before:
 dst=E/'predecessor'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,dst)
for n,b in stage.items():atomic(E/'staged'/n,b)
atomic(E/'STAGED.json',(json.dumps(dict(before=before,new=new,files={n:sha(b) for n,b in stage.items()},baseline=baseline),indent=2)+'\n').encode())
lockpath=R/'SAM_RUNTIME/R3/run.lock';lockpath.parent.mkdir(parents=True,exist_ok=True);marker=R/'CURRENT_REVISION/ACTIVATION_IN_PROGRESS.json'
with lockpath.open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assert implementation_binding()==baseline
 for n,h in before.items():assert sha((R/n).read_bytes())==h,n
 for n in new:assert not (R/n).exists(),n
 with marker.open('x') as s:json.dump(dict(action='ADDITIVE_SPIN_TOOLS_INSTALL',evidence=str(E)),s)
 changed=[]
 try:
  for n,b in stage.items():
   mode=0o755 if n=='spin-tools' else ((R/n).stat().st_mode&0o777 if (R/n).exists() else 0o644)
   atomic(R/n,b,mode);changed.append(n)
  marker.unlink();verification=verify()
 except BaseException:
  atomic(marker,b'{"action":"SPIN_TOOLS_ROLLBACK"}')
  for n in changed:
   if n in before:atomic(R/n,(E/'predecessor'/n).read_bytes(),(E/'predecessor'/n).stat().st_mode&0o777)
   else:
    dst=E/'failed_new'/n;dst.parent.mkdir(parents=True,exist_ok=True);os.replace(R/n,dst)
  marker.unlink();raise
out=dict(status='INSTALLED_ADOPTION_PENDING',entries=len(meta['entries']),objects_before=len(oldobjects),objects_after=len(index['objects']),files=len(stage),generation=g['generation'] if 'generation' in g else g.get('id'),verification=verification,before_verification=before_verify)
atomic(E/'INSTALLED.json',(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(out))
