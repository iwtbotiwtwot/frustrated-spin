"""Verify downloaded public N2000 shards and optionally restore original binaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct

HERE=Path(__file__).resolve().parent

def records(path):
    """Yield exact (E, M, count) Python integers from one restored boundary file."""
    with Path(path).open('rb') as f:
        if f.read(8)!=b'GEMB001\n':raise ValueError('Binary magic mismatch')
        size=f.read(4)
        if len(size)!=4:raise ValueError('Truncated header length')
        length=struct.unpack('<I',size)[0]
        if length>1024*1024:raise ValueError('Invalid header size')
        header=f.read(length)
        if len(header)!=length:raise ValueError('Truncated header')
        info=json.loads(header);width=info['count_bytes'];size=8+width
        if width!=(info['N']+8)//8 or width<1:raise ValueError('Invalid count width')
        while True:
            block=f.read(size)
            if not block:break
            if len(block)!=size:raise ValueError('Truncated record')
            e,m=struct.unpack('<ii',block[:8]);yield e,m,int.from_bytes(block[8:],'little')

def check(row,directory,restore=None,deep=False):
    source=directory/row['asset']
    with source.open('rb') as f:compressed=hashlib.file_digest(f,'sha256').hexdigest()
    if source.stat().st_size!=row['bytes'] or compressed!=row['sha256']:
        raise ValueError('Compressed shard mismatch: '+str(source))
    if not deep and restore is None:return
    target=restore/row['restored_path'] if restore else None
    tmp=None;out=None
    if target:
        target.parent.mkdir(parents=True,exist_ok=True)
        tmp=target.with_name(target.name+'.part');out=tmp.open('wb')
    h=hashlib.sha256();length=0
    try:
        with subprocess.Popen(['zstd','-q','-dc',str(source)],stdout=subprocess.PIPE) as process:
            for block in iter(lambda:process.stdout.read(8<<20),b''):
                h.update(block);length+=len(block)
                if out:out.write(block)
            if process.wait()!=0:raise ValueError('Zstandard decompression failed')
        if length!=row['restored_bytes'] or h.hexdigest()!=row['restored_sha256']:
            raise ValueError('Restored shard mismatch: '+str(source))
        if out:out.flush();os.fsync(out.fileno());out.close();out=None;os.replace(tmp,target)
    finally:
        if out:out.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path,help='Directory containing the 96 public *.bin.zst files')
    p.add_argument('--restore',type=Path,help='Restore exact original binaries under this directory')
    p.add_argument('--deep',action='store_true',help='Also decompress and check original SHA256 without retaining raw files')
    p.add_argument('--download',action='store_true',help='Download selected public Drive files using pinned requirements-download.txt')
    p.add_argument('--case',choices=('packet_+1','packet_-1','signed_packet_+1','signed_packet_-1','signed_packet_chain_+1','signed_packet_chain_-1'))
    p.add_argument('--state',type=int,choices=range(16))
    args=p.parse_args();rows=json.loads((HERE/'DATA_MANIFEST.json').read_text())['rows']
    selected=[r for r in rows if (args.case is None or Path(r['restored_path']).parts[2]==args.case)
              and (args.state is None or Path(r['restored_path']).name==f'boundary_{args.state:04d}.bin')]
    for i,row in enumerate(selected,1):
        if args.download:
            import gdown
            args.directory.mkdir(parents=True,exist_ok=True)
            target=args.directory/row['asset']
            ready=False
            if target.exists() and target.stat().st_size==row['bytes']:
                with target.open('rb') as f:ready=hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
            if not ready:
                file_id=row.get('drive_file_id')
                if not file_id:raise ValueError('No confirmed public Drive file ID for '+row['asset'])
                if target.exists():
                    raise ValueError('Existing final file differs; preserve or remove it explicitly before retrying: '+str(target))
                partial=target.with_name(target.name+'.download')
                result=gdown.download(id=file_id,output=str(partial),quiet=False,use_cookies=False,resume=True)
                if result is None:raise RuntimeError('Drive download failed; no successful verification is claimed')
                with partial.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
                if partial.stat().st_size!=row['bytes'] or actual!=row['sha256']:
                    raise ValueError('Downloaded data differ; partial file retained: '+str(partial))
                os.replace(partial,target)
        check(row,args.directory,args.restore,args.deep)
        print(json.dumps(dict(status='PASS',file=row['asset'],completed=i,total=len(selected))),flush=True)

if __name__=='__main__':main()
