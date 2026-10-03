# Exact coefficient batching and N20000

Sean's “Lets do it” authorizes the proposed bounded GPU batching, independently
checked N20000 window, and explicit normalization comparison. This directory
contains the coefficient leg. The normalization derivation is additive and
does not change the archived Hamiltonian or prior source records.

Use retained chain source and unchanged pilot.py, gpu_baseline.py, kernels.cu.
Only query sets and boundary contraction generalize: k=N/2±r_k and
d=floor((7m+4)/2)±r_d, all16boundary states, m=(N-20)/30.
At N10010 test radii(0,1),(4,4),(16,16); at N20000 use(4,4).
The largest N10010 window and N20000 window are independently reconstructed
by the retained seven-step exact CPU polynomial recurrence. Nested smaller
windows use those same independently computed results. Retained N10010
48-count reference is an additional comparison. Check global spin reversal.

GPU0 with hostCPU0; CPU recurrence workers on cores1 and2. Bounded remote
timeout1800seconds; local resource-managed controller1950seconds. This budget
is an operational bound, not a scientific threshold. Preserve partial outputs
if it expires. No automatic successor, unrelated worker or provider lifecycle
action. Bulk goes directly from pod container disk to T500.

STARBREAKER/SB-GEN3-ACCUMULATION-R1, SLC-GEN3-R4/SLC-GEN3-CEV1-R4,
source-bound SPIN_GPU_BATCH operation. Installed full joint solver does not
offer this selected GPU window; retain the existing adapter pattern. No generic
engine promotion. Chalkboard stays OFF_OWNER_SUSPENDED.

These windows measure batching and supply exact local counts. They are not
asserted to contain most of the Gibbs probability at a chosen temperature.
Thermal mass coverage is a separate measured quantity.
