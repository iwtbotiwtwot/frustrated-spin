"""One-time audited setup correction; preserve completed data, failures and deadline."""
import os,time
from pathlib import Path
from source_ops import load,save,append,sha
import learning
P=Path(__file__).resolve().parent
assert load(P/'BINDING_CHECK.json')['status']=='PASS'
assert not (P/'BINDING_RESTART.json').exists()
s=load(P/'STATE.json');assert not Path('/proc',str(load(P/'STATUS.json')['pid'])).exists()
old_hash=sha(P/'STATE.json');save(P/'STATE_BEFORE_BINDING_FIX.json',s)
keys=['N096','N100','N105']
if s.get('current'):
 q=s['current'];s['done'][q['question_id']]=dict(status='INTERRUPTED_FOR_SETUP_CORRECTION',reason='Owner-authorized controller setup verification detected separate plan binding defects')
 if q['source_key'] not in keys:keys.append(q['source_key'])
 s['current']=None
qs=[]
for key in keys:
 q=learning.question(key,'gpu','verified_binding_correction',alternate=key=='N096',reason='New precommit after exact qualification of retained-port binding and missing archive plan-hash normalization')
 qs.append(q);s['seen'].append(q['question_id']);s['blocked_sources'].pop(key+'|gpu',None)
s['calibration']=qs+s['calibration'];s['status']='RESTART_AFTER_VERIFIED_BINDING_CORRECTION'
save(P/'STATE.json',s)
r=dict(timestamp=time.time(),state_before_sha256=old_hash,code_sha256=sha(P/'execution.py'),qualification='BINDING_CHECK PASS',completed_observations_preserved=len(s['observations']),failed_attempts_preserved=True,deadline_preserved=s['deadline'],new_questions=[q['question_id'] for q in qs],test_observations_imported=0)
save(P/'BINDING_RESTART.json',r);append(P/'QUESTION_LEDGER.jsonl',dict(event='VERIFIED_SETUP_CORRECTION',**r))
