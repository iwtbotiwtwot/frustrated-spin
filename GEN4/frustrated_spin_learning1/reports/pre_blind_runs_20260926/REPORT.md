# GEN4 frustrated-spin research: complete report through the pre-blind runs

Prepared 26 September 2026. **Originator and conceptual director: Sean Brady. AI research collaborators: OpenAI ChatGPT and Codex.**

This report brings together the atlas-building and method-training results that supplied the learning program, the first N1–120 workstation learning campaign, its outcome-driven follow-up, the ten-worker and twenty-worker pod continuations, the fourteen-worker restoration tests, and the stopped podrun3 continuation. The cutoff is the launch of `blind_restart1` at **2026-09-26 17:23:29 UTC**. That current run's results are excluded from the historical totals; its initialization is documented at the end.

The report is a synthesis of saved sources, exact results, timing scorecards, question ledgers, state checkpoints, and installation reports. No new spin calculations were performed to write it. Prior results and controller code were not changed.

## Contents

1. Results across the program
2. Run chronology and accounting
3. Atlas construction and earlier training
4. What source structure explains about cost
5. N100/N105: packet structure and measured methods
6. N96/N120: frustrated-source scaling and execution
7. The first workstation learning campaign
8. The self-follow-up campaign and its seven certificates
9. Ten-worker pod continuation
10. Twenty-worker pod continuation
11. Fourteen-worker restoration and podrun3
12. Method-by-method findings
13. Autonomous follow-up: what it actually did
14. Failures, corrections, and retained counterexamples
15. What is installed, retained, and proposed
16. Holdout predictions and the fresh-run boundary
17. Connections and remaining research questions
18. Full atlas and GPU measurement appendices
19. Evidence, reproduction, and storage

## 1. Results across the program

The program now has a completed contiguous canonical N1–120 atlas, multiple exact routes, measured method comparisons, source-specific reusable plans, and a substantial record of same-N interventions. Its clearest operational result is that source structure and execution backend jointly determine the useful method. The integer N is insufficient to make that choice.

The packet-family N100 and N105 sources split into eight small components, with largest component 15. Their local enumeration requirements differ by just 992 assignments despite the five-spin increase. New matched workstation measurements then show that polynomial variable elimination is faster than rebuilding those component tables, while exact warm component-table reuse is faster again. This connects a structural explanation to an actual route choice.

The connected N96 source benefits from a different reduction: changing its conditioned elimination plan reduces branches and factor work. The progression from fresh min-fill through the expanded plan, combined with batched exact readout, reduced the three-repeat median from 11.2022 seconds to 3.25760 seconds in the focused campaign. The restored fourteen-worker run reproduced the expected warm timing at 3.40756 seconds. A subsequent matched-source comparison also measured the expanded plan's approximately threefold arithmetic advantage over the older plan.

N120 extends N96's frustrated source. It completed full exact density and retained-port calculations in 773.240389397 seconds. Its work is explained by conditioning 11 spins, 2,048 branches, width 21, 1,024 roots, and five CRT primes. The N97–119 completion campaign then filled the contiguous atlas using explicit N120-prefix sources while retaining the older packet N100/N105 defaults.

The self-follow-up program added repeated CPU method comparisons, exact component reuse, bridge controls, same-N rewiring, separator searches, and seven explicit sign-bijection certificates. Later pod runs expanded separator admission and GPU measurements. Configuration changes and implementation failures are recorded below with their effects on execution, rather than folded into the scientific results.

The material is usable in three forms: exact source/result objects, learned route/cost evidence, and project-local reduction implementations. These are distinguished throughout so a saved exact answer, a timed comparison, and a structural planning result can each be used appropriately.

## 2. Run chronology and accounting

All dates in this table are 26 September 2026, UTC. Chicago was UTC−5. Durations run from the saved start/restoration timestamp to the last saved update; they are controller windows, not summed solver arithmetic.


| Run | Start UTC | Last update UTC | Minutes | New completed questions | Recorded attempted IDs | End state |
|---|---|---|---|---|---|---|
| workstation1 | 2026-09-26T06:12:11+00:00 | 2026-09-26T06:32:26+00:00 | 20.244 | 407 | 438 | NO_ADMISSIBLE_QUESTION |
| followup1 | 2026-09-26T06:51:21+00:00 | 2026-09-26T07:48:09+00:00 | 56.7943 | 1476 | 1682 | SEARCH_SATURATED |
| podrun1 | 2026-09-26T13:19:52+00:00 | 2026-09-26T13:31:56+00:00 | 12.0691 | 637 | 717 | SEARCH_SATURATED |
| podrun2 | 2026-09-26T15:47:44+00:00 | 2026-09-26T16:14:46+00:00 | 27.0369 | 571 | 673 | RUNNING |
| podrun3 | 2026-09-26T16:49:43+00:00 | 2026-09-26T17:03:17+00:00 | 13.5697 | 11 | 14 | STOPPED |

The five learning stages contain **3,102 completed question records**: 407 + 1,476 + 637 + 571 + 11. They include planning, analysis, certificates, paired measurements and exact GPU questions; this total is not a count of distinct spectra. Earlier atlas-production/training campaigns are listed separately and are not added to this total.

Accounting details:

- The first workstation ledger also contains three smoke attempts under one question ID: two setup failures followed by a successful N6 check. Its 438 production attempts and 407 completed questions exclude those smoke attempts.
- Podrun1 records 717 attempted IDs: 637 complete, 74 failed/capacity-bound, and six setup interruptions.
- Podrun2's last `STATUS.json` is older than its saved `STATE.json`: status says 563 complete/665 attempted, while the state retains **571 complete/673 finished attempts**. The state and 673 result events agree. There are also eight later precommits without final result events in that copied ledger. Its old `RUNNING` label is a historical snapshot, not a claim that this process remains active.
- Podrun3 imported the podrun2 checkpoint containing 571 completed questions but saved **11 newly completed questions** in its own completed map. Its summary's 105 failed/capacity-bound total includes 102 inherited failures. The new ledger has 14 attempts: 11 complete and three failed/interrupted. Those inherited records are not counted again here.
- Exact repetitions and alternative methods within one question are separately represented in scorecards. Question totals therefore differ from arithmetic-call totals.

The complete production question inventory, including unfinished precommits, is in [ALL_QUESTIONS.csv](ALL_QUESTIONS.csv). Every saved event, including smoke/setup history and parent/child references, is preserved in [ALL_EVENTS.jsonl](ALL_EVENTS.jsonl).


| Run | Completed work by kind |
|---|---|
| workstation1 | solve: 140, plans: 145, component_rule: 120, atlas: 1, analysis: 1 |
| followup1 | paired: 573, planning: 896, gauge_certificate: 7 |
| podrun1 | planning: 313, paired: 105, separator_frontier: 206, gpu_test: 13 |
| podrun2 | separator_frontier: 206, paired: 318, planning: 18, gpu_test: 29 |
| podrun3 | paired: 9, gpu_test: 2 |

## 3. Atlas construction and earlier training

### 3.1 Original eleven-size catalog

The initial ladder explicitly calculated N2, 8, 12, 18, 24, 36, 48, 60, 72, 84 and 96 as induced subgraphs of the retained N96 source. It preserved fields, couplings, vertex mappings, ports, and transition deltas. Smaller sources used exact CPU modular arithmetic; larger sources used fourteen persistent CUDA workers and shared CPU preparation/reconstruction.

The first eleven solve calls totaled 23.726758 seconds. Session creation through the first N96 return took 25.220286 seconds, excluding prior source/plan preparation. N36 included GPU startup. N96's first and fresh-repeat times were 11.172923 and 11.010179 seconds. Its full 348-bin distribution and all sixteen open-port operators matched the retained result; the exact ground energy is −346 with degeneracy 12.

Transition planning already supplied useful structure: N60→72 lowered output work from 63,774 to 47,526 entries/root; N72→84 lowered it from 16,985,708 to 15,661,356. At N96, a fresh conditioned plan beat retaining the preceding priority order. The matched fresh N96 replay reused 5,404 GPU maps with no new uploads.

The first CART model selected depth zero and achieved 2/10 correct choices across its recorded rows, including an incorrect reserved N96 choice. It was retained as advisory. The executable candidate comparison and reusable maps were the useful selection machinery at that stage. Twenty-eight adoption/recovery checks passed on each GEN3/GEN4 installation.

### 3.2 Three transition-training campaigns

| Campaign | Work completed | Main result |
|---|---|---|
| Eleven-size method training | 165 fresh solves; five methods; three rotated repeats | N96 portfolio median 8.035 s versus fresh 11.035 s, 27.18% lower |
| N1–30 training | 450 CPU restarts and 90 exact boundary steps | All twelve frozen decisions across reserved N27–30 chose incremental transfer; N24/N25 favored restart |
| Full N1–96 training | 238 training solves, 134 unique nominated plans, one GPU warmup | All 96 exact spectra; N96 portfolio 8.474 s versus fresh 11.251 s |

The full96 session ran 251.115 seconds from creation to final native checkpoint; measured solve calls totaled 216.426 seconds. These are distinct timing scopes. Nine native policy models, 96 catalog entries and 105 transitions were installed; both runtimes passed 210 adoption/recovery checks.

The original five-method training fitted structural, transition and combined CART heads, each selecting depth one and choosing the portfolio before the N96 reserved timing. Full96's heads instead selected depth zero; the 48/48 recorded reserved choices across N81–96 came from an exact structural-work tie-break. The retained records identify which mechanism made the decision.

N30's incremental operation took 4.518 ms versus 168.186 ms for restart, using an already available previous state. The earlier N24/N25 reversal exposed the importance of the incoming boundary state, which became an input to focused follow-up.

### 3.3 Focused source-family training and readout expansion

Each of two GPU passes completed 300 fresh solves across 100 distinct plans and 37 source groups, plus a warmup. Each of two CPU boundary campaigns completed 540 exact advancement steps and 234 fresh restarts. Full densities and retained-port operators agreed; all 37 sources also matched across GPU readout backends.

Six topology families shared the N96 ancestor. Families 0–2 trained models, family 3 selected them, and families 4–5 were reserved before their timings. Two rewired full-N96 sources exceeded that campaign's scheduling envelope and remained as explicit unsolved candidates.

| Reserved evaluation | Retained scalar readout | Batched exact readout |
|---|---:|---:|
| Cost-policy fastest choices | 8/9 | 8/9 |
| Native pairwise fastest choices | 6/9 | 8/9 |
| Structural fastest choices | 7/9 | 7/9 |
| Cost-selected total seconds | 33.153472875 | 23.290642924 |
| Best measured total seconds | 33.144121434 | 23.238427899 |
| Reserved mean absolute fractional timing error | 7.14% | 10.36% |

