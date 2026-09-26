# Retained N72 benchmark route

Pod: user-supplied `txqaltf4cdtfls-644122c4@ssh.runpod.io` with the existing SSH key.
Verified direct endpoint for this run: `root@216.243.220.128:14657`.

The installed base is `/opt/gen4/current`, built for this CPU and CUDA12.8.
Benchmark scripts are `/opt/gen4/n72-benchmark1/`; compact durable checkpoints
are `/workspace/gen4/runs/n72-benchmark1/`. Active state uses `/dev/shm`.

The selected source-bound successor is `benchmark_graph.py` +
`gpu_graph_trace.py` + `monitor.py` + `activity.so` compiled from `activity.cpp`.
It runs16 fresh N72 calculations with all14 workers, batch32, tracing actual
kernel activity. Use new RAM and durable paths on every run:

```bash
cd /opt/gen4/n72-benchmark1
PYTHONPATH=/opt/gen4/current PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0 \
GEN4_N72_SOURCE=/opt/gen4/current /opt/gen4/venv/bin/python -u benchmark_graph.py \
  --ram /dev/shm/gen4-n72-NEW_RUN \
  --durable /workspace/gen4/runs/n72-benchmark1/NEW_RUN --runs 14:32
```

Source deployment is reproducible from the existing local
`GEN4/vol_i_ruler_clock1/deployment/GEN4_SOURCE.tar.zst`
(SHA256 `5505bd94ccede4cd6f553e6aa0b1a7fd15621e65b42506110abf940cf2b005d4`),
the N72 source capsule in this directory, and these successor scripts.
The runtime archive contains a `source/` prefix. Extract the N72 capsule into
that actual source root. Install its pinned `requirements.lock` into an isolated
venv; native build requires g++, libgmp-dev, nlohmann-json3-dev and libssl-dev.
Run the packaged `tools/build.sh` on the pod, then
`CURRENT_REVISION/current.py --verify`. The source instance and33retained
arithmetic dependency hashes are checked before every benchmark invocation.
`SOURCE_FILES.json` binds the68-file dependency capsule.

Compile activity tracing against the installed CUDA headers:

```bash
g++ -O2 -shared -fPIC -std=c++17 activity.cpp -I/usr/local/cuda/include \
  -L/usr/local/cuda/lib64 -Wl,-rpath,/usr/local/cuda/lib64 -lcupti -o activity.so
```

The RAM checkpoint archives retain actual DomainSession receipts, native state,
root evaluations, exact coefficients, fiber attachments, traces and telemetry.
`analyze.py` and `concurrency.py` inspect saved outputs and do not rerun arithmetic.
`complete.json` beside each archive binds its SHA256. All source/result files
are preserved on the workstation as well as the pod's retained checkpoints.
The service closes its finite worker queue after benchmark completion; a future
catalog controller should keep those owners alive across useful queued sources.
