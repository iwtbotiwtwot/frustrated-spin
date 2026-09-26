# Portable restart

The workstation holds the pod predecessor runtime and all its source dependencies
under `restart/`. `restart/MANIFEST.json` records byte counts and SHA256 hashes;
all five original files were verified after transfer. Completed campaigns and the
focused installation are stored beside this document. Consult `RESULT.md` and
the N120 `RESULT.md` for the final execution and installation state.

Use a fresh pod with fourteen visible CUDA devices for these runners. The measured
cost models describe this fourteen Blackwell MIG setup. A different configuration
can execute exact arithmetic but needs its own timing calibration.

Restore these archives into the named directories (archive prefixes shown):

| Archive | Prefix | Destination after extraction |
|---|---|---|
| `restart/runtime-predecessor.tar.gz` | `runtime` | `/opt/gen4/current` |
| `restart/exact-source.tar.gz` | `source` | `/opt/gen4/n96-benchmark1/source` |
| `restart/catalog-code.tar.gz` | `catalog-code` | `/opt/gen4/spin-catalog1` |
| `restart/training-code.tar.gz` | `training-code` | `/opt/gen4/spin-training1` |
| `restart/focused-code.tar.gz` | `spin-focused1` | `/opt/gen4/spin-focused1` |
| `restart/n120-code.tar.gz` | `spin-n120-frontier1` | `/opt/gen4/spin-n120-frontier1` |

Copy `restart/activity.so` to `/opt/gen4/n72-benchmark1/activity.so`. It needs the
CUDA/CUPTI libraries supplied by the pod image. Restore a Python environment at
`/opt/gen4/venv`; `restart/ENVIRONMENT.txt` records installed versions. The spin
code uses NumPy1.26.4, CuPy13.6.0, python-flint0.8.0 and SymPy1.13.3, with the
retained native executables already included in the runtime archive.

If the final focused upgrade is installed, apply its portable installation
package to the restored predecessor using `install.py --root /opt/gen4/current
--evidence /opt/gen4/spin-focused-install-restored`, then run `adopt.py` against
the restored runtime. Use `/opt` for installation evidence: `/workspace` does
not support the timestamp operations used by predecessor backups. The installer
expects the predecessor; do not apply it twice to an already upgraded runtime.

Set the execution environment:

```sh
export PYTHONPATH=/opt/gen4/current
export PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0
export GEN4_SPIN_SOURCE=/opt/gen4/n96-benchmark1/source
export GEN4_SPIN_CATALOG_CODE=/opt/gen4/spin-catalog1
export GEN4_SPIN_TRAINING_CODE=/opt/gen4/spin-training1
```

N120 can start fresh or continue complete-task modular checkpoints. Restore the
N120 result archive's `ram/` directory to `/dev/shm/gen4-spin-n120-frontier1` for
continuation. Preserve `SOURCE.json`, `PLAN.json`, `RESIDUES*.npz`, and
`PROFILES*.json` together. A source or plan change requires a separate run directory.
The runner contains its N30 reference and does not need earlier training RAM.

```sh
/opt/gen4/venv/bin/python -u /opt/gen4/spin-n120-frontier1/run.py \
  --skip-training-wait --deadline "$(date -u -d '+60 minutes' +%s)"
```

The skip flag bypasses tonight's training completion log on a fresh pod. Confirm
the devices are available before launching. A completed N120 result is reused
through the installed catalog; restarting the solver is unnecessary for retrieval.

RAM is the work area. Compact modular sums/coverage flush about every30seconds to
`/workspace/gen4/runs/spin-n120-frontier1`; full native sessions, telemetry and
kernel traces flush at the final boundary. Preserve the final archive off the pod
before expiration. The predecessor archive, additive upgrade, source capsules,
completed training archives and N120 archive form the portable retained state.
