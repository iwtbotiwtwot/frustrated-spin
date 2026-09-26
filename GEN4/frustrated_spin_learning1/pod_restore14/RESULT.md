# Original fourteen-worker spin configuration restored

Sean Brady requested restoration of the complete N1–120 execution configuration following an incorrect older-route N96 test. The historical runtime, focused installation, cached plans, exact batched readout, CUDA workers and N120 branch-group solver are restored on pod skqj84091pv7v0. No historical result was replaced.

## Execution configuration

- Fourteen persistent GPU owner processes, one Blackwell MIG 1g.24gb device each, shared prime/root task queue and shared CPU preparation/reconstruction. No eight-CPU-job scheduler.
- Original focused engine, reusable index/map caches, two-bank CUDA graph arithmetic, 16-root batches, batched inverse NTT and arbitrary-precision CRT.
- Original N120/gap branch-group engine, groups of 16 branches, fifth-prime capacity, and complete-task residue checkpoints.
- Original Python package versions restored in `/opt/gen4/venv`; per-library OMP/BLAS/MKL thread count one.
- Runtime `/opt/gen4/current`; full canonical atlas `/opt/gen4/spin-atlas`; original gap runners `/opt/gen4/spin-gap-97-119-1`. Working data use RAM/container storage; compact checkpoints use the volume.
- Actual allocation: 14 MIG workers, 95.2 CPU equivalents, 438,999,998,464 bytes host RAM. Historical allocation: 14 MIG workers, 47.6 CPU equivalents, 880 GB RAM. Software/process topology is restored; host CPU/RAM allocation is not identical and was not reconfigured.

## Verification and timing

49 original installation/adoption/recovery checks passed. All 120 canonical file hashes match the workstation copies. All 46 frozen N97–119 source/plan comparisons match. Original families, including packet-family N100/N105 and the distinct N120-prefix cases, remain separate.

N96 uses the exact retained expanded plan: 16 branches, width21, source dad9c1331dbc9b401ff729dde21b4e477b7b749ffea3504dab5b38c2c5d8fb44, plan 5e41d1760eb18bac845ae3d8eda407f1e653b37456b702db62734074278600df. All runs recomputed the exact answer; full scalar DOS and open/closed retained operators matched the historical result. Every GPU received work.

| Measurement | Seconds |
|---|---:|
| Historical three-repeat median | 3.257604178 |
| Restored cold-worker solve | 13.442205810 |
| Restored warm solve 1 | 3.487722907 |
| Restored warm solve 2 | 3.395276192 |
| Restored warm solve 3 | 3.407556477 |
| Restored warm median | 3.407556477 |

Cold worker preparation took 10.4624 seconds; source preparation before the solve took 0.1696 seconds. Warm and cold timing scopes are explicitly separate. The warm median is about 4.6% above the historical median; this measurement does not isolate the cause of that difference.

The original N30 branch-group/five-prime qualification also passed: 80 fresh tasks, all14 GPU workers active, full exact checks passed. The fifth-prime reconstruction check covered16,384 coefficients and a coefficient exceeding four-prime capacity. N120 itself and N121+ were not executed.

## Research continuation

Additive controller: `/opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun3/controller.py`. PID6331 was confirmed detached with PPID1; its first experiment completed exactly and its follow-up used14 actual GPU child processes. The first two new experiments completed without failures at the final setup check.

The inherited checkpoint preserves571 completed questions,69 pending questions and interrupted precommits. Six missing generated variants were reconstructed only after matching their original precommitted file SHA256 exactly; no inputs remain deferred. Prior results are inherited separately from new timing calibration. The first new question recalibrates N96 cost on the restored expanded plan; its outcome generates a matched-source alternative-plan comparison. Existing outcome-driven CPU research and structural planning continue between exclusive GPU-team calculations. CPU-only research questions do not pretend to occupy GPU workers.

The original deadline is preserved: 2026-09-26 23:47:44 UTC (18:47:44 CDT). No new hosted model calls are used. The controller checks the resource manager before each experiment, handles failures as data, writes precommits, creates native receipts and checkpoints, and uses bounded compact volume copies instead of repeatedly scanning the entire experiment tree.

## Monitor and stop

Direct SSH: `ssh root@81.27.69.178 -p 32272 -i ~/.ssh/id_ed25519`.

Monitor `/opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun3/STATUS.json`; detailed results and PRECOMMIT records are under its `experiments/` directory. Durable checkpoints: `/workspace/gen4/runs/frustrated-spin-learning-podrun3/`.

Stop safely with `kill -TERM 6331`, or create `/opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun3/STOP`. The controller terminates its own experiment group and preserves completed state. It does not stop the pod or unrelated workloads.

Qualification evidence and configuration: `results/CONFIGURATION.json`, `results/QUALIFICATION.json`, `results/ADOPTION.json`, `results/qualification-evidence.tar.gz`. Remote backup: `/workspace/gen4/runs/spin-restore14-20260926/`.

NEGATIVE DRIFT CHECK — COMPLETION: CLEAR.
Helpful findings: the previous test used the older32-branch/scalar-readout path; the original fast expanded-plan/batched-readout route restores the expected runtime. Host allocation differs despite the restored14-worker count. All canonical answers and holdouts remain unchanged.
