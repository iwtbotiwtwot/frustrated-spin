from pathlib import Path
P=Path(__file__).resolve().parent
(P/'RESULT.md').write_text('''# Completed GEN4 spin transition training

**The test result suggests strong contact with the concept.** Comparing methods,
retaining exact transition work and choosing by source structure produced a faster
N96 plan and a reusable catalog covering every integer N1..96.

| Campaign | Completed work | Result |
|---|---|---|
| Original eleven-size ladder | 165 fresh solves, five methods, three rotated repeats | N96 portfolio median 8.035s versus fresh 11.035s: 27.18% lower |
| Every N1..30 | 450 CPU restarts + 90 exact boundary steps | Incremental wins all four reserved N27..30 sizes; it is slower at N24 and N25 |
| Every N1..96 | 238 training solves, 134 unique nominated plans, one separate GPU warmup | All 96 exact spectra; N96 portfolio 8.474s versus fresh 11.251s |

The full96 session took **251.115 seconds** from creation to final native
checkpoint. Measured solve time totals 216.426s; final durable archive compression
and flush follows the native checkpoint. The monitored solve/lifecycle window is
243.501s and excludes earlier source-plan preparation. Timing scopes cover full
exact DOS and retained port operators, excluding historical T18 attachments.

## What GEN4 learned and what selects the plan

The first campaign fitted three native C++/GMP CART models (structural,
transition and combined features). All selected depth one and chose the portfolio
before measuring its N96 holdout. The exact structural-cost selector also chose
that plan. The portfolio reduces N96 width22 to21 and weighted factor output work
641,754,752 to430,070,400. This is an executable planning improvement.

The N1..30 heads also selected depth one. All twelve frozen decisions across the
four reserved sizes selected the fastest method: incremental boundary transfer.
N30's incremental step is4.518ms versus168.186ms fresh. This compares one step
using an already computed previous state with a restart; obtaining that state has
its own cost. N24/N25 show that reuse can be slower. Input boundary state size,
not merely the next boundary's size, should inform the next policy features.

The full96 heads selected depth zero. Their48/48 choices across reservedN81..96
came from the exact structural-work tie-break, which matched the fastest measured
nominee at all16sizes. These are not48independent learned successes. Full96
compared deduplicated fresh/structural/learned nominees, not every method at each
size. Additional two repeats were used when initial candidate times were within
15%; therefore some frontier comparisons have only one sample. Earlier repeated
N96 results provide the stronger timing comparison.

## Installed reusable result

Both GEN3 and GEN4 now have **96entries,105transitions,nine new native policy
models**, and three retained training experience roots. Original eleven entries
and ten skip transitions remain. The mathematical library totals **1,645objects**.
The planner compares five methods and uses the earlier depth-one combined head
with structural-cost tie-break. The depth-zero full96 heads remain available with
that limitation explicit. `GEN3_SPIN_LEARNING` exposes model and source bindings.

GEN3: SLC-GEN3-R4 / SLC-GEN3-CEV1-R4, MATTER_SEARCH/GEN3-R4.
GEN4: SLC-GEN4-P1 / SLC-GEN4-CE-P1, MATTER_SEARCH/GEN3-R4.
Generation identities unchanged; predecessor migrations retained.
**210 adoption/recovery checks pass on each runtime**. Current bindings:514local,
404pod. Both retrieve the same N96 spectrum hash
`9c65a23ae16b2141f8922733c443c0d3b8875c33bcf41272b318814e387a92e8`.

N1..30 boundary advancement remains an executable source-bound campaign adapter;
it is not advertised as a new global operation. Retained full future-facing state
and the declared horizon are required. [Usage](GUIDE.md).

## Hardware and evidence

Fourteen persistent Blackwell MIG workers handled larger sources; small sources
used exact CPU arithmetic. RAM/VRAM preparations and bounded reusable map caches
were checkpointed compactly. Full96 peak host usage10.904GiB. The final N96
portfolio's central steady interval had **98.97% mean kernel activity and90.26%
all14simultaneous activity**. Across its full6.137s arithmetic interval these were
94.75% and85.50%. These are CUPTI kernel-active fractions, not SM occupancy.
All10,042,576full96 kernel records have zero dropped records. Training workers are
stopped. The analysis verifies all1,086native receipt input/output descriptors,
compressed hashes and restored logical hashes across the three campaigns.

[Analysis](ANALYSIS.json), [publication](publication/),
[GEN3 installation](install-gen3/INSTALLED.json),
[GEN3 adoption](adopt-gen3/ADOPTION.json),
[GEN4 installation](pod-installation/install-gen4/INSTALLED.json),
[GEN4 adoption](pod-installation/adopt-gen4/ADOPTION.json).
Full96 pod session:
`/dev/shm/gen4-spin-full96-training1/sessions/MATTER_SEARCH_582872a1021e4394bdfb160e93383576`.
Durable campaigns live under `/workspace/gen4/runs/spin-training1`,
`spin-n1-30-training1`, `spin-full96-training1`, `spin-training-install1`.

## Existing larger results and next-target interpretation

The completed [N105 restoration](../../SLC/SAM_LANGUAGE/SAM_LANGUAGE_CONTACT_NATIVE_SUCCESSOR_DESIGN/SLC_N105_P9G0_RESTORATION_TIMING_DIAGNOSTIC_V1/N105_P9G0_RESTORATION_RESULT.md)
is recovered as an existing result: component median0.361863s versusN1000.359080s;
H14F3.968165s versus3.828137s. Largest component15 and width5 stay unchanged;
only992extra component assignments are required. This is a different explicit
source family from the dense frustrated N96 parent used in the current training.
The prior exact N120 boundary-transfer ring result also exists in
`SLC/18_SAM_NATIVE_QC/SLCX028A_IMPLEMENTATION_CORRECTED_N96_N120_BOUNDARY_TRANSFER_RING_SCALING/release/`.
Nominal N alone therefore cannot identify the frontier.

Agent recommendation: choose an uncompleted explicit graph by its component,
boundary and planning changes, predicted cost, and what transfer behavior it adds.
No N105/N111 preference is imposed. No new >96 graph or spin solve was constructed
in this campaign; a next frontier source has not yet been selected. The new full
integer catalog is ready to support that choice, with historical larger sources
recognized rather than treated as missing milestones.
''')