Ridge component-cost regression with alpha 0.1 won development selection. The faster native pairwise model learned a nonconstant depth-one ranking using difference+A+B features. The focused installation retained 38 source plans, eleven learned heads across the spin campaigns, four focused experiences, the N120 source, and its N96→120 transition. Both runtimes passed 49 adoption/recovery checks.

The boundary result changed with the backend. With retained readout, the policy chose the fastest method in 20/26 reserved cases, totaling 1.58782 s versus 3.12659 s for always restart. With batched readout, it achieved 26/26, selected 24 restarts and two incremental steps, and totaled 0.0600416 s. Always reuse took 1.94518 s on that same batched comparison. A faster fresh backend changes where reuse pays.

### 3.4 Completing N97–119

The gap campaign executed all 23 sizes from N97 through N119, including connected-prefix N100/N105 objects kept separate from the historical packet defaults. Sources were frozen from the N120 induced-prefix construction, with inherited restricted plans, widths 18–20, 512–2,048 branches, 1,024 roots and five primes. The runner used the fourteen-worker branch-group solver and full density plus sixteen port spectra, with N30 qualification before each source.

The saved completion state reports all 23 complete and no failed sizes. Its controller window was about 46.1 minutes, including qualifications, publication and checkpoint work. These objects completed the contiguous canonical atlas used by the learning campaign. The portable result index does not itself mean that every new family was installed into the global selector.

Source reports: [RESULT.md](../../../frustrated_spin_catalog1/RESULT.md), [RESULT.md](../../../frustrated_spin_training_install1/RESULT.md), [RESULT.md](../../../frustrated_spin_focused_training1/RESULT.md), [RESULT.md](../../../frustrated_spin_focused_install1/RESULT.md), [README.md](../../../spin_gap_97_119_1/README.md). Gap completion snapshot: [REPORT.md](evidence/gap_completion/REPORT.md).

## 4. What source structure explains about cost

### 4.1 Canonical feature table

All 120 sources have separately named pre-execution and post-execution fields. Graph features were derived retrospectively from saved inputs. PRE fields include lineage, graph/source hashes, interactions, degree distribution, connected components and their sizes, local assignment sum, fresh min-fill width/order/work, energy and coefficient bounds, root/CRT requirements and coupling multiplicities. POST fields include the executed method, hardware/readout group, seconds, selected width/branches/work, actual roots/primes, ground energy/degeneracy, occupied bins, output hash and retained stage details.

Historical selected-plan fields remain POST because selecting a historical winner is different from generating a candidate before a fresh execution. The predictive atlas fits use the PRE features. Missing timings, memory measurements and symmetry information stay unassigned rather than being reconstructed from the answer.

For disconnected components C, the structural enumeration estimate is `sum(2^|C|)`. For a connected graph this estimate is 2^N and describes the cost of that enumeration route, not the work performed by the elimination solver. The solver instead benefits from separators, narrow intermediate factors and exact modular reconstruction.

### 4.2 Interpretable baselines

The saved fits use log runtime. The following values come directly from `MODELS.json`. Leave-one-out error is mean absolute error in log time; fit R² describes the fit to the retained data.


| Model | PRE features | Leave-one-out log MAE | Fit log R² |
|---|---|---|---|
| N | N | 0.854462 | 0.841555 |
| formal_state_count | N | 0.854462 | 0.841555 |
| fresh_width | pre_minfill_width | 0.845328 | 0.843383 |
| component_assignments | pre_local_assignments | 0.919875 | 0.83427 |
| components | pre_components, pre_max_component | 0.714131 | 0.898436 |
| arithmetic | pre_arithmetic_burden | 0.697105 | 0.89336 |
| structural | pre_minfill_width, pre_components, pre_max_component, pre_root_bound, pre_crt_primes | 0.615654 | 0.927183 |

The combined structural model lowers leave-one-out log error by **27.95%** relative to N alone. Component structure and arithmetic burden each improve on the N-only baseline, and their combination with width/root/prime features improves further. N and log(2^N) contain the same information, so those two baseline results are identical.

The mixed table contains 96 retained-readout entries, 22 batched-readout entries and two historical CPU packet entries. Within the saved hardware/readout groups, structural-model leave-one-out log errors were 0.251975 for the 96-entry group and 0.233309 for the 22-entry group. The two packet observations were too few for a separate fitted calibration. These groups are inherited provenance labels; the full96 source report identifies CPU execution for its small sizes.

### 4.3 Staircase and transition points

The work staircase has several distinct causes: transform lengths change discretely, conditioning branches change discretely, elimination width changes sharply with topology/order, and historical source/backend changes affect the observed time. The saved transition detector identifies the following jumps and drops.


| From→to N | Time ratio | Roots | Branches | Selected width | Family/backend change |
|---|---|---|---|---|---|
| 1→2 | 1.78961 | [2, 4] | [1, 1] | [0, 0] | False/False |
| 2→3 | 3.31987 | [4, 8] | [1, 1] | [0, 0] | False/False |
| 3→4 | 1.94898 | [8, 8] | [1, 1] | [0, 0] | False/False |
| 5→6 | 1.87163 | [8, 16] | [1, 1] | [0, 1] | False/False |
| 7→8 | 1.96851 | [16, 32] | [1, 1] | [1, 2] | False/False |
| 11→12 | 1.99142 | [32, 64] | [1, 1] | [3, 3] | False/False |
| 24→25 | 1.92671 | [64, 128] | [1, 1] | [3, 3] | False/False |
| 40→41 | 1.80387 | [128, 256] | [1, 1] | [3, 3] | False/False |
| 61→62 | 1.89868 | [256, 512] | [1, 1] | [11, 11] | False/False |
| 89→90 | 2.19614 | [512, 1024] | [16, 32] | [18, 18] | False/False |
| 92→93 | 1.76653 | [1024, 1024] | [32, 32] | [18, 21] | False/False |
| 93→94 | 1.68311 | [1024, 1024] | [32, 32] | [21, 21] | False/False |
| 96→97 | 2.19324 | [1024, 1024] | [32, 512] | [22, 18] | True/True |
| 99→100 | 0.0272393 | [1024, None] | [512, None] | [18, 5] | True/True |
| 100→101 | 47.5923 | [None, 1024] | [None, 512] | [5, 19] | True/True |
| 104→105 | 0.010897 | [1024, None] | [512, None] | [19, 5] | True/True |
| 105→106 | 200.006 | [None, 1024] | [None, 1024] | [5, 19] | True/True |
| 118→119 | 1.99726 | [1024, 1024] | [1024, 2048] | [20, 20] | False/False |
| 119→120 | 1.54501 | [1024, 1024] | [2048, 2048] | [20, 21] | True/False |

N41–61 is a broad measured plateau near 0.35–0.38 seconds. N62 doubles transform length from 256 to 512 and rises to about 0.715 seconds. N90 doubles roots from 512 to 1,024 and branches from 16 to 32. N91/N92 then show why increasing N does not enforce increasing time: transferred ordering reduces width from 22 to 18 and markedly lowers factor work.

The earlier timing review also traced the N17→18, N33→34 and N39→40 downward steps mainly to reconstruction-time variation, while width remained three and structural work increased. These cases teach the cost model to distinguish arithmetic structure from timing overhead.

### 4.4 Regimes, neighbors and anomalies

The retained structural analysis groups sources using normalized graph/work features and records nearest neighbors. N100 and N105 are each other's structural neighbors despite their different N. N103/N104 and N108/N109 are additional close pairs in the connected-prefix region. High residuals in the combined atlas model include N89, N1, N87, N120, N119 and N86; those became candidate questions rather than silently discarded observations.

The regime labels are inspection/grouping labels derived from this atlas. The operational content is the recorded component sizes, widths, arithmetic burden and lineage—not the numerical cluster label itself.

Detailed sources: [FEATURE_SCHEMA.json](../../FEATURE_SCHEMA.json), [MODEL_SUMMARY.md](../../MODEL_SUMMARY.md), [STRUCTURAL_REGIMES.md](../../STRUCTURAL_REGIMES.md), [MODELS.json](../../MODELS.json), [REVIEW.md](../../../frustrated_spin_timing_review1/REVIEW.md).

## 5. N100/N105: packet structure and measured methods


| N | Source family | Components / sizes | Fresh width | Local assignments | Historical seconds |
|---|---|---|---|---|---|
| 99 | N120_INDUCED_PREFIX_GAP1 | [99] | 26 | 633825300114114700748351602688 | 18.3907 |
| 100 | N100_P2_PACKET_PLUS_DEPTH_V1 | [5, 10, 10, 15, 15, 15, 15, 15] | 5 | 165920 | 0.500951 |
| 101 | N120_INDUCED_PREFIX_GAP1 | [101] | 26 | 2535301200456458802993406410752 | 23.8414 |
| 104 | N120_INDUCED_PREFIX_GAP1 | [104] | 32 | 20282409603651670423947251286016 | 33.2076 |
| 105 | N105_P9G0_HISTORICAL_PACKET_RESTORATION_V1 | [10, 10, 10, 15, 15, 15, 15, 15] | 5 | 166912 | 0.361863 |
| 106 | N120_INDUCED_PREFIX_GAP1 | [106] | 32 | 81129638414606681695789005144064 | 72.3749 |

N100 has five components of size 15, two of size 10 and one of size five. N105 has five of size 15 and three of size ten. The replacement of a five-spin component by a ten-spin component increases local assignments by `2^10 − 2^5 = 992`: 165,920→166,912, about 0.598%. The largest component and fresh min-fill width stay 15 and five.

This is the minimal source-level explanation of their low cost. Neighboring connected-prefix cases have a single large component and cannot use the same independent-packet decomposition. Their source families are different, not merely different positions on one uniform size ladder.

### 5.1 Fresh matched workstation comparisons

The first paired question for each canonical packet compared component enumeration, polynomial variable elimination, memoized component calculation, and warm component reuse. Each retained three repetitions with exact scalar and ordered-port equality. Times below are median arithmetic seconds, excluding process startup and independent verification.


| N | Components | Variable elimination | Memo components | Warm components | Components/VE | Components/warm |
|---|---|---|---|---|---|---|
| 100 | 0.158809 | 0.0192118 | 0.0764425 | 0.00964717 | 8.26624 | 16.4618 |
| 105 | 0.162183 | 0.0204252 | 0.0762989 | 0.010201 | 7.94036 | 15.8988 |

