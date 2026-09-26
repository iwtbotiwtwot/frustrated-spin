# Reproduce and operate

The pod runtime is the separately qualified `/opt/gen4/current`, using `/opt/gen4/restore14/activate.sh`. Original focused and frontier engines remain under `/opt/gen4/spin-focused1` and `/opt/gen4/spin-n120-frontier1`. The fresh campaign has independent state and files under `/opt/gen4-learning/GEN4/frustrated_spin_learning1/blind_restart1`.

`launch.sh` activates that environment and starts an eight-hour controller. Run it detached only after checking no other campaign owns `/opt/gen4/restore14/research-pool.lock`. A restart of this same directory recovers its own checkpoint and original deadline. A new blind run requires a new directory with no STATE.json, models, results or question ledger.

Before the first production launch, `blind_restart1_qualification` was a separate copy with a separate durable destination. Eight bounded questions checked the result-to-child loop. `checks.py` verifies explicit gauge/permutation inverses, an exact fourteen-worker N30 solve, child generation from success and failure, frontier replenishment and fresh cost-model updates. The first check omitted activation variables; its log/session were preserved. The next cost check used only a cold measurement, correctly excluded by the learner; it was preserved and amended to acquire a warm measurement. These check data do not seed production state.

Production: monitor STATUS.json, QUESTION_LEDGER.jsonl, FRONTIER.json and OVERNIGHT_SUMMARY.md. The ledger explicitly records parent IDs, generated child IDs, input hashes, resource snapshots, exact-verification contracts and outcomes. Send SIGTERM to the controller PID in STATUS.json or create STOP in the production directory to stop safely. The controller only signals its own experiment process group.

Container data are under `/opt`; RAM/VRAM hold arithmetic arrays. Durable small checkpoints and individual experiment archives are under `/workspace/gen4/runs/spin-blind-restart1`. The controller writes periodic state at most five minutes apart and after each result. No hosted calls, extra Codex turns, system services, global selectors, pod lifecycle changes or N121+ computations are launched.
