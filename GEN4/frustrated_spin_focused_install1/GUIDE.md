# Exact spin catalog, focused planning and cost learning

The existing N1..96 catalog,105transitions,nine learned models and all predecessor
references remain. Focused training adds two native pairwise CART models, explicit
cost-regression models for both readout backends, a boundary reuse cost model,
and repeated exact best plans for the focused source roster.

GEN3_SPIN_PLAN {"source": graph, "previous_N":84} now first checks an identical-
source plan cache. Known sources return their fastest measured plan and exact
source reference, avoiding repeated expanded search. Unknown sources continue
through the installed five-method/native ranking planner. No new spectrum is
computed by a planning operation. Set optional search="expanded" to apply the
qualified32-seed/cutset-member-removal search to a new explicit graph. The added
planning cost is reported separately; identical-source cache hits avoid it.

GEN3_SPIN_FOCUSED {} returns model/source references and hardware calibration.
GEN3_SPIN_COST {"source": graph, "previous_N":84, "backend":"batched"} returns
predicted costs for the existing five-method portfolio plus the retained best
expanded plan when known. Use backend="retained" for the prior scalar readout.
Times are estimates for the trained fourteen-MIG GEN4 setup, excluding source-plan
search and initial preparation. They are not workstation runtime forecasts.

Regression runs in NumPy CPU; pairwise trees use native C++/GMP. Float64 parameters
are retained losslessly as tagged hexadecimal strings inside exact mathematical
objects. Cost estimates do not alter the exact source or its requested spectrum.

The fast exact reconstruction and source-bound GPU runner are portable campaign
successors at GEN4/frustrated_spin_focused_training1/{fast_readout.py,run_fast.py}.
They batch inverse NTT over retained port rows, cache transform constants and
precompute CRT coefficients. Integer arithmetic/count/moment/port checks remain.
The full coefficient-level qualification and end-to-end measurements are retained.

Boundary model source is the declared N30 future graph and incoming exact state.
Its results compare incremental step cost after the previous state exists.
GEN3_SPIN_LEARNING returns all training experience references; use the retained
result API to retrieve the boundary model, examples and explicit source bindings.

When the completed N120 frontier is included, `GEN3_SPIN_ENTRY {"N":120}` and
`GEN3_SPIN_TRANSITION {"from_N":96,"to_N":120}` expose its exact spectrum and
changed-boundary transition. This connected five-regular extension is a separate
source family from the earlier structured N120 ring. Its single exact execution
retains a reusable plan, with role `RETAINED_EXACT_PLAN_FOR_IDENTICAL_SOURCE`;
it is not presented as a repeated median or a trained frontier timing model.

Restart instructions and portable runtime/source/checkpoint archives are in
GEN4/frustrated_spin_focused_training1/RESTART.md. See that folder's RESULT.md
and frustrated_spin_n120_frontier1/RESULT.md for actual completed measurements.
