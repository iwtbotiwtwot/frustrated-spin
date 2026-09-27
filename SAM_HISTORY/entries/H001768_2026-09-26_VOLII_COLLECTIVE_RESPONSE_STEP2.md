---
entry_id: H001768
entry_date: 2026-09-26
entry_type: RESULT
status: IMMUTABLE_HISTORY
supersedes: NONE
affects_live:
  - SAM_LIVE/11_VOLII_EXCHANGE_CURRENT.md
---

# Volume II collective response, second bounded step

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are
research collaborators. Sean authorized the proposed next collective-coupling
experiment following H001767; Codex supplied the technical design and analysis.

Prior state: the444 source with z0=i has an M=-2↔2 ground-state switch at h=1.
Equal M² predicts that these branches' pairwise crossing is unchanged by uniform
collective coupling. Its global survival interval was not yet measured.

## Completed result

[Report](../../GEN4/vol_ii_joint_response2/REPORT.md),
[native results](../../GEN4/vol_ii_joint_response2/execution/RESPONSES.json),
[sector reduction](../../GEN4/vol_ii_joint_response2/execution/ANALYTIC_REDUCTION.json),
[source identity](../../GEN4/vol_ii_joint_response2/SOURCE_IDENTITY.json).

Installed A3D41/SLC executed43 native calls in4.214910seconds: one joint solve,
41response queries and a final checkpoint. Five fixed-M profiles give exact
sector minima for M=-4,-2,0,2,4. Six coupling slices cover both exact boundaries,
each open regime and g=0. Independent16-state enumeration agrees at all41
queries on full DOS, moments, counts, crossings and ground families.

At h=1 the three competing levels are:

- M=0: -40+3g;
- M=±2: -42+g;
- M=±4: -8-5g.

For g<-1, M=0 is the unique ground state at h=1, with a neutral plateau
2+g<h<-g. At g=-1, M=-2,0,2 coexist. For -1<g<17/3, the original ±2
switch survives. At17/3, M=-4,-2,2,4 coexist. Above17/3 a larger ±4 switch
occurs at the same field h=1. All thresholds follow exact native sector data.

Full conditional energy distributions also match for opposite M after shifting
E0→E0-M. With a=s1,b=t1,c=s2,d=t2, the source polynomial is
E0-M=-3a+13b-13c+3d-4ac-8ad+8bc-4bd. It is invariant under
T:(a,b,c,d)→(-d,-c,-b,-a). Exact substitution and16state checks give
M(Ts)=-M(s), E0(Ts)=E0(s)-2M(s), hence E(h,g;Ts)=E(2-h,g;s).
The reflection therefore covers the full spectrum at every g for the specified
source/contact and summed remaining ports. It is documented as a source
identity; no global rule or arbitrary-boundary invariance was installed.

**The test result suggests strong contact with the concept.** The result concerns
the finite formal phase source, contact-conditioned collective response and
its exact source identity.

## Assessment and preserved boundaries

The next proposed bounded test changes source couplings using one transformation-
preserving and one transformation-breaking perturbation, with a source-derived
prediction before readout. It has not started. Canonical and first-step results,
runtime selections, holdouts and unrelated work are unchanged; L-series/RH/
training remain paused. No physical unit assignment or dynamics is introduced.

The affected Volume II live section replaces step1's pending-coupling statement
with this completed step2 result, retaining the step1 and installation links.
