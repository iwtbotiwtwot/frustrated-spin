# Focused frustrated-spin training — completed

**The test result suggests strong contact with the concept.**

Both GPU passes completed300fresh solves across100distinct plans and37explicit source groups, plus one warmup each. Both CPU boundary campaigns completed540exact advancement steps and234fresh restarts each (468timed comparisons each). Exact spectra and every retained port operator agree across methods. A direct cross-backend comparison also matches all37sources coefficient-for-coefficient (`CROSS_BACKEND.json`). Two rewired fullN96sources remained outside the campaign scheduling envelope, with all candidate plans and reasons retained; no work was silently omitted.

The six related topology families share the original N96ancestor. Whole families0–2train,3selects models,4–5are reserved. Models and all reserved predictions were frozen before reserved timings. Each distinct plan has three rotated measurements.

| GPU backend | Cost policy fastest | Native pairwise fastest | Structural fastest | Cost selected / best possible (s) | Pairwise depth |
|---|---:|---:|---:|---:|---:|
| Retained scalar readout | 8/9 | 6/9 | 7/9 | 33.153472875 / 33.144121434 | 3 |
| Batched exact readout | 8/9 | 8/9 | 7/9 | 23.290642924 / 23.238427899 | 1 |

Ridge component-cost regression (alpha0.1) won development selection for both backends. Reserved mean absolute fractional timing errors were7.14% and10.36%. Regression uses NumPy CPU; pairwise CART uses native C++/GMP. The faster pairwise model uses difference+A+B features and learns a nonconstant depth-one ranking.

| Original N96 plan/readout | Three-repeat median solve (s) |
|---|---:|
| Fresh min-fill, retained readout | 11.202180587 |
| Prior six-seed portfolio, retained readout | 8.226796205 |
| Expanded plan, retained readout | 4.761149127 |
| Same expanded plan, batched readout | 3.257604178 |

The expanded N96plan uses16conditioned branches atwidth21 rather than32branches. Its one-time search takes about6seconds and is separate from solve latency. Retaining identical-source plans removes that search cost from reuse. The six-source readout qualification uses independently retained inverse transforms and full coefficient/operator equality; N96readout alone changed1.4346s→0.01482s in the isolated comparison. Full solve gains are reported separately above.

| Boundary backend | Fastest reserved choices | Selected (s) | Always restart (s) | Always reuse (s) |
|---|---:|---:|---:|---:|
| Retained | 20/26 | 1.587820826 | 3.126587324 | 1.986290889 |
| Batched | 26/26 | 0.060041617 | 0.061936855 | 1.945176127 |

The batched boundary policy selected24restarts and2incremental steps. Backend speed changed the best transition method: models must be calibrated against the actual execution path. These timings are marginal operations once the previous future-facing state exists; they exclude its construction. Six explicit N30horizons retain all incoming-state features and exact source ancestry.

RAM/VRAM hold work; compact checkpoints flush at source boundaries. Peak cgroup host use was24.03GiB in the retained pass and29.10GiB in the faster pass, including shared pod state. No requirement to fill available RAM was introduced. All14workers stop at each campaign end. Kernel-overlap evidence is in `focused-results_CONCURRENCY.json` and `fast-results_CONCURRENCY.json`.

The original retained publication encountered the canonical schema rejecting floating model parameters. All completed calculations and frozen evaluations remain unchanged; a separate publication session encodes float64 parameters losslessly as tagged hexadecimal strings. The faster successor uses this encoding from the start. The early CPU import failure and corrected rerun are also preserved.

The exact N120 frontier completed in773.240389397seconds using five primes and reusable branch groups. [N120 result](../frustrated_spin_n120_frontier1/RESULT.md). Focused models,38source plans,the new N120entry and96→120transition are installed on GEN3/GEN4;49adoption/recovery checks pass on each. [Installation](../frustrated_spin_focused_install1/RESULT.md).

Verified local archives:

- `focused-completed.tar.gz`:c12e171048baaf18a2c0285fcc956b3ea6a94c7d41b7937d27e7bdd540fee172
- `fast-completed.tar.gz`:19122a2f92e81ae35336c7b75089e658ad7aac69e22e9f1dc596da17e00ad8ae
- `boundary-completed.tar.gz`:c252aec179eb3d5ac116aaad065759c34b07b202dd9968faa9abda95e9cb4e91
- `boundary-fast-completed.tar.gz`:9b3f5fb3eefcc8f93f40bb58cffb412583df1eef7235bccf085b70a20a212032

Native sessions, receipts, source bindings, exact spectra, learned parameters, evaluation splits, telemetry and traces are inside the respective result folders. [Portable restart](RESTART.md) preserves the runtime and source dependencies.
