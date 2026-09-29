"""Verify/restore locally supplied N5000 zstd shards and stream exact records."""
import argparse,hashlib,json,struct,subprocess,os
from pathlib import Path

def records(path):
    """Read a headerless N5000 GPU .bin file, yielding exact Python integers."""
    with Path(path).open('rb') as f:
        while buf:=f.read(634):
            if len(buf)!=634:raise ValueError('Truncated N5000 record')
            e,m=struct.unpack('<ii',buf[:8]);yield e,m,int.from_bytes(buf[8:],'little')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('directory',type=Path);ap.add_argument('--manifest',type=Path,required=True,help='Completed archive MANIFEST.json or batch DOWNLOAD_STATUS.json')
    ap.add_argument('--deep',action='store_true');ap.add_argument('--restore',type=Path);a=ap.parse_args()
    manifest=json.loads(a.manifest.read_text());checked=0
    for r in manifest['shards']:
        path=a.directory/r['file']
        if path.name!=r['file'] or Path(r['raw_file']).name!=r['raw_file']:raise ValueError('Unsafe shard path')
        with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        if path.stat().st_size!=r['bytes'] or digest!=r['sha256']:raise ValueError('Compressed checksum: '+str(path))
        if a.deep or a.restore:
            out=None;part=None;h=hashlib.sha256();size=0
            if a.restore:
                a.restore.mkdir(parents=True,exist_ok=True);dest=a.restore/r['raw_file']
                if dest.exists():raise FileExistsError(dest)
                part=dest.with_suffix('.bin.part');out=part.open('wb')
            try:
                with subprocess.Popen(['zstd','-q','-d','-c',str(path)],stdout=subprocess.PIPE) as p:
                    while chunk:=p.stdout.read(8*1024**2):
                        h.update(chunk);size+=len(chunk)
                        if out:out.write(chunk)
                    if p.wait()!=0:raise ValueError('zstd decompression failed')
            finally:
                if out:out.close()
            if size!=r['raw_bytes'] or h.hexdigest()!=r['raw_sha256']:raise ValueError('Raw checksum: '+str(path))
            if part:
                part.replace(dest)
                for row in r.get('logical_rows',[]):
                    name=row['raw_file']
                    if Path(name).name!=name:raise ValueError('Unsafe logical row path')
                    alias=a.restore/name
                    if alias==dest:continue
                    if alias.exists():raise FileExistsError(alias)
                    os.link(dest,alias)
        checked+=1
    print(json.dumps(dict(status='PASS',shards=checked,deep=bool(a.deep or a.restore))))

if __name__=='__main__':main()
