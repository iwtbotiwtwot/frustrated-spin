# N72 on the 14-worker GEN4 pod

Completed September 24, 2026 (Central). Forty-five fresh calculations of the same
72-spin, 180-edge frustrated-spin instance all reproduce the exact retained
spectrum and directional-fiber checks. The useful refinement is a persistent,
demand-driven GPU service with prepared RAM inputs, next-input VRAM buffering,
and overlapping CPU reconstruction. The full monitored data are in
[ANALYSIS.json](ANALYSIS.json).

| Execution | Fresh N72 calculations | Solver lifecycle, seconds | Ready-worker batch to all answers, seconds | Median subsequent answer latency, seconds |
|---|---:|---:|---:|---:|
| Baseline: new workers, 16 roots/batch | 1 | 15.036 | — | — |
| First persistent pipeline, early shutdown | 4 | 13.853 | 2.921 | 0.212; final answer delayed |
| Refined persistent pipeline, 16 roots/batch | 4 | 16.031 | 0.817 | 0.188 |
| Refined persistent pipeline, 32 roots/batch | 4 | 15.297 | 0.793 | 0.185 |

Lifecycle timing includes source checks/preparation, worker initialization,
arithmetic, exact reconstruction, directional fiber and worker shutdown. Python
process startup adds approximately 0.26–0.30 seconds; checkpoint flushing is
separate. Ready-worker timing begins after preparation and CUDA initialization.
The warm figures are not cold-start solve times. All forty-five runs perform new
root elimination; prepared inputs and source-derived fiber structure are reused
in the pipeline. No previously computed root vectors or spectra supply answers.

The selected successor uses 32-root batches and CUDA graphs: each worker
captures 68 exact elimination steps plus one exact terminal contraction, with
two VRAM banks. The original modular step is unchanged; the terminal product
is fused into one kernel and all exact retained outputs match.

Two further 16-calculation runs use actual CUPTI concurrent-kernel tracing:

| Kernel-level measurement | Demand pipeline | CUDA-graph successor |
|---|---:|---:|
| Warm time for 16 fresh N72 answers | 2.080 s | **1.658 s** |
| Average GPU kernel-active fraction, steady window | 93.05% | **99.45%** |
| All 14 simultaneously kernel-active, steady window | 38.50% | **92.62%** |
| All 14 simultaneously kernel-active, whole GPU work window | 31.57% | **90.94%** |
| Total solver lifecycle for 16 answers | 17.948 s | **16.064 s** |

The steady window covers trials 2 through 14 of 16; the full work window also
includes the initial GPU ramp and terminal GPU tail. These are actual kernel
execution-time fractions, not SM occupancy. All 14 CUPTI streams have zero
dropped activity records. The successor reduces the warm 16-answer duration
by 20.2%. Per-answer latency and multi-answer throughput remain different
measurements: median subsequent answer latency is0.177s while the mean batch
cost per answer is0.104s because work overlaps.

[Demand activity](trace1_CONCURRENCY.json), [graph activity](graph1_CONCURRENCY.json)
and the14raw kernel timelines are retained. The graph successor uses5.29GiB
of allocated VRAM per worker and4.02GiB peak sampled host RAM. Its median
interbatch host handoff gap is0.015ms;94.2%of CPU assembly time overlaps GPU
service intervals. Its first compressed checkpoint flush takes0.435s.

The completed N96 source was also inspected directly:8independent spawned
GPU owners, one shared queue with interleaved primes, resident projection maps,
and exact CPU inverse-NTT/CRT/fiber. It completed4096roots with32cutset branches
per root in39.775s on8H100s. That larger per-job arithmetic explains why its
work granularity differs from N72's1536single-branch roots; it is not a
linear runtime estimate. The retained N72 workstation median is36.639895s.


## Hardware and execution identity

User-supplied pod: `txqaltf4cdtfls`, authenticated through its RunPod SSH gateway.
The direct endpoint was verified against that gateway using a one-time shared
file before the approved source transfer. [Hardware receipt](HARDWARE.json):

- 14 CUDA-visible RTX PRO 6000 Blackwell MIG `1g.24gb` devices, each with
  25,367,150,592 addressable bytes and 46 multiprocessors; every device passed
  an exact arithmetic check. These are 14 GPU partitions.
- AMD EPYC 9355 host; 128 allowed logical CPU IDs, with a cgroup quota of
  47.6 CPU equivalents.
- 880,000,000,000-byte memory limit: approximately 819.56 GiB.
- 500 GB container filesystem; a 410 GiB tmpfs provides active RAM storage.
  The persistent volume has a 100 GiB application capacity policy; its reported
  petabyte filesystem capacity was not used as an available-space assumption.

The rebuilt pod runtime verifies 395 registry-bound files. It selects
SLC-GEN4-P1 / SLC-GEN4-CE-P1, generation GEN4-BLACKWELL-P1-20260922-G1.
MATTER_SEARCH retains its GEN3-R4 domain name on that GEN4 runtime.
The N72 GPU operation is an explicit source-bound DomainSession successor
adapter; the workstation global selector is unchanged. Six research calls and
six native checkpoints are retained in six verified sessions. The adapter
code and complete arithmetic dependency capsule are retained beside this report.

## What the monitoring found

