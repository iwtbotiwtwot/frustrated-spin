"""One bounded collective-coupling follow-up through installed A3D41/SLC.
Sean Brady: originator/conceptual director. ChatGPT and Codex: collaborators.
Codex technical design; independent enumeration checks new native readouts.
"""
import collections
import hashlib
import itertools
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone

P=Path(__file__).resolve().parent
R=P.parents[1]
sys.path.insert(0,str(R))
from SAM_PROJECT.session import DomainSession

def save(p,v): p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    started=time.monotonic();O=P/'execution';O.mkdir(exist_ok=False)
    sourcefile=R/'GEN4/spin_joint_install1/PHASE_ADOPTION_INPUTS.json'
    graph=next(r for r in json.loads(sourcefile.read_text()) if r['rule']=='COMMON_PIVOT')['example']['result']['spin_source']
    save(O/'DESIGN.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),
        question='For 444/z0=i, where does collective coupling preserve or replace the M=-2 to M=2 transition at h=1?',
        prior='GEN4/vol_ii_joint_response1/REPORT.md',source_input_sha256=hashlib.sha256(sourcefile.read_bytes()).hexdigest(),
        source=graph,boundary=[1,-1,None,None],energy='E(h,g)=E0-h*M-g*(M*M-6)/2',
        prediction='The pairwise M=-2/+2 crossing stays at h=1; global minimality is to be determined.',
        design='Extract all five sector minima through native fixed-M readout; derive exact g envelope at h=1; native readouts at every g breakpoint and every open g interval, and all returned h transitions and intervening intervals.',
        provenance='Codex technical design; Sean authorized this next bounded experiment.',followup_started=False))
    # Independent finite-state check and phase witnesses.
    phase={(1,1):'1',(1,-1):'i',(-1,-1):'-1',(-1,1):'-i'}
    states=[]
    for tail in itertools.product((-1,1),repeat=4):
        spins=(1,-1)+tail
        e=-sum(j*spins[u]*spins[v] for u,v,j in graph['edges'])-sum(a*b for a,b in zip(graph['fields'],spins))
        states.append(dict(E=e,M=sum(spins),phases=[phase[spins[i:i+2]] for i in (0,2,4)]))
    calls=0;checked=0;responses=[];sectors=[]
    with DomainSession.start('ATOM3D',objective='Bounded collective-coupling stability of the 444 imaginary-contact alignment transition',output_root=O/'sessions',receipt_storage='gzip') as s:
        print(s.announcement(),flush=True)
        save(O/'SESSION.json',dict(path=str(s.directory),announcement=s.announcement()))
        solved=s.execute('GEN3_SPIN_SOLVE',dict(source=graph,ports=[0,1,2,3],joint=True),purpose='Bind the inherited 444 source once in a new additive session for collective-coupling response reuse');calls+=1
        save(O/'SOLVE.json',solved)
        def query(h,g,m=None):
            nonlocal calls,checked
            payload=dict(result_ref=solved['result_ref'],boundary=[1,-1,None,None],uniform_field=str(h),collective_coupling=str(g),include_spectrum=True)
            if m is not None:payload['magnetization']=m
            response=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=payload),purpose=f'Exact collective-response query h={h},g={g},fixed_M={m}');calls+=1
            a=response['result']['answer'];valid=[v for v in states if m is None or v['M']==m]
            energy=lambda v:F(v['E'])-h*v['M']-g*F(v['M']**2-6,2)
            density=collections.Counter(energy(v) for v in valid);ground=min(density)
            winners=[v for v in valid if energy(v)==ground]
            assert a['density']==[[str(e),str(c)] for e,c in sorted(density.items())]
            assert F(a['ground_energy'])==ground and int(a['ground_degeneracy'])==len(winners)
            assert {int(k):int(c) for k,c in a['ground_magnetization_counts'].items()}==dict(collections.Counter(v['M'] for v in winners))
            assert int(a['configuration_count'])==len(valid)
            for key,value in [('energy_sum',sum(energy(v) for v in valid)),('energy_square_sum',sum(energy(v)**2 for v in valid)),('magnetization_sum',sum(v['M'] for v in valid)),('magnetization_square_sum',sum(v['M']**2 for v in valid)),('energy_magnetization_sum',sum(energy(v)*v['M'] for v in valid))]:
                assert F(a[key])==value,key
            # Independent pair-intersection calculation of every h crossing.
            base=lambda v:F(v['E'])-g*F(v['M']**2-6,2)
            candidates={F(base(u)-base(v),u['M']-v['M']) for u in valid for v in valid if u['M']!=v['M']}
            cross=[]
            for q in sorted(candidates):
                level=min(base(v)-q*v['M'] for v in valid)
                if len({v['M'] for v in valid if base(v)-q*v['M']==level})>1:cross.append(q)
            assert list(map(lambda v:F(v['field']),a['ground_state_crossing_fields']))==cross
            checked+=1
            result=dict(h=str(h),g=str(g),fixed_M=m,native=response,ground_phase_witnesses=[v['phases'] for v in winners],independent_check='PASS')
            responses.append(result)
            return result
        for m in range(-4,5,2):
            row=query(F(0),F(0),m);a=row['native']['result']['answer']
            sectors.append(dict(M=m,E0=a['ground_energy'],degeneracy=a['ground_degeneracy'],
                g_coefficient=str(-F(m*m-6,2)),h_coefficient=-m,phases=row['ground_phase_witnesses']))
        save(O/'SECTORS.json',sectors)
        # Symbolic reduction from native sector minima: five exact affine planes.
        line=lambda v,g:F(v['E0'])-v['M']+g*F(v['g_coefficient'])
        cand=set()
        for u,v in itertools.combinations(sectors,2):
            if u['g_coefficient']!=v['g_coefficient']:
                cand.add(F(F(v['E0'])-v['M']-F(u['E0'])+u['M'],F(u['g_coefficient'])-F(v['g_coefficient'])))
        breaks=[]
        for g in sorted(cand):
            level=min(line(v,g) for v in sectors);winning=[v for v in sectors if line(v,g)==level]
            if len({v['g_coefficient'] for v in winning})>1:breaks.append(g)
        edges=[None]+breaks+[None];samples={F(0),*breaks};intervals=[]
        for lo,hi in zip(edges,edges[1:]):
            g=(lo+hi)/2 if lo is not None and hi is not None else hi-1 if hi is not None else lo+1 if lo is not None else F(0)
            samples.add(g);intervals.append(dict(lower=str(lo) if lo is not None else '-infinity',upper=str(hi) if hi is not None else '+infinity',sample=str(g)))
        curves=[]
        for g in sorted(samples):
            row=query(F(1),g);a=row['native']['result']['answer']
            crossings=[F(v['field']) for v in a['ground_state_crossing_fields']]
            hs=set(crossings);hedges=[None]+crossings+[None]
            for lo,hi in zip(hedges,hedges[1:]):
                hs.add((lo+hi)/2 if lo is not None and hi is not None else hi-1 if hi is not None else lo+1 if lo is not None else F(0))
            for h in sorted(hs-{F(1)}):query(h,g)
            curves.append(dict(g=str(g),ground_at_h1=a['ground_magnetization_counts'],crossings=a['ground_state_crossing_fields']))
            print(json.dumps(curves[-1]),flush=True)
        save(O/'ANALYTIC_REDUCTION.json',dict(sectors=sectors,h1_g_breakpoints=list(map(str,breaks)),h1_g_intervals=intervals,curves=curves,
            derivation='At fixed M, field and collective shifts are constants. Exact minima E0(M) therefore suffice for all ground-state questions; full DOS remains in the retained joint result. Compare the five affine planes exactly.',
            inequality_template='Sector m is minimal iff E0(m)-E0(k)-h*(m-k)-g*(m*m-k*k)/2 <= 0 for every accessible sector k.'))
        save(O/'RESPONSES.json',responses)
        s.execute('GEN3_CHECKPOINT',{},purpose='Save completed collective-coupling step, exact sector profiles and response dependencies');calls+=1
    save(O/'STATUS.json',dict(status='COMPLETE',seconds=time.monotonic()-started,native_calls=calls,source_solves=1,
        independently_checked_points=checked,g_slices=len(curves),source_sha256=solved['source']['source_sha256'],session=str(s.directory),followup_started=False))
    print((O/'SECTORS.json').read_text(),flush=True);print((O/'STATUS.json').read_text(),flush=True)

if __name__=='__main__':main()
