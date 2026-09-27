"""Detached four-stream pod -> T500 copy with per-chunk SHA-256 and restart."""
from pathlib import Path
import subprocess,shlex,json,time,hashlib,concurrent.futures,os,signal,traceback,fcntl
P=Path(__file__).resolve().parent
KEY='/home/sam/.ssh/id_ed25519'
POD=['ssh','-p','11136','-i',KEY,'-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','Compression=no','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3','root@69.8.146.173']
HELPER=['ssh','-i',KEY,'-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','Compression=no','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3','lilhelper@10.77.0.2']
DEST='/home/lilhelper/SAM_Research_Project/SAM_POD_BACKUPS/frustrated-spin-20260926'
REMOTE='/opt/gen4-spin-transfer1'
STOP=False
STATE={}
RUNTIME='/tmp/spin-publication-20260926/RUNTIME.public.tar.gz'
RUNTIME_SHA='79f4d7afe7b357fe988dfc737c7a223017b68518aa362c4c0fc2e2f440e462cc'
RECEIVER=r'''
import sys,os,hashlib
from pathlib import Path
p=Path(sys.argv[1]);expected=sys.argv[2];size=int(sys.argv[3]);p.parent.mkdir(parents=True,exist_ok=True)
q=p.with_name(p.name+'.partial');h=hashlib.sha256();count=0
with q.open('wb') as f:
 while data:=sys.stdin.buffer.read(4*1024*1024):f.write(data);h.update(data);count+=len(data)
 f.flush();os.fsync(f.fileno())
assert count==size and h.hexdigest()==expected,(count,size,h.hexdigest(),expected)
q.replace(p)
'''
EXTRACT=r'''
from pathlib import Path
import sys,json,subprocess,tarfile,threading,hashlib,os
base=Path(sys.argv[1]);layer=sys.argv[2];dst=Path(sys.argv[3]);m=json.loads((base/'MANIFEST.json').read_text());marker=base/'EXTRACTED.json'
if marker.exists():print(marker.read_text());sys.exit(0)
dst.mkdir(parents=True,exist_ok=True);z=subprocess.Popen(['zstd','-d','-q','-c'],stdin=subprocess.PIPE,stdout=subprocess.PIPE);errors=[]
def feed():
 try:
  for row in m['parts']:
   p=base/row['file'];h=hashlib.sha256()
   with p.open('rb') as f:
    while data:=f.read(4*1024*1024):h.update(data);z.stdin.write(data)
   assert h.hexdigest()==row['sha256'],str(p)
 except Exception as e:errors.append(repr(e))
 finally:z.stdin.close()
t=threading.Thread(target=feed);t.start();count=0
with tarfile.open(fileobj=z.stdout,mode='r|') as archive:
 for member in archive:
  name=Path(member.name);assert member.isfile() and not name.is_absolute() and '..' not in name.parts
  target=dst/name;target.parent.mkdir(parents=True,exist_ok=True)
  with archive.extractfile(member) as source,target.open('wb') as out:
   while data:=source.read(4*1024*1024):out.write(data)
  os.chmod(target,member.mode & 0o777);count+=1
  archive.members.clear()
t.join();assert z.wait()==0 and not errors,errors
marker.write_text(json.dumps(dict(status='EXTRACTED_VERIFIED_CHUNKS',entries=count,cut_N=m['cut_N'],layer=layer)))
print(marker.read_text())
'''

def run(host,args,**kw):return subprocess.run(host+[shlex.join(args)],check=True,**kw)
def remote_json(host,path):return json.loads(run(host,['cat',path],capture_output=True,text=True).stdout)
def save():
    STATE['heartbeat_unix']=time.time();q=P/'STATUS.json.part';q.write_text(json.dumps(STATE,indent=2)+'\n');q.replace(P/'STATUS.json')