The baseline used 1.146 seconds for source/projection preparation, 7.18–7.66
seconds per worker for device preparation, 0.416–0.462 seconds per worker for
its root batches, 0.085 seconds for CPU reconstruction and 0.748 seconds for
fiber preparation/assembly. Worker lifecycle costs dominated the single solve.

The first pipeline's last GPU batch finished at 0.779 seconds, but the CPU
received its complete last result only at 2.863 seconds as workers exited.
Keeping owners alive until result collection removed that delay. The preserved
first pipeline is a completed exact result and an observed scheduling issue.

The final 32-root pipeline computes four new spectra in a 0.793-second warm
window. After the first calculation, individual answer latencies are
0.1853, 0.1873 and 0.1849 seconds. Each warm CPU reconstruction takes
0.042–0.047 seconds and each fiber attachment takes 0.005–0.007 seconds.
Source-derived fiber preparation is done once before the measured warm window.

Measured CPU assembly intervals overlap GPU batch-service intervals for 76.8%
of their union duration, including the final CPU tail. The median gap between
successive batches on a worker is 0.092 milliseconds. All 14 workers receive
actual N72 arithmetic jobs. This is measured scheduling overlap, not a claim
that 76.8% of GPU multiprocessors are occupied.

Peak sampled host memory is 3.75–3.92 GiB over the four experiments. The shared
projection table occupies 144,818,176 bytes. The prepared source-factor bank
occupies about 5 MiB. No CPU throttling, memory-limit hits, or OOM events occur.
Full-lifecycle mean CPU use is 2.94–3.69 cores because initialization/teardown
and the short workload dominate; spare CPU capacity is available for larger
prepared workloads. The benchmark has no need to fill hundreds of GiB with
duplicate data.

All intermediate outputs, root vectors, projection maps, native session state,
CUDA cache and telemetry use tmpfs. Persistent writes happen at the completed
experiment checkpoint and final checkpoint. The first checkpoint flush is
0.35–0.56 seconds; the final 32-root experiment's first flush is 0.387 seconds.
Cgroup block counters show no new reads in the three refined experiments and
about 729 KB of writes on the container device, outside the RAM data plane.
Whole-container I/O counters can include background/driver activity and layered
block devices must not be summed. No evidence points to disk as the arithmetic
bottleneck in these runs.

Telemetry includes 100 ms cgroup CPU/memory/I/O/pressure samples, process CPU/RSS,
per-worker initialization and batch timing, CUDA event spans, allocation pools,
root coverage, CPU reconstruction/fiber spans, and checkpoint timing. Per-MIG utilization and SM occupancy were unavailable through NVIDIA's
management interface. Shared parent-card power/clocks are visible but were
not attributed to this allocation. The later CUPTI traces directly measure
concurrent kernel activity. CUDA event spans include launch gaps;
they are not isolated summed kernel-execution time or utilization percentages.

## L13/L14 mechanisms actually carried over

The directly consulted sources are [L14 demand-pipeline implementation](../l14_refine1/README.md),
[completed L14 analysis](../l14_complete1/RESULT.md) and the installed L14
`gen4/lx.py` admission logic. The N72 successor applies the useful mechanisms:

1. A finished worker immediately requests another queued batch.
2. CPU-created initial factors are prepared once in shared RAM, with explicit
   source identity, before consumers need them.
3. Each worker retains its CUDA context, projection maps and memory pool.
4. A second stream prepares the next batch in VRAM while current work is in
   flight; telemetry retains preparation and execution timestamps.
5. Completed results trigger CPU reconstruction while other GPU batches proceed.
6. Worker shutdown waits for all answers to reach CPU assembly.

The finite benchmark queue contains only the authorized N72 repeats. Empty
queues end the benchmark; no unrelated workload is generated to raise activity.
For the planned catalog, keep this service warm across useful queued instances,
prepare compatible sources ahead in RAM, and flush compressed checkpoints at
source/result boundaries. Generalizing the source family and its operator
compiler remains the next task; this benchmark uses the fixed N72 source.

## Exact result and custody

All 45 calculations close 2^72 = 4,722,366,482,869,645,213,696 configurations,
with 263 occupied energy bins and an 871-slot coefficient vector. Every
calculation checks all three prime lanes, all sixteen retained-port rows,
exact coverage, final coefficients and the retained T18 attachment.
Source: `396778a771378af50f7f6cbe594d93245fb0b653aef3f7a91b142c1e51fe450b`.
Coefficient hash: `06c8e85ea8deca940be49190b91d8f5a028338a4b1add1c62256e22017f2c353`.

The baseline, first pipeline, corrected pipeline and batch-size refinement
remain separate and immutable result directories. Their compressed checkpoints
have been downloaded and SHA-256 verified. `analyze.py` reconstructs the analysis
from these retained outputs without executing the spin calculation again.
The pod retains checkpoints at `/workspace/gen4/runs/n72-benchmark1/` and the
new installation at `/opt/gen4/current`. Source inputs are archived locally;
checkpoint custody and restart instructions are in [RUN.md](RUN.md).

All N72 benchmark workers are finished. The next owner-authorized task is the
original N96 benchmark on this pod; it is tracked separately.
For the tested 14-worker execution and overlap:
**The test result suggests strong contact with the concept.**

NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.
Helpful finding: keeping workers alive through result delivery matters as much
as keeping them alive between calculations; early teardown alone added more
than two seconds to the final answer in the first pipeline.
