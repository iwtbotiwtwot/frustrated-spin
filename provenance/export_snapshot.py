"""Build an additive public spin snapshot without changing research originals."""
from pathlib import Path, PurePosixPath
import os, json, hashlib, shutil, tarfile, gzip, io, re, time

SOURCE = Path('/home/sam/PycharmProjects/SAM_Research_Project')
DEST = Path('/home/sam/PycharmProjects/SLC-GEN3-R3/frustrated-spin')
WORK = Path('/tmp/spin-publication-20260926')
DEST.mkdir(parents=True, exist_ok=True)
events = []
patterns = [re.compile(rb'rpa_[A-Za-z0-9]{20,}'),
            re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),
            re.compile(rb'github_pat_[A-Za-z0-9_]{20,}'),
            re.compile(rb'sk-proj-[A-Za-z0-9_-]{20,}'),
            re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----')]

def sha(data): return hashlib.sha256(data).hexdigest()
def filehash(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def archive_name(name): return name.endswith(('.tar.gz', '.tgz', '.tar', '.tar.zst'))
def reason(name):
    p = PurePosixPath(name)
    if p.name in ('custody.key', '.env', 'id_ed25519', 'id_rsa'): return 'PRIVATE_AUTHENTICATION_MATERIAL'
    if any(s in p.parts for s in ('__pycache__', '.git', '.pytest_cache', '.venv')): return 'GENERATED_CACHE'
    if p.suffix in ('.pyc','.pyo','.pickle','.pkl','.cubin','.so','.o') or p.name.endswith('.lock'): return 'GENERATED_EXECUTION_CACHE'
    if p.name.endswith('_KERNELS.csv'): return 'BULK_PER_KERNEL_TRACE_RETAINED_PRIVATELY'
    return None
def note(path, action, **kw): events.append(dict(source=path, action=action, **kw))
def clean(data, label):
    out=data
    for pattern in patterns: out=pattern.sub(b'[REDACTED_PUBLIC_CREDENTIAL]', out)
    if out != data: note(label,'REDACTED_CREDENTIAL',source_sha256=sha(data),public_sha256=sha(out))
    return out
def clean_payload(data,label):
    if data.startswith(b'\x1f\x8b') and label.endswith(('.json.gz','.jsonl.gz')):
        raw=gzip.decompress(data);new=clean(raw,label+'!decompressed')
        return gzip.compress(new,mtime=0) if raw!=new else data
    return clean(data,label)
def sanitize_archive(src, out, label):
    out.parent.mkdir(parents=True,exist_ok=True)
    original_hash=filehash(src)
    members=0
    with tarfile.open(src,'r:*') as tin, tarfile.open(out,'w:gz',compresslevel=6) as tout:
        for m in tin:
            name=m.name; parts=PurePosixPath(name).parts
            if name.startswith('/') or '..' in parts: raise RuntimeError('Unsafe archive path '+label+'!'+name)
            why=reason(name)
            if why:
                note(label+'!'+name,why,bytes=m.size);continue
            if not m.isfile():
                if m.issym() or m.islnk(): note(label+'!'+name,'ARCHIVE_LINK_NOT_EXPORTED',target=m.linkname)
                continue
            stream=tin.extractfile(m)
            if archive_name(name):
                tmp=WORK/('nested-'+sha((label+'!'+name).encode()))
                with tmp.open('wb') as f:shutil.copyfileobj(stream,f)
                sub=tmp.with_suffix('.public.tar.gz')
                sanitize_archive(tmp,sub,label+'!'+name)
                data=sub.read_bytes();tmp.unlink();sub.unlink()
            else: data=clean_payload(stream.read(),label+'!'+name)
            m.size=len(data);m.uid=m.gid=0;m.uname=m.gname='';m.mode &= 0o777
            tout.addfile(m,io.BytesIO(data));members+=1
    note(label,'SANITIZED_ARCHIVE',source_sha256=original_hash,public_path=str(out.relative_to(DEST)) if out.is_relative_to(DEST) else None,public_sha256=filehash(out),public_bytes=out.stat().st_size,members=members)

duplicate_archives={
 'GEN4/frustrated_spin_packet_catalog1/COMPLETE.tar.gz':'expanded campaign files',
 'GEN4/frustrated_spin_n300_courtroom1/COMPLETED_RESULTS.tar.gz':'expanded campaign files',
 'GEN4/frustrated_spin_training1/completed.tar.gz':'results/',
 'GEN4/frustrated_spin_full96_training1/completed.tar.gz':'results/',
 'GEN4/frustrated_spin_n1_30_training1/completed.tar.gz':'results/',
 'GEN4/frustrated_spin_focused_training1/focused-completed.tar.gz':'focused-results/',
 'GEN4/frustrated_spin_focused_training1/fast-completed.tar.gz':'fast-results/',
 'GEN4/frustrated_spin_focused_training1/boundary-completed.tar.gz':'boundary-results/',
 'GEN4/frustrated_spin_focused_training1/boundary-fast-completed.tar.gz':'boundary-fast-results/',
 'GEN4/frustrated_spin_catalog1/completed.tar.gz':'results/',
 'GEN4/frustrated_spin_focused_training1/restart/runtime-predecessor.tar.gz':'historical runtime predecessor; current campaign runtime exported separately',
}

def copy_tree(base, destbase, prefix):
    for root,ds,fs in os.walk(base,followlinks=False):
        ds.sort();fs.sort()
        for d in list(ds):
            p=Path(root,d);rel=p.relative_to(base);label=str(PurePosixPath(prefix)/rel)
            if p.is_symlink():
                note(label,'SYMLINK_NOT_DEREFERENCED',target=os.readlink(p));ds.remove(d)
            elif d in ('__pycache__','.git','.pytest_cache','.venv'):
                note(label,'GENERATED_CACHE_DIRECTORY');ds.remove(d)
            elif d=='runtime':
                note(label,'SHARED_RUNTIME_PACKAGED_SEPARATELY');ds.remove(d)
        for f in fs:
            p=Path(root,f);rel=p.relative_to(base);label=str(PurePosixPath(prefix)/rel);out=destbase/rel
            if p.is_symlink():note(label,'SYMLINK_NOT_DEREFERENCED',target=os.readlink(p));continue
            why=reason(str(rel))
            if why:
                info={'bytes':p.stat().st_size}
                if why!='PRIVATE_AUTHENTICATION_MATERIAL':info['sha256']=filehash(p)
                note(label,why,**info);continue
            if label in duplicate_archives:
                note(label,'ORIGINAL_BUNDLE_RETAINED_PRIVATELY',sha256=filehash(p),bytes=p.stat().st_size,public_evidence=duplicate_archives[label]);continue
            if archive_name(f):
                # The preregistered N300 archive is already credential-free; preserve its exact seal.
                if label=='GEN4/frustrated_spin_n300_courtroom1/PRECOMMIT.tar.gz':
                    with tarfile.open(p) as t:
                        for m in t:
                            assert not reason(m.name)
                            if m.isfile():
                                b=t.extractfile(m).read();assert clean(b,label+'!'+m.name)==b
                    out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
                else:
                    suffix='.public.tar.gz';out=out.with_name(out.name+suffix)
                    sanitize_archive(p,out,label)
                continue
            data=p.read_bytes();new=clean_payload(data,label)
            out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(new);os.chmod(out,p.stat().st_mode & 0o777)

projects=sorted(p for p in (SOURCE/'GEN4').iterdir() if p.name.startswith(('frustrated_spin','spin_gap','spin_tools')) and p.is_dir())
for p in projects:
    if p.name=='frustrated_spin_pod14_learning1':
        copy_tree(p,DEST/'provenance/workstation_pod14_snapshot','WORKSTATION_POD14_SNAPSHOT')
        p=WORK/'pod14/frustrated_spin_pod14_learning1'
    print('Export',p.name,flush=True)
    copy_tree(p,DEST/'GEN4'/p.name,'GEN4/'+p.name)
    (DEST/'provenance').mkdir(exist_ok=True)
    (DEST/'provenance/EXPORT_DISPOSITIONS.json').write_text(json.dumps(events,indent=2)+'\n')

# One relocatable runtime archive, preserving the campaign's private-vs-public boundary.
runtime=SOURCE/'GEN4/frustrated_spin_learning1/runtime'
runtime_stage=WORK/'runtime_public'
print('Export shared runtime',flush=True)
copy_tree(runtime,runtime_stage,'RUNTIME')
with tarfile.open(DEST/'GEN4/frustrated_spin_learning1/RUNTIME.public.tar.gz','w:gz',compresslevel=6) as t:
    for p in sorted(runtime_stage.rglob('*')):
        if p.is_file():t.add(p,arcname='runtime/'+str(p.relative_to(runtime_stage)),recursive=False)
(DEST/'provenance/EXPORT_DISPOSITIONS.json').write_text(json.dumps(events,indent=2)+'\n')
print('DONE',len(events),'dispositions',flush=True)
