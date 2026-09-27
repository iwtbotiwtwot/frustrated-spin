"""Durable parallel custody transfer; no hosted calls and no hardware lifecycle actions."""
import concurrent.futures,datetime,hashlib,json,os,pathlib,subprocess,time
P=pathlib.Path(__file__).resolve().parent;C=P/'custody';D=C/'pod';D.mkdir(parents=True,exist_ok=True)
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','-p','11136','-i',str(pathlib.Path.home()/'.ssh/id_ed25519'),'root@69.8.146.173']
ROOTS=['/opt/gen4-spin-joint-readout1/project','/opt/gen4-spin-magnetization2/project','/opt/gen4-spin-magnetization3/project','/opt/gen4-spin-dense-solver1/project','/opt/gen4-spin-continuation1/runtime']
T500='lilhelper@10.77.0.2';TARGET='/home/lilhelper/SAM_Research_Project/SAM_POD_BACKUPS/frustrated-spin-20260926/joint-installation-final'
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,value):
 p=C/name;tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)
def state(stage,**kw):save('STATUS.json',dict(stage=stage,pid=os.getpid(),started_utc=started,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),local=str(D),T500=TARGET,**kw))
def remote(code):
 r=subprocess.run(SSH+['python','-'],input=code,text=True,capture_output=True,check=True,timeout=1200);return json.loads(r.stdout)
def inventory(hashes=False):
 return remote('import os,json,pathlib,hashlib\nrows=[]\nfor base in '+repr(ROOTS)+':\n for folder,dirs,files in os.walk(base):\n  dirs[:]=[v for v in dirs if v not in ["__pycache__"]]\n  for name in files:\n   p=pathlib.Path(folder)/name\n   if name.endswith((".part",".tmp",".lock",".pyc")):continue\n   if not p.is_file():continue\n   row=dict(path=str(p).lstrip("/"),bytes=p.stat().st_size)\n   if '+repr(hashes)+':\n    with p.open("rb") as f:row["sha256"]=hashlib.file_digest(f,"sha256").hexdigest()\n   rows.append(row)\nprint(json.dumps(rows))')
def transfer(rows,phase):
 groups=[[] for _ in range(8)];sizes=[0]*8
 for row in sorted(rows,key=lambda v:-v['bytes']):
  i=min(range(8),key=lambda j:sizes[j]);groups[i].append(row);sizes[i]+=row['bytes']
 def lane(i):
  listing=C/f'{phase}_lane{i}.list';listing.write_bytes(b'\0'.join(r['path'].encode() for r in groups[i])+b'\0')
  cmd=['rsync','-rlt','--relative','--partial','--append-verify','--from0','--files-from='+str(listing),'--info=progress2','-e','ssh -o BatchMode=yes -o ConnectTimeout=15 -p 11136 -i '+str(pathlib.Path.home()/'.ssh/id_ed25519'),'root@69.8.146.173:/',str(D)+'/']
  with (C/f'{phase}_lane{i}.log').open('w') as f:
   rc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
  return dict(lane=i,returncode=rc,bytes=sizes[i])
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:result=list(ex.map(lane,range(8)))
 save(phase+'_TRANSFER.json',result)
 if any(v['returncode'] for v in result):raise RuntimeError('Transfer lane failed; resume from retained partials using this script')
try:
 state('INVENTORY')
 rows=inventory();save('INITIAL_INVENTORY.json',rows);state('DOWNLOADING_COMPLETED_DATA',files=len(rows),bytes=sum(v['bytes'] for v in rows));transfer(rows,'initial')
 state('WAITING_FOR_SAFE_CASE_BOUNDARY')
 deadline=time.time()+1200
 while True:
  s=remote("import json,pathlib;print((pathlib.Path('/opt/gen4-spin-joint-readout1/project/STATUS.json')).read_text())")
  if s['status']!='RUNNING':break
  if time.time()>deadline:raise RuntimeError('Case-boundary wait exceeded 20 minutes; completed downloads retained')
  time.sleep(10)
 save('FINAL_POD_STATUS.json',s);state('FINAL_HASHED_INVENTORY')
 rows=inventory(True);save('FINAL_INVENTORY.json',rows);state('DOWNLOADING_FINAL_CASE',files=len(rows),bytes=sum(v['bytes'] for v in rows));transfer(rows,'final')
 state('VERIFYING_LOCAL_SHA256',files=len(rows),bytes=sum(v['bytes'] for v in rows))
 def verify(row):
  p=D/row['path']
  with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  if h!=row['sha256']:raise RuntimeError('Local hash differs: '+row['path'])
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(verify,rows))
 save('LOCAL_VERIFIED.json',dict(status='PASS',files=len(rows),bytes=sum(v['bytes'] for v in rows),verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pod_data_safe_locally=True))
 state('COPYING_TO_T500',local_verified=True)
 subprocess.run(['ssh','-o','BatchMode=yes',T500,'mkdir','-p',TARGET],check=True)
 with (C/'T500_TRANSFER.log').open('w') as f:
  subprocess.run(['rsync','-rlt','--partial','--info=progress2',str(D)+'/',T500+':'+TARGET+'/pod/'],stdout=f,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['scp','-q',str(C/'FINAL_INVENTORY.json'),T500+':'+TARGET+'/FINAL_INVENTORY.json'],check=True)
 code='import pathlib,json,hashlib\np=pathlib.Path('+repr(TARGET)+');rows=json.loads((p/"FINAL_INVENTORY.json").read_text())\nfor r in rows:\n with (p/"pod"/r["path"]).open("rb") as f:assert hashlib.file_digest(f,"sha256").hexdigest()==r["sha256"],r["path"]\nresult=dict(status="PASS",files=len(rows),bytes=sum(r["bytes"] for r in rows))\n(p/"VERIFIED.json").write_text(json.dumps(result,indent=2))\nprint(json.dumps(result))'
 r=subprocess.run(['ssh','-o','BatchMode=yes',T500,'python3','-'],input=code,text=True,capture_output=True,check=True)
 save('T500_VERIFIED.json',json.loads(r.stdout));state('COMPLETE_TWO_VERIFIED_COPIES',files=len(rows),bytes=sum(v['bytes'] for v in rows),pod_data_safe=True)
except BaseException as e:
 state('FAILED_PRESERVING_PARTIALS',error=repr(e));raise
