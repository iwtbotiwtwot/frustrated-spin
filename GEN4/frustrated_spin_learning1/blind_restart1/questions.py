"""Bounded scientific question generation from this run's returned evidence only."""
import math,time,copy,statistics
from pathlib import Path
from research import load,save,digest,sha,canonical,features
P=Path(__file__).resolve().parent

def make(kind,n=None,theme='structure',parent=None,why='',gain=10,cost=1,**extra):
 q=dict(kind=kind,N=n,theme=theme,parent_question=parent,question=why,why_chosen=why,expected_information_gain=gain,predicted_cost_seconds=max(.2,cost),maximum_admitted_seconds=180 if kind!='gpu_compare' else 900,claim_type='NEWLY_PRECOMMITTED',features_used='source structure and completed results from this fresh campaign',expected_discriminating_outcomes=['measured difference supports the proposed structural explanation','counterexample changes the proposed route or hypothesis','capacity finding redirects to decomposition or planning'],verification_contract='Full density and retained-port equality for completed solves; structural results are not primality or DOS certificates',**extra)
 identity={k:v for k,v in q.items() if k in ['kind','N','variant','method','mode','level','other_N','ports','plans','replication'] and v is not None};q['question_id']=digest(identity)[:24];q['inputs_hashes']={}
 q['candidate_methods']=[q['method']] if q.get('method') else [p.get('training_method',p['selected'].get('method','retained')) for p in q.get('plans',[])] or list(load(P/'METHOD_DEFINITIONS.json'))
 if n:q['source_lineage']=canonical(n)['provenance'];q['inputs_hashes'][f'canonical/N{n:03d}.json']=sha(P/f'canonical/N{n:03d}.json')
 if q.get('variant'):q['inputs_hashes'][q['variant']]=sha(P/q['variant'])
 return q

def enqueue(state,q):
 if q['question_id'] in state['seen']:return False
 state['seen'].append(q['question_id']);state['queue'].append(q);state['generated']+=1;return True

def initial(state):
 enqueue(state,make('atlas',theme='atlas',why='Recover every N1–120 source structure and explicitly separate PRE features from POST measurements',gain=1000))

