"""Additive transactional installation into an existing GEN3 or GEN4 runtime.

Keeps predecessor bindings, existing catalog objects, native binary and models.
No compiler, scientific rerun, or global generation replacement is involved.
"""
import argparse
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--evidence',type=Path,required=True);args=parser.parse_args()
ROOT=args.root.resolve();E=args.evidence.resolve();E.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(ROOT))
from CURRENT_REVISION.engines.SLC.gen3.machine import implementation_binding
from CURRENT_REVISION.engines.SLC.gen2.exact import canonical_bytes,digest
from CURRENT_REVISION.engines.SLC.gen3.retained import validate

PREFIX='CURRENT_REVISION/engines/SLC/'
stage={}
def enc(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def raw(n):return stage.get(n,(ROOT/n).read_bytes() if (ROOT/n).exists() else b'')
def read(n):return json.loads(raw(n))
def put(n,v):stage[n]=v if isinstance(v,bytes) else enc(v)
def ref(n):return dict(path=n,sha256=sha(raw(n)))
def replace(n,old,new):
    s=raw(n).decode();assert s.count(old)==1,(n,old);put(n,s.replace(old,new).encode())
def verify():
    v=subprocess.run([sys.executable,'-B',str(ROOT/'CURRENT_REVISION/current.py'),'--verify'],cwd=ROOT,capture_output=True,text=True)
    if v.returncode:raise RuntimeError(v.stdout+v.stderr)
    return json.loads(v.stdout)
def atomic(path,data,mode=0o644):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.spin-install.tmp')
    with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,mode);tmp.replace(path)

before_verification=verify();baseline=implementation_binding()
bundle=json.load(gzip.open(P/'BUNDLE.json.gz','rt'))
assert digest(bundle['bundle'])==bundle['sha256']
meta=json.loads((P/'CATALOG.json').read_text());learning=json.loads((P/'MODELS.json').read_text())
index=read(PREFIX+'mathematical_library/INDEX.json')
for key,obj in bundle['bundle']['objects'].items():
    validate(obj);data=canonical_bytes(obj);assert sha(data)==key
    n=PREFIX+'mathematical_library/objects/'+key[:2]+'/'+key[2:]
    if (ROOT/n).exists():assert (ROOT/n).read_bytes()==data
    put(n,data)
    index['objects'][key]=dict(kind=obj['kind'],source_binding=obj['source_binding'],label='Exact spin '+str(obj['source_binding'].get('N',str(obj['source_binding'].get('from_N'))+'->'+str(obj['source_binding'].get('to_N')))))
index['collections']['spin_transitions']=meta
put(PREFIX+'mathematical_library/INDEX.json',canonical_bytes(index))
n=PREFIX+'gen3/retained.py';s=raw(n).decode();s,count=re.subn(r"LIBRARY_INDEX_SHA256 = '[0-9a-f]+'",'LIBRARY_INDEX_SHA256 = '+repr(sha(raw(PREFIX+'mathematical_library/INDEX.json'))),s);assert count==1;put(n,s.encode())
put(PREFIX+'gen3/spin_catalog.py',(P/'native_catalog.py').read_bytes())
put(PREFIX+'gen3/spin_methods.py',(P/'native_methods.py').read_bytes())
put(PREFIX+'gen3/spin_data/CATALOG.json',meta)
put(PREFIX+'gen3/spin_data/TRAINED_MODELS.json',learning)
put(PREFIX+'SPIN_CATALOG.md',(P/'GUIDE.md').read_bytes())
modelname=meta['native_model'];models=read(PREFIX+'gen3/capabilities/MODELS.json')
for name,record in learning.items():
    assert name not in models['models'],name
    models['models'][name]=record['model'];models['source_binding'][name]=record['source_binding']
