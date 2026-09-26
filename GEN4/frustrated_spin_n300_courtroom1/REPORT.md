# N300 packet-family courtroom test: complete report

**Originator and conceptual director: Sean Brady.** AI research collaborators: OpenAI ChatGPT and Codex.

## Result

The precommitted under-25-ms warm-median prediction was met for the original packet N300 source and both prespecified signed extensions on the workstation. Every computed full spectrum matched an independently executed full-graph variable-elimination reference. All six deliberately wrong controls were detected.

**The test result suggests strong contact with the concept.**

This is a measured result for three explicit 300-spin packet-family graphs, including one connected frustrated graph. All first N300 solves were below 25 ms. The primary endpoint was the median of 31 repetitions per source; nine of the 93 individual warm trials exceeded 25 ms. Every trial remains in the record.

## 1. Owner question and frozen translation

The owner requested a courtroom-style test with a precommit, wrong controls, provenance, and a prediction that N300 would complete in less than 25 ms based on the recent N1–120 packet-family results. The test translates that into the same warm exact-solve timing scope used in the preceding catalog, on the workstation CPU. The original packet family is the primary prediction; the signed and connected signed families each have a separately registered prediction under the same threshold.

The protocol was written before target execution. No target-size warmup, source tuning, discarded timing, or post-result algorithm selection was allowed. Exactly 31 warm solves per family were scored. The later boundary-equality optimization was a separately registered secondary measurement and never substituted for the primary result.

## 2. Prediction and observed timings

| Family | Predicted size-scaled median (ms) | First solve (ms) | Warm median (31; ms) | p95 (ms) | Maximum (ms) | Below 25 ms | Prediction |
|---|---:|---:|---:|---:|---:|---:|---|
| packet | 15.554 | 22.449 | **16.993** | 25.413 | 28.475 | 28/31 | MET |
| signed_packet | 15.983 | 16.431 | **17.123** | 29.021 | 29.403 | 28/31 | MET |
| signed_packet_chain | 17.120 | 23.411 | **20.423** | 31.814 | 32.674 | 28/31 | MET |

The p95 is the nearest-rank sample percentile, rank 30 of 31. No estimate of an all-runs-under-25-ms guarantee is made. The sample medians answer the registered question; the tails remain visible.

The prior pod N120 medians were 6.222, 6.393 and 6.848 ms. Multiplication by N300/N120=2.5 gave 15.554, 15.983 and 17.120 ms. Larger integer coefficients/output and hardware differences were identified before execution; the registered ceiling was 25 ms. These predictions were not fitted to the N300 observations.

## 3. Secondary timings and reference cost

| Family | Empty-cache median (5; ms) | Independent full-graph VE (one solve; ms) |
|---|---:|---:|
| packet | 21.059 | 105.322 |
| signed_packet | 21.683 | 111.105 |
| signed_packet_chain | 25.718 | 93.409 |

The separately scored connected boundary-equality refinement had an eleven-run median of **17.917 ms**. The primary connected result remains 20.423 ms. The connected empty-cache median was 25.718 ms, so the warm-cache condition materially matters at the 25-ms threshold.

The single reference timings establish the executed comparison route; they are not multi-repetition median estimates. Empty packet cache means recomputing local packet spectra in an already running process. It does not include process startup.

## 4. Explicit source construction

Each source preserves its corresponding first 120 vertices, fields and interactions from the completed packet catalog. Twelve additional 15-spin packets are copied from the source-bound three-layer motif, giving twenty packets at N300. Every layer is K5, with perfect-matching edges between adjacent layers. All primary fields are zero. Ordered retained ports are [0,1,60,61].

| Family | Vertices | Interactions | Connected components | Frustrated triangle witnesses |
|---|---:|---:|---:|---:|
| packet | 300 | 800 | 20 | 0 |
| signed_packet | 300 | 800 | 20 | 60 |
| signed_packet_chain | 300 | 819 | 1 | 60 |

The signed graphs retain one negative edge per five-spin layer. The connected graph carries 19 signed gateway bridges as explicit interactions. Its full energy spectrum includes all 819 interactions. No existing canonical graph was altered. No source for N121–144 was generated or solved.

### Exact output summaries

| Family | Ground energy | Ground degeneracy | Occupied scalar DOS bins | Total configurations |
|---|---:|---:|---:|---|
| packet | -800 | 1048576 | 556 | 2^300 |
| signed_packet | -680 | 1048576 | 559 | 2^300 |
| signed_packet_chain | -699 | 2 | 580 | 2^300 |

Full coefficients and all sixteen conditional spectra are retained; the table is only a summary.

## 5. Exact computational route

The copied, frozen packet compiler verifies every vertex and every edge against an explicit packet partition. Local polynomial tables are keyed by complete integer fields, couplings and ordered local ports. All local tables needed for N300 were already present in the independently verified N1–120 cache; no complete N300 result was in that cache.

Independent packets combine through polynomial powers and balanced products. Connected packets sum over both gateway-spin values, retaining each bridge energy. FLINT integer polynomials preserve exact coefficients. The compiled output is converted to complete energy/count lists, then count, first-moment and second-moment checks run and the full answer hash is generated.

The independent oracle contracts the full graph with variable elimination, separately from the packet compiler. All scalar coefficients, ordered conditional rows, configuration counts and energy moments match. Each timed output matches the family output later compared with the oracle. Zero-glue open operators are reconstructed and round-tripped to every closed row.

## 6. Wrong controls and what they detected

