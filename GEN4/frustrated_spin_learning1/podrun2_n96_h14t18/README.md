# N96 H14F/T18 20-worker pod test

This additive test adapts the completed N96 H14F/T18 runner to the current
20-MIG pod. One persistent process owns each visible GPU worker. The host CPU
prepares packed factors, performs inverse NTT/CRT, exact gluing, and the source
directional-fiber closure. No separate CPU-only experiment workers run during
this test.

The calculation remains bound to historical dense N96 instance
`625bcd4327e678fa9541d7ab4109449e432d199aad1fba6e1f254395ebdd203d`.
The current canonical atlas N96 object has a different source hash
(`dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44`), so
this test is specifically a worker-layout/H14F-T18 test and will not replace
or be relabeled as the canonical-atlas N96 result.

One fresh full N96 calculation uses 20 GPU workers at root batch 16. All 4,096
roots across 32 cutset branches are calculated afresh. The original CPU fiber
and all retained exact checks remain in the solver. The test is bounded to one
run and writes active state to `/dev/shm`; only its compressed result/session
archive is sent to the durable `/workspace` mount after completion.

Run `pod_preflight.py` first. It requires 20 MIG devices visible through both
`nvidia-smi` and CuPy, at least 4 GiB free VRAM per worker, adequate RAM and
`/dev/shm`, and a successful small durable-volume write. `benchmark.py` checks
that the domain session resolves to `SLC-GEN4-P1`; it invokes the unchanged
source-bound H14F/T18 calculation with the worker count made configurable.

The previous `podrun2` campaign is kept separately. Its state and partial
outputs are not merged into this N96 test. After the N96 result is captured,
the broader learning controller can be restarted with a 20-GPU worker pool and
the CPU reserved for the matching exact readout/fiber stage.
