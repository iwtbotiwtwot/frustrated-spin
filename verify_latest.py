"""Read-only independent checks of the published, already-executed phase results."""
import collections
from fractions import Fraction as F
import itertools
import json
from pathlib import Path

P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def states(graph,boundary):
    for s in itertools.product((-1,1),repeat=graph['N']):
        if any(b is not None and b!=s[i] for i,b in enumerate(boundary)):continue
        yield (-sum(j*s[u]*s[v] for u,v,j in graph['edges'])-sum(h*z for h,z in zip(graph['fields'],s)),sum(s))
def check(graph,boundary,row,h,g,fixed=None):
    values=[(F(e)-h*m-g*F(m*m-graph['N'],2),m) for e,m in states(graph,boundary) if fixed is None or m==fixed]
    counts=collections.Counter(e for e,m in values);ground=min(counts)
    a=row['native']['result']['answer']
    assert a['density']==[[str(e),str(c)] for e,c in sorted(counts.items())]
    assert int(a['configuration_count'])==len(values)
    assert F(a['ground_energy'])==ground and int(a['ground_degeneracy'])==counts[ground]
    assert {int(k):int(v) for k,v in a['ground_magnetization_counts'].items()}==dict(collections.Counter(m for e,m in values if e==ground))
    for key,v in [('energy_sum',sum(e for e,m in values)),('energy_square_sum',sum(e*e for e,m in values)),('magnetization_sum',sum(m for e,m in values)),('magnetization_square_sum',sum(m*m for e,m in values)),('energy_magnetization_sum',sum(e*m for e,m in values))]:assert F(a[key])==v

def main():
    source_rows=load(P/'GEN4/spin_joint_install1/PHASE_ADOPTION_INPUTS.json')
    graphs={''.join(r['covers'])+'_'+r['rule']:r['example']['result']['spin_source'] for r in source_rows}
    checked=0
    for curve in load(P/'GEN4/vol_ii_joint_response1/execution/RESULTS.json'):
        for r in curve['responses']:
            check(graphs[curve['source']],curve['boundary'],r,F(r['field']),F(0));checked+=1
    second=P/'GEN4/vol_ii_joint_response2'
    design=load(second/'execution/DESIGN.json')
    for r in load(second/'execution/RESPONSES.json'):
        check(design['source'],design['boundary'],r,F(r['h']),F(r['g']),r['fixed_M']);checked+=1
    identity=load(second/'SOURCE_IDENTITY.json')
    graph=design['source']
    energy=lambda s:-sum(j*s[u]*s[v] for u,v,j in graph['edges'])-sum(a*b for a,b in zip(graph['fields'],s))
    for record in identity['bijection_checks']:
        s=record['spins'];t=record['image']
        assert t==s[:2]+[-v for v in reversed(s[2:])]
        assert energy(t)==energy(s)-2*sum(s) and sum(t)==-sum(s)
    reduction=load(second/'execution/ANALYTIC_REDUCTION.json')
    assert reduction['h1_g_breakpoints']==['-1','17/3']
    profiles={v['M']:F(v['E0']) for v in reduction['sectors']}
    assert profiles=={-4:-12,-2:-44,0:-40,2:-40,4:-4}
    for g,expected in [(F(-2),{0}),(F(-1),{-2,0,2}),(F(0),{-2,2}),(F(17,3),{-4,-2,2,4}),(F(20,3),{-4,4})]:
        energies={m:e-m-g*F(m*m-6,2) for m,e in profiles.items()}
        assert {m for m,e in energies.items() if e==min(energies.values())}==expected
    q1=load(P/'GEN4/spin_joint_install1/installed_qualification/QUALIFICATION.json')
    q2=load(P/'GEN4/spin_joint_install1/pod_upgrade/qualification2/QUALIFICATION.json')
    assert all(q1['checks'].values()) and all(q2['checks'].values())
    assert checked==85
    print(json.dumps(dict(status='PASS',retained_response_points=checked,source_bijection_states=16,
        recorded_installation_checks=[len(q1['checks']),len(q2['checks'])],new_production_solves=0),indent=2))

if __name__=='__main__':main()
