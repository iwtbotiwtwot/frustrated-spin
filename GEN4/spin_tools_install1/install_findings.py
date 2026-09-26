"""Register completed tool findings and the owner's MP shelving in the web."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from loop import Web,digest,save
w=Web(ROOT);root_hash=digest(w.meta('root_problem'));refs=[]
files=['RESULT.md','FINDINGS.md','SOURCE_SUMMARY.md','VERIFICATION.json','PACKAGE_MANIFEST_FINAL.json','CONCLUSIONS.json','AUTHORITY.json']
for f in [P/n for n in files]+sorted((P/'authority_after').glob('*.md')):
 rel=str(f.relative_to(ROOT/'sources'));raw=f.read_bytes();h=hashlib.sha256(raw).hexdigest()
 with w.db:
  old=w.db.execute('SELECT sha256 FROM source_documents WHERE path=?',(rel,)).fetchone()
  if old and old[0]!=h:raise ValueError('Published source changed '+rel)
  if not old:
   w.db.execute('INSERT INTO source_documents VALUES(?,?,?)',(rel,h,len(raw)))
   w.db.execute('INSERT INTO documents(path,body) VALUES(?,?)',(rel,raw.decode()))
  w.db.execute('INSERT OR IGNORE INTO research_nodes VALUES(?,?,?,?,?)',(rel,'spin_tools_install1','SOURCE','INSTALLED',rel))
 refs.append(w.read_source(rel)['read_id'])
observed=['SPIN_TOOLS_ADOPT_'+n for n in ['CAPABILITIES','N100','N105','N120_READOUT','SIGNED_FACTORS']]
t=dict(id='SPIN_TOOLS_FINDINGS_INSTALL',root_sha256=root_hash,mode='TARGETED',objective_ids=['vol_ii_matter','vol_i_clock','sphere_transport','rh'],sources_read=refs,observed_results=observed,synthesis='Install complete spin source knowledge, executable exact methods, native plan inference and shared signed-factor capabilities for source-specific use across the program.',alternatives=[{'idea':'Retain conditional response channels and reuse boundary-supported shifts in a future source-mapped extension.'}],proposals=[],method_needs=[],conclusions=json.loads((P/'CONCLUSIONS.json').read_text()),next_decision='Use the installed shared tools for explicitly declared research inputs; preserve the shelved MP work for owner-directed resumption.')
save(P/'FINDINGS_TURN.json',t);print(json.dumps(w.submit(t)))
with w.db:
 before=[]
 for ident in ['mp_arithmetic','sphere_mp']:
  row=w.db.execute('SELECT payload FROM research_objectives WHERE id=?',(ident,)).fetchone();v=json.loads(row[0]);before.append(v.copy());v.update(status='SHELVED_BY_OWNER',resume_requires_owner_direction=True,authority=json.loads((P/'AUTHORITY.json').read_text())['entry'])
  w.db.execute('UPDATE research_objectives SET payload=? WHERE id=?',(json.dumps(v,sort_keys=True),ident))
 save(P/'MP_OBJECTIVES_BEFORE_SHELVING.json',before)
 old=w.meta('shared_spin_tools');old.update(state='INSTALLED_EXECUTED_AND_REPORTED',report='GEN4/spin_tools_install1/RESULT.md',authority=json.loads((P/'AUTHORITY.json').read_text())['entry'],qualification={'GEN3':139,'GEN4':143},native_adoption_calls=5,checkpoints=5)
 w.set('shared_spin_tools',old)
assert digest(w.meta('root_problem'))==root_hash
status=w.status();save(P/'STATUS_AFTER.json',status)
v=dict(status='INSTALLED',report_sha256=hashlib.sha256((P/'RESULT.md').read_bytes()).hexdigest(),native_results=status['native_results'],conclusions=status['conclusions'],pending=w.db.execute('SELECT count(*) FROM proposals WHERE status="PENDING"').fetchone()[0],root_preserved=True,mp_shelved=[v['id'] for v in status['objectives'] if v['status']=='SHELVED_BY_OWNER'])
save(P/'REPORT_INSTALL.json',v);print(json.dumps(v));w.close()