The useful route ladder is therefore explicit: exploit component structure; compare an exact polynomial elimination route; reuse a component table when the source-bound energy table is identical. Warm reuse has an already populated cache as an input. The cold/memo measurements retain the work of creating missing tables.

### 5.2 Bridge and field controls

The original campaign created N100/N105 bridge variants and retained counterexamples to reusing the old component partition after a new nonzero edge joins components. The follow-up compared hub and chain connections, increased bridge strength/level through its bounded policy, varied fields/retained ports, and checked competing exact routes.

At the first hub/chain level, variable elimination took about 0.0184–0.0211 seconds across the four N100/N105 cases; conditioned components took about 0.153–0.1596 seconds. Conditioning recovered a valid computation, but it was not the fastest route in those measurements. The result connects algebraic decomposability with the separate question of which implementation is cheapest.

Later separator searches began from the 206 cases where one/two-spin conditioning was insufficient. They found additional admissible decompositions, described in the pod sections. A representative N100 connected-packet control reduced a largest component of 60 to residual components no larger than 15 by conditioning three spins, giving an estimated 934,144 assignments across all separator branches.

### 5.3 Historical provenance

The surviving records place N100 before N105 on 2 August 2026. A formal preregistered N100→N105 prediction has not been located, so this analysis uses retrospective structural transfer. N108 was absent from the historical progression before the N120 frontier launch. The specific explanation that it was skipped because N105 existed is not established by the located records.

Two N100 timing references have different provenance: the normalized learning atlas uses a retained wall time of 0.500951441 seconds; the N105 restoration comparison reports an N100 component median of 0.359080 seconds alongside N105's 0.361863 seconds. Neither is replaced by the new arithmetic-only measurements above. The report preserves each measurement's scope.

## 6. N96/N120: frustrated-source scaling and execution

N120 was constructed from the connected frustrated N96 source: preserve 228 old edges and all 96 old fields, replace twelve disjoint old edges, introduce 24 new vertices with 48 internal edges, and add 24 crosslinks. The final source is connected and five-regular with 300 couplings. Its lineage is separate from the packet N100/N105 work.

| Quantity | N96 retained atlas plan | N120 frontier plan |
|---|---:|---:|
| Vertices / edges | 96 / 240 | 120 / 300 |
| Fresh graph-only min-fill width | 32 | 40 |
| Historical executed retained width | 22 | 21 |
| Conditioning branches | 32 | 2,048 |
| Weighted factor entries | 641,754,752 in saved atlas plan field | 47,476,187,136 |
| Roots | 1,024 | 1,024 |
| CRT primes | 4 | 5 |
| Recorded atlas solve seconds | 8.473945962 | 773.240389397 |
| Ground energy / degeneracy | −346 / 12 | −434 / 8 |
| Occupied density bins | 348 | 435 |

The N96 atlas timing and selected-plan metadata need a precise distinction: the 8.473945962-second observation is the trained portfolio timing, while the copied width22/641,754,752-work fields describe an older retained plan. The training result identifies the portfolio as width21 with 430,070,400 weighted entries. This report keeps those inherited fields visible but uses source-bound matched plan/results for plan-speed comparisons. A future normalized table should bind each timing directly to its exact plan hash.

### 6.1 N120 execution stages

The source-bound CPU search took 300.315419136 seconds separately from the solve. It improved the initial usable plan from 83,991,560,192 to 47,476,187,136 weighted entries, a reduction of about 43.47%. RAM templates/maps took about 0.992 seconds to prepare.

The 773.240389397-second fresh solve contained 0.527213205 seconds of GPU preparation and 772.666548321 seconds of modular work/checkpoint handling. Exact reconstruction was 0.046110634 seconds. Fourteen persistent workers shared 40,960 tasks, each covering sixteen roots and sixteen conditioned branches. Every task contributed once, with no restart. Five-prime qualification included a coefficient exceeding four-prime capacity.

Peak host cgroup usage was 29.140 GiB, including earlier training closeout/waiting activity; per-worker pool use was about 2.996 GiB. Trace analysis recorded 99.0091% average worker kernel-active time and 90.7437% all-fourteen simultaneous activity over the modular phase. These are kernel-active durations. The saved 69,496,320 CUPTI records had no dropped records.

The exact output includes all 2^120 configurations through elimination/reconstruction, 435 occupied energy bins, all sixteen open operators and sixteen closed conditional spectra. Count, first/second moments, per-port counts and support checks passed.

### 6.2 N96 plan/readout progression

| Plan and readout | Three-repeat median seconds |
|---|---:|
| Fresh min-fill, retained readout | 11.202180587 |
| Prior six-seed portfolio, retained readout | 8.226796205 |
| Expanded plan, retained readout | 4.761149127 |
| Same expanded plan, batched exact readout | 3.257604178 |

The expanded plan uses sixteen branches at width21, compared with 32 branches in the earlier route. Its one-time search was about six seconds and is cached for identical sources. The isolated exact readout comparison changed 1.4346 seconds to 0.01482 seconds. Plan choice and reconstruction improvement are separate contributions.

The N96→N120 transition touches 24 old boundary vertices. The old four-port N96 spectrum alone does not carry those correlations; the frontier calculation used the full new source. Plans, recipes and structural experience transferred, while the full N120 distribution was freshly calculated.

Sources: [RESULT.md](../../../frustrated_spin_n120_frontier1/RESULT.md), [RESULT.md](../../../frustrated_spin_focused_training1/RESULT.md), [N96_N120_SCALING.md](../../N96_N120_SCALING.md).

## 7. First workstation learning campaign

The first learning controller rebuilt a clean canonical table, ran the interpretable fits, compared structural planners, executed cheap exact alternatives, and checked component partitions. It used one low-priority CPU worker, up to two allowed CPU affinities, a 4 GiB worker address-space limit, and a 120-second experiment ceiling. No local CUDA was available to this campaign.

It completed **407 questions**: one atlas build, one analysis, 145 planning questions, 140 exact solve questions and 120 component-rule certificates. It retained **1,445 method-scorecard rows**. Those rows mix exact measurements and structural alternatives; the observation column identifies which is which. Nine workstation method-cost fits were retained, with 20 measured rows for each of six planner routes, eight each for components and variable elimination, and four for incremental boundary.

The 120 partition certificates cover each canonical source. They verify that the supplied components have no cross-component interaction and support exact polynomial convolution. For a connected source, the partition may have only one component; that certificate supplies source/partition correctness without a decomposition speed reduction. The useful computational cases are the actual multi-component sources.

Thirty-one conditioned-plan attempts failed because the supplied source hash no longer matched the normalized graph. The corrected successor used the exact source normalizer and distinct corrected question IDs. The original failures remain in the ledger.

The campaign stopped at `NO_ADMISSIBLE_QUESTION` after about 20.2 minutes, well before its eight-hour ceiling. Its initial finite question policy had exhausted the work it knew how to ask. That stopping state motivated the broader outcome-driven successor; it did not indicate that the spin research subject was exhausted.

## 8. Self-follow-up campaign

The successor explicitly linked new questions to observed outcomes. It completed **1,476 questions**: 896 planning investigations, 573 paired method comparisons and seven gauge-certificate questions. It retained 1,174 method measurement rows and 1,606 generated follow-up questions. The 573 paired comparisons span **391 distinct source hashes**; repeated measurements/refinements are identified separately.

Across those paired questions, the fastest measured route was variable elimination in 390, components in 163, and warm component reuse in 20. These are wins within each question's candidate set, not a universal ranking across untested routes. Conditional components supplied many exact comparisons but did not win a paired question in this saved workstation set.

### 8.1 Measured coverage


| Method | Independent sources | Measurement rows | Median arithmetic seconds across rows |
|---|---|---|---|
| components | 183 | 322 | 0.00115399 |
| conditional_components | 206 | 237 | 0.0830557 |
| memo_components | 4 | 22 | 0.0734748 |
| variable_elimination | 391 | 573 | 0.00143922 |
| warm_components | 2 | 20 | 0.00968402 |

The summary medians above describe each method's sampled corpus; they should not be divided to estimate paired speedups because each method saw a different source subset. Section 5 supplies matched packet comparisons, and the combined CSV retains the question/source join for all others.

### 8.2 The seven retained certificates

These are the **seven from the earlier run** discussed in the conversation. They are in `followup1/CERTIFICATES.jsonl`. All carry the saved status `CERTIFIED_EXACT_RULE`, the rule name `EXPLICIT_SPIN_SIGN_BIJECTION`, and scope `project-local compiler reuse proposal`.

For signs g_i∈{−1,+1}, the transformation is `t_i=g_i s_i`, `h'_i=h_i g_i`, `J'ij=Jij g_i g_j`. Each spin configuration maps bijectively to one with the same energy. Scalar DOS is unchanged. An ordered retained-port assignment transforms by the corresponding port signs. The independent verifier reconstructs the original field/coupling coefficients using the inverse transformation.

The result is executable reuse information: GEN4 can recognize an explicitly transformed source, carry its source mapping and port mapping, and reuse the corresponding exact result under that certified relationship. A transformed-port observable must follow its mapping rather than blindly copying the original port labels.


| N | Parent source SHA256 | Transformed source SHA256 | Negative signs |
|---|---|---|---|
| 72 | 2c949e8f79d3db8e94006a1e043cf1865a85042263efe0e3794f0385ac4e8ff4 | 9adf39842bfb467a26ce2c193a8fd13e4049414d5cacc405614abcaaf623d81f | 33 |
| 84 | a9276261b491353b7a97dfe6fa8053ce22f644b61fc21d0b3c8e160a13727b0c | 611fa6b9324c25e1e7fd0077a8a86c2ca019e4b4059321cf7e9f2c09bfcadfac | 37 |
| 96 | dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44 | 50d2885d588328487d3c7c070c17651ed11dfb1029ef243609e8c9328de6ddf7 | 48 |
| 100 | f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b | 59fe4d4635dd29eb87d5e22c9f696305926ef3978b2031f1af78fa8cba01c4e8 | 48 |
| 105 | 5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774 | 15e40289f98e12e1bc24fce7dca21ad31d6410baaf163dd76f37e896ba04cc65 | 59 |
| 108 | 9a54c568b5318669459338e62eaee66ad8a9b98615dbca859007da933b6a57de | b925cd637cbe6f0b241c65705051d8e1395547352d609212bdc8e74575d76602 | 55 |
| 120 | bed8dbc542412f88a76795573e157e369710a0bcf8d2b7358e10a159d98df1f4 | a6354015ae5aa6b692f37e885ce944d407f1aa6e96057dd6737d1f66ccdb2625 | 57 |

