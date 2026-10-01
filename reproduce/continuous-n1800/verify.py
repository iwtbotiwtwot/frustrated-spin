"""Independent publication checks; no new numerical production or runtime download."""
import argparse, csv, gzip, hashlib, json, math, tarfile, urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def check_record(folder,item):
    receipt=json.loads((folder/'RECEIPT.json').read_text())
    path=folder/'RECORD.json.gz'
    assert sha(path)==item['record_sha256']==receipt['record_sha256']
    assert sha(folder/'RECEIPT.json')==item['receipt_sha256']
    assert path.stat().st_size==item['record_bytes']==receipt['record_bytes']
    record=json.load(gzip.open(path,'rt'));n=item['N']
    assert record['N']==receipt['N']==n and receipt['status']=='PASS'
    assert record['canonical_size_digest']==item['canonical_size_digest']
    assert len(record['cases'])==6
    assert {(c['family'],c['fill']) for c in record['cases']}=={(f,j) for f in ['packet','signed_packet','signed_packet_chain'] for j in [-1,1]}
    support=0
    for c in record['cases']:
        assert c['encoding_results']['K_MAJOR']==c['encoding_results']['T_MAJOR']
        assert c['encoding_agreement'] and c['configuration_closure_all_boundaries'] and c['conditional_magnetization_closure']
        ports=c['ordered_ports'];assert len(set(ports))==len(ports) and all(0<=p<n for p in ports)
        rows=c['encoding_results']['K_MAJOR']['rows']
        assert [x['state'] for x in rows]==list(range(2**len(ports)))
        assert all(int(x['configuration_count'])==int(x['configuration_expected'])==2**(n-len(ports)) for x in rows)
        assert sum(int(x['configuration_count']) for x in rows)==2**n
        assert sum(x['exact_record_count'] for x in rows)==c['joint_support_size']
        assert all(x['configuration_closure'] and x['conditional_magnetization_closure'] for x in rows)
        assert c['canonical_sha256']==c['encoding_results']['K_MAJOR']['canonical_sha256']
        support+=c['joint_support_size']
    assert support==item['exact_record_count_one_encoding']

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--records',type=Path,help='Extracted records/ directory, to check all1800original files')
    ap.add_argument('--assets',type=Path,help='Check downloaded release-asset hashes')
    a=ap.parse_args();index=json.loads((P/'INDEX.json').read_text());summary=json.loads((P/'SUMMARY.json').read_text())
    assert [x['N'] for x in index]==list(range(1,1801))
    cases=list(csv.DictReader((P/'CASES.csv').open()))
    assert len(cases)==10800 and summary['cases']==10800
    assert sum(x['exact_record_count_one_encoding'] for x in index)==summary['primary_joint_support_records']
    assert sum(int(x['joint_support_size']) for x in cases)==summary['primary_joint_support_records']
    checked=0
    for item in index:
        folder=(a.records or P/'examples')/f"N{item['N']:06d}"
        if a.records or folder.exists():check_record(folder,item);checked+=1
    assets=0
    if a.assets:
        for item in json.loads((P/'DATA_MANIFEST.json').read_text())['assets']:
            p=a.assets/item['name'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'];assets+=1
    print(json.dumps({'status':'PASS','indexed_sizes':1800,'case_rows':len(cases),'compact_records_checked':checked,'release_assets_checked':assets,'new_production_solves':0},indent=2))
if __name__=='__main__':main()
