"""Continue authorized training after GPU owners stop; preserve both campaigns."""
import os,time,subprocess,json
from pathlib import Path
P=Path('/opt/gen4/spin-focused1');deadline=1790308980

def alive(pid):
    p=Path(f'/proc/{pid}/stat')
    return p.exists() and p.read_text().split(') ')[1].split()[0]!='Z'
while alive(75686):time.sleep(5)
first=Path('/dev/shm/gen4-spin-focused1')
if not (first/'COMPLETE.json').exists():
    subprocess.run(['/opt/gen4/venv/bin/python',str(P/'recover_publication.py'),'--ram',str(first),'--durable','/workspace/gen4/runs/spin-focused1','--kind','gpu'],check=True)
qualified=Path('/dev/shm/gen4-spin-readout-check1/RESULT.json')
assert qualified.exists() and all(r['exact_match'] for r in json.loads(qualified.read_text()))
if time.time()>deadline-1200:raise RuntimeError('Reserve too short for full faster-backend training; retained qualification and original results remain')
print('START_FAST_SUCCESSOR',time.time(),flush=True)
with (P/'fast.log').open('w') as log:
    r=subprocess.run(['/opt/gen4/venv/bin/python','-u',str(P/'run_fast.py'),'--ram','/dev/shm/gen4-spin-focused-fast1','--durable','/workspace/gen4/runs/spin-focused-fast1','--deadline',str(deadline)],stdout=log,stderr=subprocess.STDOUT)
print('FAST_RETURN_CODE',r.returncode,flush=True)
