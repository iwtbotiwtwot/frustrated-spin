"""Exact CUDA NTT and CRT for source-bound nonnegative polynomial products."""
from pathlib import Path
import math,time
import numpy as np
import cupy as cp
from flint import fmpz

class Backend:
 def __init__(self):
  names=['twiddles','stage','combine','normalize','garner','pack']
  self.module=cp.RawModule(code=Path(__file__).with_name('kernels.cu').read_text(),options=('-std=c++17',),name_expressions=names)
  self.k={n:self.module.get_function(n) for n in names}
 def launch(self,name,n,args,block=256,grid_y=1):
  self.k[name](((n+block-1)//block,grid_y),(block,),args)
 def ntt(self,a,w,p,ni,inverse=False):
  n=a.size
  widths=[1<<i for i in range(1,n.bit_length())]
  if not inverse:widths.reverse()
  for width in widths:self.launch('stage',n//2,(a,w,np.uint64(n),np.uint64(width),np.uint64(p),np.uint64(ni),np.int32(inverse)))
 def solve(self,factors,bits):
  # factors: (sparse exponent->nonnegative count, positive multiplicity).
  assert factors and all(e>0 and r and min(r)>=0 and min(r.values())>0 for r,e in factors)
  degree=sum(max(r)*e for r,e in factors);length=degree+1;n=1<<degree.bit_length()
  if n==1:n=2
  # Product of moduli strictly exceeds the full nonnegative coefficient bound.
  bound=math.prod(sum(r.values())**e for r,e in factors)
  assert bound<=1<<bits
  primes=[];roots=[];product=1;q=((1<<61)-1)//n
  while product<=bound:
   p=q*n+1;q-=1
   if not fmpz(p).is_prime():continue
   a=2
   while True:
    root=pow(a,(p-1)//n,p)
    if pow(root,n//2,p)!=1:break
    a+=1
   primes.append(p);roots.append(root);product*=p
  limbs=(bits+1+63)//64
  if limbs>64:raise ValueError('4096-bit reconstruction capacity')
  # Keep one modulus transform resident; retain residues for exact reconstruction.
  needed=(len(primes)*length+4*n+length*limbs)*8
  free,total=cp.cuda.runtime.memGetInfo()
  if needed>free*0.85:raise MemoryError(f'GPU admission: need {needed}, free {free}')
  start=time.perf_counter();residues=cp.empty((len(primes),length),dtype=cp.uint64)
  timings=[]
  for ordinal,(p,root) in enumerate(zip(primes,roots)):
   t=time.perf_counter();ni=(-pow(p,-1,1<<64))%(1<<64);one=(1<<64)%p
   w=cp.empty(n//2,dtype=cp.uint64)
   self.launch('twiddles',n//2,(w,np.uint64(n),np.uint64(root*one%p),np.uint64(p),np.uint64(ni),np.uint64(one)))
   result=cp.full(n,one,dtype=cp.uint64)
   for sparse,exponent in factors:
    data=cp.zeros(n,dtype=cp.uint64)
    idx=np.fromiter(sparse,dtype=np.int64)
    val=np.fromiter((int(v)*one%p for v in sparse.values()),dtype=np.uint64)
    data[cp.asarray(idx)]=cp.asarray(val)
    self.ntt(data,w,p,ni)
    self.launch('combine',n,(result,data,np.uint64(n),np.uint64(exponent),np.uint64(p),np.uint64(ni),np.uint64(one)))
    del data
   self.launch('twiddles',n//2,(w,np.uint64(n),np.uint64(pow(root,-1,p)*one%p),np.uint64(p),np.uint64(ni),np.uint64(one)))
   self.ntt(result,w,p,ni,True)
   self.launch('normalize',length,(residues[ordinal],result,np.uint64(length),np.uint64(pow(n,-1,p)),np.uint64(p),np.uint64(ni)))
   cp.cuda.get_current_stream().synchronize();timings.append(time.perf_counter()-t)
   del result,w
  transform_seconds=time.perf_counter()-start
  ps=cp.asarray(primes,dtype=cp.uint64);nis=cp.asarray([(-pow(p,-1,1<<64))%(1<<64) for p in primes],dtype=cp.uint64)
  inverses=np.zeros((len(primes),len(primes)),dtype=np.uint64)
  for i,p in enumerate(primes):
   for j in range(i):inverses[j,i]=pow(primes[j],-1,p)*(1<<64)%p
  inv=cp.asarray(inverses);t=time.perf_counter()
  for j in range(len(primes)-1):
   self.launch('garner',length,(residues,ps,nis,inv,np.uint64(length),np.int32(len(primes)),np.int32(j)),grid_y=len(primes)-j-1)
  packed=cp.empty((length,limbs),dtype=cp.uint64)
  self.launch('pack',length,(residues,ps,packed,np.uint64(length),np.int32(len(primes)),np.int32(limbs)),block=128)
  cp.cuda.get_current_stream().synchronize();crt_seconds=time.perf_counter()-t
  t=time.perf_counter();host=cp.asnumpy(packed);transfer_seconds=time.perf_counter()-t
  return host,dict(degree=degree,ntt_length=n,primes=primes,coefficient_bound=str(bound),transform_seconds=transform_seconds,crt_seconds=crt_seconds,transfer_seconds=transfer_seconds,total_seconds=time.perf_counter()-start,modulus_seconds=timings,estimated_gpu_bytes=needed)
