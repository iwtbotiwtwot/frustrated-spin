# Dense solver1 launch — 2026-09-26

The pod has an accessible RTX PRO 6000 Blackwell Server Edition MIG 1g.24gb, CUDA compute capability 12.0. Driver UUID bytes: 661b6682ca4457c7a80b0259ec2f6b54. CUDA reported 25,367,150,592 bytes total device memory. Host nvidia-smi parent memory telemetry is permission-limited; CUDA operations and device memory reporting work.

Twelve N12/N18 dense qualification cases passed independent direct dense enumeration, full joint CPU/GPU table equality, two exact composition routes, binomial magnetization marginals, full DOS count/moments and ordered conditional closures. A nonzero-field variant passed. Four wrong controls were rejected. Six N30 dense cases passed next; their solve-plus-verification times were 2.8–14.6 ms, excluding process/CUDA initialization and persistence. This is not a measured GPU-versus-CPU speedup comparison.

The first attempt stopped because the synthetic nonzero-field control omitted stable parent vertex labels required by the existing normalizer. The first attempt and its error were retained; the corrected qualification passed. Runtime and canonical input files were unchanged.

Production controller PID 25333, PPID 1, session 25333. Start 2026-09-26T22:23:13 UTC, deadline 2026-09-26T22:53:13 UTC (5:53:13 pm America/Chicago). Thirty-minute maximum, one GPU owner, one CPU experiment. Cases: N30,60,96,120,300, three parents and both uniform fill signs. Completed N30 cases were hash-checked and skipped: catalog had 20 unique records, exactly six N30 records, at launch verification. First newly executed production case was N60 packet fill +1; both N60 packet fill signs had passed at the retained snapshot.

Remote project: /opt/gen4-spin-dense-solver1/project

Monitor:

    cat /opt/gen4-spin-dense-solver1/project/STATUS.json
    tail -f /opt/gen4-spin-dense-solver1/project/RUN.log

Safe stop (finish the current bounded case; admit no further work):

    touch /opt/gen4-spin-dense-solver1/project/STOP

The pre-existing packet run independently reached RESOURCE_GATE at N1203 at 22:19:28 UTC, before this pilot's first qualification at 22:20:34. The dense follower finished caught up at N1203. Later cgroup inspection showed ~35.96 GB file cache, ~0.138 GB anonymous memory, and zero OOM events. The previous manager gate reserves 8 GiB but subtracts all cgroup usage, including reclaimable cache. This pilot preserves that manager observation and adds an explicit clean-inactive-cache estimate, with its own 4 GiB process RSS and disk/time gates. No previous campaign was edited or restarted.

`pod_launch/` is a point-in-time evidence snapshot, not current live status. Native session paths in receipts remain on the pod. The launch archive contains exact results, sources, precommits, control records, and the initial failed-attempt metadata; no native custody keys are included. Preserve full container artifacts before retiring the pod.
