# Volume II joint response — collective coupling, step 2

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

Installed A3D41-T18-CONTACT-R2 / SLC-GEN3-R4 / SLC-GEN3-CEV1-R4 executed 43 native calls in 4.214910 seconds. One fresh joint solve bound the source in an additive session; 41 native response queries reused that result. Five queries extracted the fixed-M profiles. Six coupling slices covered both exact boundaries, each open coupling regime and g=0. All returned field transitions and a point in each intervening field interval were checked.

Independent enumeration of the16 allowed original-source states agrees on
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
