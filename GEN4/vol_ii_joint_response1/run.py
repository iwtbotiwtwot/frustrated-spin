"""Bounded C4 alignment/contact experiment through installed A3D41/SLC.

Sean Brady: originator and conceptual director.
OpenAI ChatGPT and Codex: research collaborators; Codex devised this step.
Independent enumeration below checks new response queries, not the old atlas.
"""
import collections
import hashlib
import itertools
import json
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

P = Path(__file__).resolve().parent
R = P.parents[1]
sys.path.insert(0, str(R))
from SAM_PROJECT.session import DomainSession

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def main():
    started = time.monotonic()
    O = P / 'execution'
    O.mkdir(exist_ok=False)
    inputs = R / 'GEN4/spin_joint_install1/PHASE_ADOPTION_INPUTS.json'
    cases = json.loads(inputs.read_text())
    save(O / 'DESIGN.json', dict(
        timestamp=datetime.now(timezone.utc).isoformat(),
        question='How do alignment and fixing the first contact phase change the complete ground-state response of the two retained C4 sources?',
        scope='One bounded step; two inherited sources, three boundary conditions; no automatic follow-up.',
        input_sha256=hashlib.sha256(inputs.read_bytes()).hexdigest(),
        source='Retained Volume II C4 sources from the installed adoption input',
        transformation='E_spin(h)=E_spin(0)-h*M; H_phase(h)=H_phase(0)-h*sum Re(z)',
        collective_coupling='0',
        boundaries={'FREE': [None]*4, 'Z0_REAL_PLUS': [1,1,None,None], 'Z0_IMAG_PLUS': [1,-1,None,None]},
        design_provenance='Codex technical design under Sean Brady authorization to proceed one step and assess',
        independent_check='64-state direct source enumeration; all ground crossings from pairwise line intersections; full DOS and moments at every crossing and one point per interval',
    ))
    results = []
    calls = 0
    with DomainSession.start('ATOM3D', objective='Exact Volume II alignment response with free and pinned C4 contacts, step 1', output_root=O/'sessions', receipt_storage='gzip') as s:
        print(s.announcement(), flush=True)
        save(O/'SESSION.json', dict(path=str(s.directory), announcement=s.announcement()))
        for case in cases:
            name = ''.join(case['covers']) + '_' + case['rule']
            graph = case['example']['result']['spin_source']
            solved = s.execute('GEN3_SPIN_SOLVE', dict(source=graph, ports=[0,1,2,3], joint=True), purpose='Retain E,M and ordered contacts of the inherited C4 source for new alignment experiments')
            calls += 1
            save(O/(name+'_SOLVE.json'), solved)
            # Independent check and phase witnesses; all main results come from SLC.
            states=[]
            phase={(1,1):'1', (1,-1):'i', (-1,-1):'-1', (-1,1):'-i'}
            for spins in itertools.product((-1,1), repeat=6):
                energy=-sum(j*spins[u]*spins[v] for u,v,j in graph['edges'])-sum(a*b for a,b in zip(graph['fields'],spins))
                states.append(dict(E=energy, M=sum(spins), spins=spins, phases=[phase[spins[k:k+2]] for k in (0,2,4)]))
            for condition, boundary in json.loads((O/'DESIGN.json').read_text())['boundaries'].items():
                valid=[v for v in states if all(b is None or v['spins'][i]==b for i,b in enumerate(boundary))]
                payload=dict(result_ref=solved['result_ref'], boundary=boundary, collective_coupling='0', include_spectrum=True)
                def query(h):
                    nonlocal calls
                    response=s.execute('GEN3_RESULT_APPLY',dict(operation='GEN3_SPIN_READOUT',payload=dict(payload,uniform_field=str(h))),purpose=f'New exact C4 response {name}/{condition}, h={h}; reuse the joint object')
                    calls+=1
                    return response
                base=query(F(0)); a=base['result']['answer']
                crossing=[F(c['field']) for c in a['ground_state_crossing_fields']]
                # Deliberately different crossing algorithm: intersect every pair,
                # then keep only intersections on the global minimum envelope.
                candidate={F(u['E']-v['E'],u['M']-v['M']) for u in valid for v in valid if u['M']!=v['M']}
                independent=[]
                for h in sorted(candidate):
                    ground=min(v['E']-h*v['M'] for v in valid)
                    if len({v['M'] for v in valid if v['E']-h*v['M']==ground})>1:
                        independent.append(h)
                assert crossing==independent, (name,condition,crossing,independent)
                edges=[None]+crossing+[None]
                intervals=[]
                for lo,hi in zip(edges,edges[1:]):
                    h=(lo+hi)/2 if lo is not None and hi is not None else hi-1 if hi is not None else lo+1 if lo is not None else F(0)
                    intervals.append(dict(lower=str(lo) if lo is not None else '-infinity',upper=str(hi) if hi is not None else '+infinity',sample=str(h)))
                points=sorted({F(0),*crossing,*(F(v['sample']) for v in intervals)})
                responses=[]
                for h in points:
                    response=base if h==0 else query(h)
                    answer=response['result']['answer']
                    density=collections.Counter(v['E']-h*v['M'] for v in valid)
                    ground=min(density)
                    winners=[v for v in valid if v['E']-h*v['M']==ground]
                    gm=collections.Counter(v['M'] for v in winners)
                    assert answer['density']==[[str(e),str(c)] for e,c in sorted(density.items())]
                    assert F(answer['ground_energy'])==ground and int(answer['ground_degeneracy'])==len(winners)
                    assert {int(k):int(v) for k,v in answer['ground_magnetization_counts'].items()}==dict(gm)
                    assert int(answer['configuration_count'])==len(valid)
                    assert F(answer['energy_sum'])==sum(e*c for e,c in density.items())
                    assert F(answer['energy_square_sum'])==sum(e*e*c for e,c in density.items())
                    assert F(answer['energy_magnetization_sum'])==sum((v['E']-h*v['M'])*v['M'] for v in valid)
                    assert int(answer['magnetization_sum'])==sum(v['M'] for v in valid)
                    assert int(answer['magnetization_square_sum'])==sum(v['M']**2 for v in valid)
                    responses.append(dict(field=str(h),native=response,ground_phase_witnesses=[v['phases'] for v in winners],independent_check='PASS'))
                for interval in intervals:
                    row=next(v for v in responses if v['field']==interval['sample'])
                    interval['ground_M_counts']=row['native']['result']['answer']['ground_magnetization_counts']
                    interval['ground_phase_witnesses']=row['ground_phase_witnesses']
                result=dict(source=name,source_sha256=solved['source']['source_sha256'],condition=condition,boundary=boundary,
                    configuration_count=len(valid),crossings=a['ground_state_crossing_fields'],intervals=intervals,responses=responses)
                save(O/(name+'_'+condition+'.json'),result)
                results.append(result)
                print(json.dumps(dict(source=name,condition=condition,crossings=result['crossings'],checks=len(points))),flush=True)
        s.execute('GEN3_CHECKPOINT',{},purpose='Preserve bounded Volume II step 1 and all source/response dependencies')
        calls+=1
    save(O/'RESULTS.json',results)
    save(O/'STATUS.json',dict(status='COMPLETE',native_calls=calls,source_solves=2,response_curves=6,
        independently_checked_points=sum(len(r['responses']) for r in results),seconds=time.monotonic()-started,
        session=str(s.directory),followup_started=False))
    print((O/'STATUS.json').read_text(),flush=True)

if __name__=='__main__':
    main()
