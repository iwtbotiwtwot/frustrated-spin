"""Read-only analysis of completed native receipts, exact results and CUPTI traces."""
from pathlib import Path
import collections
import datetime
import gzip
import hashlib
import json
import sys
P=Path(__file__).resolve().parent;R=P/'results/ram'
sys.path.insert(0,str(P.parent/'frustrated_spin_n72_bench1'))
from concurrency import summary

def gz(path):return json.load(gzip.open(path,'rt'))
meta=json.loads((R/'COMPLETE.json').read_text());sources=json.loads((R/'SOURCES.json').read_text())
rows=[]
for n in meta['sizes']:
    value=gz(R/f'N{n}_warm.json.gz');answer=value['answer'];execution=value['execution'];p=value['plan']
    assert all(answer['checks'].values()) and int(answer['configuration_count'])==1<<n
    assert sum(int(c) for _,c in answer['scalar_dos'])==1<<n
    assert all(sum(int(c) for _,c in row)==1<<(n-len(answer['retained_ports'])) for row in answer['closed_port_rows'])
    admitted=[c for c in p['candidates'] if c['width']<=22]
    fresh=min((c for c in admitted if c['method']=='fresh_min_fill'),key=lambda c:c['weighted_entries'])
    transferred=[c for c in admitted if c['method']=='transition_priority']
    transfer=min(transferred,key=lambda c:c['weighted_entries']) if transferred else None
    rows.append(dict(N=n,edges=len(sources[meta['sizes'].index(n)]['edges']),seconds=execution['total_ns']/1e9,
                     arithmetic_seconds=execution['arithmetic_ns']/1e9,prepare_seconds=execution.get('prepare_ns',0)/1e9,
                     reconstruction_seconds=answer['reconstruction_ns']/1e9,method=p['selected']['method'],branches=p['selected']['branches'],
                     width=p['selected']['width'],weighted_entries=p['selected']['weighted_entries'],
                     transfer_saving_fraction=(fresh['weighted_entries']-transfer['weighted_entries'])/fresh['weighted_entries'] if transfer else None,
                     ground_energy=answer['ground_energy'],ground_degeneracy=answer['ground_degeneracy'],bins=len(answer['scalar_dos']),
                     spectrum_sha256=answer['spectrum_sha256'],checks=answer['checks'],index_cache=value['index_cache'],
                     gpu_map_hits=sum(x['map_hits'] for x in execution.get('boot',[])),gpu_map_misses=sum(x['map_misses'] for x in execution.get('boot',[]))))
    if n>24:
        tasks=[tuple(x['task']) for x in execution['profiles']]
        assert len(set(tasks))==len(tasks) and len(tasks)*execution['batch']==p['root_count']*len(p['primes'])
session=next((R/'sessions').iterdir());receipts=[]
for path in session.rglob('RECEIPT.json'):
    receipt=json.loads(path.read_text())
    for name in ['INPUT','OUTPUT']:
        raw=(path.parent/(name+'.json.gz')).read_bytes()
        descriptor=(path.parent/(name+'.json')).read_bytes()
        assert hashlib.sha256(descriptor).hexdigest()==receipt[name.lower()+'_sha256']
        assert hashlib.sha256(raw).hexdigest()==json.loads(descriptor)['compressed_sha256']
        assert hashlib.sha256(gzip.decompress(raw)).hexdigest()==receipt[name.lower()+'_logical_sha256']
    receipts.append(receipt)
kernels={};record_count=0
for path in R.glob('GPU*_KERNELS.csv'):
    with path.open() as f:
        header=json.loads(next(f));assert header['dropped']==0
        records=[tuple(map(int,line.split(','))) for line in f]
    assert len(records)==header['records'];record_count+=len(records);offset=header['offset_ns']
    kernels[int(path.name[3:].split('_')[0])]=[((a+offset)/1e9,(b+offset)/1e9) for a,b,_,_ in records]
assert len(kernels)==14
activity={}
for name in ['N96_warm','N96_replay']:
    v=gz(R/(name+'.json.gz'));e=v['execution'];lo=e['ready_ns']/1e9;hi=e['gpu_done_ns']/1e9
    activity[name]=dict(full=summary(kernels,lo,hi),steady=summary(kernels,lo+1,hi-1),
                        seconds=e['total_ns']/1e9,prepare_seconds=e['prepare_ns']/1e9,
                        map_hits=sum(x['map_hits'] for x in e['boot']),map_misses=sum(x['map_misses'] for x in e['boot']))
assert gz(R/'N96_replay.json.gz')['answer']['scalar_dos']==gz(R/'N96_warm.json.gz')['answer']['scalar_dos']
frozen=json.loads((P.parents[1]/'SLC/18_SAM_NATIVE_QC/SLCV40_N96_CAPACITY_ADMITTED_H14C_512/work/N96_H14C/N96_RETAINED_OPERATOR.json').read_text())
fresh=gz(R/'N96_warm.json.gz')['answer']
for state,row in enumerate(fresh['open_y_operator']):
    oldstate=sum(((state>>fresh['parent_port_vertices'].index(v))&1)<<i for i,v in enumerate(frozen['port_order']))
    expected=[[k,str(c)] for k,c in enumerate(frozen['w_coefficients'][oldstate]) if c]
    assert row==expected
telemetry=json.loads((R/'TELEMETRY.json').read_text());peak=max(int(x['memory.current']) for x in telemetry)
assert 880000000000-peak>8*(1<<30)
def dt(x):return datetime.datetime.fromisoformat(x)
created=dt(json.loads((session/'SESSION.json').read_text())['created'])
solves=sorted([r for r in receipts if r['operation']=='GEN4_SPIN_CATALOG_SOLVE'],key=lambda r:r['time'])
learning=json.loads((R/'NATIVE_LEARNING.json').read_text());lessons=json.loads((R/'LESSONS.json').read_text())
pred=learning['predictions']['predictions']
result=dict(status='PASS',entries=rows,exact_complete_solves=len(solves),native_receipts=len(receipts),
            all16_N96_open_port_operators_match_original=True,
            session_wall_through_first_N96_seconds=(dt(solves[-2]['time'])-created).total_seconds(),
            sum_first11_solve_seconds=sum(r['seconds'] for r in rows),
            matched_N96_activity=activity,kernel_records=record_count,dropped_kernel_records=0,peak_host_GiB=peak/1024**3,
            peak_worker_pool_GiB=max(x['pool_bytes'] for n in meta['sizes'] if n>24 for x in gz(R/f'N{n}_warm.json.gz')['execution']['boot'])/1024**3,
            native_model_depth=learning['model']['record']['model']['depth'],
            native_predictions_correct=sum(int(p['positive']==bool(r['label'])) for p,r in zip(pred,lessons)),
            native_predictions_total=len(lessons),native_reserved_N96_correct=pred[-1]['positive']==bool(lessons[-1]['label']),
            model_role='ADVISORY; exact structural candidate comparison controls execution')
(P/'ANALYSIS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['entries','matched_N96_activity']},indent=2))
for name,r in activity.items():print(name,r['seconds'],r['prepare_seconds'],r['map_hits'],r['map_misses'],r['steady']['mean_gpu_busy_fraction'],r['steady']['all14_busy_fraction'])
