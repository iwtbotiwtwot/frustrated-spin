# Exact N120 frustrated-spin result

**N120 completed exactly in773.240389397seconds:12minutes53.24seconds.**

**The test result suggests strong contact with the concept.**

The frozen source has120spins/300couplings, is connected and five-regular, and
contains frustrated signed cycles. It extends the current N96family by preserving
228oldcouplings and all96oldfields, replacing12disjoint edges with24crosslinks
to a fresh24vertex/four-regular block. Every change is in SOURCE.json. The source
was frozen before structural search or numerical evaluation. Earlier N105packet
and N120ring results remain separate families.

| Exact result | Value |
|---|---:|
| Configuration count | 1329227995784915872903807060280344576 =2^120 |
| Ground energy | -434 |
| Ground degeneracy | 8 |
| Occupied energy bins | 435 |
| Highest occupied energy | 434 |
| Retained port states | 16 |

Energy convention:E=−sum(J s_u s_v)−sum(h s_u), with spins±1. Full scalar DOS,
all16open port polynomials, all16closed conditional spectra and exact coefficients
are retained in results/ram/RESULT1.json.gz. The five-prime CRT modulus exceeds
2^120. Total counts, first/second energy moments, individual port counts and
polynomial support all pass. This computes the full distribution by exact
elimination and modular reconstruction; it does not enumerate2^120assignments.

Source SHA256:`bed8dbc542412f88a76795573e157e369710a0bcf8d2b7358e10a159d98df1f4`.
Spectrum SHA256:`04088a31a81a8424ec44bd8a582dffabd795ec2ba3bd127a9826e46aa228f254`.
Retained result:`c666aea038e62765896f9ae62a2a6be446e2df4c6cdd83f9f5f1790b47688ee4`.
Native session:`/dev/shm/gen4-spin-n120-frontier1/sessions/MATTER_SEARCH_38ef4f61dc5441f4980fbd0e55bad5bf`.
MATTER_SEARCH/GEN3-R4 onSLC-GEN4-P1/SLC-GEN4-CE-P1;Chalkboard OFF.

The CPU searched elimination/cutset plans for300.315419136seconds separately.
Selected plan:width21 after conditioning11spins,2048branches,1024roots and5primes.
The initial usable plan had83991560192weighted entries;the chosen plan has
47476187136. This is a selected heuristic elimination width, not a minimum-width
certificate. RAM templates/maps prepared in0.992seconds.

The fresh solve includes0.527213205seconds GPU preparation and772.666548321seconds
modular work/checkpoint handling; exact reconstruction took0.046110634seconds.
Five-minute planning and the training wait are separate from773.240389397seconds.
N30qualification/warmup took8.484501620seconds, using32conditioned branches/two
groups to exercise graph reuse; every coefficient matches the saved exact source.
The CRT qualification also recovers a coefficient exceeding four-prime capacity.

Fourteen persistent CUDA workers share40960tasks,each covering16roots and16cutset
branches. GPU graphs and output buffers are reused across branch groups. Each
prime/root/group task contributes exactly once; coverage is complete and no
restart was needed. Compact modular sums/coverage flush approximately every30s;
full traces/native receipts flush at completion. Peak host cgroup use
29.140GiB includes the earlier training closeout and waiting period.
Per-worker GPU memory pool was2.996GiB.

| Whole modular phase kernel activity | Value |
|---|---:|
| Average active time per worker | 99.0091% |
| All14workers active simultaneously | 90.7437% |
| At least13workers active | 99.0340% |
| CUPTI kernel records, including qualification | 69496320 |
| Dropped records | 0 |

These are actual kernel-active durations, not SM occupancy. CUPTI
CONCURRENT_KERNEL start/end records are aligned to host monotonic time, reduced
to interval unions per worker, then swept for simultaneous activity across14.
All arithmetic time, including checkpoint stalls, is included. The first analysis
assumed non-overlapping worker intervals; its diagnostic was retained and the
analysis corrected to union overlapping kernels. This changed only trace analysis.

The user observed a near-zero live GPU display. A direct NVIDIA query returns
N/A for GPU and memory utilization on all6physical GPUs with MIG enabled. The
dashboard's precise N/A handling was not inspected. The kernel records establish
that the displayed zero did not describe execution activity.

Final archive:completed.tar.gz,723534861bytes,
SHA256`6c969f4a35b50a016b55fefd7cff2f1b4e3b9f78f2a4b33700a282bb66ce49d0`;
copied offpod and verified. CONCURRENCY.json is a separately retained post-run
analysis of those archived traces. All14calculation workers stopped cleanly.
The initial waiting setup was replaced before GPU work to strengthen the branch
reuse check;both native sessions and setup evidence remain.

[Training results](../frustrated_spin_focused_training1/RESULT.md) and
[portable restart](../frustrated_spin_focused_training1/RESTART.md) preserve the
learned policies,source code,runtime,arithmetic dependencies and exact results.
The additive installation stores this source/spectrum/plan and its real96→120
transition;the oldfour-port N96spectrum alone is insufficient for the24touched
old boundary vertices. No frontier timing model is inferred from a single solve.
