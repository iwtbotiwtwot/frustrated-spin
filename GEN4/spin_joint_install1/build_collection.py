"""Normalize completed answers and joint data into the existing native object format."""
import sys,json,gzip,hashlib,tarfile,collections,types,importlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import CURRENT_REVISION.engines.SLC.gen3 as package
package.__path__.insert(0,str(P/'package'))
from CURRENT_REVISION.engines.SLC.gen3 import spin_joint as j,spin_exact as x,retained
from CURRENT_REVISION.engines.SLC.gen2.exact import canonical_bytes,digest
machine=types.SimpleNamespace(origins={},dirty={'origins':set()},stats=collections.defaultdict(int))
runtime=types.SimpleNamespace(machine=machine)
objects={};meta=json.loads((R/'CURRENT_REVISION/engines/SLC/gen3/spin_data/CATALOG.json').read_text());sources=json.loads((R/'CURRENT_REVISION/engines/SLC/gen3/spin_data/SOURCES.json').read_text())
provenance=[]
archive=R/'GEN4/spin_gap_97_119_1/completion/spin-gap-97-119-1-complete.tar.gz'
with tarfile.open(archive) as t:
 for n in range(97,120):
  name=f'spin-gap-97-119-1/N{n}/RESULT_BUNDLE.json.gz';raw=t.extractfile(name).read();bundle=json.loads(gzip.decompress(raw));assert digest(bundle['bundle'])==bundle['sha256']
  objects.update(bundle['bundle']['objects']);old=objects[bundle['bundle']['roots'][0]]['value']
  source0=json.load(t.extractfile(f'spin-gap-97-119-1/N{n}/SOURCE.json'))
  source=x.validate_source({k:v for k,v in source0.items() if k!='source_sha256'})
  spectrum=old['answer'];spectrum=dict(spectrum,source_sha256=source['source_sha256'])
  # Preserve both identities: canonical scientific data and installed normalizer.
  val=dict(source=source,spectrum=spectrum,source_custody=dict(archive=str(archive.relative_to(R)),member=name,sha256=hashlib.sha256(raw).hexdigest()),
           archived_source_sha256=source0['source_sha256'],original_result_ref=bundle['bundle']['roots'][0],
           normalization='Retained full scalar and ordered-port spectra; no new arithmetic',claim_type='INHERITED_EXACT_RESULT')
  # Source publication remains a normalization, not a new solve.
  obj=dict(schema=retained.SCHEMA,kind='mathematical_result',source_binding=dict(source_sha256=source['source_sha256'],campaign='spin_gap_97_119_1'),
           value=val,dependencies=[bundle['bundle']['roots'][0]],provenance=dict(origin='RETAINED_CANONICAL_NORMALIZATION',original_source_sha256=source0['source_sha256']))
  retained.validate(obj);ref=digest(obj);objects[ref]=obj
  # Pure format/closure check. Historical solver results are not recomputed.
  x.canonical_retained(val)
  default=str(n) not in meta['entries']
  if default:meta['entries'][str(n)]=ref
  sources['sources'].append(dict(N=n,family=source['family'],source_sha256=source['source_sha256'],result_ref=ref,default_for_N=default,
       output_availability=spectrum.get('output_availability',dict(scalar_dos=True,closed_port_rows=True,open_y_operator=True))))
