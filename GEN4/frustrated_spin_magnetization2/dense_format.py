"""Exact complete signed graph: one explicit sign bit for every unordered pair."""
import gzip,hashlib,json
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
def filehash(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def index(n,u,v):
    assert 0<=u<v<n
    return u*(2*n-u-1)//2+v-u-1
def generate(n,edges,fill):
    assert fill in (-1,1)
    count=n*(n-1)//2;raw=bytearray([255 if fill==1 else 0])*((count+7)//8)
    if count%8:raw[-1]&=(1<<(count%8))-1
    for u,v,j in edges:
        assert j in (-1,1)
        k=index(n,u,v);mask=1<<(k%8)
        if j==1:raw[k//8]|=mask
        else:raw[k//8]&=255^mask
    return raw
def validate(raw,n,edges,fill):
    count=n*(n-1)//2
    assert len(raw)==(count+7)//8
    if count%8:assert raw[-1]>>(count%8)==0,'NONZERO_PADDING'
    seen=set();positive_parent=0
    for u,v,j in edges:
        assert 0<=u<v<n and (u,v) not in seen and j in (-1,1)
        seen.add((u,v));k=index(n,u,v)
        assert (1 if raw[k//8]&(1<<(k%8)) else -1)==j,'PARENT_COUPLING_CHANGED'
        positive_parent+=j==1
    positives=int.from_bytes(raw,'little').bit_count()
    expected=(count-len(edges)+positive_parent) if fill==1 else positive_parent
    assert positives==expected,'MISSING_PAIR_COUPLING_CHANGED'
    # For fill +1 all missing bits must be positive; for fill -1 none can be.
    # Together with individual parent checks this verifies every stored coupling.
    return dict(pair_count=count,positive_couplings=positives,negative_couplings=count-positives,
        parent_couplings_preserved=len(edges),all_missing_pairs_verified=True,padding_verified=True)
def iter_edges(n,raw):
    k=0
    for u in range(n):
        for v in range(u+1,n):
            yield [u,v,1 if raw[k//8]&(1<<(k%8)) else -1]
            k+=1
def export(manifest,output):
    manifest=Path(manifest);d=json.loads(manifest.read_text());raw=gzip.decompress((manifest.parent/d['couplings_file']).read_bytes())
    assert sha(raw)==d['raw_couplings_sha256'];assert len(raw)==(d['pair_count']+7)//8
    opener=gzip.open if str(output).endswith('.gz') else open
    with opener(output,'wt') as f:
        f.write('{"N":'+str(d['N'])+',"fields":'+json.dumps(d['fields'])+',"parent_vertices":'+json.dumps(d['parent_vertices'])+',"family":'+json.dumps(d['key'])+',"edges":[')
        first=True
        for e in iter_edges(d['N'],raw):
            if not first:f.write(',')
            f.write(json.dumps(e,separators=(',',':')));first=False
        f.write(']}\n')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('manifest');ap.add_argument('output');a=ap.parse_args();export(a.manifest,a.output)
