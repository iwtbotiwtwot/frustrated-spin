# Exact dense solver1 — bounded GPU/CPU pilot

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are AI research collaborators.

Owner request: start testing an exact dense solver on the existing pod and use the GPU where useful. This is an additive test; existing packet continuation and dense graph follower are not modified. Canonical frustrated-spin results remain unchanged.

## Mathematical map

Each tested graph is the exact complete graph in the dense follower: preserve every parent coupling and field, fill every previously absent edge with J0=+1 or -1. For M=sum(s_i),

    E = -J0*(M*M-N)/2 - sum_parent((Juv-J0)*su*sv) - sum_i(hi*si).

The correction graph retains the parent packet decomposition and chain bridges. Each local assignment contributes to an exact joint table of positive-spin count k, shifted correction energy t=(Ec+B)/2, and ordered retained/gateway states. CUDA enumerates the local assignments using integer arithmetic only. An independently written CPU Gray-code enumeration checks every local coefficient.

Global composition uses FLINT arbitrary-precision integer polynomials. The primary route encodes (k,t) as k*(B_total+1)+t and contracts the gateway chain backward. The replay encodes it as t*(N+1)+k and contracts forward. Because all intermediate k<=N and 0<=t<=B_total, neither encoding has a carry between dimensions. Each correction term belongs to exactly one local packet or declared bridge. Multiplication counts each assignment once. Final readout applies the exact collective magnetization energy. Full joint spectra and all final conditional coefficients must agree between the two routes.

Full local tables, source hashes, plans, full dense DOS, all ordered-port rows, all 3^p partial port closure spectra hashes/counts/moments, and exact replay hashes are retained. The ordered rows are the complete open-boundary operator. Scalar count is 2^N, first moment zero, second moment 2^N times the sum of squared fields/couplings. Every magnetization marginal is independently required to equal its conditional binomial count. At N<=18, independent enumeration directly over every dense edge checks the entire final answer.

This solver uses uniform completion plus a structured correction; it does not assume a route for arbitrary unrelated dense couplings. It does not reuse old energy-only packet tables. CPU and GPU timing stages, including CUDA initialization, are recorded separately. This pilot tests correctness and resource cost, not a GPU speedup claim.

## Scope and resources

Qualification: N12 and N18, three parent families, both fill signs (12 dense sources); plus a nonzero-field variant and four deliberate wrong controls. Then a smoke cycle at N30. Production: N30,60,96,120,300, all six variants, skipping hash-verified completed smoke cases on restart. Maximum N is 300; no open-ended continuation.

One GPU owner and one CPU experiment process, low priority; existing three CPU producer workers and two follower workers are left intact. Available GPU: one RTX PRO 6000 Blackwell 1g.24gb MIG slice. GPU access is established through CUDA, including actual free memory, because parent-device memory telemetry is permission-limited. No packages, GPU settings or runtime binding files are changed. CUDA driver and NVRTC are already installed; local GPU tables need at most 2 MiB of output per table under the admission bound.

Use the existing GEN4 resource-manager observation plus an explicitly recorded, project-local clean-inactive-cache allowance. Enforce 4 GiB host RSS per experiment, 480 seconds per case, 200 GiB disk reserve, local enumeration <=2^18, polynomial degree <=600,000. A separate controller watches each case and can terminate only its own process group on a gate. Default campaign window 30 minutes; admit a case only with its full eight-minute allowance remaining. SIGTERM/STOP prevents new admission and finishes the current bounded case. Failures stop the pilot and remain recorded; no automatic retry. Full data remains on container storage; only compact status/receipts are mirrored.

## Execution and restart

Pod: /opt/gen4-spin-dense-solver1/project

    /opt/gen4-spin-continuation1/.venv/bin/python run.py --qualify --minutes 20
    /opt/gen4-spin-continuation1/.venv/bin/python run.py --smoke --minutes 15
    /opt/gen4-spin-continuation1/.venv/bin/python run.py --minutes 30

`CODE_MANIFEST.json` freezes source before experiments. Each nontrivial case has an immutable precommit binding source/graph/ports, plan, code, runtime, route, resources and verification. The adapter executes through DomainSession on the restored MATTER_SEARCH runtime. A fresh CUDA context is used per case, with initialization reported separately. Existing successful case artifacts are hash-checked and skipped on restart.

Monitor STATUS.json and RUN.log. Safe stop:

    touch /opt/gen4-spin-dense-solver1/project/STOP

Preserve the full container results before retiring the pod. Do not publish any native session custody.key.
