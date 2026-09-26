"""Exact follow-up methods. Prototype optimizations stay in this campaign."""
import sys,time,json,copy,math,itertools,statistics
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from research import Research,canonical,load,save,digest,sha,features,compare_answer,independent,exact
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

class Followup(Research):
 def execute(self,op,payload):
  if op!='GEN4_SPIN_FOLLOWUP1':return super().execute(op,payload)
  assert payload['code_sha256']==sha(__file__);q=payload['question'];s=source(q);ps=ports(q);assert 1<=s['N']<=120
  if q['kind']=='planning':
   original=dict(q,kind='plans',variant=q.get('variant'))
   return super().execute('GEN4_FRUSTRATED_LEARN1',dict(code_sha256=sha(ROOT/'research.py'),question=original))
  if q['kind']=='gauge_certificate':
   original=canonical(q['N'])['source'];g=q['gauge'];emap={(u,v):j for u,v,j in s['edges']};assert s['fields']==[h*z for h,z in zip(original['fields'],g)];assert emap=={(u,v):j*g[u]*g[v] for u,v,j in original['edges']}
   return dict(status='CERTIFIED_EXACT_RULE',rule='EXPLICIT_SPIN_SIGN_BIJECTION',gauge=g,source=s['source_sha256'],parent=original['source_sha256'],derivation='t_i=g_i*s_i is a bijection; transformed fields h_i*g_i and couplings J_ij*g_i*g_j preserve each energy. Scalar DOS identical; ordered port states multiply by g on ports.',new_theorem=False)
  timings=[];expected=canonical(q['N'])['spectrum'] if not q.get('variant') else None;all_answers=[]
  if expected is not None and 'requested_ports' in q:
   old=exact.canonical_retained(canonical(q['N']));hist={i:Counter() for i in range(1<<len(ps))}
   for row in old['port_rows']:
    mask=sum(1<<i for i,v in enumerate(ps) if row['state'][old['ports'].index(v)]==1)
    for e,c in row['dos']:hist[mask][int(e)]+=int(c)
   expected=exact.finalize_answer(s,ps,hist)
  methods=q['methods'];cache={}
  # Balanced alternating method order; verifier time excluded from arithmetic timings.
  for rep in range(q.get('repeats',3)):
   for m in (methods if rep%2==0 else list(reversed(methods))):
    start=time.perf_counter_ns();cpu=time.process_time_ns()
    if m in ['components','variable_elimination']:
     r=exact.solve_cpu(s,ps,dict(method=m,max_seconds=55,max_component_size=18,max_assignments=400000,max_factor_work=3000000,max_intermediate_entries=65536));a=r['answer'];meta=r['execution']
    elif m=='memo_components':a,meta=component_reuse(s,ps,{})
    elif m=='warm_components':a,meta=component_reuse(s,ps,cache)
    elif m=='conditional_components':a,meta=conditioned(s,ps)
    else:raise ValueError(m)
    secs=(time.perf_counter_ns()-start)/1e9;cpu=(time.process_time_ns()-cpu)/1e9
    if expected is None:expected=a
    equality=compare_answer(a,expected)
    timings.append(dict(method=m,rep=rep,seconds=secs,cpu_seconds=cpu,metadata=meta,verified=equality));all_answers.append(a)
  if s['N']<=16:ind=independent(s,ps);compare_answer(all_answers[0],ind)
  elif q.get('variant') and len(set(methods))<2:raise ValueError('New variants need two independent exact routes')
  medians={m:statistics.median(r['seconds'] for r in timings if r['method']==m) for m in methods};means={m:statistics.mean(r['seconds'] for r in timings if r['method']==m) for m in methods};cv={m:statistics.pstdev(r['seconds'] for r in timings if r['method']==m)/max(means[m],1e-9) for m in methods}
  fastest=min(medians,key=medians.get);return dict(status='REPEATED_EMPIRICAL_RULE' if q.get('repeats',3)>=3 else 'OBSERVED_PATTERN',N=s['N'],source_hash=s['source_sha256'],features=features(s),timings=timings,median_seconds=medians,coefficient_of_variation=cv,fastest=fastest,speedup=max(medians.values())/min(medians.values()),answer=all_answers[0],all_full_density_equal=True,variant_reference='second independent exact route' if q.get('variant') else 'canonical retained full density',candidate_optimization='project-local exact repeated-component or conditional-separator compiler route' if any('components' in m for m in methods) else None)
