# Free/core ratio and transition type

## 1. Objects, source and normalization

This is an additive extension of the pair and chain constructions in
`../spin_transition1/PROOF.md`. The Hamiltonian is the explicitly introduced
mixed normalization

\[
 H_N=-\frac{M^2-N}{2N}+\kappa C_N,\qquad
 C_N=2\sum_{\text{negative edges}}s_i s_j,\quad s_i\in\{-1,1\}.
\]

Here J=1, κ≥0 and β>0. “Free spins” have no sparse negative edge; they still
participate in the dense M² term. The whole-Hamiltonian normalization of the
archived J₀=±1 graph corresponds instead to κ=1/N. The results below concern
fixed κ as N grows, with each stated κ explicit.

The existing negative-pair polynomial and four-path polynomial, with X
counting up spins and U counting disagreements, are

\[
 B=1+2XU+X^2,
 \quad A=1+X^4+2(X+X^2+X^3)(U+U^2)+2X^2U^3.
\]

The pair core is B, n=2, one edge. The chain core is AB⁴, n=12,
seven edges: a four-spin path plus four disjoint pairs. Frozen N5000 source
factors reconstruct B³(1+X)⁹ and AB⁴(1+X)¹⁸ exactly. Both original families
therefore have free fraction f=3/5. The names refer to these actual components;
the chain core is not a path of twelve spins.

Keep the finite root and tail unchanged. With q core copies and F free spins
per new cell, repeat it r times:

\[
 Q_b=R_b B(1+X)^3[C^q(1+X)^F]^r,
 \quad N=20+r(nq+F),\quad f=\frac F{nq+F},
\]

where C=B or AB⁴. Every rational f∈[0,1) has an integer realization (take
q=d-p,F=np for f=p/d and reduce). f=1 uses only free bulk spins. This specifies
new graph families while preserving the original finite boundary. The root
and tail contribute O(1) to log Z at fixed β and field; they do not change the
bulk variational pressure. Their finite-size boundary readouts remain defined,
but have not been recomputed for these ratios in this campaign.

## 2. Exact pressure and response

Put a=tanh(2βκ), v=tanh y and q₀=e⁻⁴ᵝκ=(1-a)/(1+a). The normalized core
partition functions are

\[
 B_y=\frac{1+q_0\cosh(2y)}{1+q_0},\qquad
 A_y=\frac{q_0^3\cosh(4y)+2(q_0^2+q_0)\cosh(2y)+q_0^2+q_0+1}
 {(1+q_0)^3}.
\]

Thus ψ_int=(log B_y)/2 for pairs and (4log B_y+log A_y)/12 for chains.
For any ratio, ψ_f=f log cosh y+(1-f)ψ_int, normalized to zero at y=0.
Completing the Gaussian square in exp(βM²/(2N)) gives the exact finite-N
Hubbard–Stratonovich integral. Taking its Laplace limit yields the excess
pressure max_y Φ_f(y), where

\[
 \Phi_f(y)=-\frac{y^2}{2\beta}+\psi_f(y),\qquad
 \Phi'_f(y)=m_f(y)-y/\beta.
\]

All core terms are finite positive sums. Uniformly on compact parameter sets,
ψ_f(y)≤|y|, hence Φ→−∞ quadratically. A maximizer has physical magnetization
m=y/β. The pressure is even. The normalized finite root cannot change the
bulk maximizing set.

Define P(a,v)=1+(-a³+2a²-3a)v²+a²v⁴. Then

\[
 m_{\rm int,pair}=\frac{(1-a)v}{1-av^2},\quad
 m_{\rm int,chain}=v+\frac{1-v^2}{12}\partial_v
 \log[(1-av^2)^4P(a,v)],\quad
 m_f=fv+(1-f)m_{\rm int}.
\]

The denominators are positive for 0≤a<1, |v|<1, as also follows from the
positive partition sums. The per-core-spin cumulants χ_int,c₄,int,c₆,int are:

| Core | χ_int | c₄,int |
|---|---|---|
| Pair | 1-a | −2(a−1)(3a−1) |
| Chain | −(a−1)(a²−a+6)/6 | −(a−1)(3a⁵−9a⁴+21a³−19a²+22a−6)/3 |

Pair c₆,int=−8(a−1)(15a²−15a+2). Chain c₆,int is

\[
 -\frac43(a-1)(15a^8-75a^7+240a^6-450a^5+570a^4
 -450a^3+257a^2-107a+12).
\]

They follow by repeated application of (1-v²)∂_v to m_int. Independent
enumeration of every 2-spin/12-spin core checks all three cumulants at five
rational a values. Mixture cumulants are exactly

\[
 \chi=f+(1-f)\chi_{\rm int},\quad c_4=-2f+(1-f)c_{4,\rm int},
 \quad c_6=16f+(1-f)c_{6,\rm int}.
\]

Writing r₀=χ−1/β, the local pressure is
Φ=r₀y²/2+c₄y⁴/24+c₆y⁶/720+O(y⁸), with analytic parameter dependence.

## 3. Two exact tricritical points

