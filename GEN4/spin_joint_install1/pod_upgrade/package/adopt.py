"""Use the installed upgrade on actual Volume II/A3D41 and SB source inputs."""
import argparse,json,sys,hashlib,collections,copy
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--external',action='store_true');a=ap.parse_args()
P=Path(__file__).resolve().parent;R=a.root.resolve();O=a.out.resolve();O.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(R))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3 import spin_joint as j,spin_exact as x
checks={};sessions=[];findings=[]
def save(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
examples=json.loads((P/'PHASE_ADOPTION_INPUTS.json').read_text())
with DomainSession.start('ATOM3D',objective='Use exact C4 source maps with joint phase-coordinate, boundary and collective response',output_root=O/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),flush=True);sessions.append(str(s.directory))
 for idx,row in enumerate(examples):
  actual=row['example']['result'];graph=actual['spin_source']
  p=dict(source=graph,ports=[0,1,2,3],joint=True)
  solved=s.execute('GEN3_SPIN_SOLVE',p,purpose='Extend the existing actual six-spin C4 source calculation to retain its full joint E,M,b operator')
  checks[f'C4_{idx}_same_source_DOS']=[(int(e),int(c)) for e,c in solved['answer']['scalar_dos']]==[(int(e),int(c)) for e,c in actual['spin_full_energy_spectrum']]
  q=dict(result_ref=solved['result_ref'],uniform_field='1/2',boundary=[1,None,None,-1],collective_coupling='1/3',include_spectrum=True)
  response=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=q),purpose='Read exact phase-coordinate alignment and boundary response on the retained Volume II source map')
  saved=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=q),purpose='Reuse the source-bound phase response through the existing native result cache')
  checks[f'C4_{idx}_reuse']=saved['reused'] and saved['arithmetic_calls']==0
  findings.append(dict(domain='ATOM3D',covers=row['covers'],rule=row['rule'],source_couplings=actual['couplings'],
   input_source_sha256=solved['source']['source_sha256'],response=response['result']['answer'],
   correspondence='z_i=(s_i+t_i)/2 + i*(s_i-t_i)/2; E_spin=2H_phase; M=2*sum Re(z_i). h is a formal phase-alignment source coordinate.'))
  save(f'C4_{idx}_SOLVE.json',solved);save(f'C4_{idx}_READOUT.json',response)
 s.execute('GEN3_CHECKPOINT',{},purpose='Retain actual A3D41/Volume II source use of installed upgrade')
with DomainSession.start('STARBREAKER',objective='Extend the retained N100 structural basis with signed boundary/collective response',output_root=O/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),flush=True);sessions.append(str(s.directory))
 status=s.execute('SB_STATUS',{},purpose='Preserve current Starbreaker engine and learned-history policy identity')
 known=s.execute('GEN3_SPIN_SOURCE',dict(N=100),purpose='Read the inherited N100 packet source used by the structure-first basis')
 solved=s.execute('GEN3_SPIN_SOLVE',dict(N=100,joint=True),purpose='Compute joint occupancy of the same exact N100 source through the shared SB consumer')
 checks['SB_N100_original_DOS']=solved['answer']['scalar_dos']==known['spectrum']['scalar_dos']
 q=dict(result_ref=solved['result_ref'],uniform_field='0',boundary=[1,None,-1,None],boundary_fields=['0','1/2','0','-1/2'])
 read=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=q),purpose='Resolve opposite signed endpoint perturbations while retaining the ordered boundary identities')
 checks['SB_existing_engine']=status['version']=='SB-GEN3-ACCUMULATION-R1'
 findings.append(dict(domain='STARBREAKER',source='Retained N100 structural basis',source_sha256=solved['source']['source_sha256'],response=read['result']['answer'],
  correspondence='Source-coordinate boundary response for the inherited N100 basis; signed event order and carrier/matter types remain in existing SB history operations.'))
 save('SB_N100_SOLVE.json',solved);save('SB_N100_READOUT.json',read)
 # A nonzero field is a control against installing the scalar boundary shortcut unconditionally.
 c=j.source_recipe(dict(family='signed_packet_chain',N=30));graph=copy.deepcopy(c['source']);graph.pop('source_sha256');graph['fields'][c['blocks'][-1][0]]=2
 r=s.execute('GEN3_SPIN_SOLVE',dict(source=graph,ports=c['ports'],decomposition={k:c[k] for k in ('blocks','bridges')}),purpose='Require full signed message contraction when a source field breaks boundary equality')
 checks['boundary_shortcut_rejects_field']=r['execution']['details']['reduction']=='NOT_ADMITTED_BOUNDARY_SPECTRA_DIFFER'
 reference=s.execute('GEN3_SPIN_SOLVE',dict(source=graph,ports=c['ports'],backend='cpu',options={'method':'variable_elimination'}),purpose='Independent existing solver comparison for the field-broken packet source')
 checks['boundary_fallback_exact']=r['answer']==reference['answer']
 s.execute('GEN3_CHECKPOINT',{},purpose='Retain SB adoption and field-control execution')
 if a.external:
  for key in ['packet_N900_fill_+1','signed_packet_chain_N300_fill_-1']:
   data=s.execute('GEN3_SPIN_SOURCE',dict(joint_key=key),purpose='Adopt the actual completed large joint dataset by authenticated source/manifest identity')
   result=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=dict(result_ref=data['result_ref'],uniform_field='1/2',boundary=[1,None,-1,None])),purpose='Use streamed completed bulk data through the installed shared Starbreaker/CE runtime')
   checks[key+'_streamed']=result['result']['answer']['configuration_count']==str(1<<(data['joint']['N']-2))
   exported=s.execute('GEN3_RESULT_EXPORT',dict(roots=[data['result_ref']]),purpose='Make external-data custody explicit in native checkpoint/export metadata')
   checks[key+'_external_portability']=exported['portability']=='REQUIRES_HASH_BOUND_EXTERNAL_DATA'
   save(key+'_READOUT.json',result);save(key+'_EXPORT.json',exported)
   findings.append(dict(domain='SHARED_GEN4_EXTERNAL_DATA',dataset=key,response=result['result']['answer']))
 s.execute('GEN3_CHECKPOINT',{},purpose='Retain all installed shared source responses')
save('FINDINGS.json',findings);save('ADOPTION.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,sessions=sessions));print(json.dumps(checks),flush=True)
assert all(checks.values()),checks
