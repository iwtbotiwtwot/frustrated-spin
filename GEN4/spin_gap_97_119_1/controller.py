import os,json,subprocess,time,hashlib,shutil,traceback,gzip
from pathlib import Path
ROOT=Path('/opt/gen4/spin-gap-97-119-1');D=Path('/workspace/gen4/runs/spin-gap-97-119-1');D.mkdir(parents=True,exist_ok=True)
os.environ.update(PYTHONPATH='/opt/gen4/current',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',GEN4_SPIN_SOURCE='/opt/gen4/n96-benchmark1/source',GEN4_SPIN_CATALOG_CODE='/opt/gen4/spin-catalog1',GEN4_SPIN_TRAINING_CODE='/opt/gen4/spin-training1')
completed=[];failed=[];previous='0'*64
start=time.time()
def event(kind,**v):
 global previous
 row=dict(time=time.time(),kind=kind,previous_sha256=previous,**v);previous=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest();row['sha256']=previous
 with (D/'EVENTS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
def status(state,n=None):
 p=D/'STATUS.tmp';p.write_text(json.dumps(dict(state=state,current_N=n,completed=completed,failed=failed,started=start,updated=time.time()),indent=2));p.replace(D/'STATUS.json')
try:
 for n in range(97,120):
  status('RUNNING',n);event('START_SIZE',N=n)
  out=D/f'N{n}';out.mkdir(exist_ok=True)
  for name in ['SOURCE.json','PLAN.json','PRIMES.json','QUALIFICATION_N30.json','run.py']:shutil.copyfile(ROOT/f'N{n}'/name,out/name)
  # A twelve-hour per-source ceiling retains exact partial work if an outlier occurs.
  with (out/'RUN.log').open('a') as log:
   rc=subprocess.call(['/opt/gen4/venv/bin/python','-u',str(ROOT/f'N{n}'/'run.py'),'--skip-training-wait','--deadline',str(time.time()+12*3600)],stdout=log,stderr=subprocess.STDOUT)
  scratch=Path(f'/opt/gen4/spin-gap-scratch/N{n}')
  done=scratch/'COMPLETE.json'
  if rc or not done.exists():
   failed.append(n);event('INCOMPLETE',N=n,returncode=rc);status('STOPPED_REVIEW',n);break
  result=json.loads(gzip.decompress((scratch/'RESULT1.json.gz').read_bytes()));assert result['status']=='EXACT';assert int(result['answer']['configuration_count'])==1<<n
  for name in ['COMPLETE.json','RESULT1.json.gz','RESULT_BUNDLE.json.gz','CHECKPOINT.json']:
   shutil.copyfile(scratch/name,out/name)
  # Native engine already flushes complete sessions in checkpoint.tar.gz.
  hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file() and not f.name.endswith('.part')}
  (out/'MANIFEST.json').write_text(json.dumps(hashes,indent=2));completed.append(n)
  catalog=dict(completed_new_sizes=completed,preexisting_sizes=list(range(1,97))+[100,105,120],full_size_coverage=sorted(set(range(1,97))|{100,105,120}|set(completed)),family='N120_INDUCED_PREFIX_GAP1',legacy_families_preserved=True)
  (D/'CATALOG.json').write_text(json.dumps(catalog,indent=2));event('EXACT_SIZE',N=n,ground=result['answer']['ground_energy'],result_sha256=hashes['RESULT1.json.gz']);status('RUNNING',n)
 else:status('COMPLETE');event('COMPLETE',sizes=completed)
except BaseException:
 event('FAILURE',traceback=traceback.format_exc());status('FAILED');raise
finally:
 (D/'REPORT.md').write_text('# N97–119 exact catalogue completion\n\n'+(D/'STATUS.json').read_text()+'\n\nNew family: induced prefixes of frozen N120 graph; older N100/N105 families retained. Each completed size has exact DOS, 16 port spectra, a native result bundle, checkpoint archive and SHA256 manifest. No Codex calls needed. Pod shutdown is manual.\n')
