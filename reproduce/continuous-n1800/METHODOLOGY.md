# Exact joint-density methodology

## Mathematical object and source family

For spins s_i in {-1,+1}, the recorded Hamiltonian and magnetization are

    E(s) = -Σ_{u<v} J_uv s_u s_v - Σ_i h_i s_i,
    M(s) = Σ_i s_i,
    g(E,M,b) = #{s : E(s)=E, M(s)=M, s restricted to ordered ports = b}.

Boundary bit i is one for spin +1 and zero for spin -1 at ordered_ports[i].
The boundary is a retained set of source vertices, not a spatial boundary
condition imposed on a square lattice. The exact ordered list is recorded for
**each case**. Small sources retain the available vertices; one must not assume
16 states for N<4. The usual four-port case has 16 states.

Every N has six labeled cases: packet, signed_packet, signed_packet_chain,
each with missing pairs filled by J0=+1 or J0=-1. Existing source couplings and
fields are preserved. Thus the completed graph contains N(N-1)/2 pair positions;
at N1800 there are 1,619,100. Six cases means six source/fill labels. Coincident
small-N constructions are not being counted as distinct graph isomorphism classes.

These are structured complete signed graphs. Their packet decomposition and
chain gateways are part of the computational input. The method's performance
is explained by that structure; the timing figures apply to these sources.

## Exact reduction of the dense interaction

Let J0 be the fill coupling. Separate the uniform complete-graph contribution:

    E(s) = C(s) - J0 (M(s)^2-N)/2,
    C(s) = -Σ_source_edges (J_uv-J0)s_u s_v - Σ_i h_i s_i.

The identity follows from M²=N+2Σ_{u<v}s_u s_v. In the chain family, source
edges between packets remain in C and are contracted through their gateway
spins. The planner verifies the vertex partition, the complete cross-edge list,
chain adjacency, and inclusion of the retained ports in the first packet.
An unexplained cross-edge is rejected, not discarded.

Write k=(M+N)/2 and let B be the sum of absolute correction couplings and fields.
The qualified integer source parity gives t=(C+B)/2 as a nonnegative integer.
Local enumeration stores exact counts by (k,t) and retained port state. Combining
packets convolves these coefficients; chain contractions retain gateway states
until their interactions have been included. Equal component tables can be reused.
The final conversion is

    M = 2k-N,
    E = 2t-B-J0*((2k-N)^2-N)/2.

See solver/baseline.py::plan, cpu_local and encode, solver/optimized.py and the
bound source records for the executable definitions. The publication's source
archive preserves all five production implementation generations, including
CONFIG, BUILD_ID and original source catalogs/indexed files.

## Two exact encodings and arithmetic

The same bivariate polynomial is evaluated in two Kronecker encodings:

    K_MAJOR: exponent = k*(B+1)+t,
    T_MAJOR: exponent = t*(N+1)+k.

The global bounds prevent overlap between encoded coordinates. Coefficients
are nonnegative arbitrary-precision integers. The CPU route uses FLINT integer
polynomials. The GPU route uses number-theoretic transforms modulo suitable
primes and Chinese-remainder reconstruction with a coefficient bound. This is
integer polynomial evaluation, not floating-point estimation of the density.
For each request, a bound C is formed from the product of sums of the
nonnegative factor coefficients, with multiplicities. Every output coefficient
is at most C. The kernel selects distinct transform-compatible primes until
their product Q exceeds C. CRT identifies an integer modulo Q uniquely; choosing
the representative in [0,Q) therefore recovers the original coefficient in
[0,C] exactly. No rounding-to-integer step is needed. The bound and prime list
are recorded in GPU request statistics. In the bound implementation, the count
bound is also checked against 2^N.

The counting identity behind composition is equally direct: each local table
counts configurations with specified k, correction energy and interface spins.
Multiplication enumerates Cartesian products of independent packet assignments;
convolution adds their k and correction coordinates. Summing compatible gateway
states includes each global assignment exactly once, after adding each bridge
energy once. Thus coefficient extraction preserves the joint counts. Integer
source terms have C(s) congruent to B modulo2, because changing a spin product's
sign changes its contribution by an even integer. This establishes the integral
t-coordinate used by the encoding.

The original GPU/CRT implementation and its checks are in the source bundle;
solver/gpu.py and solver/kernels.cu expose the numerical kernel used above N1408.

Both routes produce the canonical sorted (E,M,count) stream. K_MAJOR and T_MAJOR
must agree in all retained mathematical rows and canonical hashes. The encodings
exercise different indexing, while sharing source construction and much of the
implementation. They are not two unrelated algorithms. Separate exhaustive
spin enumeration is enabled through N10 in the original qualification/production
configuration; closure identities and analytic moments apply at every size.

