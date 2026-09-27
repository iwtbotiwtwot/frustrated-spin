"""Seal the verified scoped successor and select it without touching predecessor runs."""
import json,pathlib,hashlib,datetime,subprocess,sys
p=pathlib.Path('/opt/gen4-spin-joint-upgrade1');root=p/'runtime';sys.path.insert(0,str(root))
q=json.loads((p/'qualification2/QUALIFICATION.json').read_text());a=json.loads((p/'adoption_final/ADOPTION.json').read_text());assert q['status']==a['status']=='PASS'
from CURRENT_REVISION.runtime import verify,record
from CURRENT_REVISION.engines.SLC.gen2.exact import canonical_bytes
v=verify();assert v['status']=='PASS'
release=json.loads((root/'RELEASE.json').read_text());before=(root/'RELEASE.json').read_bytes()
missing=[n for n in release['files'] if not (root/n).exists()]
assert sorted(missing)==['CURRENT_REVISION/domains/MP/factor-kernel.so','requirements.lock'],missing
# Restore the inherited optional domain ABI from its unchanged authenticated C source.
kernel=(root/'CURRENT_REVISION/domains/MP/kernel.py').read_text()
assert "binary = HERE / 'factor-kernel.so'" in kernel
source=root/'CURRENT_REVISION/domains/MP/factor_kernel.c'
assert hashlib.sha256(source.read_bytes()).hexdigest()==release['files']['CURRENT_REVISION/domains/MP/factor_kernel.c']
subprocess.run(['cc','-O3','-std=c11','-fPIC','-shared','-fopenmp',str(source),'-o',str(root/'CURRENT_REVISION/domains/MP/factor-kernel.so')],check=True,capture_output=True)
(p/'RELEASE_PRE_SEAL_REPAIR.json').write_bytes(before)
old={n:release['files'].pop(n) for n in missing}
requirements=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
(root/'requirements.lock').write_text(requirements)
release['files']['requirements.lock']=hashlib.sha256(requirements.encode()).hexdigest()
release['files']['CURRENT_REVISION/domains/MP/factor-kernel.so']=hashlib.sha256((root/'CURRENT_REVISION/domains/MP/factor-kernel.so').read_bytes()).hexdigest()
release['predecessor_content_sha256']=release['content_sha256'];release['content_sha256']=hashlib.sha256(canonical_bytes(release['files'])).hexdigest()
(root/'RELEASE.json').write_text(json.dumps(release,sort_keys=True,indent=2)+'\n')
repair=dict(inherited_missing_entries=old,action='Restore required binary from unchanged authenticated C source; restore lock from actual qualified Python environment',MP_source_or_execution_changed=False)
(p/'SEAL_REPAIR.json').write_text(json.dumps(repair,indent=2)+'\n')
for n,h in release['files'].items():assert hashlib.sha256((root/n).read_bytes()).hexdigest()==h,n
pointer=pathlib.Path('/opt/gen4');pointer.mkdir(exist_ok=True);current=pointer/'current'
assert not current.exists() and not current.is_symlink();current.symlink_to(root,target_is_directory=True)
out=dict(status='PROMOTED_INSTALLED_AND_ADOPTED',capability='SHARED_SPIN_JOINT_V1',runtime=str(root),current=str(current),previous_runtime='/opt/gen4-spin-continuation1/runtime',
 timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),global_slc=record('SLC')['version'],ce=record('CE')['version'],qualification_checks=q['check_count'],adoption_checks=len(a['checks']),verification=v,release_sha256=hashlib.sha256((root/'RELEASE.json').read_bytes()).hexdigest())
(p/'PROMOTION.json').write_text(json.dumps(out,indent=2)+'\n');(pointer/'CURRENT_SHARED_CAPABILITY.json').write_text(json.dumps(out,indent=2)+'\n')
(p/'ENVIRONMENT.json').write_text(json.dumps(dict(python=sys.version,packages=requirements.splitlines()),indent=2)+'\n')
rows=[]
for f in sorted(p.rglob('*')):
 if f.is_file() and '__pycache__' not in f.parts:
  rows.append(dict(path=str(f.relative_to(p)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(p/'FINAL_DOWNLOAD_MANIFEST.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(out))
