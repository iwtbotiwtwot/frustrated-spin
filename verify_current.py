"""Verify current documentation alongside the original scientific publication checks."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    manifest_path=ROOT/'provenance/PUBLIC_MANIFEST.json'
    original=json.loads(manifest_path.read_text())
    overrides=json.loads((ROOT/'provenance/CURRENT_DOCUMENT_OVERRIDES.json').read_text())
    assert sha(manifest_path)==overrides['original_manifest_sha256']
    by={row['path']:row for row in original['files']}
    allowed={'README.md','PUBLICATION.md','CITATION.cff','.zenodo.json',
             'reproduce/n2000/README.md','reproduce/n4000/README.md','reproduce/n5000/README.md',
             'reproduce/n4000/DATA_MANIFEST.json','reproduce/n5000/DATA_MANIFEST.json'}
    assert len(overrides['files'])==len(allowed)
    assert {r['path'] for r in overrides['files']}==allowed
    metadata={'hosting_status','download_status','previous_hosting_status','historical_download_status','custody_update','distribution','public_access_scope'}
    for row in overrides['files']:
        prior=by[row['path']];old=ROOT/row['historical_copy'];current=ROOT/row['path']
        assert row['original_sha256']==prior['sha256'] and row['original_bytes']==prior['bytes']
        assert old.stat().st_size==prior['bytes'] and sha(old)==prior['sha256']
        assert current.stat().st_size==row['current_bytes'] and sha(current)==row['current_sha256']
        if current.name=='DATA_MANIFEST.json':
            a=json.loads(old.read_text());b=json.loads(current.read_text())
            assert {k:v for k,v in a.items() if k not in metadata}=={k:v for k,v in b.items() if k not in metadata}
        prior['bytes']=row['current_bytes'];prior['sha256']=row['current_sha256']
    # Reuse the unchanged original verifier and all of its scientific checks.
    ns={'__file__':str(ROOT/'verify_publication.py'),'__name__':'retained_publication_verifier'}
    exec(compile((ROOT/'verify_publication.py').read_text(),ns['__file__'],'exec'),ns)
    old_load=ns['load']
    def load(path):
        return original if Path(path)==manifest_path else old_load(path)
    ns['load']=load
    ns['main']()
    print(json.dumps({'status':'PASS','preserved_original_documents':len(allowed),'current_document_overrides':len(allowed),'scientific_manifest_changes':0}))
if __name__=='__main__':main()
