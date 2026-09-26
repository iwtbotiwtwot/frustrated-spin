# Retained N96 execution and recovery

User-authorized pod `txqaltf4cdtfls`, verified direct SSH endpoint
`root@216.243.220.128:14657`. GEN4 base and CUPTI recorder are retained by the
preceding [N72 benchmark](../frustrated_spin_n72_bench1/RUN.md).

The original54-file source capsule is retained locally as
`SAM_REVIEW/campaigns/GEN3_POD_N96_H100X8_PREP1/payload.tar.gz` and extracted on
this pod at `/opt/gen4/n96-benchmark1/source`. The adapter scripts live in
`/opt/gen4/n96-benchmark1`. Preserve every completed run and select new paths:

```bash
cd /opt/gen4/n96-benchmark1
PYTHONPATH=/opt/gen4/current PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0 \
GEN4_N96_SOURCE=/opt/gen4/n96-benchmark1/source \
/opt/gen4/venv/bin/python -u benchmark.py \
  --ram /dev/shm/gen4-n96-NEW_RUN \
  --durable /workspace/gen4/runs/n96-benchmark1/NEW_RUN --runs 14:16
```

`runner.py` computes a fresh original N96 result. `gpu_graph.py` captures its
32cutset branches on two reusable VRAM banks; `kernel.cu` is the unchanged
retained modular-elimination kernel. `monitor.py` samples cgroup/process state
in RAM. `activity.so`, built from the retained N72 `activity.cpp`, captures
actual concurrent kernels. The native call has a900-second process timeout;
worker failures and traces are retained in the selected RAM directory.
The two qualified batch sizes are8and16.

Each completed archive contains source identity, graph, all four exact prime
lanes, final operator, recovered density of states/fiber, kernel timelines,
batch/worker profiles, CPU/memory/I/O samples and actual DomainSession receipts.
Use `analyze.py graph1` or `analyze.py graph2-b16` for saved-data reconstruction;
those commands do not rerun arithmetic. Archive SHA256 identities are in each
`complete.json`. The1.1MB original capsule and small successor scripts are
sufficient additions to the retained GEN4 base for restoration.
