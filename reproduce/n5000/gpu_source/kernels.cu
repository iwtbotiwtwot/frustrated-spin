typedef unsigned long long U;
__device__ __forceinline__ U mul(U a,U b,U p,U ni){
 U lo=a*b,hi=__umul64hi(a,b),m=lo*ni,ml=m*p;
 U t=hi+__umul64hi(m,p)+(lo+ml<lo);
 return t>=p?t-p:t;
}
__device__ __forceinline__ U add(U a,U b,U p){U c=a+b;return c>=p?c-p:c;}
__device__ __forceinline__ U sub(U a,U b,U p){return a>=b?a-b:a+p-b;}
__device__ U power(U x,U e,U p,U ni,U one){U v=one;while(e){if(e&1)v=mul(v,x,p,ni);x=mul(x,x,p,ni);e>>=1;}return v;}
extern "C" __global__ void twiddles(U* w,U n,U root,U p,U ni,U one){
 U i=(U)blockIdx.x*blockDim.x+threadIdx.x;if(i<n/2)w[i]=power(root,i,p,ni,one);
}
extern "C" __global__ void stage(U* a,const U* w,U n,U width,U p,U ni,int inverse){
 U i=(U)blockIdx.x*blockDim.x+threadIdx.x;if(i>=n/2)return;
 U half=width/2,j=i%half,k=(i/half)*width+j,t=j*(n/width),u=a[k],v=a[k+half];
 if(inverse){v=mul(v,w[t],p,ni);a[k]=add(u,v,p);a[k+half]=sub(u,v,p);}
 else {a[k]=add(u,v,p);a[k+half]=mul(sub(u,v,p),w[t],p,ni);}
}
extern "C" __global__ void combine(U* a,const U* b,U n,U exponent,U p,U ni,U one){
 U i=(U)blockIdx.x*blockDim.x+threadIdx.x;if(i<n)a[i]=mul(a[i],power(b[i],exponent,p,ni,one),p,ni);
}
extern "C" __global__ void normalize(U* out,const U* a,U length,U scale,U p,U ni){
 U i=(U)blockIdx.x*blockDim.x+threadIdx.x;if(i<length)out[i]=mul(a[i],scale,p,ni);
}
// Mixed-radix Garner reconstruction. Residues are canonical, not Montgomery.
// inverses[j*P+i] = p_j^{-1} mod p_i in Montgomery representation.
extern "C" __global__ void garner(U* digits,const U* primes,const U* nis,
 const U* inverses,U length,int P,int j){
 U k=(U)blockIdx.x*blockDim.x+threadIdx.x;int i=blockIdx.y+j+1;
 if(k>=length || i>=P)return;
 U p=primes[i],v=digits[(U)j*length+k]%p;
 digits[(U)i*length+k]=mul(sub(digits[(U)i*length+k],v,p),inverses[j*P+i],p,nis[i]);
}
// Horner reconstruction into little-endian 64-bit limbs; up to80limbs (5120bits); P is independent of limb count.
extern "C" __global__ void pack(const U* digits,const U* primes,U* out,U length,int P,int limbs){
 U k=(U)blockIdx.x*blockDim.x+threadIdx.x;if(k>=length)return;
 U acc[80];for(int t=0;t<limbs;t++)acc[t]=0;
 for(int j=P-1;j>=0;j--){
  U carry=digits[(U)j*length+k];
  for(int t=0;t<limbs;t++){
   U lo=acc[t]*primes[j],hi=__umul64hi(acc[t],primes[j]);
   U v=lo+carry;carry=hi+(v<lo);acc[t]=v;
  }
 }
 for(int t=0;t<limbs;t++)out[k*(U)limbs+t]=acc[t];
}
