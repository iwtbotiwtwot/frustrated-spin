"""Adopt installed shared tools in the existing research web; preserve prior work."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from loop import Web,digest,save
w=Web(ROOT);refs=[]
if not (P/'WEB_BEFORE.json').exists():save(P/'WEB_BEFORE.json',w.status())
root_hash=digest(w.meta('root_problem'))
for name in ['ROOT_PROBLEM.json','OBJECTIVES.json']:
 refs.append(w.read_source(name)['read_id'])
for name in ['GUIDE.md','CAPABILITY_MAP.md','SOURCES.json','SOURCES_METHOD.md','EXACT_METHOD.md','GPU_METHOD.md','SELECT_METHOD.md']:
 f=P/name;rel=str(f.relative_to(ROOT/'sources'));raw=f.read_bytes();h=hashlib.sha256(raw).hexdigest()
 with w.db:
  old=w.db.execute('SELECT sha256 FROM source_documents WHERE path=?',(rel,)).fetchone()
  if old and old[0]!=h:raise ValueError('Published tool source changed '+rel)
  if not old:
   w.db.execute('INSERT INTO source_documents VALUES(?,?,?)',(rel,h,len(raw)))
   w.db.execute('INSERT INTO documents(path,body) VALUES(?,?)',(rel,raw.decode()))
  w.db.execute('INSERT OR IGNORE INTO research_nodes VALUES(?,?,?,?,?)',(rel,'spin_tools_install1','CAPABILITY_SOURCE','INSTALLED',rel))
 refs.append(w.read_source(rel)['read_id'])
contract=dict(variables=[dict(name='x',domain=[-1,1]),dict(name='y',domain=[0,1,2])],factors=[dict(scope=['x','y'],table=[2,-3,5,-7,11,-13]),dict(scope=['x'],table=[1,-1])],keep=['y'],source_binding=dict(campaign='SPIN_TOOLS_WEB_ADOPTION',meaning='Synthetic finite signed factors; shared-operation wiring, not an RH hypothesis'))
cases=[('CAPABILITIES','ATOM3D','GEN3_SPIN_TOOLS',{},['vol_ii_matter']),('N100','ATOM3D','GEN3_SPIN_SOURCE',{'N':100},['vol_ii_matter']),('N105','ATOM3D','GEN3_SPIN_SOURCE',{'N':105},['vol_ii_matter']),('N120_READOUT','STARBREAKER','GEN3_SPIN_READOUT',{'N':120},['vol_i_clock','sphere_transport']),('SIGNED_FACTORS','RH','GEN3_SPIN_CONTRACT',contract,['rh'])]
for suffix,domain,operation,payload,objectives in cases:
 ident='SPIN_TOOLS_ADOPT_'+suffix
 if w.db.execute('SELECT 1 FROM native_results WHERE id=?',(ident,)).fetchone():continue
 proposal=dict(id=ident,domain=domain,operation=operation,payload=payload,question='Exercise installed shared exact tools through the existing research-web native route',source_mapping='Use the installed source-family registry or the explicit synthetic signed tables. Operation schema and limits are bound by the installed runtime and supplied tool guide.',root_connection='Supply reusable exact operations for source-specific research while preserving the RH root and existing scientific scopes.',assumptions=['This is capability adoption; no physical source assignment or uniform RH bound is inferred.'],scope='Installed tool retrieval/readout or synthetic finite-factor interface check',expected_return='Exact retained source/readout or signed table[9,-14,18] with complete native receipt',dependencies=[],objective_ids=objectives)
 t=dict(id='TURN_'+ident,root_sha256=root_hash,mode='TARGETED',objective_ids=objectives,sources_read=refs,observed_results=[],synthesis='Make completed spin knowledge and reusable exact algorithms callable from the current web.',alternatives=[dict(idea='Read a completed source or execute a declared finite input through the same source-aware interface.')],proposals=[proposal],method_needs=[],conclusions=[],next_decision='Retain tool adoption results and use the installed capability for explicitly mapped research inputs.')
 save(P/(ident+'_TURN.json'),t);print(json.dumps(w.submit(t)),flush=True)
 r=w.execute(ident);save(P/(ident+'_RETURNED.json'),r);print(json.dumps(dict(returned=ident)),flush=True)
with w.db:
 w.set('shared_spin_tools',dict(state='INSTALLED_AND_EXECUTED',campaign='spin_tools_install1',guide='GEN4/spin_tools_install1/GUIDE.md',source_registry='GEN4/spin_tools_install1/SOURCES.json',default_sizes=list(range(1,97))+[100,105,120],source_count=100,scope='Exact source-aware finite tools; source-to-domain mapping stays explicit',unattended_workers=False))
 w.set('mp_research_direction',dict(state='SHELVED_BY_OWNER',candidate_exponent=224872321,retained_report='GEN4/mp53_prediction1/RESULT.md',automatic_resumption=False))
 for objective in ['vol_ii_matter','vol_i_clock','sphere_transport','rh']:
  w.db.execute('INSERT OR IGNORE INTO research_edges VALUES(?,?,?)',('GEN4/spin_tools_install1/GUIDE.md',objective,'SHARED_EXACT_CAPABILITY_WITH_EXPLICIT_SOURCE_MAP'))
assert digest(w.meta('root_problem'))==root_hash
save(P/'WEB_AFTER_ADOPTION.json',w.status());w.close()
