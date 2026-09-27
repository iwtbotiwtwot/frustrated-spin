"""Add latest spin research to its established publication; keep bulk custody explicit."""
from pathlib import Path
import os, json, hashlib, shutil, tarfile, gzip, re, datetime
S=Path('/home/sam/PycharmProjects/SAM_Research_Project')
D=Path('/home/sam/PycharmProjects/SLC-GEN3-R3/frustrated-spin')
W=Path('/tmp/spin-publication-latest-20260926')
TAG='frustrated-spin-joint-2026-09-26'
patterns=[re.compile(rb'rpa_[A-Za-z0-9]{20,}'),re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),re.compile(rb'github_pat_[A-Za-z0-9_]{20,}'),re.compile(rb'sk-proj-[A-Za-z0-9_-]{20,}'),re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----')]
events=[];copied=[]
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def private(p):
    return p.name in ('custody.key','.env','id_ed25519','id_rsa')
def generated(p):
    return p.suffix in ('.pyc','.pyo','.pickle','.pkl','.cubin','.o') or (p.name.endswith('.lock') and p.name!='requirements.lock')
def clean(data,label):
    compressed=label.endswith(('.json.gz','.jsonl.gz')) and data[:2]==b'\x1f\x8b'
    raw=gzip.decompress(data) if compressed else data
    new=raw
    for pattern in patterns:new=pattern.sub(b'[REDACTED_PUBLIC_CREDENTIAL]',new)
    if new!=raw:
        events.append(dict(path=label,action='CREDENTIAL_REDACTED',original_sha256=hashlib.sha256(data).hexdigest()))
        return gzip.compress(new,mtime=0) if compressed else new
    return data
def copy(p,out,label):
    data=clean(p.read_bytes(),label);out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists() or out.read_bytes()!=data:
        temp=out.with_name(out.name+'.publication-tmp');temp.write_bytes(data);os.chmod(temp,p.stat().st_mode&0o777);os.replace(temp,out)
    copied.append(dict(path=label,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
def walk(base,outbase,prefix,runtime=False):
    for root,ds,fs in os.walk(base,followlinks=False):
        ds.sort();fs.sort()
        for n in list(ds):
            p=Path(root,n);rel=p.relative_to(base);label=str(Path(prefix)/rel)
            reason=None
            if p.is_symlink():reason='LINK_RECORDED_NOT_FOLLOWED'
            elif n in ('__pycache__','.git','.pytest_cache','.venv'):reason='GENERATED_CACHE'
            elif not runtime and n=='runtime':reason='RUNTIME_RELEASE_ASSET_OR_PREDECESSOR_CUSTODY'
            elif not runtime and n=='R3_STATE':reason='PRIVATE_SESSION_STATE_RETAINED_IN_OWNER_CUSTODY'
            elif not runtime and n=='candidate':reason='DUPLICATE_CANDIDATE_RUNTIME_RETAINED_IN_OWNER_CUSTODY'
            elif not runtime and label=='GEN4/spin_joint_install1/custody/pod':reason='BULK_CUSTODY_INDEXED_SEPARATELY'
            if reason:
                events.append(dict(path=label,action=reason));ds.remove(n)
        for n in fs:
            p=Path(root,n);rel=p.relative_to(base);label=str(Path(prefix)/rel);out=outbase/rel
            if p.is_symlink():events.append(dict(path=label,action='LINK_RECORDED_NOT_FOLLOWED',target=os.readlink(p)));continue
            if private(p):events.append(dict(path=label,action='PRIVATE_AUTHENTICATION_MATERIAL'));continue
            if generated(p):continue
            if n.endswith(('.tar.gz','.tgz','.tar','.zip','.tar.zst')):
                events.append(dict(path=label,action='ORIGINAL_BUNDLE_RETAINED_IN_OWNER_CUSTODY',bytes=p.stat().st_size,sha256=digest(p)));continue
            is_final_answer='/frustrated_spin_workstation1/packet/results/' in label and n.endswith('_N001408.json.gz')
            if not runtime and p.stat().st_size>10*1024**2 and not is_final_answer:
                events.append(dict(path=label,action='LARGE_ARTIFACT_RETAINED_IN_OWNER_CUSTODY',bytes=p.stat().st_size,sha256=digest(p)));continue
            copy(p,out,label)

projects=['frustrated_spin_packet_continuation1','frustrated_spin_dense_extension1','frustrated_spin_dense_follower1','frustrated_spin_dense_solver1','frustrated_spin_magnetization2','frustrated_spin_magnetization3','frustrated_spin_joint_readout1','frustrated_spin_workstation1','frustrated_spin_transfer1','spin_joint_install1','vol_ii_joint_response1','vol_ii_joint_response2']
for name in projects:
    print('Export',name,flush=True);walk(S/'GEN4'/name,D/'GEN4'/name,'GEN4/'+name)

# Compact completed production evidence and joint table manifests, in original paths.
custody=S/'GEN4/spin_joint_install1/custody/pod/opt'
for p in sorted(custody.rglob('*')):
    if not p.is_file() or p.is_symlink() or private(p):continue
    rel=p.relative_to(custody)
    if 'runtime' in rel.parts or 'sessions' in rel.parts:continue
    if (p.name in ('MANIFEST.json','STATUS.json','README.md','CODE_MANIFEST.json','HASHES.txt','RESULT.md') or 'receipts' in rel.parts) and p.stat().st_size<2*1024**2:
        label='GEN4/spin_joint_install1/custody/pod/opt/'+str(rel);copy(p,D/label,label)

for num in (1765,1766,1767,1768):
    p=next((S/'SAM_HISTORY/entries').glob(f'H{num:06d}_*.md'));copy(p,D/'SAM_HISTORY/entries'/p.name,'SAM_HISTORY/entries/'+p.name)

print('Package promoted joint runtime',flush=True)
runtime=S/'GEN4/spin_joint_install1/pod_upgrade/runtime';stage=W/'runtime_public'
walk(runtime,stage,'RELEASE_RUNTIME',runtime=True)
asset=W/'SPIN_JOINT_RUNTIME.public.tar.gz'
with tarfile.open(asset,'w:gz',compresslevel=3) as t:
    for p in sorted(stage.rglob('*')):
        if p.is_file():t.add(p,arcname='runtime/'+str(p.relative_to(stage)),recursive=False)
release=dict(tag=TAG,assets=[dict(filename=asset.name,bytes=asset.stat().st_size,sha256=digest(asset),restore_prefix='runtime/',url=f'https://github.com/SAMresearchproject/SLC-GEN3-R3/releases/download/{TAG}/{asset.name}')])
(D/'provenance/RELEASE_JOINT_20260926.json').write_text(json.dumps(release,indent=2)+'\n')
receipt=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner='Sean Brady',source_root=str(S),destination='SAMresearchproject/SLC-GEN3-R3',projects=projects,
    scope='Latest spin source, reports, compact exact evidence, final N1408 packet answers, dense graph extension, installed joint capability and two phase-response steps. Large data custody is explicitly indexed; the upgraded public runtime is a release asset.',
    source_originals_modified=False,bulk_data_uploaded=False,bulk_custody='Verified workstation and T500 copies; see spin_joint_install1 custody manifests and omitted file identities below.',
    runtime_release=release,dispositions=events)
(D/'provenance/SYNC_JOINT_20260926.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(copied_files=len(copied),bytes=sum(x['bytes'] for x in copied),dispositions=len(events),runtime_bytes=asset.stat().st_size)),flush=True)
