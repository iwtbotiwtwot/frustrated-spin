# Cooperative14 research summary

Owner: Sean Brady, originator and conceptual director.

Status: STOPPED; new completed questions: 73; new observations: 249.

## 1. Did the pod remain in qualified topology?

Qualified original Focus/Frontier engines; accepted GPU measurements require14 live owners and positive contribution from every owner. 156 GPU observations retained. Topology/cohort PIDs are in each row.

## 2. Which measurements were excluded?

Historical single-MIG timings imported:0. Cold/initial loading and incomplete context excluded from normal cost fitting: 39. See backend model exclusion records.

## 3. What predicts CPU cost?

CPU models use PRE factor work, conditioned by method,cache and CPU topology. Current fitted groups: 8. Coefficients and source-grouped errors are in CPU_COST_MODEL.json.

## 4. What predicts cooperative-GPU cost?

GPU models use PRE weighted factor entries × roots × primes, conditioned by plan/backend/cache/readout. Groups: 9. No N-only selector.

## 5. When should GEN4 choose CPU?

[{"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "source_key": "N100", "preferred_backend": "LOCAL_FLINT_CPU", "warm_end_to_end_seconds": {"LOCAL_FLINT_CPU": 0.02259392896667123, "COOP14_MIG_BRANCH_GROUP": 0.09102504}, "execution_context": {"LOCAL_FLINT_CPU": {"method": "variable_elimination", "plan_hash": "da0c3ebe1a22b3ad2df71939cd5815aa6e1c35f645c366a9a0155ea98b1508b3", "cache_state": "WARM_SAME_SOURCE"}, "COOP14_MIG_BRANCH_GROUP": {"method": "fresh_min_fill", "plan_hash": "9bba112fdafcc7ff8767041e14b7104dc56bb4e85722a3fea8c9f3578fb4077f", "cache_state": "WARM_SAME_SOURCE"}}, "status": "REPEATED_EMPIRICAL_RULE", "scope": "Matched source and ordered observable; native route includes internal checks; startup and external verification excluded; cache reuse alternatives separately recorded"}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "source_key": "N105", "preferred_backend": "LOCAL_FLINT_CPU", "warm_end_to_end_seconds": {"LOCAL_FLINT_CPU": 0.024194170022383332, "COOP14_MIG_BRANCH_GROUP": 0.107189816}, "execution_context": {"LOCAL_FLINT_CPU": {"method": "variable_elimination", "plan_hash": "36f415dc55f796534a8292eff61c9d1ffba193f9b9c59e84c444064502b52234", "cache_state": "WARM_NEW_SOURCE"}, "COOP14_MIG_BRANCH_GROUP": {"method": "fresh_min_fill", "plan_hash": "4ce49b3bd57787671e8d84190fc6ac27792c247097b95e747076012c6fbf8164", "cache_state": "WARM_SAME_SOURCE"}}, "status": "REPEATED_EMPIRICAL_RULE", "scope": "Matched source and ordered observable; native route includes internal checks; startup and external verification excluded; cache reuse alternatives separately recorded"}]

## 6. Which features predict the N96 gain?

N96 targets branches,width,weighted entries,root/prime load and factor map preparation; warm comparison observations are in N96_PLAN_BACKEND.md.

## 7. Which residuals remain unexplained?

[{"source_hash": "dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44", "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "fresh_min_fill", "cache_state": "WARM_NEW_PLAN", "log_residual": 3.8564621456281136, "observed_seconds": 9.909064456999998}, {"source_hash": "dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44", "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "expanded_portfolio", "cache_state": "WARM_NEW_PLAN", "log_residual": 1.08879598375094, "observed_seconds": 3.3804880754999997}, {"source_hash": "a9276261b491353b7a97dfe6fa8053ce22f644b61fc21d0b3c8e160a13727b0c", "plan_hash": "df459afe4918c4a5d2601a5fc00975c11aee6d4fd21a1ef6c4aa65578eb9404b", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "expanded_portfolio", "cache_state": "WARM_NEW_PLAN", "log_residual": -1.08879598375094, "observed_seconds": 0.38305685}, {"source_hash": "dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44", "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "fresh_min_fill", "cache_state": "WARM_SAME_SOURCE", "log_residual": 0.9366005480190434, "observed_seconds": 9.915663608999997}, {"source_hash": "23e5189c367e97c6f5689f15ec54e6d0aa61cd43346758be28ea6c77327c3ed6", "plan_hash": "684af504adde9c88bc3d4dce8cbc686ea9635ad884a3121f784288a02874bdf4", "backend": "LOCAL_FLINT_CPU", "method": "components", "cache_state": "WARM_SAME_SOURCE", "log_residual": -0.8391893545831994, "observed_seconds": 0.003879804455209524}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "plan_hash": "4ce49b3bd57787671e8d84190fc6ac27792c247097b95e747076012c6fbf8164", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "fresh_min_fill", "cache_state": "WARM_SAME_SOURCE", "log_residual": 0.8313517045308716, "observed_seconds": 0.10718981600000002}, {"source_hash": "2c949e8f79d3db8e94006a1e043cf1865a85042263efe0e3794f0385ac4e8ff4", "plan_hash": "ca15183fe5eabb0db37077d72fae45c4b83d053fee5455030505268a5471c254", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "fresh_min_fill", "cache_state": "WARM_NEW_PLAN", "log_residual": -0.8162727709567934, "observed_seconds": 0.09261677699999998}, {"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "plan_hash": "9bba112fdafcc7ff8767041e14b7104dc56bb4e85722a3fea8c9f3578fb4077f", "backend": "COOP14_MIG_BRANCH_GROUP", "method": "fresh_min_fill", "cache_state": "WARM_SAME_SOURCE", "log_residual": 0.6918508395551779, "observed_seconds": 0.09102504000000002}]

## 8. Exact reusable rules?

7 independently verified project-local certificates; precise statements, support and counterexample searches are in CERTIFICATES.jsonl. No global installation.

## 9. Which rules or attempts failed?

18 failure/counterexample records retained. Capacity or implementation errors are typed separately from an exact precondition counterexample.

## 10. Did the generator maintain diversity?

Calibration cannot be displaced by descendants. Adaptive active frontier<=25,candidate pool<=40,each narrow family<=20%;three low-information siblings close/deprioritize a family; at most one capacity diagnostic. Current theme counts: {"packet_placement": 4, "plan_discrimination": 1, "source_calibration": 2, "transition_calibration": 1, "verified_binding_correction": 4, "prefix_calibration": 1, "branch_calibration": 2, "high_cost_calibration": 1, "low_width_calibration": 1, "component_rule": 2, "unmeasured_regime": 43, "gauge_transfer": 5, "capacity_diagnosis": 12, "residual_plan": 5, "same_N_transfer": 5}

## 11. Five highest-value next questions

- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N113
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N095
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N103
- Which concrete source or verifier capacity condition explains this failure? Source N117
- Which admitted exact CPU method is cheapest for this source and cache state? Source N034

## 12. What remains untouched?

N121–144 unexecuted; SOURCE_UNDEFINED entries contain no invented numerical predictions. Canonical files checked against the initial manifest at shutdown.

