# Reproduction and recovery

From repository root, use `.venv-r3/bin/python`.

1. `GEN4/frustrated_spin_learning1/bootstrap.py` builds the additive source copies
   from manifests and retained archives. Do not rebuild during an active run.
2. `GEN4/frustrated_spin_learning1/controller.py --smoke --max-experiments 1 --hours .05`
   runs a bounded independent N6 exact replay with native receipts.
3. `GEN4/frustrated_spin_learning1/controller.py --hours 8` resumes STATE.json or
   creates an eight-hour campaign. Completed IDs are skipped. An interrupted
   precommit is recorded and skipped rather than silently repeated.
4. `touch GEN4/frustrated_spin_learning1/STOP` requests stop; SIGTERM interrupts
   a current child promptly. Preserve STATE.json and all experiment directories.

Use nohup with stdin detached and stdout to RUN.log. Controller PID is in
STATUS.json. Deadline and source/adapter hashes are retained. No random global
seed: the copied legal variant generator uses explicit deterministic seeds1..3.

Historical timing groups differ in hardware and readout. Atlas fits are
retrospective; only graph-derived PRE fields enter predictive feature matrices.
Historical selected-plan data is POST-selected and used descriptively. Per-method
CPU regressions only consume new verified timing rows. Native per-call sessions
retain GEN3_CHECKPOINT output and source-bound input/output receipts.
