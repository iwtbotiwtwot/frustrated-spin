"""Verify installed catalog retrieval, model wiring and checkpoint recovery."""
import argparse,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.root.resolve()))
from SAM_PROJECT.session import DomainSession
a.out.mkdir(parents=True,exist_ok=False);checks={}
with DomainSession.start('MATTER_SEARCH',objective='Adopt all-integer spin training, expanded exact catalog and portfolio planner',output_root=a.out/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),str(s.directory),flush=True)
 cap=s.execute('GEN3_CAPABILITIES',{},purpose='Check installed training operations and models');meta=s.execute('GEN3_SPIN_CATALOG',{},purpose='Read expanded source roster');learn=s.execute('GEN3_SPIN_LEARNING',{},purpose='Recover retained policy sources and training experience')
 checks['all96_sizes']=meta['sizes']==list(range(1,97));checks['nine_models']=len(learn['models'])==9 and all(x in cap['installed_models'] for x in learn['models']);checks['105_transitions']=len(meta['transitions'])==105
 entries={}
 for n in meta['sizes']:
  v=s.execute('GEN3_SPIN_ENTRY',dict(N=n),purpose='Adopt exact integer source without new spin arithmetic');entries[n]=v
  checks[f'N{n}']=int(v['spectrum']['configuration_count'])==1<<n and not v['recomputed']
 for key in meta['transitions']:
  x,y=map(int,key.split('->'));v=s.execute('GEN3_SPIN_TRANSITION',dict(from_N=x,to_N=y),purpose='Recover measured source-bound transition');checks[key]=v['transition']['from_source']==entries[x]['source']['source_sha256'] and v['transition']['to_source']==entries[y]['source']['source_sha256']
 v=s.execute('GEN3_SPIN_PLAN',dict(source=entries[96]['source'],previous_N=84),purpose='Use installed learned ranking and five-method planning on held N96 source')
 checks['five_methods']=len(v['plan']['method_comparison'])==5;checks['N96_portfolio']=v['plan']['selected']['weighted_entries']==430070400 and v['plan']['selected']['width']==21
 checks['native_predictions']=len(v['model_prediction']['predictions'])==5;checks['unretained_boundary_reported']=not v['previous_spectrum_sufficient']
 try:s.execute('GEN3_SPIN_ENTRY',dict(N=96,source_sha256='0'*64),purpose='Check source identity guard')
 except ValueError:checks['wrong_source_rejected']=True
 else:checks['wrong_source_rejected']=False
 s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint adopted learning');directory=s.directory
with DomainSession(directory) as recovered:
 v=recovered.execute('GEN3_SPIN_ENTRY',dict(N=96),purpose='Recover installed exact result across restart');checks['recovery']=v['spectrum']==entries[96]['spectrum']
result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,session=str(directory),check_count=len(checks),engine=s.manifest,N96_spectrum_sha256=entries[96]['spectrum']['spectrum_sha256'])
(a.out/'ADOPTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','engine']}));assert all(checks.values()),[k for k,v in checks.items() if not v]