meta['sizes']=sorted(map(int,meta['entries']));assert meta['sizes']==list(range(1,121))
sources.update(source_count=len(sources['sources']),default_size_count=120)
joints={}
for folder in sorted((R/'GEN4/frustrated_spin_joint_readout1/examples/joint').iterdir()):
 if not folder.is_dir():continue
 manifest=json.loads((folder/'MANIFEST.json').read_text());family=folder.name[len('production_'):].split('_N')[0]
 parent=j.source_recipe(dict(family=family,N=120));source=j.full_source(parent['source'],manifest['fill_coupling']);ports=manifest['ordered_ports']
 assert parent['source']['source_sha256']==manifest['source_identity']['parent_source_sha256']
 # Authenticate original graph bits reconstructed from the exact explicit couplings.
 bits=bytearray((120*119//2+7)//8)
 for k,(u,v,w) in enumerate(source['edges']):
  if w==1:bits[k//8]|=1<<(k%8)
 assert hashlib.sha256(bits).hexdigest()==manifest['source_identity']['raw_couplings_sha256']
 rows={};chunks=[]
 for shard in manifest['shards']:
  f=folder/shard['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==shard['sha256']
  vals=[(e,m,int(c)) for e,m,c in (json.loads(line) for line in gzip.open(f,'rt'))]
  rows[shard['boundary_state']]=vals;chunks.append(j.chunk(runtime,vals,source,ports,shard['boundary_state']))
 answer=j.verify_rows(source,ports,rows)
 joint=dict(schema=j.SCHEMA,N=120,ports=ports,source_sha256=source['source_sha256'],rows=chunks,verification=manifest['verification'])
 value=dict(operation='GEN3_SPIN_SOLVE',status='EXACT',source=source,answer=answer,joint=joint,
            acquisition='INHERITED_VERIFIED_JOINT_RESULT',original_source_identity=manifest['source_identity'],
            provenance=dict(manifest_sha256=hashlib.sha256((folder/'MANIFEST.json').read_bytes()).hexdigest(),project='frustrated_spin_joint_readout1'))
 ref=j.keep(runtime,value,dict(capability=j.VERSION,source_sha256=source['source_sha256'],ordered_ports=ports,acquisition='INHERITED_VERIFIED_JOINT_RESULT'),[v['result_ref'] for v in chunks])
 key=f"{family}_N120_fill_{manifest['fill_coupling']:+d}"
 joints[key]=dict(result_ref=ref,N=120,family=family,fill_coupling=manifest['fill_coupling'],source_sha256=source['source_sha256'],ordered_ports=ports)
objects.update({key[len(retained.PREFIX):]:obj for key,obj in machine.origins.items()})
for ref,obj in objects.items():retained.validate(obj);assert digest(obj)==ref
catalog=dict(schema=j.VERSION,canonical_defaults=120,source_records=len(sources['sources']),
 packet_recipes=dict(families=list(j.FAMILIES),N_min=1,N_max=1408,canonical_replacement=False,coverage='Completed exact packet spectra in separately preserved campaigns'),
 dense_sources=dict(families=list(j.FAMILIES),fills=[-1,1],N_min=1,N_max=1408,source_count=8448,status='FULL_GRAPH_SOURCES_GENERATED',dense_DOS_coverage='Only explicitly retained/executed results; source coverage is not DOS coverage'),
 retained_joint_results=joints,method_contract='Method and backend follow the source/decomposition and requested observables',
 provenance=dict(packet='frustrated_spin_packet_catalog1;frustrated_spin_workstation1',dense='frustrated_spin_dense_extension1',joint='frustrated_spin_joint_readout1'))
for name,value in [('CATALOG.json',meta),('SOURCES.json',sources),('JOINT_CATALOG.json',catalog)]:
 (P/'package/spin_data'/name).write_text(json.dumps(value,indent=2)+'\n')
body=dict(schema='SLC_MATHEMATICAL_BUNDLE_V1',roots=[v['result_ref'] for v in joints.values()],objects=objects,calculations={})
(P/'COLLECTION.json.gz').write_bytes(gzip.compress(canonical_bytes(dict(bundle=body,sha256=digest(body))),mtime=0))
(P/'COLLECTION_BUILD.json').write_text(json.dumps(dict(objects=len(objects),canonical_defaults=120,source_records=len(sources['sources']),joint_datasets=len(joints)),indent=2)+'\n')
print((P/'COLLECTION_BUILD.json').read_text())
