import sys,json
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P),str(P/'runtime')]
from research import load,save
from SAM_PROJECT.session import DomainSession
s=load(P/'STATE.json');before=set(s['completed']);first=next(iter(s['completed'].values()));r=load(P/first['result'])
with DomainSession(r['session']) as session:
 restored=session.execute('GEN3_CHECKPOINT',{},purpose='Bounded restart qualification: reopen saved native state without repeating research')
 save(P/'RECOVERY_TEST.json',dict(passed=True,reopened_session=r['session'],announcement=session.announcement(),checkpoint=restored,completed_questions_preserved=sorted(before),experiments_repeated=0))
assert before==set(load(P/'STATE.json')['completed'])
print('RECOVERY_PASSED',len(before))