def changed_source(v):return v['features']['structural_signature']!=v['parent_features']['structural_signature']
def follow(state,q,r,error=None):
 children=[];qid=q['question_id'];n=q.get('N')
 def add(kind,nn=n,**kw):
  child=make(kind,nn,parent=qid,**kw)
  if enqueue(state,child):children.append(child['question_id'])
 if error:
  if n and q['kind'] not in ['plans','compare','component_rule']:
   add('plans',theme='capacity_explanation',variant=q.get('variant'),why='Which exact decomposition or width feature explains the failed execution capacity?',gain=30)
  return children
 v=r['value'];kind=q['kind']
 if kind=='atlas':add('analysis',None,theme='cost_models',why='Fit simple atlas cost baselines, examine transitions and nearest structural neighbours before choosing experiments',gain=1000)
 elif kind=='analysis':
  m=load(P/'MODELS.json');anchors={96,120,99,100,101,104,105,106,72,84,108}
  anchors.update(x['N'] for x in m['anomalies'][:10]);anchors.update(x['from_N'] for x in m['transitions'][:8]);anchors.update(x['to_N'] for x in m['transitions'][:8])
  for nn in sorted(anchors):
   add('plans',nn,theme='method_choice',why='Which source-specific exact method explains this observed runtime discontinuity or anomaly?',gain=35 if nn in [96,100,105,120] else 15,cost=3)
   add('component_rule',nn,theme='exact_reductions',why='Does the explicit interaction graph admit an exact independent-component factorization?',gain=10)
  for x in m['neighbors']:
   if x['N'] in anchors:add('compare',x['N'],theme='source_transfer',other_N=x['neighbor'],why='Why do these nearest structural neighbours have similar or different execution cost?',gain=12)
  for nn,other in [(99,100),(100,101),(104,105),(105,106),(96,120)]:add('compare',nn,theme='forensics',other_N=other,why='Find the smallest structural and arithmetic change that explains the observed cost difference',gain=45)
 elif kind=='compare':
  for nn in [n,q['other_N']]:add('plans',nn,theme='source_transfer',why='Test whether neighbouring-source structure suggests a reusable exact execution plan',gain=16)
  # A graph intervention distinguishes a structural explanation from a size association.
  mode='bridge' if v['a']['components']>1 else 'coupling'
  add('variant',theme='causal_ablation',mode=mode,level=1,why='Change one relevant structural ingredient at fixed N to distinguish the competing cost explanations',gain=20)
 elif kind=='component_rule':
  groups=v['certificate']['groups']
  if len(groups)>1:
   add('variant',theme='exact_reductions',mode='bridge',level=1,why='Find the boundary where the proposed component-factorization reduction stops applying',gain=25)
   if max(map(len,groups))<=18:
    for method in ['components','variable_elimination']:add('solve',theme='method_choice',method=method,why='Measure exact component and elimination work on the same source with full closure',gain=35)
 elif kind=='plans':
  f=v['features'];variants=q.get('variant');plans=v['plans'];eligible=[]
  for p in plans:
   sel=p['selected'];work=sel['weighted_entries']*p['root_count']*len(p['primes']);estimated=12+work/8e10
   if sel['width']<=22 and sel['branches']<=2048 and estimated<220:eligible.append((estimated,p))
  if f['max_component']<=18 and f['local_assignments']<400000:add('solve',theme='method_choice',method='components',variant=variants,why='Verify whether source decomposition actually yields the predicted low exact cost',gain=20)
  if f['minfill_width']<=14 and f['minfill_work']<500000:
   add('solve',theme='method_choice',method='variable_elimination',variant=variants,why='Acquire a distinct exact counterfactual method and retain every density coefficient',gain=18)
   if n<=18:add('solve',theme='boundary_reuse',method='incremental_boundary',variant=variants,why='Compare exact incremental boundary continuation with recomputation',gain=15)
   for p in plans[:6]:
    if p['selected']['width']<=8:add('solve',theme='method_choice',method=p.get('training_method','fresh_min_fill'),variant=variants,plan=p,why='Measure this distinct exact planning method on an admitted cheap source',gain=12)
  elif eligible:
   eligible.sort(key=lambda x:x[0]);chosen=[eligible[0][1]]
   # Retain one meaningful competing order/cutset, not every alias of the same plan.
   signature=lambda p:(tuple(p['selected']['cutset']),tuple(p['selected']['order']))
   for _,p in eligible[1:]:
    if signature(p)!=signature(chosen[0]):chosen.append(p);break
   proof=load(P/variants).get('proof') if variants else True
   if proof or len(chosen)>1:add('gpu_compare',theme='method_choice',variant=variants,plans=chosen,repeats=2,why='Which competing exact plan is faster on this source using the restored shared fourteen-worker backend?',gain=50,cost=sum(12+p['selected']['weighted_entries']*p['root_count']*len(p['primes'])/8e10 for p in chosen)*2)
  if not variants:
   for mode in ['gauge','permutation','rewire','coupling','fieldzero']:
    add('variant',theme={'gauge':'symmetry','permutation':'representation','rewire':'topology','coupling':'coupling_fields','fieldzero':'coupling_fields'}[mode],mode=mode,level=1,why=f'Does {mode} change exact method choice or work at fixed N, and which source property explains it?',gain=12)
   ports=canonical(n)['spectrum'].get('retained_ports',list(range(min(4,n))))
   for chosen in [ports[:1],ports[:2],[]]:add('ports',theme='boundary_reuse',ports=chosen,why='What exact retained-boundary information can be eliminated by coefficient-wise marginalization?',gain=7)
 elif kind=='variant' and v['status']!='NOT_APPLICABLE':
  signature=v['features']['graph_hash'];seen=state.setdefault('variant_graphs',{})
  if signature in seen:
   state['neutral'][f'{n}:{q["mode"]}']=2
   return []
  seen[signature]=qid
  variant=v['variant'];add('plans',theme=q['theme'],variant=variant,why='Determine whether the changed source alters widths, arithmetic work, or the preferred exact route',gain=20)
  if v.get('proof'):add('symmetry',theme='exact_reductions',variant=variant,why='Can an explicit reversible source transformation be independently certified as preserving all energies and port states?',gain=18)
  novelty=changed_source(v);branch=f'{n}:{q["mode"]}';state['neutral'][branch]=0 if novelty else state['neutral'].get(branch,0)+1
  # Expand only evidence-responsive levels, with neutral streaks closing a branch.
  if novelty and q.get('level',1)<8 and state['neutral'][branch]<2:
   add('variant',theme=q['theme'],mode=q['mode'],level=q['level']+1,why='The first intervention changed the structural regime; locate the next transition and test whether the explanation survives',gain=10,cost=2)
 elif kind in ['solve','gpu_compare']:
  f=features(canonical(n)['source']) if not q.get('variant') else features(load(P/q['variant'])['source']);best=None
  if kind=='gpu_compare':
   timings={}
   for x in v['measurements']:
    if not x['cold_workers']:timings.setdefault(x['method'],[]).append(x['seconds'])
   med={k:statistics.median(a) for k,a in timings.items()};best=min(med,key=med.get) if med else None
   if len(med)>1 and max(med.values())/max(1e-9,min(med.values()))<1.15 and not q.get('replication'):
    add('gpu_compare',theme='timing_uncertainty',variant=q.get('variant'),plans=q['plans'],replication=1,repeats=3,why='The competing methods were nearly tied; do additional alternating measurements distinguish noise from a reproducible route advantage?',gain=30,cost=sum(med.values())*3+12)
   if med:state['observations'].append(dict(N=n,variant=q.get('variant'),backend=v['backend'],methods=med,features=f,parent=qid,work_by_method={p.get('training_method',p['selected'].get('method','retained')):p['selected']['weighted_entries']*p['root_count']*len(p['primes']) for p in v['plans']}))
  else:state['observations'].append(dict(N=n,variant=q.get('variant'),backend='CPU',methods={q['method']:r['seconds']},features=f,parent=qid,work_by_method={q['method']:f['local_assignments'] if q['method']=='components' else f['minfill_work']}))
  if not q.get('variant'):
   mode='bridge' if f['components']>1 else 'rewire';add('variant',theme='heldout_transfer',mode=mode,level=2,why='Challenge the measured route advantage on a new fixed-N source that was not used to choose it',gain=25)
  # Directly request a neighbour based on this result, not only a preloaded list.
  rows=load(P/'ATLAS_ROWS.json');near=sorted((x for x in rows if x['N']!=n),key=lambda x:abs(x['pre_minfill_width']-f['minfill_width'])+abs(math.log2(max(1,x['pre_local_assignments']))-math.log2(max(1,f['local_assignments']))))[:2]
  for x in near:add('plans',x['N'],theme='heldout_transfer',why='Test transfer of the observed cost explanation to a structurally similar canonical source',gain=20)
 return children

