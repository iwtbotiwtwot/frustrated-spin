# Cooperative14 research summary

Owner: Sean Brady, originator and conceptual director.

Status: RESTART_AFTER_VERIFIED_BINDING_CORRECTION; new completed questions: 5; new observations: 36.

## 1. Did the pod remain in qualified topology?

Qualified original Focus/Frontier engines; accepted GPU measurements require14 live owners and positive contribution from every owner. 12 GPU observations retained. Topology/cohort PIDs are in each row.

## 2. Which measurements were excluded?

Historical single-MIG timings imported:0. Cold/initial loading and incomplete context excluded from normal cost fitting: 3. See backend model exclusion records.

## 3. What predicts CPU cost?

CPU models use PRE factor work, conditioned by method,cache and CPU topology. Current fitted groups: 8. Coefficients and source-grouped errors are in CPU_COST_MODEL.json.

## 4. What predicts cooperative-GPU cost?

GPU models use PRE weighted factor entries × roots × primes, conditioned by plan/backend/cache/readout. Groups: 3. No N-only selector.

## 5. When should GEN4 choose CPU?

Matched CPU/GPU placement calibration is pending; no result inferred from old topology timings.

## 6. Which features predict the N96 gain?

N96 targets branches,width,weighted entries,root/prime load and factor map preparation; warm comparison observations are in N96_PLAN_BACKEND.md.

## 7. Which residuals remain unexplained?

[{"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "plan_hash": "a6ac15413a3704a551d9e56c682c6201a61d1ab4b927a9c5fb182fc84b45df57", "backend": "LOCAL_FLINT_CPU", "method": "warm_components", "cache_state": "CACHE_REUSE", "log_residual": -0.19548467052230567, "observed_seconds": 0.01350359403295443}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "plan_hash": "9f381cca28e40506d8ac88dfbef352c29577c82dd8927bb442bafa0c14a1d713", "backend": "LOCAL_FLINT_CPU", "method": "warm_components", "cache_state": "CACHE_REUSE", "log_residual": 0.19548467052230567, "observed_seconds": 0.019963891478255395}, {"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "plan_hash": "da0c3ebe1a22b3ad2df71939cd5815aa6e1c35f645c366a9a0155ea98b1508b3", "backend": "LOCAL_FLINT_CPU", "method": "variable_elimination", "cache_state": "WARM_SAME_SOURCE", "log_residual": -0.04092807788517705, "observed_seconds": 0.022593928966671232}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "plan_hash": "36f415dc55f796534a8292eff61c9d1ffba193f9b9c59e84c444064502b52234", "backend": "LOCAL_FLINT_CPU", "method": "variable_elimination", "cache_state": "WARM_SAME_SOURCE", "log_residual": 0.04092807788517705, "observed_seconds": 0.02452118397923186}, {"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "plan_hash": "437347a4da455a5628500fe0cfe500a53a99be3e584c02eab7a4cafc95567497", "backend": "LOCAL_FLINT_CPU", "method": "components", "cache_state": "WARM_NEW_SOURCE", "log_residual": -0.03538277076251095, "observed_seconds": 0.22740638896357268}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "plan_hash": "a0463e01376b218bbaeba8761671595b4c8d31e88eee47ba51f35a7328d1bb51", "backend": "LOCAL_FLINT_CPU", "method": "components", "cache_state": "WARM_NEW_SOURCE", "log_residual": 0.03538277076251095, "observed_seconds": 0.24408199603203684}, {"source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b", "plan_hash": "437347a4da455a5628500fe0cfe500a53a99be3e584c02eab7a4cafc95567497", "backend": "LOCAL_FLINT_CPU", "method": "components", "cache_state": "WARM_SAME_SOURCE", "log_residual": -0.015906429735808914, "observed_seconds": 0.2240317355026491}, {"source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774", "plan_hash": "a0463e01376b218bbaeba8761671595b4c8d31e88eee47ba51f35a7328d1bb51", "backend": "LOCAL_FLINT_CPU", "method": "components", "cache_state": "WARM_SAME_SOURCE", "log_residual": 0.01590642973580869, "observed_seconds": 0.23127340397331866}]

## 8. Exact reusable rules?

0 independently verified project-local certificates; precise statements, support and counterexample searches are in CERTIFICATES.jsonl. No global installation.

## 9. Which rules or attempts failed?

3 failure/counterexample records retained. Capacity or implementation errors are typed separately from an exact precondition counterexample.

## 10. Did the generator maintain diversity?

Calibration cannot be displaced by descendants. Adaptive active frontier<=25,candidate pool<=40,each narrow family<=20%;three low-information siblings close/deprioritize a family; at most one capacity diagnostic. Current theme counts: {"packet_placement": 4, "plan_discrimination": 1, "source_calibration": 2, "transition_calibration": 1}

## 11. Five highest-value next questions

- Which PRE plan features explain the measured cost difference between distinct exact plans on the same cooperative14 backend? Source N096
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N100
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N105
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N100_prefix
- What is the warm exact cost of this source-bound plan on all fourteen cooperative GPUs? Source N105_prefix

## 12. What remains untouched?

N121–144 unexecuted; SOURCE_UNDEFINED entries contain no invented numerical predictions. Canonical files checked against the initial manifest at shutdown.

