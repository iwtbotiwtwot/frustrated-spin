"""Retain final bounded authority formatting and completion records."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from loop import Web,save
w=Web(ROOT)
for f in [P/'AUTHORITY_FINAL.json',P/'HISTORY_VALIDATION.log',P/'RESTORE.md']+sorted((P/'authority_final').glob('*.md')):
 rel=str(f.relative_to(ROOT/'sources'));raw=f.read_bytes();h=hashlib.sha256(raw).hexdigest()
 with w.db:
  old=w.db.execute('SELECT sha256 FROM source_documents WHERE path=?',(rel,)).fetchone()
  if old and old[0]!=h:raise ValueError('Published final record changed '+rel)
  if not old:
   w.db.execute('INSERT INTO source_documents VALUES(?,?,?)',(rel,h,len(raw)));w.db.execute('INSERT INTO documents(path,body) VALUES(?,?)',(rel,raw.decode()))
  w.db.execute('INSERT OR IGNORE INTO research_nodes VALUES(?,?,?,?,?)',(rel,'spin_tools_install1','FINAL_AUTHORITY','INSTALLED',rel))
with w.db:
 v=w.meta('shared_spin_tools');v['final_authority']='GEN4/spin_tools_install1/AUTHORITY_FINAL.json';v['restore_capsule']='/workspace/gen4/runs/spin-tools-install1/RESTORE_CAPSULE.tar.gz';w.set('shared_spin_tools',v)
save(P/'FINAL_STATUS.json',w.status());w.close()