| Wrong control | Expected failure | Observed outcome |
|---|---|---|
| Changed source with stale plan | Reject source/plan mismatch | Rejected before table reuse |
| Extra cross-packet edge absent from interfaces | Reject incomplete edge partition | Rejected by compiler |
| Positive packet tables forged under signed keys | Reject incorrect spectrum | Full coefficient comparison rejected; count/moment checks alone passed |
| Third-finite-difference coefficient corruption | Reject wrong coefficients despite preserved moments | Rejected by full equality; counts and first two moments passed |
| Swapped unequal conditional rows | Reject wrong ordered observable | Ordered-port comparison rejected; scalar DOS was unchanged |
| Nonzero field breaks gateway equality | Decline invalid symmetry collapse | Declined; full two-state result matched independent VE |

The moment-preserving corruption used energy bins −674, −672, −670, −668 and coefficient changes [1,−3,3,−1]. Nonnegativity and zeroth/first/second moments remained intact. This is executable evidence that full coefficient/observable checks add information beyond moment closure alone.

Altered sources, forged outputs, exact exceptions and fallback results are in WRONG_CONTROLS.json and artifacts/CONTROL_*.json.gz. Wrong controls were excluded from timing statistics.

## 7. Timing and hardware contract

Host CPU: Intel Core i9-12900HK. One serial coordinator, existing SAM resource-manager budget, affinity [4, 5]. No GPU was used. No GPU/CPU clock setting was changed. Thread settings and complete budget are retained in EXECUTION_ENVIRONMENT.json.

Clock: clock_gettime(CLOCK_MONOTONIC), resolution 1e-09 seconds. Python perf_counter_ns bracketed each solver call. Python process/FLINT startup and cache file loading occurred before target timing.

Included: source-record binding, full exact composition, all scalar/port output construction, integer/string conversion, answer hash, count and moment checks. Excluded and separately retained: source compilation, independent output comparison, process startup, native receipts, output persistence and zero-glue open-operator export. This is the same scope used for the preceding packet-catalog warm timings.

The operator order was deterministic and cyclically balanced across families. The first solve of each family was scored. There was no N300 warmup. Frequency/OS scheduling variation was not attributed to a specific cause; all observed timing variation remains in the dataset.

Peak process RSS reported by the operating system: 86956 KiB.

## 8. Precommit and provenance chronology

- Protocol seal: `2026-09-26T20:36:56.003210+00:00`.
- Separately stored witness receipt: `2026-09-26T20:38:13.802599+00:00`.
- First target solve announced in the chained ledger: `2026-09-26T20:38:39.712051+00:00`.
- Protocol SHA-256: `d9ed0b03d6c2e7a75698337ec149af00ceed7b2811955350a6e3c6da2086372f`.
- Precommit manifest SHA-256: `25ec51a7b6d07b25248a87bd46dbb29169dd565747f07ec2b4b17400c5f522c2`.
- Precommit archive SHA-256: `aaadb98c58ac7fc56b0879bcd610d0f7650d0efdf7c77b0fbfc6e1da05e773ff`.

The frozen manifest binds code, sources, inherited inputs, cache bytes, prediction, protocol and runtime preflight. The unchanged-manifest check passed after execution. The event ledger records every scored duration in a SHA-256 chain. The witness copy was stored on the pod before the first target solve; it is separate custody rather than an external trusted timestamp service.

One setup incident is preserved: the pod volume rejected chmod, leaving the initial witness receipt incomplete. The first local launch stopped at that witness gate before a native session or N300 calculation. The witness receipt was then completed using content hashes. No frozen source, algorithm, threshold or trial protocol changed; no target timing was discarded. See PREEXECUTION_INCIDENT.json and PREFLIGHT_ATTEMPT1.log.

## 9. Native execution and reproducibility

MATTER_SEARCH Domain, SLC-GEN4-P1 — verified; CE: SLC-GEN4-CE-P1; domain engine: GEN3-R4; Chalkboard: OFF (owner-suspended)

Session: `/home/sam/PycharmProjects/SAM_Research_Project/GEN4/frustrated_spin_n300_courtroom1/sessions/MATTER_SEARCH_a405606d6bd44af7adfdfa9b8295c254`.

The five source-bound operations execute qualification, warm timing, independent references, secondary timing and wrong controls. Native call receipts and a final checkpoint are retained under sessions/. No hosted subagents or additional hosted-model calls were used by the executable campaign.

Use the existing resource manager for any separately named reproduction. The sealed runner deliberately refuses to overwrite this scored run or an existing event ledger. A new timing study must use a new output project and a new precommit. document.py only reads retained results and never re-executes calculations.

## 10. Interpretation and next use

All three registered median predictions met their threshold, full exact outputs agreed with independent calculation, and all wrong controls were detected. The connected frustrated case retains millisecond performance through bounded interfaces, even at N300. The results support extending source-bound packet composition as a computational capability.

The control outcome is also useful for GEN4: counts and low moments alone can accept wrong spectra and wrong port assignments. Complete coefficient and ordered-observable verification must remain attached to any proposed reduction.

The original canonical frustrated frontier graphs have different interactions. Their decomposition remains a separate research target. The training campaign stays paused; no global rule, selector or prior answer was rewritten.

## 11. Evidence index

- [Frozen protocol](PROTOCOL.md), [precommit](PRECOMMIT.json), [seal](PRECOMMIT_SEAL.json), [frozen manifest](FROZEN_MANIFEST.json), [witness](WITNESS.json).
- [Scorecard](SCORECARD.json), [all timings](TIMINGS.csv), [raw results](RESULTS.json), [final verification](FINAL_VERIFICATION.json).
- [Source records](sources/), [exact spectra and wrong controls](artifacts/), [native receipts](sessions/).
- [Runtime preflight](RUNTIME_PREFLIGHT.json), [execution environment](EXECUTION_ENVIRONMENT.json), [event ledger](EVENTS.jsonl).
