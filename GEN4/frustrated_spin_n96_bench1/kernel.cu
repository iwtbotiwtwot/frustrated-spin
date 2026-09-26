
extern "C" __global__ void step(const unsigned long long* fs,const unsigned long long* ms,const unsigned int* bits,unsigned int* out,unsigned long long n,int batch,int nf,unsigned int p,unsigned long long reciprocal){
 unsigned long long i=(unsigned long long)blockIdx.x*blockDim.x+threadIdx.x;
 if(i>=n)return;
 unsigned long long row=i/batch;unsigned int root=i%batch;unsigned long long a=1,b=1;
 for(int k=0;k<nf;k++){
 const unsigned int* f=(const unsigned int*)fs[k];const unsigned int* m=(const unsigned int*)ms[k];
 unsigned long long z=m[row],o=z|bits[k];
 unsigned long long v=a*f[z*batch+root],q=__umul64hi(v,reciprocal);a=v-q*p;if(a>=p)a-=p;
 v=b*f[o*batch+root];q=__umul64hi(v,reciprocal);b=v-q*p;if(b>=p)b-=p;
 }
 unsigned long long s=a+b;out[i]=(unsigned int)(s>=p?s-p:s);
}
