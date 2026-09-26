"""Exact whole-run kernel overlap from all fourteen CUPTI traces (read-only)."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import json,gzip,sys,concurrent.futures
from pathlib import Path
import numpy as np

def scan(task):
    path,lo,hi=task
    with path.open() as f:meta=json.loads(next(f))
    a=np.loadtxt(path,delimiter=',',skiprows=1,usecols=(0,1),dtype=np.int64)
    assert len(a)==meta['records'] and meta['dropped']==0
    a+=meta['offset_ns'];a=a[(a[:,0]<hi)&(a[:,1]>lo)];a[:,0]=np.maximum(a[:,0],lo);a[:,1]=np.minimum(a[:,1],hi)
    if np.any(a[1:,0]<a[:-1,0]):a=a[np.argsort(a[:,0],kind='stable')]
    # Reduce the union, including overlapping concurrent kernels on a worker.
    running_end=np.maximum.accumulate(a[:,1]);starts=np.r_[0,np.flatnonzero(a[1:,0]>running_end[:-1])+1]
    ends=np.r_[starts[1:]-1,len(a)-1];a=np.column_stack((a[starts,0],running_end[ends]))
    return int(path.name[3:].split('_')[0]),a,meta['records']

def summary(rows,lo,hi):
    spans={d:a[(a[:,0]<hi)&(a[:,1]>lo)].copy() for d,a in rows.items()}
    for a in spans.values():a[:,0]=np.maximum(a[:,0],lo);a[:,1]=np.minimum(a[:,1],hi)
    n=sum(len(a) for a in spans.values());times=np.empty(2*n,dtype=np.int64);deltas=np.empty(2*n,dtype=np.int8);i=0
    duty={}
    for d,a in spans.items():
        m=len(a);times[i:i+m]=a[:,0];deltas[i:i+m]=1;i+=m;times[i:i+m]=a[:,1];deltas[i:i+m]=-1;i+=m
        duty[d]=int(np.sum(a[:,1]-a[:,0]))/(hi-lo)
    order=np.argsort(times,kind='stable');times=times[order];deltas=deltas[order];del order
    counts=np.cumsum(deltas,dtype=np.int64);assert counts[-1]==0 and counts.min()>=0 and counts.max()<=14
    widths=np.diff(times);hist=np.bincount(counts[:-1],weights=widths,minlength=15);hist[0]+=times[0]-lo+hi-times[-1]
    assert int(hist.sum())==hi-lo
    return dict(window_seconds=(hi-lo)/1e9,mean_gpu_busy_fraction=sum(duty.values())/14,all14_busy_fraction=float(hist[14]/(hi-lo)),atleast13_busy_fraction=float(hist[13:].sum()/(hi-lo)),busy_fraction_by_worker=duty,active_count_seconds={str(k):float(v/1e9) for k,v in enumerate(hist)})

if __name__=='__main__':
    p=Path(sys.argv[1]);result=json.load(gzip.open(p/'RESULT1.json.gz'));e=result['execution'];lo=e['ready_ns'];hi=e['gpu_done_ns']
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:raw=list(pool.map(scan,[(f,lo,hi) for f in p.glob('GPU*_KERNELS.csv')]))
    rows={d:a for d,a,n in raw};assert len(rows)==14
    out=dict(kernel_records=sum(n for d,a,n in raw),zero_dropped_records=True,scope='Exact fraction of time with actual kernel activity per worker; not SM occupancy. Full arithmetic includes checkpoint stalls.',full_arithmetic=summary(rows,lo,hi),middle_without_first_last_second=summary(rows,lo+10**9,hi-10**9))
    (p/'CONCURRENCY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
