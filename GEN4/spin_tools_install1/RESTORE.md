# Spin tool installation and recovery

The installation is complete on the workstation and research pod. Use the
existing runtimes directly; restoration is needed only after a lifecycle loss
or into a separately prepared runtime.

- Workstation root: `/home/sam/PycharmProjects/SAM_Research_Project`.
- Research pod: `root@198.13.252.37`, port32398, identity`~/.ssh/id_ed25519`.
- Pod runtime: `/opt/gen4/current`.
- Pod package/evidence: `/opt/gen4/spin-tools-install1`.
- Durable web report: `/workspace/gen4/rh-voli-unified1/sources/GEN4/spin_tools_install1`.
- Durable restore capsule: `/workspace/gen4/runs/spin-tools-install1/RESTORE_CAPSULE.tar.gz`.
- Capsule SHA256: `ed60896c4560161fe10b8fee64c968ea35d48c1165f20d278fce04c1d1895be2`.

The capsule retains the three prerequisite installer packages, their successful
install/adoption records, the final source-aware package, staged final runtime
changes, rollback predecessors, native qualification sessions, returned results,
GPU checkpoint and CLI output. Its tar root is `spin-tools-install1/`. Original
GEN4 base runtime restoration remains the existing pod-release procedure.

For a fresh restored base that lacks spin capability, install the prerequisite
packages in order: `frustrated_spin_catalog1`,
`frustrated_spin_training_install1`, `frustrated_spin_focused_install1`.
Their installation and adoption commands are preserved in the stage logs and
portable scripts. Inspect the installed catalog first; do not apply earlier
stages over an already newer spin installation.

Then use the final installer with a new evidence directory:

```sh
cd /opt/gen4/current
PYTHONPATH=/opt/gen4/current /opt/gen4/venv/bin/python -B \
  /opt/gen4/spin-tools-install1/package/install.py \
  --root /opt/gen4/current --evidence /opt/gen4/spin-tools-restore-evidence
./current-revision --verify
./spin-tools sources
```

The installer authenticates the baseline, preserves previous bindings and
references, stages backups, changes the current runtime transactionally, and
rolls back on verification failure. It does not change generation identity.
The final package hashes are retained in `PACKAGE_MANIFEST_FINAL.json` beside
the durable web report and in the workstation campaign.

Existing native results can be recovered by explicit source/result references
in compatible sessions. A GPU checkpoint is reusable only with its matching
source, plan, vendor and batch layout. Inspect inherited and fresh task counts;
the completed qualification checkpoint has80retained tasks and needs no new
arithmetic. Resource limits and native API contracts are in `GUIDE.md`.