def event(**row):
    with (P/'EVENTS.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),**row))+'\n')
def halted():return STOP or (P/'STOP').exists()
def wait_ready(name,layer):
    while not halted():
        r=subprocess.run(POD+[shlex.join(['test','-f',f'{REMOTE}/{name}/{layer}/READY.json'])])
        if r.returncode==0:return remote_json(POD,f'{REMOTE}/{name}/{layer}/MANIFEST.json')
        STATE.update(stage='WAITING_FOR_ARCHIVE',snapshot=name,layer=layer);save();time.sleep(10)
    raise InterruptedError('OWNER_STOP')
def send_bytes(data,path):
    h=hashlib.sha256(data).hexdigest();run(HELPER,['python3','-c',RECEIVER,path,h,str(len(data))],input=data)
def existing(base,manifest):
    script="from pathlib import Path;import json,sys,hashlib;p=Path(sys.argv[1]);m=json.load(sys.stdin);print(json.dumps([r['file'] for r in m['parts'] if (p/r['file']).is_file() and (p/r['file']).stat().st_size==r['bytes'] and hashlib.file_digest((p/r['file']).open('rb'),'sha256').hexdigest()==r['sha256']]))"
    return set(json.loads(run(HELPER,['python3','-c',script,base],input=json.dumps(manifest),capture_output=True,text=True).stdout))
def stream(source,dest,row,local=False):
    start=time.monotonic()
    for attempt in range(2):
        reader=Path(source).open('rb') if local else subprocess.Popen(POD+[shlex.join(['cat',source])],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        inp=reader if local else reader.stdout
        writer=subprocess.Popen(HELPER+[shlex.join(['python3','-c',RECEIVER,dest,row['sha256'],str(row['bytes'])])],stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        inp.close();out,err=writer.communicate();a=0 if local else reader.wait()
        if writer.returncode==0 and a==0:
            return dict(file=dest,bytes=row['bytes'],seconds=time.monotonic()-start,sha256=row['sha256'])
        event(event='TRANSFER_RETRY',file=dest,attempt=attempt,error=err.decode()[-1000:])
    raise RuntimeError('Transfer failed: '+dest)
def runtime():
    row=dict(file='runtime.public.tar.gz',bytes=Path(RUNTIME).stat().st_size,sha256=RUNTIME_SHA)
    assert hashlib.file_digest(Path(RUNTIME).open('rb'),'sha256').hexdigest()==RUNTIME_SHA
    base=DEST+'/environment';known=existing(base,dict(parts=[row]))
    if row['file'] not in known:stream(RUNTIME,base+'/'+row['file'],row,local=True)
    send_bytes(json.dumps(row,indent=2).encode(),base+'/RUNTIME.json');event(event='RUNTIME_VERIFIED',**row)
def layer(name,kind):
    manifest=wait_ready(name,kind);base=f'{DEST}/{name}/{kind}';STATE.update(stage='TRANSFERRING',snapshot=name,layer=kind,cut_N=manifest['cut_N'],layer_bytes=manifest['compressed_bytes']);save()
    send_bytes(json.dumps(manifest,indent=2).encode(),base+'/MANIFEST.json')
    known=existing(base,manifest);todo=[r for r in manifest['parts'] if r['file'] not in known]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pending={}
        def admit():
            while todo and len(pending)<4 and not halted():
                r=todo.pop(0);future=pool.submit(stream,f'{REMOTE}/{name}/{kind}/'+r['file'],base+'/'+r['file'],r);pending[future]=r
        admit()
        while pending:
            finished,_=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
            for f in finished:
                r=f.result();pending.pop(f);STATE['verified_bytes']=STATE.get('verified_bytes',0)+r['bytes'];event(event='CHUNK_VERIFIED',**r)
            save();admit()
    if halted():raise InterruptedError('OWNER_STOP')
    STATE['stage']='VERIFYING_AND_EXTRACTING';save()
    result=run(HELPER,['python3','-c',EXTRACT,base,kind,DEST+'/restored'],capture_output=True,text=True)
    event(event='LAYER_EXTRACTED',snapshot=name,layer=kind,result=json.loads(result.stdout))
    return manifest

def main():
    global STATE
    lock=(P/'transfer.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    STATE=dict(status='RUNNING',pid=os.getpid(),start_unix=time.time(),destination=DEST,host='lilhelper@10.77.0.2',streams=4,verified_bytes=0,safe_stop=f'touch {P}/STOP')
    save();os.nice(10)
    try:
        runtime()
        first=layer('initial','restart');layer('initial','history')
        while not halted():
            ps=remote_json(POD,'/opt/gen4-spin-continuation1/project/STATUS.json');fs=remote_json(POD,'/opt/gen4-spin-dense-follower1/project/STATUS.json')
            if ps['status'] not in ['RUNNING','QUALIFYING'] and fs['last_contiguous_N']>=ps['last_completed_N']:break
            STATE.update(stage='WAITING_FOR_FINAL_POD_CHECKPOINT',pod_N=ps['last_completed_N'],follower_N=fs['last_contiguous_N']);save();time.sleep(15)
        if halted():raise InterruptedError('OWNER_STOP')
        launch="from pathlib import Path;import subprocess;p=Path('/opt/gen4-spin-transfer1');f=(p/'BUILD_FINAL.log').open('a');c=subprocess.Popen(['python3','/opt/gen4-spin-transfer-build.py','final','--after',%r],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);print(c.pid)" % str(first['cut_N'])
        exists=subprocess.run(POD+[shlex.join(['test','-f',REMOTE+'/final/DONE.json'])]).returncode==0
        if not exists:event(event='FINAL_BUILDER',pid=run(POD,['python3','-c',launch],capture_output=True,text=True).stdout.strip())
        final=layer('final','restart');layer('final','history')
        completion=dict(status='TRANSFER_VERIFIED',final_N=final['cut_N'],runtime_sha256=RUNTIME_SHA,
            scope='Restart, full mathematical results, dense graphs, completed dense pilot and metadata; duplicate native packet output blobs remain on pod',
            no_pod_shutdown=True,time=time.time())
        send_bytes(json.dumps(completion,indent=2).encode(),DEST+'/COMPLETE.json')
        STATE.update(status='COMPLETE',stage='READY_FOR_WORKSTATION',final_N=final['cut_N'])
    except InterruptedError:STATE.update(status='STOPPED',stage='RESUMABLE_CHUNKS_RETAINED')
    except Exception:STATE.update(status='FAILED',error=traceback.format_exc());event(event='FAILED',error=STATE['error'])
    finally:save()
if __name__=='__main__':
    def stop(*_):
        global STOP
        STOP=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);main()
