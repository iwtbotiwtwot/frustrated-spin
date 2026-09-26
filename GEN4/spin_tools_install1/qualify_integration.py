"""Exercise shared native tools through active CE routes and retained source families."""
import argparse,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--gpu',action='store_true');a=ap.parse_args()
R=a.root.resolve();P=a.out.resolve();P.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(R))
from SAM_PROJECT.session import DomainSession
checks={};sessions=[];results={}
def save(name,value):(P/name).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
contract=dict(variables=[dict(name='x',domain=[-1,1]),dict(name='y',domain=[0,1,2])],factors=[dict(scope=['x','y'],table=[2,-3,5,-7,11,-13]),dict(scope=['x'],table=[1,-1])],keep=['y'],source_binding=dict(campaign='SHARED_SPIN_TOOLS_ADOPTION',meaning='Synthetic signed integer factors for CE interoperability; not a domain-specific scientific input'))
for domain in ['MATTER_SEARCH','ATOM3D','STARBREAKER','RH']:
 with DomainSession.start(domain,objective='Adopt shared exact finite-factor tool through this existing CE route',output_root=P/'sessions',receipt_storage='gzip') as s:
  print(s.announcement(),s.directory,flush=True)
  r=s.execute('GEN3_SPIN_CONTRACT',contract,purpose='Exercise the same explicit signed factor table through the current shared SLC interface')
  checks[domain+'_signed_factor_result']=r['answer']['table']==['9','-14','18'] and r['answer']['total']=='13'
  s.execute('GEN3_CHECKPOINT',{},purpose='Retain shared-tool interoperability state');sessions.append(str(s.directory));save(domain+'_RETURNED.json',r)
with DomainSession.start('MATTER_SEARCH',objective='Adopt fresh component spectra, policy inference and portable GPU execution',output_root=P/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),s.directory,flush=True)
 sessions.append(str(s.directory))
 for n in [100,105]:
  old=s.execute('GEN3_SPIN_SOURCE',dict(N=n),purpose='Read retained exact packet source and conditional spectrum')
  r=s.execute('GEN3_SPIN_SOLVE',dict(N=n,backend='cpu'),purpose='Recompute the complete packet source through the installed general component solver')
  checks[f'N{n}_fresh_scalar']=r['recomputed'] and r['answer']['scalar_dos']==old['spectrum']['scalar_dos']
  checks[f'N{n}_fresh_ports']=[v['dos'] for v in r['answer']['port_rows']]==old['spectrum']['closed_port_rows']
  save(f'N{n}_FRESH.json',r)
  selected=s.execute('GEN3_SPIN_SELECT',dict(N=n),purpose='Select a source-appropriate exact component route')
  checks[f'N{n}_component_selection']=selected['execution_backend']=='cpu';save(f'N{n}_SELECT.json',selected)
 # Unseen identity and changed fields: no retained answer lookup can satisfy this.
 old=s.execute('GEN3_SPIN_SOURCE',dict(N=30),purpose='Acquire a retained graph for a changed-source implementation check')
 graph=dict(old['source']);graph.pop('source_sha256');graph['family']='SHARED_TOOL_CHANGED_FIELD_ADOPTION';graph['fields']=list(graph['fields']);graph['fields'][0]+=1
 ports=old['spectrum']['retained_ports']
 cpu=s.execute('GEN3_SPIN_SOLVE',dict(source=graph,ports=ports,backend='cpu',options={'method':'variable_elimination'}),purpose='Compute a fresh changed-source spectrum with native polynomial elimination')
 checks['changed_source_is_fresh']=cpu['recomputed'] and cpu['source']['source_sha256']!=old['source']['source_sha256'];save('CHANGED_SOURCE_CPU.json',cpu)
 selection=s.execute('GEN3_SPIN_SELECT',dict(source=graph,ports=ports,execution_backend='gpu',policy='focused_pairwise',previous_N=100),purpose='Exercise native focused model inference with an explicit transfer scope and a component-family predecessor')
 checks['native_focused_model_used']=selection['model_applied'] and bool(selection['model_prediction'])
 checks['component_predecessor_anchor_explicit']=bool(selection['anchor_note']);save('FOCUSED_SELECTION.json',selection)
 if a.gpu:
  from copy import deepcopy
  gpu_plan=deepcopy(selection['plan'])
  cutset=[v for v in range(graph['N']) if v not in ports][:5]
  gpu_plan['selected']['cutset']=cutset
  gpu_plan['selected']['order']=[v for v in gpu_plan['selected']['order'] if v not in cutset]
  gpu_plan['primes']=[998244353,1004535809,469762049,167772161,1224736769]
  gpu_plan.pop('mathematical_plan_sha256',None)
  p=dict(source=graph,ports=ports,backend='gpu',plan=gpu_plan,options=dict(checkpoint_dir=str(P/'gpu_checkpoint'),max_seconds=120,root_batch=16,branch_group=16))
  gpu=s.execute('GEN3_SPIN_SOLVE',p,purpose='Execute adaptive CUDA tasks and compare every exact scalar and conditional coefficient with the CPU result')
  checks['actual_cuda_execution']=gpu['status']=='EXACT' and gpu['execution']['fresh_arithmetic_tasks']>0 and gpu['execution']['worker_count']>0
  checks['five_primes_two_branch_groups']=gpu['execution']['branch_count']==32 and gpu['execution']['branches_per_task']==16
  checks['gpu_cpu_full_answer']=gpu['answer']==cpu['answer'];save('CHANGED_SOURCE_GPU.json',gpu)
  recovered=s.execute('GEN3_SPIN_SOLVE',p,purpose='Recover all completed source-bound modular tasks from the on-disk checkpoint')
  checks['gpu_checkpoint_recovery']=recovered['answer']==gpu['answer'] and recovered['execution']['resumed_tasks']==recovered['execution']['total_tasks'] and recovered['execution']['fresh_arithmetic_tasks']==0
  save('GPU_RECOVERY.json',recovered)
 s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint source/solver/policy adoption')
 directory=s.directory;ref=cpu['result_ref']
with DomainSession(directory) as s:
 r=s.execute('GEN3_SPIN_SOLVE',dict(source=graph,ports=ports,mode='recover',result_ref=ref),purpose='Recover a new solved source by exact retained reference after reopening the native session')
 checks['fresh_result_session_recovery']=not r['recomputed'] and r['answer']==cpu['answer'];save('SESSION_RECOVERY.json',r)
out=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,check_count=len(checks),sessions=sessions,gpu=a.gpu)
save('QUALIFICATION.json',out);print(json.dumps(out));assert all(checks.values()),checks