At a=1/2, the core cumulants are (1/2,1/2,−7) for pairs and
(23/48,77/192,−2231/384) for chains. Solving c₄=0 and βχ=1 gives:

| Family | f_t | β_t | κ_t | c₆ at the point |
|---|---|---|---|---|
| Pair | 1/5 | 5/3 | 3 log 3 /20 | −12/5 |
| Chain | 77/461 | 461/261 | 261 log 3 /1844 | −999/461 |

Minimal cells are two pairs plus one free spin (5 spins), and 32 chain cores
plus 77 free spins (461 spins). Their interacting fractions are 4/5 and
384/461. These are specific points of a parameter-dependent phase diagram,
not universal ratio thresholds for every κ, and not thresholds asserted at κ=1.

### Global exclusion of a remote competing maximum

Set S₄(v)=1+v²/3+v⁴/5+v⁶/7+v⁸/9. For y=atanh v>0,
y/v>S₄(v). At the pair point,

\[
 \chi S_4-m_f/v=
 \frac{v^4(21+27v^2+25v^4-35v^6)}{525(2-v^2)}.
\]

The numerator Q(x), x=v², has Bernstein coefficients
[21,30,142/3,38] on [0,1], all strictly positive. At the chain point,

\[
 \chi S_4-m_f/v=
 \frac{v^4(4662+83v^2-29v^4-13079v^6+10585v^8-2030v^{10})}
 {16135(2-v^2)(2v^4-9v^2+8)}.
\]

The degree-five Bernstein coefficients of this Q(x) are
[4662,23393/5,46923/10,16976/5,7982/5,192], all positive.
Both denominators are positive for 0≤v≤1; for the chain quadratic this
follows from its decreasing derivative and value 1 at x=1. Exact expansion
back to the power basis independently checks both coefficient lists.
Consequently m_f(y)<χy for every y>0. At β_tχ=1 this implies Φ'(y)<0.
Zero is the unique global maximizer, with a strictly stabilizing sixth term.

### No earlier transition, and the continuous side of ratio variation

EXTENSION.json strengthens each point identity to the whole rectangle
0≤a≤1/2,0≤v²≤1, at f=f_t. It records the exact rational polynomial
v²p(2a,v²)/D(a,v) for χS₄−m_f/v. The pair polynomial has degrees (2,4)
and the chain polynomial (7,6). All 71 tensor Bernstein coefficients are
nonnegative, with exact reconstruction. Their denominators are positive.
The strictly positive remainder y/v−S₄ still gives m_f(y)<χy for y>0.

At fixed κ_t, β≤β_t implies a≤1/2. Also

\[
 \frac{d(\beta\chi)}{d\beta}
 =\chi+(1-a^2)\operatorname{atanh}(a)\chi_a
 \ge \chi_t-(1-f_t)d\log(3)/2>0,
\]

where d=1 for pairs and d=7/6 for chains. Indeed χ decreases with a,
χ≥χ_t, and |χ_a|≤(1-f_t)d on this interval. Both lower bounds are
certified positive with 192-bit Arb. Therefore βχ<1 for every β<β_t:
Φ'<0 on y>0 throughout that range. The tricritical point is the first
ordering onset when cooling at its stated f_t,κ_t.

For every f≥f_t at the same κ_t, m_f is a convex combination of m_f_t and
tanh y, and χ is the matching convex combination of χ_t(a) and 1.
The same strict global bound and monotonicity apply until β_t. A unique
β_c≤β_t solves β_cχ=1. For f>f_t, c₄<0 there: the old component's c₄≤0
follows from the global bound near y=0, and the added free component has −2.
Thus the first ordering onset is continuous with the usual square-root law.
This includes each retained 60%-free construction at the specified κ_t.

### Ratio variation supplies a genuine tricritical unfolding

Hold κ=κ_t fixed and use (β,f) as the two parameters. At each point r₀,β>0,
and the Jacobian det ∂(r₀,c₄)/∂(β,f) is strictly negative:

| Family | r₀,β | Jacobian |
|---|---|---|
| Pair | 9/25−9log3/50 | −9/10+27log3/100 |
| Chain | (68121−36018log3)/212521 | −22707/29504+1684233log3/6800672 |

Arb encloses both signs strictly. The map to (r₀,u=c₄) is locally invertible.
The quartic along r₀=0 has derivative Jacobian/r₀,β<0 with respect to f.
Hence f just below f_t gives u>0 at the local-instability curve; f just above
gives u<0. The negative sixth coefficient supplies stability.

For completeness, write t=y² and c=c₆,t<0. A nonzero stationary phase with
the same pressure as zero solves

\[
 0=r_0+ut/6+ct^2/120+O(t^3),\qquad
 0=r_0/2+ut/24+ct^2/720+O(t^3).
\]

For u>0 set t=uT, r₀=u²R and apply the implicit-function theorem at
T=−15/c,R=5/(8c); the two-equation Jacobian in (R,T) is nonzero.
This yields

\[
 y_*^2=-15u/c+O(u^2),\qquad r_0=5u^2/(8c)+O(u^3)<0.
\]

