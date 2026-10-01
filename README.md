# GEN4 frustrated-spin research

**Continuous exact g(E,M,b) coverage now includes every N1–1800:**
**10,800 structured graph/fill cases** and **118,387,509,614 primary
joint-support entries evaluated**, with both exact encodings agreeing throughout.
The [new results and methodology](reproduce/continuous-n1800/README.md) include
per-size/per-case tables and [original compact-data inventory](reproduce/continuous-n1800/DATA_MANIFEST.json).
Compact records retain source identities, counts, moments, hashes and responses;
expanded coefficient tables are retained separately at selected milestones.
The [8.34 GB data release](https://github.com/iwtbotiwtwot/frustrated-spin/releases/tag/continuous-n1800-20261001)
is public: 18 range archives and the bound solver/source package, all SHA-256
verified. Five example records are also included in Git.

**Exact g(E,M,b) is complete at N2000, N3000, N4000 and N5000**, each covering six graph cases, all 16 ordered boundary states per case, and two independent encodings: **192 rows and 96 matching encoding pairs per size**.

The reproduction packages include frozen inputs, production verification receipts, bound solver code, exact CPU recomputation and checksum-verified archive manifests. Each N3000–N5000 package recomputes the complete packet/+1 case on CPU—32 rows across both encodings—and checks it against the GPU results.

| Reproduction package | Primary exact records | Verified compressed archive | CPU packet/+1 reproduction |
|---|---:|---:|---:|
| [N5000](reproduce/n5000/README.md) | 1,530,259,992 | 609.67 GB; 6 batches | 37.769 seconds |
| [N4000](reproduce/n4000/README.md) | 978,880,708 | 311.14 GB; 3 batches | 16.473 seconds |
| [N3000](reproduce/n3000/README.md) | 550,074,346 | 236.96 GB; 3 batches | 10.486 seconds |
| [N2000](reproduce/n2000/README.md) | 244,104,392 | 37.4 GB | See package validation |

N3000–N5000 transfer batches contain whole shards and are capped at 100 GiB. The package READMEs describe reproduction scope, data formats and access.

[Public N2000 data folder](https://drive.google.com/drive/folders/1F8wvIRqL3pdB34db-llz0YjnIbFbRg9Y) · [Data manifest and hosting status](reproduce/n2000/DATA_MANIFEST.json) · [Fresh reproduction checks](reproduce/n2000/VALIDATION.json)

**Fully constructed graphs for every spin count from N=1 through N=1408,
including every integer in between, with no gaps.** The catalog contains
**six fully connected signed graph variants at each N: 8,448 graphs in total**.
Each N1408 graph explicitly stores all **990,528 pair interactions**.

The six variants come from packet, signed packet and signed packet chain sources,
each completed with +1 or -1 couplings on previously absent pairs. See the
[construction record and graph locations](GEN4/frustrated_spin_dense_extension1/README.md)
for coverage and verification. The full catalog is retained in verified custody;
this checkout includes selected sources and provenance. Exact dense-solution
coverage is reported separately below.

This standalone repository collects the exact spin atlas, solver development, learning
campaigns, packet-family extension, the September 26, 2026 N300 courtroom
test, and the subsequent joint-response capability and phase experiments. Sean Brady is the originator and conceptual director; OpenAI ChatGPT and
Codex are AI research collaborators and co-authors.

This is the standalone copy of the [frustrated-spin publication in SLC-GEN3-R3](https://github.com/SAMresearchproject/SLC-GEN3-R3/tree/74dbef016c96a58593fed362713c111a55f85071/frustrated-spin).
Its three publication commits are preserved as directory-filtered history.
[Copy provenance](provenance/STANDALONE_COPY.json) binds the original and extracted commits.
Software is **[MIT licensed](LICENSE)**; research data, reports and figures are **[CC BY 4.0](LICENSE-DATA)**. [License scope](LICENSING.md) includes the frozen runtime and public N2000 dataset. [Attribution](NOTICE.md), [citation/DOI](CITATION.cff), and the owner [stewardship commitment](STEWARDSHIP.md) are retained.

## Start here

| Record | Contents |
|---|---|
| [Continuous N1–1800](reproduce/continuous-n1800/README.md) | 10,800 cases; detailed equations, original compact records, source code and checksums |
| [N5000 reproduction package](reproduce/n5000/README.md) | Complete 192-row result, exact CPU reproduction, 89 verified shards in six batches |
| [N4000 reproduction package](reproduce/n4000/README.md) | Complete 192-row result, exact CPU reproduction, 89 verified shards in three batches |
| [N3000 reproduction package](reproduce/n3000/README.md) | Six completed cases, 192 GPU rows, exact CPU replay, frozen sources and shard inventory |
| [Reproduce N2000 exact g(E,M,b)](reproduce/n2000/README.md) | Six completed cases, 96 boundaries, 192 independent encoding receipts, exact binary hashes, public data and native recomputation |
| [Earlier joint capability and results](GEN4/spin_joint_install1/RESULT.md) | Installed shared packet/joint solver; N1408 construction coverage, 54 dense magnetization cases and 24 joint datasets |
| [Phase response, step 1](GEN4/vol_ii_joint_response1/REPORT.md) | Equal zero-field spectra with different contact-conditioned alignment responses |
| [Collective response, step 2](GEN4/vol_ii_joint_response2/REPORT.md) | Exact coupling thresholds and full-spectrum reflection around h=1 |
| [Complete graph catalog: every N1–N1408](GEN4/frustrated_spin_dense_extension1/README.md) | No gaps: six fully constructed variants at every spin count, 8,448 graphs total; construction checks and custody locations |
| [Fully connected N300 sources](GEN4/frustrated_spin_dense_completion1/README.md) | Six complete graphs with 44,850 interactions each; preserved parent couplings and an exact collective-magnetization representation |
| [Consecutive packet continuation](GEN4/frustrated_spin_packet_continuation1/README.md) | Resumable CPU campaign starting at N121, independent exact verification, and retained launch/recovery evidence |
| [N300 report](GEN4/frustrated_spin_n300_courtroom1/REPORT.md) | Prospective timing prediction, sealed protocol, independent exact comparisons, six wrong controls, and every timing sample |
| [Packet-family idea](GEN4/frustrated_spin_packet_catalog1/IDEA.md) | Source grammar, extension, signed and connected constructions, and the reusable computation |
| [Packet-family results](GEN4/frustrated_spin_packet_catalog1/REPORT.md) | All N1–120 in three explicit families: 360 sources and 3,240 timed exact calculations |
| [Runtime scaling](GEN4/frustrated_spin_packet_catalog1/RUNTIME_SCALING.md) | Size, polynomial composition, ordered-port readout, and timing changes |
| [Canonical atlas](GEN4/frustrated_spin_learning1/CANONICAL_ATLAS.csv) | Original completed contiguous N1–120 catalog, with [exact source/result objects](GEN4/frustrated_spin_learning1/canonical/) |
| [Earlier campaign synthesis](GEN4/frustrated_spin_learning1/reports/pre_blind_runs_20260926/REPORT.md) | Detailed history of the research runs before the blind restart |
| [Cooperative-14 campaign](GEN4/frustrated_spin_pod14_learning1/OVERNIGHT_SUMMARY.md) | Qualified production topology, CPU/GPU learning, returned questions and results |
| [N100/N105 hardware placement](GEN4/frustrated_spin_pod14_learning1/N100_N105_HARDWARE_PLACEMENT.md) | Separate CPU and cooperative GPU cost observations |
| [N96 plan/backend study](GEN4/frustrated_spin_pod14_learning1/N96_PLAN_BACKEND.md) | Expanded versus older plans on the cooperative-14 backend |
| [Publication and reproduction](PUBLICATION.md) | Export boundary, verification, archive mapping, and runtime setup |

## Latest continuation, magnetization and joint response

Exact joint computation now covers **every N1–1800**, six source/fill cases per
size. The [continuous package](reproduce/continuous-n1800/README.md) publishes
original compact scientific records, bound source/solver code and verification.
The earlier explicitly serialized graph catalog through N1408 retains its own
construction/custody record. The new production additionally binds complete-graph
identities at every solved size. Isolated full-output milestones extend to N5000.

The [shared capability](GEN4/spin_joint_install1/GUIDE.md) extends existing
SLC/CE/GEN3/GEN4 operations and has executed SB/A3D41 adoption. Local installation
qualification passes369checks; scoped GEN4 qualification passes381checks including
CUDA comparisons. It adds source-structure selection, exact packet composition,
joint readout and reusable field/pair/boundary transformations.

Two subsequent Volume II experiments use that installed capability. Step1 gives
six exact contact/alignment response curves. Step2 gives coupling thresholds
-1 and17/3 and a source-specific full-spectrum identity relating fields h and2-h.
Their code, complete numerical responses, independent checks and source identity
are included. No follow-up is running.

This supplement includes all three complete N1408 packet answers, compact
production receipts, generated extension graphs, executable source and complete
small-case response evidence. The large earlier packet catalog and older bulk joint
shards remain in verified workstation/T500 custody; **they are not all embedded
in this Git checkout**. N2000 primary shards are distributed through the linked
Google Drive folder, with its exact upload state recorded in DATA_MANIFEST.json. Their inventory hashes and export dispositions are in
[the latest sync receipt](provenance/SYNC_JOINT_20260926.json) and the original
[custody manifest](GEN4/spin_joint_install1/custody/FINAL_INVENTORY.json).
The upgraded runtime is a separately downloadable
[release asset](provenance/RELEASE_JOINT_20260926.json).

The older continuation publication was a launch-time N121–N259 snapshot. Its
original receipt remains at `provenance/SYNC_CONTINUATION_DENSE_20260926.json`.
The N300 generated-only record describes that earlier stage; later solved cases
are separately identified by source hashes in the new coverage inventory.

## Precommitted packet-family N300 result

The precommitted primary endpoint was a **warm exact-solve median below 25 ms**,
with 31 scored trials for each of three N300 sources. The workstation was an
Intel Core i9-12900HK, using the serial CPU route. All three predictions passed.

| N300 source | Primary median | Individual trials below 25 ms |
|---|---:|---:|
| Packet | 16.993 ms | 28/31 |
| Signed packet | 17.123 ms | 28/31 |
| Signed connected packet chain | 20.423 ms | 28/31 |

All three first target solves were below 25 ms. All full-spectrum comparisons
against independent variable elimination passed, and all six wrong controls
were detected. Nine of the 93 primary individual timings exceeded 25 ms; all
remain in the [timing table](GEN4/frustrated_spin_n300_courtroom1/TIMINGS.csv).
The [protocol](GEN4/frustrated_spin_n300_courtroom1/PROTOCOL.md) defines the
timing boundary and distinguishes the primary measurement from cold runs and
the later boundary refinement.

The preceding packet-family catalog ran on the pod CPU. Every N1–120 case in
each of the three families had a three-trial warm median below 10 ms. These
are separately identified sources alongside the original canonical atlas.

## Retained scientific and execution identities

- The original canonical N1–120 atlas is complete and remains unchanged.
- Historical packet N100/N105 and N96-derived frustrated N120 retain their
  distinct source lineages. The surviving records place N100 before N105 on
  August 2, 2026; a formal preregistered N100 → N105 prediction has not been
  located. Retrospective transfer analysis is labeled accordingly.
- N108 was absent from the historical progression before the N120 launch.
  The causal claim that it was skipped because N105 existed is not established
  by the located records.
- The cooperative-14 campaign's final pod snapshot is **STOPPED**, with
  **73 completed questions and 249 observations**. Historical workstation
  snapshots are retained separately under `provenance/workstation_pod14_snapshot/`.
- CPU, single-MIG, and cooperative-14 measurements retain their backend,
  topology, plan, cache state, and timing scope. No new model merges these
  measurements in this publication.
- The initial packet-catalog and N300 campaigns did not execute N121–144;
  the later authorized continuation did. The N300 sources
  were constructed directly from the packet grammar.

This repository contains the spin research and evidence. Its isolated GEN4
runtime is supplied as a release asset; the parent repository's portable R3
installation remains in SLC-GEN3-R3.

## N4000 exact GPU result and reproduction package

[N4000 reproduction](reproduce/n4000/README.md) adds all 192 exact rows alongside
N2000 and N3000. The PRO6000 rerun finished in 11m27s; the 32-row packet/+1 CPU
replay took 16.473s with identical raw/canonical hashes. The archive preserves
all logical rows through 89 unique contents and 100 GiB batches. N4000 downloads
are held pending owner clearance.

## N5000 exact GPU result and reproduction package

[N5000 reproduction](reproduce/n5000/README.md) adds all 192 exact rows and
96 matching encoding pairs. PRO6000 production completed in 47m04s;
the 32-row packet/+1 CPU replay took 37.769s with identical raw/canonical
hashes. Lossless shards preserve all original rows in batches up to 100 GiB.
Bulk downloads remain held while data move to the owner's storage pod.

## Verify the downloaded record

From this directory:

```sh
python3 verify_publication.py
python3 verify_latest.py
python3 reproduce/n2000/run.py verify-record
```

This checks the public SHA-256 manifest, the original N300 frozen manifest and
precommit witness binding, event-chain continuity, retained exact comparisons,
and the source counts. It performs no new spin calculation or timing trial.
