"""Source-bound N96: 32 branch graphs, packed inputs, two resident VRAM banks."""
import numpy as np
from pathlib import Path
TERMINAL=r'''
extern "C" __global__ void finish(const unsigned long long* fs,const unsigned long long* maps,unsigned long long* out,const unsigned int* shifts,int nf,int batch,unsigned int prime,int reset){
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=16*batch)return;int state=i/batch,root=i%batch;unsigned long long value=1;
 for(int f=0;f<nf;f++){const unsigned int* values=(const unsigned int*)fs[f];const unsigned int* idx=(const unsigned int*)maps[f];value=value*values[idx[state]*batch+root]%prime;}
 value=value*shifts[root]%prime;out[i]=reset?value:(out[i]+value)%prime;
}
'''
class GPUWorker:
 def __init__(self,device,a,templates,desc,cache,batch):
  import cupy as cp
  cp.cuda.Device(device).use();self.cp=cp;self.a=a;self.templates=templates;self.batch=batch;self.engine=a.n96_engine;self.exact=self.engine.retained_engine._modules()[1]
  kernel=cp.RawKernel(Path(__file__).with_name('kernel.cu').read_text(),'step');kernel.compile();finish=cp.RawKernel(TERMINAL,'finish');finish.compile()
  self.maps=[[cp.asarray(m,dtype=cp.uint32) for m in group] for group in cache.maps]
  self.bits=[cp.asarray([x['eliminated_factor_bit'] for x in s['maps']],dtype=cp.uint32) for s in desc['steps']]
  self.pointers=[cp.asarray([m.data.ptr for m in group],dtype=cp.uint64) for group in self.maps]
  points=self.engine.zeta_points(self.engine.PRIMES[0],1024,0,batch)
  prototype=[self.exact._initial_factors(t.local_instance,points,self.engine.PRIMES[0]) for t in templates]
  self.layout=[];offset=0
  for fs in prototype:
   row=[]
   for f in fs:
    shape=f.values.shape;n=int(np.prod(shape));row.append((tuple(f.scope),shape,offset,offset+n));offset+=n
   assert a.canonical_sha256([list(x[0]) for x in row])==desc['initial_factor_scope_sha256'];self.layout.append(row)
  self.input_count=offset;self.banks=[]
  for bank_id in range(2):
   packed=cp.empty(offset,dtype=cp.uint32);shifts=cp.empty((len(templates),batch),dtype=cp.uint32);terminal=cp.empty((16,batch),dtype=cp.uint64)
   outputs=[cp.empty((s['output_count'],batch),dtype=cp.uint32) for s in desc['steps']]
   branch_steps=[];keep=[]
   for ti,layout in enumerate(self.layout):
    factors=[(scope,packed[lo:hi].reshape(shape)) for scope,shape,lo,hi in layout];steps=[]
    for si,s in enumerate(desc['steps']):
     selected=[f for f in factors if s['vertex'] in f[0]];factors=[f for f in factors if s['vertex'] not in f[0]]
     assert [list(f[0]) for f in selected]==[x['factor_scope'] for x in s['maps']]
     ptr=cp.asarray([v.data.ptr for _,v in selected],dtype=cp.uint64);keep.append(ptr);steps.append((si,ptr,len(selected)))
     factors.append((tuple(s['output_scope']),outputs[si]))
    idx=[cp.asarray(self.engine.retained_engine._project_indices(np.arange(16,dtype=np.uint64),templates[ti].port_order,scope),dtype=cp.uint32) for scope,_ in factors]
    ptr=cp.asarray([v.data.ptr for _,v in factors],dtype=cp.uint64);ip=cp.asarray([v.data.ptr for v in idx],dtype=cp.uint64);keep.extend([*idx,ptr,ip]);branch_steps.append((steps,ptr,ip,len(factors)))
   cp.cuda.get_current_stream().synchronize();stream=cp.cuda.Stream(non_blocking=True);graphs=[]
   for prime in self.engine.PRIMES:
    with stream:
     stream.begin_capture()
     for ti,(steps,ptr,ip,nf) in enumerate(branch_steps):
      for si,fp,nfstep in steps:
       out=outputs[si];n=out.size
       kernel(((n+255)//256,),(256,),(fp,self.pointers[si],self.bits[si],out,np.uint64(n),np.int32(batch),np.int32(nfstep),np.uint32(prime),np.uint64((1<<64)//prime)))
      finish(((terminal.size+255)//256,),(256,),(ptr,ip,terminal,shifts[ti],np.int32(nf),np.int32(batch),np.uint32(prime),np.int32(ti==0)))
     graphs.append(stream.end_capture())
   self.banks.append({'packed':packed,'shifts':shifts,'terminal':terminal,'graphs':graphs,'keep':keep,'outputs':outputs})
  self.copy_stream=cp.cuda.Stream(non_blocking=True);self.nextbank=0
 def prepare(self,task):
  pi,lo,hi=task;assert hi-lo==self.batch;prime=self.engine.PRIMES[pi];points=self.engine.zeta_points(prime,1024,lo,hi)
  packed=np.empty(self.input_count,dtype=np.uint32);shifts=np.empty((len(self.templates),self.batch),dtype=np.uint32)
  for ti,(template,layout) in enumerate(zip(self.templates,self.layout)):
   fs=self.exact._initial_factors(template.local_instance,points,prime);assert len(fs)==len(layout)
   for f,(scope,shape,begin,end) in zip(fs,layout):
    assert tuple(f.scope)==scope and f.values.shape==shape;packed[begin:end]=f.values.reshape(-1)
   shifts[ti]=[pow(int(x),template.z_degree_shift,prime) for x in points]
  bank=self.banks[self.nextbank];self.nextbank=1-self.nextbank
  with self.copy_stream:
   bank['packed'].set(packed,stream=self.copy_stream);bank['shifts'].set(shifts,stream=self.copy_stream);event=self.cp.cuda.Event();event.record()
  return task,bank,event,packed,shifts
 def launch(self,prepared):
  task,bank,event,*_=prepared;stream=self.cp.cuda.get_current_stream();stream.wait_event(event)
  start=self.cp.cuda.Event();end=self.cp.cuda.Event();start.record();bank['graphs'][task[0]].launch(stream);end.record();return start,end
 def result(self,prepared,events):
  v=self.cp.asnumpy(prepared[1]['terminal']).astype(np.int64);ms=self.cp.cuda.get_elapsed_time(*events);return v,ms
