"""Source-bound installed CE calls, independent exact controls, and native recovery."""
import argparse,collections,copy,gzip,itertools,json,sys,time
from pathlib import Path
from fractions import Fraction
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--gpu',action='store_true');a=ap.parse_args()
R=a.root.resolve();P=a.out.resolve();P.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(R))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3 import spin_joint as j,spin_exact as x
checks={};sessions=[];records=[]
def save(name,value):(P/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def check(name,condition):
 checks[name]=bool(condition)
 if not condition:raise AssertionError(name)
def direct(source,ports,h='0',g='0',boundary=None,bfields=None,mag=None):
 n=source['N'];h=Fraction(h);g=Fraction(g);boundary=boundary or [None]*len(ports);bfields=bfields or ['0']*len(ports)
 density=collections.Counter();gm=collections.Counter();records=[]
 for s in itertools.product((-1,1),repeat=n):
  if any(v is not None and v!=s[ports[i]] for i,v in enumerate(boundary)):continue
  m=sum(s)
  if mag is not None and m!=mag:continue
  e=-sum(w*s[u]*s[v] for u,v,w in source['edges'])-sum(w*z for w,z in zip(source['fields'],s))-h*m-g*Fraction(m*m-n,2)-sum(Fraction(v)*s[k] for k,v in zip(ports,bfields))
  density[e]+=1;records.append((e,m))
 ground=min(density) if density else None
 for e,m in records:
  if e==ground:gm[m]+=1
 return dict(density=[[str(e),str(c)] for e,c in sorted(density.items())],configuration_count=str(len(records)),ground_energy=str(ground) if ground is not None else None,
  ground_degeneracy=str(density[ground]) if ground is not None else '0',ground_magnetization_counts={str(k):str(v) for k,v in sorted(gm.items())},
  energy_sum=str(sum(e for e,m in records)),energy_square_sum=str(sum(e*e for e,m in records)),magnetization_sum=str(sum(m for e,m in records)),
  magnetization_square_sum=str(sum(m*m for e,m in records)),energy_magnetization_sum=str(sum(e*m for e,m in records)))
def compare(expected,answer,name):
 for k,v in expected.items():check(name+'_'+k,answer[k]==v)
with DomainSession.start('MATTER_SEARCH',objective='Qualify installed shared packet/joint exact source methods',output_root=P/'sessions',receipt_storage='gzip') as s:
 print(s.announcement(),flush=True);sessions.append(str(s.directory))
 def call(op,p,why):return s.execute(op,p,purpose=why)
 tools=call('GEN3_SPIN_TOOLS',{},'Read installed additive capability identity')
 check('shared_extension',tools['shared_extension']==j.VERSION)
 check('120canonical_defaults',tools['default_sizes']==list(range(1,121)))
 for n in (97,100,105,119,120):
  src=call('GEN3_SPIN_SOURCE',{'N':n},'Read completed canonical result without recomputation')
  check(f'canonical_{n}_inherited',src['arithmetic_calls']==0)
  if n in (100,105):check(f'canonical_{n}_packet_preserved','PACKET' in src['source']['family'])
  if n==97:
   out=call('GEN3_SPIN_READOUT',{'result_ref':src['result_ref']},'Exercise original scalar readout with newly installed gap result')
   check('gap_readout',out['spectrum_recomputed'] is False)
 for family in j.FAMILIES:
  p=dict(source_recipe=dict(family=family,N=300))
  q=call('GEN3_SPIN_SELECT',p,'Select exact source-bound packet compilation')
  r=call('GEN3_SPIN_SOLVE',p,'Execute complete N300 scalar and ordered boundary density')
  check(f'N300_{family}',r['answer']['configuration_count']==str(1<<300))
  check(f'N300_{family}_method',q['method']=='PACKET_POLYNOMIAL')
  save('N300_'+family+'.json',r)
 for family in j.FAMILIES:
  for fill in (-1,1):
   p=dict(source_recipe=dict(family=family,N=12),dense_fill=fill,joint=True)
   cpu=call('GEN3_SPIN_SOLVE',p,'Compute small complete-source joint DOS through the shared runtime')
   check(f'{family}_{fill}_joint',bool(cpu['joint']))
   source=cpu['source'];ports=cpu['answer']['ports'];boundary=[1]+[None]*(len(ports)-1)
   for h,g,bc in [('0','0',None),('1/2','-1/3',boundary),('-2/3','1/2',None)]:
    fields=['1/3']+['0']*(len(ports)-1)
    req=dict(result_ref=cpu['result_ref'],uniform_field=h,collective_coupling=g,boundary=bc or [None]*len(ports),boundary_fields=fields,include_spectrum=True)
    out=call('GEN3_SPIN_READOUT',req,'Exact collective/boundary response without re-enumeration')
    compare(direct(source,ports,h,g,bc,fields),out['answer'],f'{family}_{fill}_{h}')
    for crossing in out['answer']['ground_state_crossing_fields']:
     d=direct(source,ports,crossing['field'],g,bc,fields)
     check(f'{family}_{fill}_{h}_cross_{crossing["field"]}',d['ground_magnetization_counts']=={str(v['M']):v['degeneracy'] for v in crossing['coexisting_magnetizations']})
   magreq=dict(result_ref=cpu['result_ref'],uniform_field='1/2',magnetization=0,include_spectrum=True)
   out=call('GEN3_SPIN_READOUT',magreq,'Condition the same exact source at fixed total magnetization')
   compare(direct(source,ports,'1/2',mag=0),out['answer'],f'{family}_{fill}_M0')
   if a.gpu:
    gpu=call('GEN3_SPIN_SOLVE',dict(p,backend='gpu'),'Execute GPU local integer arithmetic and exact CPU reconstruction')
    check(f'CUDA_{family}_{fill}',gpu['answer']==cpu['answer'] and gpu['joint']==cpu['joint'])
    check(f'CUDA_backend_{family}_{fill}',gpu['execution']['backend']=='CUDA_LOCAL_INTEGER_CPU_FLINT_JOINT')
   recovery_payload=dict(p,mode='recover',result_ref=cpu['result_ref']);recover_ref=cpu['result_ref']
 # Force general joint VE on a connected graph using a small component admission.
 graph=dict(N=7,edges=[[i,i+1,(-1)**i*(i%3+1)] for i in range(6)],fields=[1,-2,0,1,0,0,-1],parent_vertices=list(range(7)),family='QUALIFICATION_WEIGHTED_PATH')
 p=dict(source=graph,ports=[6,1],joint=True,options=dict(max_component_size=2))
 r=call('GEN3_SPIN_SOLVE',p,'Exercise weighted-source joint variable elimination')
 check('general_joint_VE',r['execution']['backend']=='CPU_FLINT_JOINT_VARIABLE_ELIMINATION')
 out=call('GEN3_SPIN_READOUT',dict(result_ref=r['result_ref'],uniform_field='2/3',boundary=[-1,None],include_spectrum=True),'Query weighted source, preserving reordered ports')
 compare(direct(r['source'],[6,1],'2/3',boundary=[-1,None]),out['answer'],'weighted_VE')
 # Explicit mathematical controls on decomposition and response typing.
 c=j.source_recipe(dict(family='signed_packet_chain',N=30));bad=copy.deepcopy(c['source']);bad.pop('source_sha256');bad['edges'].append([1,16,2]);bad=x.validate_source(bad)
 try:call('GEN3_SPIN_SELECT',dict(source=bad,ports=c['ports'],decomposition={k:c[k] for k in ('blocks','bridges')},joint=True),'Reject an omitted interaction rather than silently factor it away')
 except (ValueError,AssertionError):checks['undeclared_cross_edge_rejected']=True
 else:raise AssertionError('undeclared_cross_edge_rejected')
 for name,req in [('float_field',dict(result_ref=r['result_ref'],uniform_field=0.5)),('wrong_boundary',dict(result_ref=r['result_ref'],uniform_field='0',boundary=[True,None]))]:
  try:call('GEN3_SPIN_READOUT',req,'Reject an inexact or incorrectly typed readout input')
  except ValueError:checks[name+'_rejected']=True
  else:raise AssertionError(name)
 request=dict(operation='GEN3_SPIN_READOUT',payload=dict(result_ref=r['result_ref'],uniform_field='1/3',boundary=[None,1]))
 first=call('GEN3_RESULT_APPLY',request,'Cache an exact source/parameter/implementation-bound response')
 second=call('GEN3_RESULT_APPLY',request,'Reuse the same exact response')
 check('native_readout_reuse',not first['reused'] and second['reused'] and second['arithmetic_calls']==0)
 bundle=call('GEN3_RESULT_EXPORT',dict(roots=[r['result_ref']]),'Export complete joint chunk dependency closure')
 save('PORTABLE_BUNDLE.json',bundle)
 s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint joint results and response reuse')
 directory=s.directory
with DomainSession(directory) as s:
 print(s.announcement(),flush=True)
 recovered=s.execute('GEN3_RESULT_APPLY',request,purpose='Recover and reuse the exact response after closing the prior native consumer')
 check('checkpoint_response_reuse',recovered['reused'] and recovered['arithmetic_calls']==0 and recovered['result']==first['result'])
 r=s.execute('GEN3_SPIN_SOLVE',recovery_payload,purpose='Recover a full joint result without any new spin arithmetic')
 check('checkpoint_joint_recovery',r['recomputed'] is False and r['result_ref']==recover_ref)
# The same native capability is reached through each active intended consumer.
for domain in ['ATOM3D','STARBREAKER']:
 with DomainSession.start(domain,objective='Adopt shared exact source/boundary response and portable result reuse',output_root=P/'sessions',receipt_storage='gzip') as s:
  print(s.announcement(),flush=True);sessions.append(str(s.directory))
  s.execute('GEN3_RESULT_IMPORT',dict(bundle=bundle['bundle'],sha256=bundle['sha256']),purpose='Adopt portable joint source and all native dependencies')
  q=s.execute('GEN3_SPIN_READOUT',dict(result_ref=bundle['bundle']['roots'][0],uniform_field='2/3',boundary=[-1,None],include_spectrum=True),purpose='Use imported joint spectrum through this existing domain runtime')
  compare(direct(graph,[6,1],'2/3',boundary=[-1,None]),q['answer'],domain+'_portable')
  known=s.execute('GEN3_SPIN_SOURCE',dict(joint_key='signed_packet_chain_N120_fill_-1'),purpose='Adopt installed exact dense N120 joint data')
  result=s.execute('GEN3_SPIN_READOUT',dict(result_ref=known['result_ref'],uniform_field='1/2',boundary=[1,None,-1,None]),purpose='Read installed complete-source conditional collective response')
  check(domain+'_N120_ground',result['answer']['ground_energy']=='-639' and result['answer']['ground_degeneracy']=='15')
  save(domain+'_INSTALLED_READOUT.json',result)
  s.execute('GEN3_CHECKPOINT',{},purpose='Retain domain adoption of shared exact joint readout')
out=dict(status='PASS',checks=checks,check_count=len(checks),sessions=sessions,gpu=a.gpu)
save('QUALIFICATION.json',out);print(json.dumps(dict(status='PASS',checks=len(checks))),flush=True)
