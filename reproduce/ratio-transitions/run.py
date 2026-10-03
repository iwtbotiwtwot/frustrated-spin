"""Standalone independent replay of the published ratio calculation."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
manifest=json.loads((P/'source/MANIFEST.json').read_text())
for n,h in manifest.items():assert hashlib.sha256((P/'source'/n).read_bytes()).hexdigest()==h,n
if len(sys.argv)>1 and sys.argv[1]=='verify-record':
 print(json.dumps(dict(status='PASS',source_files=len(manifest))));raise SystemExit
with tempfile.TemporaryDirectory(prefix='spin-ratio-replay-') as tmp:
 d=Path(tmp)
 for n in manifest:shutil.copy2(P/'source'/n,d/n)
 for n in ['worker.py','extension.py']:subprocess.run([sys.executable,str(d/n)],check=True)
 actual=json.loads((d/'output/RESULTS.json').read_text());expected=json.loads((R/'research/spin_ratio1/RESULTS.json').read_text())
 for a,b in zip(actual['families'],expected['families']):
  for k in ['family','free_fraction','beta_tricritical','kappa_tricritical','sixth_cumulant','core_cumulants','global_difference','bernstein','jacobian_beta_fraction','enumeration','source_sha256']:assert a[k]==b[k],(a['family'],k)
 ext=json.loads((d/'output/EXTENSION.json').read_text());old=json.loads((R/'research/spin_ratio1/EXTENSION.json').read_text())
 for a,b in zip(ext['families'],old['families']):
  for k in ['family','numerator','denominator','degrees','bernstein']:assert a[k]==b[k],k
 print(json.dumps(dict(status='PASS',main_checks=actual['independent_exact_checks'],extension_coefficients=ext['bernstein_coefficients'],comparison='Exact formulas, source identities, cumulants and polynomial certificates; directed witness signs checked by worker; numerical branches recomputed',seconds=actual['wall_seconds']+ext['wall_seconds']),indent=2))
