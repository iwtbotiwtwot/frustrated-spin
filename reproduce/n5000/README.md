# N5000 exact g(E,M,b) and cheap replay

All six cases are complete: packet, signed_packet and signed_packet_chain,
each with fill +1/-1, all 16 ordered boundary states and two independent
encodings. All 192 rows and 96 encoding pairs passed.

The RTX PRO6000 Blackwell production took **2824.215 seconds (47m04s)**,
including GPU computation, CPU output checks, writing, fsync and checksum
readback. Two qualified pilot groups were reused; 92 new polynomial groups
were computed. Both encodings occupy 1,940,369,669,856 logical raw bytes;
hardlinked production output occupies 1,045,161,207,036 unique bytes.
This is end-to-end production time, not GPU-only time.

Energy is E=-sum J_uv*s_u*s_v-sum h_i*s_i; magnetization M=sum s_i.
Ordered ports are [0,1,60,61]; bit i of b selects +1 when set, -1 otherwise.
Counts are exact. Each fixed boundary accounts for 2^4996 configurations.

## Verify retained results

```sh
python3 reproduce/n5000/run.py verify-record
```

Checks frozen input hashes, all 192 production receipts, code/source/plan
bindings, configuration counts, independent-encoding agreement and the archive
mapping. It reads receipts without requiring the bulk dataset.

## Cheap CPU replay

Use the Python 3.12 environment and runtime described in [N2000](../n2000/README.md).

```sh
python -m pip install -r reproduce/n5000/requirements.txt
python reproduce/n5000/run.py fetch-runtime --destination runs/n2000-runtime
python reproduce/n5000/run.py smoke \
  --runtime runs/n2000-runtime/runtime --work-dir runs/n5000
python reproduce/n5000/run.py verify-results --work-dir runs/n5000
```

Use a fresh work directory with 1 GiB free. No GPU or bulk download is needed.
The replay recomputes packet/+1 for all 16 boundaries in both encodings using
a source-bound MATTER_SEARCH DomainSession. **37.769 seconds**, 32 matching
canonical/raw hashes, moments and record counts. Measurement: VALIDATION.json.
The five other cases are covered by the retained production record.

The engine admits the explicit frozen N5000 pair source through the installed
catalog normalizer; the general runtime's 4096-variable API limit is unchanged.
The mathematical core is unchanged from N4000. Public runtime: SLC-GEN4-P1 /
CE SLC-GEN4-CE-P1 / domain GEN3-R4; the research project's selector is unchanged.

All 16 frozen input files were restored byte-for-byte from retained construction
receipts and source grammar after their former backup path became unavailable.
Every restored SHA256 matches the source hashes bound to GPU production.

## Bulk format and lossless archive

Compression complete: **609671270157 bytes**, 89 unique shards.

| Batch | Shards | GiB |
|---|---:|---:|
| 1 | 15 | 97.9732 |
| 2 | 9 | 90.4901 |
| 3 | 16 | 98.6761 |
| 4 | 17 | 90.7681 |
| 5 | 9 | 92.6573 |
| 6 | 23 | 97.2357 |


DATA_MANIFEST.json lists verified Zstandard level-3 shards and whole-shard
batches capped at 100 GiB. Identical raw contents are stored once; logical_rows
preserves every original filename and independent encoding receipt. Each shard
is decompressed and matched to the original raw SHA256 on the producer.

Records contain signed little-endian int32 E and M, then an unsigned **626-byte
little-endian count: 634 bytes per record**. data.records(path) streams Python
integers. CPU replay files add a GEMB001 header, which is stripped before
comparison with GPU raw hashes.

```sh
python reproduce/n5000/data.py /path/to/batch-001 \
  --manifest /path/to/batch-001/BATCH_MANIFEST.json --deep
```

Add --restore /path/to/raw to reconstruct the raw files and hardlinked aliases.
Install zstd for deep verification/restoration. Existing raw files are preserved.

Workstation bulk downloads remain held. Archive custody is being moved to the
owner's storage pod; source-container retirement requires complete destination
verification. No public bulk URL is available yet. Bulk files stay outside Git.

Sean Brady is originator/conceptual director; OpenAI ChatGPT and Codex are AI
research collaborators. Code MIT; research data/results CC BY 4.0. Existing
[license scope](../../LICENSING.md) and [runtime grant](../../RUNTIME_LICENSE.md) apply.
