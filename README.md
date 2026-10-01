# Frustrated-spin: graphs to N20000, exact joint densities to N5000

**Fully constructed graphs at every N1–20000. Continuous exact g(E,M,b) at
every N1–1800. Larger isolated exact milestones at N2000, N3000, N4000 and N5000.**

This repository publishes structured Ising graph sources, exact joint-density
results, solver implementations, reproducible checks and research provenance.
[Current status](CURRENT_STATUS.md) · [Machine-readable coverage](CURRENT_STATUS.json) ·
[Data and reproduction guide](PUBLICATION.md) · [Citation](CITATION.cff)

| Completed work | Coverage | Results and evidence |
|---|---|---|
| Fully constructed complete signed graphs | Every N1–20000; six variants per size; **120,000 graph sources** | [Construction record](provenance/graph-construction-n20000/README.md) |
| Continuous exact energy–magnetization–boundary density | Every N1–1800; **10,800 cases**; **118,387,509,614 primary joint-support entries evaluated** | [Results, equations and methodology](reproduce/continuous-n1800/README.md) |
| Larger exact joint-density milestones | N2000, N3000, N4000, N5000; six cases and 192 encoding rows at each size | [Milestone packages](#exact-milestone-packages) |

**Due to their size, the large expanded datasets are hosted on Google Drive,
not stored in this Git repository.** The repository contains code, methodology,
results, manifests and selected examples. The compact N1–1800 dataset is supplied
separately through the linked GitHub release.

Each N20000 graph explicitly encodes **199,990,000 pair interactions**. The six
labeled cases are packet, signed_packet and signed_packet_chain, each completed
with +1 or -1 couplings on previously absent pairs. Existing couplings and fields
are preserved. Graph construction and exact density computation have the separate
coverage shown above; N20000 is the construction endpoint.

## Public continuous data

[Download the N1–1800 release](https://github.com/iwtbotiwtwot/frustrated-spin/releases/tag/continuous-n1800-20261001):
**19 assets, 8,340,788,456 bytes (8.34 GB)**. Eighteen archives cover 100 sizes each;
one contains the bound solver/source implementations. All asset SHA-256 digests
match, and an anonymous sample download was checked.

These are original compact scientific records and receipts. They retain source
identities, exact counts and moments, both encodings' canonical hashes, response
summaries and regeneration plans. Expanded coefficients were computed and checked
in RAM; full tables are retained separately at selected milestones. The release
does not contain every expanded coefficient from the continuous campaign.

[Per-size index](reproduce/continuous-n1800/INDEX.json) ·
[10,800-case table](reproduce/continuous-n1800/CASES.csv) ·
[Checksums](reproduce/continuous-n1800/DATA_MANIFEST.json) ·
[Methodology and derivations](reproduce/continuous-n1800/METHODOLOGY.md)

## Exact milestone packages

All four milestones below have **completed exact spectra**, each with six cases,
16 ordered boundary states per case, and two encodings: 192 rows and 96 matching
encoding pairs. Each package includes frozen inputs, original production receipts,
solver code and exact CPU reproduction. The N3000–N5000 CPU replays recompute the
complete packet/+1 case, all 32 encoding rows, against the production hashes.

| Package | Primary joint-support entries | Compressed archive | CPU packet/+1 replay |
|---|---:|---:|---:|
| [N5000](reproduce/n5000/README.md) | 1,530,259,992 | 609.67 GB; 6 batches | 37.769 s |
| [N4000](reproduce/n4000/README.md) | 978,880,708 | 311.14 GB; 3 batches | 16.473 s |
| [N3000](reproduce/n3000/README.md) | 550,074,346 | 236.96 GB; 3 batches | 10.486 s |
| [N2000](reproduce/n2000/README.md) | 244,104,392 | 37.40 GB | See package validation |

N2000's original report predates these completed N3000–N5000 spectra. Its earlier
N3000 partial checkpoint and N4000/N5000 graph-only statuses are superseded by
the completed production receipts in these packages. The N1408 catalog is an
earlier milestone, not the current construction or continuous-density limit.

Data folders: [N4000](https://drive.google.com/drive/folders/1WzwxQ3YcRh81BLsEa_4AdjikM2YryBEu) ·
[N5000](https://drive.google.com/drive/folders/1nM20zqOsxTDVEgw_Go3GnsEX2Srj4kfu) ·
[N3000](https://drive.google.com/drive/folders/18y6ZEJGw6IhqAN-jJCXVvueTAzjwcypi) ·
[N2000](https://drive.google.com/drive/folders/1F8wvIRqL3pdB34db-llz0YjnIbFbRg9Y).
[Access and custody status](CURRENT_STATUS.md#storage-and-access) distinguishes
folder links, verified holdings and confirmed public downloads. N4000 and N5000 folder links were supplied by the owner on October 1, 2026.

## Completed spectra and storage accounting

The **approximately 3 TiB figure is 3.055 TiB of completed logical raw N3000–N5000
spectra across both encodings**. It is not a projection, unique physical disk use,
or compressed download volume.

| Size | Logical raw bytes, both encodings | Archived raw shard bytes | Compressed archive bytes |
|---|---:|---:|---:|
| N3000 | 422,457,097,728 | 422,457,097,728 | 236,963,585,976 |
| N4000 | 996,500,560,744 | 536,744,413,701 | 311,143,296,485 |
| N5000 | 1,940,369,669,856 | 1,045,145,366,546 | 609,671,270,157 |
| **Total** | **3,359,327,328,328 (3.055 TiB)** | **2,004,346,877,975 (1.823 TiB)** | **1,157,778,152,618 (1.053 TiB)** |

Logical output includes duplicated encoding/boundary content. Archived raw counts
follow each archive's deduplication policy. These totals exclude N2000, the
continuous campaign, graph-construction data and runtime/metadata.
[Exact accounting and receipt bindings](provenance/SPECTRA_STORAGE_ACCOUNTING.json).

The continuous campaign's **42,030,624,816,236-byte hypothetical headerless output**
is a projection of storage for both expanded encodings at every N1–1800. Most
expanded tables were released after checks; that figure is not retained data.
Its public compact-data/source release is the separate 8.34 GB package above.

## Verify and reproduce

```sh
python3 reproduce/continuous-n1800/verify.py
python3 reproduce/n2000/run.py verify-record
python3 reproduce/n3000/run.py verify-record
python3 reproduce/n4000/run.py verify-record
python3 reproduce/n5000/run.py verify-record
```

These commands check retained evidence without launching new production. For
actual CPU recomputation, use each milestone package's environment and smoke
commands. Its exact size-specific title and runtime requirements remain relevant.
[Publication guide](PUBLICATION.md) explains current and historical verification.

## Earlier research and provenance

[Historical campaign index](GEN4/README.md) links packet-family timing experiments,
the N300 precommitted test, solver development, shared capability installation and
Volume II response experiments. Their original reports, titles, runtime bindings
and launch states describe their own dates. They remain preserved evidence;
[CURRENT_STATUS.md](CURRENT_STATUS.md) is the current whole-repository overview.

The original [N300 timing report](GEN4/frustrated_spin_n300_courtroom1/REPORT.md),
[shared capability result](GEN4/spin_joint_install1/RESULT.md), and
[boundary-response experiments](GEN4/vol_ii_joint_response2/REPORT.md) retain their
scientific scopes. [Literature context](reproduce/continuous-n1800/LITERATURE.md)
explains comparisons by observable, graph family, arithmetic and data retention.
The repository's original extraction from SLC-GEN3-R3 is recorded in
[copy provenance](provenance/STANDALONE_COPY.json); this repository has since advanced.

Sean Brady is the originator and conceptual director; OpenAI ChatGPT and Codex
are AI research collaborators and co-authors. Software: **[MIT](LICENSE)**.
Research data, reports and figures: **[CC BY 4.0](LICENSE-DATA)**.
[License scope](LICENSING.md) · [Runtime licensing](RUNTIME_LICENSE.md) ·
[Attribution](NOTICE.md) · [Stewardship](STEWARDSHIP.md).
