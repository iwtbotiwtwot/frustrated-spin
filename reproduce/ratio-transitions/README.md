# Reproduce the free/interacting-spin ratio result

Python 3.12 reference environment, CPU only. No GPU, private runtime, pod,
large dataset or expanded graph is required.

```sh
python3 -m venv .venv
.venv/bin/pip install -r reproduce/ratio-transitions/requirements.txt
.venv/bin/python reproduce/ratio-transitions/run.py verify-record
.venv/bin/python reproduce/ratio-transitions/run.py
```

The replay checks frozen source hashes, reconstructs the original component
factors, derives two exact tricritical points, enumerates the cores independently,
checks directed pressure inequalities and reconstructs the global polynomial
certificates. It compares exact results against the published records. Temporary
outputs are removed after comparison. About 7.5 seconds of original pod worker
time; runtime on other CPUs varies.

[Results and scope](../../research/spin_ratio1/REPORT.md) ·
[Complete derivation](../../research/spin_ratio1/PROOF.md) ·
[Original methods](../../research/spin_ratio1/METHODOLOGY.md)

This is the standalone reproduction path. Original production used a scoped
STARBREAKER adapter with retained SLC/CE receipts, as documented in the methods.
The source workers are unchanged; source/MANIFEST.json binds the exact bytes.
The original reports retain their research-workspace paths and dated custody
statements. Those paths are provenance, not dependencies of this public replay.