Certificate evidence: [CERTIFICATES.jsonl](../../followup1/CERTIFICATES.jsonl). The complete gauge vectors and derivations are retained there. The previous chat response had inspected the first campaign’s partition ledger instead; these seven are the separate sign-bijection records above.

### 8.3 How its follow-up expanded

Near ties or noisy timings generated alternating-order repeats, up to three refinement stages. Packet comparisons generated field and port ablations. Successful bridge controls generated stronger hub/chain controls up to level seven. A novel width/work fingerprint generated another same-N rewiring; three duplicate fingerprints closed that branch, with seed index capped at 128. An admitted cheap structural regime led to a full exact comparison. Failed routes generated structural diagnosis rather than indefinite retries.

The run encountered **206 cases beyond its one/two-spin separator and component-size admission**, all saved with `FAILED_OR_CAPACITY_BOUND`. Those cases became the explicit inputs to deeper pod separator research. The run stopped `SEARCH_SATURATED` after about 56.8 minutes with no queued questions under that policy, retaining five next scientific questions.

## 9. Ten-worker pod continuation

Podrun1 used ten local experiment processes, each assigned one MIG GPU for its CUDA work. This was ten independent experiment slots, not a fourteen-worker cooperative solver. The distinction matters when reading its N96 seconds.

It completed **637 questions**: 313 structural planning questions, 206 extended separator searches, 105 paired exact CPU comparisons and thirteen exact GPU questions. The 206 earlier separator failures seeded deterministic greedy search up to depth twelve. Sixty-two resulting plans were admitted for exact work and 144 were not. Depth counts are retained below.

**podrun1 separator depths:** 3: 31 cases, 4: 19 cases, 5: 20 cases, 6: 7 cases, 7: 1 cases, 8: 1 cases, 9: 1 cases, 10: 3 cases, 11: 2 cases, 12: 121 cases.

**podrun2 separator depths:** 1: 23 cases, 2: 29 cases, 3: 24 cases, 4: 3 cases, 5: 1 cases, 6: 4 cases, 7: 7 cases, 8: 3 cases, 9: 6 cases, 10: 12 cases, 11: 1 cases, 12: 1 cases, 20: 92 cases.

Podrun1's CPU scorecard has 222 rows: 105 variable-elimination, 89 conditional-component, fourteen memo-component, twelve warm-component and two direct-component measurements. The exact GPU measurements cover N12 qualification, N72, N84 and N96, with root batches sixteen and thirty-two.

For N96, the one-device expanded plan took 42.1464 seconds at batch16 and 39.5613 at batch32. The older 32-branch plan took 90.9451 and 85.8854 seconds respectively. All thirteen GPU scorecard rows report full-density equality. These timings describe one-device per-question execution and are not comparable to the historical fourteen-device 3.2576-second result as if the hardware/process setup were the same.

The run stopped `SEARCH_SATURATED` after about 12.1 minutes. Six setup interruptions came from the network filesystem rejecting ownership/timestamp preservation. The copy procedure changed to content-only checksum copies. Among 74 failed/capacity-bound attempts, sixty exceeded admitted exact separator work, nine had source/plan mismatch, four had requested-port/plan mismatch, and one exceeded the elimination-width gate. These records supplied concrete corrections to the next pod run.

## 10. Twenty-worker pod continuation

Podrun2 increased resource admission and rebuilt plans for their exact sources and ordered ports. Its configuration allowed twenty one-MIG GPU experiment workers plus eight independent CPU workers. CPU workers could use up to 20 GiB each subject to aggregate availability; experiments had a two-hour ceiling, exact operations 7,000 seconds, separator depth twenty, residual components up to 26 and estimated assignments up to 100 million. GPU admission checked measured free VRAM, with configured width30, map-size8 GiB, branches2^18 and task-count10 million ceilings.

That independent GPU/CPU pool differed from the requested workstation-style cooperative topology. The later correction restored one coordinated GPU team with shared CPU preparation and reconstruction. Results from the independent pool remain valid for their recorded sources and exact checks; its performance measurements retain their actual execution context.

The latest saved state contains **571 completed questions**: 206 separator searches, 318 paired comparisons, 29 GPU questions and eighteen planning questions. It has 102 failed/capacity-bound results and 69 queued questions, plus interrupted in-flight precommits carried into recovery. It was superseded rather than completing its eight-hour window.

### 10.1 Separator follow-through

The deterministic beam search used width twelve and the expanded depth/work limits. It admitted 114 of the 206 separator cases, compared with 62 in podrun1. Ninety-two remained unadmitted at depth twenty. This is 52 additional structurally admitted cases under the changed search/resource policy. Admission is recorded separately from successful full-density execution.

A representative N100 bridge control again reaches residual maximum component15 with a three-spin cutset and 934,144 estimated assignments. The retained traces show the intermediate decompositions and alternative cutsets. These traces are reusable method-selection data, including cases where a deeper separator is mathematically viable but slower than low-width variable elimination.

### 10.2 CPU and GPU measurements

The CSV contains 848 CPU measurement rows: 318 variable elimination, 265 memo components, 212 warm components, 51 conditional components and two components. Its saved `METHOD_MODELS.json` lags the last state/scorecard update: for example it summarizes 310 VE and 43 conditional-component rows. This report uses the CSV counts and preserves the older model summary as its own snapshot.

The 29 exact GPU questions include packet and changed-source controls, N72/N84, and connected N90/N96/N99/N101 cases. Every saved GPU row reports full-density equality. Each question used one visible GPU. Larger examples include N90 at 84.9193 and 129.518 seconds for different records/plans, N96 at 97.8775, N99 at 98.1207, and N101 at 150.7834 seconds. The complete source/plan/batch distinction is in the GPU appendix and CSV.

Root batch 128 often lowered recorded elapsed time compared with batch64 for small/mid-sized tasks, but source variant, plan and concurrent worker load also differed across this corpus. The scorecard retains actual batch size: the N12 request for batch128 executed batch64 because only 64 roots were present.

### 10.3 Failures and the retained-port correction

The saved failures include 64 retained-index `KeyError` cases (indices 0–3 plus one index61), sixteen VRAM gates, fifteen finite-factor-work limits, four width gates, one map-byte gate, an initial `spin_gpu` import failure and one generic subprocess failure. The retained-port-safe separator correction generated explicit follow-up questions; successful successor results were added without erasing the earlier errors.

Repeated warm-packet comparisons accumulated heavily: the old model summary shows 212 warm rows from just two independent sources. That is useful timing/refinement evidence, but it also explains why question counts could rise much faster than structural source coverage. The fresh restart later addressed broader question generation rather than importing this queue.

## 11. Fourteen-worker restoration and podrun3

### 11.1 Restoring the actual N1–120 execution path

The original focused and N120 branch-group engines, package versions, cached source plans, batched inverse NTT and integer CRT, reusable maps, two-bank CUDA graphs and sixteen-root batches were restored. Fourteen persistent GPU owners shared a work queue; the CPU handled common preparation and exact reconstruction. The eight-independent-CPU-job scheduler was removed from this continuation.

The restored pod had fourteen RTX PRO 6000 Blackwell MIG 1g.24gb workers, 95.2 CPU equivalents and 438,999,998,464 bytes of host RAM. The historical fourteen-worker host had 47.6 CPU equivalents and 880 GB RAM. Software/process configuration was restored; the host allocation was different.

Forty-nine original adoption/recovery checks passed. All 120 canonical file hashes matched the workstation; all 46 frozen gap source/plan comparisons matched. The N96 qualification used the expanded source-bound plan, sixteen branches and width21. Full scalar DOS and open/closed retained operators matched, with work on every GPU.

| Restoration measurement | Seconds |
|---|---:|
| Historical expanded/batched median | 3.257604178 |
| Restored cold solve | 13.442205810 |
| Restored warm solve 1 | 3.487722907 |
| Restored warm solve 2 | 3.395276192 |
| Restored warm solve 3 | 3.407556477 |
| Restored warm median | 3.407556477 |

Cold worker preparation was 10.4624 seconds, with 0.1696 seconds of source preparation before the solve. The original N30 branch-group qualification also passed with eighty fresh tasks on all fourteen workers. Fifth-prime reconstruction covered 16,384 coefficients, including a coefficient beyond four-prime capacity.

The earlier slow N96 diagnostic had used the older 32-branch/scalar-readout path. That setup difference was the relevant cause to correct; duplicating GPU count alone did not duplicate the source plan or readout path.

### 11.2 Podrun3's actual new work

Podrun3 resumed 571 completed checkpoint records but added only eleven new completed questions: two N96 GPU plan comparisons and nine paired CPU comparisons. Six missing generated variants were reconstructed and accepted only after matching their original precommitted file SHA256. The controller was then stopped at Sean's request; its PID6331 exited, status is `STOPPED`, and 73 questions remain saved.

The two N96 records include one cold and two warm repetitions each. The `seconds` field summarizes the whole multi-repeat operation, not one warm solve. The table below extracts the individual execution totals and arithmetic stages.


| Plan | Branches | Width | Weighted entries | Repeat | Prepare s | Arithmetic s | Total solve s | Readout s |
|---|---|---|---|---|---|---|---|---|
| expanded_portfolio | 16 | 21 | 203956800 | 0 | 9.54575 | 2.83544 | 12.5196 | 0.0778676 |
| expanded_portfolio | 16 | 21 | 203956800 | 1 | 0.541344 | 2.82347 | 3.45828 | 0.0428487 |
| expanded_portfolio | 16 | 21 | 203956800 | 2 | 0.702451 | 2.79348 | 3.59266 | 0.0451182 |
| fresh_min_fill | 32 | 22 | 641754752 | 0 | 9.42759 | 9.07203 | 18.6157 | 0.0684696 |
| fresh_min_fill | 32 | 22 | 641754752 | 1 | 1.24516 | 9.03008 | 10.3744 | 0.0468311 |
| fresh_min_fill | 32 | 22 | 641754752 | 2 | 0.819814 | 9.0076 | 9.93287 | 0.053871 |

The work ratio is 641,754,752 / 203,956,800 = **3.14652**. Warm GPU arithmetic is about 9.01–9.03 seconds for fresh min-fill versus 2.79–2.82 for the expanded plan, approximately 3.2×. This matched source/backend result directly connects planned work reduction with measured execution reduction. The full multi-repeat question totals were 21.5916 and 41.0755 seconds respectively.

