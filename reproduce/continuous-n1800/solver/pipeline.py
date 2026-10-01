"""One CUDA service, bounded shared-RAM results, independent CPU consumers."""
import os,time,traceback,collections
import multiprocessing as mp
from multiprocessing.connection import wait
from multiprocessing.shared_memory import SharedMemory
import numpy as np
CONNECTION=None

class RemoteArray:
 def __init__(self,meta):
  self.shm=SharedMemory(name=meta['name']);self.name=meta['name'];self.data=np.ndarray(meta['shape'],dtype=np.uint64,buffer=self.shm.buf)
  if meta['indices'] is not None:self.indices=np.ndarray((meta['indices'],),dtype=np.int64,buffer=self.shm.buf,offset=self.data.nbytes)
 def __iter__(self):return iter(self.data)
 def release(self):
  del self.data
  if hasattr(self,'indices'):del self.indices
  self.shm.close();self.shm.unlink();CONNECTION.send(('release',self.name))

class Client:
 def solve(self,factors,bits):
  start=time.perf_counter();CONNECTION.send(('solve',factors,bits))
  if not CONNECTION.poll(1800):raise TimeoutError('GPU service did not return within1800seconds')
  msg=CONNECTION.recv()
  if msg[0]=='error':raise RuntimeError(msg[1])
  _,meta,stats=msg;stats['pipeline_roundtrip_seconds']=time.perf_counter()-start
  return RemoteArray(meta),stats

def init_worker(out,connections,counter):
 global CONNECTION
 with counter.get_lock():idx=counter.value;counter.value+=1
 CONNECTION=connections[idx]
 import sys
 runner=sys.modules["__main__"]
 assert hasattr(runner,"work")
 runner.init(out);runner.GPU=Client()

def serve(connections,cache_budget,solve_count):
 from gpu import Backend
 import cupy as cp
 backends=collections.OrderedDict();allocated=set();solves=0;started=time.perf_counter()
 try:
  while True:
   for conn in wait(connections):
    try:msg=conn.recv()
    except EOFError:connections.remove(conn);continue
    if msg[0]=='stop':return
    if msg[0]=='release':allocated.discard(msg[1]);continue
    assert msg[0]=='solve';_,factors,bits=msg
    try:
     if conn not in backends:backends[conn]=Backend()
     backend=backends[conn];backends.move_to_end(conn)
     while sum(b.cache.nbytes if b.cache is not None else 0 for b in backends.values())>cache_budget:
      victim=next((c for c in backends if c is not conn),None)
      if victim is None:break
      backends.pop(victim).clear()
     while True:
      try:data,stats=backend.solve(factors,bits);break
      except (MemoryError,cp.cuda.memory.OutOfMemoryError):
       victim=next((c for c in backends if c is not conn),None)
       if victim is None:raise
       backends.pop(victim).clear()
     array=data.data if hasattr(data,'indices') else data;indices=data.indices if hasattr(data,'indices') else None
     size=array.nbytes+(indices.nbytes if indices is not None else 0)
     # One result per client is live; shared-RAM capacity is checked before allocation.
     st=os.statvfs('/dev/shm');assert size<st.f_bavail*st.f_frsize*.9,'Shared RAM capacity exhausted'
     shm=SharedMemory(create=True,size=size);allocated.add(shm.name);target=np.ndarray(array.shape,dtype=np.uint64,buffer=shm.buf);target[:]=array
     if indices is not None:
      target_indices=np.ndarray(indices.shape,dtype=np.int64,buffer=shm.buf,offset=array.nbytes);target_indices[:]=indices;del target_indices
     meta=dict(name=shm.name,shape=array.shape,indices=len(indices) if indices is not None else None);del target;shm.close();del data,array,indices
     solves+=1;solve_count.value=solves;stats['service_solves']=solves;conn.send(('ok',meta,stats))
    except BaseException:conn.send(('error',traceback.format_exc()))
 finally:
  for name in allocated:
   try:s=SharedMemory(name=name);s.close();s.unlink()
   except FileNotFoundError:pass
  print('GPU_SERVICE_STOP',solves,time.perf_counter()-started,flush=True)

class Service:
 def __init__(self,workers,cache_budget):
  # Start one shared resource tracker before forking CUDA service/CPU workers.
  s=SharedMemory(create=True,size=1);s.close();s.unlink()
  self.ctx=mp.get_context('fork');pairs=[self.ctx.Pipe() for _ in range(workers)];self.clients=[p[0] for p in pairs];servers=[p[1] for p in pairs]
  self.counter=self.ctx.Value('i',0);self.solves=self.ctx.Value('q',0);self.process=self.ctx.Process(target=serve,args=(servers,cache_budget,self.solves));self.process.start()
 def close(self):
  if self.process.is_alive():self.clients[0].send(('stop',))
  self.process.join(30)
  if self.process.is_alive():self.process.terminate();self.process.join()
