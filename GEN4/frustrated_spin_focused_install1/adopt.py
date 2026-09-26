"""Adopt focused exact-plan reuse, hardware-bound costs, models and recovery."""
import argparse,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.root.resolve()))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3 import retained
from CURRENT_REVISION.engines.SLC.gen3.spin_focus import decode
checks={};a.out.mkdir(parents=True,exist_ok=False)
with DomainSession.start('MATTER_SEARCH',objective='Adopt focused source-plan cache and calibrated cost learning',output_root=a.out/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),s.directory,flush=True)
 meta=s.execute('GEN3_SPIN_FOCUSED',{},purpose='Discover installed focused source plans and explicit hardware scope');cap=s.execute('GEN3_CAPABILITIES',{},purpose='Verify new operation and pairwise model installation');checks['new_operations']=all('GEN3_SPIN_'+x in cap['operations'] for x in ['FOCUSED','COST'])
 known=[]
 for sha,row in meta['sources'].items():
  # Public mathematical retrieval schema follows installed retained API.
  from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import validate_source
  obj=json.loads((a.root/'CURRENT_REVISION/engines/SLC/mathematical_library/objects'/row['result_ref'][:2]/row['result_ref'][2:]).read_text());value=obj['value'];source=validate_source(value['source'])
  result=s.execute('GEN3_SPIN_PLAN',dict(source=source,previous_N=min(84,source['N']-1)),purpose='Reuse identical-source best measured plan without repeating expanded search')
  role='RETAINED_EXACT_PLAN_FOR_IDENTICAL_SOURCE' if value.get('measurement_kind')=='single_exact_execution' else 'RETAINED_MEASURED_PLAN_FOR_IDENTICAL_SOURCE'
  checks[row['group']]=result['plan']['mathematical_plan_sha256']==value['plan']['mathematical_plan_sha256'] and result['model_role']==role;known.append(value)
 n96=next(v for v in known if v['source_group']=='G0-N96')
 for backend in ['retained','batched']:
  result=s.execute('GEN3_SPIN_COST',dict(source=n96['source'],previous_N=95,backend=backend),purpose='Use retained time-model parameters with exact lightweight plan features')
  checks['cost_'+backend]=len(result['estimates'])==5 and all(0<r['predicted_nanoseconds']<10**18 for r in result['estimates']) and result['known_best']['plan']['mathematical_plan_sha256']==n96['plan']['mathematical_plan_sha256']
 probe=dict(n96['source']);probe.pop('source_sha256');probe['family']='FOCUSED_INSTALL_PLAN_WIRING_CHECK'
 result=s.execute('GEN3_SPIN_PLAN',dict(source=probe,previous_N=95,search='expanded'),purpose='Exercise generic expanded search on an uncached source identity; planning only')
 checks['generic_expanded_search']=len(result['plan']['method_comparison'])==6 and result['plan']['execution_admitted'] and 'retained_plan_ref' not in result['plan']
 checks['pairwise_models']=all(name in cap['installed_models'] for name in ['spin-focused-pairwise-v1','spin-focused-fast-pairwise-v1'])
 old=s.execute('GEN3_SPIN_ENTRY',dict(N=96),purpose='Verify original exact catalog remains available');checks['original_spectrum']=old['spectrum']['spectrum_sha256']==n96['spectrum_sha256']
 if any(v['source']['N']==120 for v in known):
  frontier=s.execute('GEN3_SPIN_ENTRY',dict(N=120),purpose='Retrieve the new exact frontier spectrum');tr=s.execute('GEN3_SPIN_TRANSITION',dict(from_N=96,to_N=120),purpose='Retrieve its actual changed-boundary transition')
  checks['N120_exact_count']=frontier['spectrum']['configuration_count']==str(1<<120)
  checks['N120_transition']=len(tr['transition']['removed_parent_edges'])==12 and len(tr['transition']['added_parent_edges'])==72 and not tr['transition']['retained_boundary_sufficient']
  fc=s.execute('GEN3_SPIN_COST',dict(source=frontier['source'],previous_N=96),purpose='Retrieve observed frontier cost with its distinct branch-group backend')
  checks['N120_cost_scope']=not fc['estimated'] and fc['observed_nanoseconds']==frontier['execution']['total_ns'] and not fc['estimates']
  from CURRENT_REVISION.engines.SLC.gen3.spin_planning import plan as structural_plan
  frozen=json.loads((a.root/'CURRENT_REVISION/engines/SLC/gen3/spin_data/PARENT_PLAN.json').read_text())
  # Implementation wiring check only: arithmetic already qualified on pod.
  cp=structural_plan(frontier['source'],frozen)
  checks['five_prime_planner_capacity']=cp['primes'][-1]==1224736769 and cp['prime_product_sufficient']
 s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint focused capability adoption');directory=s.directory
with DomainSession(directory) as s:
 restored=s.execute('GEN3_SPIN_PLAN',dict(source=n96['source'],previous_N=95),purpose='Recover measured source-plan reuse across restart');checks['checkpoint_recovery']=restored['plan']['mathematical_plan_sha256']==n96['plan']['mathematical_plan_sha256']
result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,check_count=len(checks),session=str(directory),N96_plan_sha256=n96['plan']['mathematical_plan_sha256'],N96_median_ns=n96['best_median_ns'])
(a.out/'ADOPTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}));assert all(checks.values()),checks
