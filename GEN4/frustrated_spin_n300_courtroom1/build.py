"""Create and seal declared N300 sources. This script executes no spin solve."""
import copy,datetime,os,platform,subprocess,tarfile,importlib.metadata as md
from packet import *

def main():
    assert not (P/'PRECOMMIT_SEAL.json').exists()
    assert not (P/'RESULTS.json').exists()
    records=[]
    for family in ['packet','signed_packet','signed_packet_chain']:
        old=load(P/'inputs'/f'{family}_N120.json');c=copy.deepcopy(old);s=c['source'];first=c['blocks'][0];mp={v:i for i,v in enumerate(first)}
        motif=[[mp[u],mp[v],j] for u,v,j in s['edges'] if u in mp and v in mp]
        for start in range(120,300,15):
            block=list(range(start,start+15));previous=c['blocks'][-1];i=len(c['blocks'])-1;c['blocks'].append(block)
            s['edges'].extend([[min(block[u],block[v]),max(block[u],block[v]),j] for u,v,j in motif])
            if family=='signed_packet_chain':
                edge=[previous[0],block[0],-1 if i%2 else 1];c['bridges'].append(edge);s['edges'].append([min(edge[:2]),max(edge[:2]),edge[2]])
        c.update(N=300,key=family+'_N300',claim_type='PRECOMMITTED_NEW_SOURCE',canonical_replacement=False)
        c['source']=norm(300,s['edges'],[0]*300,'N300_COURTROOM1_'+family.upper())
        assert [e for e in c['source']['edges'] if max(e[:2])<120]==old['source']['edges']
        assert len(c['source']['edges'])==(819 if c['bridges'] else 800)
        witnesses=[];edges={tuple(e[:2]):e[2] for e in c['source']['edges']}
        for block in c['blocks']:
            for i in [0,5,10]:
                tri=block[i:i+3]
                if all(tuple(sorted(e)) in edges for e in itertools.combinations(tri,2)):
                    prod=1
                    for e in itertools.combinations(tri,2):prod*=edges[tuple(sorted(e))]
                    if prod<0:witnesses.append(tri)
        c['frustrated_triangles']=witnesses;assert len(witnesses)==(0 if family=='packet' else 60)
        save(P/'sources'/f'{c["key"]}.json',c)
        records.append(dict(family=family,key=c['key'],N=300,source_hash=c['source']['source_sha256'],record_hash=digest(c),ordered_ports=c['ports'],components=len(exact.components(c['source'])),edges=len(c['source']['edges']),frustrated_triangle_witnesses=len(witnesses),inherited_N120_hash=old['source']['source_sha256']))
    from CURRENT_REVISION import runtime
    identity=dict(binding=runtime.verify(),python=sys.version,packages={x:md.version(x) for x in ['python-flint','numpy']},hostname=platform.node(),hardware=subprocess.check_output(['lscpu'],text=True),git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip(),old_campaign_modified=False)
    save(P/'RUNTIME_PREFLIGHT.json',identity)
    save(P/'PRECOMMIT.json',dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner='Sean Brady',primary_family='packet',secondary_prediction_families=['signed_packet','signed_packet_chain'],prediction=dict(metric='median of 31 warm exact full-spectrum solves',threshold_ms=25,strict=True,hardware='workstation Intel i9-12900HK',predicted_medians_from_size_scaling_ms=dict(packet=15.554,signed_packet=15.983,signed_packet_chain=17.120)),sources=records,protocol_sha256=sha(P/'PROTOCOL.md'),target_size_executed=False,source_size_holdouts_preserved=list(range(121,145)),warm_repeats=31,empty_cache_repeats=5,refinement_repeats=11,wrong_controls=6))
    files=[f for f in P.rglob('*') if f.is_file() and 'runtime' not in f.relative_to(P).parts and '__pycache__' not in f.parts]
    manifest={str(f.relative_to(P)):sha(f) for f in sorted(files)};save(P/'FROZEN_MANIFEST.json',manifest)
    seal=dict(sealed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_sha256=sha(P/'FROZEN_MANIFEST.json'),protocol_sha256=sha(P/'PROTOCOL.md'),precommit_sha256=sha(P/'PRECOMMIT.json'),no_N300_solve_before_seal=True)
    save(P/'PRECOMMIT_SEAL.json',seal)
    with tarfile.open(P/'PRECOMMIT.tar.gz','w:gz') as t:
        for f in files+[P/'FROZEN_MANIFEST.json',P/'PRECOMMIT_SEAL.json']:t.add(f,arcname=str(f.relative_to(P)))
    for f in files+[P/'FROZEN_MANIFEST.json',P/'PRECOMMIT_SEAL.json']:f.chmod(0o444)
    print(json.dumps(seal,indent=2))

if __name__=='__main__':main()
