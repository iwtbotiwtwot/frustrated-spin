"""Bounded exact catalog construction, independent route comparison and receipts."""
import os,sys,time,signal,json,gzip,csv,statistics,platform,subprocess,argparse,shutil,traceback
from pathlib import Path
from packet import *
from SAM_PROJECT.session import DomainSession
import resource_manager as rm
STOP=False
def stop(*args):
    global STOP
    STOP=True
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)

def budget():
    cpus=sorted(os.sched_getaffinity(0));r=rm.snapshot({'hosts':{'pod':dict(allowed_cpus=cpus,fraction_of_available=.9,worker_order=cpus,critical_path_preferred_cpus=cpus[:1],io_cpus=cpus[:1])}},'pod')
    cg=Path('/sys/fs/cgroup');limit=(cg/'memory.max').read_text().strip();used=int((cg/'memory.current').read_text());quota=(cg/'cpu.max').read_text().split()
    r['cpu_equivalents']=min(r['cpu_equivalents'],float(quota[0])/int(quota[1]) if quota[0]!='max' else len(cpus));r['effective_available_ram']=min(r['prelaunch_mem_available'],int(limit)-used if limit!='max' else r['prelaunch_mem_available'])
    assert r['effective_available_ram']>2*1024**3 and shutil.disk_usage(P).free>4*1024**3 and r['cpu_equivalents']>=1
    r.update(execution='one serial CPU coordinator, single-thread FLINT; no GPU workers',hostname=platform.node(),cpu_model=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),None));return r

def read_result(key,folder='results'):
    return json.load(gzip.open(P/folder/(key+'.json.gz'),'rt'))

