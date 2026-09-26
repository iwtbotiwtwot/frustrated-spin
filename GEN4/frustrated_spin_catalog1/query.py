"""Small command-line front end to the installed native spin operations."""
import argparse
import json
from pathlib import Path
import sys

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--full',action='store_true')
sub=p.add_subparsers(dest='command',required=True);sub.add_parser('list')
entry=sub.add_parser('entry');entry.add_argument('N',type=int)
tr=sub.add_parser('transition');tr.add_argument('from_N',type=int);tr.add_argument('to_N',type=int)
plan=sub.add_parser('plan');plan.add_argument('source',type=Path);plan.add_argument('--previous',type=int,required=True)
a=p.parse_args();sys.path.insert(0,str(a.root))
from SAM_PROJECT.session import DomainSession
operation={'list':'CATALOG','entry':'ENTRY','transition':'TRANSITION','plan':'PLAN'}[a.command]
payload={} if a.command=='list' else dict(N=a.N) if a.command=='entry' else dict(from_N=a.from_N,to_N=a.to_N) if a.command=='transition' else dict(source=json.loads(a.source.read_text()),previous_N=a.previous)
with DomainSession.start('MATTER_SEARCH',objective='Read installed frustrated-spin catalog and transition memory',output_root=a.root/'SAM_RUNTIME/SPIN_QUERIES',receipt_storage='gzip') as s:
    result=s.execute('GEN3_SPIN_'+operation,payload,purpose='Use installed exact source catalog and measured transition experience')
    if not a.full:
        if a.command=='list':result={k:result[k] for k in ['sizes','source_family','native_model','model_role']}
        elif a.command=='entry':result=dict(N=a.N,source_sha256=result['source']['source_sha256'],edges=len(result['source']['edges']),configuration_count=result['spectrum']['configuration_count'],ground_energy=result['spectrum']['ground_energy'],ground_degeneracy=result['spectrum']['ground_degeneracy'],occupied_bins=len(result['spectrum']['scalar_dos']),plan=result['plan']['selected'],recomputed=result['recomputed'])
        elif a.command=='transition':
            tr=result['transition'];result={k:tr[k] for k in ['from_N','to_N','previous_boundary_touched','retained_boundary_sufficient','previous_plan','next_plan','index_cache']}
        else:result={k:result[k] for k in ['plan','previous_boundary_touched','previous_spectrum_sufficient','model_role','result_boundary']}
    print(json.dumps(result,indent=2));print('Session:',s.directory,file=sys.stderr)
