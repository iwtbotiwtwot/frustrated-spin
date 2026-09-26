"""Outcome-driven extension: bounded breadth, branching experiments and active follow-up."""
import sys,os,json,time,signal,subprocess,fcntl,math,copy,statistics,datetime,traceback
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path[:0]=[str(P),str(ROOT)]
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from operations import canonical,normalize,load,save,digest,sha,features,exact,compare_answer
from research import append,writecsv
stop=False;child=None
def signal_stop(signum,frame):
 global stop
 stop=True
 if child and child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal_stop)
def qmake(kind,n,methods=None,variant=None,why='',parent=None,stage=0,priority=5,**extras):
 q=dict(kind=kind,N=n,methods=methods or [],variant=variant,question=why,parent_question=parent,stage=stage,repeats=3,maximum_admitted_seconds=180,predicted_cost_seconds=3,expected_information_gain=priority,source_lineage=canonical(n)['provenance'],claim_type='NEWLY_PRECOMMITTED',features_used='source features, prior outcomes and measured timing dispersion',expected_discriminating_outcomes=['repeated advantage survives matched-source controls','counterexample changes method choice','certificate verifies exact transformation','capacity failure identifies boundary'],verification_contract='Full DOS and all ordered port rows equal retained canonical or a second exact route; exact count and moments retained',**extras)
 q['inputs_hashes']={f'canonical/N{n:03d}.json':sha(ROOT/f'canonical/N{n:03d}.json')}
 if variant:q['inputs_hashes'][variant]=sha(ROOT/variant)
 q['question_id']=digest({k:v for k,v in q.items() if k not in ['predicted_cost_seconds','expected_information_gain']})[:24];return q

def variant(n,mode,level):
 s=copy.deepcopy(canonical(n)['source']);meta={}
 if mode in ['hub','chain']:
  gs=exact.components(s)
  for i in range(min(level,len(gs)-1)):
   a=gs[0][min(i,len(gs[0])-1)] if mode=='hub' else gs[i][-1];b=gs[i+1][0];s['edges'].append([min(a,b),max(a,b),1 if i%2==0 else -1])
  meta=dict(bridge_count=min(level,len(gs)-1),mode=mode)
 elif mode=='swap':
  from variant_generator import graph_family
  s=graph_family(s,level);meta=dict(seed=level,generator='retained degree-preserving six-edge-swap generator')
 elif mode=='gauge':
  g=[-1 if int(digest([n,level,i])[:4],16)%2 else 1 for i in range(n)];s['fields']=[h*z for h,z in zip(s['fields'],g)];s['edges']=[[u,v,j*g[u]*g[v]] for u,v,j in s['edges']];meta=dict(gauge=g)
 elif mode=='fieldzero':s['fields']=[0]*n;meta=dict(change='remove fields only, pair-graph definition unchanged')
 else:raise ValueError(mode)
 s['family']='FOLLOWUP1_'+mode;s=normalize(s);f=P/'variants'/f'N{n}_{mode}_{level}.json'
 if not f.exists():save(f,dict(kind='NEW_VARIANT',source=s,provenance=meta,parent_hash=canonical(n)['source']['source_sha256']))
 return str(f.relative_to(ROOT)),meta

def initialize():
 prior=load(ROOT/'STATE.json');state=dict(started=time.time(),deadline=prior['deadline'],status='STARTING',queue=[],done={},completed={},seen_structure={},next_seed={},generated=0)
 for n in [100,105]:
  state['queue'].append(qmake('paired',n,['components','variable_elimination','memo_components','warm_components'],why='Does exact repeated-component reuse improve on the observed packet elimination advantage?',priority=100))
  for mode in ['hub','chain']:
   v,meta=variant(n,mode,1);state['queue'].append(qmake('paired',n,['variable_elimination','conditional_components'],v,why='Does conditioning a bridge recover cheap independent components?',priority=70,branch_mode=mode,level=1))
 # Explore all cheap structural regimes, not a blanket N<=20 ceiling.
 for row in load(ROOT/'ATLAS_ROWS.json'):
  n=row['N']
  if n in [100,105]:continue
  if row['pre_minfill_width']<=7 and row['pre_minfill_work']<100000:
   methods=['variable_elimination','components'] if row['pre_max_component']<=18 else ['variable_elimination','conditional_components']
   state['queue'].append(qmake('paired',n,methods,why='Test route choice on low-width sources beyond the previous size ceiling',priority=10+row['pre_minfill_width']))
 for n in [72,84,96,100,105,108,120]:
  v,meta=variant(n,'gauge',1);state['queue'].append(qmake('gauge_certificate',n,variant=v,why='Can an explicit sign-bijection certify exact source reuse at fixed N?',priority=20,**meta))
  v,meta=variant(n,'swap',4);state['queue'].append(qmake('planning',n,variant=v,why='Which same-N changes move width/work across a route boundary?',priority=20,seed=4,neutral=0))
 return state

