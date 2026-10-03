# Exact coefficient batching and N20000 completion

**Batching produces363times as many N10010counts for only44.4%
more total GPU-route time. All1296N20000counts now agree exactly with the
independent CPU recurrence.** Prior scientific artifacts are unchanged.

| N | Requested counts | GPU route seconds | Transforms/transfer | CRT/root |
|---:|---:|---:|---:|---:|
| 10,010 | 48 | 5.7592 | 5.7188 | 0.0355 |
| 10,010 | 1,296 | 5.9593 | 5.7251 | 0.2292 |
| 10,010 | 17,424 | 8.3164 | 5.7352 | 2.5759 |
| 20,000 | 1,296 | 53.5532 | 52.7388 | 0.8055 |

GPU route includes modulus planning, transforms, selected transfer, CPU exact
CRT and root contraction. Initialization0.799314s
is separate. Same-pod independent CPU recurrence: N10010wide window
81.226677s; N20000window
812.311829s. CPU/GPU N20000 ratio
15.17x relative to that recurrence.
Two independent CPU workers ran concurrently with GPU work, on separate cores.
This is a bounded batch measurement; no extrapolated throughput is substituted.

There are18720unique independently compared records; nested smaller batches
bring the record comparisons and reversal checks to20064.
The old48N10010reference also matches. Exact polynomial divisions:
N10010=1183,N20000=2337.
N20000uses k9996..10004 (M-8..8), d2329..2337,all16boundary states.
Largest N10010window uses k4989..5021, d1151..1183.

N20000transform length134,217,728;328prime moduli;
276transferred intermediate coefficients;
724,224residue bytes. Measured live CuPy array
pool peak2,684,361,216bytes, not full-device process peak.
Full modular transform vectors are retained; the saving is selected transfer
and exact reconstruction, not a sparse transform algorithm.

The measurement identifies CPU CRT/root work as the growing batch cost.
The companion [normalization study](../spin_normalization1/REPORT.md) shows
why physically chosen windows matter: the old central window contains an
extremely small Gibbs mass under fixed-strength frustration. A useful next
GPU batch should follow that thermal distribution.

## Hardware, execution and custody

Pod213.192.6.70:40117;RTX PRO6000Blackwell Workstation Edition;EPYC9575F;
31.13CPU equivalents;124999999488-byte memory limit;500G container disk.
GPU hostCPU0;independent CPU workers1/2. Python3.12.3,CuPy13.6.0,
python-flint0.8.0,retained CUDA12.8 runtime and unchanged exact CUDA kernels.
Raw source identities, moduli, timings and output records are retained.

STARBREAKER/SB-GEN3-ACCUMULATION-R1 through SLC-GEN3-R4/SLC-GEN3-CEV1-R4;
source-bound SPIN_GPU_BATCH adapter, native result/export/checkpoint receipts.
Local controller uses the project resource manager. Companion thermal/readout
controllers share its existing sam-r3.slice budget; pod thermal workers use
separate cores4–15. No generic-engine promotion, helper compute, Chalkboard
activation, prime-event change or automatic successor.

All9remote output/log hashes match direct T500 copies. Bulk and native sessions:
/home/sam/mnt/lilhelper-t500/GEN4/spin_gpu_batch1. Archive/readback details are in CUSTODY.json. Pod originals remain;
T500originals and archive share one physical disk. Workers complete, pod rented.
This is selected exact g(E,M,b) through N20000, not an expanded full table.