Both zero and ±y_* are local maxima on this coexistence curve. The second
derivative at y_* has leading value u t/3+c t²/30=5u²/(2c)<0.
The intervening nonzero stationary branch is a local minimum. The leading
coexistence polynomial factors as (c/720)t(t+15u/c)²≤0. Analytic
remainders and the implicit-function theorem preserve this local maximum
structure and its unique equal-pressure curve for sufficiently small u>0.

There are no distant maxima to pre-empt these nearby phases: at the exact
point Φ<0 away from zero; on every compact annulus this has a uniform
negative gap, and quadratic coercivity handles the tails uniformly in a
parameter neighborhood. For β in a compact subset strictly below β_t the
preceding global certificate gives the same gap and strictly negative local
curvature, stable under sufficiently small ratio changes. β≤1 is globally
disordered for every ratio: both antiferromagnetic core factors decrease
relative to coshⁿ y, so ψ_f≤log cosh y≤y²/2. These facts also exclude an
earlier remote onset as f approaches f_t from below. Thus, for all f<f_t
sufficiently close to f_t, cooling at κ_t has a first-order ordering onset.

Exactly at f_t, along κ_t and β=β_t+δ with δ↓0,

\[
 y_*\sim\left(\frac{-120 r_{0,\beta}}{c_{6,t}}\delta\right)^{1/4},
 \qquad m_*\sim y_*/\beta_t.
\]

This gives the tricritical fourth-root law. The exact coefficients establish
the local unfolding; the numerical offsets in RESULTS.json explore its shape
without assigning a rigorous radius to “sufficiently close.”

### Finite-size and boundary corollaries

At either exact point, put d=−c₆,t/720>0. The unique global maximum and
negative sixth coefficient give, after y=N^(−1/6)z, the limiting density
proportional to exp(−dz⁶). The fixed root/tail supplies a positive smooth
factor at zero. It cancels in normalized leading moments. Taylor remainders
are uniform near zero; the global gap and coercivity above bound the remaining
integral, justifying the rescaling by dominated convergence. Thus

\[
 N^{1/3}\left\langle(M/N)^2\right\rangle\ \longrightarrow\
 \frac{1}{\beta_t^2}\left(\frac{720}{-c_{6,t}}\right)^{1/3}
 \frac{\Gamma(1/2)}{\Gamma(1/6)}.
\]

One can transfer the auxiliary-field moment exactly: conditioned on the spin
configuration, the Hubbard–Stratonovich field is Gaussian with mean βM/N
and variance β/N. Hence ⟨(M/N)²⟩=⟨y²⟩/β²−1/(βN); the subtracted term
vanishes after multiplication by N^(1/3). Integer cells give f_N=f_t+O(1/N),
which also leaves the leading sixth-order limit unchanged.

For the preserved boundary root, Z_b/Z_0 tends to R_b(0)/R_0(0), with R
evaluated at the actual sparse Gibbs coupling. Both points have
β_tκ_t=log3/4. Therefore their limiting equilibrium boundary distributions
are identical, since their root and root coupling are identical. This is a
statement about equilibrium weights. Any claim about finite-time memory
must still apply the specified transition rates and protocol. The bulk
finite-size power has changed from N^(−1/2) at ordinary criticality to
N^(−1/3) here, furnishing a concrete next finite-size check.

## 4. Separate global first-order witnesses

At f=0,κ=1/5 the pair susceptibility is 1−tanh(2κβ). For all β>0,

\[
 \beta\chi_{\rm pair}\le2\beta e^{-4\kappa\beta}
 \le\frac1{2\kappa e}=\frac5{2e}<1.
\]

The chain susceptibility is smaller by a(1−a)²/6, so zero remains strictly
locally stable for both families at every β. Nevertheless directed Arb
evaluation gives Φ(4)>0.04161255 for the pair at β=4 and
Φ(12)>0.11251009 for the chain at β=12. Literal spin enumeration independently
agrees with the factor evaluation. Both families are disordered for β≤1 as
above. Continuity and coercivity give a first global onset between β=1 and
the stated witness. On that compact β interval the uniform bound βχ<1
keeps curvature at zero strictly negative; emerging maximizing states stay
away from zero. Hence that onset is discontinuous. Its precise temperature
was not needed or determined by this witness argument.

## 5. Useful counterexample and remaining measurements

For pairs c₄=−2+(1-f)(8a−6a²), so positive quartic is possible only when
f<1/4. At f=1/4,a=2/3 the quartic vanishes but c₆=4/3>0. This is not a
stabilized sixth-order tricritical point. The extra global and sixth-order
checks above are essential to the classification, not an arbitrary condition.

The derived thermodynamic results apply at all growing cell counts. This
campaign does not expand g(E,M,b). Finite-size boundary memory, metastable
barrier heights and exact coefficient windows across these new transitions
are not yet calculated. The highest-value next calculation is the finite-N
boundary-memory readout on the two sides of the chain tricritical point,
using the newly explicit source factors and the existing root/protocol.
