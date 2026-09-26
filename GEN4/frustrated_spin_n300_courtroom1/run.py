"""Frozen prospective N300 timing, exact reference, and wrong-control execution."""
import os,time,gzip,copy,datetime,statistics,platform,traceback,csv,resource
from packet import *
from refine import collapse
from SAM_PROJECT.session import DomainSession

def event(kind,**kw):
    path=P/'EVENTS.jsonl';previous=load(P/'EVENT_HEAD.json')['hash'] if (P/'EVENT_HEAD.json').exists() else None
    r=dict(event=kind,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic_ns=time.monotonic_ns(),previous_hash=previous,**kw);r['hash']=digest(r)
    with path.open('a') as f:f.write(json.dumps(r,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    save(P/'EVENT_HEAD.json',dict(hash=r['hash']))

def frozen():
    seal=load(P/'PRECOMMIT_SEAL.json');assert sha(P/'FROZEN_MANIFEST.json')==seal['manifest_sha256']
    for name,h in load(P/'FROZEN_MANIFEST.json').items():assert sha(P/name)==h,name
    assert load(P/'WITNESS.json')['precommit_archive_sha256']==sha(P/'PRECOMMIT.tar.gz')

def tables():
    assert sha(P/'inputs/PACKET_TABLES.json.gz')==load(P/'inputs/PACKET_TABLES_MANIFEST.json')['sha256']
    raw=json.load(gzip.open(P/'inputs/PACKET_TABLES.json.gz','rt'))
    return {key:{tuple(r['state']):fmpz_poly([int(v) for v in r['coefficients']]) for r in rows} for key,rows in raw.items()}

def gz(name,value):
    path=P/'artifacts'/name;path.parent.mkdir(exist_ok=True)
    with gzip.open(path,'wt') as f:json.dump(value,f)
    return dict(path=str(path.relative_to(P)),sha256=sha(path))

def expect_reject(action,reason):
    try:action()
    except (AssertionError,ArithmeticError,ValueError) as e:return dict(rejected=True,exception=type(e).__name__,message=str(e),reason=reason)
    raise AssertionError('Wrong control accepted: '+reason)

class Trial:
    def __init__(self,base):self.base=base;self.cache=tables();self.cases={f:load(P/'sources'/f'{f}_N300.json') for f in ['packet','signed_packet','signed_packet_chain']};self.plans={};self.answers={};self.references={};self.rows=[]
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_N300_QUALIFY':
            checks=[]
            old=P.parent/'frustrated_spin_packet_catalog1'
            for family in self.cases:
                c=load(P/'inputs'/f'{family}_N120.json');pl=compile_source(c);a=packet_solve(c,pl,self.cache)['answer'];ref=json.load(gzip.open(old/'results'/f'{family}_N120.json.gz','rt'))['answers']['variable_elimination'];checks.append(dict(family=family,verification=compare(a,ref)))
            return dict(status='PASS',checks=checks)
        if op=='GEN4_N300_WARM':
            prepare=time.perf_counter()
            for family,c in self.cases.items():
                self.plans[family]=compile_source(c);assert all(p['key'] in self.cache for p in self.plans[family]['pieces']),'All local tables must preexist target execution'
            prep=time.perf_counter()-prepare;families=list(self.cases)
            event('FIRST_N300_SOLVE_ABOUT_TO_EXECUTE',source=self.cases[families[0]]['source']['source_sha256'],preparation_seconds=prep)
            for repeat in range(31):
                order=families[repeat%3:]+families[:repeat%3]
                for family in order:
                    c=self.cases[family];start=time.perf_counter_ns();r=packet_solve(c,self.plans[family],self.cache);duration=time.perf_counter_ns()-start
                    assert r['execution']['cache_misses']==0
                    t=time.perf_counter_ns();a=r['answer']
                    if family not in self.answers:self.answers[family]=a
                    vh=compare(a,self.answers[family]);verification=time.perf_counter_ns()-t
                    row=dict(family=family,repeat=repeat,method='PACKET_WARM',duration_ns=duration,comparison_ns=verification,verification_hash=vh,answer_hash=a['spectrum_sha256'],execution=r['execution']);self.rows.append(row)
                    event('TIMED_SOLVE',family=family,repeat=repeat,duration_ns=duration,answer_hash=a['spectrum_sha256'])
            return dict(status='EXECUTED_REFERENCE_PENDING',source_hashes={f:c['source']['source_sha256'] for f,c in self.cases.items()},plan_hashes={f:digest(p) for f,p in self.plans.items()},rows=self.rows,preparation_seconds=prep,full_answers={f:gz(f+'_WARM.json.gz',a) for f,a in self.answers.items()})
        if op=='GEN4_N300_REFERENCES':
            out={}
            for family,c in self.cases.items():
                start=time.perf_counter_ns();r=exact.solve_cpu(c['source'],c['ports'],dict(method='variable_elimination',max_seconds=120,max_factor_work=10000000));duration=time.perf_counter_ns()-start;self.references[family]=r['answer'];vh=compare(self.answers[family],r['answer'])
                a=r['answer'];B=c['source']['energy_bound_B'];opens=[[[ (int(e)+B)//2,count] for e,count in row['dos']] for row in a['port_rows']]
                assert all([[2*y-B,count] for y,count in row]==a['port_rows'][i]['dos'] for i,row in enumerate(opens))
                out[family]=dict(duration_ns=duration,verification_hash=vh,reference=gz(family+'_INDEPENDENT_VE.json.gz',r),open_operator=gz(family+'_OPEN_OPERATOR.json.gz',dict(ports=c['ports'],glue=[],local_bound=B,rows=opens)),verified_all_warm_trials=all(x['verification_hash']==vh for x in self.rows if x['family']==family))
                assert out[family]['verified_all_warm_trials']
            return dict(status='EXACT',references=out)
        if op=='GEN4_N300_SECONDARY':
            rows=[]
            for family,c in self.cases.items():
                for repeat in range(5):
                    start=time.perf_counter_ns();r=packet_solve(c,self.plans[family],{});duration=time.perf_counter_ns()-start;vh=compare(r['answer'],self.references[family]);rows.append(dict(family=family,method='PACKET_EMPTY_CACHE',repeat=repeat,duration_ns=duration,verification_hash=vh,execution=r['execution']))
            c=self.cases['signed_packet_chain']
            for repeat in range(11):
                start=time.perf_counter_ns();r=collapse(c,self.plans['signed_packet_chain'],self.cache);duration=time.perf_counter_ns()-start;vh=compare(r['answer'],self.references['signed_packet_chain']);rows.append(dict(family='signed_packet_chain',method='BOUNDARY_REFINEMENT_SECONDARY',repeat=repeat,duration_ns=duration,verification_hash=vh,execution=r['execution']))
            return dict(status='EXACT',rows=rows)
        if op=='GEN4_N300_WRONG_CONTROLS':
            out={};c=self.cases['signed_packet'];wrong=copy.deepcopy(c);wrong['source']['edges'][0][2]*=-1;wrong['source']=norm(300,wrong['source']['edges'],wrong['source']['fields'],'WRONG_BINDING')
            out['stale_plan']=expect_reject(lambda:packet_solve(wrong,self.plans['signed_packet'],self.cache),'changed source with stale plan');out['stale_plan']['artifact']=gz('CONTROL_STALE_PLAN.json.gz',wrong)
            wrong=copy.deepcopy(c);wrong['source']['edges'].append([c['blocks'][0][0],c['blocks'][1][0],1]);wrong['source']=norm(300,wrong['source']['edges'],wrong['source']['fields'],'UNDECLARED_INTERACTION')
            out['unaccounted_edge']=expect_reject(lambda:compile_source(wrong),'missing interface edge');out['unaccounted_edge']['artifact']=gz('CONTROL_EXTRA_EDGE.json.gz',wrong)
            forged=dict(self.cache)
            for signed,positive in zip(self.plans['signed_packet']['pieces'],self.plans['packet']['pieces']):forged[signed['key']]=self.cache[positive['key']]
            bad=packet_solve(c,self.plans['signed_packet'],forged)['answer'];out['wrong_cache']=expect_reject(lambda:compare(bad,self.references['signed_packet']),'positive coefficients under signed cache key');out['wrong_cache'].update(count_and_moment_checks_passed=True,artifact=gz('CONTROL_WRONG_CACHE.json.gz',bad))
            a=self.references['signed_packet'];hist={i:{int(e):int(v) for e,v in row['dos']} for i,row in enumerate(a['port_rows'])};found=None
            for mask,row in hist.items():
                energies=sorted(row)
                for i in range(len(energies)-3):
                    es=energies[i:i+4]
                    if es[1]-es[0]==es[2]-es[1]==es[3]-es[2] and min(row[e] for e in es)>=3:found=(mask,es);break
                if found:break
            assert found;mask,es=found
            for e,delta in zip(es,[1,-3,3,-1]):hist[mask][e]+=delta
            bad=exact.finalize_answer(c['source'],c['ports'],hist);assert bad['energy_moments']==a['energy_moments']
            out['moment_preserving_corruption']=expect_reject(lambda:compare(bad,a),'altered coefficients preserve first three moments');out['moment_preserving_corruption'].update(count_and_moment_checks_passed=True,energies=es,deltas=[1,-3,3,-1],artifact=gz('CONTROL_MOMENT_PRESERVING.json.gz',bad))
            hist={i:{int(e):int(v) for e,v in row['dos']} for i,row in enumerate(a['port_rows'])};i,j=next((i,j) for i in hist for j in hist if hist[i]!=hist[j]);hist[i],hist[j]=hist[j],hist[i];bad=exact.finalize_answer(c['source'],c['ports'],hist);assert bad['scalar_dos']==a['scalar_dos']
            out['wrong_port_order']=expect_reject(lambda:compare(bad,a),'exchanged conditional rows');out['wrong_port_order'].update(scalar_and_moments_unchanged=True,swapped=[i,j],artifact=gz('CONTROL_PORT_ROWS.json.gz',bad))
            field=copy.deepcopy(self.cases['signed_packet_chain']);field['source']['fields'][field['blocks'][-1][0]]=2;field['source']=norm(300,field['source']['edges'],field['source']['fields'],'FIELD_BREAKS_BOUNDARY_SYMMETRY');pl=compile_source(field);cache={};plain=packet_solve(field,pl,cache);reduced=collapse(field,pl,cache);assert reduced['execution']['reduction']=='NOT_ADMITTED_BOUNDARY_SPECTRA_DIFFER';ref=exact.solve_cpu(field['source'],field['ports'],dict(method='variable_elimination',max_seconds=120));vh=compare(reduced['answer'],ref['answer']);compare(plain['answer'],ref['answer'])
            out['invalid_symmetry_shortcut']=dict(rejected=True,fallback_verified=True,verification_hash=vh,artifact=gz('CONTROL_FIELD_SYMMETRY.json.gz',dict(source=field,answer=reduced['answer'],execution=reduced['execution'],independent_reference=ref)))
            return dict(status='PASS',controls=out)
        return self.base.execute(op,payload)

def main():
    frozen();assert not (P/'RESULTS.json').exists(),'Scored run cannot be silently repeated'
    assert not (P/'EVENTS.jsonl').exists(),'Any retry requires a separate sealed attempt'
    assert os.environ.get('SAM_R3_RUN_ID'),'Use existing resource manager'
    runtime=dict(pid=os.getpid(),hostname=platform.node(),affinity=sorted(os.sched_getaffinity(0)),cgroup=Path('/proc/self/cgroup').read_text(),resource_budget=load(os.environ['SAM_R3_BUDGET']),clock=dict(implementation=time.get_clock_info('perf_counter').implementation,resolution=time.get_clock_info('perf_counter').resolution),thread_environment={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']})
    save(P/'EXECUTION_ENVIRONMENT.json',runtime);event('SEALED_RUN_START',seal=load(P/'PRECOMMIT_SEAL.json'),witness=load(P/'WITNESS.json'))
    save(P/'STATUS.json',dict(status='RUNNING',pid=os.getpid(),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    results={}
    try:
        with DomainSession.start('MATTER_SEARCH',objective='Precommitted workstation N300 exact packet computation below 25ms with wrong controls',output_root=P/'sessions',receipt_storage='gzip') as session:
            print(session.announcement(),flush=True);save(P/'SESSION.json',dict(path=str(session.directory),announcement=session.announcement()));session.consumer=Trial(session.consumer)
            for phase,op in [('qualification','GEN4_N300_QUALIFY'),('warm','GEN4_N300_WARM'),('references','GEN4_N300_REFERENCES'),('secondary','GEN4_N300_SECONDARY'),('wrong_controls','GEN4_N300_WRONG_CONTROLS')]:
                event('PHASE_START',phase=phase);t=time.perf_counter();r=session.execute(op,dict(seal_sha256=sha(P/'PRECOMMIT_SEAL.json'),source_manifest=load(P/'PRECOMMIT.json')['sources']),purpose='Frozen protocol phase '+phase);results[phase]=r;save(P/(phase.upper()+'.json'),r);event('PHASE_COMPLETE',phase=phase,wall_seconds=time.perf_counter()-t,artifact_sha256=sha(P/(phase.upper()+'.json')));print('COMPLETE',phase,flush=True)
            results['checkpoint']=session.execute('GEN3_CHECKPOINT',{},purpose='Preserve prospective N300 exact outputs, timings and wrong-control evidence')
        frozen();results['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;save(P/'RESULTS.json',results);event('COMPLETE',results_sha256=sha(P/'RESULTS.json'));save(P/'STATUS.json',dict(status='COMPLETE',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid()))
    except BaseException:
        save(P/'FAILURE.json',dict(error=traceback.format_exc()));event('FAILED',error=traceback.format_exc());save(P/'STATUS.json',dict(status='FAILED',pid=os.getpid()));raise

if __name__=='__main__':main()
