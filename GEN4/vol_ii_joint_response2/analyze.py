"""Derive the source identity and report from completed native sector responses."""
import collections
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

P=Path(__file__).resolve().parent;O=P/'execution'
sectors=json.loads((O/'SECTORS.json').read_text())
responses=json.loads((O/'RESPONSES.json').read_text())
status=json.loads((O/'STATUS.json').read_text())
reduction=json.loads((O/'ANALYTIC_REDUCTION.json').read_text())
graph=json.loads((O/'DESIGN.json').read_text())['source']

# Compare complete native conditional energy distributions after subtracting M.
shifted={r['fixed_M']:[[str(F(e)-r['fixed_M']),c] for e,c in r['native']['result']['answer']['density']]
         for r in responses if r['fixed_M'] is not None}
assert all(shifted[m]==shifted[-m] for m in shifted)

# Independent symbolic substitution, restricted to the declared contact.
# a=s1,b=t1,c=s2,d=t2, with s0=1,t0=-1.
poly=collections.Counter()
for u,v,j in graph['edges']:
    coeff=-j;key=[]
    for k in (u,v):
        if k<2:coeff*=1 if k==0 else -1
        else:key.append(k-2)
    poly[tuple(sorted(key))]+=coeff
for k,f in enumerate(graph['fields']):
    if k<2:poly[()]+=-f*(1 if k==0 else -1)
    else:poly[(k-2,)]+=-f
shiftpoly=poly.copy()
for k in range(4):shiftpoly[(k,)]-=1
transformed=collections.Counter()
for key,coefficient in shiftpoly.items():
    transformed[tuple(sorted(3-i for i in key))]+=coefficient*(-1)**len(key)
clean=lambda d:{k:v for k,v in d.items() if v}
assert clean(shiftpoly)==clean(transformed)
energy=lambda spins:-sum(j*spins[u]*spins[v] for u,v,j in graph['edges'])-sum(a*b for a,b in zip(graph['fields'],spins))
records=[]
for tail in itertools.product((-1,1),repeat=4):
    spins=(1,-1)+tail;other=(1,-1)+tuple(-v for v in reversed(tail))
    assert energy(other)==energy(spins)-2*sum(spins)
    assert sum(other)==-sum(spins)
    assert tuple(-v for v in reversed(other[2:]))==tail
    records.append(dict(spins=spins,image=other,E=energy(spins),image_E=energy(other),M=sum(spins),image_M=sum(other)))
symmetry=dict(status='EXACT_SOURCE_IDENTITY',source_sha256=status['source_sha256'],contact='z0=i',
    map='(a,b,c,d) -> (-d,-c,-b,-a); equivalently (z0,z1,z2) -> (i,-conj(z2),-conj(z1))',
    energy_identity='E0(Ts)=E0(s)-2M(s)',magnetization_identity='M(Ts)=-M(s)',
    response_identity='E(h,g;Ts)=E(2-h,g;s)',
    shifted_native_sector_spectra=shifted,
    exact_polynomial={','.join(map(str,k)):v for k,v in sorted(clean(shiftpoly).items())},
    symbolic_substitution='PASS',full_native_sector_spectra_match=True,bijection_checks=records,
    scope='This 444 source with imaginary contact and uniform h/g, remaining ports summed. General source-family extension and arbitrary boundary-field invariance are not executed.',
    installed_globally=False)
(P/'SOURCE_IDENTITY.json').write_text(json.dumps(symmetry,indent=2)+'\n')