The nine CPU pairs compared variable elimination with conditional components on retained changed-source N37, N40, N41, N44, N45 and N46 cases. All nine favored variable elimination. VE arithmetic was about 0.00350–0.00567 seconds; conditional components ranged from 2.85470 to 39.25233 seconds. The question-specific table below retains those results.


| N | Question ID | VE seconds | Conditioned seconds | Conditioned/VE |
|---|---|---|---|---|
| 44 | f02c0300bb1dee84354715cf | 0.00474533 | 39.015 | 8221.75 |
| 44 | 99b08ec16d1c673c6dc9a4d7 | 0.00495379 | 2.8547 | 576.265 |
| 44 | bee22c5cb8f0cce29acf5805 | 0.00566982 | 38.5417 | 6797.71 |
| 45 | 87b95bebb3857511c4ee6cdf | 0.00501291 | 4.6921 | 936.003 |
| 46 | b8894aa6e07e4483507756df | 0.00526037 | 7.23204 | 1374.81 |
| 41 | 18f01183cf76b0e218f419f1 | 0.00513232 | 19.0538 | 3712.51 |
| 37 | 637e13b068a88d3d1b8af303 | 0.00349562 | 19.1318 | 5473.08 |
| 40 | 3252ec8d0d9fb2e21749e880 | 0.00379293 | 9.805 | 2585.07 |
| 40 | 5af08f9730ca6cb0997b326f | 0.00453656 | 39.2523 | 8652.45 |

The three new failed/interrupted attempts were two finite-factor-work limits and the final generic subprocess failure recorded around stop. The ledger does not assign a more specific cause to that final empty subprocess error. Sources: [RESULT.md](../../pod_restore14/RESULT.md), [QUESTION_LEDGER.jsonl](evidence/podrun3/QUESTION_LEDGER.jsonl), [STATE.json](evidence/podrun3/STATE.json).

## 12. Method-by-method findings

The learning project's nine method-family definitions comprise six planner routes and three exact execution/reuse routes. Earlier installations also had nine fitted policy heads; those heads and the nine method families are different objects. Follow-up added memoized/warm/conditioned component prototypes beyond that initial roster.

| Method | What it does | What the retained work says |
|---|---|---|
| Fresh min-fill | Constructs an elimination order from the current source | Necessary baseline; wins some transitions, including the initial N96 conditioned comparison against inherited priority; later expanded search improves it |
| Transition priority | Uses preceding source/order experience to resolve planning choices | Strong N91/N92 improvement; width22→18, substantial work and timing reduction |
| Parent plan | Reuses the ancestor ordering/cutset mapped into the current source | Cheap planning baseline; must be compared with current-source alternatives; source/port identity checks matter |
| Repair transfer | Locally repairs inherited order | Included in exact small-source counterfactuals and portfolio comparisons; no universal win assigned |
| Tie portfolio | Searches deterministic min-fill tie alternatives | Improves N85/N86/N93/N96; repeated N96 median 8.035 s versus 11.035 s fresh in early training |
| Expanded portfolio | Broadens source-bound cutset/order search | N96 sixteen-branch width21 plan, 203,956,800 weighted entries; cached search and batched readout underpin the 3.2576 s result |
| Components | Enumerates separate components and convolves exact polynomials | Structural explanation for packet N100/N105; wins 163 follow-up paired questions |
| Variable elimination | Eliminates spin factors using exact polynomial sums/products | Fastest in 390 workstation follow-up pairs and all nine restored CPU pairs; beats cold packet enumeration |
| Incremental boundary | Carries sufficient future-facing state to the next source | Wins reserved N27–30 in early CPU training; incoming state and actual backend determine its advantage |
| Memo components (follow-up) | Reuses identical component energy tables within an exact computation | Reduces packet rebuilding relative to cold components; retains source-bound equality keys |
| Warm components (follow-up) | Reuses already populated exact component tables | Fastest in twenty follow-up packet comparison/refinement questions; cache provenance is part of the input |
| Conditional components (follow-up) | Conditions a separator, solves residual components, sums all branches | Expands applicability beyond disconnected graphs; deeper separator admission improved, while measured VE frequently remained cheaper |

The useful selector combines source features, route-specific work, exact admissibility, cache/boundary availability and hardware/readout calibration. No run established that one method dominates all source regimes. The existing focused policy evaluations provide the strongest retained held-out method-selection measurements; the overnight continuations add a much broader source/control corpus.

## 13. Autonomous follow-up: what it actually did

The research was locally controlled Python/GEN4 execution with deterministic question policies, saved exact operations, cost summaries and model updates. The controllers made no hosted model calls. A source-bound DomainSession operation executed each native question and retained a checkpoint/receipt; local orchestration scheduled it and recorded the outcome.

The progression across runs is visible in their ledgers:

1. Initial atlas analysis exposed structural discontinuities and packet/frustrated differences.
2. Paired packet measurements led to cache, field, port and bridge follow-ups.
3. Bridge/rewire outcomes generated same-N structural questions and exact comparisons.
4. One/two-spin capacity boundaries supplied 206 explicit separator-search inputs.
5. The ten-worker greedy search produced deeper cutsets and exact candidates.
6. The twenty-worker beam search admitted additional cases and source/port corrections.
7. The restored N96 calibration generated a matched alternative-plan experiment.

This was genuine result-to-next-question execution: parent IDs and generated child IDs are retained. Its scope was determined by the implemented question families. The first run stopped when its finite frontier ended; the follow-up and ten-worker run later stopped under their respective saturation rules. Podrun2 instead accumulated many repeated packet refinements and was superseded with work pending. Podrun3 inherited that queue and was stopped before the clean restart.

The combined records show both useful depth and where breadth needed work. Component reuse was measured repeatedly on few sources; rewiring produced hundreds of source-specific planning/comparison records; separator searches carried actual earlier failure cases forward. The next controller needed to balance these activities, revisit unexplained regimes, and prevent equivalent questions from dominating. That requirement motivated the fresh-state controller rather than another inherited continuation.

## 14. Failures, corrections, and retained counterexamples

Failures are grouped below by their recorded cause and operational effect. Full errors remain in the event export and original ledgers.

| Stage | Recorded issue | Effect and subsequent handling |
|---|---|---|
| Original catalog setup | Module-name collision after five small cases | Interrupted artifact retained; corrected catalog completed |
| Catalog installation | FUSE timestamp preservation | Moved transactional staging to container storage |
| Focused CPU setup | Import failure | Corrected rerun preserved alongside failure |
| Focused publication | Canonical schema rejected floating model parameters | Completed calculations retained; lossless tagged hexadecimal float64 encoding used in separate publication |
| N120 trace analysis | Initial analysis assumed non-overlapping kernel intervals | Corrected interval-union analysis; arithmetic result unchanged |
| First learning smoke | Runtime binding mismatch, then `closed_port_rows` mismatch | Restored original bindings, vendored additive modules; normalized full conditional rows; third smoke attempt completed |
| First learning production | 31 graph/source-hash mismatches | Exact normalizer correction and distinct corrected question identities |
| First learning controls | N100/N105 bridge invalidates old partition | Two explicit `EXACT_PRECONDITION_VIOLATED` records; old partition not reused |
| Follow-up | 206 one/two-spin decomposition limits | Preserved as separator-search inputs for pod continuations |
| Podrun1 setup | Three ownership and three timestamp copy interruptions | Content-only checksum copy policy |
| Podrun1 research | 60 work limits, nine source mismatches, four port mismatches, one width limit | Source-specific planning, corrected bindings and expanded resource gates in successor |
| Podrun2 | 64 retained-index errors | Port-safe separator correction and explicit follow-up questions |
| Podrun2 | 16 VRAM, 15 factor-work, four width and one map-size gate | Retained as concrete route/resource limits |
| Podrun2 setup/other | Missing `spin_gpu` import and one generic subprocess failure | Qualification repeated with corrected import; other failure retained |
| N96 diagnostic | Older plan/readout rather than historical fast setup | Restored focused plan, batched readout, package/runtime and fourteen-worker team; repeated exact qualification |
| Podrun3 | Two factor-work limits, one generic subprocess stop-era failure | Retained; controller stopped as requested |

The failure records do not all describe mathematical counterexamples. A source-hash error is an implementation binding failure; a capacity gate identifies an unadmitted route; the bridge controls specifically invalidate an old partition assumption. The report uses their actual recorded meaning.

Two reporting inconsistencies were also resolved here: podrun2's status/model summaries lag its state/scorecard; podrun3's generated summary mixes inherited failure totals with new completed totals. The accounting in this report separates them. The N96 atlas timing/plan mismatch is documented in Section 6 rather than silently rewritten.

## 15. What is installed, retained, and proposed

The earlier catalog/training/focused installations put exact entries, source transitions, cached plans, learned model objects and cost/lookup interfaces into both GEN3 and GEN4. The retained focused installation includes the qualified fifth-prime arithmetic needed by N120. The later shared spin-tools installation exposes fresh exact solving and replay as reusable operations; its source and adoption report remain the authority for that installed interface.

The overnight learning projects are additive. Their new component/gauge certificates, method observations, separator controls and cost summaries are retained inside `frustrated_spin_learning1/`. They were not installed as new global selector authority. The gap-completion atlas objects are available through their portable source/result bundles and the normalized canonical table; availability in this campaign is distinguished from a global catalog installation.

Important retained assets are:

- 120 canonical source/result objects, with lineage and exact output hashes.
- Explicit N120-prefix variants for packet-number collisions at N100/N105.
- Earlier installed structural/transition policy heads and focused cost models.
- The original 120 partition certificates and seven follow-up sign-bijection certificates.
- Exact component-table reuse and conditioned-component prototypes.
- Hundreds of same-N planning and paired comparisons, with both successful and capacity-bound outcomes.
- Source-bound GPU task/residue checkpoints, exact NTT/CRT reconstruction and full-density checks.
- Parent/child question ledgers, model snapshots, method scorecards and recorded stop/recovery state.

For ordinary use, exact output reuse requires matching source/observable identity or the explicit certified transformation. A learned cost rule chooses the route; the route still returns the exact checked result.

Installed tool source: [RESULT.md](../../../spin_tools_install1/RESULT.md). Earlier focused installation: [RESULT.md](../../../frustrated_spin_focused_install1/RESULT.md).

## 16. Holdout predictions and the fresh-run boundary

