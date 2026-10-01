# Continuous exact joint-density coverage: N1–1800

**Every integer N from 1 through 1800 is complete:** 10,800 labeled
structured graph/fill cases, 168,420 retained-boundary
rows per encoding, and **118,387,509,614 primary joint-support
entries evaluated** across the range. Two exact encodings agree for every case.
Support entries count occupied (E,M,b) bins, not individual spin configurations.

[Detailed results](RESULTS.md) · [Method and equations](METHODOLOGY.md) ·
[Download data](https://github.com/iwtbotiwtwot/frustrated-spin/releases/tag/continuous-n1800-20261001) ·
[Per-size index](INDEX.json) · [10,800-case CSV](CASES.csv) · [Literature context](LITERATURE.md)

This continuous campaign complements the separately published
[N2000](../n2000/README.md), [N3000](../n3000/README.md),
[N4000](../n4000/README.md) and [N5000](../n5000/README.md) milestones.
N1800 is the continuous-coverage endpoint, not the largest isolated solved N.

## Download and inspect data

**Hosting status: PUBLIC.** All 19 assets (8.34 GB) are available without
sign-in. Their byte counts and SHA-256 digests match the verified local assets;
an anonymous download of the N1–100 archive also passed its checksum.
The five example records, per-size index, case CSV, source code and reports
are included in the repository. DATA_MANIFEST.json records the public status.

The release has 18 archives covering 100 sizes each and one bound solver/source archive.
Each range archive expands into records/Nxxxxxx/RECORD.json.gz and RECEIPT.json.
All original compact record and receipt bytes are preserved. SHA-256 and byte
counts are in [DATA_MANIFEST.json](DATA_MANIFEST.json). Bulk assets are separate
from Git history. Examples at N1,100,1000,1408,1800 are included in this checkout.

```sh
python3 reproduce/continuous-n1800/verify.py
# Download selected assets from the linked release, then extract them:
tar -xf spin-joint-N1701-N1800.tar
python3 - <<'READ'
import gzip, json
r = json.load(gzip.open('records/N001800/RECORD.json.gz', 'rt'))
for c in r['cases']:
    print(c['family'], c['fill'], c['joint_support_size'], c['canonical_sha256'])
READ
# After downloading every asset:
python3 reproduce/continuous-n1800/verify.py --assets /path/to/downloads
# After extracting all 18record archives to one directory:
python3 reproduce/continuous-n1800/verify.py --records /path/to/records
```

The verifier uses Python 3.11+ standard library and performs read-only evidence
checks. It does not launch GPU work or imply a fresh recomputation of all sizes.

## What is retained

The compact records contain exact support/count/moment checks, both encodings'
canonical hashes, source and complete-graph identities, regeneration plans,
thermal intervals and boundary-response summaries, code identities, timing and
memory scopes. Their compressed records total **8,279,670,464 bytes**.
They are sufficient to inspect the retained results and identify a regenerated
table. They do not contain every expanded (E,M,count) coefficient.

Selected full-output milestones in this campaign: 1, 2, 3, 4, 5, 6, 7, 8, 12, 20, 50, 75, 100, 120, 200, 300, 400, 500, 750, 900, 1000, 1200, 1408.
Those expanded tables have separate custody and are not in these compact assets.
The isolated milestone packages retain their own data links and manifests.

## Recompute a selected source

The solver archive preserves the five original production implementation trees
and source catalogs. Its final spin_joint_2000_1 tree covers N1409–2000;
execution recorded by this release ends at1800. CONFIG's upper admission bound
is not a completion claim. Python 3.12/little-endian, python-flint, NumPy, Cython
and the recorded CUDA environment are required for that original implementation.
Rebuild fast_cpu from setup_fast.py when changing Python ABI; preserve the original
BUILD_ID and identify the rebuilt implementation separately. The unchanged
production runner checks the original build's files before execution.

For an already tested portable native CPU reproduction, use the commands in
[N2000](../n2000/README.md) and the other isolated milestone packages. The new
continuous package publishes original bound production code and evidence;
it does not claim a new portable all 1800-size replay qualification.

Research production used MATTER_SEARCH / GEN3-R4, SLC-GEN3-R4 and
SLC-GEN3-CEV1-R4. Independent publication checks are identified in VERIFY.json.
Software: MIT. Data, reports and figures: CC BY 4.0, under repository licensing.
Sean Brady: originator/conceptual director. OpenAI ChatGPT and Codex: AI research
collaborators and co-authors.
