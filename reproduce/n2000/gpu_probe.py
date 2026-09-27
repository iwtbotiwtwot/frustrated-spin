"""Run with exactly one CUDA-visible GPU; retain CPU-checked local tables."""
import json,os,time
from pathlib import Path
from engine import ROOT,C,source,atomic,sha
from math_core import b
from CURRENT_REVISION.engines.SLC.gen3.spin_joint_core.cuda_tables import CUDA
index=int(os.environ['N2000_GPU_INDEX']);pieces={}
for family in C['families']:
 for fill in (1,-1):
  c,_=source(family,2000,fill)
  for piece in b.plan(c,fill)['pieces']:pieces[piece['table_key']]=piece
cuda=CUDA();rows=[]
try:
 for ordinal,(key,piece) in enumerate(sorted(pieces.items())):
  if ordinal%2!=index:continue
  start=time.perf_counter();gpu,timing=cuda.enumerate(piece['n'],piece['edges'],piece['fields'],piece['ports']);gpu_total=time.perf_counter()-start
  start=time.perf_counter();cpu=b.cpu_local(piece);cpu_seconds=time.perf_counter()-start
  if gpu!=cpu:raise ArithmeticError('GPU/independent CPU local table mismatch')
  path=ROOT/'local_tables'/f'{key}.json'
  atomic(path,dict(table_key=key,rows=[[state,[[k,t,v] for (k,t),v in sorted(row.items())]] for state,row in sorted(gpu.items())]))
  rows.append(dict(table_key=key,file=str(path.relative_to(ROOT)),sha256=sha(path),gpu_total_seconds=gpu_total,cpu_seconds=cpu_seconds,timing=timing))
 result=dict(status='PASS',gpu=index,identity=cuda.identity,initialization_seconds=cuda.initialization_seconds,tables=rows)
 atomic(ROOT/f'GPU_{index}.json',result)
 print(json.dumps(dict(status='PASS',gpu=index,tables=len(rows),gpu_seconds=sum(r['gpu_total_seconds'] for r in rows),cpu_seconds=sum(r['cpu_seconds'] for r in rows))),flush=True)
finally:cuda.close()
