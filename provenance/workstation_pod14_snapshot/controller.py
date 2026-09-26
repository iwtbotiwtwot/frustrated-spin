"""One local eight-hour controller, one executor, one cooperative GPU team."""
import os,sys,time,signal,subprocess,fcntl,json,traceback,tarfile,shutil,datetime,statistics,collections,argparse
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from source_ops import load,save,sha,digest,append,writecsv,canonical,exact
import learning
stop=False;executor=None
def stopped(*args):
    global stop
    stop=True
signal.signal(signal.SIGTERM,stopped);signal.signal(signal.SIGINT,stopped)
def stamp(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()

def verify_rule(q,v):
    """Independent controller-side verification; no certificate reuse as a label."""
    c=load(P/'sources'/f'{q["source_key"]}.json');s=c['source']
    if v['rule']=='SOURCE_BOUND_COMPONENT_PARTITION':
        groups=v['groups'];seen=[x for g in groups for x in g];assert sorted(seen)==list(range(s['N']));labels={x:i for i,g in enumerate(groups) for x in g}
        assert all(labels[u]==labels[w] for u,w,j in s['edges'])
        assert v['supporting_canonical_cases'] and v['counterexample_search'] if len(groups)>1 else True
    elif v['rule']=='EXPLICIT_GAUGE_BIJECTION':
        t=load(P/'sources'/f'{v["variant_key"]}.json')['source'];g=v['certificate']['signs'];assert len(g)==s['N'] and all(x in [-1,1] for x in g)
        assert [h*g[i] for i,h in enumerate(t['fields'])]==s['fields']
        assert sorted([[u,w,j*g[u]*g[w]] for u,w,j in t['edges']])==sorted(s['edges'])
        assert all(g[x]==1 for x in v['certificate']['ports_fixed'])
    else:raise ValueError('Unimplemented independent verifier')
    return v|dict(status='CERTIFIED_EXACT_RULE',question_id=q['question_id'],independent_verifier='controller.verify_rule',installed_globally=False)

def reports(s):
    models,excluded,residuals=learning.fit_models(s['observations']);s['models']=models;s['residuals']=residuals
    cpu={k:v for k,v in models.items() if v['backend']=='LOCAL_FLINT_CPU'};gpu={k:v for k,v in models.items() if v['backend']=='COOP14_MIG_BRANCH_GROUP'}
    save(P/'CPU_COST_MODEL.json',dict(models=cpu,training_origin='Fresh campaign only',exclusions=excluded))
    save(P/'COOP14_COST_MODEL.json',dict(models=gpu,training_origin='Fresh qualified cooperative14 only',exclusions=excluded))
    flat=[]
    for o in s['observations']:
        row={k:v for k,v in o.items() if k not in ['features','timings','exact_verification']};row.update(o['timings']);row.update(verification_hash=o['exact_verification']['verification_hash'],PRE_features=o['features']);flat.append(row)
    clean=[r for r in flat if r.get('warm_training_eligible') and r['cost_context']=='COMPLETE']
    for name,rs in [('CLEAN_OBSERVATIONS.csv',clean),('CPU_METHOD_SCORECARD.csv',[r for r in flat if r['backend_id']=='LOCAL_FLINT_CPU']),('COOP14_GPU_SCORECARD.csv',[r for r in flat if r['backend_id']=='COOP14_MIG_BRANCH_GROUP'])]:
        if rs:writecsv(P/name,rs)
        elif not (P/name).exists():(P/name).write_text('question_id,source_hash,backend_id,cache_state,timing_scope\n')
    bysource=collections.defaultdict(lambda:collections.defaultdict(list))
    for o in s['observations']:
        if o.get('warm_training_eligible'):bysource[o['source_hash']][o['backend_id']].append(o)
    selectors=[]
    for src,b in bysource.items():
        if len(b)<2:continue
        costs={};states={}
        for backend,rs in b.items():
            by=collections.defaultdict(list)
            for o in rs:
                if o['cache_state']=='CACHE_REUSE':continue
                by[(o['method'],o['plan_hash'],o['cache_state'])].append(o['timings']['end_to_end_solve_seconds'])
            if by:
                key=min(by,key=lambda k:statistics.median(by[k]));costs[backend]=statistics.median(by[key]);states[backend]=dict(method=key[0],plan_hash=key[1],cache_state=key[2])
        if len(costs)==2:selectors.append(dict(source_hash=src,source_key=next(iter(b.values()))[0]['source_key'],preferred_backend=min(costs,key=costs.get),warm_end_to_end_seconds=costs,execution_context=states,status='REPEATED_EMPIRICAL_RULE',scope='Matched source and ordered observable; native route includes internal checks; startup and external verification excluded; cache reuse alternatives separately recorded'))
    save(P/'HARDWARE_SELECTOR.json',dict(status='LEARNED_HEURISTIC',source_bound_decisions=selectors,rule='Do not select hardware from N; compare admitted exact routes with source/port/backend/cache identity',undefined_sources='No forced placement',cold_start='Separately measured; not pooled with warm labels'))
    active=learning.frontier(s) if not s['calibration'] else []
    save(P/'FRONTIER.json',dict(calibration_remaining=s['calibration'],active_frontier=active,candidate_count=len(s['candidates']),candidate_catalog=s['candidates'],active_limit=25,candidate_limit=40,narrow_family_max_fraction=.2,formula='(uncertainty/novelty information + underrepresented-family bonus)/sqrt(expected seconds) + bounded waiting age',no_gpu_starvation='at most two CPU/analysis choices while GPU work is admissible',closed_or_deprioritized=[k for k,v in s['low_information'].items() if v>=3],one_followup_per_capacity_failure=True))
    save(P/'PREDICTIONS_121_144.json',[dict(N=n,status='SOURCE_UNDEFINED',executed=False,source_family=None,preferred_method=None,width=None,runtime_interval=None,reason='An actual future source family/graph has not been specified for this campaign') for n in range(121,145)])
    (P/'N100_N105_HARDWARE_PLACEMENT.md').write_text('# Packet hardware placement\n\nPacket and connected-prefix identities remain separate. Fresh matched decisions:\n\n```json\n'+json.dumps(selectors,indent=2)+'\n```\n\nCPU cache reuse is reported separately from fresh recomputation. All saved rows retain timing scopes and verification identity.\n')
    n96=[{k:o[k] for k in ['method','plan_hash','weighted_entries','retained_width','branch_count','cache_state','timings']} for o in s['observations'] if o['source_key']=='N096']
    (P/'N96_PLAN_BACKEND.md').write_text('# N96 plan/backend research\n\nQualification is separate from training. The expanded plan has16 branches,width21,203956800 weighted entries; older fresh plan has32,width22,641754752. Fresh observations:\n\n```json\n'+json.dumps(n96,indent=2)+'\n```\n')
    nexts=[q['question']+' Source '+q['source_key'] for q in (s['calibration']+active)[:5]]
    fallback=['Which PRE factor shapes best explain remaining runtime residuals?','When does exact CPU elimination beat cooperative14 after matching cache and observable?','Can source-bound reductions transfer across a new legal same-N intervention?','Which separator boundary merits one targeted exact comparison?','Which explicit future source family should define the untouched N121–144 test?']
    nexts=(nexts+fallback)[:5]
    cert=lines(P/'CERTIFICATES.jsonl');fail=lines(P/'COUNTEREXAMPLES.jsonl')
    answers=[
      'Qualified original Focus/Frontier engines; accepted GPU measurements require14 live owners and positive contribution from every owner. '+str(sum(o['backend_id']=='COOP14_MIG_BRANCH_GROUP' for o in s['observations']))+' GPU observations retained. Topology/cohort PIDs are in each row.',
      'Historical single-MIG timings imported:0. Cold/initial loading and incomplete context excluded from normal cost fitting: '+str(len(excluded))+'. See backend model exclusion records.',
      'CPU models use PRE factor work, conditioned by method,cache and CPU topology. Current fitted groups: '+str(len(cpu))+'. Coefficients and source-grouped errors are in CPU_COST_MODEL.json.',
      'GPU models use PRE weighted factor entries × roots × primes, conditioned by plan/backend/cache/readout. Groups: '+str(len(gpu))+'. No N-only selector.',
      json.dumps(selectors) if selectors else 'Matched CPU/GPU placement calibration is pending; no result inferred from old topology timings.',
      'N96 targets branches,width,weighted entries,root/prime load and factor map preparation; warm comparison observations are in N96_PLAN_BACKEND.md.',
      json.dumps(residuals[:8]) if residuals else 'Too few completed clean measurements for a residual ranking.',
      str(len(cert))+' independently verified project-local certificates; precise statements, support and counterexample searches are in CERTIFICATES.jsonl. No global installation.',
      str(len(fail))+' failure/counterexample records retained. Capacity or implementation errors are typed separately from an exact precondition counterexample.',
      'Calibration cannot be displaced by descendants. Adaptive active frontier<=25,candidate pool<=40,each narrow family<=20%;three low-information siblings close/deprioritize a family; at most one capacity diagnostic. Current theme counts: '+json.dumps(s['theme_counts']),
      '\n'.join('- '+q for q in nexts),
      'N121–144 unexecuted; SOURCE_UNDEFINED entries contain no invented numerical predictions. Canonical files checked against the initial manifest at shutdown.'
    ]
    titles=['Did the pod remain in qualified topology?','Which measurements were excluded?','What predicts CPU cost?','What predicts cooperative-GPU cost?','When should GEN4 choose CPU?','Which features predict the N96 gain?','Which residuals remain unexplained?','Exact reusable rules?','Which rules or attempts failed?','Did the generator maintain diversity?','Five highest-value next questions','What remains untouched?']
    text='# Cooperative14 research summary\n\nOwner: Sean Brady, originator and conceptual director.\n\nStatus: '+s['status']+'; new completed questions: '+str(len(s['completed']))+'; new observations: '+str(len(s['observations']))+'.\n\n'
    for i,(t,a) in enumerate(zip(titles,answers),1):text+=f'## {i}. {t}\n\n{a}\n\n'
    (P/'OVERNIGHT_SUMMARY.md').write_text(text)

def lines(p):return [json.loads(x) for x in p.read_text().splitlines() if x] if p.exists() else []

def main():
    global executor
    ap=argparse.ArgumentParser();ap.add_argument('--hours',type=float,default=8);ap.add_argument('--smoke',action='store_true');ap.add_argument('--resume-check',action='store_true');args=ap.parse_args()
    lock=(P/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);pool=Path('/opt/gen4/restore14/research-pool.lock').open('a');fcntl.flock(pool,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert load(P/'POD_QUALIFICATION.json')['status']=='PASS'
    sf=P/('SMOKE_STATE.json' if args.smoke else 'STATE.json')
    if args.resume_check:
        old=load(P/'SMOKE_STATE.json');assert len(old['completed'])==1;assert (P/'experiments'/next(iter(old['completed']))/'RESULT.json').exists()
        save(P/'RECOVERY_CHECK.json',dict(status='PASS',completed_ids=list(old['completed']),new_executions=0,precommit_unchanged=True));return
    if sf.exists():s=load(sf)
    else:
        now=time.time();cal=learning.initialize() if not args.smoke else [learning.question('N012','cpu','production_smoke',['components','variable_elimination'])]
        s=dict(started=now,deadline=now+args.hours*3600,status='STARTING',done={},completed={},observations=[],models={},residuals=[],calibration=cal,candidates=[],seen=[q['question_id'] for q in cal],steps=0,theme_counts={},low_information={},blocked_sources={},non_gpu_streak=0,current=None,imported_observations=0,imported_models=0,imported_queue=0)
    for f in ['QUESTION_LEDGER.jsonl','STRUCTURAL_DISCOVERIES.jsonl','RULE_CANDIDATES.jsonl','COUNTEREXAMPLES.jsonl','CERTIFICATES.jsonl']:(P/f).touch(exist_ok=True)
    if s.get('current'):
        q=s['current'];s['done'][q['question_id']]=dict(status='INTERRUPTED',reason='Restart preserves precommit, no silent repeat');learning.add_candidates(s,learning.follow(s,q,{},error='Interrupted exact experiment'));s['current']=None
    durable=Path(os.environ.get('POD14_DURABLE','/workspace/gen4/runs/frustrated-spin-pod14-learning1'));durable.mkdir(parents=True,exist_ok=True)
    custody={}
    def checkpoint(status):
        s.update(status=status,updated=time.time());save(sf,s)
        statusfile=P/('SMOKE_STATUS.json' if args.smoke else 'STATUS.json')
        live=load(P/'EXECUTOR_LIVE.json') if (P/'EXECUTOR_LIVE.json').exists() else {}
        save(statusfile,dict(status=status,pid=os.getpid(),executor_pid=executor.pid if executor and executor.poll() is None else None,worker_pids=live.get('worker_pids',[]),start_utc=stamp(s['started']),deadline_utc=stamp(s['deadline']),completed=len(s['completed']),observations=len(s['observations']),remaining_calibration=len(s['calibration']),candidate_count=len(s['candidates']),active_question=s['current'],topology='COOP14_MIG_BRANCH_GROUP',gpu_workers=14,cooperative_experiment_slots=1,cpu_role='shared preparation,readout,reconstruction,verification and separately labeled serial exact CPU methods',stop_command=f'kill -TERM {os.getpid()}',hosted_calls=0,imported_observations=0,imported_models=0,session=load(P/'EXECUTOR_READY.json').get('session') if (P/'EXECUTOR_READY.json').exists() else None))
        files=sorted(f for f in P.iterdir() if f.is_file() and f.suffix in ['.py','.json','.jsonl','.csv','.md'])
        (P/'HASHES.txt').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in files))
    def sync():
        # One bounded compact snapshot; no repeated walk of all completed experiment trees.
        target=P/'checkpoint.part'
        with tarfile.open(target,'w:gz',compresslevel=1) as t:
            for f in P.iterdir():
                if f.is_file() and f.suffix in ['.json','.jsonl','.csv','.md','.py','.txt']:t.add(f,arcname=f.name)
            if s['current']:
                for f in (P/'service/engine').glob('RESIDUES*.npz'):t.add(f,arcname='partial/'+f.name)
        target.replace(P/'checkpoint.tar.gz')
        try:
            subprocess.run(['timeout','30','cp',str(P/'checkpoint.tar.gz'),str(durable/'checkpoint.new.tar.gz')],check=True);(durable/'checkpoint.new.tar.gz').replace(durable/'checkpoint.tar.gz')
            for name in ['STATUS.json','OVERNIGHT_SUMMARY.md','POD_QUALIFICATION.json']:
                if (P/name).exists():shutil.copyfile(P/name,durable/name)
            # Incremental native-session custody: unchanged receipts are never recopied.
            for f in (P/'service/sessions').rglob('*'):
                if not f.is_file():continue
                info=(f.stat().st_size,f.stat().st_mtime_ns)
                if custody.get(str(f))==info:continue
                dst=durable/'native_sessions'/f.relative_to(P/'service/sessions');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst);custody[str(f)]=info
        except Exception as e:append(P/'SYNC_ERRORS.jsonl',dict(time=time.time(),error=str(e)))
    log=(P/'EXECUTOR.log').open('a');(P/'EXECUTOR_READY.json').unlink(missing_ok=True);(P/'RESPONSE.json').unlink(missing_ok=True);(P/'REQUEST.json').unlink(missing_ok=True)
    executor=subprocess.Popen([sys.executable,str(P/'runner.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    last=0;reports(s);checkpoint('STARTING')
    try:
        startup=time.time()
        while not (P/'EXECUTOR_READY.json').exists():
            if executor.poll() is not None:raise RuntimeError('Executor startup failed; inspect EXECUTOR.log')
            if time.time()-startup>90:raise TimeoutError('executor startup')
            time.sleep(.3)
        checkpoint('RUNNING')
        while not stop and not (P/'STOP').exists() and time.time()<s['deadline']-30:
            if args.smoke and s['completed']:checkpoint('SMOKE_COMPLETE');break
            q=learning.choose(s)
            if q is None:checkpoint('NO_DIVERSE_ADMISSIBLE_QUESTION');break
            if q['question_id'] in s['done']:continue
            from execution import resource_snapshot,gpu_inventory
            gate=resource_snapshot()
            if q['kind']=='gpu':gate['GPU_inventory']=gpu_inventory();assert gate['GPU_inventory']['mig_uuids']==load(P/'POD_QUALIFICATION.json')['GPU_inventory']['mig_uuids']
            if not gate['admitted']:s['candidates'].append(q);checkpoint('RESOURCE_GATE');break
            remaining=s['deadline']-time.time()-30
            if remaining<q['predicted_seconds']*1.1:
                append(P/'QUESTION_LEDGER.jsonl',dict(event='DEADLINE_ADMISSION_REJECTED',question_id=q['question_id'],remaining=remaining));continue
            out=P/'experiments'/q['question_id'];out.mkdir(parents=True,exist_ok=True);assert not (out/'PRECOMMIT.json').exists(),'Immutable precommit would be overwritten'
            q.update(timestamp=stamp(time.time()),deadline=min(s['deadline']-20,time.time()+q['maximum_seconds']),resource_gate=gate,code_hash=sha(P/'execution.py'),runtime_package_hash=load(P/'RUNTIME_IDENTITY.json')['runtime_package_hash'])
            save(out/'PRECOMMIT.json',q);append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',**q));s['current']=q;checkpoint('RUNNING');save(P/'REQUEST.json',q)
            last_resource_check=0
            while not (P/'RESPONSE.json').exists():
                if executor.poll() is not None:raise RuntimeError('Executor exited before result')
                if stop or (P/'STOP').exists() or time.time()>q['deadline']:
                    os.killpg(executor.pid,signal.SIGTERM)
                    try:executor.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(executor.pid,signal.SIGKILL);executor.wait()
                    raise InterruptedError('Owner stop or exact experiment/deadline gate')
                if time.time()-last_resource_check>10:
                    cg=Path('/sys/fs/cgroup');used=int((cg/'memory.current').read_text());maximum=int((cg/'memory.max').read_text())
                    if used>maximum-8*1024**3 or shutil.disk_usage(P).free<8*1024**3:raise InterruptedError('Live exact memory/disk reserve gate')
                    last_resource_check=time.time()
                if time.time()-last>300:checkpoint('RUNNING');sync();last=time.time()
                time.sleep(.5)
            resp=load(P/'RESPONSE.json');(P/'RESPONSE.json').unlink();assert resp['question_id']==q['question_id'];r=load(resp['result']);v=r.get('value',{});err=r.get('error')
            if r['status']=='COMPLETE':
                if v.get('independent_verifier_required'):
                    cert=verify_rule(q,v);append(P/'CERTIFICATES.jsonl',cert)
                    for ce in v.get('counterexample_search',[]) if isinstance(v.get('counterexample_search'),list) else []:append(P/'COUNTEREXAMPLES.jsonl',dict(question_id=q['question_id'],kind='EXACT_PRECONDITION_COUNTEREXAMPLE',**ce))
                s['completed'][q['question_id']]=dict(question=q,result=str(out/'RESULT.json'))
                s['observations'].extend(v.get('observations',[]))
                append(P/'STRUCTURAL_DISCOVERIES.jsonl',dict(question_id=q['question_id'],source_key=q['source_key'],kind=q['kind'],status=v['status'],plan_summaries=v.get('plan_summaries'),observations=len(v.get('observations',[]))))
                if q['kind'] in ['rule','variant']:append(P/'RULE_CANDIDATES.jsonl',dict(question_id=q['question_id'],**v))
            else:append(P/'COUNTEREXAMPLES.jsonl',dict(question_id=q['question_id'],kind='EXECUTION_OR_CAPACITY',error=err))
            children=learning.follow(s,q,v,error=err);learning.add_candidates(s,children)
            s['done'][q['question_id']]=dict(status=r['status'],children=[x['question_id'] for x in children],error=err);s['steps']+=1;s['theme_counts'][q['theme']]=s['theme_counts'].get(q['theme'],0)+1;s['non_gpu_streak']=0 if q['kind']=='gpu' else s['non_gpu_streak']+1
            append(P/'QUESTION_LEDGER.jsonl',dict(event='RESULT',question_id=q['question_id'],**s['done'][q['question_id']]));s['current']=None;reports(s);checkpoint('RUNNING')
            # Each exact result/precommit is mirrored once, without rescanning old results.
            dest=durable/'experiments'/q['question_id'];dest.mkdir(parents=True,exist_ok=True)
            for f in out.iterdir():
                if f.is_file() and f.suffix in ['.json','.gz']:shutil.copyfile(f,dest/f.name)
            if (P/'sources'/f'{q["source_key"]}.json').exists():
                (durable/'sources').mkdir(exist_ok=True);shutil.copyfile(P/'sources'/f'{q["source_key"]}.json',durable/'sources'/f'{q["source_key"]}.json')
            sync();last=time.time()
        if stop or (P/'STOP').exists():checkpoint('STOPPED')
        elif time.time()>=s['deadline']-30:checkpoint('DEADLINE')
    except InterruptedError as e:checkpoint('STOPPED' if stop or (P/'STOP').exists() else 'EXACT_RESOURCE_GATE');append(P/'QUESTION_LEDGER.jsonl',dict(event='INTERRUPTED',error=str(e),question=s['current']))
    except BaseException:
        s['controller_error']=traceback.format_exc();checkpoint('FAILED');raise
    finally:
        if executor and executor.poll() is None:
            os.killpg(executor.pid,signal.SIGTERM)
            try:executor.wait(timeout=15)
            except subprocess.TimeoutExpired:os.killpg(executor.pid,signal.SIGKILL);executor.wait()
        manifest=load(P/'ATLAS_MANIFEST.json');assert all(sha(P/'canonical'/f'{key}.json')==h for key,h in manifest['hashes'].items())
        reports(s);checkpoint(s['status']);sync();log.close()

if __name__=='__main__':main()
