"""Project-scoped source analysis, interpretable models and exact research adapters."""
import os,sys,json,hashlib,math,time,csv,statistics,itertools,copy
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'runtime'))
from vendor import spin_exact as exact
from vendor import spin_methods,spin_expanded
METHODS=spin_methods.METHODS+['expanded_portfolio','components','variable_elimination','incremental_boundary']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n');t.replace(p)
def append(p,x):
 with Path(p).open('a') as f:f.write(json.dumps(x,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def canonical(n):assert 1<=n<=120;return load(P/f'canonical/N{n:03d}.json')
def minfill(s):
 adj=[set() for _ in range(s['N'])]
 for u,v,j in s['edges']:adj[u].add(v);adj[v].add(u)
 active=set(range(s['N']));width=work=0;order=[]
 while active:
  v=min(active,key=lambda v:(sum(b not in adj[a] for a,b in itertools.combinations(adj[v],2)),len(adj[v]),v));ns=adj[v].copy();width=max(width,len(ns));work+=1<<len(ns)
  for u in ns:adj[u]=(adj[u]|ns)-{u,v}
  active.remove(v);adj[v]=set();order.append(v)
 return width,work,order

def features(s):
 groups=exact.components(s);deg=[0]*s['N']
 for u,v,j in s['edges']:deg[u]+=1;deg[v]+=1
 w,work,order=minfill(s);B=sum(map(abs,s['fields']))+sum(abs(j) for u,v,j in s['edges']);roots=1<<max(1,B).bit_length();primes=[998244353,1004535809,469762049,167772161,1224736769];prod=1;pc=0
 while prod<=1<<s['N']:prod*=primes[pc];pc+=1
 return dict(N=s['N'],source_family=s.get('family','UNKNOWN'),graph_hash=digest(dict(N=s['N'],edges=s['edges'],fields=s['fields'])),source_hash=s['source_sha256'],edges=len(s['edges']),degree_min=min(deg),degree_max=max(deg),degree_mean=statistics.mean(deg),degree_std=statistics.pstdev(deg),components=len(groups),component_sizes=sorted(map(len,groups)),max_component=max(map(len,groups)),local_assignments=sum(1<<len(g) for g in groups),minfill_width=w,minfill_work=work,minfill_order=order,energy_bound=B,root_bound=roots,crt_primes=pc,arithmetic_burden=work*roots*pc,coefficient_bound=str(1<<s['N']),coupling_multiplicities=dict(Counter(str(j) for _,_,j in s['edges'])),symmetry='not assumed',degree_signature=sorted(deg))

def atlas():
 rows=[]
 for n in range(1,121):
  c=canonical(n);f=features(c['source']);pl=c['plan'];sel=pl.get('selected',{})
  row={**{'pre_'+k:v for k,v in f.items()},'N':n,'provenance':'INHERITED; graph features NEWLY_DERIVED retrospectively','post_seconds':c['timing']['seconds'],'post_method':c['timing']['method'],'post_hardware':c['timing']['hardware'],'post_retained_width':sel.get('width',pl.get('width')),'post_branches':sel.get('branches'),'post_work':sel.get('weighted_entries',pl.get('local_assignment_count')),'post_roots':pl.get('root_count'),'post_primes':len(pl.get('primes',[])) or None,'post_ground':c['spectrum']['ground_energy'],'post_degeneracy':c['spectrum']['ground_degeneracy'],'post_bins':len(c['spectrum']['scalar_dos']),'post_output_hash':digest(c['spectrum']),'post_stages':c['timing'].get('stages',{}),'post_plan_selection':'historical selected plan; descriptive only'}
  rows.append(row)
 save(P/'ATLAS_ROWS.json',rows);writecsv(P/'CANONICAL_ATLAS.csv',rows)
 save(P/'FEATURE_SCHEMA.json',dict(pre_execution=[k for k in rows[0] if k.startswith('pre_')],post_execution=[k for k in rows[0] if k.startswith('post_')],missing='JSON null/CSV empty means unretained, never zero-imputed timing',feature_provenance='structural PRE-eligible features computed now from frozen graphs; historical selected-plan features POST-selected and excluded from prospective regression',unretained=['peak_RAM unless execution record retained','CPU/GPU split unless retained','symmetry certificate','communication timings','verification stage timing'],canonical_policy='N100/N105 packet defaults; all other sizes inherited frustrated sources. Alternate connected N100/N105 kept separate.'))
 return dict(rows=120,hash=sha(P/'CANONICAL_ATLAS.csv'))
def writecsv(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with Path(p).open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
def loo(X,y):
 out=[]
 for i in range(len(y)):
  keep=np.arange(len(y))!=i;b=np.linalg.lstsq(X[keep],y[keep],rcond=None)[0];out.append(float(X[i]@b))
 return np.asarray(out)
def analyze():
 rows=load(P/'ATLAS_ROWS.json');valid=[r for r in rows if r['post_seconds'] and r['post_seconds']>0];y=np.log([r['post_seconds'] for r in valid]);models={}
 definitions={'N':['N'],'formal_state_count':['N'],'fresh_width':['pre_minfill_width'],'component_assignments':['pre_local_assignments'],'components':['pre_components','pre_max_component'],'arithmetic':['pre_arithmetic_burden'],'structural':['pre_minfill_width','pre_components','pre_max_component','pre_root_bound','pre_crt_primes']}
 predictions={}
 for name,cols in definitions.items():
  # Formal log(2^N) is exactly proportional to N; both baselines intentionally coincide.
  X=np.asarray([[1]+[math.log2(max(1,r[c])) if c in ['pre_local_assignments','pre_arithmetic_burden','pre_root_bound'] else r[c] for c in cols] for r in valid],float)
  pred=loo(X,y);b=np.linalg.lstsq(X,y,rcond=None)[0];models[name]=dict(features=cols,coefficients=b.tolist(),loo_log_MAE=float(np.mean(abs(pred-y))),fit_log_R2=float(1-np.sum((X@b-y)**2)/np.sum((y-y.mean())**2)),scope='retrospective descriptive mixed-hardware atlas; not a frontier calibration');predictions[name]=pred
 # Hardware-stratified estimates avoid presenting CPU/GPU differences as graph effects.
 strata={}
 for hw in sorted({r['post_hardware'] for r in valid}):
  ids=[i for i,r in enumerate(valid) if r['post_hardware']==hw]
  if len(ids)<5:strata[hw]=dict(n=len(ids),status='insufficient independent examples');continue
  X=np.asarray([[1,math.log2(max(1,valid[i]['pre_arithmetic_burden'])),valid[i]['pre_minfill_width']] for i in ids]);yy=y[ids];pp=loo(X,yy);strata[hw]=dict(n=len(ids),loo_log_MAE=float(np.mean(abs(pp-yy))))
 score=abs(predictions['structural']-y);anomalies=[dict(N=valid[i]['N'],log_error=float(score[i]),question='Which source/route/stage explains residual cost?') for i in np.argsort(-score)[:15]]
 # Deterministic standardized structural nearest neighbours and 3-means, inspection only.
 cols=['pre_minfill_width','pre_components','pre_max_component','pre_degree_mean','pre_root_bound'];A=np.asarray([[r[k] for k in cols] for r in rows],float);A=(A-A.mean(0))/np.maximum(A.std(0),1e-9);centers=A[[10,70,104]].copy()
 for _ in range(20):
  labs=np.argmin(((A[:,None]-centers)**2).sum(2),axis=1)
  for k in range(3):
   if np.any(labs==k):centers[k]=A[labs==k].mean(0)
 neighbours=[]
 for i,r in enumerate(rows):
  dist=((A-A[i])**2).sum(1);dist[i]=np.inf;j=int(np.argmin(dist));neighbours.append(dict(N=i+1,neighbor=j+1,distance=float(dist[j]),regime=int(labs[i])))
 transitions=[dict(from_N=a['N'],to_N=b['N'],ratio=b['post_seconds']/a['post_seconds'],root_change=[a['post_roots'],b['post_roots']],branch_change=[a['post_branches'],b['post_branches']],width_change=[a['post_retained_width'],b['post_retained_width']],family_change=a['pre_source_family']!=b['pre_source_family'],hardware_change=a['post_hardware']!=b['post_hardware']) for a,b in zip(rows,rows[1:]) if a['post_seconds'] and b['post_seconds'] and (b['post_seconds']/a['post_seconds']>1.5 or b['post_seconds']/a['post_seconds']<.67)]
 out=dict(models=models,hardware_strata=strata,anomalies=anomalies,neighbors=neighbours,transitions=transitions)
 save(P/'MODELS.json',out);(P/'MODEL_SUMMARY.md').write_text('# Interpretable baselines\n\n'+json.dumps(models,indent=2)+'\n\nHardware strata:\n'+json.dumps(strata,indent=2)+'\nNo post-result features enter these fits. Historical selected-route comparisons are descriptive. N and log formal state-count carry identical information.\n')
 (P/'STRUCTURAL_REGIMES.md').write_text('# Structural regimes\n\nThree-means and standardized nearest neighbours are exploratory descriptions, not source classes or certificates.\n\nTransitions:\n'+json.dumps(transitions,indent=2)+'\n\nNeighbours:\n'+json.dumps(neighbours,indent=2))
 comparison=[{k:r[k] for k in ['N','pre_source_family','pre_components','pre_component_sizes','pre_local_assignments','pre_minfill_width','post_seconds','post_hardware','post_method']} for r in rows if r['N'] in [99,100,101,104,105,106]]
 (P/'N100_N105_FORENSIC.md').write_text('# N100/N105 structural forensics\n\nRetrospective family transfer, not a located preregistered prediction. N100 ran before N105 on August2. The causal claim about skippingN108 is not established.\n\n'+json.dumps(comparison,indent=2)+'\n\nMinimal explanation: independent components bound local enumeration by the sum of component state counts, followed by polynomial convolution. Packet N100/N105 have largest component15; nearby canonical connected sources cannot use that decomposition. Adding the restored packet changes local assignment work only modestly. Hardware and historical execution scopes differ, so the time ratio alone is not a causal measurement. New within-host component/VE comparisons and bridge ablations test this explanation.\n')
 pair=[rows[95],rows[119]]
 (P/'N96_N120_SCALING.md').write_text('# N96/N120 separate frustrated lineage\n\nN120 preserves228N96edges and all96fields, replaces12edges and adds24vertices,48internal and24cross edges. This is separate from packet restoration. N96 retained timing and N120 use different reconstruction generations; comparisons retain that distinction.\n\n'+json.dumps(pair,indent=2)+'\n\nBranch count, retained width, transform length and five-prime CRT jointly determine work. These are plan-dependent costs, not N-only scaling. The current learner compares fresh graph-only structure with historical plan burden and seeks same-source route alternatives.\n')
 predictions_future=[]
 for n in range(121,145):predictions_future.append(dict(N=n,claim_type='CONDITIONAL_UNEXECUTED',source_defined=False,regime='unknown until graph/lineage supplied',preferred_method={'max_component_15':'components','connected_frustrated':'compare inherited cutset and expanded planning'},width=None,work_class='sum(2^component_size) or roots*prime_count*sum(2^retained_width)*branches',CRT_prime_count=next((i for i in range(1,6) if math.prod([998244353,1004535809,469762049,167772161,1224736769][:i])>1<<n),None),NTT_class='next power of two strictly greater than source energy bound',RAM_VRAM='conditional on factor widths and batching; no source-independent value',runtime_interval=None,expensive_stage='component enumeration/convolution or conditioned elimination, depending on source',confidence='source unresolved; no numerical frontier forecast',nearest_analogs=[100,105] if n%5==0 else [96,120]))
 save(P/'PREDICTIONS_121_144.json',predictions_future)
 return dict(baselines=len(models),anomalies=anomalies)

def compare_answer(actual,expected):
 def dos(x):return {int(e):int(v) for e,v in x}
 assert dos(actual['scalar_dos'])==dos(expected['scalar_dos'])
 def rows(a):
  if 'port_rows' in a:return {tuple(r['state']):dos(r['dos']) for r in a['port_rows']}
  ports=a.get('retained_ports',list(range(4)));return {tuple(1 if mask>>i&1 else -1 for i in range(len(ports))):dos(row['dos'] if isinstance(row,dict) else row) for mask,row in enumerate(a['closed_port_rows'])}
 assert rows(actual)==rows(expected), 'Full retained-port density mismatch'
 return dict(full_scalar_equality=True,port_equality=set(rows(actual))==set(rows(expected)),configuration_count=actual['configuration_count'],checks='native exact count/first/second moment and all port closures passed')
def independent(s,ports):
 hist={i:Counter() for i in range(1<<len(ports))}
 for bits in range(1<<s['N']):
  spins=[1 if bits>>i&1 else -1 for i in range(s['N'])];e=-sum(j*spins[u]*spins[v] for u,v,j in s['edges'])-sum(h*x for h,x in zip(s['fields'],spins));mask=sum((1<<i) for i,v in enumerate(ports) if spins[v]==1);hist[mask][e]+=1
 return exact.finalize_answer(s,ports,hist)

def solve_plan(s,plan,seconds=60):
 fixed=plan['selected']['cutset'];ports=plan['ports'];hist={i:Counter() for i in range(1<<len(ports))};work=0;t=time.monotonic()
 assert s['N']<=24 and len(fixed)<=8
 for branch in range(1<<len(fixed)):
  if time.monotonic()-t>seconds:raise TimeoutError('plan budget')
  signs={v:1 if branch>>i&1 else -1 for i,v in enumerate(fixed)};sites=[v for v in range(s['N']) if v not in fixed];mp={v:i for i,v in enumerate(sites)};fields=[s['fields'][v] for v in sites];edges=[];constant=-sum(s['fields'][v]*z for v,z in signs.items())
  for u,v,j in s['edges']:
   if u in signs and v in signs:constant-=j*signs[u]*signs[v]
   elif u in signs:fields[mp[v]]+=j*signs[u]
   elif v in signs:fields[mp[u]]+=j*signs[v]
   else:edges.append([mp[u],mp[v],j])
  reduced=dict(N=len(sites),fields=fields,edges=edges,parent_vertices=list(range(len(sites))),family='CONDITIONED_EXACT_BRANCH');reduced=exact.validate_source(reduced)
  r=exact.solve_cpu(reduced,ports=[mp[v] for v in ports],options=dict(method='variable_elimination',elimination_order=[mp[v] for v in plan['selected']['order']],max_seconds=max(1,int(seconds-(time.monotonic()-t))),max_factor_work=2000000,max_intermediate_entries=65536))
  work+=r['execution']['arithmetic_work_units']
  for row in r['answer']['port_rows']:
   mask=sum(1<<i for i,x in enumerate(row['state']) if x==1)
   for e,c in row['dos']:hist[mask][int(e)+constant]+=int(c)
 return dict(status='EXACT',answer=exact.finalize_answer(s,ports,hist),execution=dict(arithmetic_work_units=work,elapsed_ns=int((time.monotonic()-t)*1e9)))

class Research:
 def __init__(self,base):self.base=base
 def close(self):self.base.close()
 def execute(self,op,payload):
  if op!='GEN4_FRUSTRATED_LEARN1':return self.base.execute(op,payload)
  assert payload['code_sha256']==sha(__file__);q=payload['question'];kind=q['kind']
  if kind=='atlas':return atlas()
  if kind=='analysis':return analyze()
  c=canonical(q['N']);s=c['source']
  if q.get('variant'):
   s=load(P/q['variant'])['source'];s=exact.validate_source({k:v for k,v in s.items() if k!='source_sha256'})
  assert s['N']<=120
  if kind=='plans':
   frozen=load(P/'runtime/CURRENT_REVISION/engines/SLC/gen3/spin_data/PARENT_PLAN.json');previous=canonical(max(1,min(q['N']-1,96)))['plan'];plans=spin_expanded.expanded(s,frozen,previous)
   return dict(status='LEARNED_HEURISTIC',source=s['source_sha256'],N=s['N'],plans=plans,features=features(s),meaning='structural planning only; no new DOS',method_roster=METHODS)
  if kind=='solve':
   method=q['method'];ports=c['spectrum'].get('retained_ports',list(range(min(4,s['N']))));ports=ports if ports and isinstance(ports[0],int) else list(range(min(4,s['N'])))
   if method in ['components','variable_elimination']:
    r=exact.solve_cpu(s,ports,dict(method=method,max_component_size=18,max_assignments=400000,max_seconds=60,max_factor_work=2000000,max_intermediate_entries=65536))
   elif method=='incremental_boundary':
    assert s['N']<=18
    # Exact explicit all-spin boundary continuation; no scalar-spectrum reuse.
    n=s['N'];small=copy.deepcopy(s);small.update(N=n-1,fields=s['fields'][:-1],edges=[e for e in s['edges'] if max(e[:2])<n-1]);energies=[]
    for bits in range(1<<(n-1)):
     z=[1 if bits>>i&1 else -1 for i in range(n-1)];energies.append(-sum(h*x for h,x in zip(small['fields'],z))-sum(j*z[u]*z[v] for u,v,j in small['edges']))
    hist={i:Counter() for i in range(1<<len(ports))};t=time.perf_counter_ns()
    for bits,e0 in enumerate(energies):
     z=[1 if bits>>i&1 else -1 for i in range(n-1)];field=s['fields'][-1]+sum(j*z[u] for u,v,j in s['edges'] if v==n-1)
     for zlast in [-1,1]:
      state=z+[zlast];mask=sum(1<<i for i,v in enumerate(ports) if state[v]==1);hist[mask][e0-zlast*field]+=1
    r=dict(status='EXACT',answer=exact.finalize_answer(s,ports,hist),execution=dict(elapsed_ns=time.perf_counter_ns()-t,arithmetic_work_units=1<<n,boundary_preparation_excluded=True,boundary_states=1<<(n-1)))
   else:r=solve_plan(s,q['plan'])
   if not q.get('variant'):r['verification']=compare_answer(r['answer'],c['spectrum'])
   if s['N']<=16:r['independent_verification']=compare_answer(r['answer'],independent(s,ports))
   elif q.get('variant'):
    other=exact.solve_cpu(s,ports,dict(method='variable_elimination' if method=='components' else 'components',max_component_size=18,max_assignments=400000,max_seconds=60,max_factor_work=2000000,max_intermediate_entries=65536));r['independent_verification']=compare_answer(r['answer'],other['answer'])
   return r
  if kind=='component_rule':
   groups=exact.components(s);seen=set();edges=s['edges'];mapping={v:i for i,g in enumerate(groups) for v in g}
   assert sorted(v for g in groups for v in g)==list(range(s['N']));assert all(mapping[u]==mapping[v] for u,v,j in edges)
   return dict(status='CERTIFIED_EXACT_RULE',rule='DISCONNECTED_COMPONENT_CONVOLUTION',certificate=dict(groups=groups,source_hash=s['source_sha256'],edge_separation=True),derivation='H=sum_c H_c over disjoint variables, so sum_s z^H(s)=product_c sum_{s_c} z^H_c(s_c). Ordered retained port conditions factor with the same partition; convolution preserves all coefficients.',scope='pair-interaction source with the supplied independently checked partition; no intercomponent edge')
  raise ValueError(kind)
