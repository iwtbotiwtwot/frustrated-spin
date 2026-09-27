"""Create immutable restart and mathematical-result layers from a completed cut."""
from pathlib import Path
import os,json,hashlib,tarfile,subprocess,threading,time,shutil,io,gzip
BASE=Path('/opt/gen4-spin-transfer1')
PACKET=Path('/opt/gen4-spin-continuation1/project')
FOLLOWER=Path('/opt/gen4-spin-dense-follower1/project')
DENSE=Path('/opt/gen4-spin-dense-solver1/project')
RESUME=Path('/opt/gen4-spin-resume1/project')
CHUNK=64*1024**2

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.part');q.write_text(json.dumps(v,indent=2)+'\n');q.replace(p)
def files(root):
    return [p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and not p.name.endswith('.part')]
def pack(dest,entries,metadata):
    dest.mkdir(parents=True,exist_ok=True);z=subprocess.Popen(['nice','-n','15','zstd','-q','-1','-T1','-c'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    parts=[];error=[]
    def consume():
        try:
            idx=0
            while True:
                blob=z.stdout.read(CHUNK)
                if not blob:break
                name=f'part-{idx:05d}';p=dest/(name+'.partial');p.write_bytes(blob);p.rename(dest/name)
                parts.append(dict(file=name,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()));idx+=1
        except Exception as e:error.append(repr(e))
    worker=threading.Thread(target=consume);worker.start()
    try:
        with tarfile.open(fileobj=z.stdin,mode='w|') as t:
            for path,name in entries:
                t.add(path,arcname=name,recursive=False)
            data=(json.dumps(metadata,indent=2)+'\n').encode();info=tarfile.TarInfo('BUNDLE.json');info.size=len(data);info.mode=0o600;t.addfile(info,io.BytesIO(data))
    finally:z.stdin.close()
    worker.join();assert z.wait()==0 and not error,error
    manifest=dict(**metadata,parts=parts,compressed_bytes=sum(r['bytes'] for r in parts),archive='Concatenate numbered parts in order; zstd-decompress; tar-extract',entry_count=len(entries))
    save(dest/'MANIFEST.json',manifest);save(dest/'READY.json',dict(status='READY',manifest_sha256=sha(dest/'MANIFEST.json')))
    return manifest

def build(name,after=120):
    dest=BASE/name
    if (dest/'DONE.json').exists():return
    dest.mkdir(parents=True,exist_ok=True);stage=dest/'snapshot';stage.mkdir(exist_ok=True)
    ps=json.loads((PACKET/'STATUS.json').read_text());fs=json.loads((FOLLOWER/'STATUS.json').read_text())
    cut=min(ps['last_completed_N'],fs['last_contiguous_N']);assert cut>=1300
    rows=[json.loads(l) for l in (PACKET/'CATALOG.jsonl').read_text().splitlines()];rows=[r for r in rows if r['N']<=cut]
    latest=[r for r in rows if r['N']==cut];assert len(latest)==3
    for r in latest:assert sha(PACKET/r['artifact'])==r['sha256']
    sources=[(PACKET/'sources'/Path(r['artifact']).name.replace('.json.gz','.json')) for r in latest]
    snap=dict(ps,status='TRANSFER_CHECKPOINT',last_completed_N=cut,next_N=cut+1,current_N=None,
        completed_source_cases=sum(r['N']>=121 for r in rows),transfer_cut_N=cut,pod_observed_status=ps['status'])
    save(stage/'STATUS.json',snap);save(stage/'POD_OBSERVED_STATUS.json',ps)
    save(stage/'CHECKPOINT.json',dict(last_completed_N=cut,latest_artifacts=latest,transfer_snapshot=True))
    (stage/'CATALOG.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for p in PACKET.iterdir():
        if p.is_file() and p.name not in ['STOP','controller.lock','STATUS.json','CHECKPOINT.json','CATALOG.jsonl']:
            shutil.copyfile(p,stage/p.name)
    event_lines=[]
    for line in (stage/'EVENTS.jsonl').read_text().splitlines():
        try:r=json.loads(line)
        except json.JSONDecodeError:continue
        if r.get('N',0)<=cut:event_lines.append(json.dumps(r))
    (stage/'EVENTS.jsonl').write_text('\n'.join(event_lines)+'\n')
    core=[(p,'packet/'+p.name) for p in stage.iterdir() if p.is_file()]
    for sub in ['inputs','vendor','identities','setup_history']:
        core += [(p,'packet/'+str(p.relative_to(PACKET))) for p in files(PACKET/sub)]
    core += [(PACKET/r['artifact'],'packet/'+r['artifact']) for r in latest]
    core += [(p,'packet/sources/'+p.name) for p in sources]
    for p in FOLLOWER.iterdir():
        if p.is_file() and p.name not in ['STOP','controller.lock']:
            target=stage/'follower'/p.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);core.append((target,'follower/'+p.name))
    fstatus=json.loads((stage/'follower/STATUS.json').read_text())
    fstatus.update(status='TRANSFER_CHECKPOINT',last_contiguous_N=cut,completed_N_count=cut,generated_graphs=cut*6)
    save(stage/'follower/STATUS.json',fstatus)
    index=[json.loads(line) for line in (stage/'follower/INDEX.jsonl').read_text().splitlines() if line.strip()]
    (stage/'follower/INDEX.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in index if r['N']<=cut))
    # Full tiny source-generator recovery seed, and every required latest graph.
    seed=Path('/opt/gen4-spin-dense-follower1/seed_catalog')
    core += [(p,'seed_catalog/'+str(p.relative_to(seed))) for p in files(seed)]
    for n in {cut,fs['last_contiguous_N']}:
        folder=FOLLOWER/'graphs'/f'N{n:06d}'
        core += [(p,'follower/'+str(p.relative_to(FOLLOWER))) for p in files(folder)]
    core += [(p,'resume/'+p.name) for p in RESUME.iterdir() if p.is_file() and p.name not in ['controller.lock']]
    core += [(p,'dense_solver/'+str(p.relative_to(DENSE))) for p in files(DENSE) if p.name not in ['STOP','controller.lock']]
    metadata=dict(schema='GEN4_SPIN_MIGRATION_V1',snapshot=name,cut_N=cut,after_N=after,created_unix=time.time(),
        packet_exact_cases=sum(r['N']>=121 for r in rows),latest_artifacts=latest,
        runtime_sha256='79f4d7afe7b357fe988dfc737c7a223017b68518aa362c4c0fc2e2f440e462cc',
        scope='Restart code, checkpoint, latest full answers, seed, completed dense solver; historical answers in separate layer',
        source_pod='/opt/gen4-spin-continuation1',pod_was_running=ps['status']=='RUNNING')
    pack(dest/'restart',core,dict(metadata,layer='restart'))
    history=[]
    for r in rows:
        if after<r['N']<=cut:
            history.append((PACKET/r['artifact'],'packet/'+r['artifact']))
            path=PACKET/'sources'/Path(r['artifact']).name.replace('.json.gz','.json');history.append((path,'packet/sources/'+path.name))
    for folder in sorted((FOLLOWER/'graphs').glob('N*')):
        n=int(folder.name[1:])
        if (name=='initial' or n>after) and n<=cut:history += [(p,'follower/'+str(p.relative_to(FOLLOWER))) for p in files(folder)]
    # Preserve native input/receipt descriptors; giant OUTPUT payloads remain on pod.
    # Their mathematical content is retained in full exact result files above.
    # This is a restart + mathematical-result backup, not a byte-complete native-session backup.
    for p in files(PACKET/'sessions'):
        if p.name!='OUTPUT.json.gz':
            target=stage/'native_metadata'/p.relative_to(PACKET/'sessions');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            history.append((target,'packet/sessions/'+str(p.relative_to(PACKET/'sessions'))))
    pack(dest/'history',history,dict(metadata,layer='history',
        scope='Full exact mathematical answers including independent references, sources, dense graphs and native metadata',
        omitted='Native packet OUTPUT.json.gz payload copies; retained on pod. This layer is not a full native-session restore.'))
    save(dest/'DONE.json',dict(status='PACKAGED',cut_N=cut,after_N=after))
    print(json.dumps(dict(status='PACKAGED',snapshot=name,cut_N=cut)),flush=True)

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('name');a.add_argument('--after',type=int,default=120);args=a.parse_args();os.nice(10);build(args.name,args.after)
