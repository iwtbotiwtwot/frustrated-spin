"""Bounded, source-bound free/core ratio investigation. No expanded large-N table."""
import itertools,json,time,hashlib,platform,resource,os
from collections import Counter
from pathlib import Path
import sympy as s
import mpmath as mp
from flint import arb,ctx
P=Path(__file__).resolve().parent;O=P/'output';O.mkdir(exist_ok=True)
ctx.prec=192;ctx.threads=1;mp.mp.dps=65
def save(n,z):(O/n).write_text(json.dumps(z,indent=2)+'\n')
def wire(z):return dict(lower=str(z.lower().fmpq()),upper=str(z.upper().fmpq()),mid=str(z.mid()))
def real(q):
 q=s.Rational(q);return arb(int(q.p))/int(q.q)
def main():
 start=time.perf_counter();v,a,x,X,U,f=s.symbols('v a x X U f');checks=0;rows=[];witnesses=[];maps=[]
 pair=1+2*X*U+X**2
 path=1+X**4+2*(X+X**2+X**3)*(U+U**2)+2*X**2*U**3
 PP=1+(-a**3+2*a*a-3*a)*v*v+a*a*v**4
 for family,G,n,source_name,repeat in [('pair',1-a*v*v,2,'signed_packet',pair**3*(1+X)**9),('chain',(1-a*v*v)**4*PP,12,'signed_packet_chain',path*pair**4*(1+X)**18)]:
  src=json.loads((P/f'N005000_{source_name}_+1_K_MAJOR.json').read_text())['case'];stride=src['bound']//src['step']+1;size=15 if n==2 else 30
  fac=next(q for q in src['factors'] if max(i//stride for i,w in q['row'])==size);L=max(i%stride for i,w in fac['row'])
  exact=sum(w*X**(i//stride)*U**(L-i%stride) for i,w in fac['row']);assert s.Poly(exact-repeat,X,U).is_zero;checks+=1
  mint=s.cancel(v+(1-v*v)*s.diff(G,v)/(n*G));mf=f*v+(1-f)*mint
  cumul=[];d=mint
  for j in range(1,6):
   d=s.cancel((1-v*v)*s.diff(d,v))
   if j in [1,3,5]:cumul.append(s.factor(d.subs(v,0)))
  chi=f+(1-f)*cumul[0];c4=-2*f+(1-f)*cumul[1];c6=16*f+(1-f)*cumul[2]
  ft=s.factor(cumul[1].subs(a,s.Rational(1,2))/(2+cumul[1].subs(a,s.Rational(1,2))))
  sub={a:s.Rational(1,2),f:ft};ct=s.factor(chi.subs(sub));bt=1/ct;kt=ct*s.log(3)/4;c6t=s.factor(c6.subs(sub));assert c4.subs(sub)==0 and c6t<0;checks+=2
  # Exact global response certificate: chi*S4 - m/v = v^4 Q(v^2)/D(v^2).
  S4=sum(v**(2*j)/s.Integer(2*j+1) for j in range(5));diff=s.factor((chi*S4-mf/v).subs(sub))
  num,den=s.fraction(diff)
  if den.subs(v,0)<0:num=-num;den=-den
  Q=s.Poly(num/v**4,v);Q=s.Poly(sum(z*x**(j[0]//2) for j,z in Q.terms()),x);degree=Q.degree()
  bern=[s.factor(sum(z*s.binomial(i,j[0])/s.binomial(degree,j[0]) for j,z in Q.terms() if j[0]<=i)) for i in range(degree+1)]
  assert all(z>0 for z in bern)
  restored=sum(bern[i]*s.binomial(degree,i)*x**i*(1-x)**(degree-i) for i in range(degree+1));assert s.expand(restored-Q.as_expr())==0;checks+=2
  # Jacobian of (r,c4) with respect to (beta,f), kappa held at kt.
  da_db=2*kt*(1-s.Rational(1,2)**2)
  rb=s.simplify(s.diff(chi,a).subs(sub)*da_db+ct**2);rf=s.diff(chi,f).subs(sub)
  c4b=s.diff(c4,a).subs(sub)*da_db;c4f=s.diff(c4,f).subs(sub);jac=s.simplify(rb*c4f-rf*c4b)
  rb_ball=real(rb.coeff(s.log(3),0))+real(s.expand(rb).coeff(s.log(3)))*arb(3).log()
  jac_ball=real(s.expand(jac).coeff(s.log(3),0))+real(s.expand(jac).coeff(s.log(3)))*arb(3).log()
  assert rb_ball>0 and jac_ball<0;checks+=2
  # Independent literal spin enumeration: no factor or derivative formulas used.
  edges=[(0,1)] if n==2 else [(0,1),(1,2),(2,3),(4,5),(6,7),(8,9),(10,11)]
  hist=Counter((sum(sp),sum(sp[i]==sp[j] for i,j in edges)) for sp in itertools.product([-1,1],repeat=n))
  enumeration=[]
  for av in map(s.Rational,['0','1/4','1/2','3/4','9/10']):
   q=(1-av)/(1+av);Z=sum(count*q**aligned for (M,aligned),count in hist.items())
   moments=[sum(count*q**aligned*M**j for (M,aligned),count in hist.items())/Z for j in [2,4,6]]
   c2,c4e,c6e=moments[0],moments[1]-3*moments[0]**2,moments[2]-15*moments[1]*moments[0]+30*moments[0]**3
   assert all(s.factor(c/n-form.subs(a,av))==0 for c,form in zip([c2,c4e,c6e],cumul));checks+=3
   enumeration.append(dict(a=str(av),cumulants_per_spin=list(map(str,[c2/n,c4e/n,c6e/n]))))
  # Positive-factor directed Arb evaluation of pressure; independent histogram overlap.
  def pressure(beta,kap,frac,y):
   q=(-4*beta*kap).exp();B=(1+q*(2*y).cosh())/(1+q)
   logint=B.log()/2 if n==2 else (4*B.log()+((q**3*(4*y).cosh()+2*(q*q+q)*(2*y).cosh()+q*q+q+1)/(1+q)**3).log())/12
   return -y*y/(2*beta)+frac*y.cosh().log()+(1-frac)*logint
  beta=arb(4 if n==2 else 12);kap=real('1/5');y=beta;val=pressure(beta,kap,arb(0),y);assert val>0
  q=(-4*beta*kap).exp();num=sum(count*q**al*(M*y).exp() for (M,al),count in hist.items());den0=sum(count*q**al for (M,al),count in hist.items())
  direct=-y*y/(2*beta)+(num/den0).log()/n;assert val.overlaps(direct);checks+=2
  witnesses.append(dict(family=family,free_fraction='0',kappa='1/5',beta=str(beta.mid()),y=str(y.mid()),pressure=wire(val),independent_enumeration_overlap=True,all_beta_local_stability_bound=wire(arb(5)/(2*arb(1).exp()))))
  # Numerical local phase-curve exploration. These roots are explicitly approximations.
  chifun=s.lambdify((a,f),chi,'mpmath');c4fun=s.lambdify((a,f),c4,'mpmath');c6fun=s.lambdify((a,f),c6,'mpmath');mfun=s.lambdify((v,a,f),mf,'mpmath')
  ktm=mp.mpf(str(s.N(kt,70)));btm=mp.mpf(str(s.N(bt,70)));ftm=mp.mpf(str(s.N(ft,70)))
  def psi(y,b,ff):
   q=mp.exp(-4*b*ktm);B=(1+q*mp.cosh(2*y))/(1+q)
   li=mp.log(B)/2 if n==2 else (4*mp.log(B)+mp.log((q**3*mp.cosh(4*y)+2*(q*q+q)*mp.cosh(2*y)+q*q+q+1)/(1+q)**3))/12
   return -y*y/(2*b)+ff*mp.log(mp.cosh(y))+(1-ff)*li
  for delta in ['-0.03','-0.01','0','0.01','0.03','0.1']:
   ff=ftm+mp.mpf(delta);bs=mp.findroot(lambda b:b*chifun(mp.tanh(2*b*ktm),ff)-1,(btm*mp.mpf('.95'),btm*mp.mpf('1.05')))
   av=mp.tanh(2*bs*ktm);four=c4fun(av,ff);six=c6fun(av,ff)
   row=dict(family=family,kappa=mp.nstr(ktm,35),free_fraction=mp.nstr(ff,35),offset=delta,local_instability_beta=mp.nstr(bs,35),quartic_at_instability=mp.nstr(four,35),root_type='numerical local instability; not a global phase certification')
   if mp.mpf(delta)<0:
    yi=mp.sqrt(-15*four/six)
    def equations(b,y):return (mfun(mp.tanh(y),mp.tanh(2*b*ktm),ff)-y/b)/y,psi(y,b,ff)/(y*y)
    bc,yc=mp.findroot(equations,(bs-mp.mpf('.005'),yi),tol=mp.mpf('1e-48'),maxsteps=100)
    assert bc<bs and yc>0 and abs(psi(yc,bc,ff))<mp.mpf('1e-45')
    row.update(coexistence_beta=mp.nstr(bc,35),positive_y=mp.nstr(yc,35),magnetization_jump=mp.nstr(yc/bc,35),coexistence_residual=mp.nstr(abs(psi(yc,bc,ff)),5),coexistence_scope='numerical stationary equal-pressure branch; local theorem gives the nearby first-order structure')
   maps.append(row)
  rows.append(dict(family=family,core_spins=n,core_edges=len(edges),free_fraction=str(ft),interacting_fraction=str(1-ft),beta_tricritical=str(bt),kappa_tricritical=str(kt),kappa_decimal=str(s.N(kt,30)),susceptibility=str(ct),sixth_cumulant=str(c6t),core_cumulants=list(map(str,cumul)),mixed_cumulants=list(map(str,[chi,c4,c6])),global_difference=str(diff),Q=str(Q.as_expr()),denominator=str(s.factor(den)),bernstein=list(map(str,bern)),r_beta=str(rb),jacobian_beta_fraction=str(jac),r_beta_interval=wire(rb_ball),jacobian_interval=wire(jac_ball),enumeration=enumeration,source_sha256=hashlib.sha256((P/f'N005000_{source_name}_+1_K_MAJOR.json').read_bytes()).hexdigest()))
 counter=dict(family='pair',free_fraction='1/4',a='2/3',quartic='0',sixth='4/3',meaning='Quartic zero alone is insufficient for stabilized tricriticality')
 assert (-2*f+(1-f)*(-2+8*a-6*a*a)).subs({a:s.Rational(2,3),f:s.Rational(1,4)})==0
 assert (16*f+(1-f)*(16-136*a+240*a*a-120*a**3)).subs({a:s.Rational(2,3),f:s.Rational(1,4)})==s.Rational(4,3);checks+=2
 result=dict(status='PASS',families=rows,first_order_witnesses=witnesses,local_curve=maps,quartic_only_counterexample=counter,independent_exact_checks=checks,wall_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,precision_bits=192,large_N_expansion=False)
 save('RESULTS.json',result);save('HARDWARE.json',dict(platform=platform.platform(),python=platform.python_version(),affinity=sorted(os.sched_getaffinity(0)),sympy=s.__version__,mpmath=mp.__version__,cpu_workers=1,gpu_used=False))
 print(json.dumps(dict(status='PASS',checks=checks,wall_seconds=result['wall_seconds'])),flush=True)
if __name__=='__main__':main()
