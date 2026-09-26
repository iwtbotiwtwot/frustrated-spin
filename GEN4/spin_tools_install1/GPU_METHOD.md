# Installed exact CUDA spin execution

`spin_gpu.solve_gpu(source, plan, options)` promotes retained conditioning,
CUDA elimination graphs, inverse NTT and CRT arithmetic into one source-explicit
solver. The source and requested ports are explicit; a supplied plan is checked
against the graph. Without a plan, deterministic min-fill constructs one for
the requested ports. A planning operation itself computes no spectrum.

The source energy is `E=-sum(J*s_u*s_v)-sum(h*s_u)` with integer couplings/fields
and spins ±1. Bit i selects the sign at ports[i], with 0=-1 and 1=+1. Source
validation, distinct glue edges within the ports, conditioning/order coverage,
recomputed width, exact energy bound, root order and CRT capacity are checked
before execution. The product of qualified primes must strictly exceed 2^N.
The qualified fifth prime retains the N120 arithmetic capacity. Arbitrary
additional primes are not admitted by this implementation.

`build_gpu_vendor.py` extracts unchanged named exact-factor, projection and
root definitions from the retained exact-source archive. The CUDA worker and
kernel come from the catalog archive; batched readout comes from the focused
archive. Installed-relative imports replace campaign startup paths. The
compatibility namespace supplies only their existing arithmetic interfaces;
it imports no historical run script. Archive/member hashes and every emitted
file hash are retained in vendor/MANIFEST.json. Install that directory as
`CURRENT_REVISION/engines/SLC/gen3/spin_vendor/`. The live solver verifies these
file hashes before calling them. No old `/opt` path or campaign environment
variable is required. The readout documentation includes the fifth prime;
its squared products remain below signed-int64 capacity.

The executor observes visible CUDA devices. Optional `devices` and `workers`
restrict that observed roster; there is no fourteen-worker requirement.
Each selected device owns CUDA graphs, arrays, maps and a worker thread.
Root batches and conditioned-branch groups are powers of two. Each
prime/root-batch/branch-group contributes exactly once to modular totals.
Changing a branch group reuses its compatible graph layout and buffers.
CUDA-event nanoseconds and host/task times are retained; these are not SM
occupancy measurements and no old timing model predicts the new hardware.

Projection-map byte counts are calculated before materializing exponential
arrays. Width, branch/task counts, energy span, requested output size, map
bytes and resident arithmetic-array estimates have explicit admission limits.
VRAM estimates are checked against current free memory before allocation;
CUDA graph/pointer overhead also remains subject to the device allocator.
The defaults include width22,4096branches,1milliontasks and2GiB projection maps.
N120's qualified machinery is supported, but this installation does not launch
a new N120 solve merely to expose it.

`checkpoint_dir` enables resumable modular state. The immutable binding names
the source, mathematical execution plan, vendor and batch layout. Each flushed
NPZ is content addressed; an atomically replaced STATE.json authenticates its
hash, binding and coverage count. Load rejects changed sources/plans, invalid
shapes/ranges or changed residue bytes. Completed task coverage is retained
explicitly. The deadline returns `CHECKPOINTED` with no answer when a checkpoint
directory exists, and otherwise raises a timeout. A resumed call reports its
inherited task count and newly executed task count separately. A completed
checkpoint does not masquerade as fresh arithmetic.

Exact inverse NTT/CRT reconstructs all open-port polynomials and closed
conditional spectra. Retained count, first/second energy moment, per-port
count and polynomial-support checks remain. The common CPU/GPU finalizer
constructs canonical `GEN3_EXACT_SPIN_DOS_V1` output and repeats its own exact
checks. Elapsed times are integer nanoseconds; model metadata cannot alter
exact counts. GPU arithmetic runs through the installed source-bound domain
operation dispatched by spin_exact, rather than outside the native session.

The relevant runtime dependencies are NumPy, CuPy with CUDA support, FLINT
for the common finalizer, and the installed source/catalog modules. CUDA
availability is required only when GPU execution is requested. The workstation
can retain the same capability while using its exact CPU backend.
