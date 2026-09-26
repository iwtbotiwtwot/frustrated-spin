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
