"""Read-only summary of repeated plans, cost calibration and whole-topology tests."""
from pathlib import Path
import json,statistics,gzip,datetime
P=Path(__file__).resolve().parent

def read(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
def analyze(folder):
    groups=read(folder/'GROUPED_EXPERIENCE.json');measurements=read(folder/'MEASUREMENTS.json');specs=read(folder/'SPECIFICATIONS.json');ev=read(folder/'EVALUATION.json');models=read(folder/'FROZEN_MODELS.json')
    winners={gid:min([g for g in groups if g['group']==gid],key=lambda x:x['total_ns']) for gid in sorted({g['group'] for g in groups})}
    policies={}
    for policy in ['cost','pairwise','structural','fresh']:
        active=[(k,e) for k,e in ev.items() if policy in e['choices']];informative=[(k,e) for k,e in active if len({v['case'] for v in e['choices'].values()})>1]
        policies[policy]=dict(groups=len(active),selected_seconds=sum(e['choices'][policy]['total_ns'] for k,e in active)/1e9,oracle_seconds=sum(e['oracle_ns'] for k,e in active)/1e9,optimal=sum(e['choices'][policy]['excess_ns']==0 for k,e in active),choices={k:e['choices'][policy] for k,e in active})
    testcases=[g for g in groups if g['split']=='test'];pred=read(folder/'RESERVED_PREDICTIONS.json');ape=[]
    for gid,row in pred.items():
        for ci,t in zip(row['indices'],row['cost_ns']):
            actual=next(g['total_ns'] for g in testcases if g['case']==ci);ape.append(abs(t-actual)/actual)
    telemetry=read(folder/'TELEMETRY.json');session=next((folder/'sessions').iterdir());receipts=[read(p) for p in (session/'calls').rglob('RECEIPT.json')];start=datetime.datetime.fromisoformat(read(session/'SESSION.json')['created']);end=max(datetime.datetime.fromisoformat(r['time']) for r in receipts)
    result=dict(solves=len(measurements),cases=len(specs),source_groups=len(winners),single_case_test_groups=[gid for gid in ev if len([g for g in testcases if g['group']==gid])==1],best=winners,policies=policies,cost_kind=models['cost']['selected']['kind'],cost_param=models['cost']['selected']['param'],pairwise_depth=models['pairwise']['fit']['depth'],reserved_cost_median_absolute_fractional_error=statistics.median(ape),reserved_cost_mean_absolute_fractional_error=statistics.mean(ape),native_receipts=len(receipts),session_to_last_receipt_seconds=(end-start).total_seconds(),peak_host_GiB=max(int(t['memory.current']) for t in telemetry)/2**30,unadmitted=read(folder/'UNADMITTED.json'))
    for g in groups:
        rr=[r for r in measurements if r['case']==g['case']];assert len(rr)==3 and g['total_ns']==int(statistics.median(r['total_ns'] for r in rr))
    return result

out={}
for name,directory in [('retained','focused-results/ram'),('batched','fast-results/ram')]:
    if (P/directory/'COMPLETE.json').exists():out[name]=analyze(P/directory)
for name,directory in [('boundary','boundary-results/ram'),('boundary_batched','boundary-fast-results/ram')]:
    b=P/directory
    if not (b/'COMPLETE.json').exists():continue
    ev=read(b/'EVALUATION.json');out[name]=dict(choices=len(ev),optimal=sum(e['excess_ns']==0 for e in ev.values()),selected_seconds=sum(e['observed_ns'][e['selected']] for e in ev.values())/1e9,oracle_seconds=sum(min(e['observed_ns'].values()) for e in ev.values())/1e9,restart_seconds=sum(e['observed_ns']['restart'] for e in ev.values())/1e9,reuse_seconds=sum(e['observed_ns']['incremental'] for e in ev.values())/1e9,model=read(b/'FROZEN_MODEL.json')['selected']['kind'],completion=read(b/'COMPLETE.json'))
(P/'ANALYSIS.json').write_text(json.dumps(out,indent=2)+'\n')
for name,row in out.items():
    print(name,json.dumps({k:v for k,v in row.items() if k not in ['best','unadmitted','policies']}))
    if 'policies' in row:print('policies',json.dumps({k:{a:b for a,b in v.items() if a!='choices'} for k,v in row['policies'].items()}))
    if 'best' in row:print('N96',row['best'].get('G0-N96'))
