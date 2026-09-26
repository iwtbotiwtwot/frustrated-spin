---
entry_id: H001709
entry_date: 2026-09-24
entry_type: RESULT_AND_AUTHORITY_CHANGE
status: IMMUTABLE_HISTORY
supersedes: H001574 for latest spin-pod benchmark cursor; preserves prior results
prior_entries: [H001563, H001574, H001673, H001707]
affects_live:
  - SAM_LIVE/00_CURRENT.md
  - SAM_LIVE/01_SLC_CURRENT.md
  - SAM_LIVE/10_PODS_CURRENT.md
---

# GEN4 fourteen-worker frustrated-spin benchmarks

The owner supplied pod txqaltf4cdtfls, requested N72 benchmarking, fourteen GPU
workers with CPU directional fiber, RAM-first checkpointing, full monitoring,
L13/L14/N96 scheduling review, simultaneous GPU activity, and then fresh N96.
The direct endpoint216.243.220.128:14657 was verified against the owner-supplied
SSH gateway by a shared nonce. Source upload was explicitly approved after
an initial automatic review rejection; the completed transfer succeeded.

Hardware:14Blackwell MIG1g.24gb devices,47.6CPU equivalents,880GB memory.
Rebuilt scoped SLC-GEN4-P1 / SLC-GEN4-CE-P1 verifies395bound files.
MATTER_SEARCH uses its retained GEN3-R4 domain identity on that pod runtime.
Global workstation SLC-GEN3-R4 and other research policies are unchanged.

[N72 report](../../GEN4/frustrated_spin_n72_bench1/RESULT.md):45fresh exact
calculations across6sessions. The cold baseline takes15.036s. Persistent queues,
RAM factors, VRAM prefetch and delayed shutdown remove measured scheduling
costs. CUDA graphs fuse68elimination launches plus terminal contraction.
Actual CUPTI steady kernel activity rises93.05%→99.45%mean per GPU, and
38.50%→92.62%all14simultaneously.16fresh answers take1.658s after preparation;
whole lifecycle16.064s. Exact spectra/ports/T18 agree on every calculation.

[N96 report](../../GEN4/frustrated_spin_n96_bench1/RESULT.md):two fresh original
96-spin/240-edge runs,4096roots/32cutset branches each, all14checks passing.
8-root batches:27.543s to answer/29.670s including shutdown.16-root batches:
23.265s to answer/25.460s including shutdown; ready-to-answer12.014s.
Steady mean kernel activity99.24%,all14simultaneous91.54%;full-window all14
87.46%.The changed startup dominates the total-time difference; warm execution
is essentially unchanged.6.45GiB host/3.34GiB per-worker device pool;zero CPU
throttling. Original CPU exact reconstruction and mathematical fiber retained.

All CUPTI streams have zero dropped records. Memory-first outputs and compact
checkpoint archives are retained on pod and workstation with matching hashes.
Eight sessions/16native operation-and-checkpoint receipts verify. All benchmark
workers have exited. Earlier baselines, first-pipeline teardown delay and exact
successor runs remain preserved. These are source-bound DomainSession adapters,
not an unrequested global engine replacement or an all-size spin catalog.

For the tested exact execution and overlap:
**The test result suggests strong contact with the concept.**

The owner next requests a reusable catalog at N2,8,12,18,24,36,48,60,72,84,96,
with GEN4 running each and retaining useful learning for frontier work. That
catalog is authorized follow-on work; it is not represented as completed here.
Negative drift check:clear. Helpful finding:GPU service intervals hid launch
gaps; actual concurrent-kernel tracing identified them and CUDA graphs removed
most. Coarser final batches leave a measurable terminal-load imbalance.
