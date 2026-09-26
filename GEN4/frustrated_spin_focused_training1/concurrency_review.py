"""Read-only actual kernel overlap for the three best original N96 repeats."""
import json,gzip,sys,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'frustrated_spin_n72_bench1'))
from concurrency import summary
def read(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
def scan(task):
    path,windows=task;spans=[];seen=0
    with path.open() as f:
        meta=json.loads(next(f));offset=meta['offset_ns'];lo=min(a for a,b in windows);hi=max(b for a,b in windows)
        for line in f:
            seen+=1;a,_,rest=line.partition(',');start=int(a)+offset
            if start>hi:continue
            b=rest.partition(',')[0];end=int(b)+offset
            if end<lo:continue
            if any(start<y and end>x for x,y in windows):spans.append((start/1e9,end/1e9))
    assert seen==meta['records'] and meta['dropped']==0
    return int(path.name[3:].split('_')[0]),spans,seen
def main():
    folder=P/sys.argv[1]/'ram';groups=read(folder/'GROUPED_EXPERIENCE.json');best=min([g for g in groups if g['group']=='G0-N96'],key=lambda g:g['total_ns']);ci=best['case']
    results=[read(folder/f'case{ci:03d}_r{r}.json.gz') for r in [1,2,3]];windows=[(r['execution']['ready_ns'],r['execution']['gpu_done_ns']) for r in results]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:rows=list(pool.map(scan,[(p,windows) for p in folder.glob('GPU*_KERNELS.csv')]))
    spans={d:ss for d,ss,n in rows};assert len(spans)==14
    out=dict(source_group='G0-N96',case=ci,method=best['method'],kernel_records=sum(n for d,ss,n in rows),zero_drops=True,scope='Fraction of wall time with an actual kernel active on each worker; not SM occupancy.',trials=[])
    for a,b in windows:
        lo,hi=a/1e9,b/1e9;trial=dict(full_arithmetic=summary(spans,lo,hi))
        if hi-lo>2:trial['middle_without_first_last_half_second']=summary(spans,lo+.5,hi-.5)
        out['trials'].append(trial)
    (P/(sys.argv[1]+'_CONCURRENCY.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
