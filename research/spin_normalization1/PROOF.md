# Explicit normalization comparison and finite-source identities

New derivation by Codex, following Sean's authorization to execute the proposed
coefficient-batching and normalization campaign. Prior model/results are unchanged.

## Models and reusable counts

Let M=sum_i s_i and C_N=sum_original(1-J_ij)s_i s_j for the retained
positive-fill source. In the signed families C_N=2 sum_negative s_i s_j.
The archived Hamiltonian is H_old=-(M^2-N)/2+C_N. Its beta=c/N Gibbs
measure is exactly that of H_old/N at inverse temperature c.

We now define, explicitly, H_{N,kappa}=-(M^2-N)/(2N)+kappa*C_N at inverse
temperature beta. Thus kappa=1/N recovers the previous normalization;
kappa=1 keeps the sparse correction order one. This extension is not the
operation of keeping all original +/-1 bonds while rescaling only missing-edge
fill. Original positive edges would then also require new correction terms.

Every retained count g(E,M,b) supplies C=E+(M^2-N)/2. Consequently

    Z_b(beta,kappa)=sum_{E,M} g(E,M,b)
                    exp[beta*(M^2-N)/(2N)-beta*kappa*C].

No coupling-specific recounting is necessary. If only a window W is available,
the same sum divided by the complete Z gives its exact Gibbs probability.
No uncomputed part of the spectrum is silently assigned zero probability.

## Exact finite-source integral and complete normalization

Decode every source row into (k,t,count) with its original stride. A component
of n spins supplies F(y)=sum count*exp((2k-n)y-2*step*beta*kappa*t).
The original correction is C=2*step*T-bound_N, with T the sum of component
t indices, including the boundary root. For signed sources step=2 and
bound_N=2L; packet has bound_N=0. Repeated powers are changed only by the
retained N=20+30m continuation; the root has15vertices and4fixed spins.

Gaussian integration of exp(beta*M^2/(2N)) gives exactly

    Z_b = exp(-beta/2+beta*kappa*bound_N)*sqrt(N/(2*pi*beta))
          integral_R exp(-N*y^2/(2*beta)) R_b(y) prod_i F_i(y)^m_i dy.

The common factors are even. Replacing the root by
(R_b(y)+R_b(-y))/2 and integrating twice over y>=0 is exact, including for
fixed boundary states. Positive source weights permit grouping by |2k-n| into
cosh terms. Normalize each factor and root by its value at y=0; these constants
are included in pressure and boundary weights, not dropped. The implementation
subtracts an arbitrary common integer exponent shift solely for conditioning.

For y>=Y=4 and all beta in {1,7/5,9/5}, every normalized n-spin factor is
<=exp(n*y). Their product, including root, is <=exp(N*y). Put

    a=N*(Y/beta-1)>0,
    v=-N*Y^2/(2*beta)+N*Y-shift.

Concavity of the Gaussian exponent then bounds the omitted integrals by

    T0 <= exp(v)/a,
    T2 <= exp(v)*(Y^2/a+2Y/a^2+2/a^3).

The second bound follows by integrating (Y+u)^2 exp(-a*u). Both are added
as outward Arb error radii. Finite-panel quadrature uses acb.integral with
analytic-branch checks. These bounds include all omitted y, for every root.

The Gaussian auxiliary variable conditional on spins has mean beta*M/N and
variance beta/N. Hence the full, boundary-summed magnetization moment is

    <(M/N)^2> = (<y^2>-beta/N)/beta^2.

This furnishes a second thermal consumer without expanding the spectrum.
All boundary weights enter the existing heat-bath/readout protocol unchanged;
its one-third intervals remain a declared model clock.

## Exact infinite-volume local susceptibility

The correction components are independent at zero mean field. Write
t=-tanh(2*beta*kappa). A negative pair has spin covariance t. On a negative
four-spin path, covariance at graph distance r is t^r: summing the endpoint
spin successively gives the conditional factor t at each edge.

One signed-packet15 motif contains9free spins and3negative pairs. One
chain30 motif contains18free spins,4negative pairs and a four-spin path.
The finite root/tail contribute O(1) to the log partition; the following
limiting susceptibilities are per spin:

    chi_packet = 1,
    chi_signed = 1 + 2*t/5,
    chi_chain  = (30+14*t+4*t^2+2*t^3)/30.

These formulas also follow by exact differentiation of the frozen component
polynomials, independently of the covariance argument.

The limiting HS exponent has quadratic coefficient
(chi-1/beta)/2. Therefore its zero-field stationary point changes local
stability precisely at beta*chi(beta,kappa)=1. For fixed kappa>=0 there
is exactly one such value in [1,5/3]. For kappa>0 finite it lies strictly
inside that interval. Indeed chi is between3/5 and1. Its t derivative is
2/5 for signed packets and (14+8t+6t^2)/30<=7/15 for chains. Since
s*sech(s)^2<=1/2 (cosh(s)^2>=1+s^2>=2s),

    d(beta*chi)/d beta >= 3/5 - (7/15)/2 = 11/30 > 0

for chains, and >=2/5 for signed packets. Endpoint values give existence.
The packet value is beta=1. In the whole-scaled sequence kappa=1/N, t tends
to zero, so both signed families also have limiting local threshold beta=1.

## Quartic coefficient: local bifurcation direction

Exact fourth cumulants of one repeated component are

    packet: -30,
    signed: -(36*t^2+48*t+30),
    chain: -(12*t^6+48*t^5+120*t^4+160*t^3+164*t^2+112*t+60).

The signed bracket is36*(t+2/3)^2+14. For chains set u=-t in[0,1].
The degree6 Bernstein coefficients of the bracket are

    [60,124/3,168/5,144/5,404/15,28,36].

All are positive and the Bernstein basis is nonnegative with sum one.
Thus the quartic coefficient is strictly negative for every kappa>=0.
The local symmetry-breaking branch at the instability is continuous. This
local argument alone does not exclude a competing distant maximum before
that point; global phase classification remains a separate question.

## Relation to the enormous-N result

The whole-scaled model has |C_N|<=2L=O(N). At bounded beta its perturbation
changes log Z by at most2*beta*L/N=O(1), and pressure log Z/N by O(1/N).
At fixed kappa the same bound is O(N) for log Z and O(1) for pressure.
The susceptibility formulas exhibit explicitly how order-one local corrections
enter the limiting quadratic response. The finite normalization comparison
tests the associated boundary and magnetization responses on the retained
source families; no new physical time calibration is supplied.
