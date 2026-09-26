# Reproduction and recovery

Inputs: N1..120 frozen atlas from the SHA256-checked podrun1 input bundle; prior podrun1 status, precommits, result receipts, GPU scorecard and separator findings from `/workspace/gen4/runs/frustrated-spin-learning-podrun1/`. The new run writes only `/opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun2` and mirrors completed state under `/workspace/gen4/runs/frustrated-spin-learning-podrun2/`.

Run the isolated controller with the podrun2 venv. STATUS reports PID and deadline. SIGTERM completes active children, persists state and mirrors results. Restart reloads queue/ledger and does not repeat completed questions. Each experiment stores PRECOMMIT, native MATTER_SEARCH session/receipts, result/checkpoint and exact verification. Worker MIG assignment, live cgroup/RAM sample, exact source hashes and code digest are recorded in PRECOMMIT.

All calculated N values are at most120. Replaying GPU arithmetic is always fresh; no answer may be inferred from runtime or plan cost.
