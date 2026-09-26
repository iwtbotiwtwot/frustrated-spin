# GEN4 frustrated-spin research

This new addition collects the exact spin atlas, solver development, learning
campaigns, packet-family extension, and the September 26, 2026 N300 courtroom
test. Sean Brady is the originator and conceptual director; OpenAI ChatGPT and
Codex are AI research collaborators and co-authors.

## Start here

| Record | Contents |
|---|---|
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

## Fully connected extension and consecutive continuation

The [dense-completion project](GEN4/frustrated_spin_dense_completion1/RESULTS.json)
constructs six fully connected N300 sources from the three existing families.
Each preserves its parent's couplings and fills absent pairs with either +1
or −1. Pair coverage, inherited couplings, and the collective-magnetization
energy identity are checked. **Their full density-of-states calculations have
not been run.** The proposed exact route extends packet tables to retain joint
correction energy, magnetization, and ordered ports.

Separately, the packet continuation launched on the cheaper pod with three
CPU workers. Its retained launch check confirms every N121–N259 in all three
families: **417 independently verified source cases**. This is a dated launch
snapshot, not a live progress feed. Sources, code, qualification, N121/N122
outputs, and checkpoint-recovery evidence are included. Later running results
remain on the pod until a subsequent export.

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
- The packet and N300 campaigns did not execute N121–144. The N300 sources
  were constructed directly from the packet grammar.

This is a research addition inside `frustrated-spin/`. Its isolated GEN4
runtime snapshot does not change the repository's portable R3 installation.

## Verify the downloaded record

From this directory:

```sh
python3 verify_publication.py
```

This checks the public SHA-256 manifest, the original N300 frozen manifest and
precommit witness binding, event-chain continuity, retained exact comparisons,
and the source counts. It performs no new spin calculation or timing trial.