def refill(state):
 """A review pass widens unanswered scientific coverage when current children are exhausted."""
 if not (P/'ATLAS_ROWS.json').exists():return 0
 added=0;rows=load(P/'ATLAS_ROWS.json');studied={q['N'] for q in state['completed_questions'] if q['kind']=='plans'}
 for r in sorted(rows,key=lambda r:(r['N'] in studied,-r['pre_minfill_width'])):
  if r['N'] not in studied:
   added+=enqueue(state,make('plans',r['N'],theme='coverage',why='Frontier review found this structural regime has no measured method-choice investigation',gain=12,cost=4))
   if added>=8:break
 if added:return added
 # Broaden the scientific intervention, without repeating an equivalent seed sweep.
 for r in rows:
  for mode in ['bridge','fieldzero','coupling','permutation','gauge','rewire']:
   branch=f'{r["N"]}:{mode}'
   if state['neutral'].get(branch,0)>=2:continue
   if enqueue(state,make('variant',r['N'],theme='unanswered_intervention',mode=mode,level=1,why='Frontier review found an untested causal distinction in the source-to-method map',gain=8,cost=2)):added+=1
   if added>=8:return added
 return added

def score(state,q):
 # Information / cost, family balance, and explicit waiting age prevent one cheap branch monopolizing the run.
 count=state['theme_counts'].get(q['theme'],0);age=max(0,state['steps']-q.get('enqueued_step',0));novel=2 if count==0 else 0
 predicted=q['predicted_cost_seconds']
 if q['kind']=='gpu_compare' and state.get('cost_models'):
  estimates=[]
  for p in q['plans']:
   method=p.get('training_method',p['selected'].get('method','retained')); candidates=[m for m in state['cost_models'].values() if m['method']==method and m['backend']!='CPU']
   if candidates:
    m=candidates[0];work=p['selected']['weighted_entries']*p['root_count']*len(p['primes']);estimates.append(math.exp(max(-10,min(15,m['intercept']+m['slope']*math.log(max(1,work))))))
  if estimates:predicted=12+sum(estimates)*q.get('repeats',2);q['fresh_cost_prediction_seconds']=predicted
 return (q['expected_information_gain']+novel)/(max(.2,predicted)**.5)/(1+count)**.35 + min(age,200)*.1
