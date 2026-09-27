# Shared exact spin and finite-factor tools

Installed entry point: `./spin-tools`, or the GEN3_SPIN operations through any current CE domain session. GEN3 and scoped GEN4 use the same source-aware interface.

The default roster is exactly every N from1 through96, plus100,105,120. A separately named historical N120ring is also retained. Retrieval never starts a fresh solve; SOLVE explicitly computes a new answer unless mode=recover supplies an authenticated prior result.

| Operation | Purpose |
|---|---|
| GEN3_SPIN_TOOLS | Discover the shared capability and its scope |
| GEN3_SPIN_SOURCES / SOURCE | List or retrieve exact source-family records |
| GEN3_SPIN_SELECT | Select a source-appropriate plan and execution backend |
| GEN3_SPIN_SOLVE | Fresh exact CPU/CUDA spectrum or explicit recovery |
| GEN3_SPIN_CONTRACT | Exact finite signed integer factor contraction |
| GEN3_SPIN_READOUT | Exact moments, rational reweighting and port conditioning |

The seven prior catalog/planning/learning/cost operations remain callable. Legacy PLAN/COST use the N96 transition planner; SELECT/SOLVE provide the common source-family interface including component sources. Model timing calibration and exact arithmetic are separate.

# Spin tools command line

The installed `./spin-tools` calls the current MATTER_SEARCH DomainSession and
prints its verified engine announcement/session path to stderr. Each operation
retains its full native receipt and an additional full JSON result file; terminal
output is compact unless `--full` is selected. `--output FILE` chooses the full
result file and refuses to overwrite an existing file. `--session DIRECTORY`
reopens an explicit compatible session; work commands checkpoint their results.

```sh
./spin-tools sources
./spin-tools source --N 100
./spin-tools source --N 105 --full
./spin-tools source --N 120 --family SLCX028_N120_REPEATED_MOTIF_RING_V1
./spin-tools select --N 105 --policy structural
./spin-tools solve graph.json --payload solve-options.json
./spin-tools solve --N 105 --payload solve-options.json
./spin-tools contract contraction-payload.json
./spin-tools readout readout-payload.json
./spin-tools call GEN3_SPIN_SOURCE '{"N":100}'
```

Graph and payload arguments accept a JSON filename, an inline object, or `-`
for stdin. Select/solve accept an explicit graph or the catalog selectors `--N`,
`--family`, `--hash`; their optional `--payload` contributes operation-specific
fields unchanged. The generic `call OP PAYLOAD` passes its entire JSON object
unchanged, allowing all installed options without extending the CLI. Global
`--root`, `--session`, `--output`, and `--full` work before or after a command.
For example, a solve payload can contain `{"backend":"cpu","mode":"fresh",
"options":{"method":"components"}}`. Fresh solve computes the supplied graph;
source retrieval reuses a completed result. Recovery mode accepts the explicit
retained result reference defined by the solve operation.

On the workstation, calculation commands run through the installed resource
controller and `.venv-r3`. GEN4 uses `/opt/gen4/venv` under pod resource management.
No launcher starts workers, restores old campaigns, or changes source selection
implicitly. N-only 120 selects the current frontier; request the historical ring
by its family or canonical source hash. N100/N105 retained component metadata is
not a precomputed CUDA cutset plan; select/solve use their declared operation
policy and backend.


# Shared exact spin tools: source and capability map

The requested default roster is exactly every integer N1 through N96, then
N100, N105 and the completed frustrated N120. This is99defaultentries. The
historical N120ring is retained additionally under its own family/hash; it does
not replace the current default. A source is an explicit graph with integer
fields/couplings, stable vertex labels and specified boundary ports.

The installation has four distinct kinds of reusable material:

| Material | Installed use |
|---|---|
| Exact spectra and conditional operators | Read/query without repeating the completed calculation |
| Source transitions and alternative plans | Determine which boundary information or structural work can be reused |
| Learned policy and cost models | Rank admissible plans; keep calibration hardware explicit |
| Exact algorithms | Solve new declared graphs or contract finite signed factor tables |

