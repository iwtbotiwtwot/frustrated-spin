# Reproduce and operate

On the authorized pod:

```sh
cd /opt/gen4-learning/GEN4/frustrated_spin_pod14_learning1
. /opt/gen4/restore14/activate.sh
/opt/gen4/venv/bin/python controller.py --hours 8
```

Use launch.sh for detached execution. STATUS.json records the original deadline; restarting uses STATE.json and preserves that deadline and all completed IDs. Never remove STATE.json to resume. Do not rerun qualification into its retained artifact directory.

Monitor STATUS.json, OVERNIGHT_SUMMARY.md, QUESTION_LEDGER.jsonl and EXECUTOR.log. Stop safely with `touch /opt/gen4-learning/GEN4/frustrated_spin_pod14_learning1/STOP` or SIGTERM the PID in STATUS.json. Only this controller's executor process group is terminated.

POD_QUALIFICATION.json and RUNTIME_IDENTITY.json bind original installed solver/runtime/package hashes and GPU UUIDs. HASHES.txt binds current top-level campaign artifacts. Canonical input hashes are in ATLAS_MANIFEST.json. Source-bound PRECOMMIT and exact result hashes remain in experiments. Qualification and controller integration tests are not imported into production learning state.

The copied source_ops/cpu_routes utilities and vendor definitions retain historical implementation provenance; neither imports historical observations or queues. Timing models are rebuilt from the new STATE.json observations only. Native GEN4 receipts/checkpoints are retained in service/sessions and the durable mirror.
