"""Resource-admitted exact CUDA solver with reusable common-factor transforms."""
from pathlib import Path
import math,time
import numpy as np
import cupy as cp
from flint import fmpz
from gpu_baseline import Backend as Original

class Counts:
 def __init__(self,data,indices):self.data=data;self.indices=indices
 @property
 def nbytes(self):return self.data.nbytes+self.indices.nbytes

class Backend(Original):
 def __init__(self,cache=True,pinned=True):
  super().__init__();self.cache_enabled=cache;self.pinned=pinned;self.cache=None;self.cache_key=None;self.parameters={}
 def clear(self):
  self.cache=None;self.cache_key=None;cp.get_default_memory_pool().free_all_blocks();cp.get_default_pinned_memory_pool().free_all_blocks()
 def solve(self,factors,bits):
  assert factors and all(e>0 and r and min(r)>=0 and min(r.values())>0 for r,e in factors)
  degree=sum(max(r)*e for r,e in factors);length=degree+1;n=max(2,1<<degree.bit_length())
  bound=math.prod(sum(r.values())**e for r,e in factors);assert bound<=1<<bits
  parameter_key=(n,bound)
  if parameter_key not in self.parameters:
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
   self.parameters[parameter_key]=(primes,roots)
  primes,roots=self.parameters[parameter_key];limbs=(bits+1+63)//64
  if limbs>64:raise ValueError('4096-bit reconstruction capacity')
  key=(n,tuple(primes),tuple((tuple(sorted(r.items())),e) for r,e in factors[:-1]))
  if self.cache_key!=key:self.clear()
  hit=self.cache is not None
  needed=(len(primes)*length+4*n+length*limbs)*8
  cache_bytes=len(primes)*n*8 if self.cache_enabled and len(factors)>1 else 0
  free,total=cp.cuda.runtime.memGetInfo();available=free+cp.get_default_memory_pool().free_bytes()+(self.cache.nbytes if hit else 0)
  if needed>available*.85:raise MemoryError(f'GPU admission: need {needed}, available {available}')
  use_cache=cache_bytes>0 and needed+cache_bytes<=available*.85
  if not use_cache:self.clear();hit=False;cache_bytes=0
  if use_cache and not hit:self.cache=cp.empty((len(primes),n),dtype=cp.uint64);self.cache_key=key
  # No output-array overcommit while prior host writers are active.
  host_bytes=length*limbs*8
  cg=Path('/sys/fs/cgroup');limit=(cg/'memory.max').read_text().strip()
  if limit!='max':
   stat=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines());used=int((cg/'memory.current').read_text())-int(stat.get('inactive_file',0))
   if used+host_bytes>int(limit)*.85:raise MemoryError('Host output admission; reduce writer queue')
  start=time.perf_counter();residues=cp.empty((len(primes),length),dtype=cp.uint64);timings=[]
  for ordinal,(p,root) in enumerate(zip(primes,roots)):
   t=time.perf_counter();ni=(-pow(p,-1,1<<64))%(1<<64);one=(1<<64)%p
   w=cp.empty(n//2,dtype=cp.uint64)
   self.launch('twiddles',n//2,(w,np.uint64(n),np.uint64(root*one%p),np.uint64(p),np.uint64(ni),np.uint64(one)))
   result=self.cache[ordinal].copy() if hit else cp.full(n,one,dtype=cp.uint64)
   work=factors[-1:] if hit else factors
   for index,(sparse,exponent) in enumerate(work):
    if use_cache and not hit and index==len(factors)-1:self.cache[ordinal]=result
    data=cp.zeros(n,dtype=cp.uint64);idx=np.fromiter(sparse,dtype=np.int64);val=np.fromiter((int(v)*one%p for v in sparse.values()),dtype=np.uint64)
    data[cp.asarray(idx)]=cp.asarray(val);self.ntt(data,w,p,ni)
    self.launch('combine',n,(result,data,np.uint64(n),np.uint64(exponent),np.uint64(p),np.uint64(ni),np.uint64(one)));del data
   self.launch('twiddles',n//2,(w,np.uint64(n),np.uint64(pow(root,-1,p)*one%p),np.uint64(p),np.uint64(ni),np.uint64(one)))
   self.ntt(result,w,p,ni,True)
   self.launch('normalize',length,(residues[ordinal],result,np.uint64(length),np.uint64(pow(n,-1,p)),np.uint64(p),np.uint64(ni)))
   cp.cuda.get_current_stream().synchronize();timings.append(time.perf_counter()-t);del result,w
  transform_seconds=time.perf_counter()-start
  ps=cp.asarray(primes,dtype=cp.uint64);nis=cp.asarray([(-pow(p,-1,1<<64))%(1<<64) for p in primes],dtype=cp.uint64);inverses=np.zeros((len(primes),len(primes)),dtype=np.uint64)
  for i,p in enumerate(primes):
   for j in range(i):inverses[j,i]=pow(primes[j],-1,p)*((1<<64)%p)%p
  inv=cp.asarray(inverses);t=time.perf_counter()
  for j in range(len(primes)-1):self.launch('garner',length,(residues,ps,nis,inv,np.uint64(length),np.int32(len(primes)),np.int32(j)),grid_y=len(primes)-j-1)
  packed=cp.empty((length,limbs),dtype=cp.uint64)
  self.launch('pack',length,(residues,ps,packed,np.uint64(length),np.int32(len(primes)),np.int32(limbs)),block=128)
  cp.cuda.get_current_stream().synchronize();crt_seconds=time.perf_counter()-t
  del residues,ps,nis,inv
  compact_start=time.perf_counter();indices=None
  if length>=1000000:
   indices=cp.flatnonzero(cp.any(packed,axis=1));dense=packed;packed=dense[indices];del dense
  cp.cuda.get_current_stream().synchronize();compact_seconds=time.perf_counter()-compact_start;t=time.perf_counter()
  host_bytes=packed.nbytes;shape=packed.shape
  if self.pinned:
   quantum=256*1024**2 if host_bytes>64*1024**2 else 4096
   capacity=((host_bytes+quantum-1)//quantum)*quantum
   buffer=cp.cuda.alloc_pinned_memory(capacity);host=np.frombuffer(buffer,dtype=np.uint64,count=packed.size).reshape(shape);packed.get(out=host,blocking=False);cp.cuda.get_current_stream().synchronize()
  else:host=cp.asnumpy(packed)
  if indices is not None:host=Counts(host,cp.asnumpy(indices))
  transfer_seconds=time.perf_counter()-t
  return host,dict(degree=degree,ntt_length=n,primes=primes,coefficient_bound=str(bound),transform_seconds=transform_seconds,crt_seconds=crt_seconds,transfer_seconds=transfer_seconds,total_seconds=time.perf_counter()-start,modulus_seconds=timings,estimated_gpu_bytes=needed+cache_bytes,cache_bytes=cache_bytes,cache_hit=hit,cache_enabled=use_cache,pinned_host=self.pinned,compact_seconds=compact_seconds,host_bytes=host.nbytes,compact=indices is not None)
