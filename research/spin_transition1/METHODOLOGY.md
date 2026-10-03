# Implementation, source provenance and reproduction

## Source and model

The exact roots and repeated factors are copied from
GEN4/sb_dynamics_extension1/inputs/N005000_{family}_+1_K_MAJOR.json,
through the retained spin_normalization1 bundle. The chain GPU source and
exact CUDA kernels come from spin_gpu_coeff2, whose lineage is recorded in
spin_gpu_coeff1 and spin_gpu_n5000_1. Their file identities appear in the
bundle MANIFEST.json and native BINDING.json. No source discovery or explicit
graph construction occurs in this campaign.

The continuation is N=20+30m. The root contains15vertices with4fixed boundary
spins. Signed packet repeats a15vertex component2m times; chain repeats a
30vertex componentm times. A5vertex tail completes the system. Original
positive fill is represented exactly by the M-dependent background energy.
The new model H=-(M²-N)/(2N)+kappa*C_N is explicit; kappa=1/N is the old
whole-scaled sequence, while this map varies fixed kappa. No original source
labels or integer counts are changed by reweighting.

## Phase and finite thermal calculation

PROOF.md gives the global onset argument. algebra.py constructs two rational
Bernstein matrices (15 and56 entries), checks every entry nonnegative, and
reconstructs their power-basis polynomials exactly. Its separate motif
factorization check compares the frozen source polynomial to explicit pair/path
products. THEOREM.json retains all coefficients, exact counterexamples to the
discarded concavity argument, and192-bit brackets for the critical curve.

The phase map has154production cases: two sizes5000/20000, both signed
families at five correction strengths0,1/4,1/2,1,2 and seven beta offsets;
packet control has one correction strength because C_N=0. Four N200cases
check the new parameter wiring against direct exact-spectrum Gibbs sums.
Beta centers are rounded to12decimal places to specify exact rational
input temperatures. The exact critical brackets are retained separately.

thermal.py generalizes only the kappa input of spin_normalization1/thermal.py.
It preserves128-bit Arb/acb integration, normalized source factors, analytic
branch checks,16panels on[0,4], absolute tolerance1e-24, relative tolerance
1e-22, and the explicit infinite tails for zeroth/second moments. The floating
guide determines only an arbitrary exponential shift; it cannot change the
integral or its error bounds. Pressure includes all component normalizers.
Finite magnetization is <(M/N)²>, not spontaneous magnetization at finite N.

finite_verify.py derives full N200counts by ordinary exact integer polynomial
powering in a collision-free Kronecker encoding. It then sums finite Gibbs
weights directly at192bits. Its84comparisons cover16boundary weights,
magnetization, pressure and3protocol contributions in each of4cases.

## Boundary protocol and meaning of the three differences

Boundary state b has weight w_b=Z_b/Z_0. If j differs from b in one bit,
Q_{j,b}=w_j/(w_b+w_j); other off-diagonal entries vanish, and columns sum to0.
This is the retained declared heat-bath clock. No conversion to physical
seconds or fitted physical transition rates is made.

Let C group boundary states by their least-significant bit. R distributes
each coarse state over its boundary states with conditional stationary weights;
Pi=RC. P accepts even boundary states. For interval delta=1/3,
T=P exp(Q*delta), initial e=e_0, q=C e, and coarse generator A=CQR:

    p_full = 1^T T³ e
    p_equilibrated = 1^T T³ Rq
    p_reset = 1^T T Pi T Pi T Rq
    p_coarse = 1_2^T [P_2 exp(A*delta)]³ q.

The reported differences are p_full-p_equilibrated (preparation),
p_equilibrated-p_reset (between readings), and p_reset-p_coarse (within interval).
“Equilibrated” here means conditionally equilibrated inside the initial coarse
class, not a globally stationary initial mixture. A negative preparation
difference is retained as signed data. protocol.py copies the original function
unchanged. Probabilities and matrix exponentials use certified Arb/acb.

## Exact window selection and independent algorithms

Window selection uses the correction model's aligned-edge variable t=L-d.
Near beta_c at kappa1, zero-field expected t is about1.5 atN5000 and6 atN20000.
This supplies a reproducible guide, not an assumed finite distribution.
N5000 uses k2372..2628,t0..16; N20000 uses k9744..10256,t0..24. Both include
all16boundary labels. Count coordinates and the actual measured probability
coverage are retained. Centered windows are not presumed to follow the separated
magnetization peaks above the transition.