def report(state):
    rows=[]
    for key in state['completed']:
        r=read_result(key);c=load(P/'sources'/f'{key}.json');row=dict(key=key,N=c['N'],family=c['family'],source_hash=c['source']['source_sha256'],components=len(exact.components(c['source'])),edges=len(c['source']['edges']),largest_packet=max(map(len,c['blocks'])),frustrated_triangles=len(c['frustrated_triangles']),output_hash=r['answers']['packet_warm']['spectrum_sha256'],plan_hash=r['plan_hash'],claim_type=c['claim_type'])
        for method in ['variable_elimination','packet_cold','packet_warm']:
            obs=[x for x in r['observations'] if x['method']==method and (method!='packet_warm' or x['cache_state']=='CACHE_REUSE')]
            row[method+'_median_ms']=1000*statistics.median(x['seconds'] for x in obs)
        rows.append(row)
    if rows:
        with (P/'CATALOG.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={}
    for family in ['packet','signed_packet','signed_packet_chain']:
        rr=[r for r in rows if r['family']==family]
        if rr:summary[family]=dict(completed=len(rr),warm_median_ms=statistics.median(r['packet_warm_median_ms'] for r in rr),warm_max_ms=max(r['packet_warm_median_ms'] for r in rr),warm_under_100ms=sum(r['packet_warm_median_ms']<100 for r in rr),connected=sum(r['components']==1 for r in rr))
    save(P/'SUMMARY.json',dict(status=state['status'],families=summary,completed=len(rows),training_resumed=False,holdouts_executed=False))
    lines=['# Packet-family extension across N1–120','','Owner: Sean Brady, originator and conceptual director.','','Status: '+state['status']+'. Training remains paused. All timings below were measured on the pod CPU in this campaign.','','## Construction and computation','','The N100 graph is exactly the induced first 100 vertices of N105. Both use zero fields and positive unit couplings. Their components are chains of K5 layers with perfect-matching interfaces. The N105 extension completes its three two-layer packets to three layers each, giving eight 15-spin packets at N120. The full N1–120 ladder is formed by explicit induced prefixes, preserving both anchors exactly.','','Two additional agent-designed families retain the packet vertices and internal topology: one negative edge per complete five-spin clique creates explicit frustrated triangles; a connected version links the packets through one gateway spin per packet, with signed bridges. These are separately named new sources. Existing canonical connected graphs and answers are unchanged.','','The compiler verifies every vertex and edge against its packet partition. It computes exact local port-conditioned polynomial spectra, caches them by full local source and ordered ports, and combines repeated scalar packets with polynomial powers and a balanced product. Connected cases use exact two-state boundary messages, summing both assignments at each bridge. No full-result lookup supplies a timed answer.','','Every row compares three fresh full-graph variable-elimination solves, three solves with an empty packet cache, and three solves with a persistent packet cache. All scalar coefficients, ordered retained-port spectra, configuration counts and first/second moments agree. Open operators use the explicitly declared zero-glue convention. Timings include source-bound solve and native readout/checks; planning, external equality verification, native receipt and file writing are outside the timed solve.','','## Anchor and extension measurements','','| Family | N | Components | Fresh VE (ms) | Empty packet cache (ms) | Warm packet cache (ms) |','|---|---:|---:|---:|---:|---:|']
    for r in rows:
        if r['N'] in [96,100,105,110,115,120]:lines.append(f"| {r['family']} | {r['N']} | {r['components']} | {r['variable_elimination_median_ms']:.3f} | {r['packet_cold_median_ms']:.3f} | {r['packet_warm_median_ms']:.3f} |")
    lines+=['','## Coverage','',json.dumps(summary,indent=2),'','## Reusable result','','Packet size and retained boundary size govern this route. The connected signed family makes the distinction executable: a graph can be connected and frustrated while retaining small exact packet interfaces. Larger connected components alone do not determine high cost.','','The unchanged historical frustrated graphs have different interactions; this catalog supplies an additional family at each N. Applying packet messages to those existing graphs requires their actual source-bound separators. No coupling was removed from an existing canonical calculation.','','The test result suggests strong contact with the concept.' if state['status']=='COMPLETE' else 'Campaign remains in progress.','','## Reproduce','','Use `run.py --smoke` for the bounded regression, then `run.py` for all 360 source records. Existing completed result files are not silently overwritten. `query.py FAMILY N` retrieves a source-bound result or executes a fresh packet solve. No global selector or training queue is changed.','']
    (P/'REPORT.md').write_text('\n'.join(lines))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');args=ap.parse_args();resource=budget();save(P/'RESOURCE_SNAPSHOT.json',resource)
    manifest=make_sources() if not (P/'SOURCE_MANIFEST.json').exists() else load(P/'SOURCE_MANIFEST.json')
    smoke=args.smoke;folder='smoke' if smoke else 'results';(P/folder).mkdir(exist_ok=True);statefile=P/('SMOKE_STATUS.json' if smoke else 'STATUS.json')
    state=load(statefile) if statefile.exists() else dict(completed=[],started=time.time(),status='STARTING',pid=os.getpid())
    state.update(status='RUNNING',pid=os.getpid());save(statefile,state)
    roster=[r for r in manifest if not smoke or r['N'] in [1,4,100,105,110,120]]
    from CURRENT_REVISION import runtime
    save(P/'RUNTIME_IDENTITY.json',dict(verified=runtime.verify(),python=sys.version,implementation_hash=sha(P/'packet.py'),solver_hash=sha(P/'vendor/spin_exact.py'),resource=resource,baseline='Fresh full-graph FLINT variable elimination',optimized='Source-bound packet polynomial power/product or two-state bridge contraction'))
    with DomainSession.start('MATTER_SEARCH',objective='Extend the exact N100/N105 packet family across N1–120 and execute signed connected packet variants',output_root=P/('smoke_sessions' if smoke else 'sessions'),receipt_storage='gzip') as session:
        print(session.announcement(),flush=True);save(P/('SMOKE_SESSION.json' if smoke else 'SESSION.json'),dict(path=str(session.directory),announcement=session.announcement()));session.consumer=Adapter(session.consumer)
        try:
            for item in roster:
                key=item['key']
                if key in state['completed']:continue
                if STOP or (P/'STOP').exists():state['status']='STOPPED';break
                if time.time()-state['started']>1800:state['status']='TIME_GATE';break
                budget();c=load(P/'sources'/f'{key}.json');state.update(active=key,updated=time.time());save(statefile,state)
                pre=dict(key=key,source_hash=item['source_hash'],source_record_hash=digest(c),code_hash=sha(P/'packet.py'),question='Can the recovered packet grammar retain fast exact full spectra at this N, including signed and connected variants?',method_comparison=['full_graph_variable_elimination','empty_packet_cache','warm_packet_cache'],resource_backend='POD_SERIAL_FLINT_CPU',expected_output='Full scalar and ordered-port DOS, zero-glue open operators, count and first/second moment checks',canonical_overwrite=False)
                save(P/folder/(key+'_PRECOMMIT.json'),pre)
                result=session.execute('GEN4_PACKET_CATALOG_SOLVE',pre,purpose='Source structure to exact packet factorization; compare every coefficient with independent full-graph elimination')
                with gzip.open(P/folder/(key+'.json.gz'),'wt') as f:json.dump(result,f)
                state['completed'].append(key);state['active']=None;save(statefile,state)
                if len(state['completed'])%10==0:
                    session.execute('GEN3_CHECKPOINT',{},purpose='Preserve exact packet catalog result custody');print('COMPLETE',len(state['completed']),key,flush=True)
                    if not smoke:report(state)
            else:state['status']='COMPLETE'
            session.execute('GEN3_CHECKPOINT',{},purpose='Final exact packet catalog checkpoint')
            if not smoke:
                payload={key:[dict(state=list(state),coefficients=[str(v) for v in poly]) for state,poly in table.items()] for key,table in session.consumer.cache.items()}
                with gzip.open(P/'PACKET_TABLES.json.gz','wt') as f:json.dump(payload,f)
                save(P/'PACKET_TABLES_MANIFEST.json',dict(sha256=sha(P/'PACKET_TABLES.json.gz'),distinct_tables=len(payload),key_contract='SHA256 of complete local fields, edges and ordered ports',validation='All completed global outputs checked against independent full-graph variable elimination',complete_global_results_cached=False))
        except BaseException:
            state['status']='FAILED';state['error']=traceback.format_exc();save(statefile,state);raise
        finally:
            state['updated']=time.time();save(statefile,state)
            if not smoke:report(state)
    print(state['status'],len(state['completed']),flush=True)

if __name__=='__main__':main()
