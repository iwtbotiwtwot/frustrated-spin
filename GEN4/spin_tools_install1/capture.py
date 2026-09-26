"""Retain installed shared-tool calls and their following checkpoints."""
import hashlib,json,shutil,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from loop import Web,save
from SAM_PROJECT.receipt_storage import read_record
w=Web(ROOT);calls=[]
turns=[json.loads(f.read_text()) for f in P.glob('SPIN_TOOLS_ADOPT_*_TURN.json')]
expected={(t['proposals'][0]['operation'],json.dumps(t['proposals'][0]['payload'],sort_keys=True)) for t in turns}
cutoff=(P/'WEB_BEFORE.json').stat().st_mtime
from datetime import datetime
for domain,path in w.db.execute('SELECT domain,path FROM unified_sessions'):
 s=Path(path);storage=json.loads((s/'SESSION.json').read_text()).get('receipt_storage','plain');ordered=[]
 for d in (s/'calls').iterdir():
  f=d/'RECEIPT.json'
  if not f.exists():f=d/'FAILED.json'
  if f.exists():ordered.append((d,json.loads(f.read_text()),f.name))
 selected=[];previous=False
 for d,r,name in sorted(ordered,key=lambda x:x[1]['time']):
  inp=json.loads(read_record(d/'INPUT.json',r.get('receipt_storage',storage)))
  op=inp['operation'];ours=(op,json.dumps(inp.get('payload',{}),sort_keys=True)) in expected and datetime.fromisoformat(r['time']).timestamp()>=cutoff
  if ours or (previous and op=='GEN3_CHECKPOINT'):selected.append((d,r,name,op))
  previous=ours and r['status']=='RETURNED'
 if not selected:continue
 for d,r,name,op in selected:
  dst=P/'custody/native'/s.name/'calls'/d.name;shutil.copytree(d,dst,dirs_exist_ok=True)
  calls.append(dict(domain=domain,operation=op,status=r['status'],time=r['time'],receipt=str((dst/name).relative_to(P))))
 dst=P/'custody/native'/s.name/'SESSION.json';shutil.copy2(s/'SESSION.json',dst)
files=[dict(path=str(f.relative_to(P)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted((P/'custody/native').rglob('*')) if f.is_file()]
save(P/'custody/MANIFEST.json',dict(calls=calls,files=files))
rows=[]
for row in w.db.execute('SELECT payload FROM native_results'):
 v=json.loads(row[0])
 if v['proposal'].startswith('SPIN_TOOLS_ADOPT_'):rows.append(v)
save(P/'custody/FULL_RESULTS.json',rows)
summary=dict(native_returned=len(rows),checkpoints=sum(x['operation']=='GEN3_CHECKPOINT' for x in calls),native_files=len(files),charged_seconds=sum(x['elapsed_seconds'] for x in rows),web_native_results=w.status()['native_results'])
save(P/'EXECUTION_SUMMARY.json',summary);print(json.dumps(summary));w.close()
