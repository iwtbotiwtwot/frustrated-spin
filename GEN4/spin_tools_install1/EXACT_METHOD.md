# Reusable native exact spin and finite-factor operations

This successor makes source-explicit exact spin computation, retained-spectrum
readout and signed finite-factor contraction available through the existing
domain runtime. The operations supply computational tools across domains;
an application supplies its own variable interpretation and source mapping.
No graph is inferred from an unrelated domain label.

## Sources and installation seam

The CPU component method develops the installed
`CURRENT_REVISION/engines/SLC/native/structure.py` N100 component-conditional
route. It preserves explicit fields, signed couplings and requested port states,
and supports retained ports distributed over multiple disconnected components.
Scientific integer arithmetic uses FLINT `fmpz`; polynomial convolution uses
FLINT `fmpz_poly`. The source normalizer is the installed `spin_catalog.py`.
Source graphs use local vertices0..N−1, integer fields, unique edges[u,v,J],
stable `parent_vertices`, source family and source hash. The energy convention is

`E(s) = -sum(J_uv*s_u*s_v) - sum(h_u*s_u)`, with each spin±1.

The historical component route's localized-port restriction is not inherited:
each component carries its own port bits, and disjoint masks combine exactly.
Higher-order energy tables and nonzero energy constants are not silently dropped;
the pair-graph solver rejects them. The separate finite-factor API accepts
explicit higher-arity integer factors.

The GPU seam is `.spin_gpu.solve_gpu(source, plan, options)`. It shares the
canonical answer builder with CPU. GPU plan/cutset preparation, source-binding,
modular coverage and partial-checkpoint behavior are documented by that adapter.
This module is staged under `GEN4/spin_tools_install1`; installation and binding
updates are owned by the root installer, not by this file.

## SOLVE: fresh computation and explicit recovery

`GEN3_SPIN_SOLVE` requires `source`. The root bridge can resolve a registered
N/family/hash selector before dispatch. Optional fields are `ports`, `backend`,
`options`, `plan`, `previous_N`, `policy`, `search`, `mode` and `result_ref`.
Ports are local vertex indices in the requested order, defaulting to the first
min(N,4)vertices. Bit i=1 denotes spin+1 at ports[i]; bit i=0 denotes−1.

`backend` is `auto`, `cpu` or `gpu`. Auto selects CPU for admitted small
components; otherwise it uses available CUDA devices. If CUDA is unavailable,
it attempts explicitly bounded CPU polynomial elimination. It never returns a
previous outcome as a substitute for a fresh solve. Without a supplied plan,
the operation calls installed `GEN3_SPIN_SELECT`, so cached identical-source
plans and eligible learned policies participate in actual execution. The
selection receipt and referenced plan dependencies accompany the new result.
CPU arithmetic still independently checks its own component/elimination limits.

`mode=fresh` is the default and forbids an outcome `result_ref`.
`mode=recover` requires a retained fresh-solve result reference and verifies
the requested source hash and ordered ports. Recovery explicitly reports
`recomputed=false`. A new READOUT can also consume an original catalog result
without first solving it again.

CPU options and defaults:

| Option | Default | Meaning |
|---|---:|---|
|method|auto|components or variable_elimination can be selected explicitly|
|max_component_size|20|Largest enumerated connected component|
|max_assignments|2000000|Sum of component assignment counts|
|max_factor_work|10000000|Finite-table work admission units|
|max_intermediate_entries|1000000|Largest admitted finite intermediate table|
|max_output_rows|1000000|Retained coefficient/table output ceiling|
|max_energy_span|200000|Dense energy-polynomial support ceiling|
|max_port_states|256|Maximum retained port assignments|
|max_seconds|120|Checked wall-time budget in integer seconds|
|elimination_order|automatic|Optional complete nonretained-variable ordering|

These are explicit implementation resource ceilings, not claims about the
mathematics or permanent exclusions. Source graphs currently admit at most4096
vertices. The component path uses Gray-code single-spin energy updates in
native integers. Each component produces conditional histograms; their native
polynomial convolutions reconstruct the complete distribution without expanding
the product assignment space.