The published registry retains all previous references. N100/N105 come from
their completed packet/component sources and full16conditional spectra.
No synthetic96→100→105 transition is invented. The original96→120 transition
retains its actual changed-boundary record. The historical ring import has a
scalar spectrum; its transfer-state tables are not relabeled as the newer
four-port conditional operator.

## Executable source mappings

- **Volume II:** a declared classical or diagonal interaction graph maps to
  integer couplings/fields and boundary variables. The exact tools return its
  density of states and conditional source responses. Noncommuting exchange
  operators retain their existing separate operators.
- **Volume I:** declared finite source responses can use exact moments,
  rational reweighting and boundary conditioning. A density of states alone
  does not specify transition rates or a physical clock; any dynamics map is
  supplied explicitly by the research question.
- **RH:** finite signed arithmetic factors can use the generic contraction
  operation. That operation evaluates caller-supplied arithmetic data with
  signed exact integers. Spin spectra are not substituted for RH inputs.
  This installation adds no uniform-cancellation result.
- **General computation:** source decomposition, exact polynomial convolution,
  variable elimination, finite signed factors, plan choice and authenticated
  result reuse are available through the same GEN3 operation interface.

Local GEN3 remains the global workstation runtime. The research pod uses its
scoped GEN4 runtime. Changes are additive in their current generations, with
predecessor bindings and rollback copies retained. Existing paused controllers
and suspended Chalkboard remain unchanged. MP candidate224872321 is shelved;
this installation launches no MP research or prime verification.

## Adoption design

Retrieve the complete99-size roster through native operations, verify exact
source identity and preserve both N120families. Compare fresh small CPU solves
against independent enumeration, exercise signed cancellation and nonbinary
factor domains, and exercise source-conditioned readouts. Execute a fresh GPU
case on the actual research device and compare its full scalar and conditional
outputs. Recover published output from a reopened native session. Exercise the
shared interface through MATTER_SEARCH, ATOM3D, STARBREAKER and RH consumers.
These are implementation/adoption checks; completed N120arithmetic is reused.


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


# Explicit spin plan selection

`GEN3_SPIN_SELECT` accepts `source` and optional `previous_N` (default96),
`policy` (`auto`, `structural`, `focused_pairwise`), `backend` (`batched` or
`retained` readout), `search` (`standard` or `expanded`), `ports` and
`execution_backend` (`auto`, `cpu`, `gpu`). It returns a plan and explicit
execution backend; no spectrum is computed by selection.

Disconnected sources with independently enumerable components route to exact
CPU component-polynomial contraction. The selected plan retains every component
and its assignment count. This includes the separate N100/N105 packet sources;
their N labels do not imply the N96 family's graph or CUDA order. An explicit
CPU request may instead request bounded polynomial elimination for a larger
component. If a requested predecessor has component-route metadata, N96 is
used only as the named retained ordering/feature anchor for GPU planning.
This does not construct a physical/source transition between those families.

For an identical known graph with matching ports, `auto` can reuse its retained
mathematical plan. The returned original measurement kind remains attached to
its source; it is not a runtime forecast for the caller's hardware. Otherwise
the standard five-method or expanded portfolio is generated, and every admitted
candidate is validated through the same exact GPU plan contract. Custom ports
can use structural min-fill; they are outside the focused model's declared
training port convention.

`structural` selects by exact weighted elimination work, then width and stable
candidate order. `focused_pairwise` explicitly invokes the installed native
`GEN3_TREE_PREDICT` with the retained model and its exact source binding.
Features are the existing15-component focused vector. Each ordered candidate
pair supplies difference+A+B (45features); exact rational probability sums
rank plans, with structural work breaking ties. The fast/batched model is
`spin-focused-fast-pairwise-v1`; retained readout uses
`spin-focused-pairwise-v1`. No model fitting occurs here.

