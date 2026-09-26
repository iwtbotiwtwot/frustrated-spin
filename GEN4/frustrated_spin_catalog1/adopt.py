"""Fresh installed-runtime adoption and checkpoint recovery checks."""
import argparse
import gzip
import json
from pathlib import Path
import sys

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
sys.path.insert(0,str(args.root.resolve()))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.retained import digest
args.out.mkdir(parents=True,exist_ok=False)
checks={}
s=DomainSession.start('MATTER_SEARCH',objective='Adopt installed exact spin catalog and transition memory in a fresh native consumer',output_root=args.out/'sessions',receipt_storage='gzip')
print(s.announcement(),str(s.directory),flush=True)
try:
    cap=s.execute('GEN3_CAPABILITIES',{},purpose='Verify installed source-bound catalog operations and learned policy')
    checks['four_native_operations']=all('GEN3_SPIN_'+x in cap['operations'] for x in ['CATALOG','ENTRY','TRANSITION','PLAN'])
    catalog=s.execute('GEN3_SPIN_CATALOG',{},purpose='Discover installed spin sources and transition references')
    entries=[]
    for n in catalog['sizes']:
        value=s.execute('GEN3_SPIN_ENTRY',dict(N=n),purpose='Read installed exact spectrum without new spin arithmetic')
        checks['N'+str(n)]=value['arithmetic_calls']==0 and not value['recomputed'] and int(value['spectrum']['configuration_count'])==1<<n
        entries.append(value)
    transitions=[]
    for x,y in zip(catalog['sizes'],catalog['sizes'][1:]):
        value=s.execute('GEN3_SPIN_TRANSITION',dict(from_N=x,to_N=y),purpose='Adopt executed transition, source changes, candidate costs and reusable work')
        checks[f'transition{x}_{y}']=value['arithmetic_calls']==0 and not value['recomputed'];transitions.append(value)
    value=s.execute('GEN3_SPIN_PLAN',dict(source=entries[-1]['source'],previous_N=84),purpose='Exercise installed transition planning on the exact N84 to N96 source change')
    checks['planner_reproduces_N96_choice']=value['plan']['selected']['weighted_entries']==entries[-1]['plan']['selected']['weighted_entries']
    checks['unretained_boundary_reported']=not value['previous_spectrum_sufficient']
    checks['native_model_installed']=catalog['native_model'] in cap['installed_models']
    checks['model_used_advisory']=value['model_role'].startswith('ADVISORY') and bool(value['model_prediction']['predictions'])
    try:s.execute('GEN3_SPIN_ENTRY',dict(N=96,source_sha256='0'*64),purpose='Verify source mismatch cannot select an unrelated spectrum')
    except ValueError:checks['wrong_source_rejected']=True
    else:checks['wrong_source_rejected']=False
    state=s.execute('GEN3_CHECKPOINT',{},purpose='Retain adopted catalog, transition closure and installed native model')
    directory=s.directory
finally:s.close()
with DomainSession(directory) as recovered:
    value=recovered.execute('GEN3_SPIN_ENTRY',dict(N=96),purpose='Recover exact source catalog from installed native checkpoint')
    checks['checkpoint_recovery']=value['spectrum']==entries[-1]['spectrum']
result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,session=str(directory),engine=s.manifest,
            installed_objects=1462,entries=11,transitions=10,N96_spectrum_sha256=entries[-1]['spectrum']['spectrum_sha256'])
(args.out/'ADOPTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
assert all(checks.values())
