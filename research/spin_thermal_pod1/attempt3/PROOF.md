# Exact quadratic cancellation with bounded series remainders

This is a new numerical derivation for this campaign. It retains the source and
integral derived in spin_families1; no asymptotic replacement is made.

## 1. Split the finite factors exactly

For an unrestricted component of n spins, the sum of its exact table counts
at fixed k is binomial(n,k), independently of the correction-energy index t.
The implementation checks this integer identity for every input factor.
With beta=c/N, put

    delta_n(x)=2^-n sum_(k,t) count(k,t)
                 [exp(-2 step beta t)-1] cosh((2k-n)x).

Spin reversal has already justified the even form. The binomial identity gives

    L_n(x)=cosh(x)^n+delta_n(x)
          =cosh(x)^n [1+delta_n(x)/cosh(x)^n].

`expm1` evaluates the small correction coefficient without subtracting two
nearby interval values. Delta is retained exactly as an analytic expression;
it is not linearized in beta. Integer multiplicities m_i satisfy
sum_i n_i m_i=N-n_root, with n_root=15.

## 2. Cancel the large terms before quadrature

Set R=N^(1/4), x=X/R, c=1+lambda/sqrt(N),
A=sqrt(N)(1-1/c)/2 and g(x)=log(cosh(x))-x^2/2. Then

    -sqrt(N)X^2/(2c) + sum_i m_i log L_i(x) + log L_root(x)
    = A X^2 - n_root x^2/2 + (N-n_root)g(x)
      + log L_root(x)
      + sum_i m_i log[1+delta_i(x)/cosh(x)^n_i].

The equality follows by substituting log(cosh x)=x^2/2+g(x) and
Nx^2=sqrt(N)X^2. It cancels the large quadratic contributions algebraically.
All factors are positive on the real integration interval. Root and correction
logs use acb's analytic branch check in the complex neighborhoods requested by
quadrature. If a neighborhood cannot certify that branch, it returns an
unresolved enclosure and the integrator subdivides.

The exponential of the right side is the original integrand. Root interactions,
the final component, integer multiplicities, and all temperature corrections
are preserved. The original real-axis infinite-tail bound remains valid.

## 3. Enclose g without reintroducing the cancellation

For a complex interval x with |x|<=r<1/2, evaluate

    u_20=sum_(j=1)^20 x^(2j)/(2j)!,
    v_20=sum_(j=2)^20 x^(2j)/(2j)!.

The omitted cosh tail has modulus at most

    e_c=r^42/[42! (1-r^2/2)].

Indeed its first term has magnitude at most r^42/42!, and every subsequent
term ratio is at most r^2/2. Add a complex rectangle of radius e_c to each
polynomial, enclosing u=cosh(x)-1 and v=u-x^2/2 respectively.

Let q be the resulting outward upper bound for |u| and require q<1. The
logarithm series gives

    g(x)=v + sum_(j=2)^32 (-1)^(j+1)u^j/j + remainder,
    |remainder| <= q^33/[33(1-q)].

The last inequality bounds 1/j by1/33 in the omitted tail and sums the
geometric series. The code propagates both complex error rectangles, including
the cosh error inside every power of u. Their possible dependence is handled
by interval overenclosure, not an independence assumption. It then multiplies
the resulting enclosure by N-n_root in the exponent, so the scale-dependent
remainder is fully retained.

On |x|<1/2 the true functions are analytic: |cosh(x)-1| is bounded by
cosh(1/2)-1<1. The series selects the logarithm agreeing with the real one at
zero. If r>=1/2 or q>=1, the evaluator returns unresolved and requires a
smaller complex neighborhood. Thus no unsupported analyticity assertion is
passed to the integrator.

The two finite polynomials with explicit remainder enclose the exact function;
they do not define a truncated physical model. At real X up to10 in the
production ladder, |x|<0.178. N5000 qualification uses its existing cutoff8;
its larger real |x| can exceed1/2, so that scale must use the preserved direct
formula rather than this small-argument evaluator.
