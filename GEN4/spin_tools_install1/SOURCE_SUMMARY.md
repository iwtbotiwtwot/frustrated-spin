# Completed spin source inventory

The additive source package contains **100 named source-family records across
99 default sizes: every N1–N96, N100, N105 and N120**. All 97 preceding catalog
references remain unchanged. Three new retained objects supply N100, N105 and
the separately named historical N120 ring. The portable export contains 100
registry roots and 102 objects including their dependencies.

| Records | Source family | Retained exact outputs |
|---|---|---|
| N1–N96 | `N96_INDUCED_TRANSITION_LADDER_V1` | Existing scalar DOS, open polynomial operators and complete requested conditional rows; existing source, plan, learning and transition references preserved |
| N100 | `N100_P2_PACKET_PLUS_DEPTH_V1` | 260 couplings; scalar DOS and 16 conditional rows; ground −260 with 256 states; 177 occupied bins |
| N105 | `N105_P9G0_HISTORICAL_PACKET_RESTORATION_V1` | 275 couplings; scalar DOS and 16 conditional rows; ground −275 with 256 states |
| Default N120 | `N120_FIVE_REGULAR_DEGREE_PRESERVING_N96_EXTENSION_V1` | Current connected five-regular frustrated source, 300 couplings; scalar DOS and 16 conditional rows; ground −434 with 8 states; 435 bins |
| Named historical N120 | `SLCX028_N120_REPEATED_MOTIF_RING_V1` | Ten repeated 12-vertex cells, 300 couplings, 20 cross-cell edges; archived scalar DOS; ground −430 with 2 states; 421 bins |

The two N120 sources have the same vertex and edge counts but different graphs,
source identities and exact spectra. N-only selection continues to return the
current frontier. The historical ring remains independently selectable by its
family or canonical graph hash. Its archived 16 transfer states are not exposed
as full-source conditional rows: the release used here contains scalar DOS,
and the registry explicitly marks its conditional rows unavailable.

## Original source custody

- **Existing N1–N96 and current N120:** the installed
  [catalog](../../CURRENT_REVISION/engines/SLC/gen3/spin_data/CATALOG.json)
  and its content-addressed mathematical objects. The
  [focused installation result](../frustrated_spin_focused_install1/RESULT.md)
  records the preceding 97-entry installation; the
  [frontier result](../frustrated_spin_n120_frontier1/RESULT.md) records the
  completed new N120 source and exact execution.
- **N100:** [source instance](../../CURRENT_REVISION/domains/ATOM3D/source/N100_INSTANCE.json)
  and [complete reference tensor](../../CURRENT_REVISION/domains/ATOM3D/source/N100_REFERENCE.json).
  This is the completed component-conditional packet-plus-depth result,
  with component sizes 15,15,15,15,15,10,10,5 and 165,920 retained assignment-work count.
- **N105:** [restored instance](../../SLC/SAM_LANGUAGE/SAM_LANGUAGE_CONTACT_NATIVE_SUCCESSOR_DESIGN/SLC_N105_P9G0_RESTORATION_TIMING_DIAGNOSTIC_V1/N105_P9G0_RESTORED_INSTANCE.json)
  and [completed result](../../SLC/SAM_LANGUAGE/SAM_LANGUAGE_CONTACT_NATIVE_SUCCESSOR_DESIGN/SLC_N105_P9G0_RESTORATION_TIMING_DIAGNOSTIC_V1/N105_P9G0_RESTORATION_RESULT.json).
  The five historical `p=9,g=0` role rows extend N100 to components
  15,15,15,15,15,10,10,10; the archived assignment-work count is 166,912.
  Historical packet typing remains distinct from present W8/W9 site-phase semantics.
- **Historical N120 ring:** [frozen motif vault](../../SLC/18_SAM_NATIVE_QC/SLCX028_EXACT_N96_N120_BOUNDARY_TRANSFER_RING_SCALING/SLCX028_MOTIF_FAMILY_VAULT.json),
  `instances` row `N=120`, and [exact ring DOS](../../SLC/18_SAM_NATIVE_QC/SLCX028A_IMPLEMENTATION_CORRECTED_N96_N120_BOUNDARY_TRANSFER_RING_SCALING/release/SLCX028A_N120_FINAL_SCALING_HOLDOUT_DOS.json).
  Its completed corrected campaign dates to July 21, 2026; it is not a new frontier execution.

## Normalized representation

Every source receives the installed `validate_source` graph representation:
integer fields, integer `[u,v,J]` edges, stable parent vertex labels, an explicit
family and canonical `source_sha256`. Archived semantic hashes remain separate
from these normalized graph hashes. Original typed source instances and file
SHA256 custody remain inside the new retained records.

N100/N105 both use ports `[0,1,60,61]`, ordered as plus, minus, anti_plus,
anti_minus. Their saved bit convention already agrees with the spin tools:
bit zero means spin −1 and bit one means spin +1. Coefficient index k maps to
energy `E=2k−B`; normalization preserves all 16 rows without permutation or a
new Hamiltonian solve. Scalar closure and individual row counts were checked
as conversion checks. Their open polynomial representation removes no glue
edges and therefore uses the full energy bound.

N100's archived native-factor energy tables are zero. The normalized pair graph
retains its energy exactly; the original factor and observable tables remain in
`archived_instance`. Native source-row quantities are not assigned as new graph
couplings or physical energy units. N100/N105 plan metadata describes their
completed component route, not a CUDA cutset plan. No transition from the N96
ladder into these separate packet families is invented.

## Publication and package

[PUBLICATION.json](PUBLICATION.json) identifies the completed native MATTER_SEARCH
session and checkpoint. The session used SLC-GEN3-R4 / SLC-GEN3-CEV1-R4 and
published three new mathematical objects. The initial publication attempt rejected
untagged archived timing floats before any new object was published; its receipts
remain preserved. The successor retains those values losslessly as tagged
`float64_hex` metadata.

- [SOURCES.json](SOURCES.json): complete source-family registry and output availability.
- [CATALOG.json](CATALOG.json): additive default-size catalog; 99 entries.
- [BUNDLE.json.gz](BUNDLE.json.gz): 102 exported objects, 4,739,129 bytes;
  SHA256 `68e3d80bd607cdb1deaca9de47f92a22c7043db375156885871b112526e19910`.
- [SOURCES_METHOD.md](SOURCES_METHOD.md): normalization and source-selection contract.
- [qualify_sources.py](qualify_sources.py): installed retrieval and fresh-process
  checkpoint recovery qualification, separate from completed historical calculations.

Every registry reference is present in the exported object closure, and all 97
preceding references are unchanged. This inventory records source publication;
the coordinating installation/adoption reports establish each target runtime's
installation state. No historical spectrum was recomputed to build this package.
