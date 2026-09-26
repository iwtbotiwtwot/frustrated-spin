"""Publish completed focused costs and best measured source-bound plans."""
import gzip,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import metadata
from CURRENT_REVISION.engines.SLC.gen3.retained import digest
D=P.parent/'frustrated_spin_focused_training1'
folders=dict(retained=D/'focused-results/ram',batched=D/'fast-results/ram',boundary_retained=D/'boundary-results/ram',boundary=D/'boundary-fast-results/ram')
def read(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
meta=metadata();focused=dict(schema='GEN3_GEN4_FOCUSED_SPIN_V1',sources={},cost_models={},hardware='GEN4 pod: fourteen Blackwell MIG1g.24gb, CPU preparation/readout, warm worker pool',boundary_experience_ref=None,boundary_models={},readout='Exact batched NumPy int64 inverse NTT; precomputed Python integer CRT; qualified for retained primes and powers of two',readout_source_sha256=__import__('hashlib').sha256((D/'fast_readout.py').read_bytes()).hexdigest());roots=[];models={}
with DomainSession.start('MATTER_SEARCH',objective='Install completed focused execution-cost learning and best measured plans',output_root=P/'publication',receipt_storage='gzip') as s:
 print(s.announcement(),s.directory,flush=True)
 for label,folder in folders.items():
  assert (folder/'COMPLETE.json').exists();bundle=read(folder/'TRAINING_BUNDLE.json.gz');s.execute('GEN3_RESULT_IMPORT',{k:bundle[k] for k in ['bundle','sha256']},purpose='Adopt exact portable focused learning closure');ref=bundle['bundle']['roots'][0];roots.append(ref);meta['training_experience_refs']['focused_'+label]=ref
  if label.startswith('boundary'):
   focused['boundary_models'][label]=dict(experience_ref=ref)
   if label=='boundary':focused['boundary_experience_ref']=ref
   continue
  focused['cost_models'][label]=dict(experience_ref=ref);fit=read(folder/'FROZEN_MODELS.json');record=fit['pairwise']['export']['record'];models[record['name']]=record
 focused['experience_ref']=focused['cost_models']['batched']['experience_ref']
 fast=folders['batched'];specs=read(fast/'SPECIFICATIONS.json');groups=read(fast/'GROUPED_EXPERIENCE.json');exact=read(fast/'EXACT_SPECTRA.json.gz')
 for gid in sorted({g['group'] for g in groups}):
  best=min([g for g in groups if g['group']==gid],key=lambda g:g['total_ns']);spec=specs[best['case']];source=spec['source'];answer=exact[gid]
  value=dict(source=source,plan=spec['plan'],best_median_ns=best['total_ns'],method=best['method'],source_group=gid,backend='BATCHED_EXACT_NTT_PRECOMPUTED_CRT_V1',timings=[g for g in groups if g['group']==gid],spectrum_sha256=answer['spectrum_sha256'],preparation_time_excluded=True)
  pub=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=value,source_binding=dict(campaign='GEN4_SPIN_FOCUSED_FAST1',source_sha256=source['source_sha256'],N=source['N']),provenance=dict(training_session=read(fast/'COMPLETE.json').get('session'),qualification='Three exact fresh solves per plan; full source DOS and all port operators agree'),dependencies=[focused['experience_ref']]),purpose='Retain best measured exact plan for this identical source without repeating the expensive search')
  focused['sources'][source['source_sha256']]=dict(N=source['N'],group=gid,result_ref=pub['result_ref']);roots.append(pub['result_ref'])
 frontier=P.parent/'frustrated_spin_n120_frontier1/results/ram'
 if (frontier/'COMPLETE.json').exists():
  bundle=read(frontier/'RESULT_BUNDLE.json.gz');s.execute('GEN3_RESULT_IMPORT',{k:bundle[k] for k in ['bundle','sha256']},purpose='Adopt completed exact N120 frontier result');frontier_ref=bundle['bundle']['roots'][0];roots.append(frontier_ref)
  source=read(frontier/'SOURCE.json');p=read(frontier/'PLAN.json');r=read(frontier/'RESULT1.json.gz');assert r['status']=='EXACT';answer=r['answer']
  value=dict(source=source,spectrum=answer,plan=p,source_group='FRONTIER-N120',method='source_bound_cutset_search',measurement_kind='single_exact_execution',measured_execution_ns=r['execution']['total_ns'],spectrum_sha256=answer['spectrum_sha256'],execution=r['execution'])
  pub=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=value,source_binding=dict(campaign='GEN4_N120_FRONTIER1',N=120,source_sha256=source['source_sha256']),provenance=dict(session=read(frontier/'COMPLETE.json')['session'],backend=r['execution']['backend']),dependencies=[frontier_ref]),purpose='Add exact N120 frontier source, plan and full retained port spectrum to the catalog')
  ref=pub['result_ref'];roots.append(ref);meta['entries']['120']=ref;meta['sizes']=sorted(set(meta['sizes']+[120]));meta['frontier_sizes']=[120];meta['frontier_source_family']=source['family'];focused['sources'][source['source_sha256']]=dict(N=120,group='FRONTIER-N120',result_ref=ref)
  previous=s.execute('GEN3_SPIN_ENTRY',dict(N=96),purpose='Bind the executed N96 to N120 transition to its installed parent source');assert previous['source']['source_sha256']==source['parent_source_sha256']
  def edges(q):return {tuple(sorted((q['parent_vertices'][u],q['parent_vertices'][v])))+(j,) for u,v,j in q['edges']}
  old=previous['source'];added=edges(source)-edges(old);removed=edges(old)-edges(source);boundary=sorted({v for e in added|removed for v in e[:2] if v in set(old['parent_vertices'])})
  transition=dict(from_N=96,to_N=120,from_source=old['source_sha256'],to_source=source['source_sha256'],added_parent_vertices=list(range(96,120)),added_parent_edges=[list(e) for e in sorted(added)],removed_parent_edges=[list(e) for e in sorted(removed)],previous_boundary_touched=boundary,retained_boundary_sufficient=set(boundary)<=set(previous['spectrum']['parent_port_vertices']),next_plan=p['selected'],execution=r['execution'],source_construction=source['construction'],learning_boundary='One measured frontier execution; reusable exact plan and transition, not a fitted frontier timing model')
  pub=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=transition,source_binding=dict(campaign='GEN4_N120_FRONTIER1',from_N=96,to_N=120),provenance=dict(session=read(frontier/'COMPLETE.json')['session']),dependencies=[previous['result_ref'],ref]),purpose='Retain the changed-boundary transition and exact N120 execution for future planning');meta['transitions']['96->120']=pub['result_ref'];roots.append(pub['result_ref'])
 bundle=s.execute('GEN3_RESULT_EXPORT',dict(roots=roots),purpose='Export installed focused models and source-plan cache')
 with gzip.open(P/'BUNDLE.json.gz','wt') as f:json.dump(bundle,f,sort_keys=True,separators=(',',':'))
 s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint focused learning publication')
meta['models'].update({name:dict(source_binding=row['source_binding'],model_sha256=digest(row),feature_count=row['model']['feature_count']) for name,row in models.items()});meta['focused']=dict(metadata_path='spin_data/FOCUSED.json',sources=len(focused['sources']),exact_plan_cache=True,cost_backend='source-bound NumPy CPU regression');meta['learning_note']+=' Focused timing/pairwise learning and identical-source plan reuse are installed; GEN3_SPIN_FOCUSED and GEN3_SPIN_COST expose the qualified hardware scope.'
for name,value in [('CATALOG.json',meta),('FOCUSED.json',focused),('MODELS.json',models)]: (P/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(plan_sources=len(focused['sources']),native_models=len(models),portable_objects=bundle['object_count'])))
