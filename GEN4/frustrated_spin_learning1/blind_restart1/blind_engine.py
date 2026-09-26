"""Fresh research operations; no prior campaign result or model inputs."""
import os,sys,time,json,copy,math,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent
from research import Research,canonical,load,save,digest,features,compare_answer,exact,sha,independent

def source(q):return load(P/q['variant'])['source'] if q.get('variant') else canonical(q['N'])['source']
def row_features(q):return features(source(q))
def descriptor(s):
 f=features(s);f['structural_signature']=digest({k:f[k] for k in ['degree_signature','component_sizes','minfill_width','minfill_work','root_bound','crt_primes','coupling_multiplicities']});return f

def make_variant(q):
 s=copy.deepcopy(source(q));parent=s['source_sha256'];n=s['N'];ports=canonical(n)['spectrum'].get('retained_ports',list(range(min(n,4))));free=[v for v in range(n) if v not in ports];mode=q['mode'];level=q.get('level',1);proof=None
 if mode=='gauge':
  signs=[1 if i in ports else (-1 if int(digest([level,i])[:4],16)%2 else 1) for i in range(n)];s['fields']=[h*signs[i] for i,h in enumerate(s['fields'])];s['edges']=[[u,v,j*signs[u]*signs[v]] for u,v,j in s['edges']];proof=dict(kind='EXPLICIT_GAUGE_BIJECTION',signs=signs,ports_fixed=True)
 elif mode=='permutation':
  order=sorted(free,key=lambda v:digest([level,v]));mp=dict(zip(free,order));mp.update({v:v for v in ports});old=copy.deepcopy(s);s['fields']=[0]*n
  for i,h in enumerate(old['fields']):s['fields'][mp[i]]=h
  s['parent_vertices']=[0]*n
  for i,v in enumerate(old['parent_vertices']):s['parent_vertices'][mp[i]]=v
  s['edges']=[[*sorted([mp[u],mp[v]]),j] for u,v,j in old['edges']];proof=dict(kind='EXPLICIT_VERTEX_BIJECTION',mapping=mp,ports_fixed=True)
 elif mode=='rewire':
  import itertools
  pairs={tuple(e[:2]) for e in s['edges']};glue={(0,1),(2,3)}
  legal=any(len({a,b,c,d})==4 and tuple(sorted((a,d))) not in pairs|glue and tuple(sorted((c,b))) not in pairs|glue for (a,b),(c,d) in itertools.combinations(sorted(pairs-glue),2))
  if not legal:return dict(status='NOT_APPLICABLE',N=n,mode=mode,reason='No legal degree-preserving switch for this source grammar')
  from variant_generator import graph_family
  s=graph_family(s,level)
 elif mode=='bridge':
  groups=exact.components(s)
  if len(groups)<2:return dict(status='NOT_APPLICABLE',reason='Source already connected',mode=mode,N=n)
  for i in range(min(level,len(groups)-1)):
   u,v=sorted([groups[i][0],groups[i+1][0]]);s['edges'].append([u,v,1 if i%2==0 else -1])
 elif mode=='coupling':
  ids=sorted(range(len(s['edges'])),key=lambda i:digest([level,i]))[:min(level,len(s['edges']))]
  for i in ids:s['edges'][i][2]*=-1
 elif mode=='fieldzero':s['fields']=[0]*n
 else:raise ValueError(mode)
 s['edges'].sort()
 if s['edges']==sorted(source(q)['edges']) and s['fields']==source(q)['fields']:return dict(status='NOT_APPLICABLE',N=n,mode=mode,reason='Intervention leaves this source unchanged')
 s['family']='BLIND_RESTART_VARIANT_'+mode;s['energy_bound_B']=sum(map(abs,s['fields']))+sum(abs(j) for u,v,j in s['edges']);s.pop('source_sha256',None);s['source_sha256']=digest(s)
 path='variants/'+q['question_id']+'.json';save(P/path,dict(source=s,parent_source=parent,mode=mode,level=level,proof=proof,claim_type='NEWLY_EXECUTED_SOURCE_TRANSFORMATION'))
 return dict(status='OBSERVED_PATTERN',N=n,variant=path,parent_source=parent,features=descriptor(s),parent_features=descriptor(source(q)),mode=mode,level=level,proof=proof)