CPU production enumerates the four-spin path directly and reverses the defect
variable; its motif constant term is32X^6. It uses the seven-step logarithmic
derivative recurrence with exact polynomial divisions (16 or24steps), then
contracts the remaining pair, free-spin factor and root. GPU verification uses
the original defect variable, exact61-bit-prime NTTs, selected residue transfer,
and CPU integer CRT. The prime product strictly exceeds2^(N-15); all
intermediate coefficients match before any final root contraction. Global
reversal is checked for every final record.

Zero counts are legitimate and are preserved. Every record contains N,b,k,M,
aligned t,disagreeing d,original E,and the exact decimal integer g. Original
E=4t-2L-(M²-N)/2. No floating arithmetic enters the integer coefficients.

All final records are stored as gzip JSONL. Compression follows exact
reconstruction and does not truncate data. File SHA-256 and uncompressed record
stream SHA-256 are both retained. Complete certified partition functions
normalize the window sums at beta_c and beta_c±0.03, giving explicit captured
and omitted probability. No missing coefficient is silently assigned zero.

## Hardware and timing boundaries

Existing pod213.192.6.70:40117: RTX PRO6000Blackwell Workstation Edition,
EPYC9575F,31.13CPU-equivalent quota,124999999488-byte RAM quota,500Gcontainer
disk. The retained isolated Python3.12.3/CuPy13.6.0/python-flint0.8.0/CUDA12.8
environment is reused. HARDWARE.json records the inspection. No system
package changes, new rentals or GPU-memory reservation are required.

Thermal workers use12processes onCPU4–15. GPU control usesCPU0, and the
independent count recurrence usesCPU1. Timings separate transforms/transfer,
CRT/readout, CPU coefficients and final root contraction/serialization/mass.
Reported CPU/GPU coefficient comparisons concern the same intermediate keys;
common final root/output work is reported separately. CPU recurrence and GPU
work overlap on separate cores. CUDA event timing independently accompanies
the GPU-route host timer. Live CuPy pool memory is not total process GPU memory.

The local i9 controller runs through the project resource manager; the remote
worker has a1800second timeout. The1950second local budget includes transfer.
Native STARBREAKER/SB-GEN3-ACCUMULATION-R1 execution uses SLC-GEN3-R4 and
SLC-GEN3-CEV1-R4. The source-bound SPIN_TRANSITION_MAP adapter supplies the
missing fixed-coupling transition/window operation. It is not a generic-engine
installation. Chalkboard stays OFF_OWNER_SUSPENDED. Lilhelper is used only
for T500storage; prime-event and all unrelated workloads are unchanged.

## Preserved execution faults

The first launch preceded completion of asynchronous source transfer. No
scientific calculation started. The failed log/native session are retained
under attempt1_deployment_race. Transfer completion and all14source hashes
were then checked before restart.

The second attempt completed all158thermal cases, source algebra and84direct
checks. Its first targeted-count serialization incorrectly asserted g>0.
The source permits exact zeros, so this was replaced by g>=0 with an explicit
zero counter. All old code, logs, partial output and native failure records
remain under attempt2_zero_count. Completed thermal/algebra outputs were copied
as manifest-bound PRIOR inputs. resume_worker.py checks every unchanged
scientific source/code identity before reuse; only window/worker plumbing
changes. No completed thermal case was silently recomputed or altered.

## Reproduction

Restore the verified archive to a separate work directory. Copy the files listed
in bundle/MANIFEST.json plus that manifest into an empty calculation directory;
do not execute inside the immutable archived original. With the recorded CUDA
and Python dependencies, run worker.py to regenerate the algebra, thermal map,
independent finite checks and both CPU/GPU windows. resume_worker.py is the
recorded successful continuation using the included PRIOR results.

For project-native execution, adapt only the new deployment paths/SSH endpoint
in native_run.py, retain its source binding, and launch through the resource
manager. Scientific inputs are deterministic; no random seeds, fitting or
sampling acceptance criteria are involved. Changing window coordinates or
model parameters constitutes a new recorded calculation.

plot.py reads the retained RESULTS.json, displays rounded interval midpoints,
and exports PNG/PDF plus PLOT_DATA.csv. Matplotlib3.10.7 was installed only in
/tmp/spin-transition-plot-packages through official standalone pip; the project
scientific environment was not modified. PLOT_RECEIPT.json records the figure's
input hash. Connecting lines are visual guides between certified data points.

## Custody

Bulk output transfers directly from the pod to
/home/sam/mnt/lilhelper-t500/GEN4/spin_transition1. Source/report/figure copies
are local. REMOTE_HASHES.json checks current and preserved-failure artifacts.
CUSTODY.json records full archive readback and exact archive hash. Pod originals
remain. T500originals and their archive share a disk; they are not independent
physical replicas. No provider shutdown, public upload, repository push or
revision of the earlier unpublished manuscript is performed by this campaign.