The learning campaigns kept N121–144 unexecuted. Their saved prediction file has 24 conditional entries. It marks future source graphs undefined, leaves numerical width/runtime unassigned, and distinguishes packet-like sources with maximum component15 from connected frustrated sources requiring inherited-cutset/expanded-plan comparison. It gives five-prime arithmetic under the retained coefficient-bound planning convention and makes root length/memory conditional on the actual source and batching.

The next prospective region therefore remains available for a source-defined test. These files are conditional planning outputs, not a hidden executed frontier.

The current `blind_restart1` began at 17:23:29 UTC on 26 September, with a deadline of 01:23:29 UTC on 27 September. It started with zero completed research questions, zero imported observations, zero fitted campaign models and zero imported certificates. It retained the canonical sources/answers, original method definitions and separately qualified exact runtime. Earlier research queues and fitted outcomes were not imported.

Its qualification was separate: eight bounded controller questions, explicit gauge/permutation inverse checks, an N30 exact test on all fourteen workers, success/failure follow-up, empty-frontier review and cost-model updates. A missing activation variable and a cold-only cost sample were preserved as setup-check failures before corrected checks completed. Those qualification data did not seed the production state.

This report ends at that handoff. The current run's developing results and the later status counts are not added to the historical comparisons above.

Prediction file: [PREDICTIONS_121_144.json](../../PREDICTIONS_121_144.json). Fresh launch: [LAUNCH.md](../../blind_restart1/LAUNCH.md).

## 17. Connections and next research questions

The following synthesis is drawn from the completed records; it does not launch additional work.

**Source decomposition and execution structure meet at the factor representation.** Packet components make enumeration cheap; an elimination plan can make the same source cheaper still. A connected graph can become separable after conditioning, but the number of branches and residual factor sizes determine whether that transformation saves time. The common learning target is the exact computational representation produced from the source, not component count or N in isolation.

**Boundary information controls which history can be reused.** N1–30 incremental work, retained-port ablations, gauge port mappings and the N96→N120 boundary all address the same operational issue: what information must remain available to calculate the requested next observable? A scalar density can be sufficient for one reuse and insufficient for another. The saved future-facing boundary or certified port mapping supplies a precise mechanism for reuse.

**Plan quality and backend quality multiply.** Expanded N96 planning lowers arithmetic; batched NTT/CRT lowers reconstruction. The CPU boundary policy then changes its preferred method because fresh restart has become much cheaper. Method learning therefore needs the actual readout/backend identity, cache state and worker topology alongside graph features.

**Exact transfer can be learned as a recognizer plus an executable mapping.** The seven sign-bijection certificates show one form: recognize a source relation, verify its inverse, map ports and reuse the result. Component-table equality and boundary transfer are related operational patterns with different certificates and inputs. A project-local compiler can organize these as explicit source-to-operation rules.

**Capacity failures can supply informative research questions.** The 206 one/two-spin failures became deeper separator questions; beam search increased admission from 62 to 114 cases. The remaining question is not just whether a decomposition exists but which source features forecast its benefit relative to elimination. The restored nine CPU pairs show that a valid separator route can remain far more expensive than VE.

The highest-value next questions supported by the retained work are:

1. Which PRE factor/separator features predict VE versus conditioned-component cost on new same-N sources, including the 52 newly admitted separator cases?
2. Can the source-bound equality/gauge/boundary mechanisms share an exact reuse interface that preserves ordered observables and exposes actual work eliminated?
3. How much of route choice changes with the readout backend and cooperative GPU topology after conditioning on the same source and plan?
4. Which interventions explain the remaining N84–96 and N119/N120 cost residuals: width, branch count, factor shapes, map traffic, reconstruction or preparation?
5. Can an explicit prospective source family for N121–144 be defined so structural regime, plan and runtime predictions are frozen before arithmetic, using the now-complete lower atlas?

The immediate program improvement suggested by these records is to bind every cost observation to **source hash + ordered ports + plan hash + backend + worker topology + cache state + timing stage**. The restored N96 comparison shows why all seven matter. This is an analysis recommendation from this report; no selector or running controller was modified here.

## 18. Detailed numerical appendices

### 18.1 Complete canonical N1–120 atlas

Times are the inherited normalized atlas observations, not a new uniform benchmark. `retained` and `batched` refer to the atlas provenance groups; small full96 sources used CPU arithmetic as documented above. N100/N105 retain packet defaults. Width here is fresh graph-only min-fill width; it is not the selected conditioned execution width. Exact source, graph and output hashes and all other columns are in [ATLAS_120.csv](ATLAS_120.csv).


