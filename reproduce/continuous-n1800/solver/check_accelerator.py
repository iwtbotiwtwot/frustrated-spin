import ast,collections,itertools,math,struct,time
from pathlib import Path
import numpy as np
import fast_cpu
from flint import arb,ctx

def run():
 checks=0
 for n in [10,65,1000,1408,1750,2000]:
  limbs=(n+64)//64;values=[0,1,(1<<n)-1,1<<(n//2)]*16;data=np.zeros((len(values),limbs),dtype=np.uint64)
  for i,v in enumerate(values):data[i]=np.frombuffer(v.to_bytes(limbs*8,'little'),dtype=np.uint64)
  for orientation in [True,False]:
   for fill in [-1,1]:
    bound=100
    for compact in [False,True]:
     indices=np.arange(len(values),dtype=np.int64) if compact else np.empty(0,dtype=np.int64)
     expected=[];marginal=collections.Counter();mom=[0,0,0];mm=[0,0,0]
     for idx,c in enumerate(values):
      if not c:continue
      k,t=divmod(idx,bound+1) if orientation else tuple(reversed(divmod(idx,n+1)))
      if k>n:break
      m=2*k-n;e=2*t-bound-fill*((m*m-n)//2);expected.append((e,m,c));marginal[k]+=c;mom[0]+=c;mom[1]+=e*c;mom[2]+=e*e*c;mm[0]+=m*c;mm[1]+=m*m*c;mm[2]+=e*m*c
     else:
      got=fast_cpu.decode(data,indices,compact,n,bound,fill,orientation);assert got==(sorted(expected),dict(marginal),mom,mm)
      raw=struct.pack('<IQ',3,len(expected))+b''.join(struct.pack('<qq',e,m)+c.to_bytes((n+8)//8,'little') for e,m,c in sorted(expected));assert fast_cpu.canonical(n,3,got[0])==raw;checks+=2
 cfg=dict(thermal_beta_numerators_over_N=[1,4]);ctx.prec=128
 text=(Path(__file__).parent.parent/'reference/runner.py').read_text();node=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='reduce_row');ns=dict(CONFIG=cfg,arb=arb,ctx=ctx);exec(compile(ast.Module(body=[node],type_ignores=[]),'reference_reduction','exec'),ns)
 for n in [65,1000,1408,1750,2000]:
  entries=[(-12,-4,1<<n),(-12,4,5),(-2,-4,13),(4,0,(1<<n)-1),(8,4,3)]
  a,fa=ns['reduce_row'](entries,n,{});b,fb=fast_cpu.reduce_row(entries,n,{},cfg);assert a==b and [v.str(40) for v in fa]==[v.str(40) for v in fb];checks+=1
 return dict(status='PASS',checks=checks)
if __name__=='__main__':print(run())