`auto` enables the focused model only on the observed retained hardware
signature:14BlackwellPRO6000-class MIG devices,46SM each, approximately24GiB
each. Otherwise it uses structural selection. An explicit focused request can
transfer the ranking policy to another machine, but its result identifies
that transfer and supplies no timing forecast. Matching a hardware signature
is a routing condition; it does not newly calibrate CPU, driver or workload
costs. The stored timing regression remains separately accessible through
`GEN3_SPIN_COST` with its existing hardware scope.

The focused models were learned from six topology families sharing the N96
ancestor, with training/development/reserved families separated. Native model
inference changes the chosen admissible plan only. The worker still executes
the exact source and retained-port query. The model is not a new energy law,
a guaranteed optimum, or a source for new physical/RH results.

Source-registry families, exact spectra, learned policies, cached measured
plans and reusable algorithms therefore remain distinct but executable parts
of the same installed interface. No paused controller or shelved domain is
restarted by selection or installation.


# Installed exact CUDA spin execution

`spin_gpu.solve_gpu(source, plan, options)` promotes retained conditioning,
CUDA elimination graphs, inverse NTT and CRT arithmetic into one source-explicit
solver. The source and requested ports are explicit; a supplied plan is checked
against the graph. Without a plan, deterministic min-fill constructs one for
the requested ports. A planning operation itself computes no spectrum.

The source energy is `E=-sum(J*s_u*s_v)-sum(h*s_u)` with integer couplings/fields
and spins ±1. Bit i selects the sign at ports[i], with 0=-1 and 1=+1. Source
validation, distinct glue edges within the ports, conditioning/order coverage,
recomputed width, exact energy bound, root order and CRT capacity are checked
before execution. The product of qualified primes must strictly exceed 2^N.
The qualified fifth prime retains the N120 arithmetic capacity. Arbitrary
additional primes are not admitted by this implementation.

`build_gpu_vendor.py` extracts unchanged named exact-factor, projection and
root definitions from the retained exact-source archive. The CUDA worker and
kernel come from the catalog archive; batched readout comes from the focused
archive. Installed-relative imports replace campaign startup paths. The
compatibility namespace supplies only their existing arithmetic interfaces;
it imports no historical run script. Archive/member hashes and every emitted
file hash are retained in vendor/MANIFEST.json. Install that directory as
`CURRENT_REVISION/engines/SLC/gen3/spin_vendor/`. The live solver verifies these
file hashes before calling them. No old `/opt` path or campaign environment
variable is required. The readout documentation includes the fifth prime;
its squared products remain below signed-int64 capacity.

The executor observes visible CUDA devices. Optional `devices` and `workers`
restrict that observed roster; there is no fourteen-worker requirement.
Each selected device owns CUDA graphs, arrays, maps and a worker thread.
Root batches and conditioned-branch groups are powers of two. Each
prime/root-batch/branch-group contributes exactly once to modular totals.
Changing a branch group reuses its compatible graph layout and buffers.
CUDA-event nanoseconds and host/task times are retained; these are not SM
occupancy measurements and no old timing model predicts the new hardware.

Projection-map byte counts are calculated before materializing exponential
arrays. Width, branch/task counts, energy span, requested output size, map
bytes and resident arithmetic-array estimates have explicit admission limits.
VRAM estimates are checked against current free memory before allocation;
CUDA graph/pointer overhead also remains subject to the device allocator.
The defaults include width22,4096branches,1milliontasks and2GiB projection maps.
N120's qualified machinery is supported, but this installation does not launch
a new N120 solve merely to expose it.

`checkpoint_dir` enables resumable modular state. The immutable binding names
the source, mathematical execution plan, vendor and batch layout. Each flushed
NPZ is content addressed; an atomically replaced STATE.json authenticates its
hash, binding and coverage count. Load rejects changed sources/plans, invalid
shapes/ranges or changed residue bytes. Completed task coverage is retained
explicitly. The deadline returns `CHECKPOINTED` with no answer when a checkpoint
directory exists, and otherwise raises a timeout. A resumed call reports its
inherited task count and newly executed task count separately. A completed
checkpoint does not masquerade as fresh arithmetic.

