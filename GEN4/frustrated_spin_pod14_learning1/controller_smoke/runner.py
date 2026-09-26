"""Qualification and one persistent, source-bound GEN4 execution service."""
import os,sys,time,signal,json,traceback,statistics,copy
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from execution import *
stopping=False
def stop(*args):
    global stopping
    stopping=True
    raise KeyboardInterrupt('OWNER_OR_DEADLINE_STOP')

def qualify():
    import fcntl
    lock=Path('/opt/gen4/restore14/research-pool.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ident=runtime_identity();save(P/'RUNTIME_IDENTITY.json',ident);inventory=gpu_inventory();resource=resource_snapshot();assert resource['admitted']
    prepare_sources();s=load(P/'N96_SPEC.json');p=s['plan'];assert p['selected']['method']=='expanded_portfolio'
    assert (p['selected']['branches'],p['selected']['width'],p['selected']['weighted_entries'])==(16,21,203956800)
    old=canonical(96)['plan'];assert old['selected']['branches']==32 and old['selected']['width']==22 and old['selected']['weighted_entries']==641754752
    save(P/'N96_OLD_PLAN.json',old)
    root=P/'qualification';root.mkdir(exist_ok=True);q=dict(kind='gpu',source_key='N096',question_id='qualification_n96',repeats=3,deadline=time.time()+600)
    out=P/'experiments'/q['question_id'];out.mkdir(parents=True,exist_ok=True)
    with DomainSession.start('MATTER_SEARCH',objective='Qualify original cooperative fourteen-worker production topology before clean learning',output_root=root/'sessions',receipt_storage='gzip') as session:
        print(json.dumps(session.announcement()),flush=True)
        prod=Production(session.consumer,root/'engine');session.consumer=Adapter(session.consumer,prod)
        r=session.execute('GEN4_POD14_RESEARCH',dict(question=q,code_sha256=sha(P/'execution.py')),purpose='One cold N96 followed by three warm exact repetitions using the frozen expanded production plan')
        session.execute('GEN3_CHECKPOINT',{},purpose='Retain cold/warm N96 qualification separately from training')
        rows=r['observations'];assert len(rows)==4 and rows[0]['cache_state']=='COLD'
        assert all(x['cache_state']=='WARM_SAME_SOURCE' for x in rows[1:])
        warm=statistics.median(x['timings']['end_to_end_solve_seconds'] for x in rows[1:]);assert warm<8.,f'GROSS_TIMING_INCONSISTENCY {warm}'
    # Exact original bounded branch-group / fifth-prime regressions.
    front=frontier_class();q30=load(front.HERE/'QUALIFICATION_N30.json');src=q30['source'];pl=copy.deepcopy(q30['plan']);pl['primes']=load(front.HERE/'PLAN.json')['primes'];fixed=list(range(4,9));st=front.structure(30,[e for e in src['edges'] if e not in pl['glue']],pl['ports'],fixed);pl['selected']=dict(**st,cutset=fixed,branches=32,weighted_entries=st['output_entries']*32,method='branch_group_scheduler_qualification');pl['mathematical_plan_sha256']=digest(pl)
    cache=IndexCache();ts=templates(src,pl);desc,maps,stats=cache.compile(ts[0]);ram=root/'n30';ram.mkdir(exist_ok=True)
    with DomainSession.start('MATTER_SEARCH',objective='Qualify N30 all-fourteen branch groups and fifth-prime exact reconstruction',output_root=ram/'sessions',receipt_storage='gzip') as session:
        a=front.Frontier(session.consumer,ram,[(src,pl,ts,desc,maps,stats)],cache,deadline=time.time()+300);a.durable=ram/'durable';a.durable.mkdir(exist_ok=True);session.consumer=a
        crt=session.execute('GEN4_N120_CRT_CHECK',dict(primes=pl['primes']),purpose='Exercise 16384 inverse-NTT/CRT coefficients and coefficient beyond four-prime capacity')
        rr=session.execute('GEN4_N120_CHUNKED_SOLVE',dict(case=0,source_sha256=src['source_sha256'],plan_sha256=pl['mathematical_plan_sha256']),purpose='Execute every branch/root/prime on the original shared work queue')
        assert rr['status']=='EXACT' and all(rr['execution']['tasks_per_gpu']) and len(a.workers)==14
        check,_=verify_answer(rr['answer'],q30['answer'],src,pl)
        n30=dict(execution=rr['execution'],verification=check,worker_pids=[w.pid for w in a.workers])
        cp=session.execute('GEN3_CHECKPOINT',{},purpose='Retain N30 and fifth-prime qualification')
    qualification=dict(status='PASS',qualified_utc=time.time(),GPU_inventory=inventory,resource_allocation=resource,runtime_identity=ident,source_hash=s['source']['source_sha256'],retained_plan_hash=p['mathematical_plan_sha256'],plan_hash=plan_identity(p),topology='COOP14_MIG_BRANCH_GROUP',worker_topology_id=ident['topology_id'],cold=rows[0],warm=rows[1:],warm_median_seconds=warm,N30=n30,fifth_prime_regression=crt,checkpoint=cp,training_observations_imported=0)
    save(P/'POD_QUALIFICATION.json',qualification);print(json.dumps(dict(qualification='PASS',warm_median=warm,worker_pids=rows[-1]['worker_pids'])),flush=True)

def serve():
    qual=load(P/'POD_QUALIFICATION.json');assert qual['status']=='PASS'
    current=runtime_identity();assert current['runtime_package_hash']==load(P/'RUNTIME_IDENTITY.json')['runtime_package_hash']
    actual=gpu_inventory();assert actual['mig_uuids']==qual['GPU_inventory']['mig_uuids']
    (P/'service').mkdir(exist_ok=True)
    with DomainSession.start('MATTER_SEARCH',objective='Fresh source-to-method-to-backend exact learning on the qualified cooperative14 pod',output_root=P/'service/sessions',receipt_storage='gzip') as session:
        prod=Production(session.consumer,P/'service/engine');session.consumer=Adapter(session.consumer,prod)
        save(P/'EXECUTOR_READY.json',dict(pid=os.getpid(),session=str(session.directory),announcement=session.announcement(),runtime_package_hash=current['runtime_package_hash'],started=time.time()))
        print(json.dumps(session.announcement()),flush=True)
        try:
            while not stopping:
                path=P/'REQUEST.json'
                if not path.exists():time.sleep(.2);continue
                q=load(path);path.unlink();out=P/'experiments'/q['question_id'];out.mkdir(parents=True,exist_ok=True)
                save(P/'EXECUTOR_LIVE.json',dict(pid=os.getpid(),question_id=q['question_id'],worker_pids=[w.pid for w in prod.adapter.workers] if prod.adapter else [],updated=time.time()))
                started=time.monotonic()
                try:
                    r=session.execute('GEN4_POD14_RESEARCH',dict(question=q,code_sha256=sha(P/'execution.py')),purpose=q['question'])
                    cp=session.execute('GEN3_CHECKPOINT',{},purpose='Retain exact result and measurement identities before next question')
                    result=dict(status='COMPLETE',value=r,checkpoint=cp,session=str(session.directory),operation_seconds=time.monotonic()-started)
                except Exception:
                    result=dict(status='FAILED',error=traceback.format_exc(),operation_seconds=time.monotonic()-started)
                    # A failed GPU command may leave an incomplete queue; rebuild only our cohort.
                    if q['kind']=='gpu':prod.close();prod.mode=None;prod.last=None
                save(out/'RESULT.json',result);save(P/'RESPONSE.json',dict(question_id=q['question_id'],result=str(out/'RESULT.json')))
        finally:prod.close()

if __name__=='__main__':
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    if '--qualify' in sys.argv:
        try:qualify()
        except BaseException:
            save(P/'QUALIFICATION_FAILURE.json',dict(error=traceback.format_exc()));raise
    else:serve()
