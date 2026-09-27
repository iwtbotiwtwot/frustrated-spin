"""Lossless gzip level-1 receipt/result writer, local to resumed worker processes."""
import os,json,gzip,time
from pathlib import Path
from SAM_PROJECT import receipt_storage as storage

def write_record(path,data,mode):
    if mode=='plain':return storage.write_record(path,data,mode)
    if mode!='gzip':raise ValueError('Unsupported receipt storage mode')
    path=Path(path);logical={'sha256':storage.digest(data),'bytes':len(data)}
    blob=gzip.compress(data,compresslevel=1,mtime=0);blob_path=path.with_suffix(path.suffix+'.gz')
    storage.write_bytes(blob_path,blob)
    descriptor=dict(schema=storage.SCHEMA,codec='gzip',file=blob_path.name,compressed_bytes=len(blob),
        compressed_sha256=storage.digest(blob),logical_bytes=len(data),logical_sha256=logical['sha256'])
    storage.write_bytes(path,(json.dumps(descriptor,indent=2,sort_keys=True)+'\n').encode())
    return logical

def initialize(config):
    import profile_hooks,campaign
    from SAM_PROJECT import session
    profile_hooks.initialize(config)
    session.write_record=write_record
    def write_gz(path,obj):
        start=time.perf_counter();cpu=time.process_time()
        try:
            path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.part')
            # Exact same compact JSON bytes as the original writer.
            blob=gzip.compress(json.dumps(obj,separators=(',',':')).encode(),compresslevel=1,mtime=0)
            with tmp.open('wb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
            tmp.replace(path)
        finally:
            profile_hooks.MEASURE['result_serialize_compress_fsync_seconds']=time.perf_counter()-start
            profile_hooks.MEASURE['result_serialize_compress_cpu_seconds']=time.process_time()-cpu
            profile_hooks.MEASURE['gzip_level']=1
    campaign.write_gz=write_gz

def test():
    import tempfile,hashlib
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'OUTPUT.json';raw=(json.dumps({'integer':str(2**1350),'exact':True})+'\n').encode()*1000
        logical=write_record(p,raw,'gzip')
        assert storage.read_record(p,'gzip')==raw
        assert logical['sha256']==hashlib.sha256(raw).hexdigest()
        blob=p.with_suffix('.json.gz');bad=bytearray(blob.read_bytes());bad[-1]^=1;blob.write_bytes(bad)
        try:storage.read_record(p,'gzip')
        except ValueError:pass
        else:raise AssertionError('Corrupted receipt accepted')
    return dict(status='PASS',unchanged_reader_exact_round_trip=True,corrupted_blob_rejected=True)
