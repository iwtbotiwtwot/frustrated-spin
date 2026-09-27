# Magnetization2: exact composition and memory optimization

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are AI research collaborators.

Owner direction: finish packet N1350, keep downloading to lilhelper T500, then focus the pod on analysis and acceleration of the exact dense magnetization solver using CPU, GPU, RAM and VRAM as appropriate. The completed N1..1350 packet calculations and previous dense pilot remain immutable.

## Measured target

At N300, six complete-graph cases took 0.288–121.456 s including exact replay and verification, excluding cold CUDA initialization and persistence. Peak host RSS was 228–984 MiB. Hardest case: signed chain, fill -1; primary composition 12.172 s, replay composition 100.933 s. GPU local arithmetic was below 0.2 ms per source; the largest local output was 262,144 bytes. These measurements motivate CPU composition and memory improvements first. They do not demonstrate a benefit from more GPU workers or VRAM.

## Exact reduction

Dense completion energy is the uniform magnetization term plus the original-source correction, with bridge delta J_parent-J_fill. A bridge with delta=0 contributes exactly zero for every assignment. Splitting the correction graph at precisely those bridges preserves the entire joint distribution of correction energy, magnetization and ordered ports. For the current alternating signed chain, these cuts yield small independent packet components, mostly pairs. Enumerating all spins globally is unnecessary because the joint generating function factors across disconnected correction components.

Compute each component's joint polynomial using its own small stride. Equal complete component polynomials may be reused exactly via integer powers. Compose a balanced product; decode one retained-port polynomial at a time rather than holding all 16 global port polynomials. The uniform M² energy shift is applied only after the exact joint distribution is composed. This is an exact use of established factorization, with every source/correction term accounted for, not a learned substitution for required arithmetic.

Verification uses independently CPU-enumerated local tables, forward versus backward component contraction, and a different global Kronecker encoding. The full joint spectrum, conditional spectra, all counts, binomial magnetization marginals and exact moments must agree. Small N also has direct dense enumeration. All N300 results must match the previous full retained spectra. The hardest N300 case additionally reruns the original slow solver in the same process and compares every result.

## Bounded run

One GPU owner and one CPU experiment at a time on the existing pod; no hardware reconfiguration or rental. Qualification at N12 and N18 (both fill signs, all three families), nonzero-field control and four wrong controls. Then N300, N450 and N600, six cases per N. Cases stop on mismatch, 15-minute wall limit, 8 GiB host RSS, 200 GiB free-disk reserve, or the one-hour run window. A case is admitted only with its full time allowance remaining. No N above 600 in this dense pilot. This does not restrict the already completed separate packet catalog N1350.

Matched GPU versus CPU local costs are retained; large-integer composition remains on CPU FLINT. A GPU convolution would require verified modular arithmetic and CRT for the full coefficient bound. It will be proposed only if the new stage timings justify it. Extra VRAM cannot by itself accelerate a CPU-bound step.

Remote project: /opt/gen4-spin-magnetization2/project

    /opt/gen4-spin-continuation1/.venv/bin/python run.py --qualify --minutes 30
    /opt/gen4-spin-continuation1/.venv/bin/python run.py --minutes 60

Monitor STATUS.json, RUN.log and CATALOG.jsonl. Stop safely with project/STOP or SIGTERM; only the current bounded case finishes. Existing transfer and pod history remain untouched. Source code manifests, precommits, full exact results, comparisons and native session receipts remain in this additive project.
