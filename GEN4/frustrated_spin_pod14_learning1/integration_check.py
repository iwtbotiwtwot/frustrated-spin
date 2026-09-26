"""Bounded qualification-only dynamic-owner and policy checks; no training import."""
from execution import *
import learning,fcntl,collections

def main():
    lock=Path('/opt/gen4/restore14/research-pool.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert plan_identity(load(P/'N96_SPEC.json')['plan'])==load(P/'POD_QUALIFICATION.json')['plan_hash']
    root=P/'dynamic_owner_check';root.mkdir(exist_ok=True)
    rows=[];owners=[]
    with DomainSession.start('MATTER_SEARCH',objective='Verify dynamic sources on persistent cooperative14 owners before production learning',output_root=root/'sessions',receipt_storage='gzip') as session:
        prod=Production(session.consumer,root/'engine');session.consumer=Adapter(session.consumer,prod)
        for key in ['N072','N084']:
            q=learning.question(key,'gpu','qualification_only');q.update(question_id='integration_'+key,repeats=1,deadline=time.time()+300)
            r=session.execute('GEN4_POD14_RESEARCH',dict(question=q,code_sha256=sha(P/'execution.py')),purpose='Verify two source-bound solves share the same fourteen persistent owners')
            rows.extend(r['observations']);owners.append(r['observations'][-1]['worker_pids'])
        assert owners[0]==owners[1]
        session.execute('GEN3_CHECKPOINT',{},purpose='Retain integration evidence outside production training state')
    state=dict(observations=[],completed={},seen=[],candidates=[],steps=0,models={},residuals=[],low_information={},blocked_sources={},non_gpu_streak=0,calibration=[])
    qs=learning.initialize();learning.add_candidates(state,qs*3);assert len(state['candidates'])==len(qs)
    active=learning.frontier(state);assert active and max(collections.Counter(q['narrow_family'] for q in active).values())*5<=len(active)
    children=learning.follow(state,qs[0],{},error='test capacity');assert len(children)==1 and children[0]['kind']=='diagnostic';assert not learning.follow(state,children[0],{},error='bounded failure')
    models,excluded,residuals=learning.fit_models(rows);assert any(x['reason']=='COLD_OR_INITIAL_LOADING_MEASUREMENT' for x in excluded)
    assert all(m['backend']=='COOP14_MIG_BRANCH_GROUP' for m in models.values())
    save(P/'INTEGRATION_CHECK.json',dict(status='PASS',same_14_owners_across_sources=True,worker_pids=owners,observations=rows,not_imported_into_training=True,policy_checks=['fingerprint deduplication','20 percent family limit','one capacity followup','cold excluded','backend identity retained']))
    print('DYNAMIC OWNER AND POLICY CHECK PASS',flush=True)
if __name__=='__main__':main()
