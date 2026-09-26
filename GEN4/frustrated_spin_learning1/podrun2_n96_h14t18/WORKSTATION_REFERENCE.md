# Fresh exact N96 on fourteen GEN4 GPU workers

Two fresh runs of the original 96-spin,240-edge frustrated-spin source complete
on the owner's14-MIG pod. Both pass all14retained exact checks, including the
full density of states and original open/closed directional-fiber attachments.
Each freshly computes4096root vectors across32cutset branches and closes
2^96=79,228,162,514,264,337,593,543,950,336 configurations.

| Measurement | 8-root batches | 16-root batches |
|---|---:|---:|
| Initialization/source/graph preparation | 15.477s | 11.251s |
| Ready workers through exact answer | 12.067s | 12.014s |
| Source checks through exact answer | 27.543s | **23.265s** |
| Including worker shutdown | 29.670s | **25.460s** |
| CPU final fiber/reconstruction attachment | 1.343s | 1.368s |
| Mean GPU kernel-active fraction, steady window | 98.68% | **99.24%** |
| All14simultaneously kernel-active, steady window | 84.74% | **91.54%** |
| All14simultaneously kernel-active, full GPU window | 82.84% | **87.46%** |
| Peak host RAM sampled | 6.39GiB | 6.45GiB |
| Largest per-worker GPU allocation pool | 1.83GiB | 3.34GiB |
| First compressed durable checkpoint flush | 1.119s | 0.852s |

The selected starting configuration is14resident workers,16roots/batch, packed
RAM inputs and two VRAM banks, with CUDA graphs executing32branches of87exact
elimination steps plus terminal contraction. The original modular CUDA step is
unchanged. Its terminal product and branch-shift accumulation are fused, and
every reconstructed coefficient and retained attachment agrees with the source.

The ready-worker execution duration is essentially unchanged between the two
runs. The lower second total mostly reflects initialization variability;
that reduction should not be assigned wholly to the larger batch. The measured
improvement in simultaneous14-worker activity is distinct from total runtime.
The full-window mean GPU activity is97.56%for8roots and95.83%for16roots:
coarser jobs improve simultaneous steady activity but leave a longer uneven
terminal tail. Steady mean activity and all-device concurrence measure different
aspects of the schedule.

[8-root analysis](graph1_ANALYSIS.json) and
[16-root analysis](graph2-b16_ANALYSIS.json) retain the complete timings,
per-worker counts, all14checks, exact trace coverage, cgroup counters and
checkpoint hashes. The steady window excludes the first and final one second
of the roughly10.53-second GPU work window; full-window metrics include both.

## Actual overlap and hardware use

This uses CUDA CUPTI concurrent-kernel records, not a host-process utilization
proxy. Every trace is aligned to host monotonic time. The8-root run retains
1,441,792records, and the16-root run720,896records; all14workers have zero dropped
records. Counts equal the executed batches times32branches times88kernels.
Kernel-active fractions mean that at least one kernel is executing on the
worker; they are not SM occupancy percentages. Parent-card management counters
are not attributed to the individual MIG slices.

Every GPU has work. The first run assigns288–296roots per device; the second
assigns288–304. Workers pull from one prime-interleaved queue, prepare packed
inputs for the next assignment while their current graph runs, retain maps and
allocation pools, and wait for result collection before shutdown. GPU work
runs concurrently; completed prime lanes trigger CPU inverse-NTT work as other
lanes finish. The CPU then performs exact CRT, gluing and the original
mathematical directional-fiber reconstruction.

The pod allocation is14Blackwell MIG1g.24gb devices,47.6CPU equivalents and
880GB (819.56GiB) of host memory. Both runs show zero CPU throttling. Independent
readback of every telemetry sample verifies that the one-GiB memory reserve
was retained. Detailed cgroup I/O deltas are reported separately by device;
layered-device counters must not be summed. The host workspace, projection
cache, root vectors, kernel traces, session state and telemetry use tmpfs.
Compact checkpoints are flushed after completion; there is no per-root
persistent file write.

## Comparison with the retained N96 pod run

The [previous eight-H100 run](../../SAM_REVIEW/campaigns/GEN3_POD_N96_H100X8_RUN1/RESULT.md)
completed in39.775s, including fresh roots and CPU fiber. Its runner supplied
independent persistent GPU owners, a shared prime-interleaved queue and resident
projection maps. Those source mechanisms are carried forward here, together
with the [N72 graph refinement](../frustrated_spin_n72_bench1/RESULT.md),
RAM-first checkpoints, packed preparation and double buffering.

The current best measured lifecycle is25.460s versus that recorded39.775s:
about1.56times the recorded throughput for this one source. Hardware, scheduling
and storage differ between the runs; this comparison is not an isolated
measurement of any one change. The current run also retains kernel tracing.

## Source, native route and custody

Source instance:
`625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d`.
All54retained capsule dependencies are checked before execution. CPU assembly
uses the original N96 authority and all14checks return true in both runs.
The off-pod analysis independently verifies all512/256batches, each of4096roots
exactly once, all14worker contributions, traced kernel counts and memory reserve.

Both calls use MATTER_SEARCH/GEN3-R4 on the pod's SLC-GEN4-P1 / SLC-GEN4-CE-P1,
generation GEN4-BLACKWELL-P1-20260922-G1. These are explicit source-bound GPU
successor adapters through DomainSession, with two native checkpoints. They do
not modify the global workstation SLC selector or the frozen original source.

The compact result archives, exact spectra/operator/fiber, native receipts,
all activity traces and telemetry are on the pod at
`/workspace/gen4/runs/n96-benchmark1/` and downloaded here with SHA256 verification.
[Run and recovery instructions](RUN.md) identify the retained source capsule and
successor implementation. Both N96 calculations are complete; all benchmark
workers have exited. The N2–N96 catalog has not been generated by these two runs.

For the tested exact fourteen-worker execution and overlap:
**The test result suggests strong contact with the concept.**

NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.
Helpful finding: the larger batch raises simultaneous steady activity above91%,
but its larger final work units reduce the average over the entire GPU tail;
the next useful scheduler refinement is smaller final batches while retaining
larger steady batches, if further optimization is requested.