def plans(q):
 s=source(q);frozen=load(P/'runtime/CURRENT_REVISION/engines/SLC/gen3/spin_data/PARENT_PLAN.json');previous=canonical(max(1,min(s['N']-1,96)))['plan'];result=[];failures=[]
 from vendor import spin_methods,spin_expanded
 try:result=spin_expanded.expanded(s,frozen,previous)
 except (AssertionError,ValueError,KeyError) as e:failures.append(repr(e))
 if not q.get('variant'):
  inherited=canonical(s['N'])['plan']
  if all(k in inherited for k in ['selected','ports','glue','root_count','primes']):result.append(dict(inherited,training_method='inherited_exact_plan'))
 unique={}
 for p in result:
  p=copy.deepcopy(p);p['source_sha256']=s['source_sha256'];p.setdefault('mathematical_plan_sha256',digest(p));signature=digest({k:p[k] for k in ['selected','ports','glue','root_count','primes']});unique.setdefault(signature,p)
 return dict(status='LEARNED_HEURISTIC',N=s['N'],variant=q.get('variant'),source_hash=s['source_sha256'],features=descriptor(s),plans=list(unique.values()),planning_failures=failures,scope='PRE-execution structural choices; no spectrum computed')

class Borrowed:
 def __init__(self,base):self.base=base
 def execute(self,*a,**kw):return self.base.execute(*a,**kw)
 def close(self):pass

