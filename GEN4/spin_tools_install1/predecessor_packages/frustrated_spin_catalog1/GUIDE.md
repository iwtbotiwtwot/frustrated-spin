# Exact spin catalog and transition memory

GEN3 and GEN4 share four installed operations through any active DomainSession:

| Operation | Payload | Result |
|---|---|---|
| `GEN3_SPIN_CATALOG` | `{}` | Source roster, entry/transition references, model binding |
| `GEN3_SPIN_ENTRY` | `{"N":96}` | Exact source, DOS, 16 retained port rows, elimination plan |
| `GEN3_SPIN_TRANSITION` | `{"from_N":84,"to_N":96}` | Added interactions, required boundary, candidate costs, observed execution |
| `GEN3_SPIN_PLAN` | `{"source":graph,"previous_N":96}` | Compared exact structural plans, reuse recipes, advisory prediction |

Entry lookup optionally takes `source_sha256` and rejects a mismatch. The source
roster is N2,8,12,18,24,36,48,60,72,84,96: nested induced subgraphs of the retained
96-spin,240-edge source. Smaller entries have different graphs from the older
standalone dense benchmarks. Original N72 benchmark custody remains separate.

All entries were freshly calculated on the pod in a GEN4 MATTER_SEARCH session.
The exact integer DOS counts all 2^N configurations. Small cases use retained
modular CPU arithmetic; N36 onward uses fourteen persistent CUDA workers,
two VRAM input banks and CPU exact NTT/CRT reconstruction. Source-specific
retained ports and removed/reinserted glue edges are explicit in each entry.

`GEN3_SPIN_PLAN` requires integer `N`, `fields`, `edges` as `[u,v,J]`, distinct
stable `parent_vertices`, and a `parent_instance_sha256` identifying provenance.
The graph's bound and identity are recomputed. It compares fresh min-fill,
previous-order priority, and the parent plan, with/without inherited cutset
sites. Index recipes depend on normalized bit positions, so their reuse remains
exact across different graphs. The returned recipe path is an installed compact
input for the pod worker's RAM/VRAM cache; it is not a claim that VRAM survives
worker shutdown. More than four NTT primes or width above22 is reported through
the plan admission fields, so a future executor can refine its resource plan.

The ten executed transitions retain all candidate costs and chosen plans. The
native `spin-transition-plan-v1` CART model is installed with its exact source
binding. Its first ten-row curriculum selected depth0 and predicts the same
class for every row; it remains advisory. Exact measured candidate costs choose
execution. A later model must use a new identity and retain these observations.
N84 selected development depth; N96 labels were reserved from fit/selection.

The retained boundary must cover all changed interactions before an old
conditional spectrum can be extended directly. The planner reports the touched
boundary and changed fields. Otherwise it reuses plans/index recipes and computes
the new spectrum. A scalar DOS alone cannot preserve those correlations.

Generic `GEN3_RESULT_GET/EXPORT/IMPORT` works with these objects and their
dependency closure, including portable GEN3↔GEN4 transfer. Fresh native sessions
can retrieve entries and transitions without new spin arithmetic or model fitting.
The catalog does not assign a universal spectrum to N: every answer has an exact
graph, fields, couplings, energy convention and source identity.