| N | Edges | Components | Max component | Fresh width | Seconds | Method | Ground | Degeneracy | Bins |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 1 | 1 | 0 | 0.000964084 | fresh_min_fill | -1 | 1 | 2 |
| 2 | 1 | 1 | 2 | 1 | 0.00172534 | fresh_min_fill | -4 | 1 | 4 |
| 3 | 1 | 2 | 2 | 1 | 0.0057279 | fresh_min_fill | -5 | 1 | 6 |
| 4 | 2 | 2 | 2 | 1 | 0.0111635 | fresh_min_fill | -6 | 1 | 8 |
| 5 | 2 | 3 | 2 | 1 | 0.0112754 | fresh_min_fill | -8 | 1 | 10 |
| 6 | 3 | 3 | 2 | 1 | 0.0211034 | fresh_min_fill | -10 | 1 | 11 |
| 7 | 4 | 3 | 3 | 1 | 0.0210371 | fresh_min_fill | -13 | 1 | 14 |
| 8 | 6 | 3 | 4 | 2 | 0.0414116 | fresh_min_fill | -18 | 1 | 18 |
| 9 | 8 | 3 | 5 | 2 | 0.040622 | fresh_min_fill | -22 | 1 | 22 |
| 10 | 11 | 3 | 6 | 3 | 0.0421387 | fresh_min_fill | -28 | 1 | 28 |
| 11 | 12 | 3 | 7 | 3 | 0.0411351 | fresh_min_fill | -31 | 1 | 31 |
| 12 | 13 | 3 | 8 | 3 | 0.0819172 | fresh_min_fill | -32 | 1 | 33 |
| 13 | 13 | 4 | 8 | 3 | 0.081135 | fresh_min_fill | -32 | 2 | 33 |
| 14 | 14 | 4 | 8 | 3 | 0.080012 | fresh_min_fill | -33 | 6 | 34 |
| 15 | 14 | 5 | 8 | 3 | 0.0810208 | fresh_min_fill | -34 | 6 | 35 |
| 16 | 15 | 5 | 8 | 3 | 0.081932 | fresh_min_fill | -35 | 6 | 36 |
| 17 | 15 | 6 | 8 | 3 | 0.101044 | fresh_min_fill | -36 | 6 | 37 |
| 18 | 16 | 6 | 8 | 3 | 0.0806915 | fresh_min_fill | -38 | 12 | 40 |
| 19 | 16 | 7 | 8 | 3 | 0.0807891 | fresh_min_fill | -40 | 12 | 42 |
| 20 | 17 | 7 | 9 | 3 | 0.0827742 | fresh_min_fill | -43 | 12 | 44 |
| 21 | 18 | 7 | 9 | 3 | 0.082525 | fresh_min_fill | -47 | 4 | 48 |
| 22 | 19 | 7 | 10 | 3 | 0.0827765 | fresh_min_fill | -49 | 4 | 50 |
| 23 | 19 | 8 | 10 | 3 | 0.0825598 | fresh_min_fill | -51 | 4 | 52 |
| 24 | 19 | 9 | 10 | 3 | 0.0833068 | fresh_min_fill | -53 | 4 | 54 |
| 25 | 22 | 7 | 10 | 3 | 0.160508 | fresh_min_fill | -58 | 2 | 58 |
| 26 | 22 | 8 | 10 | 3 | 0.161445 | fresh_min_fill | -60 | 2 | 60 |
| 27 | 25 | 6 | 17 | 3 | 0.161358 | fresh_min_fill | -64 | 2 | 65 |
| 28 | 25 | 7 | 17 | 3 | 0.16069 | fresh_min_fill | -65 | 2 | 66 |
| 29 | 27 | 6 | 23 | 3 | 0.160672 | fresh_min_fill | -71 | 1 | 72 |
| 30 | 28 | 6 | 24 | 3 | 0.166382 | fresh_min_fill | -71 | 3 | 74 |
| 31 | 30 | 5 | 26 | 3 | 0.183232 | fresh_min_fill | -75 | 6 | 77 |
| 32 | 30 | 6 | 26 | 3 | 0.185094 | fresh_min_fill | -77 | 6 | 79 |
| 33 | 31 | 6 | 27 | 3 | 0.234611 | fresh_min_fill | -79 | 8 | 81 |
| 34 | 31 | 7 | 27 | 3 | 0.194114 | fresh_min_fill | -80 | 8 | 82 |
| 35 | 31 | 8 | 27 | 3 | 0.194651 | fresh_min_fill | -81 | 8 | 83 |
| 36 | 34 | 7 | 29 | 3 | 0.201039 | fresh_min_fill | -87 | 4 | 88 |
| 37 | 37 | 6 | 31 | 3 | 0.188424 | fresh_min_fill | -90 | 4 | 91 |
| 38 | 38 | 6 | 32 | 3 | 0.196067 | fresh_min_fill | -90 | 8 | 93 |
| 39 | 39 | 6 | 32 | 3 | 0.292337 | fresh_min_fill | -91 | 16 | 95 |
| 40 | 41 | 6 | 33 | 3 | 0.200628 | fresh_min_fill | -94 | 16 | 98 |
| 41 | 44 | 4 | 38 | 3 | 0.361907 | fresh_min_fill | -101 | 12 | 104 |
| 42 | 46 | 4 | 39 | 3 | 0.359212 | fresh_min_fill | -106 | 12 | 107 |
| 43 | 48 | 4 | 40 | 4 | 0.3572 | fresh_min_fill | -113 | 6 | 112 |
| 44 | 50 | 4 | 41 | 4 | 0.363719 | fresh_min_fill | -117 | 6 | 118 |
| 45 | 52 | 4 | 42 | 4 | 0.369012 | fresh_min_fill | -121 | 1 | 121 |
| 46 | 54 | 4 | 43 | 4 | 0.371544 | fresh_min_fill | -123 | 1 | 122 |
| 47 | 56 | 3 | 45 | 4 | 0.368883 | fresh_min_fill | -128 | 1 | 128 |
| 48 | 58 | 3 | 46 | 4 | 0.37435 | fresh_min_fill | -133 | 1 | 133 |
| 49 | 60 | 3 | 47 | 5 | 0.367542 | tie_portfolio | -138 | 1 | 138 |
| 50 | 64 | 3 | 48 | 5 | 0.365534 | fresh_min_fill | -140 | 2 | 143 |
| 51 | 66 | 3 | 49 | 5 | 0.373548 | transition_priority | -143 | 2 | 146 |
| 52 | 67 | 3 | 50 | 5 | 0.369625 | transition_priority | -144 | 2 | 147 |
| 53 | 69 | 3 | 51 | 5 | 0.370547 | fresh_min_fill | -144 | 6 | 149 |
| 54 | 72 | 3 | 52 | 5 | 0.372715 | transition_priority | -150 | 10 | 155 |
| 55 | 75 | 3 | 53 | 5 | 0.366231 | transition_priority | -155 | 4 | 159 |
| 56 | 77 | 3 | 54 | 6 | 0.357534 | fresh_min_fill | -158 | 4 | 161 |
| 57 | 81 | 2 | 56 | 8 | 0.377526 | tie_portfolio | -164 | 2 | 167 |
| 58 | 85 | 2 | 57 | 8 | 0.373003 | tie_portfolio | -169 | 4 | 172 |
| 59 | 88 | 2 | 58 | 9 | 0.373817 | fresh_min_fill | -173 | 4 | 177 |
| 60 | 91 | 2 | 59 | 9 | 0.375025 | fresh_min_fill | -177 | 4 | 180 |
| 61 | 93 | 2 | 60 | 10 | 0.37663 | fresh_min_fill | -181 | 4 | 182 |
| 62 | 98 | 2 | 61 | 10 | 0.7151 | fresh_min_fill | -188 | 4 | 189 |
| 63 | 100 | 2 | 62 | 10 | 0.733873 | fresh_min_fill | -190 | 4 | 193 |
| 64 | 103 | 2 | 63 | 10 | 0.746584 | fresh_min_fill | -193 | 2 | 197 |
| 65 | 106 | 2 | 64 | 10 | 0.757183 | fresh_min_fill | -198 | 2 | 201 |
| 66 | 111 | 2 | 65 | 10 | 0.709149 | fresh_min_fill | -202 | 2 | 206 |
| 67 | 114 | 2 | 66 | 11 | 0.746651 | fresh_min_fill | -205 | 3 | 209 |
| 68 | 118 | 2 | 67 | 12 | 0.724157 | fresh_min_fill | -211 | 1 | 213 |
| 69 | 121 | 2 | 68 | 12 | 0.72734 | tie_portfolio | -214 | 1 | 216 |
| 70 | 124 | 2 | 69 | 12 | 0.728134 | tie_portfolio | -219 | 1 | 220 |
| 71 | 128 | 1 | 71 | 13 | 0.726827 | tie_portfolio | -226 | 1 | 226 |
| 72 | 132 | 1 | 72 | 13 | 0.734869 | tie_portfolio | -231 | 2 | 232 |
| 73 | 137 | 1 | 73 | 14 | 0.72812 | tie_portfolio | -236 | 1 | 237 |
| 74 | 141 | 1 | 74 | 14 | 0.738483 | fresh_min_fill | -236 | 15 | 240 |
| 75 | 146 | 1 | 75 | 15 | 0.744142 | fresh_min_fill | -241 | 12 | 245 |
| 76 | 149 | 1 | 76 | 15 | 0.745729 | fresh_min_fill | -248 | 8 | 250 |
| 77 | 153 | 1 | 77 | 15 | 0.775793 | fresh_min_fill | -251 | 8 | 253 |
| 78 | 158 | 1 | 78 | 18 | 0.780967 | transition_priority | -254 | 8 | 256 |
| 79 | 162 | 1 | 79 | 20 | 0.782066 | fresh_min_fill | -260 | 8 | 262 |
| 80 | 166 | 1 | 80 | 19 | 0.808799 | transition_priority | -262 | 4 | 266 |
| 81 | 170 | 1 | 81 | 20 | 0.835143 | tie_portfolio | -264 | 4 | 270 |
| 82 | 174 | 1 | 82 | 21 | 0.829768 | transition_priority | -267 | 2 | 272 |
| 83 | 178 | 1 | 83 | 21 | 0.866123 | tie_portfolio | -268 | 17 | 275 |
| 84 | 183 | 1 | 84 | 22 | 0.93801 | tie_portfolio | -280 | 2 | 283 |
| 85 | 187 | 1 | 85 | 22 | 0.9377 | tie_portfolio | -285 | 2 | 289 |
| 86 | 191 | 1 | 86 | 22 | 0.917727 | tie_portfolio | -293 | 6 | 296 |
| 87 | 196 | 1 | 87 | 26 | 1.01546 | tie_portfolio | -293 | 12 | 297 |
| 88 | 200 | 1 | 88 | 24 | 1.28204 | tie_portfolio | -305 | 4 | 305 |
| 89 | 205 | 1 | 89 | 26 | 1.35516 | fresh_min_fill | -308 | 2 | 308 |
| 90 | 210 | 1 | 90 | 28 | 2.97611 | fresh_min_fill | -311 | 8 | 310 |
| 91 | 215 | 1 | 91 | 27 | 3.19676 | transition_priority | -323 | 8 | 322 |
| 92 | 220 | 1 | 92 | 26 | 3.15624 | transition_priority | -325 | 8 | 325 |
| 93 | 225 | 1 | 93 | 28 | 5.5756 | tie_portfolio | -336 | 4 | 336 |
| 94 | 230 | 1 | 94 | 28 | 9.38435 | tie_portfolio | -343 | 1 | 342 |
| 95 | 235 | 1 | 95 | 27 | 9.24034 | fresh_min_fill | -346 | 4 | 345 |
| 96 | 240 | 1 | 96 | 32 | 8.47395 | tie_portfolio | -346 | 12 | 348 |
| 97 | 229 | 1 | 97 | 26 | 18.5854 | inherited_N120_plan | -340 | 2 | 342 |
| 98 | 230 | 1 | 98 | 26 | 18.3615 | inherited_N120_plan | -341 | 2 | 343 |
| 99 | 231 | 1 | 99 | 26 | 18.3907 | inherited_N120_plan | -341 | 4 | 344 |
| 100 | 260 | 8 | 15 | 5 | 0.500951 | components | -260 | 256 | 177 |
| 101 | 234 | 1 | 101 | 26 | 23.8414 | inherited_N120_plan | -348 | 8 | 352 |
| 102 | 237 | 1 | 102 | 28 | 33.0255 | inherited_N120_plan | -357 | 4 | 362 |
| 103 | 239 | 1 | 103 | 32 | 33.1289 | inherited_N120_plan | -365 | 4 | 368 |
| 104 | 240 | 1 | 104 | 32 | 33.2076 | inherited_N120_plan | -368 | 4 | 371 |
| 105 | 275 | 8 | 15 | 5 | 0.361863 | components | -275 | 256 | 187 |
| 106 | 246 | 1 | 106 | 32 | 72.3749 | inherited_N120_plan | -378 | 4 | 383 |
| 107 | 249 | 1 | 107 | 33 | 74.1058 | inherited_N120_plan | -378 | 8 | 383 |
| 108 | 252 | 1 | 108 | 32 | 81.6992 | inherited_N120_plan | -380 | 16 | 385 |
| 109 | 255 | 1 | 109 | 32 | 82.1407 | inherited_N120_plan | -386 | 8 | 389 |
| 110 | 258 | 1 | 110 | 31 | 83.7856 | inherited_N120_plan | -392 | 4 | 395 |
| 111 | 260 | 1 | 111 | 31 | 92.471 | inherited_N120_plan | -395 | 4 | 398 |
| 112 | 264 | 1 | 112 | 33 | 93.7947 | inherited_N120_plan | -400 | 4 | 401 |
| 113 | 266 | 1 | 113 | 33 | 114.853 | inherited_N120_plan | -401 | 4 | 403 |
| 114 | 270 | 1 | 114 | 34 | 145.077 | inherited_N120_plan | -402 | 4 | 405 |
| 115 | 275 | 1 | 115 | 37 | 151.908 | inherited_N120_plan | -406 | 20 | 411 |
| 116 | 280 | 1 | 116 | 36 | 193.612 | inherited_N120_plan | -411 | 4 | 415 |
| 117 | 285 | 1 | 117 | 37 | 253.805 | inherited_N120_plan | -416 | 4 | 419 |
| 118 | 290 | 1 | 118 | 39 | 250.582 | inherited_N120_plan | -421 | 8 | 425 |
| 119 | 295 | 1 | 119 | 38 | 500.477 | inherited_N120_plan | -425 | 8 | 429 |
| 120 | 300 | 1 | 120 | 40 | 773.24 | source_bound_cutset_search | -434 | 8 | 435 |

### 18.1a All 23 connected-prefix completion runs

This table includes the connected-prefix N100 and N105 results that are deliberately separate from the packet defaults in the canonical table. It reports actual solve-stage time from each saved `COMPLETE.json`, using fourteen cooperative workers. Source/plan preparation, per-source qualification and publication are separate from these solve totals.


| N | Solve seconds | Arithmetic seconds | Preparation seconds | Width | Branches | Tasks |
|---|---|---|---|---|---|---|
| 97 | 18.5854 | 18.1081 | 0.458862 | 18 | 512 | 10240 |
| 98 | 18.3615 | 17.9746 | 0.37019 | 18 | 512 | 10240 |
| 99 | 18.3907 | 18.0021 | 0.370338 | 18 | 512 | 10240 |
| 100 | 23.8447 | 23.4894 | 0.336554 | 19 | 512 | 10240 |
| 101 | 23.8414 | 23.4934 | 0.330828 | 19 | 512 | 10240 |
| 102 | 33.0255 | 32.6674 | 0.339296 | 19 | 512 | 10240 |
| 103 | 33.1289 | 32.7031 | 0.405242 | 19 | 512 | 10240 |
| 104 | 33.2076 | 32.7767 | 0.413356 | 19 | 512 | 10240 |
| 105 | 67.7913 | 67.4016 | 0.340948 | 19 | 1024 | 20480 |
| 106 | 72.3749 | 71.9608 | 0.367742 | 19 | 1024 | 20480 |
| 107 | 74.1058 | 73.7323 | 0.355732 | 19 | 1024 | 20480 |
| 108 | 81.6992 | 81.2938 | 0.358629 | 19 | 1024 | 20480 |
| 109 | 82.1407 | 81.6911 | 0.407826 | 19 | 1024 | 20480 |
| 110 | 83.7856 | 83.3336 | 0.432371 | 19 | 1024 | 20480 |
| 111 | 92.471 | 92.0671 | 0.383277 | 19 | 1024 | 20480 |
| 112 | 93.7947 | 93.3815 | 0.394152 | 19 | 1024 | 20480 |
| 113 | 114.853 | 114.317 | 0.485634 | 19 | 1024 | 20480 |
| 114 | 145.077 | 144.506 | 0.486891 | 20 | 1024 | 20480 |
| 115 | 151.908 | 151.272 | 0.499337 | 20 | 1024 | 20480 |
| 116 | 193.612 | 193.077 | 0.514733 | 20 | 1024 | 20480 |
| 117 | 253.805 | 253.269 | 0.516462 | 20 | 1024 | 20480 |
| 118 | 250.582 | 250.044 | 0.493028 | 20 | 1024 | 20480 |
| 119 | 500.477 | 499.918 | 0.512142 | 20 | 2048 | 40960 |

