# Global continuous ordering onset for the retained families

New derivation by Codex in the Sean Brady / ChatGPT / Codex collaboration.
Continuation of spin_normalization1; archived unit-fill and whole-scaled
Hamiltonians are unchanged. The theorem below concerns the explicit extension

\[
 H_{N,\kappa}=-\frac{M^2-N}{2N}+\kappa C_N,\qquad \kappa\ge0,
 \quad N=20+30m\longrightarrow\infty.
\]

Here \(M=\sum_i s_i\), and \(C_N=2\sum_{\text{negative edges}}s_i s_j\)
for the retained signed sources. The packet source has \(C_N=0\).
\(\beta>0\) is inverse temperature in the declared model units, and the
dense coefficient is fixed at \(J=1\). This is not the model obtained by
rescaling only missing-edge fill while keeping every original bond fixed.

## 1. Thermodynamic reduction

Let \(F(y)\) be the partition function of one repeated correction component
in external field \(y\), with Boltzmann factor
\(\exp[y\sum s_i-2\beta\kappa\sum_{\rm neg}s_i s_j]\).
The component contains \(n=15\) spins for packet/signed packet, or \(n=30\)
for the chain. A finite root and tail complete the source. The exact Gaussian
identity retained in spin_normalization1 gives the limiting variable part of
the pressure as

\[
 \sup_{y\in\mathbb R}\Phi_{\beta,\kappa}(y),\qquad
 \Phi(y)=-\frac{y^2}{2\beta}+\frac1n\log\frac{F(y)}{F(0)}.
\]

The finite root/tail change \(\log Z\) by only \(O(1)\) on each compact
field interval. All factors are positive for real fields. Moreover,
\(F(y)/F(0)\le e^{n|y|}\), giving Gaussian domination outside compact sets.
Upper/lower Laplace bounds therefore yield the stated supremum. The fixed
boundary conditions likewise do not change this limiting bulk maximization.
They remain fully present in finite boundary weights and memory readouts.

Define the motif magnetization per spin and its zero-field susceptibility:

\[
 m_0(y)=\frac1n\partial_y\log F(y),\qquad \chi=m_0'(0).
\]

At every stationary point, \(y=\beta m_0(y)\). Since
\(|m_0(y)|\le1\), every maximizer satisfies \(|y|\le\beta\).
The macroscopic magnetization of an extremal state is \(m_*=y_*/\beta\).

## 2. Exact rational field responses

Put \(a=\tanh(2\beta\kappa)\in[0,1)\), \(v=\tanh y\), and
\[
 P(a,v)=1+(-a^3+2a^2-3a)v^2+a^2v^4.
\]
Removing field-independent constants, the repeated factors are

\[
 F_{\rm packet}(y)\propto\cosh^{15}y,
\]
\[
 F_{\rm signed}(y)\propto\cosh^{15}y(1-av^2)^3,
\]
\[
 F_{\rm chain}(y)\propto\cosh^{30}y(1-av^2)^4P(a,v).
\]

For example, with \(q=e^{-4\beta\kappa}=(1-a)/(1+a)\), the four-spin
path factor is proportional to
\(q^3\cosh4y+2(q^2+q)\cosh2y+q^2+q+1\).
Substituting the double-angle formulas gives \(\cosh^4y\,P(a,v)\) times
a positive constant. Consequently \(P(a,v)>0\) for \(|v|<1\), including
the limiting \(a=1\), where \(P=(1-v^2)^2\).

Writing \(G=(1-av^2)^3,n=15\) or
\(G=(1-av^2)^4P,n=30\), respectively,

\[
 m_0(y)=v+\frac{1-v^2}{n}\frac{\partial_vG}{G}.
\]

The exact source polynomial equality is checked using
\[
 B(X,U)=1+2XU+X^2,
\]
\[
 A(X,U)=1+X^4+2(X+X^2+X^3)(U+U^2)+2X^2U^3.
\]
The signed15 factor equals \(B^3(1+X)^9\), and the chain30 factor equals
\(AB^4(1+X)^{18}\), with \(U\) counting disagreeing negative edges.
The retained source's aligned index is converted exactly by \(d=L-t\).

## 3. Global bound from a finite rational certificate

Let
\[
 S_4(x)=1+x/3+x^2/5+x^3/7+x^4/9.
\]
For both signed motifs the following identity defines a polynomial
\(Q_f(a,x)\), where \(x=v^2\):

