from pathlib import Path
import tarfile,json,gzip,shutil,hashlib,csv
P=Path(__file__).resolve().parent;R=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
a=R/'GEN4/frustrated_spin_focused_training1/restart/runtime-predecessor.tar.gz'
rt=P/'runtime'
if not (rt/'CURRENT_REVISION').exists():
 with tarfile.open(a) as t:
  for m in t.getmembers():
   parts=Path(m.name).parts
   if len(parts)>1:m.name=str(Path(*parts[1:]));t.extract(m,rt,filter='data')
# Isolated vendor package avoids modifying runtime binding sources.
v=P/'vendor';v.mkdir(exist_ok=True);(v/'__init__.py').touch()
origin=R/'CURRENT_REVISION/engines/SLC/gen3'
for f in origin.glob('spin_*.py'):shutil.copy2(f,v/f.name)
shutil.copytree(origin/'spin_data',v/'spin_data',dirs_exist_ok=True)
archives=[a,R/'GEN4/spin_tools_install1/BUNDLE.json.gz',R/'GEN4/spin_gap_97_119_1/completion/spin-gap-97-119-1-complete.tar.gz']
with tarfile.open(archives[-1]) as t:
 for m in t.getmembers():
  if m.isfile() and (m.name.endswith(('SOURCE.json','PLAN.json','COMPLETE.json','RESULT1.json.gz','CATALOG.json','STATUS.json','MANIFEST.json'))):t.extract(m,P/'inputs',filter='data')
b=json.loads(gzip.decompress(archives[1].read_bytes()))['bundle']['objects'];cat=json.loads((origin/'spin_data/CATALOG.json').read_text())
timings={int(r['N']):r for r in csv.DictReader((R/'GEN4/frustrated_spin_timing_review1/TIMINGS.csv').open())}
manifest=[]
for n in range(1,121):
 if n<=96 or n in [100,105,120]:
  ref=cat['entries'][str(n)];v=b[ref]['value'];item=dict(N=n,source=v['source'],plan=v['plan'],spectrum=v['spectrum'],historical=v,provenance=dict(kind='INHERITED',object_ref=ref,input=str(archives[1]),lineage=v['source'].get('family',v.get('source_group'))))
  if n<=96:item['timing']=dict(seconds=float(timings[n]['best_method_median_seconds']),method=timings[n]['best_method'],hardware='14_MIG_GPU_retained_readout',selection='retrospective best method',record=timings[n])
  elif n==120:item['timing']=dict(seconds=v['execution']['total_ns']/1e9,method=v.get('method','branch_group'),hardware='14_MIG_GPU_batched_readout',stages=v['execution'])
  else:
   ts=v['plan'].get('timing',{});runs=ts.get('paired_runs',[])
   import statistics
   vals=[float.fromhex(x['wall_seconds']['float64_hex']) for x in runs if x['N']==n]
   sec=statistics.median(vals) if vals else None
   if sec is None:
    for k,x in ts.items():
     if k=='wall_seconds' and isinstance(x,dict) and 'float64_hex' in x:sec=float.fromhex(x['float64_hex']);break
   item['timing']=dict(seconds=sec,method='components',hardware='historical_CPU',record=ts)
 else:
  d=P/'inputs/spin-gap-97-119-1'/f'N{n}';v=json.loads(gzip.decompress((d/'RESULT1.json.gz').read_bytes()));item=dict(N=n,source=json.loads((d/'SOURCE.json').read_text()),plan=json.loads((d/'PLAN.json').read_text()),spectrum=v['answer'],timing=dict(seconds=v['execution']['total_ns']/1e9,method='inherited_N120_plan',hardware='14_MIG_GPU_batched_readout',stages=v['execution']),provenance=dict(kind='INHERITED',input=str(archives[-1]),lineage='N120_INDUCED_PREFIX_GAP1'))
 save(P/f'canonical/N{n:03d}.json',item);manifest.append(dict(N=n,path=f'canonical/N{n:03d}.json',sha256=sha(P/f'canonical/N{n:03d}.json'),source_sha256=item['source']['source_sha256'],provenance=item['provenance']))
# retain the additional same-N connected N100/N105 families as noncanonical controls
for n in [100,105]:
 d=P/'inputs/spin-gap-97-119-1'/f'N{n}';save(P/f'variants/inherited_gap_N{n}.json',dict(source=json.loads((d/'SOURCE.json').read_text()),plan=json.loads((d/'PLAN.json').read_text()),kind='INHERITED_VARIANT',parent='N120'))
save(P/'ATLAS_MANIFEST.json',dict(canonical_count=120,contiguous=True,rows=manifest,inputs=[dict(path=str(a),sha256=sha(a)) for a in archives],runtime='isolated retained GEN4; additive CPU adapter modules; no registry changes'))
print('BUILT',len(manifest),flush=True)
