"""Compiled exact output/checking stage, independently checked against Python writer."""
import ctypes,json,shutil,subprocess,time,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
LIB=None
def write(data,c,state,path):
 global LIB
 if LIB is None:
  target=HERE/'libspin_output.so';source=HERE/'output.cpp'
  if not target.exists() or target.stat().st_mtime<source.stat().st_mtime:
   subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC',str(source),'-o',str(target),'-lgmpxx','-lgmp','-lcrypto'],check=True)
  LIB=ctypes.CDLL(str(target));LIB.write_counts.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_uint64]+[ctypes.c_int]*8
 if shutil.disk_usage(path.parent).free<12*1024**3+data.nbytes:raise RuntimeError('12GiB disk reserve')
 final=path;path=path.with_suffix(path.suffix+'.partial')
 receipt=path.with_suffix('.native.json');t=time.perf_counter()
 rc=LIB.write_counts(str(path).encode(),str(receipt).encode(),data.ctypes.data,len(data),data.shape[1],c['N'],c['bound'],c['step'],int(c['orientation']=='K_MAJOR'),state,c['fill'],len(c['ports']))
 if rc:raise ArithmeticError('Native output/checking failed')
 result=json.loads(receipt.read_text());path.replace(final);receipt.replace(final.with_suffix('.native.json'))
 fd=os.open(final.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
 result['write_and_readback_seconds']=time.perf_counter()-t
 return result