def gpu_compare(base,q,out):
 # Import the historical qualified engines directly, keeping their process topology.
 sys.path[:0]=['/opt/gen4/spin-focused1','/opt/gen4/spin-training1','/opt/gen4/spin-catalog1']
 # This module is deliberately named blind_engine on import to leave historical `engine` available.
 from run_fast import Focus
 from arithmetic import templates,IndexCache
 s=source(q);selected=q['plans'];cache=IndexCache();cases=[];prep=time.monotonic()
 for p in selected:
  assert p['source_sha256']==s['source_sha256'] and p['selected']['width']<=22
  ts=templates(s,p);desc,maps,stats=cache.compile(ts[0]);cases.append((s,p,ts,desc,maps,stats))
 source_prepare=time.monotonic()-prep;ram=out/'gpu_work';ram.mkdir(exist_ok=True);os.environ['CUPY_CACHE_DIR']='/opt/gen4/restore14/blind-cuda-cache';results=[];reference=None
 if not q.get('variant'):reference=canonical(s['N'])['spectrum']
 else:
  v=load(P/q['variant'])
  if v.get('proof'):reference=canonical(s['N'])['spectrum']
 if reference is None and len(cases)<2:raise ValueError('Uncertified changed source requires two distinct exact elimination plans')
 for p in selected:assert math.prod(p['primes'])>1<<s['N']
 adapter=None;t=time.monotonic()
 try:
  # All plans in one comparison use the same backend class, preserving timing comparability.
  branch=max(len(c[2]) for c in cases)>32
  if branch:
   spec=importlib.util.spec_from_file_location('blind_original_frontier','/opt/gen4/spin-n120-frontier1/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
   adapter=m.Frontier(Borrowed(base),ram,[cases[0]]+cases,cache,deadline=time.time()+q['maximum_admitted_seconds']-30);adapter.durable=ram/'checkpoints';adapter.durable.mkdir(exist_ok=True)
  else:adapter=Focus(Borrowed(base),ram,cases,cache)
  for rep in range(q.get('repeats',2)):
   for ci in (range(len(cases)) if rep%2==0 else reversed(range(len(cases)))):
    p=selected[ci]
    if branch:
     # Distinct repeats must compute fresh residues, never time a completed checkpoint replay.
     for name in [f'RESIDUES{ci+1}.npz',f'PROFILES{ci+1}.json']:
      f=ram/name
      if f.exists():f.rename(ram/(f'repeat{rep-1}_'+name))
     r=adapter.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=ci+1,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256']));assert r['status']=='EXACT'
    else:r=adapter.execute('GEN4_SPIN_FOCUSED_SOLVE',dict(case=ci,source_sha256=s['source_sha256'],plan_sha256=p['mathematical_plan_sha256'],repeat=rep))
    if reference is None:reference=r['answer']
    compare_answer(r['answer'],reference);assert all(r['answer']['checks'].values())
    results.append(dict(plan=ci,method=p.get('training_method',p['selected'].get('method','retained')),repeat=rep,seconds=r['execution']['total_ns']/1e9,execution=r['execution'],verified=True,cold_workers=rep==0 and ci==0))
    save(out/'PARTIAL_MEASUREMENTS.json',results)
 finally:
  if adapter:adapter.close()
 return dict(status='OBSERVED_PATTERN',N=s['N'],variant=q.get('variant'),source_hash=s['source_sha256'],features=descriptor(s),measurements=results,answer=reference,full_density_verified=True,source_preparation_seconds=source_prepare,total_seconds=time.monotonic()-t,backend=r['execution']['backend']+'_BATCHED_READOUT',plans=selected)

class Campaign(Research):
 def __init__(self,base,out):super().__init__(base);self.out=out
 def execute(self,op,payload):
  if op!='GEN4_BLIND_RESEARCH':return super().execute(op,payload)
  q=payload['question'];kind=q['kind']
  if kind in ['atlas','analysis','solve','component_rule']:
   return super().execute('GEN4_FRUSTRATED_LEARN1',dict(question=q,code_sha256=sha(P/'research.py')))
  if kind=='plans':return plans(q)
  if kind=='variant':return make_variant(q)
  if kind=='compare':
   a=source(q);b=canonical(q['other_N'])['source'];fa=descriptor(a);fb=descriptor(b);changed={k:[fa[k],fb[k]] for k in fa if fa[k]!=fb.get(k)}
   return dict(status='OBSERVED_PATTERN',N=q['N'],other_N=q['other_N'],a=fa,b=fb,changes=changed,question=q['question'],cause_established=False)
  if kind=='gpu_compare':return gpu_compare(self.base,q,self.out)
  if kind=='ports':
   c=canonical(q['N']);s=c['source'];from collections import Counter
   old=exact.canonical_retained(c);retained=old['ports'];chosen=q['ports'];assert set(chosen)<=set(retained);hist={i:Counter() for i in range(1<<len(chosen))}
   for row in old['port_rows']:
    mask=sum(1<<i for i,v in enumerate(chosen) if row['state'][retained.index(v)]==1)
    for e,count in row['dos']:hist[mask][int(e)]+=int(count)
   a=exact.finalize_answer(s,chosen,hist);assert a['scalar_dos']==old['scalar_dos']
   return dict(status='CERTIFIED_EXACT_RULE',N=q['N'],rule='EXACT_PORT_MARGINALIZATION',ports=chosen,original_ports=retained,answer=a,proof='Explicit summation partitions the complete retained-state table; every coefficient included exactly once.',scope='This explicit source and retained-state table',independent_verifier_required=True)
  if kind=='symmetry':
   v=load(P/q['variant']);s=v['source'];original=canonical(q['N'])['source'];proof=v['proof'];assert proof
   if proof['kind']=='EXPLICIT_GAUGE_BIJECTION':
    g=proof['signs'];assert s['fields']==[h*g[i] for i,h in enumerate(original['fields'])];assert s['edges']==sorted([[u,w,j*g[u]*g[w]] for u,w,j in original['edges']])
   else:
    mp={int(k):v for k,v in proof['mapping'].items()};assert sorted(mp.values())==list(range(s['N']));assert s['edges']==sorted([[*sorted([mp[u],mp[v]]),j] for u,v,j in original['edges']]);assert all(s['fields'][mp[i]]==h for i,h in enumerate(original['fields']))
   return dict(status='EXACT_RULE_CANDIDATE',N=q['N'],variant=q['variant'],proof=proof,source_hash=s['source_sha256'],parent_hash=original['source_sha256'],claim='Explicit configuration bijection preserving every energy and the fixed port labels',requires_independent_inverse_check=True)
  raise ValueError(kind)