text='''# Volume II joint response — collective coupling, step 2

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are
research collaborators. Codex designed this bounded follow-up under Sean's
authorization to take the next step and assess the result.

## Result

**The test result suggests strong contact with the concept.** The 444 source
with its first phase fixed at i has an exact field-reflection identity centered
at h=1. Collective coupling changes the alignment sectors that participate,
while preserving this center. The original -2↔2 ground-state switch survives
for -1<g<17/3, with additional coexisting sectors at the endpoints.

| Collective coupling g | Ground sectors at h=1 | Behavior near h=1 |
|---|---|---|
| g < -1 | M=0 | A neutral plateau replaces the direct switch |
| g = -1 | M=-2,0,2 | Three configurations coexist |
| -1 < g < 17/3 | M=-2,2 | Original direct switch |
| g = 17/3 | M=-4,-2,2,4 | Four configurations coexist |
| g > 17/3 | M=-4,4 | Larger direct switch, still at h=1 |

Every listed sector has one ground configuration at the stated coexistence.
The source has 16 admissible configurations under this contact. These are
finite-source ground selections in the formal phase model.

## Source, intervention and pre-execution prediction

The inherited 444/COMMON_PIVOT six-spin source and its z0=i contact are unchanged
from [step 1](../vol_ii_joint_response1/REPORT.md). Ordered retained ports remain
[s0,t0,s1,t1], with [s0,t0]=[1,-1] and remaining ports summed.

The existing readout applies

    E(h,g) = E0 - h M - g (M²-6)/2.

M=2 sum Re(z_i); E_spin=2H_phase. Thus h is the formal real-axis phase-alignment
field and g is an added uniform binary pair interaction. In phase energy the
collective contribution is -g(M²-6)/4. No physical unit assignment is added.

The recorded prediction was conditional: the M=-2 and M=2 pairwise crossing
stays at h=1 because their M² values agree. The unknown was where other sectors
become globally preferred. No thresholds were supplied as execution targets.

## Exact sector reduction

Native fixed-M readout returns the following minima and phase witnesses:

| M | E0 minimum | E(h,g) minimum in sector | (z0,z1,z2) |
|---|---|---|---|
| -4 | -12 | -12+4h-5g | (i,-1,-1) |
| -2 | -44 | -44+2h+g | (i,-1,i) |
| 0 | -40 | -40+3g | (i,i,i) |
| 2 | -40 | -40-2h+g | (i,i,1) |
| 4 | -4 | -4-4h-5g | (i,1,1) |

At h=1 these reduce to three competing levels:

    M=0:    -40+3g
    M=±2:   -42+g
    M=±4:    -8-5g

Comparing the levels gives g=-1 and g=17/3 exactly. Ground-state response for
all h,g reduces to comparing these five affine planes because the perturbation
is constant within each fixed-M sector. The full joint DOS is still retained
for counts and higher-energy questions; sector minima alone do not replace it.

For g<-1, the M=0 plateau extends from h=2+g to h=-g; its width is -2(1+g)
and its center is h=1. For -1<g<17/3, the three transition fields are
3g-16, 1, and 18-3g. At g=17/3 these collapse to h=1. Above that coupling,
the intermediate sectors leave the lower envelope and the -4↔4 switch remains.
For g<-1 the outer transitions remain 3g-16 and 18-3g.

## Why the center survives: a full-spectrum identity

The returned fixed-M densities show more than equality of the sector minima.
After subtracting M from E0, the complete distributions match for opposite M:

| Sectors | Distribution of E0-M, written energy:count |
|---|---|
| M=-4 and M=4 | -8:1 |
| M=-2 and M=2 | -42:1, 10:2, 22:1 |

This led to an exact source transformation. Write a=s1,b=t1,c=s2,d=t2 with
the contact fixed. The shifted source polynomial is

    E0-M = -3a+13b-13c+3d -4ac-8ad+8bc-4bd.

It is invariant under T:(a,b,c,d)→(-d,-c,-b,-a). In C4 coordinates this is
(i,z1,z2)→(i,-conj(z2),-conj(z1)). T is an involution and reverses M.
Symbolic coefficient substitution and all16 source states independently give

    M(Ts) = -M(s),
    E0(Ts) = E0(s)-2M(s),
    E(h,g;Ts) = E(2-h,g;s).

Consequently the entire scalar energy distribution at h equals that at 2-h,
with opposite M sectors paired, for every g in this source/contact family.
At h=1 a nonzero-M ground state therefore has an opposite-M partner. A unique
M=0 minimum is also compatible with the identity, as the negative-g regime
demonstrates. A zero-field global rotation and this shifted reflection are
different transformations; step 2 identifies the latter explicitly.

This identity applies with the remaining contacts summed and the specified
uniform perturbations. T moves the other ordered coordinates. Additional
boundary constraints or fields must be transformed accordingly; no arbitrary
fixed-boundary invariance is asserted. The identity is documented in
[SOURCE_IDENTITY.json](SOURCE_IDENTITY.json), not installed as a global rule.

## Execution and verification

'''
text+=f"Installed A3D41-T18-CONTACT-R2 / SLC-GEN3-R4 / SLC-GEN3-CEV1-R4 executed {status['native_calls']} native calls in {status['seconds']:.6f} seconds. One fresh joint solve bound the source in an additive session; 41 native response queries reused that result. Five queries extracted the fixed-M profiles. Six coupling slices covered both exact boundaries, each open coupling regime and g=0. All returned field transitions and a point in each intervening field interval were checked.\n\n"
text+='''Independent enumeration of the16 allowed original-source states agrees on
full transformed DOS, counts, energy and M moments, mixed moment, ground energies,
degeneracies and ground M counts at all41 queries. All native field-crossing
lists agree with independent pairwise affine intersections. The all-g threshold
statement follows from exact sector inequalities, rather than interpolation
between the six slices. No numerical or implementation failure occurred.

Native calculations: [responses](execution/RESPONSES.json),
[sector profiles](execution/SECTORS.json),
[analytic reduction](execution/ANALYTIC_REDUCTION.json),
[status/session](execution/STATUS.json), [design](execution/DESIGN.json).
The installed resource launcher admitted this workstation CPU run under
`SAM_RUNTIME/R3/runs/volii-joint-response2/`; it exited normally.

## Assessment and next proposed step

This step returns a reusable computational idea: an exact source transformation
can predict the center of an entire response family while collective coupling
controls which sector wins. Here the full-spectrum identity explains why a
larger switch replaces the original one without moving its center.

The next bounded question should test that mechanism on changed source
couplings: one matched perturbation preserving the transformation and one
breaking it. Predict the reflection center from the source algebra before
readout, then observe the exact response. That would establish whether this
source-level identity can become a useful selector/reduction across a family
of Volume II configurations. This is a proposed next step only.

The first-step artifacts and canonical results remain immutable. Runtime
selection is unchanged, no follow-up process is running, and L-series/RH/training
remain paused. No new pod or GPU was needed.

NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.
'''
(P/'REPORT.md').write_text(text)
(P/'README.md').write_text('# Volume II collective response, step 2\n\nSee [REPORT.md](REPORT.md). Completed bounded experiment; no follow-up is running.\n')
(P/'REPRODUCE.md').write_text('''# Reproduce

From the repository root, use `.venv-r3/bin/python`. Preserve this completed
directory: copy run.py and analyze.py to a fresh sibling directory under GEN4
and use a fresh lowercase resource-run name. run.py refuses to overwrite an
existing execution directory.

```
.venv-r3/bin/python CURRENT_REVISION/engines/SLC/gen3/resources.py run --name FRESH-NAME --seconds 600 -- .venv-r3/bin/python GEN4/FRESH-DIRECTORY/run.py
.venv-r3/bin/python GEN4/FRESH-DIRECTORY/analyze.py
```

The first script executes the installed domain. The second derives the report
and checks the source polynomial identity from saved native results; it does
not launch another domain experiment. Input hash and source are in DESIGN.json,
while execution/sessions contains native receipts and the final checkpoint.
''')
files=[p for p in P.rglob('*') if p.is_file() and p.name!='HASHES.txt' and '__pycache__' not in p.parts]
(P/'HASHES.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(P))+'\n' for p in sorted(files)))
print(json.dumps(dict(full_sector_symmetry=True,symbolic_identity='PASS',bijection_states=len(records),report=str(P/'REPORT.md'),files=len(files)),indent=2))
