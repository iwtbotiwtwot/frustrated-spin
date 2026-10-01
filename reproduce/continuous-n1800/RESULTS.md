# Results: continuous N1–1800 exact g(E,M,b)

The completed catalog contains 1,800 sizes and 10,800 labeled cases. Its primary joint-support sum is 118,387,509,614. Every size has both fill signs for all three source families. The source-bound per-size and per-case tables are INDEX.json and CASES.csv.

## Production batches

| Range | Sizes | Workers | Seconds | GPU service requests |
|---|---:|---:|---:|---:|
| 1–100 | 100 | 8 | 14.989184 | CPU route |
| 101–500 | 400 | 16 | 2790.049861 | CPU route |
| 501–1000 | 500 | 16 | 11658.632146 (last sampled) | Counter unavailable after stop |
| 1001–1408 | 408 | 24 | 10630.406660 | 78336 |
| 1409–1456 | 48 | 24 | 2678.580908 | 9216 |
| 1457–1504 | 48 | 24 | 2990.495370 | 9216 |
| 1505–1552 | 48 | 24 | 4678.634886 | 9216 |
| 1553–1600 | 48 | 24 | 5529.880132 | 9216 |
| 1601–1648 | 48 | 24 | 5985.270313 | 9216 |
| 1649–1696 | 48 | 24 | 6239.790212 | 9216 |
| 1697–1744 | 48 | 24 | 6553.860213 | 9216 |
| 1745–1800 | 56 | 28 | 9039.131238 | 10752 |

N501–1000 is separately preserved as an owner-stopped, verified 500-size completion. Its last sampled elapsed time was 11,658.632146 seconds with 16 workers. The live aggregate GPU counter was unavailable after stop; it is not filled in from the expected request count. See evidence/N0501-1000-SUMMARY.json. An extra completed N1001 from that interrupted run remains in research custody; the contiguous publication selects the later N1001–1408 production record consistently.

Batch times describe their stated compute runs; transfer and publication times are separate. Worker topology and source sizes changed across campaigns.

## Final N1745–1800 batch

All 56 sizes passed: 336 cases,10,752GPU requests,9,039.131238 seconds (2h30m39s). Retained scientific files occupied748,489,954 bytes. Maximum worker-lifetime RSS was3,538,919,424 bytes; swap use was zero. The complete hypothetical headerless output in both encodings would be4,941,192,052,912 bytes. No full expanded nonmilestone table was written.

The native controller completed at 22:29:04 CDT on September 30, 2026. Final T500 verification preceded confirmed provider stop at 22:30:54 CDT. The final custody archive was 4,454,669,000 bytes and covers the latest extension plus supporting source/operational files. It is distinct from the larger all-range compact publication and earlier full milestones.

## Accounting and interpretation

Across all 1800 sizes, the comparable headerless expanded output in both encodings would occupy 42,030,624,816,236 bytes. This is calculated output volume, not an archive size or number of publicly stored coefficients.

At N1800 each complete graph has 1,619,100 pair positions; each four-port boundary contains 2^1796 configurations. Six case labels and 16 boundaries give 96 boundary rows per encoding at this size. Lower-N boundary counts follow the actual source ports.

Exact integer densities and certified finite-precision thermal readouts are distinguished in METHODOLOGY.md. The data derive from the stated structured source families. Literature comparisons must retain graph, observable, arithmetic and retention scope.

## Preserved operational findings

The GPU pipeline qualification initially found workers using private backends rather than the intended shared service; the corrected qualification enforces per-request service use. The N1000 resume comparison distinguished warm/cold cache counters from mathematical equality. The first 24-worker N1745–1800 attempt ended before any size completed; the published result is the completed 28-worker attempt. A later collection-controller admission typo was corrected without restarting scientific workers. None of these interrupted operational attempts is included as an additional successful data point.
