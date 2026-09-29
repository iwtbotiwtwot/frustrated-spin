# Reproduce N2000 exact g(E,M,b)

All six N2000 graph cases completed: packet, signed_packet and signed_packet_chain, each with fill coupling +1 and -1. Each case retains all 16 ordered-boundary states in two independently computed encodings. The 96 primary rows contain 244,104,392 exact (E,M,count) records. Original production completed in 816.625 seconds on 27.2 CPU equivalents with 14 workers x 2 FLINT threads and a 465.66 GiB cgroup RAM limit. Both A100s prepared 22 CPU-checked local tables; global arithmetic ran on CPU. These are measured run details, not timing guarantees on other hardware.

`g(E,M,b)` counts configurations of 2000 binary spins. Energy is `E = -sum_{u<v} J_uv*s_u*s_v - sum_i h_i*s_i`; magnetization is `M = sum_i s_i`. Ordered retained ports are `[0,1,60,61]`. State integer `b` has bit i=1 for spin+1 at port i, and bit i=0 for spin-1. The graph manifests under `inputs/N002000` define each complete source and pin its compressed parent and complete pair-coupling bitstream. No source is reconstructed from prose alone.

## Verify the retained completed result

```sh
python3 reproduce/n2000/run.py verify-record
```

This standard-library check authenticates the 16 source files and verifies all six scientific manifests, 96 boundary states and 192 independent encoding receipts. It checks configuration-count closure and canonical/binary hash agreement. It does not claim to recompute the large spectra or read absent bulk data. The original `reference/PRODUCE.json`, `reference/results` and original source scripts remain unchanged. Filesystem paths and process IDs inside historical receipts describe the original run.

## Install the exact reproduction environment

