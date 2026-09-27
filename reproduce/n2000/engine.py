"""Source-bound parallel joint rows with RAM staging and container-only custody."""
import collections, fcntl, gzip, hashlib, itertools, json, math, os
from pathlib import Path
import resource, shutil, struct, time
from math_core import b, o, j, x, ctx, prepare, encode, scalar, decode

P=Path(__file__).resolve().parent
C=json.loads((P/'CONFIG.json').read_text());ROOT=Path(os.environ['SPIN_WORK']);RAM=Path(os.environ['SPIN_RAM'])
CACHE={};FLUSH=None
MAGIC=b'GEMB001\n'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.part')
    with tmp.open('w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)


def initialize(threads,flush):
    global FLUSH
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
    ctx.threads=threads;FLUSH=flush
    RAM.mkdir(parents=True,exist_ok=True)


def source(family,n,fill):
    if n!=2000:
        c=j.source_recipe(dict(family=family,N=n));return c,dict(parent_source_sha256=c['source']['source_sha256'],N=n)
    folder=P/'inputs/N002000';manifest=folder/f'{family}_N002000_fill_{"plus" if fill==1 else "minus"}.json'
    d=json.loads(manifest.read_text());parent=folder/d['parent_record']
    for path in (manifest,parent,folder/d['couplings_file']):
        if sha(path)!=C['source_files'][path.name]:raise ValueError('Frozen source custody mismatch')
    c=json.load(gzip.open(parent,'rt'))
    if x.validate_source(c['source'])['source_sha256']!=d['parent_source_sha256']:raise ValueError('Parent binding')
    if c['ports']!=d['ordered_ports'] or fill!=d['fill_coupling']:raise ValueError('Ordered boundary/fill binding')
    return c,dict(parent_source_sha256=d['parent_source_sha256'],manifest_sha256=sha(manifest),
                  graph_sha256=d['graph_sha256'],raw_couplings_sha256=d['raw_couplings_sha256'],N=n)


def expected_moments(c,fill,state):
    n=c['source']['N'];ports=c['ports'];fixed={v:1 if state&(1<<i) else -1 for i,v in enumerate(ports)}
    weights={(u,v):q for u,v,q in c['source']['edges']};fields=c['source']['fields']
    def coupling(u,v):return weights.get((min(u,v),max(u,v)),fill)
    constant=-sum(fields[v]*spin for v,spin in fixed.items())
    constant-=sum(coupling(u,v)*fixed[u]*fixed[v] for u,v in itertools.combinations(ports,2))
    free=[v for v in range(n) if v not in fixed]
    variance=sum((fields[v]+sum(coupling(v,p)*s for p,s in fixed.items()))**2 for v in free)
    variance+=len(free)*(len(free)-1)//2*fill*fill
    variance+=sum(q*q-fill*fill for u,v,q in c['source']['edges'] if u not in fixed and v not in fixed)
    total=1<<(n-len(ports))
    return [total,total*constant,total*(constant*constant+variance)]


def read_binary(path):
    with Path(path).open('rb') as f:
        if f.read(8)!=MAGIC:raise ValueError('Binary magic')
        size=struct.unpack('<I',f.read(4))[0];header=json.loads(f.read(size));width=header['count_bytes'];length=8+width
        while True:
            buf=f.read(length)
            if not buf:break
            if len(buf)!=length:raise ValueError('Truncated exact row')
            e,m=struct.unpack('<ii',buf[:8]);yield e,m,int.from_bytes(buf[8:],'little')


def write_row(poly,plan,c,orientation,step,state,folder,identity):
    n=plan['N'];bound=plan['correction_bound'];fill=plan['fill'];width=(n+8)//8
    header=dict(schema='EXACT_G_E_M_B_BINARY_V1',N=n,state=state,ports=plan['ports'],fill=fill,
                count_bytes=width,record='int32_le_E,int32_le_M,unsigned_le_count',orientation=orientation,
                source_identity=identity,energy='E=Ec-J0*(M*M-N)/2',magnetization='M=sum spins')
    hbytes=json.dumps(header,sort_keys=True,separators=(',',':')).encode()
    prefix=MAGIC+struct.pack('<I',len(hbytes))+hbytes
    staged=RAM/f'{os.getpid()}_{state}_{time.time_ns()}.bin';path=folder/f'boundary_{state:04d}.bin'
    filehash=hashlib.sha256();buckets=[hashlib.sha256() for _ in range(n+1)]
    marginal=[0]*(n+1);moments=[0,0,0];records=0;last_t=[-1]*(n+1)
    t0=time.perf_counter();cpu=time.process_time()
    with staged.open('wb',buffering=4*1024**2) as f:
        f.write(prefix);filehash.update(prefix)
        # Never construct millions of Python tuples or decimal count strings.
        for index,value in enumerate(poly):
            if not value:continue
            if orientation=='K_MAJOR':k,t=divmod(index,bound//step+1)
            else:t,k=divmod(index,n+1)
            t*=step;count=int(value)
            if not (0<=k<=n and 0<=t<=bound and count>0 and t>last_t[k]):raise ArithmeticError('Exact coefficient closure')
            last_t[k]=t;ec=2*t-bound;m=2*k-n;e=ec-fill*((m*m-n)//2)
            countbytes=count.to_bytes(width,'little')
            record=struct.pack('<ii',e,m)+countbytes;f.write(record);filehash.update(record)
            buckets[k].update(struct.pack('<q',ec)+countbytes)
            marginal[k]+=count;moments[0]+=count;moments[1]+=e*count;moments[2]+=e*e*count;records+=1
    for k,count in enumerate(marginal):
        q=k-state.bit_count();expected=math.comb(n-len(plan['ports']),q) if 0<=q<=n-len(plan['ports']) else 0
        if count!=expected:raise ArithmeticError('Conditional magnetization marginal')
    if moments!=expected_moments(c,fill,state):raise ArithmeticError('Conditional count/first/second energy moment')
    canonical=hashlib.sha256(struct.pack('<II',n,state)+b''.join(h.digest() for h in buckets)).hexdigest()
    stage_seconds=time.perf_counter()-t0;stage_cpu=time.process_time()-cpu
    staged_size=staged.stat().st_size
    if shutil.disk_usage(ROOT).free<C['disk_reserve_bytes']+staged_size:raise RuntimeError('Container disk reserve')
    # Bound flush concurrency without writing live output to any network volume.
    if FLUSH is not None:FLUSH.acquire()
    try:
        flush0=time.perf_counter();tmp=path.with_name(path.name+'.part')
        with staged.open('rb') as src,tmp.open('wb',buffering=4*1024**2) as dst:
            shutil.copyfileobj(src,dst,4*1024**2);dst.flush();os.fsync(dst.fileno())
        if sha(tmp)!=filehash.hexdigest():raise ArithmeticError('Container readback checksum')
        tmp.replace(path)
        directory_fd=os.open(folder,os.O_DIRECTORY)
        try:os.fsync(directory_fd)
        finally:os.close(directory_fd)
        staged.unlink();flush_seconds=time.perf_counter()-flush0
    finally:
        if FLUSH is not None:FLUSH.release()
    row=dict(state=state,file=path.name,sha256=filehash.hexdigest(),joint_row_sha256=canonical,
             records=records,bytes=staged_size,moments=[str(v) for v in moments],
             plan_sha256=x.digest(plan),source_identity=identity,orientation=orientation,
             implementation_sha256=sha(__file__),math_core_sha256=sha(P/'math_core.py'),
             stage_seconds=stage_seconds,stage_cpu_seconds=stage_cpu,flush_seconds=flush_seconds)
    atomic(folder/f'boundary_{state:04d}.json',row)
    return row


def job(payload):
    start=time.perf_counter();cpu=time.process_time()
    family,n,fill,orientation=(payload[k] for k in ('family','N','fill','orientation'))
    folder=ROOT/payload['output']/f'N{n:06d}'/f'{family}_{fill:+d}'/orientation
    folder.mkdir(parents=True,exist_ok=True)
    key=(family,n,fill,orientation);c,identity=source(family,n,fill)
    results=[];computed=0
    for state in payload['states']:
        if (ROOT/'STOP').exists():break
        lock=(folder/f'boundary_{state:04d}.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        receipt=folder/f'boundary_{state:04d}.json'
        if receipt.exists():
            row=json.loads(receipt.read_text())
            if row['source_identity']!=identity or row['implementation_sha256']!=sha(__file__) or row['math_core_sha256']!=sha(P/'math_core.py'):
                raise ValueError('Checkpoint source/implementation changed')
            if sha(folder/row['file'])!=row['sha256']:raise ValueError('Checkpoint custody mismatch')
            results.append(row);lock.close();continue
        if CACHE.get('key')!=key:
            CACHE.clear()
            plan,parts,step=prepare(c,fill,orientation)
            factor=scalar(plan,parts,orientation,step)
            CACHE.update(key=key,plan=plan,parts=parts,step=step,factor=factor)
        plan,parts,step,factor=(CACHE[k] for k in ('plan','parts','step','factor'))
        root=encode(parts[0][1]['rows'][state],n,plan['correction_bound'],orientation,step)
        poly=root*factor;del root
        row=write_row(poly,plan,c,orientation,step,state,folder,identity);del poly
        results.append(row);computed+=1;lock.close()
    return dict(payload=payload,rows=results,computed_rows=computed,seconds=time.perf_counter()-start,
                cpu_seconds=time.process_time()-cpu,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,pid=os.getpid())
