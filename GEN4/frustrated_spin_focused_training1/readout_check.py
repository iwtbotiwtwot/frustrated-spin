"""Independent exact readout check using retained polynomial coefficients."""
import os,sys,gzip,json,time,statistics
from pathlib import Path
sys.path.insert(0,os.environ['GEN4_SPIN_CATALOG_CODE']);sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
from arithmetic import reconstruct,exact
import fast_readout
from SAM_PROJECT.session import DomainSession
from engine import save

class Check:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op=='GEN4_READOUT_CHECK':
            source,p,answer=payload['source'],payload['plan'],payload['answer'];length=p['root_count'];values=[]
            for prime in p['primes']:
                rows=[]
                for sparse in answer['open_y_operator']:
                    coeff=[0]*length
                    for k,c in sparse:coeff[k]=int(c)%prime
                    # Forward transform via the independent retained inverse transform.
                    row=exact._inverse_ntt(coeff,prime);rows.append([row[(-k)%length]*length%prime for k in range(length)])
                values.append(np.asarray(rows,dtype=np.int64))
            for vals,prime in zip(values,p['primes']):assert fast_readout.batched_inverse_ntt(vals,prime).tolist()==[exact._inverse_ntt(row.tolist(),prime) for row in vals]
            times={'retained':[],'batched':[]}
            for repeat in range(5):
                for label,fn in ([('retained',reconstruct),('batched',fast_readout.reconstruct)] if repeat%2 else [('batched',fast_readout.reconstruct),('retained',reconstruct)]):
                    t=time.perf_counter_ns();result=fn(source,p,values);times[label].append(time.perf_counter_ns()-t)
                    for k in ['scalar_dos','open_y_operator','closed_port_rows','configuration_count','ground_energy','ground_degeneracy','checks']:assert result[k]==answer[k]
            return dict(N=source['N'],source_sha256=source['source_sha256'],exact_match=True,times_ns=times,median_ns={k:int(statistics.median(v)) for k,v in times.items()},qualification='Retained exact polynomial forward transform, independent inverse equality and full readout checks; fresh GPU end-to-end comparison follows')
        return self.base.execute(op,payload)

p=Path('/dev/shm/gen4-spin-full96-training1');out=Path('/dev/shm/gen4-spin-readout-check1');out.mkdir(exist_ok=False)
specs=json.loads((p/'SPECIFICATIONS.json').read_text());groups=json.loads((p/'GROUPED_EXPERIENCE.json').read_text());sources=json.loads((p/'SOURCES.json').read_text())
with DomainSession.start('MATTER_SEARCH',objective='Qualify exact batched readout and invariant CRT reuse against retained reconstruction',output_root=out/'sessions',receipt_storage='gzip') as s:
 s.consumer=Check(s.consumer);results=[]
 for n in [18,30,60,84,91,96]:
  best=min([g for g in groups if g['N']==n],key=lambda g:g['median_ns']);result=json.load(gzip.open(p/f'case{best["case"]:03d}_r1.json.gz'))
  answer=dict(result['answer']);answer['checks'].pop('original_N96_exact_reference',None);answer['checks'].pop('independent_enumeration',None)
  r=s.execute('GEN4_READOUT_CHECK',dict(source=sources[n-1],plan=specs[best['case']]['plan'],answer=answer),purpose='Check optimized inverse transform and CRT against independent retained exact polynomial coefficients');results.append(r);print(json.dumps(r),flush=True)
 save(out/'RESULT.json',results);save(out/'CHECKPOINT.json',s.execute('GEN3_CHECKPOINT',{},purpose='Retain exact readout qualification'))
