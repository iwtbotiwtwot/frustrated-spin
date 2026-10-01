"""Match CPU and GPU exact polynomial products at the pilot upper endpoint."""
import time,json,gzip,collections
from pathlib import Path
from flint import fmpz_poly,ctx
import baseline as b
import optimized as opt
from gpu import Backend
HERE=Path(__file__).resolve().parent
sources=json.loads(gzip.decompress((HERE/'SOURCES.json.gz').read_bytes()));backend=Backend();ctx.threads=1;rows=[]
for family in ['packet','signed_packet_chain']:
 c=sources[f'{family}_N100'];plan=b.plan(c,-1);tables={p['table_key']:b.cpu_local(p) for p in plan['pieces']}
 for orientation in ['K_MAJOR','T_MAJOR']:
  parts=opt.components(plan,tables,orientation=='K_MAJOR');counts=collections.Counter(k for k,p in parts[1:]);by=dict(parts)
  def encode(row):return {(k*(plan['correction_bound']+1)+t if orientation=='K_MAJOR' else t*101+k):v for (k,t),v in row.items()}
  fs=[(encode(by[k]['rows'][0]),count) for k,count in counts.items()]+[(encode(parts[0][1]['rows'][0]),1)]
  for repeat in range(2):
   t=time.perf_counter();cpu=fmpz_poly([1])
   for sparse,e in fs:
    values=[0]*(max(sparse)+1)
    for i,v in sparse.items():values[i]=v
    cpu*=fmpz_poly(values)**e
   cpu_seconds=time.perf_counter()-t;t=time.perf_counter();data,stats=backend.solve(fs,100);gpu_seconds=time.perf_counter()-t
   actual=[int.from_bytes(row.tobytes(),'little') for row in data];expected=list(map(int,cpu));assert actual==expected
   rows.append(dict(family=family,orientation=orientation,repeat=repeat,cpu_seconds=cpu_seconds,gpu_seconds_including_setup=gpu_seconds,gpu_internal_seconds=stats['total_seconds'],exact_coefficients=len(expected),agreement=True))
  backend.clear()
result=dict(status='PASS',N=100,rows=rows,scope='Matched exact global polynomial composition; source compilation/verification/readout excluded. CPU production also reuses the common scalar across boundaries. First GPU call includes JIT/setup; repeat1 is warm.')
(HERE.parent/'BENCHMARK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