\[
 \chi S_4(v^2)-\frac{m_0(y)}v
 =\frac{v^2Q_f(a,v^2)}{D_f(a,v)}.
\]

Here
\[
 D_{\rm signed}=1575(1-av^2),\qquad
 D_{\rm chain}=4725(1-av^2)P(a,v).
\]
Both denominators are positive on \(0\le a\le1,0\le v<1\).
The degrees of \(Q\) in \((a,x)\) are \((2,4)\) and \((7,6)\).
Their full integer power-basis coefficients and exact rational Bernstein
coefficient matrices are retained in **THEOREM.json**.

For completeness, the certificate conversion is explicit. If
\(Q(a,x)=\sum c_{rs}a^rx^s\) has bidegree \((d,e)\), then
\[
 b_{ij}=\sum_{r\le i,s\le j}c_{rs}
 \frac{\binom{i}{r}}{\binom{d}{r}}
 \frac{\binom{j}{s}}{\binom{e}{s}}.
\]
All \(b_{ij}\) are nonnegative rational numbers. Direct exact expansion
of \(\sum b_{ij}\binom di a^i(1-a)^{d-i}\binom ejx^j(1-x)^{e-j}\)
reconstructs \(Q\) coefficient-for-coefficient. The Bernstein basis is
nonnegative on the unit square, so \(Q\ge0\) there. This is a finite
algebraic certificate over the entire parameter square, not sampled positivity.

For \(0<v<1\), the strictly positive Taylor remainder gives
\[
 \frac{\operatorname{atanh}v}{v}
 =\sum_{j\ge0}\frac{v^{2j}}{2j+1}>S_4(v^2).
\]
Since \(\chi\ge3/5>0\), it follows that
\[
 \boxed{m_0(y)<\chi y\quad\text{for every }y>0.}
\]
For the packet source this is simply \(\tanh y<y\).

The bound is deliberately weaker than global concavity of \(m_0\), which
is false. THEOREM.json retains exact positive values of \(m_0''(y)\) for
both signed families at \(a=49/50,v=24/25,y=\log7\). Thus the stronger
shortcut is excluded by an arithmetic counterexample and is not used.

## 4. The actual ordering transition

The retained susceptibilities, now with \(a=-t\), are
\[
 \chi_{\rm packet}=1,\quad
 \chi_{\rm signed}=1-2a/5,\quad
 \chi_{\rm chain}=(30-14a+4a^2-2a^3)/30.
\]
For every fixed finite \(\kappa\ge0\), let \(\beta_c\) solve
\(\beta_c\chi(\beta_c,\kappa)=1\).
The monotonicity bound from spin_normalization1 gives a unique solution in
\([1,5/3]\), strictly inside for finite positive \(\kappa\).
The two signed families can also be ordered exactly:
\[
 \chi_{\rm chain}-\chi_{\rm signed}=-a(1-a)^2/15\le0.
\]
Therefore \(\beta_{c,\rm chain}\ge\beta_{c,\rm signed}\), strictly for
finite positive \(\kappa\). Both tend to \(5/3\) as \(\kappa\to\infty\).

If \(\beta\chi\le1\), then for every \(y>0\)
\[
 \Phi'(y)=m_0(y)-y/\beta
 <(\chi-1/\beta)y\le0.
\]
Evenness makes zero the unique global maximizer, including at equality.
There is no distant state that pre-empts the zero-field threshold.

If \(\beta\chi>1\), then \(\Phi''(0)>0\), so zero is not a maximum
and some nonzero \(\pm y_*\) attain strictly larger pressure. Hence
\(\beta_c\) is the global ordering onset for every fixed \(\kappa\).

To establish continuity, take \(\beta\downarrow\beta_c\) and any global
maximizers \(y_*(\beta)\). They lie in a common compact set by
\(|y_*|\le\beta\). Every subsequential limit maximizes \(\Phi\) at
\(\beta_c\), whose maximizer is uniquely zero. Thus \(y_*\to0\).

The exact motif fourth cumulants retained in spin_normalization1 are strictly
negative for all \(a\in[0,1]\). Let \(c_4\) denote the fourth cumulant
per spin, and \(r(\beta)=\chi(\beta,\kappa)-1/\beta\). Near onset,
\[
 \Phi'(y)=r y+c_4y^3/6+O(y^5),\qquad
 y_*^2=-6r/c_4+O(r^2).
\]
The already established positive derivative of \(\beta\chi\) at crossing
makes this a nondegenerate continuous square-root onset. This classifies the
first ordering transition; it does not claim a census of all stationary points
arbitrarily far above it.

