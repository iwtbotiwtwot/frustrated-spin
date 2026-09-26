# GEN4 exact spin catalog and transition learning

Completed and installed on the workstation GEN3 and the authorized pod GEN4.
The requested sizes are **N2,8,12,18,24,36,48,60,72,84,96**. There are eleven
exact entries, ten measured adjacent transitions and four installed native
operations. The shared retained library now contains1462objects (1441prior+21new).

## Source and calculation

Agent implementation uses a nested induced-subgraph ladder of the retained
N96 source `625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d`.
Every graph, field, coupling, vertex mapping, retained port and transition delta
is saved. Proper subgraphs are not the older independent five-regular benchmark
instances. The original N72 benchmark remains a separate reference.

Each entry was freshly calculated through a warm GEN4 DomainSession. The
explicit successor supplies generalized conditioning and CUDA graphs, using
retained exact initial-factor, inverse-NTT and CRT arithmetic. N2–24 use CPU
modular arithmetic; N36–96 use14persistent CUDA workers with the CPU preparing
factors and reconstructing exact integer spectra. RAM holds working data and
VRAM retains index maps; compact archives flush at completed checkpoints.

The first eleven solve calls total **23.726758seconds**. Session creation through
first N96 return takes **25.220286seconds**; source-plan preparation precedes
session creation. N36 includes the first GPU-context/JIT startup.

| N | Edges | Solve seconds | Selected width | Branches | Ground energy | Occupied bins |
|---|---|---|---|---|---|---|
| 2 | 1 | 0.003296 | 0 | 1 | -4 | 4 |
| 8 | 6 | 0.041035 | 2 | 1 | -18 | 18 |
| 12 | 13 | 0.081995 | 3 | 1 | -32 | 33 |
| 18 | 16 | 0.094791 | 3 | 1 | -38 | 40 |
| 24 | 19 | 0.081887 | 3 | 1 | -53 | 54 |
| 36 | 34 | 9.841628 | 3 | 1 | -87 | 88 |
| 48 | 58 | 0.346446 | 4 | 1 | -133 | 133 |
| 60 | 91 | 0.386335 | 9 | 1 | -177 | 180 |
| 72 | 132 | 0.730089 | 13 | 1 | -231 | 232 |
| 84 | 183 | 0.946333 | 22 | 1 | -280 | 283 |
| 96 | 240 | 11.172923 | 22 | 32 | -346 | 348 |

N96 covers all **2^96 = 79228162514264337593543950336** configurations, with
minimum energy−346 and degeneracy12. All348energy bins match the original
retained spectrum. All16open-port operators also match exactly after the saved
vertex/port permutation. Count, first/second moments, per-port counts and support
checks pass for every entry. Independent enumeration agrees throughN18.

A second **fresh** N96 solve takes **11.010179seconds**. Its exact counts are
recomputed; resident index maps are reused. These timings cover exact spectra
and retained ports. The older23.265second benchmark additionally includes cold
startup and T18open/closed attachments; it is a different timing scope.

## What the transitions teach

The previous ordering changes min-fill tie priority. GEN4 compares that plan
with a fresh ordering and the frozen parent plan, with/without retained cutset
sites, then chooses by exact structural work within the worker memory admission.

- N60→72: output work falls63774→47526entries per root (**25.48%**).
- N72→84:16985708→15661356entries per root (**7.80%**).
- N84→96: a fresh ordering with32cutset branches wins. Its weighted output
  work641754752 is21.21%below the frozen parent's814475904. Blindly retaining
  previous-order priority would cost1421452928entries.
- CPU index construction atN96 reuses283recipes and creates103. The14GPU
  workers collectively reuse3962maps and create1442. The matched fresh N96
  replay reuses **5404maps with zero new map uploads**. Preparation changes
  0.712443→0.577512seconds; total changes11.172923→11.010179seconds. These are
  single matched observations, not a repeated-run speedup distribution.
- Transitions retain the boundary touched by new/changed interactions. If the
  saved ports do not cover it, the next solve reuses plans/index recipes and
  recalculates the spectrum; the old scalar DOS is not used as a substitute
  for missing correlations.

Native C++ exact CART fitted `spin-transition-plan-v1`:8training rows,
N84development, N96reserved. It selecteddepth0 and predicts one class on every
row (2/10correct including training/development; reservedN96incorrect). The
model and its provenance are installed **as advisory**. The useful execution
policy is the retained exact candidate comparison and map reuse. Future fits
must use a new identity and additional transition experience.

## Hardware evidence

14Blackwell MIG1g.24gb slices;47.6CPU equivalents;880GBmemory allocation.
Peak observed host memory7.35GiB; per-worker pool2.76GiB.1,461,424CUPTI kernel
records, **zero dropped**. N96steady activity:99.02%mean worker kernel-active,
89.82%all14simultaneously. Replay:99.09%mean,91.57%all14simultaneously.
These measure time with an executing kernel, not SMoccupancy. Small graphs are
short and queue imbalance is visible; their timings are not utilization claims.

## Installed use and checks

Workstation **SLC-GEN3-R4 / SLC-GEN3-CEV1-R4**, pod
**SLC-GEN4-P1 / SLC-GEN4-CE-P1**. Both use MATTER_SEARCH/GEN3-R4 domain identity.
Existing generations remain; predecessor state bindings and all existing models
and objects are retained.28adoption/recovery checks pass on each runtime.
Registry verification passes512workstation/402podbindings. Fresh native lookup
requires no new spin arithmetic or model fit; source mismatch is rejected.

```
./spin-catalog list
./spin-catalog entry 96
./spin-catalog transition 84 96
./spin-catalog plan next_graph.json --previous 96
```

Native operations: `GEN3_SPIN_CATALOG`, `GEN3_SPIN_ENTRY`,
`GEN3_SPIN_TRANSITION`, `GEN3_SPIN_PLAN`. Details in
[installed guide](../../CURRENT_REVISION/engines/SLC/SPIN_CATALOG.md).
Generic `GEN3_RESULT_EXPORT/IMPORT` transfers the exact dependency closure.
Compressed portable catalog:448KiB; completed run archive17.80MiB.

## Custody and next step

[Analysis](ANALYSIS.json), [native results](results/ram/COMPLETE.json),
[GEN3adoption](adopt-gen3/ADOPTION.json),
[GEN4adoption](pod-installation/adopt-gen4/ADOPTION.json).
38native calculation/learning/publication/export/checkpoint receipts are hash-
verified, plus installed adoption receipts. The first interrupted attempt
(module-name collision after five completed small cases) is preserved in
`interrupted1.tar.gz`; the corrected campaign contains twelve complete solves.
A pod installation staging attempt hit FUSE timestamp preservation; no runtime
files had changed. Container-backed transactional staging then succeeded.

Pod checkpoint:/workspace/gen4/runs/spin-catalog1/completed/checkpoint.tar.gz.
Pod installation backups and adoption:/workspace/gen4/runs/spin-catalog1/
installation-evidence.tar.gz. Local copies match. Compute workers are stopped;
the allocated pod remains available.

Recommended next execution is a short **N96→N108** successor, with an explicit
N108graph construction, matched output/timing scope, warm workers and retained
transition experience. N108has not been constructed or run in this campaign.

For exact execution and reusable transition work:
**The test result suggests strong contact with the concept.**
Negative drift check:clear. Helpful finding:transfer is selective—order reuse
helpsN72/N84, while a fresh conditioned plan is cheaper atN96. Exact planning
retains that distinction even though the initial statistical model does not.