Use Linux and Python3.12. Install the OS Python venv package if your distribution omits it. Zstandard is needed only for compressed-data verification/restoration.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r reproduce/n2000/requirements.txt
python reproduce/n2000/run.py fetch-runtime --destination runs/n2000-runtime
```

The runtime downloader checks the existing 386MB public release SHA256 before extraction. It also restores a 143,710-byte sealed foundation source archive that the prior public exporter omitted. `RUNTIME_SUPPLEMENT.json` records this correction; the supplement matches the runtime's existing foundation hash. No authentication check is bypassed and no bound runtime code is changed. Installation also copies the checksum-verified open license grant and texts into `runtime/PUBLIC_LICENSES`, alongside the unchanged sealed runtime files. New native sessions generate their own private state under the new work directory. Original private custody keys are not published.

## Small qualification and an actual N2000 reproduction

```sh
runtime_dir="$PWD/runs/n2000-runtime/runtime"
run_dir="$PWD/runs/n2000"
python reproduce/n2000/run.py prepare --runtime "$runtime_dir" --work-dir "$run_dir"
python reproduce/n2000/run.py qualify --runtime "$runtime_dir" --work-dir "$run_dir"
python reproduce/n2000/run.py smoke --runtime "$runtime_dir" --work-dir "$run_dir"
```

Preparation enumerates the same 22 exact local tables on CPU, so CUDA is not required. The historical `GPU_TABLES.json` filename remains a compatibility catalog name; new receipts identify CPU enumeration. Qualification compares N12 with independent joint variable elimination, N30 with the uncompressed component method, and rejects a truncated binary. The smoke command really computes the complete N2000 packet/+1 case: all 16 boundaries in both encodings. All 32 binary SHA256 values must match the original published result. In the clean public-runtime test this compute phase took 3.07 seconds. `VALIDATION.json` records the checks and the initial missing-foundation failure/correction. The other five large cases were not rerun for this publication.

## Recompute all six cases

Use a separate output directory with at least 150GB free durable disk; the two exact encodings total 126.45GB. The original single-thread pilot peaked at 17.79GiB per worker. The runner measures your own pilot and uses a 1.5x allowance, an 85% memory budget, CPU quota and RAM-staging capacity to admit workers. A large machine is needed for comparable parallel throughput. A smaller admitted allocation can run fewer workers. No automatic cloud provisioning occurs.

```sh
python reproduce/n2000/run.py pilot --runtime "$runtime_dir" --work-dir "$run_dir" --threads 2
python reproduce/n2000/run.py produce --runtime "$runtime_dir" --work-dir "$run_dir" --threads 2
python reproduce/n2000/run.py verify-results --work-dir "$run_dir"
```

The pilot computes boundary zero of signed_packet/-1 in both encodings using one worker, then compares canonical digests. Production automatically chooses a fitting worker count; add `--workers 14` to request the recorded topology when memory and CPU limits admit it. RAM staging defaults to `/dev/shm/spin-n2000`; set `--ram-dir` on each command if needed. Allow at least 2GiB staging per worker (e.g. 32GiB shared memory for 14 workers). Completed rows flush/fsync to durable disk and are checksum-read back. Keep the work directory on persistent local/container storage.

Every mathematical operation executes through a source-bound MATTER_SEARCH DomainSession. The portable adapter retains the original arbitrary-precision arithmetic and binary format; it changes paths, resource selection and local-table preparation. It does not require the old pod IP, root account, two GPUs, workstation paths or original session secrets. Output verification requires all 192 reproduced rows to match original binary and canonical SHA256, counts, moments and source identities.

Watch progress with `tail -f` on redirected stdout or read `results/PROGRESS.json` under the work directory. Each job contains two boundary states. `touch "$run_dir/STOP"` stops at boundary checkpoints; wait for the process to exit before copying results. To resume, intentionally remove STOP and rerun produce with the same sources/code/work directory. It hashes and reuses existing complete rows. Ctrl+C requests the same checkpoint stop. `produce` is a foreground command: run it under tmux or your service manager for disconnection resilience.

## Obtain and verify the bulk data

The public-upload set is 96 `.bin.zst` files totaling 37,397,887,721 bytes (34.83GiB), restoring to 63,223,097,516 bytes. The [public Google Drive folder](https://drive.google.com/drive/folders/1F8wvIRqL3pdB34db-llz0YjnIbFbRg9Y) supplies the data. Its exact hosting status and each compressed/original SHA256 are in `DATA_MANIFEST.json`. Anonymous small and large download checks passed both hashes. Recomputing the exact tables above does not depend on the bulk-data host. The second encoding's full scientific receipts are in this repository; the primary encoding contains the complete g(E,M,b).

Download with the per-file IDs in the manifest; this avoids folder-list pagination limits. The optional downloader uses gdown 5.2.0 and does not use browser cookies or require a Google login:

```sh
python -m pip install -r reproduce/n2000/requirements-download.txt
python reproduce/n2000/data.py /path/to/downloads --download
```

For a quick public-download check, add `--case packet_+1 --state 0 --deep`. Downloads resume through temporary files and are renamed only after their compressed SHA256 matches. Existing valid files are reused. Google Drive can impose download quotas; in that case the command reports the failure and retains partial data for retry.

Check public availability and expected sizes without downloading the full dataset:

```sh
python reproduce/n2000/check_host.py
```

Once the files are downloaded into one directory:

```sh
python reproduce/n2000/data.py /path/to/downloads --deep
python reproduce/n2000/data.py /path/to/downloads --restore /path/to/restored
```

Use `--case packet_+1 --state 0` to check or restore just one boundary. `--deep` verifies decompressed hashes without storing raw data; `--restore` writes exact originals beneath `results/N002000`. Keeping both compressed and restored primary data needs approximately 100.6GB. The standard-library `records(path)` iterator in data.py streams exact Python-integer `(E,M,count)` records.

The binary format starts with `GEMB001\n`, then a four-byte little-endian JSON-header length, then the JSON header. Each record is signed int32 little-endian E, signed int32 little-endian M, and a 251-byte unsigned little-endian count. Counts are never floating point. K_MAJOR and T_MAJOR order the same joint records differently; their canonical joint digest agrees even when file hashes differ. Summing counts over M and/or boundary states yields exact marginal densities.

## Scope and attribution

This publication installs completed N2000 joint results and a tested portable reproduction path. The earlier N3000 stop at 12 rows is superseded by the [completed N3000 GPU run and cheap CPU replay](../n3000/README.md). Prior contiguous graph construction through N1408 and later N2000/N3000/N4000/N5000 construction milestones are distinct from solved joint-table coverage. Sean Brady is the originator and conceptual director; OpenAI ChatGPT and Codex are AI research collaborators. Project-owned code is MIT; data, reports and figures are CC BY 4.0. See [license scope](../../LICENSING.md), [frozen runtime grant](../../RUNTIME_LICENSE.md) and [citation](../../CITATION.cff). The original hashes and scientific receipts are unchanged.

The pinned GitHub Actions workflow runs retained-record verification, public-runtime installation, CPU preparation, N12/N30 qualification and the complete N2000 packet/+1 smoke case. It does not launch the six-case large-memory production run.
