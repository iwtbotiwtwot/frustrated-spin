"""Publish three completed GEN4 training campaigns as native portable inputs."""
import gzip,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import metadata
from CURRENT_REVISION.engines.SLC.gen3.retained import digest
folders={k:P.parent/n/'results/ram' for k,n in [('ladder','frustrated_spin_training1'),('small','frustrated_spin_n1_30_training1'),('full96','frustrated_spin_full96_training1')]}
def read(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
f=folders['full96'];sources=read(f/'SOURCES.json');spectra=read(f/'EXACT_SPECTRA.json.gz');specs=read(f/'SPECIFICATIONS.json');groups=read(f/'GROUPED_EXPERIENCE.json');smallgroups=read(folders['small']/'GROUPED_EXPERIENCE.json')
meta=metadata();meta['original_sizes']=meta['sizes'].copy();meta['training_sizes']=list(range(1,97));meta['sizes']=list(range(1,97));meta['training_experience_refs']={};models={}
for key,folder in folders.items():
    records=read(folder/('FROZEN_POLICIES.json' if key=='ladder' else 'FROZEN_MODELS.json'))
    if key=='ladder':records=records['fits']
    for family,v in records.items():
        row=v['export' if key=='ladder' else 'model']['record'];models[row['name']]=row
meta['models']={name:dict(source_binding=row['source_binding'],model_sha256=digest(row),feature_count=row['model']['feature_count']) for name,row in models.items()}
meta.update(native_model='spin-transition-combined-v2',model_role='NATIVE_LEARNED_RANKING_WITH_EXACT_COST_TIE_BREAK',source_family='N96_INDUCED_TRANSITION_LADDER_V1',exact_planner_selects_execution=False)
meta['active_model_binding']=models[meta['native_model']]['source_binding']
meta['learning_note']='Full96 heads are depth zero: reserved 16/16 choices are structural cost tie-breaks. Prior ladder depth-one head remains the ranking policy; all nine new heads retained.'
roots=[]
with DomainSession.start('MATTER_SEARCH',objective='Publish completed GEN4 all-integer transition learning for installed reuse',output_root=P/'publication',receipt_storage='gzip') as session:
    print(session.announcement(),str(session.directory),flush=True)
    for label,folder in folders.items():
        bundle=read(folder/'TRAINING_BUNDLE.json.gz');session.execute('GEN3_RESULT_IMPORT',{k:bundle[k] for k in ['bundle','sha256']},purpose='Adopt the completed source-bound GEN4 training closure')
        ref=bundle['bundle']['roots'][0];roots.append(ref);meta['training_experience_refs'][label]=ref
    bestplans={n:min((g for g in groups if g['N']==n),key=lambda g:g['median_ns']) for n in range(1,97)}
    for source in sources:
        n=source['N'];p=specs[bestplans[n]['case']]['plan'];answer=spectra[str(n)]
        if str(n) in meta['entries']:
            old=session.execute('GEN3_SPIN_ENTRY',dict(N=n,source_sha256=source['source_sha256']),purpose='Reuse identical installed source when catalog rosters overlap');assert old['spectrum']['scalar_dos']==answer['scalar_dos'];continue
        r=session.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=dict(source=source,spectrum=answer,plan=p),source_binding=dict(catalog='GEN4_SPIN_FULL96_TRAINING1',N=n,source_sha256=source['source_sha256']),provenance=dict(session=read(f/'COMPLETE.json')['session'],operation='GEN4_SPIN_FULL96_SOLVE'),dependencies=[meta['training_experience_refs']['full96']]),purpose='Publish fresh exact integer-size spectrum and retained port operators')
        meta['entries'][str(n)]=r['result_ref'];roots.append(r['result_ref'])
    for n in range(2,97):
        previous,current=sources[n-2:n];old=set(previous['parent_vertices'])
        def edges(s):return {tuple(sorted((s['parent_vertices'][u],s['parent_vertices'][v])))+(j,) for u,v,j in s['edges']}
        added=sorted(edges(current)-edges(previous));boundary=sorted({v for e in added for v in e[:2] if v in old});observations=[g for g in groups if g['N']==n]
        transition=dict(from_N=n-1,to_N=n,from_source=previous['source_sha256'],to_source=current['source_sha256'],added_parent_vertices=sorted(set(current['parent_vertices'])-old),added_parent_edges=[list(e) for e in added],removed_edges=[],previous_boundary_touched=boundary,retained_boundary_sufficient=set(boundary)<=set(previous['parent_vertices'][:4]),previous_plan=specs[bestplans[n-1]['case']]['plan']['selected'],next_plan=specs[bestplans[n]['case']]['plan']['selected'],execution=observations,best_observed_method=bestplans[n]['method'])
        if n<=30:transition.update(incremental_experience=[g for g in smallgroups if g['N']==n],incremental_condition='Requires exact future-facing state for the declared N30 horizon; scalar spectra alone are insufficient')
        r=session.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=transition,source_binding=dict(catalog='GEN4_SPIN_FULL96_TRAINING1',from_N=n-1,to_N=n),provenance=dict(session=read(f/'COMPLETE.json')['session']),dependencies=[meta['entries'][str(n-1)],meta['entries'][str(n)],*meta['training_experience_refs'].values()]),purpose='Retain measured adjacent-integer transition and the methods compared')
        meta['transitions'][f'{n-1}->{n}']=r['result_ref'];roots.append(r['result_ref'])
    bundle=session.execute('GEN3_RESULT_EXPORT',dict(roots=roots),purpose='Export new catalog and learning dependency closure')
    with gzip.open(P/'BUNDLE.json.gz','wt') as out:json.dump(bundle,out,sort_keys=True,separators=(',',':'))
    session.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint catalog publication')
(P/'CATALOG.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n');(P/'MODELS.json').write_text(json.dumps(models,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(entries=len(meta['entries']),transitions=len(meta['transitions']),models=len(models),portable_objects=bundle['object_count'])))
