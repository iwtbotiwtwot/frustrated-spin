# N3000 exact g(E,M,b) and reproduction package

**Large data are hosted on [Google Drive](https://drive.google.com/drive/folders/18y6ZEJGw6IhqAN-jJCXVvueTAzjwcypi) because of their size,
not stored in this Git repository.** This package contains methodology, source
code, checksums and reproduction/verification records.


All six N3000 cases are complete: `packet`, `signed_packet` and `signed_packet_chain`, each with fill coupling +1 and -1. Each has all 16 ordered-boundary states in two independently computed encodings. All 96 encoding pairs agree exactly. The primary encoding contains **550,074,346 exact records**; both encodings occupy **422,457,097,728 bytes** before compression.

Production on an RTX 3090 completed on September 29, 2026. The production phase took **1,712.316 seconds (28m32s)**, computing 190 rows and reusing two authenticated pilot rows. The pilot took 46.255 seconds. Production includes exact integer GPU transforms, CRT reconstruction, writing, fsync and checksum readback; it is not a GPU-kernel-only timing. `reference/PRODUCE.json` preserves the original production result. `reference/Q01.json` and `Q02.json` preserve qualification and the pilot; `gpu_source/` contains the exact bound production implementation and compiled source inputs.

Energy is `E = -sum J_uv*s_u*s_v - sum h_i*s_i`; magnetization is `M = sum s_i`. Ordered ports are `[0,1,60,61]`; bit i of boundary state b is 1 for spin +1 and 0 for spin -1. Frozen complete-graph sources and parents are in `inputs/N003000`. Counts remain exact integers throughout.

## Verify the complete retained record

```sh
python3 reproduce/n3000/run.py verify-record
```

This standard-library command authenticates 16 source files, the retained result and production code, and all 192 rows. It checks source/plan bindings, configuration-count closure, coverage, and agreement of canonical hashes, record counts and energy moments between the two encodings. It reads receipts rather than the bulk tables.

## CPU reproduction and shared runtime

Reuse the same Python 3.12 environment and public runtime as [N2000](../n2000/README.md). From a fresh checkout:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r reproduce/n3000/requirements.txt
python reproduce/n3000/run.py fetch-runtime --destination runs/n2000-runtime
python reproduce/n3000/run.py smoke \
  --runtime runs/n2000-runtime/runtime --work-dir runs/n3000
python reproduce/n3000/run.py verify-results --work-dir runs/n3000
```

Skip `fetch-runtime` when the N2000 runtime is already installed. No GPU or bulk-data download is required. Use a fresh work directory for each measured replay; allow 1 GiB free disk. The replay computes the **complete packet/+1 case**, all 16 boundary states in both encodings. It runs through a source-bound MATTER_SEARCH DomainSession, using exact CPU arithmetic and locally enumerated operators.

The measured replay passed in **10.486 seconds**, with all 32 canonical digests, moments, record counts and raw record SHA256 values matching the completed GPU run. See `VALIDATION.json`. The reproduction package recomputes one of the six cases. The other five completed cases are represented by the full retained record above. The portable engine is adapted from the tested N2000 CPU engine, with frozen input selection changed to N3000; `math_core.py` is unchanged.

The CPU replay writes the existing N2000-style `GEMB001\n` header plus exact records. The GPU archive is headerless. Verification strips the replay header before comparing the complete raw-record hash, so both formats are explicitly accounted for.

## Compressed shards and 100 GiB transfer batches

Each of the 192 production rows is compressed independently with Zstandard level 3. Each shard is decompressed on the producer and checked against the production raw SHA256 before it becomes available. Both encodings are preserved. Whole shards are grouped into transfer batches no larger than **100 GiB (107,374,182,400 bytes)**. Each batch stops before the next shard would exceed the cap.

`DATA_MANIFEST.json` lists all 192 compressed and raw rows, their sizes and SHA256 values, and the three batch inventories. Compression is complete: **236,963,585,976 bytes (220.69 GiB)**, down from 422.46 GB raw. Every shard passed decompression and raw-hash verification. All three workstation downloads are complete. Batches 001 and 002 have been uploaded to the [N3000 data folder](https://drive.google.com/drive/folders/18y6ZEJGw6IhqAN-jJCXVvueTAzjwcypi); their listed filenames, exact sizes and manifests were checked. Cloud payload hashes were not independently verified. Batch 003 is ready for upload. The completed archive manifest and each download batch receipt carry compressed sizes and SHA256 values. Bulk files are outside Git. The existing N2000 public data remain linked from its own package.

Given a downloaded batch and its `DOWNLOAD_STATUS.json`, verify it with:

```sh
python reproduce/n3000/data.py /path/to/batch-001 \
  --manifest /path/to/batch-001/DOWNLOAD_STATUS.json --deep
```

Install the `zstd` command for deep verification/restoration. Add `--restore /path/to/raw` to write the decompressed originals, allowing room for their raw sizes. Without `--deep`, the command verifies compressed sizes and SHA256 only. A complete batch has `status: BATCH_COMPLETE`; a live download receipt inventories only already verified shards.

Each raw record is signed int32 little-endian E, signed int32 little-endian M, and an unsigned **376-byte little-endian count** (384 bytes per record). There is no header in GPU production files. `data.records(path)` streams exact `(E,M,count)` values. T_MAJOR and K_MAJOR contain the same joint density in different orders; their canonical joint hashes match, while raw-file hashes can differ. Either complete encoding supplies the full g(E,M,b).

Sean Brady is originator and conceptual director; OpenAI ChatGPT and Codex are AI research collaborators. Project-owned code is MIT; research data and results are CC BY 4.0. Existing [license scope](../../LICENSING.md), [runtime grant](../../RUNTIME_LICENSE.md) and attribution apply.
