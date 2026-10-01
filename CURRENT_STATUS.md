# Current coverage and data status — October 1, 2026

| Category | Completed coverage | Evidence |
|---|---|---|
| Fully constructed complete signed graphs | Every N1–20000; six variants per N;120,000 sources | [Construction](provenance/graph-construction-n20000/README.md) |
| Continuous exact g(E,M,b) | Every N1–1800;10,800 cases | [Continuous package](reproduce/continuous-n1800/README.md) |
| Larger isolated exact g(E,M,b) | N2000, N3000, N4000, N5000; six cases and 192 encoding rows at each | [Milestone packages](README.md#exact-milestone-packages) |
| Public continuous release | 19 assets;8,340,788,456bytes; original compact records and bound solvers | [Public release](https://github.com/iwtbotiwtwot/frustrated-spin/releases/tag/continuous-n1800-20261001) |

## What supersedes what

- The original N2000-era N3000 partial checkpoint is superseded by the completed
  September 29 N3000 run. N4000/N5000 graph-only states are superseded by their
  completed joint-density production receipts.
- N1408 is an earlier construction and solver milestone. Graph construction
  reaches N20000; the continuous joint-density computation reaches N1800.
- N4000's older download hold is superseded by verified Drive custody of all 89 shards.
- N5000's storage-pod migration is complete: all 89 shards are in verified external
  custody, batches 001–002 on Drive and 003–006 on T500.
- The continuous release's draft/approval-pending state is superseded by its
  public release receipt. The original upload receipt remains a dated event.

## Storage and access

**The large expanded datasets are hosted on Google Drive because of their size,
not in this Git repository.** The public compact N1–1800 release is hosted
separately on GitHub Releases. Code, reports, indices and selected examples are in Git.

Completed N3000–N5000 outputs total 3.055 TiB logically across both encodings;
their archived raw shards total 1.823 TiB and compressed archives total 1.053 TiB.
[Exact accounting](provenance/SPECTRA_STORAGE_ACCOUNTING.json). Logical output
includes duplicated content and does not describe physical disk use.
The continuous campaign's 42.031 TB hypothetical headerless expanded output is a
storage projection, not saved data. Its public 8.34 GB package contains compact
records, receipts and solver/source code.

| Dataset | Latest documented access/custody |
|---|---|
| Continuous N1–1800 compact data | Public GitHub release; all 19 asset digests verified; anonymous sample download checked |
| N2000 expanded density | Public Drive distribution; see its [manifest](reproduce/n2000/DATA_MANIFEST.json) |
| N3000 expanded density | Latest retained publication receipts: all 3 download batches complete; Drive 001/002 uploaded and filename/size checked; cloud payload hashes not independently checked; 003 upload not confirmed |
| N4000 expanded density | [Owner-supplied Drive folder](https://drive.google.com/drive/folders/1WzwxQ3YcRh81BLsEa_4AdjikM2YryBEu); all 89 compressed shards have verified Drive custody |
| N5000 expanded density |[Owner-supplied Drive folder](https://drive.google.com/drive/folders/1nM20zqOsxTDVEgw_Go3GnsEX2Srj4kfu);89 shards have prior verified Drive/T500 custody |
| N1–20000 constructed graph corpus | Research custody; compact N20000 endpoint evidence is in Git, not the full bulk corpus |

## Reading old records

[GEN4](GEN4/README.md) and SAM_HISTORY contain preserved campaigns and results.
Titles such as N1408 or N2000 refer to the scope of those files, not today's
maximum. Original README/report bytes bound into provenance/PUBLIC_MANIFEST.json
remain unchanged; additive CURRENT_CONTEXT.md files connect campaign directories
to this status. Snapshot prose about running jobs, upload holds, runtime versions
or pending work describes the original execution date. Reproduction packages
retain their own exact N and runtime requirements.

Machine-readable current scope: [CURRENT_STATUS.json](CURRENT_STATUS.json).