### Critical finite-size amplitude

At the exact critical temperature, put \(b=-c_4/24>0\). The preceding
global uniqueness and negative quartic coefficient imply
\(\Phi(y)=-by^4+O(y^6)\). Finite root/tail prefactors are smooth and
strictly positive at zero. Splitting the integral into a fixed neighborhood
of zero and its complement, global uniqueness gives an exponential gap on
the compact complement, and the Gaussian bound controls the distant tail.
Inside the neighborhood, \(\Phi(y)\le-by^4/2\) after reducing its radius.
Thus dominated convergence under \(u=N^{1/4}y\) applies to both zeroth and
second moments. Since
\(\int_0^\infty u^r e^{-bu^4}du=\tfrac14b^{-(r+1)/4}\Gamma((r+1)/4)\),
\[
 \boxed{\sqrt N\,\langle(M/N)^2\rangle\longrightarrow
 \frac{\sqrt{24/(-c_4)}}{\beta_c^2}
 \frac{\Gamma(3/4)}{\Gamma(1/4)}.}
\]
The auxiliary-Gaussian subtraction \(\beta_c/N\) is lower order here.
This statement uses the exact \(\beta_c\); the finite map's rounded rational
temperature centers are explicitly distinguished from it.

### Boundary-memory limit below and at onset

Let \(R_b(y)\) be the original fixed-boundary root factor, including its
correction Boltzmann weights. Below and at \(\beta_c\), the common-factor
integral concentrates at zero, so
\[
 \boxed{Z_b/Z_0\longrightarrow R_b(0)/R_0(0).}
\]
The proof follows from the same Laplace localization: the root is a finite
positive analytic factor, and its value at zero multiplies the common leading
integral. The finite tail and common factor normalization cancel in the ratio.
Every generator entry, matrix exponential and declared protocol readout is
continuous in these strictly positive weights. Therefore the complete
three-part boundary-memory limit is obtained by applying the unchanged
protocol directly to \(R_b(0)/R_0(0)\). This is an exact finite-source
limiting expression, with no enormous-N numerical extrapolation.

Just above onset, the previously derived unique local maximizing pair gives
the analogous ratio of even root factors
\([R_b(y_*)+R_b(-y_*)]/[R_0(y_*)+R_0(-y_*)]\).
At the onset itself, LIMITS.json evaluates the zero-field expression and the
critical amplitude with directed Arb intervals. For finite \(\kappa>0\)
the local corrections can therefore retain a nonzero boundary-memory limit.

## 5. Finite transition map and exact occupied windows

The finite map preserves the complete Gaussian integral and its explicit
tails from spin_normalization1. All sampled \(\beta<1.8\), so the same
cutoff4 bounds apply. Finite systems are smooth; measured finite-size curves
are compared to the exact infinite-volume transition, not declared singular.
The boundary root and the declared one-third heat-bath clock are retained.

To target exact counts, use the aligned index \(t=L-d\). At zero field a
negative edge has aligned probability \(1/(1+e^{4\beta\kappa})\). This
motivates the windows but is not substituted for their finite Gibbs mass.
The measured mass uses every selected exact count and complete certified Z.

Reversing the defect variable in the chain motif gives
\(\widehat F(X,U)=U^7F(X,U^{-1})\), whose constant term is
\(\widehat f_0=32X^6\). The same exact coefficient recurrence becomes
\[
 q_0=(32X^6)^m,\qquad
 n\widehat f_0q_n=\sum_{i=1}^7((m+1)i-n)\widehat f_iq_{n-i}.
\]
Every polynomial division is checked to have zero remainder. Only16 or24
steps are needed for the chosen windows, instead of thousands of central
defect steps. The remaining pair is \(2X+(1+X^2)U\), followed by the
unchanged free-spin factor and exact boundary root. The GPU uses the retained
original defect encoding and independent modular transforms, so matching
their intermediate coefficients also verifies the variable reversal.

For any selected window \(W\),
\[
 P(W)=Z^{-1}\sum_{(k,t,b)\in W}g(k,t,b)
 e^{\beta((2k-N)^2-N)/(2N)-\beta\kappa(4t-2L)}.
\]
The exact original energy remains
\(E=4t-2L-((2k-N)^2-N)/2\). Both captured and omitted probability are
retained as directed intervals. Count-file hashes, all coordinates, source
identities, timers and independent checks accompany the results.
