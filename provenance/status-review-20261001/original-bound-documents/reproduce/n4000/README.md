# N4000 exact g(E,M,b) and reproduction package

All six cases are complete: `packet`, `signed_packet`, `signed_packet_chain`, each
with fill +1/-1, all 16 ordered boundary states, and two independently computed
encodings. All 96 encoding pairs match. The primary encoding has **978,880,708
exact records**; both encodings contain 996,500,560,744 logical raw bytes.

The RTX PRO6000 Blackwell rerun took **686.923 seconds (11m27s)**, including
computation, CPU output checks, writing, fsync and full checksum readback.
All 192 raw/canonical hashes, record counts, byte counts and moments match the
original 781.956-second run. The original bulk was lost in a container reset;
this rerun regenerated it. Both results and their comparison are in `reference/`.
This is end-to-end time, not GPU-only. `gpu_source/` is the bound implementation;
`inputs/N004000/` holds the frozen graphs and parents.

Energy is E=-sum J_uv*s_u*s_v-sum h_i*s_i; magnetization M=sum s_i. Ordered ports
are [0,1,60,61]; bit i of b selects +1 when set, -1 otherwise. Counts are exact.

## Retained record verification

```sh
python3 reproduce/n4000/run.py verify-record
```

Authenticates 16 source files, bound code, all 192 rows, source/plan bindings,
configuration counts and agreement of both encodings. Reads receipts, not bulk.

## Reproduction package

Use the same Python 3.12 environment and public runtime as [N2000](../n2000/README.md).

```sh
python -m pip install -r reproduce/n4000/requirements.txt
python reproduce/n4000/run.py fetch-runtime --destination runs/n2000-runtime
python reproduce/n4000/run.py smoke \
  --runtime runs/n2000-runtime/runtime --work-dir runs/n4000
python reproduce/n4000/run.py verify-results --work-dir runs/n4000
```

Skip fetch-runtime if installed. Use a fresh work directory; allow 1 GiB disk.
No GPU or bulk download is required. Packet/+1 is recomputed for all 16 boundaries
in both encodings through a source-bound MATTER_SEARCH DomainSession. The measured
replay took **16.473 seconds**; all 32 canonical hashes, moments, counts and raw
binary hashes match GPU production. `VALIDATION.json` preserves the measurement.
The other five cases remain represented by the full retained record.

The N3000 replay engine is adapted to N4000 frozen inputs; `math_core.py` is
unchanged. Public runtime: SLC-GEN4-P1 / CE SLC-GEN4-CE-P1 / domain GEN3-R4.

## Compressed shards and 100 GiB batches

`DATA_MANIFEST.json` inventories Zstandard level 3 shards and whole-shard transfer
batches <=100 GiB (107,374,182,400 bytes). Every shard is decompressed on the producer
and checked against its original raw SHA256. **89 distinct raw contents preserve
all 192 logical rows.** Each shard's `logical_rows` lists every associated file,
boundary identity and canonical hash. Identical data are stored once; both independent
encoding calculation receipts remain. No boundary or encoding is discarded.

Compression is complete: **311,143,296,485 bytes (289.77 GiB)**.

| Batch | Unique shards | GiB |
|---|---:|---:|
| 1 | 24 | 96.3509 |
| 2 | 33 | 96.5052 |
| 3 | 32 | 96.9187 |

All N4000 workstation bulk downloads are **OWNER_HOLD**, including batch 1.
No public bulk URL is available yet. Data remain on owner-selected container disk;
no network-storage output copy is configured. Bulk files remain outside Git.

```sh
python reproduce/n4000/data.py /path/to/batch-001 \
  --manifest /path/to/batch-001/BATCH_MANIFEST.json --deep
```

Install zstd for deep verification. Add `--restore /path/to/raw` to restore files
and hardlinked aliases from `logical_rows`; the destination must support hardlinks.
Existing files are not overwritten. Without --deep, compressed SHA256/sizes are checked.

GPU records are headerless: signed int32 little-endian E, signed int32 little-endian M,
and unsigned **501-byte little-endian count: 509 bytes per record**. `data.records(path)`
streams exact Python integers. K_MAJOR/T_MAJOR raw order can differ; canonical hashes
agree. CPU replay includes a GEMB001 header, stripped for raw-hash comparison.
Either complete encoding supplies the full g(E,M,b).

Sean Brady is originator/conceptual director; OpenAI ChatGPT and Codex are AI research
collaborators. Code MIT; research data/results CC BY 4.0. Existing
[license scope](../../LICENSING.md) and [runtime grant](../../RUNTIME_LICENSE.md) apply.
