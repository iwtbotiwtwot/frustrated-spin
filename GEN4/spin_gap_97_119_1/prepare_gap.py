import json,hashlib,math
from pathlib import Path
ROOT=Path('/opt/gen4/spin-gap-97-119-1');OLD=Path('/opt/gen4/spin-n120-frontier1')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
parent=json.loads((OLD/'SOURCE.json').read_text());oldplan=json.loads((OLD/'PLAN.json').read_text())
for n in range(97,120):
 out=ROOT/f'N{n}';out.mkdir(parents=True,exist_ok=True)
 s=dict(N=n,fields=parent['fields'][:n],edges=[e for e in parent['edges'] if max(e[:2])<n],parent_vertices=parent['parent_vertices'][:n],parent_source_sha256=parent['source_sha256'],family='N120_INDUCED_PREFIX_GAP1',construction=dict(operation='induced vertex prefix',parent_N=120,vertices=list(range(n))))
 adj=[set() for _ in range(n)]
 for u,v,j in s['edges']:adj[u].add(v);adj[v].add(u)
 seen={0};todo=[0]
 while todo:
  for v in adj[todo.pop()]-seen:seen.add(v);todo.append(v)
 assert len(seen)==n
 s['energy_bound_B']=sum(map(abs,s['fields']))+sum(abs(e[2]) for e in s['edges']);s['source_sha256']=digest(s)
 fixed=[v for v in oldplan['selected']['cutset'] if v<n];ports=oldplan['ports'];order=[v for v in oldplan['selected']['order'] if v<n]
 assert set(order)==set(range(n))-set(fixed)-set(ports)
 glue=[e for e in oldplan['glue'] if e in s['edges']]
 adj=[set() for _ in range(n)]
 for u,v,j in s['edges']:
  if u not in fixed and v not in fixed and [u,v,j] not in glue:adj[u].add(v);adj[v].add(u)
 width=work=0
 for v in order:
  ns=adj[v];width=max(width,len(ns));work+=1<<len(ns)
  for u in ns:adj[u]=(adj[u]|ns)-{u,v}
  adj[v]=set()
 assert width<=oldplan['selected']['width']
 bound=s['energy_bound_B']-sum(abs(e[2]) for e in glue)
 p=dict(N=n,source_sha256=s['source_sha256'],ports=ports,glue=glue,local_bound=bound,root_count=1<<bound.bit_length(),primes=oldplan['primes'],selected=dict(order=order,width=width,output_entries=work,cutset=fixed,branches=1<<len(fixed),weighted_entries=work*(1<<len(fixed))),execution_admitted=True,prime_product_sufficient=math.prod(oldplan['primes'])>1<<n)
 p['mathematical_plan_sha256']=digest(p)
 save(out/'SOURCE.json',s);save(out/'PLAN.json',p)
 for name in ['PRIMES.json','QUALIFICATION_N30.json']:(out/name).write_bytes((OLD/name).read_bytes())
 code=(OLD/'run.py').read_text().replace("Path('/dev/shm/gen4-spin-n120-frontier1')",f"Path('/opt/gen4/spin-gap-scratch/N{n}')").replace("Path('/workspace/gen4/runs/spin-n120-frontier1')",f"Path('/workspace/gen4/runs/spin-gap-97-119-1/N{n}')").replace("ram.mkdir(exist_ok=True)","ram.mkdir(parents=True,exist_ok=True)").replace("campaign='GEN4_N120_FRONTIER1'","campaign='GEN4_SPIN_GAP_97_119_1'")
 code=code.replace("trace=ctypes.CDLL('/opt/gen4/n72-benchmark1/activity.so');trace.trace_end.argtypes=[ctypes.c_char_p]","trace=None # Exact solver unchanged; omit bulk CUPTI tracing").replace("assert trace.trace_begin()==0","pass")
 (out/'run.py').write_text(code)
 print(n,len(s['edges']),width,len(fixed),p['root_count'],flush=True)
