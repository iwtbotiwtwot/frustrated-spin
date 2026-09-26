"""Bounded configuration check; run only inside the separate qualification directory."""
import os,sys,json,time
from pathlib import Path
P=Path(__file__).resolve().parent;assert P.name.endswith('_qualification');sys.path[:0]=[str(P),str(P/'runtime')]
from research import load,save,canonical,digest
import questions as policy
from blind_engine import Campaign
from controller import independent_rule,reports
from SAM_PROJECT.session import DomainSession
state=load(P/'STATE.json');assert len(state['completed'])==8 and len(state['done'])==8 and state['result_children']>8
out=P/'gpu_and_rule_check';out.mkdir(exist_ok=False);checks={}
with DomainSession.start('MATTER_SEARCH',objective='Check restored GPU execution and result-derived blind-restart self-follow-up wiring',output_root=out/'sessions',receipt_storage='gzip') as s:
 s.consumer=Campaign(s.consumer,out)
 for mode in ['gauge','permutation']:
  q=policy.make('variant',12,mode=mode,level=1,theme='symmetry',why='Check executable source bijection and independently verified inverse');r=s.execute('GEN4_BLIND_RESEARCH',dict(question=q),purpose=q['question']);assert r['status']=='OBSERVED_PATTERN'
  children=policy.follow(state,q,dict(value=r));assert children
  cert=policy.make('symmetry',12,variant=r['variant'],theme='exact_reductions',why='Check inverse reconstruction of generated bijection');v=s.execute('GEN4_BLIND_RESEARCH',dict(question=cert),purpose=cert['question']);verified=independent_rule(cert,v);assert verified['independent_verification'];checks[mode]=verified
 p=canonical(30)['plan'];p.setdefault('mathematical_plan_sha256',digest(p));q=policy.make('gpu_compare',30,plans=[p],repeats=2,theme='method_choice',why='Check fresh full-density N30 through the unchanged original fourteen-worker engine');q['maximum_admitted_seconds']=180;r=s.execute('GEN4_BLIND_RESEARCH',dict(question=q),purpose=q['question']);assert r['full_density_verified'];e=r['measurements'][0]['execution'];assert e['workers']==14 and all(e['roots_per_gpu']);checks['gpu']=dict(backend=r['backend'],seconds=e['total_ns']/1e9,all14_active=True,full_density_verified=True)
 children=policy.follow(state,q,dict(value=r));assert children;checks['gpu_followups']=children
 unused=next(n for n in range(1,121) if policy.make('plans',n,variant=None)['question_id'] not in state['seen'])
 error_children=policy.follow(state,policy.make('gpu_compare',unused,plans=[],theme='method_choice',why='Synthetic capacity-failure policy check'),None,error='qualified synthetic capacity event');assert error_children;checks['failure_followups']=error_children
 assert policy.refill(state)>0;checks['empty_frontier_review']=True
 reports(state);assert state['cost_models'];checks['fresh_cost_model_update']=True
 s.execute('GEN3_CHECKPOINT',{},purpose='Retain isolated restart configuration checks')
save(P/'CHECK_RESULTS.json',dict(status='PASS',initial_completed=8,initial_generated_followups=state['result_children'],checks=checks,production_state_seeded=False))
print(json.dumps(dict(status='PASS',checks=list(checks),gpu=checks['gpu'])),flush=True)
