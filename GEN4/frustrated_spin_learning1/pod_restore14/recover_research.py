import sys,json,time,hashlib,tarfile,shutil
from pathlib import Path
R=Path('/opt/gen4-learning/GEN4/frustrated_spin_learning1');P=R/'podrun3';OLD=Path('/workspace/gen4/runs/frustrated-spin-learning-podrun2')
sys.path[:0]=[str(P),str(R),'/opt/gen4/current']
from operations import load,save,sha
import questions as ql
old=load(OLD/'STATE.json');save(P/'INHERITED_STATE.json',old)
queue=list(old['queue']);interrupted=old.get('inflight',[])
for q in interrupted:
 q=dict(q);q['parent_question']=q['question_id'];q['question_id']=ql.digest(dict(parent=q['parent_question'],configuration='RESTORED14'))[:24];q['question']='Resume interrupted research question under restored shared-team configuration: '+q['question'];queue.append(q)
needed={k:v for q in queue for k,v in q['inputs_hashes'].items() if not (R/k).exists() or sha(R/k)!=v}
for rel,h in list(needed.items()):
 if rel.startswith('podrun2/'):
  f=OLD/rel[len('podrun2/'):]
  if f.is_file() and sha(f)==h:
   target=R/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);del needed[rel]
if needed:
 archive=Path('/opt/gen4/restore14/packages/previous-inputs.tar.gz');shutil.copyfile(OLD/'INPUT_RUNTIME.tar.gz',archive)
 with tarfile.open(archive) as tar:
  for m in tar:
   rel=next((k for k in needed if m.isfile() and (m.name==k or m.name.endswith('/'+k))),None)
   if rel:
    data=tar.extractfile(m).read()
    if hashlib.sha256(data).hexdigest()==needed[rel]:
     target=R/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);del needed[rel]
   if not needed:break
admitted=[];deferred=[]
for q in queue:
 missing=[k for k,h in q['inputs_hashes'].items() if not (R/k).exists() or sha(R/k)!=h]
 (deferred if missing else admitted).append(dict(question=q,missing=missing) if missing else q)
s=dict(started=old['started'],deadline=old['deadline'],status='READY_AFTER_RESTORATION',queue=admitted,done=old['done'],completed={},seen_structure=old.get('seen_structure',{}),next_seed=old.get('next_seed',{}),generated=old['generated'],inherited_completed=len(old['completed']),inherited_checkpoint_sha256=sha(OLD/'STATE.json'),restored_at=time.time())
q=ql.qmake('gpu_test',96,why='Recalibrate source-plan cost and explain N96 work reduction using the restored fourteen-worker backend',priority=5000);q.update(repeats=3,restored_plan=load('/opt/gen4/restore14/N96_SPEC.json')['plan'],followup_plan=load(P/'N96_ALTERNATIVE_PLAN.json'));ql.enqueue(s,q)
for n in [84,97]:
 q=ql.qmake('gpu_test',n,why='Measure exact restored-backend cost on a retained source adjacent to the unexplained runtime transition',priority=100);q.update(repeats=2);ql.enqueue(s,q)
save(P/'STATE.json',s);save(P/'DEFERRED_INPUTS.json',deferred)
for name in ['QUESTION_LEDGER.jsonl','RULE_CANDIDATES.jsonl','CERTIFICATES.jsonl','STRUCTURAL_DISCOVERIES.jsonl','COUNTEREXAMPLES.jsonl']:(P/name).touch()
print(json.dumps(dict(pending=len(admitted),inherited=len(old['completed']),deferred=len(deferred),deadline=old['deadline'])))
# Isolated exact worker smoke, does not consume the research queue.
q=ql.qmake('gpu_test',12,why='Bounded restored-controller wiring qualification',priority=1);out=P/'qualification';out.mkdir(exist_ok=True);q.update(checkpoint_dir=str(out/'gpu_checkpoint'),repeats=1,maximum_admitted_seconds=120);save(out/'PRECOMMIT.json',q)