## Checks at each boundary and each N

If p ports are fixed, each boundary has exactly 2^(N-p) configurations. If b
contains u positive fixed spins, the magnetization marginal is

    Σ_E g(E, 2(k+u)-N, b) = binomial(N-p,k),  0<=k<=N-p.

Summing boundary configuration counts gives 2^N. These are exact integer checks.
For fixed port spins s_a, set

    C_b = -Σ_a h_a s_a - Σ_{a<a'} J_aa' s_a s_a',
    H_i = h_i + Σ_a J_ia s_a  (i free).

A uniform average over free spins gives

    Σ E*g = 2^(N-p) C_b,
    Σ E²*g = 2^(N-p) [C_b² + Σ_free_i H_i² + Σ_free_i<j J_ij²].

The runner independently constructs these moments from the graph and compares
them to decoded coefficients. It also records magnetization and mixed moments,
source/plan/graph hashes, joint support sizes, build identity and boundary order.
These checks are performed before releasing each expanded table from memory.

## Canonical data and retention

The canonical stream begins with SAM_GEMB_CANON_V1, a four-byte little-endian
JSON-header length, and the header. Its declared row order is boundary, E, M,
each ascending. Coefficients use unsigned fixed-width little-endian counts of
floor(N/8)+1 bytes; E and M in the canonical format use signed int64. The exact
boundary framing is implemented in fast_cpu.pyx::canonical (and the predecessor
Python implementation). Use that implementation when regenerating hashes.

The hypothetical-output metric in receipts uses a **different**, headerless
comparison format: int32 E, int32 M and the same count width, in both encodings.
It is a calculated byte count, not disk space actually consumed or published.

For most N, full coefficients exist in RAM, are decoded, checked, reduced and
hashed, and then released. Original RECORD.json.gz and RECEIPT.json files retain
canonical hashes, exact support and moments, source identities, regeneration
plans, response summaries and resource measurements. The release publishes
these compact scientific records for **every N1–1800**. A compact record is not
an expanded list of every (E,M,count) coefficient.

Selected full-output milestones are listed in SUMMARY.json. Those existing
large tables have separate custody. They are not silently included in the compact
release assets. The isolated N2000/3000/4000/5000 packages retain their own full
output formats, inventories, reproduction commands and access status.

## Derived responses

The exact joint object supports reweighting by uniform field h, collective-pair
shift g, and fields λ_a on retained ports without recomputing the count:

    E_new = E - h M - g(M²-N)/2 - Σ_a λ_a s_a,
    Z_b(β,h,g) = Σ_{E,M} g(E,M,b) exp[-β(E-hM-g(M²-N)/2)].

The retained production reductions include zero-temperature response summaries
and thermal readouts at β=1/N and 4/N, h=g=0, in formal source units. Thermal
expressions use 128-bit Arb interval arithmetic; their interval endpoints are
not exact integer densities. Boundary free energies F_b=-log(Z_b)/β can be
expanded in the full Walsh basis of retained spins:

    J_A^eff = 2^(-p) Σ_b F_b Π_{a in A}s_a(b).

Every subset, including the constant and higher-order interactions, is retained
in the production boundary expansion. Temperature/readout scope is recorded.

## Execution and resource accounting

N1–100 and N101–500 used CPU/FLINT. N501 onward used one shared exact GPU service
and CPU consumers. Shared-memory coefficient transfers, one outstanding result
per consumer and a 48-GiB cache budget bound the queued GPU work. No coefficient
queue is written to disk. Per-N source loading in the final extension avoids
loading all larger source catalogs in every worker. Compiled CPU loops accelerate
decode, serialization and unchanged readout reductions.

The final N1745–1800 batch used 28 CPU workers and one RTX PRO6000 Blackwell
Workstation GPU. It completed 56 sizes, 336 cases and 10,752 service solves in
9,039.131238 seconds. Its measured maximum worker-lifetime RSS was 3,538,919,424
bytes. This is a maximum for one worker, including its lifetime cache/history;
it is not aggregate machine RAM. Batch time includes calculation and retained
file work; external transfers, publication and provider shutdown are separate.

The earlier 24-worker N1745–1800 attempt was stopped before any size finished.
The completed 28-worker attempt was later reattached to a new collection controller
without restarting its workers. It finished before the extended cutoff. Completed
batch data were independently hash-verified on the T500 before workstation
copies were removed; native results, checkpoint/export and final T500 custody
preceded provider stop. See evidence/ for immutable completion receipts.