The polynomial elimination path assigns each local interaction a nonnegative
power `abs(J)-J*s_u*s_v`, and each field `abs(h)-h*s_u`. Summing eliminated
spins and multiplying factors in `fmpz_poly` yields `y^(E+B)`, where
`B=sum(abs(J))+sum(abs(h))`. Subtracting B recovers signed physical energy.
The complete finite-table schedule is checked before elimination arithmetic.
This permits connected low-width sources beyond the component enumeration
ceiling. A work unit bounds scalar/table operations, not native polynomial
coefficient operations; the energy-span ceiling separately controls those.
Wall limits are checked between native operations, so an individual admitted
native operation can complete after the precise deadline.

The canonical answer contains scalar DOS, every requested closed port row,
configuration count, ground energy/degeneracy, first three energy moments,
source hash and spectrum hash. It checks nonnegative counts, every conditional
count `2^(N-number_of_ports)`, total `2^N`, zero first moment, and second moment
`2^N*(sum(J²)+sum(h²))`. These are independent algebraic source identities.
The GPU adapter may also retain its open-port operators separately.

## CONTRACT: generic signed finite sums

`GEN3_SPIN_CONTRACT` requires `variables`, `factors` and a nonempty
`source_binding`; optional fields are `keep` and `options`.

```
variables = [{"name":"x","domain":[-1,1]},
             {"name":"y","domain":["a","b","c"]}]
factors = [{"scope":["x","y"],"table":[1,-2,3,4,0,-1]}]
keep = ["x"]
```

Each domain explicitly lists distinct integer/string states. A factor table is
row-major in its declared scope, with the last variable varying fastest. Empty
scope is a scalar factor. Coefficients are exact signed integers or decimal
strings; floating-point inputs are rejected. The operation sums all variables
outside `keep` and returns their exact signed tensor. Isolated eliminated
variables contribute their actual domain cardinality. Empty factor collections
are the multiplicative identity, not an empty answer. Cancellations remain signed.

The generic engine chooses a deterministic minimum-table-size elimination order
unless one is explicitly supplied, preflights its dense intermediate sizes and
executes all coefficient sums/products using native `fmpz`. Domain sizes are
at most256 and the input accepts at most10000factors. This is a finite exact
contraction, not a probability model or an inferred physical transport law.

## READOUT: exact conditional and rational response

`GEN3_SPIN_READOUT` requires `result_ref`; optional fields are `conditioning`,
`moment_orders` and `energy_weights`. Conditioning maps canonical string local
vertex IDs to integer±1. The vertex must be a retained port. Moment orders are
distinct integers0..16. Default moments are0,1,2.

`energy_weights=[{"energy":-2,"weight":"3/7"},...]` defines explicit rational
weights; omitted energies receive zero weight. Without this field all
configurations have weight1. FLINT `fmpq` computes weighted mass, raw moments
and normalized moments. When signed weights cancel to zero, normalization is
undefined and returned as null. Signed weights are labeled as such, without
interpreting them as probabilities.

Original catalog spectra are accepted through a source-bound conversion. Full
closed-port rows retain their actual port identities. A historical scalar-only
result is represented with no retained ports: scalar readout works, and port
conditioning is rejected because those correlations were not stored. Conversion
does not claim a new spin solve.

## Persistence and qualification

Successful fresh operations publish their exact result using
`GEN3_RESULT_PUBLISH` with implementation/source provenance and explicit operand
dependencies, then checkpoint. These publications remain linked to actual
operation receipts; they do not masquerade as a different native solver type.
GPU partial completion returns `CHECKPOINTED` with no exact answer and is not
published as a completed spectrum.

Run `qualify_exact.py --root CURRENT_RUNTIME --out NEW_EVIDENCE_DIRECTORY`
through the project resource wrapper after installation. It calls the installed
operations through `DomainSession`, retaining the actual engine announcement.
Small independent full enumeration and the open-chain binomial formula run in
a separately bound native reference adapter within the same session. Tests
compare every scalar/conditional coefficient, both CPU algorithms, connected
N30 elimination, nonbinary signed contraction, exact cancellation, isolated
domains, rational zero-mass readout, admission/source controls and persisted
result/readout recovery. It performs no N120 rerun. An optional `--domain`
supports the same explicitly mapped qualification in another open domain.
