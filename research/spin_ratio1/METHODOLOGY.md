# Implementation and reproduction

## Source and graph construction

Frozen inputs are the signed_packet and signed_packet_chain N005000 +1
K_MAJOR JSONs from GEN4/sb_dynamics_extension1/inputs. The worker decodes
stride=bound/step+1, extracts the size-15 or size-30 repeat, and reverses the
aligned index to the disagreement exponent. It compares the resulting exact
polynomial to B³(1+X)⁹ or AB⁴(1+X)¹⁸. Source SHA-256 identities are in
RESULTS.json and the frozen bundle manifest. PROOF.md specifies the new integer
cell constructions and the unchanged finite root/tail.

## Algorithms

1. Symbolically differentiate the exact core response with (1−v²)∂v to obtain
   second, fourth and sixth cumulants per core spin. Add the free contribution
   with its literal fraction; no fitted coefficients.
2. At a=1/2 solve c₄=0, βχ=1 exactly. Check global response domination using
   a truncated atanh series and positive rational Bernstein coefficients.
3. Extend that identity over a∈[0,1/2] by tensor Bernstein coefficients;
   independently reconstruct each power polynomial from those coefficients.
4. Verify cumulants by enumerating every literal core spin configuration at
   five rational a values. Construct a histogram of total magnetization and
   aligned edges, without using B or A. Weights q₀^(aligned edges) are exact
   rationals for these checks; all constant Gibbs factors cancel.
5. Compute positive-pressure witnesses with directed 192-bit Arb balls, both
   from positive factor expressions and from the independent histogram.
6. Explore the local ratio curve with 65-digit mpmath root finding. Equal
   pressure and stationarity are both enforced. These numerical coordinates
   are exploratory branch estimates, not interval-certified global extrema.

Maximum explicitly enumerated core: 12 spins, 4,096 states. No full graph or
joint spectrum is expanded. The pair/chain symbolic certificates are exact
at every cell count in the thermodynamic statement, not fitted to large N.

## Hardware and runtime

Existing pod root@213.192.6.70:40117. AMD EPYC 9575F host;
cpu.max=3113000/100000 (31.13 CPU-equivalent allocation), memory.max=
124999999488 bytes. GPU: RTX PRO 6000 Blackwell Workstation Edition,
97887 MiB reported; not used by this algebra workload. Workers pinned to
pod logical CPU 0, one worker, Arb threads=1. Local source-bound controller
uses workstation CPU4 under the shared resource manager. No lilhelper compute.

Pod Python 3.12.3, SymPy 1.13.3, mpmath 1.3.0, python-flint 0.8.0 in the
existing /root/spin_gpu_coeff1_venv. HARDWARE.json records worker runtime and
POD_SNAPSHOT.json records the actual host limits. The main worker's measured
wall time and peak RSS are retained in RESULTS.json; extension timing is
separate in EXTENSION.json. No speedup or hardware-saturation claim is made.

## Native execution and portable replay

Installed domain: STARBREAKER / SB-GEN3-ACCUMULATION-R1 / SLC-GEN3-R4 /
SLC-GEN3-CEV1-R4. The installed spin operations lack variable-ratio global
tricritical analysis; two source-bound scoped adapters fill that specific gap.
They do not replace the selected numerical engine or promote a new capability.
Each call retains a mathematical_result plus native export and checkpoint.
The controller compares bundle hashes before execution, imposes timeout1800s,
and transfers completed outputs directly to T500.

Replaying the portable worker in a copied bundle requires the two frozen JSON
inputs next to worker.py. Run worker.py, then extension.py; each writes its
own output file. For project execution use the included native controllers
through CURRENT_REVISION/engines/SLC/gen3/resources.py, adjusting remote and
output paths in a new additive reproduction directory. Never overwrite the
completed campaign. Plot.py only reads retained results and produces figures.
Matplotlib 3.10.7 was supplied from /tmp/spin-transition-plot-packages; no
project scientific environment was altered for plotting.

## Fault and custody accounting

The shared manager declined starts while the concurrent RH campaign held its
lock; that process was left undisturbed. The first extension worker completed
its assertions but failed writing its result because its output directory was
not created. The original worker, manifest, log, native session and exit record
are preserved in attempt1_extension_output_directory. Adding mkdir corrected
the implementation; mathematical formulas were unchanged. Preliminary local
derivation scratch also hit a SymPy Boolean-to-int formatting error, corrected
by conditional counting; it supplied no retained numerical result.

Small manuscripts/code/figures are on the workstation. Sources, execution
receipts, failure records and outputs are on T500. Executed source/result
hashes are compared against the pod after completion. The full archive is
read back file-by-file and SHA-256 checked; CUSTODY.json names it. Pod originals
and T500 are separate copies; the archive on T500 is not another physical
replica. The pod remains rented and idle when this bounded work completes.
Chalkboard stays owner-suspended. No prime-event process is changed.