Exact inverse NTT/CRT reconstructs all open-port polynomials and closed
conditional spectra. Retained count, first/second energy moment, per-port
count and polynomial-support checks remain. The common CPU/GPU finalizer
constructs canonical `GEN3_EXACT_SPIN_DOS_V1` output and repeats its own exact
checks. Elapsed times are integer nanoseconds; model metadata cannot alter
exact counts. GPU arithmetic runs through the installed source-bound domain
operation dispatched by spin_exact, rather than outside the native session.

The relevant runtime dependencies are NumPy, CuPy with CUDA support, FLINT
for the common finalizer, and the installed source/catalog modules. CUDA
availability is required only when GPU execution is requested. The workstation
can retain the same capability while using its exact CPU backend.


# Completed spin source registry

This additive publication retains every installed N1–N96 and current N120
reference unchanged and adds the completed N100 P2 packet-plus-depth and N105
historical-packet restoration records. A separately named historical N120 ring
is retained alongside the current frontier. Integer N is a size, not a family.
N120 alone continues to resolve to the current five-regular frustrated frontier.

`GEN3_SPIN_SOURCES {}` lists each source's N, family, canonical graph hash,
result reference, default selection and available spectrum outputs.
`GEN3_SPIN_SOURCE` accepts optional N, family and source_sha256 selectors;
at least one is required and the intersection must identify one record. N-only
selects the documented default. Family-only queries matching several sizes are
explicitly ambiguous. Existing `GEN3_SPIN_ENTRY` gains N100/N105 through the
additive catalog. No transition to them is invented.

The archived N100/N105 edge dictionaries become integer [u,v,J] triples,
fields remain exact integers, and stable parent vertex labels are 0 through
N−1. Installed validate_source creates the canonical graph/hash. Archived
instance and spectrum identities remain separately recorded, with full source
file SHA256 custody and original typed variable/observable metadata. The N100
source's native-factor energy tables are all zero; their source records and
observable tables remain available in archived_instance. A nonzero constant or
factor energy is rejected rather than silently dropped.

Both archived packet tensors use bit zero = spin −1 and bit one = spin +1,
with bit i corresponding to port_order[i]. Their order is [0,1,60,61], roles
plus, minus, anti_plus, anti_minus, so no port permutation is needed. Ascending
coefficient index k denotes energy E=2k−B. Converting these existing coefficients
to sparse closed_port_rows and scalar_dos is representation normalization only.
The sparse open_y_operator uses the same coefficients and removes no glue edges;
its local bound is the full graph bound. Exact count/row-sum/scalar-closure checks
catch conversion faults without rerunning the completed Hamiltonian calculation.

N100/N105 plan metadata describes their retained component route and historical
measurements. It is not a CUDA cutset plan or newly trained timing model. The
archived timing floats are retained losslessly as tagged float64_hex strings for
the exact native object store. The first publication attempt rejected an untagged
timing float before publishing a new object; its session receipts remain retained.
The corrected successor uses this representation without changing any timing.
The
historical N120 ring supplies its archived scalar DOS and source/transfer method;
closed conditional rows are explicitly unavailable in that release artifact.
Its recorded 16 transfer states are not substituted for 16 full-source
conditional spectra. The new frontier's full port tensor stays unchanged.

Publication and export use a fresh MATTER_SEARCH DomainSession under the current
GEN3 runtime. Existing entries are retrieved through the native catalog; new
records enter through GEN3_RESULT_PUBLISH, export through GEN3_RESULT_EXPORT,
and a native checkpoint retains the publication. No existing result is recomputed,
no frozen source is edited, and no global generation or runtime is changed by
the builder. Installation/adoption is performed separately by the coordinating
installer. BUNDLE.json.gz contains all registry roots and their dependency closure.

Shared extension: [packet compilation and joint readout](SPIN_JOINT.md), SHARED_SPIN_JOINT_V1.

Shared extension: [packet compilation and joint readout](SPIN_JOINT.md), SHARED_SPIN_JOINT_V1.

Shared extension: [packet compilation and joint readout](SPIN_JOINT.md), SHARED_SPIN_JOINT_V1.
