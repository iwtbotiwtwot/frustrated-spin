"""Summarize completed native responses; no additional scientific executions."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

P=Path(__file__).resolve().parent
rows=json.loads((P/'execution/RESULTS.json').read_text())
status=json.loads((P/'execution/STATUS.json').read_text())
def zero(r):
    return next(v for v in r['responses'] if v['field']=='0')['native']['result']['answer']
comparisons=[]
for source in dict.fromkeys(r['source'] for r in rows):
    a,b=[next(r for r in rows if r['source']==source and r['condition']==c) for c in ('Z0_REAL_PLUS','Z0_IMAG_PLUS')]
    za,zb=zero(a),zero(b)
    comparisons.append(dict(source=source,zero_field_energy_DOS_equal=za['density']==zb['density'],
        real_ground_M=za['ground_magnetization_counts'],imaginary_ground_M=zb['ground_magnetization_counts'],
        real_energy_M_covariance=za['energy_magnetization_covariance'],imaginary_energy_M_covariance=zb['energy_magnetization_covariance'],
        magnetization_variance_equal=za['magnetization_variance']==zb['magnetization_variance'],
        common_magnetization_variance=za['magnetization_variance']))
(P/'COMPARISONS.json').write_text(json.dumps(comparisons,indent=2)+'\n')

lines=['# Volume II joint response — first bounded step', '',
'Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are research collaborators. The experiment design and following interpretation are Codex contributions under Sean’s instruction to proceed one step, observe, and assess.', '',
'## Result and assessment', '',
'**The test result suggests strong contact with the concept.** The retained joint operator separates contact-dependent alignment responses that have identical complete zero-field energy spectra. All six finite-source response curves were obtained through installed A3D41/SLC operations. The useful next step is a bounded collective-coupling intervention on the 444 imaginary-contact source, described below; it has not been executed.', '',
'The real and imaginary pinned contacts are related by a global C4 rotation. That rotation leaves the unperturbed energy invariant, explaining their identical scalar spectra. The alignment field remains on the fixed real axis, so the response need not remain equal. The result identifies exactly where the orientation information becomes useful.', '',
'## Question and source mapping', '',
'How does a uniform alignment field change the ground configurations of the two retained frustrated C4 sources, and what changes when the first phase is fixed at 1 or i?', '',
'The sources are 333/XYZ_TRIANGLE with couplings [(0,2),(-2,0),(4,2)], and 444/COMMON_PIVOT with [(8,-6),(4,8),(8,-4)], inherited from `GEN4/spin_joint_install1/PHASE_ADOPTION_INPUTS.json`. Each has three C4 coordinates, represented by six binary coordinates and 64 configurations.', '',
'With z_i=(s_i+t_i)/2+i(s_i-t_i)/2, E_spin=2H_phase and M=2 sum Re(z_i), the intervention is E_spin(h)=E_spin(0)-hM, or H_phase(h)=H_phase(0)-h sum Re(z_i). h is the formal phase-alignment field in these source units. Collective coupling and boundary fields are zero throughout this step.', '',
'Ordered ports are [s0,t0,s1,t1]. FREE sums all 64 configurations. Z0_REAL_PLUS fixes [s0,t0]=[1,1]; Z0_IMAG_PLUS fixes [1,-1]. Each pinned case has 16 configurations. Fixing the imaginary first phase limits achievable M to [-4,4]; full M=6 alignment is unavailable under that contact.', '',
'## Complete transition map', '',
'Fields below are exact. Between consecutive transitions, the listed magnetization and degeneracy stay constant; all coexisting sectors at the transitions are retained in the execution records. These are finite-source ground-state transitions.', '',
'| Source | Contact | Transition fields h | M on successive open intervals |',
'|---|---|---|---|']
for r in rows:
    lines.append('| '+r['source']+' | '+r['condition']+' | '+', '.join(c['field'] for c in r['crossings'])+' | '+' → '.join('/'.join(i['ground_M_counts']) for i in r['intervals'])+' |')
lines += ['', 
'### Information gained from the joint readout', '',
'| Source | Equal full scalar DOS for real/imaginary contact at h=0? | Real-contact ground M (count) | Imaginary-contact ground M (count) | Cov(E,M), real / imaginary |',
'|---|---|---|---|---|']
for c in comparisons:
    lines.append(f"| {c['source']} | {c['zero_field_energy_DOS_equal']} | {c['real_ground_M']} | {c['imaginary_ground_M']} | {c['real_energy_M_covariance']} / {c['imaginary_energy_M_covariance']} |")
lines += ['',
'Both pairs also have equal M variance, namely 4, under uniform counting over their allowed configurations. The energy–M covariance differs. Thus this step establishes equal scalar spectra and equal M variance with different joint responses; it does not identify an equal-full-covariance pair. These moments are uniform configuration-count moments, not thermal expectation values.', '',
'### The 444 contact response gives the clearest next lead', '',
'With the real contact fixed, the ground state remains (1,i,1), M=4, over -34/3<h<2. The opposing-field transition at -34/3 goes directly from M=-2 to M=4, skipping M=0 and M=2 as interval minima. Its two source energies are 24 and -44: 24+2h=-44-4h gives h=-34/3.', '',
'With the imaginary contact fixed, the ground state is (i,-1,i), M=-2, over -16<h<1. A weak positive real-axis field therefore initially retains a negative total alignment. At h=1 it switches to (i,i,1), M=2, which persists until h=18. The source energies -44 and -40 give -44+2h=-40-2h at h=1. This is an equilibrium ground-state selection result; no history, hysteresis or dynamical switching time was measured.', '',
'The unconstrained 444 source reaches M=6 at h=2. The imaginary-contact source reaches its own maximum M=4 at h=18. Those maxima refer to different admissible sets; the exact response curves retain that distinction.', '',
'The 333 source also separates contacts: its positive-field transition to the maximum allowed M is at h=4 for the real contact and h=8 for the imaginary contact. Its larger zero-field ground family appears explicitly in the transition multiplicities.', '',
'## Executed method and checks', '',
f"The installed ATOM3D domain selected A3D41-T18-CONTACT-R2, SLC-GEN3-R4 and SLC-GEN3-CEV1-R4. {status['native_calls']} native calls comprised two fresh joint source solves, 44 response applications and one final checkpoint. Measured script wall time was {status['seconds']:.6f} seconds; hardware allocation is retained under `SAM_RUNTIME/R3/runs/volii-joint-response1/`.", '',
'For each contact, the native readout returns the exact lower envelope of E_min(M)-hM. This yields the full real-field transition map, with no grid spacing. Readout calls then evaluate every transition, h=0, and a rational point in every open interval. No new spin solve is performed for those response queries.', '',
'An identified independent direct enumeration of the 64 original source states checks the new results. Pairwise affine intersections give an independent crossing list, rather than repeating the native hull algorithm. At all 44 query points, full transformed DOS, count, ground energy, ground multiplicity, ground M counts, energy first/second moments, M first/second moments and mixed E–M moment agree exactly. Phase witnesses in the report are recovered by that independent state enumeration. No numerical failure occurred. Optional plot rendering was omitted because matplotlib is absent from both the installed scientific environment and system Python; the complete exact interval table is retained.', '',
f"Session: `{status['session']}`. [Execution status](execution/STATUS.json), [all native results and witnesses](execution/RESULTS.json), [source/experiment design](execution/DESIGN.json), [scalar/joint comparisons](COMPARISONS.json).", '',
'## Assessment and one proposed next experiment', '',
'Keep the 444 source and imaginary contact fixed, and vary the already-installed collective term -g(M²-6)/2. The observed h=1 switch joins M=-2 and M=2, whose M² values agree. Therefore the collective term shifts both branches equally: their crossing stays at h=1 for every g while those branches remain globally minimal. Other M sectors can nevertheless undercut them.', '',
'The next question is: at which exact g values do competing sectors enter and remove this protected crossing? That would turn the first response map into a test of how collective coupling reshapes contact-selected phase families. This is a conditional algebraic prediction derived from the returned states, not a second executed experiment. No automatic continuation is running.', '',
'## Preservation and scope', '',
'The original atlas and source results are unchanged. This project is additive and uses existing installed operations, with no runtime modification, pod dependency, larger-N run, L-series resumption, RH resumption or autonomous training. The retained source coordinate M is used as phase alignment; no physical magnetic moment or unit assignment is introduced.', '',
'NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.', '']
(P/'REPORT.md').write_text('\n'.join(lines))

(P/'README.md').write_text('# Volume II joint response, step 1\n\nSee [REPORT.md](REPORT.md) for results and assessment.\n\nNo follow-up run is active.\n')
(P/'REPRODUCE.md').write_text('# Reproduce\n\nRun from the repository using `.venv-r3/bin/python` and the installed resource launcher. `run.py` opens a current ATOM3D DomainSession and creates `execution/` only when absent. Preserve this completed directory; copy the scripts to a fresh sibling project directory under GEN4 for a rerun. Use a fresh resource run name.\n\n```sh\n.venv-r3/bin/python CURRENT_REVISION/engines/SLC/gen3/resources.py run --name NEW-LOWERCASE-NAME --seconds 600 -- .venv-r3/bin/python GEN4/NEW-PROJECT/run.py\n.venv-r3/bin/python GEN4/NEW-PROJECT/analyze.py\n```\n\n`analyze.py` derives the report from saved results without scientific execution. Source input hash is in execution/DESIGN.json. Native payloads and receipts, exact source identities and checkpoint are retained in execution/sessions/.\n')
hashes=[]
for f in sorted(P.rglob('*')):
    if f.is_file() and f.name!='HASHES.txt' and '__pycache__' not in f.parts:
        hashes.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(P)))
(P/'HASHES.txt').write_text('\n'.join(hashes)+'\n')
print(json.dumps(dict(report=str(P/'REPORT.md'),comparisons=comparisons,hashed_files=len(hashes)),indent=2))
