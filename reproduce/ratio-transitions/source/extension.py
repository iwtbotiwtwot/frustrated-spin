"""Exact all-high-temperature extension of the tricritical point certificates."""
import json,time
from pathlib import Path
import sympy as s
from flint import arb,ctx
P=Path(__file__).resolve().parent;O=P/'output';O.mkdir(exist_ok=True);ctx.prec=192
def run():
 start=time.perf_counter();v,a,x,u=s.symbols('v a x u');PP=1+(-a**3+2*a*a-3*a)*v*v+a*a*v**4;rows=[]
 for name,G,n,f in [('pair',1-a*v*v,2,s.Rational(1,5)),('chain',(1-a*v*v)**4*PP,12,s.Rational(77,461))]:
  m=s.cancel(v+(1-f)*(1-v*v)*s.diff(G,v)/(n*G));chi=s.diff(m,v).subs(v,0)
  num,den=s.fraction(s.cancel(chi*sum(v**(2*j)/s.Integer(2*j+1) for j in range(5))-m/v))
  if den.subs({a:0,v:0})<0:num=-num;den=-den
  pp=s.Poly(num/v**2,v);p=s.Poly(sum(z*x**(j[0]//2) for j,z in pp.terms()).subs(a,u/2),u,x);du,dx=p.degree_list()
  B=[[s.factor(sum(z*s.binomial(i,ia)/s.binomial(du,ia)*s.binomial(j,ix)/s.binomial(dx,ix) for (ia,ix),z in p.terms() if ia<=i and ix<=j)) for j in range(dx+1)] for i in range(du+1)]
  assert all(z>=0 for row in B for z in row)
  restored=sum(B[i][j]*s.binomial(du,i)*u**i*(1-u)**(du-i)*s.binomial(dx,j)*x**j*(1-x)**(dx-j) for i in range(du+1) for j in range(dx+1))
  assert s.Poly(restored-p.as_expr(),u,x).is_zero
  ct=chi.subs(a,s.Rational(1,2));dmax=1 if n==2 else s.Rational(7,6)
  def ar(q):q=s.Rational(q);return arb(int(q.p))/int(q.q)
  lower=ar(ct)-ar((1-f)*dmax)*arb(3).log()/2;assert lower>0
  rows.append(dict(family=name,free_fraction=str(f),a_interval=['0','1/2'],degrees=[du,dx],numerator=str(p.as_expr()),denominator=str(s.factor(den)),multiplier='v^2',substitution='a=u/2, x=v^2',bernstein=[[str(z) for z in row] for row in B],exact_reconstruction=True,nonnegative=True,critical_function_derivative_lower_bound=str(lower),consequence='m(y)<chi*y globally for a<=1/2; beta*chi strictly increases up to beta_t at fixed kappa_t; extends to all f>=f_t by convexity'))
 out=dict(status='PASS',families=rows,bernstein_coefficients=sum((r['degrees'][0]+1)*(r['degrees'][1]+1) for r in rows),wall_seconds=time.perf_counter()-start)
 (O/'EXTENSION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status='PASS',coefficients=out['bernstein_coefficients'],seconds=out['wall_seconds'])),flush=True)
if __name__=='__main__':run()