put(PREFIX+'gen3/capabilities/MODELS.json',models)
manifest=read(PREFIX+'gen3/capabilities/MANIFEST.json')
for name in manifest['files']:manifest['files'][name]=ref(PREFIX+'gen3/capabilities/'+name)['sha256']
put(PREFIX+'gen3/capabilities/MANIFEST.json',manifest)
migration=read(PREFIX+'gen3/CAPABILITY_MIGRATIONS.json')
if baseline not in migration['predecessor_bindings']:migration['predecessor_bindings'].insert(0,baseline)
put(PREFIX+'gen3/CAPABILITY_MIGRATIONS.json',migration)
interface=read(PREFIX+'INTERFACE.json')
for op in ['CATALOG','ENTRY','TRANSITION','PLAN','LEARNING']:interface['operations']['GEN3_SPIN_'+op]='Source-bound exact spin catalog and transition planning; see SPIN_CATALOG.md'
put(PREFIX+'INTERFACE.json',interface)
registry=read('CURRENT_REVISION/REGISTRY.json')
extra=[n for n in stage if n.startswith(PREFIX) and '/mathematical_library/objects/' not in n]
for section in ['engines','domains']:
    for name,record in registry[section].items():
        row=read(record['path']);paths={r['path'] for r in row.get('binding_sources',[])}
        if name=='SLC':paths.update(extra)
        row['binding_sources']=[ref(n) for n in sorted(paths)]
        if row.get('runtime_path'):row['runtime_sha256']=ref(row['runtime_path'])['sha256']
        put(record['path'],row)
for section in ['engines','domains']:registry[section]={k:ref(v['path']) for k,v in registry[section].items()}
registry['control_plane']=[ref(r['path']) for r in registry['control_plane']]
put('CURRENT_REVISION/REGISTRY.json',registry)
generation=read('CURRENT_REVISION/GENERATION.json');generation.update(engines=registry['engines'],domains=registry['domains'],control_plane=registry['control_plane']);put('CURRENT_REVISION/GENERATION.json',generation)
slc=read(registry['engines']['SLC']['path']);selector=read('SLC/18_SAM_NATIVE_QC/CURRENT_SLC_REVISION.json')
selector.update(native_runtime_sha256=slc['runtime_sha256'],current_registry_file_sha256=ref('CURRENT_REVISION/REGISTRY.json')['sha256'],generation_manifest_sha256=ref('CURRENT_REVISION/GENERATION.json')['sha256'])
put('SLC/18_SAM_NATIVE_QC/CURRENT_SLC_REVISION.json',selector);put(PREFIX+'selection.json',selector)
if (ROOT/'RELEASE.json').exists():
    release=read('RELEASE.json');release['predecessor_content_sha256']=release['content_sha256']
    for n in stage:release['files'][n]=ref(n)['sha256']
    release['content_sha256']=sha(canonical_bytes(release['files']));release['additive_spin_catalog']='GEN4_SPIN_ALL96_TRAINED_CATALOG_V2';put('RELEASE.json',release)
stage={n:data for n,data in stage.items() if not (ROOT/n).exists() or (ROOT/n).read_bytes()!=data}
before={n:sha((ROOT/n).read_bytes()) for n in stage if (ROOT/n).exists()};new=[n for n in stage if not (ROOT/n).exists()]
for n in before:
    dst=E/'predecessor'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dst)
for n,data in stage.items():atomic(E/'staged'/n,data)
atomic(E/'STAGED.json',enc(dict(before=before,new=new,files={n:sha(v) for n,v in stage.items()},baseline=baseline)))
lockpath=ROOT/'SAM_RUNTIME/R3/run.lock';lockpath.parent.mkdir(parents=True,exist_ok=True)
marker=ROOT/'CURRENT_REVISION/ACTIVATION_IN_PROGRESS.json'
with lockpath.open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert implementation_binding()==baseline
    for n,h in before.items():assert sha((ROOT/n).read_bytes())==h,n
    for n in new:assert not (ROOT/n).exists(),n
    with marker.open('x') as f:json.dump(dict(action='ADDITIVE_SPIN_CATALOG_INSTALL',evidence=str(E)),f)
    changed=[]
    try:
        for n,data in stage.items():
            atomic(ROOT/n,data,(ROOT/n).stat().st_mode&0o777 if (ROOT/n).exists() else 0o644);changed.append(n)
        marker.unlink();verification=verify()
    except BaseException:
        atomic(marker,enc(dict(action='SPIN_CATALOG_ROLLBACK')))
        for n in changed:
            if n in before:atomic(ROOT/n,(E/'predecessor'/n).read_bytes(),(E/'predecessor'/n).stat().st_mode&0o777)
            else:
                dst=E/'failed_new'/n;dst.parent.mkdir(parents=True,exist_ok=True);os.replace(ROOT/n,dst)
        marker.unlink();raise
atomic(E/'INSTALLED.json',enc(dict(status='INSTALLED_ADOPTION_PENDING',verification=verification,before_verification=before_verification,
                                 entries=len(meta['entries']),transitions=len(meta['transitions']),objects=len(index['objects']),native_model=modelname,files=len(stage))))
print((E/'INSTALLED.json').read_text())
