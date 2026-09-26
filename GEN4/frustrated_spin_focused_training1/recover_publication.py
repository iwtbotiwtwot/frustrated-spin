"""Complete publication after float64 timing models meet exact-only object schema.

The exact arithmetic and frozen timing evaluation are read from completed files.
Floating-point model parameters are retained losslessly using hex strings.
"""
import argparse,gzip,json,sys,time
from pathlib import Path
sys.path.insert(0,'/opt/gen4/current')
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.retained import digest

def portable(x):
    if isinstance(x,float):return {'__float64_hex__':x.hex()}
    if isinstance(x,dict):return {k:portable(v) for k,v in x.items()}
    if isinstance(x,list):return [portable(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ram',type=Path,required=True);ap.add_argument('--durable',type=Path,required=True);ap.add_argument('--kind',choices=['boundary','gpu'],required=True);a=ap.parse_args();r=a.ram
    failure=json.loads((r/'FAILURE.json').read_text());assert 'Unsupported canonical value: float' in failure['traceback'],failure
    groups=json.loads((r/'GROUPED_EXPERIENCE.json').read_text());evaluation=json.loads((r/'EVALUATION.json').read_text());measurements=json.loads((r/'MEASUREMENTS.json').read_text());model=json.loads((r/('FROZEN_MODEL.json' if a.kind=='boundary' else 'FROZEN_MODELS.json')).read_text())
    sourcefile='FUTURE_SOURCES.json' if a.kind=='boundary' else 'SPECIFICATIONS.json';sources=json.loads((r/sourcefile).read_text());binding=dict(campaign='GEN4_FOCUSED_'+a.kind.upper()+'1',sources_sha256=digest(portable(sources)),encoding='Float64 parameters retained losslessly as __float64_hex__ tagged strings')
    with DomainSession.start('MATTER_SEARCH',objective='Complete lossless publication of already executed focused training',output_root=r/'publication_sessions',receipt_storage='gzip') as s:
        print(s.announcement(),s.directory,flush=True)
        obj=s.execute('GEN3_RESULT_PUBLISH',dict(kind='mathematical_result',value=portable(dict(groups=groups,measurements=measurements,evaluation=evaluation,models=model)),source_binding=binding,provenance=dict(original_session=str(next((r/'sessions').iterdir())),recovery_session=str(s.directory),correction='Encode floating point timing-model parameters losslessly for exact retained object schema; no arithmetic rerun')),purpose='Retain completed timing predictions, exact execution experience and reusable cost models')
        bundle=s.execute('GEN3_RESULT_EXPORT',dict(roots=[obj['result_ref']]),purpose='Export losslessly encoded focused learning')
        with gzip.open(r/'TRAINING_BUNDLE.json.gz','wt') as f:json.dump(bundle,f,sort_keys=True,separators=(',',':'))
        state=s.execute('GEN3_CHECKPOINT',{},purpose='Checkpoint final focused training publication');(r/'PUBLICATION_CHECKPOINT.json').write_text(json.dumps(state,indent=2)+'\n')
        complete=dict(status='COMPLETE_PUBLICATION_RECOVERED',kind=a.kind,measurements=len(measurements),groups=len({g['group'] for g in groups}),experience_ref=obj['result_ref'],original_session=str(next((r/'sessions').iterdir())),publication_session=str(s.directory))
        (r/'COMPLETE.json').write_text(json.dumps(complete,indent=2)+'\n');print(json.dumps(complete),flush=True)
    sys.path.insert(0,'/opt/gen4/spin-catalog1');sys.path.insert(0,'/opt/gen4/spin-focused1')
    from engine import flush
    flush(r,a.durable,'COMPLETE_PUBLICATION_RECOVERED')
if __name__=='__main__':main()