Full identities: [GAP_23_MEASUREMENTS.csv](GAP_23_MEASUREMENTS.csv). The packet and connected-prefix sources at the same N provide a direct structural distinction in the corpus; their execution hardware and timing scope are retained separately.

### 18.2 All ten/twenty-worker GPU question measurements

Every row below is an exact successful GPU question with one GPU assigned to that question. Identical N values can refer to different variants or plans. Full source variant paths, question IDs, plan hashes, task counts and timing stages are retained in [ALL_GPU_MEASUREMENTS.csv](ALL_GPU_MEASUREMENTS.csv). These rows are separate from the restored cooperative fourteen-worker measurements in Section 11.


| Run | N | Question ID | Actual batch | Branches | Elapsed s | GPU phase s | Full density equal |
|---|---|---|---|---|---|---|---|
| podrun1 | 12 | 4e3788110fcec819bdfa70cc | 16 | 1 | 0.452909 | 0.0271049 | True |
| podrun1 | 72 | a17e7f8f755b4f79164fb25a | 16 | 1 | 2.2569 | 0.26484 | True |
| podrun1 | 72 | 9bcf2921c2c976676a0b0666 | 16 | 1 | 2.30342 | 0.268909 | True |
| podrun1 | 84 | 27db7574b95a1e3a1c9ae42a | 16 | 8 | 3.4299 | 1.38978 | True |
| podrun1 | 84 | c367e69b379d9fa48d779e60 | 16 | 1 | 4.49183 | 0.777857 | True |
| podrun1 | 72 | f3dd1f5f2848ed186e5fe242 | 32 | 1 | 1.15566 | 0.104973 | True |
| podrun1 | 72 | d08dd4162120d0313391ec17 | 32 | 1 | 1.10612 | 0.102028 | True |
| podrun1 | 84 | 8d704a9ac73bab42c3ae20af | 32 | 8 | 1.83022 | 0.808494 | True |
| podrun1 | 84 | 4531c032d02f61ea885881a1 | 32 | 1 | 3.91451 | 0.629516 | True |
| podrun1 | 96 | ca53264cde2a8f362bea069f | 16 | 16 | 42.1464 | 40.9949 | True |
| podrun1 | 96 | d5bca5708cbed4635e269ab1 | 32 | 16 | 39.5613 | 38.8769 | True |
| podrun1 | 96 | 80a35486979ee16c28b31dec | 16 | 32 | 90.9451 | 89.793 | True |
| podrun1 | 96 | d257606d969208ebd57156f1 | 32 | 32 | 85.8854 | 85.1612 | True |
| podrun2 | 12 | c1949b27329b43238fa2b270 | 64 | 1 | 1.02564 | 0.174406 | True |
| podrun2 | 12 | bfba7dfc30b0eee84e4e3061 | 64 | 1 | 0.780059 | 0.0359413 | True |
| podrun2 | 100 | ab194e9bee13186d683ece2d | 64 | 1 | 10.9183 | 0.306329 | True |
| podrun2 | 105 | 3d08f2d1f9ee3134e66b43fd | 64 | 1 | 10.9189 | 0.28129 | True |
| podrun2 | 72 | 1e4359ca957ffef7dba5cb46 | 64 | 1 | 10.8138 | 0.345335 | True |
| podrun2 | 84 | 39b81c39ef1d8b962a18fc2a | 64 | 1 | 12.6459 | 1.61439 | True |
| podrun2 | 100 | 38837497dce7eed5c0a302d2 | 64 | 1 | 7.84547 | 0.279215 | True |
| podrun2 | 105 | 76c4c046f3fed93b2c96a200 | 64 | 1 | 10.7691 | 0.315542 | True |
| podrun2 | 100 | 41a282e45225f48d20292822 | 128 | 1 | 3.14868 | 0.248828 | True |
| podrun2 | 105 | 1828f749c91c55acf9bde6ae | 128 | 1 | 4.35104 | 0.242951 | True |
| podrun2 | 72 | 253a59dfd04da76c1cf4c75f | 128 | 1 | 4.20496 | 0.274439 | True |
| podrun2 | 84 | 821d29cadc1844b52e1c4712 | 128 | 1 | 6.00824 | 1.47303 | True |
| podrun2 | 72 | b1838e1964641b6078ade471 | 64 | 1 | 0.885261 | 0.097485 | True |
| podrun2 | 84 | af182059d79459755baa725f | 64 | 8 | 6.07076 | 2.95014 | True |
| podrun2 | 84 | 120705e9c02796eee637d706 | 64 | 1 | 4.87324 | 1.34014 | True |
| podrun2 | 100 | ee751bcf8b6cc59aafe4b493 | 64 | 1 | 6.26903 | 0.159969 | True |
| podrun2 | 72 | 621040489d7a5175a41a6262 | 128 | 1 | 6.67134 | 0.49329 | True |
| podrun2 | 100 | 7130b90e1bf5a2b812f72e46 | 64 | 32 | 9.26196 | 3.00748 | True |
| podrun2 | 105 | 43a1ff7850798ebbf732a4ea | 64 | 1 | 4.99519 | 0.158097 | True |
| podrun2 | 105 | 62ac72eda8d4d97693fac6fe | 64 | 32 | 8.16686 | 2.94996 | True |
| podrun2 | 100 | 28741a18e9cd750a691cf57e | 128 | 1 | 3.39568 | 0.101962 | True |
| podrun2 | 100 | f1f0804def2759e1184e1c96 | 128 | 1 | 1.84418 | 0.307212 | True |
| podrun2 | 105 | 9563855fb2e753852647c27d | 128 | 1 | 1.93085 | 0.103684 | True |
| podrun2 | 105 | 44bc8e6db64f232007723b3a | 128 | 1 | 0.963834 | 0.100306 | True |
| podrun2 | 90 | 69bc04bb49cd9031b507b8b7 | 64 | 16 | 84.9193 | 81.1096 | True |
| podrun2 | 96 | 50b02ae4c6fdc3ebd62a2b6b | 64 | 32 | 97.8775 | 90.4074 | True |
| podrun2 | 99 | 4e238f06bc118de302bc8e16 | 64 | 32 | 98.1207 | 92.3032 | True |
| podrun2 | 90 | 0ffe490ad24f802d788055e0 | 64 | 32 | 129.518 | 126.053 | True |
| podrun2 | 101 | aa12604ffdf615af09aa2f6b | 64 | 32 | 150.783 | 146.58 | True |

### 18.3 Every question and method record

[ALL_QUESTIONS.csv](ALL_QUESTIONS.csv) contains each production question ID, run, N, kind, parent, methods, source variant, status, elapsed/predicted time where saved, generated children, result path, input hashes and full failure text. It includes the eight podrun2 precommits with no final result and excludes re-counting podrun3's inherited completed set.

[ALL_METHOD_MEASUREMENTS.csv](ALL_METHOD_MEASUREMENTS.csv) contains every row of the five run scorecards, with the originating run added. The first campaign's structural/measurement labels remain intact. Subsequent rows retain arithmetic medians and timing dispersion. [ALL_EVENTS.jsonl](ALL_EVENTS.jsonl) preserves every ledger event including smoke, interruption and parent/child history.

[RUN_COUNTS.json](RUN_COUNTS.json) provides the machine-readable count reconciliation used by this report. Original files are preserved alongside the exports, so no normalized report row replaces its source evidence.

## 19. Evidence, reproduction, and storage

This report and its evidence are inside the local repository directory:

`GEN4/frustrated_spin_learning1/reports/pre_blind_runs_20260926/`

The broader `frustrated_spin_learning1/` directory was **untracked in Git** when this report was prepared. Being present inside the working tree is different from being committed/pushed. This reporting task creates local files; it does not claim remote Git publication.

The pod ran working files under `/opt/gen4-learning/GEN4/frustrated_spin_learning1/`. Durable pod copies were stored under `/workspace/gen4/runs/frustrated-spin-learning-podrun1`, `...podrun2` and `...podrun3`. Before this report, not all those top-level reports and ledgers had been copied back locally. They have now been copied into this report's `evidence/` folder. The two restored N96 results and nine new CPU result receipts were also copied from podrun3.

This is a report/ledger evidence collection, not a claim that every large GPU residue/trace/native-session archive from all pod continuations was downloaded. The original durable campaign archives retain that deeper execution evidence. Earlier full training/frontier archives already have their own local custody records and are linked from their result reports.

Local report evidence folders:

- `evidence/workstation1/`: first campaign table, models, certificates, state and ledgers.
- `evidence/followup1/`: self-follow-up summaries, seven certificates, state, scorecards and ledgers.
- `evidence/frustrated-spin-learning-podrun1/`: copied ten-worker top-level records.
- `evidence/frustrated-spin-learning-podrun2/`: copied twenty-worker top-level records, including the older status and newer state.
- `evidence/podrun3/`: stopped continuation state, ledger and all eleven completed result JSONs.
- `evidence/gap_completion/`: exact completion status, catalog and report extracted from the retained gap archive.

`build_report.py` reproduces this synthesis from the named local sources and copied pod evidence without running a solver or touching a controller. `HASHES.txt` records SHA256 hashes for this report, exports, script and evidence files. The report preserves original family lineage and timing scopes. Canonical answers, global selectors, unrelated projects and the current research process were not modified.

**NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.** The report describes the completed work, operational improvements, exact records and retained failures in their source-defined terms. Helpful findings surfaced during compilation are the exact location/content of the seven certificates, the matched N96 plan/work/arithmetic relationship, and the three accounting/binding distinctions documented above: podrun2 snapshot lag, podrun3 inherited failures, and the N96 atlas timing/plan mismatch.

