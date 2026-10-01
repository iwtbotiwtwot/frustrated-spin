# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
import cython
from libc.stdint cimport uint64_t,int64_t
from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_FromStringAndSize,PyBytes_AsString
cdef extern from "Python.h":
    ctypedef struct PyLongObject:
        pass
    object _PyLong_FromByteArray(const unsigned char*,size_t,int,int)
    int _PyLong_AsByteArray(PyLongObject*,unsigned char*,size_t,int,int) except -1
from flint import arb,ctx

def decode(uint64_t[:,::1] data,int64_t[::1] indices,bint compact,long n,long bound,long fill,bint kmajor):
    cdef Py_ssize_t i,j,limbs=data.shape[1],length=data.shape[0]
    cdef long idx,k,t,m,e
    cdef object value,m0=0,m1=0,m2=0,mm0=0,mm1=0,mm2=0
    cdef list entries=[],marginal=[0]*(n+1)
    for i in range(length):
        idx=indices[i] if compact else i
        value=_PyLong_FromByteArray(<unsigned char*>&data[i,0],limbs*8,1,0)
        if not value:continue
        if kmajor:k=idx//(bound+1);t=idx%(bound+1)
        else:t=idx//(n+1);k=idx%(n+1)
        assert 0<=k<=n and 0<=t<=bound and value>0
        m=2*k-n;e=2*t-bound-fill*((m*m-n)//2)
        entries.append((e,m,value));marginal[k]+=value
        m0+=value;m1+=e*value;m2+=e*e*value;mm0+=m*value;mm1+=m*m*value;mm2+=e*m*value
    entries.sort()
    for i in range(1,len(entries)):
        assert entries[i][0]!=entries[i-1][0] or entries[i][1]!=entries[i-1][1]
    return entries,{i:v for i,v in enumerate(marginal) if v},[m0,m1,m2],[mm0,mm1,mm2]

def canonical(long n,unsigned int state,list entries):
    import struct
    cdef Py_ssize_t width=(n+8)//8,stride=16+width,length=len(entries),i
    cdef long long e,m
    cdef object count
    cdef bytes result=PyBytes_FromStringAndSize(NULL,12+length*stride)
    cdef char* dest=PyBytes_AsString(result)
    cdef bytes header=struct.pack('<IQ',state,length)
    memcpy(dest,PyBytes_AsString(header),12)
    for i in range(length):
        e=entries[i][0];m=entries[i][1];count=entries[i][2]
        memcpy(dest+12+i*stride,&e,8);memcpy(dest+20+i*stride,&m,8)
        _PyLong_AsByteArray(<PyLongObject*>count,<unsigned char*>(dest+28+i*stride),width,1,0)
    return result

@cython.locals(n=cython.long,e=cython.long,m=cython.long)
def reduce_row(entries,n,weights,CONFIG):
 minima={};levels={}
 for e,m,c in entries:
  if m not in minima or e<minima[m][0]:minima[m]=[e,c]
  elif e==minima[m][0]:minima[m][1]+=c
  v=levels.setdefault(e,[0,0,0]);v[0]+=c;v[1]+=m*c;v[2]+=m*m*c
 ground=min(e for e,c in minima.values());deg=sum(c for e,c in minima.values() if e==ground)
 hull=[]
 for m,(e,c) in sorted(minima.items()):
  while len(hull)>1:
   a,z=hull[-2:]
   if (z[1]-a[1])*(m-z[0])>=(e-z[1])*(z[0]-a[0]):hull.pop()
   else:break
  hull.append((m,e))
 from fractions import Fraction
 crossings=[]
 for a,z in zip(hull,hull[1:]):
  h=Fraction(z[1]-a[1],z[0]-a[0]);intercept=a[1]-h*a[0]
  crossings.append(dict(uniform_field=str(h),coexisting_M=[m for m,(e,c) in sorted(minima.items()) if e-h*m==intercept]))
 thermal=[];free_energies=[]
 for numerator in CONFIG['thermal_beta_numerators_over_N']:
  beta=arb(numerator)/n;z=arb(0);es=arb(0);e2s=arb(0);ms=arb(0);m2s=arb(0);ems=arb(0)
  for e,(count,mcount,m2count) in levels.items():
   key=numerator,e
   if key not in weights:weights[key]=(-beta*e).exp()
   w=weights[key];wc=w*count;z+=wc;es+=wc*e;e2s+=wc*(e*e);ms+=w*mcount;m2s+=w*m2count;ems+=w*(e*mcount)
  logz=z.log();emean=es/z;mmean=ms/z;ev=e2s/z-emean**2;mv=m2s/z-mmean**2;free=-logz/beta;free_energies.append(free)
  values=dict(log_partition=logz,free_energy=free,mean_energy=emean,mean_magnetization=mmean,energy_variance=ev,magnetization_variance=mv,energy_magnetization_covariance=ems/z-emean*mmean,entropy=logz+beta*emean,heat_capacity=beta**2*ev,uniform_field_susceptibility=beta*mv)
  thermal.append(dict(beta=f'{numerator}/{n}',uniform_field=0,collective_shift=0,precision_bits=ctx.prec,arithmetic='ARB_CERTIFIED_BALL',intervals={k:v.str(40) for k,v in values.items()}))
 return dict(fixed_M_minima=[[m,e,str(c)] for m,(e,c) in sorted(minima.items())],ground_energy=ground,ground_degeneracy=str(deg),ground_crossing_fields=crossings,thermal=thermal),free_energies