def semantic(q):return digest({k:q.get(k) for k in ['kind','N','methods','variant','stage','seed','level','branch_mode','requested_ports','plan','root_batch','max_cutset']})

def enqueue(state,q):
 signature=semantic(q)
 if any(semantic(x)==signature for x in state['queue']) or any(semantic(x['question'])==signature for x in state['completed'].values()):return
 if q['question_id'] in state['done'] or any(x['question_id']==q['question_id'] for x in state['queue']):return
 state['queue'].append(q);state['generated']+=1

def follow(state,q,r):
 v=r['value'];kids=[]
 def add(child):enqueue(state,child);kids.append(child['question_id'])
 if q['kind']=='paired':
  cv=max(v['coefficient_of_variation'].values());ordered=sorted(v['median_seconds'].values());ratio=ordered[1]/ordered[0] if len(ordered)>1 else 1
  if (cv>.12 or ratio<1.2) and q['stage']<3:
   child=qmake('paired',q['N'],q['methods'],q.get('variant'),why='Does the apparent near-tie/noisy advantage persist with additional alternating-order measurements?',parent=q['question_id'],stage=q['stage']+1,priority=15+cv*10,repetition_reason='timing uncertainty');child['repeats']=min(9,3+2*(q['stage']+1));add(child)
  if q.get('branch_mode') and q['level']<7 and r['seconds']<45:
   vpath,meta=variant(q['N'],q['branch_mode'],q['level']+1);add(qmake('paired',q['N'],q['methods'],vpath,why='Where does bridge-conditioned component reuse cease to beat generic elimination?',parent=q['question_id'],priority=35,branch_mode=q['branch_mode'],level=q['level']+1))
  # A returned cheap computation licenses a nearby same-N structural control.
  if not q.get('variant') and q['N']>=12 and q['N'] not in [100,105]:
   vpath,meta=variant(q['N'],'swap',7);add(qmake('planning',q['N'],variant=vpath,why='Does the selected cheap route survive degree-preserving rewiring?',parent=q['question_id'],priority=18,seed=7,neutral=0))
  if q['N'] in [100,105] and not q.get('variant') and 'requested_ports' not in q:
   for ps in [[],canonical(q['N'])['spectrum']['retained_ports'][:1],canonical(q['N'])['spectrum']['retained_ports'][:2]]:
    add(qmake('paired',q['N'],['variable_elimination','memo_components','warm_components'],why='Does retained-port placement prevent otherwise reusable identical component tables?',parent=q['question_id'],priority=30,requested_ports=ps))
   vpath,meta=variant(q['N'],'fieldzero',0);add(qmake('paired',q['N'],['variable_elimination','memo_components'],vpath,why='Is packet reuse controlled by topology or broken by field-dependent component identities?',parent=q['question_id'],priority=35))
  # Record falsifiable repeated result, not a theorem from timing.
  append(P/'RULE_CANDIDATES.jsonl',dict(question=q['question_id'],status='REPEATED_EMPIRICAL_RULE',fastest=v['fastest'],medians=v['median_seconds'],source=v['source_hash'],candidate='structure-conditioned route choice',exactness='all full densities agree; runtime ranking is empirical'))
 elif q['kind']=='planning':
  f=v['features'];plans=v['plans'];best=min(plans,key=lambda p:p['selected']['weighted_entries']);signature=digest(dict(N=q['N'],components=f['component_sizes'],width=best['selected']['width'],logwork=int(math.log2(max(1,best['selected']['weighted_entries']))*4)))
  novel=signature not in state['seen_structure'];state['seen_structure'][signature]=q['question_id']
  cost=best['selected']['weighted_entries'];parent=canonical(q['N'])['plan'].get('selected',{}).get('weighted_entries');gain=(parent/cost) if parent and cost else 1
  append(P/'STRUCTURAL_DISCOVERIES.jsonl',dict(N=q['N'],question=q['question_id'],signature=signature,novel=novel,work=cost,canonical_work_ratio=gain,width=best['selected']['width'],method=best['training_method']))
  if f['minfill_width']<=7 and f['minfill_work']<100000 and str(q.get('variant') or q['N']) not in state.get('blocked_exact_sources',[]):
   methods=['variable_elimination','components'] if f['max_component']<=18 else ['variable_elimination','conditional_components'];add(qmake('paired',q['N'],methods,q['variant'],why='Does a newly found structural regime actually change exact method cost?',parent=q['question_id'],priority=30))
  neutral=0 if novel else q.get('neutral',0)+1
  # Finite branching search, no endless equivalent sweeps. Successful novel branches explore farther.
  if q['seed']<512 and neutral<3:
   for offset in ([1,2] if novel and gain>1.1 else [1]):
    seed=q['seed']+offset;path,meta=variant(q['N'],'swap',seed);add(qmake('planning',q['N'],variant=path,why='Follow structural novelty/model disagreement to a new matched-N control',parent=q['question_id'],priority=8+min(10,gain),seed=seed,neutral=neutral))
 elif q['kind']=='gauge_certificate':
  # Independent verifier reconstructs every transformed coefficient, separately from native adapter.
  original=canonical(q['N'])['source'];changed=load(ROOT/q['variant'])['source'];g=v['gauge'];assert len(g)==q['N'] and all(x in [-1,1] for x in g)
  assert all(changed['fields'][i]*g[i]==original['fields'][i] for i in range(q['N']))
  edge={(u,w):j for u,w,j in changed['edges']};assert all(edge[(u,w)]*g[u]*g[w]==j for u,w,j in original['edges'])
  append(P/'CERTIFICATES.jsonl',dict(**v,independent_verifier='coefficient-wise inverse gauge reconstruction',scope='project-local compiler reuse proposal'))
 return kids

