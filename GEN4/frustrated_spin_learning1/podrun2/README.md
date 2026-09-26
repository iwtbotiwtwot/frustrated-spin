# GEN4 frustrated-spin learning podrun2

Follow-on to podrun1 on a 20-MIG RTX PRO 6000 Blackwell pod. Parent results and failures are read-only inputs; all new code, precommits, exact outputs, GPU residues and reports belong to this directory.

Campaign ceiling: eight hours. Up to20 GPU workers (one MIG partition each) plus8 CPU workers. Admission reads the live pod cgroup and resource manager. CPU exact workers may use up to20 GiB each (aggregate worker cap remains below pod memory); GPU arithmetic sizes from each MIG device’s measured free VRAM. Experiments may run up to two hours; exact CPU/GPU arithmetic has a 7,000-second operation cap. Separator search reaches depth20, residual components26 and estimated 100,000,000 assignments. GPU widths up to30, map bytes8 GiB, branch cap2^18, task cap10,000,000, root batches64/128. Measured source structures, observed rates and actual memory gates are retained per precommit.

Plans are rebuilt for each exact source and ordered retained ports. Failed previous attempts remain data. Every accepted density is checked against its canonical result or an independent exact route. No N121 or larger calculation. No hosted model calls, system services, global selectors, external hardware lifecycle operations or unrelated project edits.

Monitor `/workspace/gen4/runs/frustrated-spin-learning-podrun2/STATUS.json`, `SUMMARY.md`, `QUESTION_LEDGER.jsonl`, `GPU_SCORECARD.json`, `SEPARATOR_FINDINGS.jsonl`. Stop with SIGTERM to PID in STATUS; container disk holds working state; completed checkpoints mirror to volume.
