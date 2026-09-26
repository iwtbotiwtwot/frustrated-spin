"""Exact follow-up methods. Prototype optimizations stay in this campaign."""
import sys,time,json,copy,math,itertools,statistics
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;ROOT=P;sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from source_ops import Research,canonical,load,save,digest,sha,features,compare_answer,independent,exact
from flint import fmpz_poly

def normalize(s):return exact.validate_source({k:v for k,v in s.items() if k!='source_sha256'})
def source(q):return normalize(load(ROOT/q['variant'])['source'] if q.get('variant') else canonical(q['N'])['source'])
def ports(q):return q.get('requested_ports',canonical(q['N'])['spectrum'].get('retained_ports',list(range(min(4,q['N'])))))
def convolve(a,b):
 if not a or not b:return {}
 lo=min(a);other=min(b);pa=[0]*(max(a)-lo+1);pb=[0]*(max(b)-other+1)
 for e,c in a.items():pa[e-lo]=int(c)
 for e,c in b.items():pb[e-other]=int(c)
 prod=fmpz_poly(pa)*fmpz_poly(pb)
 return {i+lo+other:int(c) for i,c in enumerate(prod) if c}
def component_reuse(s,ps,cache):
 groups=exact.components(s);rows={0:{0:1}};hits=0;misses=0;keys=[];cost=0
 for group in groups:
  if len(group)>18:raise exact.CapacityError('component >18; requires conditional decomposition or another route')
  mp={v:i for i,v in enumerate(group)};localports=[v for v in ps if v in mp];sub=normalize(dict(N=len(group),edges=[[mp[u],mp[v],j] for u,v,j in s['edges'] if u in mp and v in mp],fields=[s['fields'][v] for v in group],parent_vertices=list(range(len(group))),family='EXACT_LOCAL_COMPONENT'))
  key=digest(dict(edges=sub['edges'],fields=sub['fields'],ports=[mp[v] for v in localports]));keys.append(dict(key=key,vertices=group,ports=localports))
  if key in cache:r=cache[key];hits+=1
  else:
   r=exact.solve_cpu(sub,[mp[v] for v in localports],dict(method='components',max_component_size=18,max_assignments=300000,max_seconds=50));cache[key]=r;misses+=1;cost+=r['execution']['arithmetic_work_units']
  nex={}
  for a,poly in rows.items():
   for row in r['answer']['port_rows']:
    mask=a|sum(1<<ps.index(v) for v,z in zip(localports,row['state']) if z==1)
    nex[mask]=convolve(poly,{int(e):int(c) for e,c in row['dos']})
  rows=nex
 return exact.finalize_answer(s,ps,rows),dict(cache_hits=hits,cache_misses=misses,component_keys=keys,arithmetic_work_units=cost,proof='Identical explicit local fields, couplings and ordered port indices define identical finite energy tables. Disjoint tables combine by exact polynomial convolution.')

def conditioned(s,ps):
 # Choose a separator by exact structural enumeration of one or two non-port vertices.
 options=[];n=s['N'];vertices=[v for v in range(n) if v not in ps]
 for v in vertices:
  groups=remaining_groups(s,{v});options.append((max(map(len,groups),default=0),sum(1<<len(g) for g in groups),[v]))
 options.sort();fixed=options[0][2]
 if options[0][0]>18:
  candidates=options[:12]
  pairs=[]
  for _,_,one in candidates:
   for v in vertices:
    if v in one:continue
    g=remaining_groups(s,set(one+[v]));pairs.append((max(map(len,g),default=0),sum(1<<len(x) for x in g),sorted(one+[v])))
  pairs.sort();fixed=pairs[0][2]
 groups=remaining_groups(s,set(fixed))
 if max(map(len,groups),default=0)>18:raise exact.CapacityError('No admitted one/two-spin decomposition; retain as structural boundary')
 rows={i:Counter() for i in range(1<<len(ps))};cache={};hits=misses=cost=0;certs=[]
 for zs in itertools.product([-1,1],repeat=len(fixed)):
  signed=dict(zip(fixed,zs));sites=[v for v in range(n) if v not in signed];mp={v:i for i,v in enumerate(sites)};fields=[s['fields'][v] for v in sites];edges=[];offset=-sum(s['fields'][v]*z for v,z in signed.items())
  for u,v,j in s['edges']:
   if u in signed and v in signed:offset-=j*signed[u]*signed[v]
   elif u in signed:fields[mp[v]]+=j*signed[u]
   elif v in signed:fields[mp[u]]+=j*signed[v]
   else:edges.append([mp[u],mp[v],j])
  sub=normalize(dict(N=len(sites),fields=fields,edges=edges,parent_vertices=list(range(len(sites))),family='EXACT_CONDITIONAL_COMPONENTS'))
  answer,meta=component_reuse(sub,[mp[v] for v in ps],cache);hits+=meta['cache_hits'];misses+=meta['cache_misses'];cost+=meta['arithmetic_work_units'];certs.append(dict(signs=signed,offset=offset,keys=meta['component_keys']))
  for row in answer['port_rows']:
   mask=sum(1<<i for i,z in enumerate(row['state']) if z==1)
   for e,c in row['dos']:rows[mask][int(e)+offset]+=int(c)
 return exact.finalize_answer(s,ps,rows),dict(cutset=fixed,branches=1<<len(fixed),largest_residual_component=max(map(len,groups)),cache_hits=hits,cache_misses=misses,arithmetic_work_units=cost,branch_certificates=certs,proof='Partition sum over every separator assignment; absorb each incident edge into residual fields and retain the exact fixed-spin energy offset. No assignments omitted.')
def remaining_groups(s,removed):
 adj={v:set() for v in range(s['N']) if v not in removed}
 for u,v,j in s['edges']:
  if u in adj and v in adj:adj[u].add(v);adj[v].add(u)
 seen=set();groups=[]
 for v in adj:
  if v in seen:continue
  group={v};todo=[v];seen.add(v)
  while todo:
   for w in adj[todo.pop()]-seen:seen.add(w);group.add(w);todo.append(w)
  groups.append(sorted(group))
 return groups