def summary(state):
 rows=[];discoveries=[]
 for rec in state['completed'].values():
  r=load(P/rec['result']);v=r['value']
  if 'median_seconds' in v:
   for m,t in v['median_seconds'].items():rows.append(dict(N=v['N'],source=v['source_hash'],method=m,arithmetic_median_seconds=t,cv=v['coefficient_of_variation'][m],question=rec['id']))
 writecsv(P/'METHOD_SCORECARD.csv',rows)
 # Fit arithmetic-only regressions, grouped by exact source for validation.
 if rows:
  import numpy as np
  fits={}
  for m in sorted({r['method'] for r in rows}):
   rs=[r for r in rows if r['method']==m];groups={}
   for r in rs:groups.setdefault(r['source'],[]).append(r)
   fits[m]=dict(independent_sources=len(groups),measured_rows=len(rs),median_seconds=statistics.median(r['arithmetic_median_seconds'] for r in rs),scope='arithmetic-only; no subprocess startup or verifier costs')
  save(P/'METHOD_MODELS.json',fits)
 failures=[v for v in state['done'].values() if v['status']!='COMPLETE'];pending=sorted(state['queue'],key=lambda q:-q['expected_information_gain']/max(.1,q['predicted_cost_seconds']))
 nexts=[q['question'] for q in pending[:5]]
 fallback=['Can a source-bound separator certificate eliminate expensive branches in connected N96/N120 without a new full solve?','Which repeated component identities remain after field and coupling changes?','Does the best measured CPU rule transfer to GPU arithmetic on already-authorized hardware?','Can uncertainty-aware routing improve held-out same-N sources?','Which explicit graph family should define a later prospective N121–144 test?']
 for q in fallback:
  if len(nexts)<5 and q not in nexts:nexts.append(q)
 save(P/'NEXT_QUESTIONS.json',nexts)
 (P/'SUMMARY.md').write_text('# Outcome-driven follow-up\n\nStatus: '+state['status']+'\nCompleted: '+str(len(state['completed']))+'; failed/capacity-limited: '+str(len(failures))+'; pending: '+str(len(pending))+'\n\nArithmetic-only method measurements:\n'+json.dumps(rows[-30:],indent=2)+'\n\nFive next scientific questions:\n'+json.dumps(nexts,indent=2)+'\n\nExact spectra never inferred from timing. Memoized components require identical explicit energy tables; separator reuse sums every fixed-spin branch. HoldoutN121–144 untouched. Original campaign remains preserved.\n')
 save(P/'FRONTIER.json',dict(questions=pending,policy='outcome-driven breadth and bounded branching: noise/near ties -> repetitions; cheap solves -> matched structural controls; bridge success -> stronger ablation; novel work -> nearby rewiring; certificates -> independent verification',saturation='three consecutive duplicate structural fingerprints stop that branch; maximum128seed index, no equivalent endless sweep'))

