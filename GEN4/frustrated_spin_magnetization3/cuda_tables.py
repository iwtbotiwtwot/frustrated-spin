"""Small exact integer enumeration on the available CUDA device, via driver/NVRTC."""
import ctypes as C
import time
import numpy as np

KERNEL = r'''
extern "C" __global__ void enumerate_joint(int n,int ne,const int* edges,
 const int* fields,int np,const int* ports,int bound,unsigned long long* out) {
 unsigned int a=blockIdx.x*blockDim.x+threadIdx.x;
 if(a >= (1u<<n)) return;
 int energy=0, state=0;
 for(int i=0;i<ne;i++) {
  int u=edges[3*i],v=edges[3*i+1],j=edges[3*i+2];
  int su=2*((a>>u)&1u)-1,sv=2*((a>>v)&1u)-1;
  energy-=j*su*sv;
 }
 for(int i=0;i<n;i++) energy-=fields[i]*(2*int((a>>i)&1u)-1);
 for(int i=0;i<np;i++) state|=((a>>ports[i])&1u)<<i;
 int k=__popc(a),t=(energy+bound)/2;
 out[a]=((unsigned long long)state*(n+1)+k)*(bound+1)+t;
}
'''

def checked(fn,*args):
    r=fn(*args)
    if r:raise RuntimeError(f'{fn.__name__}: CUDA/NVRTC status {r}')

class CUDA:
    def __init__(self):
        start=time.perf_counter();self.driver=C.CDLL('libcuda.so.1')
        d=self.driver;checked(d.cuInit,0);count=C.c_int();checked(d.cuDeviceGetCount,C.byref(count))
        assert count.value==1,f'Expected one available CUDA device, found {count.value}'
        self.dev=C.c_int();checked(d.cuDeviceGet,C.byref(self.dev),0)
        name=C.create_string_buffer(256);checked(d.cuDeviceGetName,name,256,self.dev)
        major,minor=C.c_int(),C.c_int()
        checked(d.cuDeviceGetAttribute,C.byref(major),75,self.dev)
        checked(d.cuDeviceGetAttribute,C.byref(minor),76,self.dev)
        self.context=C.c_void_p();checked(d.cuDevicePrimaryCtxRetain,C.byref(self.context),self.dev)
        checked(d.cuCtxSetCurrent,self.context)
        free,total=C.c_size_t(),C.c_size_t();checked(d.cuMemGetInfo_v2,C.byref(free),C.byref(total))
        assert free.value>256*1024**2,'Insufficient free GPU memory'
        uuid=C.create_string_buffer(16);checked(d.cuDeviceGetUuid_v2,C.byref(uuid),self.dev)
        self.identity=dict(name=name.value.decode(),compute_capability=[major.value,minor.value],
            cuda_device_uuid_bytes=bytes(uuid).hex(),visible_devices=count.value,free_bytes=free.value,total_bytes=total.value)
        nv=C.CDLL('/usr/local/cuda/lib64/libnvrtc.so');program=C.c_void_p()
        checked(nv.nvrtcCreateProgram,C.byref(program),KERNEL.encode(),b'exact_joint.cu',0,None,None)
        opts=(C.c_char_p*2)(f'--gpu-architecture=compute_{major.value}{minor.value}'.encode(),b'--std=c++11')
        status=nv.nvrtcCompileProgram(program,2,opts)
        if status:
            size=C.c_size_t();nv.nvrtcGetProgramLogSize(program,C.byref(size));log=C.create_string_buffer(size.value);nv.nvrtcGetProgramLog(program,log)
            raise RuntimeError(log.value.decode())
        size=C.c_size_t();checked(nv.nvrtcGetPTXSize,program,C.byref(size));ptx=C.create_string_buffer(size.value)
        checked(nv.nvrtcGetPTX,program,ptx);checked(nv.nvrtcDestroyProgram,C.byref(program))
        self.module=C.c_void_p();checked(d.cuModuleLoadData,C.byref(self.module),ptx)
        self.function=C.c_void_p();checked(d.cuModuleGetFunction,C.byref(self.function),self.module,b'enumerate_joint')
        self.initialization_seconds=time.perf_counter()-start

    def enumerate(self,n,edges,fields,ports):
        assert 1<=n<=18 and len(ports)<=6
        bound=sum(abs(e[2]) for e in edges)+sum(map(abs,fields))
        assert bound<2**20
        start=time.perf_counter();d=self.driver;allocated=[]
        def alloc(size):
            p=C.c_uint64();checked(d.cuMemAlloc_v2,C.byref(p),C.c_size_t(max(4,size)));allocated.append(p);return p
        def upload(values):
            a=np.asarray(values,dtype=np.int32);p=alloc(a.nbytes)
            if a.nbytes:checked(d.cuMemcpyHtoD_v2,p,C.c_void_p(a.ctypes.data),C.c_size_t(a.nbytes))
            return p
        try:
            ep=upload(edges);fp=upload(fields);pp=upload(ports)
            out=np.empty(1<<n,dtype=np.uint64);op=alloc(out.nbytes)
            args=[C.c_int(n),C.c_int(len(edges)),ep,fp,C.c_int(len(ports)),pp,C.c_int(bound),op]
            params=(C.c_void_p*len(args))(*[C.cast(C.byref(x),C.c_void_p) for x in args])
            prepared=time.perf_counter()
            checked(d.cuLaunchKernel,self.function,(len(out)+255)//256,1,1,256,1,1,0,None,params,None)
            checked(d.cuCtxSynchronize);computed=time.perf_counter()
            checked(d.cuMemcpyDtoH_v2,C.c_void_p(out.ctypes.data),op,C.c_size_t(out.nbytes));read=time.perf_counter()
            keys,counts=np.unique(out,return_counts=True);rows={}
            for key,count in zip(keys,counts):
                sk,t=divmod(int(key),bound+1);state,k=divmod(sk,n+1)
                rows.setdefault(state,{})[(k,t)]=int(count)
            return rows,dict(upload_seconds=prepared-start,gpu_arithmetic_seconds=computed-prepared,
                readout_seconds=read-computed,histogram_seconds=time.perf_counter()-read,
                gpu_output_bytes=out.nbytes,assignments=len(out))
        finally:
            for ptr in allocated:checked(d.cuMemFree_v2,ptr)

    def close(self):
        checked(self.driver.cuModuleUnload,self.module)
        checked(self.driver.cuDevicePrimaryCtxRelease_v2,self.dev)
