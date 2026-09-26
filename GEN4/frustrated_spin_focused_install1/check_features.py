"""Verify lightweight runtime features against executed descriptor features."""
import argparse,json,math,sys,ast
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--specifications',type=Path,required=True);ap.add_argument('--planning-code',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.planning_code))
from planning import plan,digest
p=Path(__file__).resolve().parent;tree=ast.parse((p/'native_focus.py').read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['lg','features']];namespace={'math':math};exec(compile(ast.Module(body=functions,type_ignores=[]),'<feature_wiring_check>','exec'),namespace)
frozen=json.loads((a.planning_code/'parent_plan.json').read_text());specs=json.loads(a.specifications.read_text())
for sp in specs:
 s=sp['source'];prev={k:v for k,v in s.items() if k not in ['source_sha256','N','fields','edges','parent_vertices','energy_bound_B']};n=s['N']-1;prev.update(N=n,fields=s['fields'][:n],edges=[e for e in s['edges'] if e[1]<n],parent_vertices=s['parent_vertices'][:n]);prev['energy_bound_B']=sum(map(abs,prev['fields']))+sum(abs(e[2]) for e in prev['edges']);prev['source_sha256']=digest(prev)
 actual=namespace['features'](s,prev,plan(prev,frozen),sp['plan']);assert actual==sp['features'],(sp['case'],actual,sp['features'])
print(json.dumps(dict(status='PASS',checked_cases=len(specs),meaning='Exact descriptor features reproduced without allocating projection maps')))
