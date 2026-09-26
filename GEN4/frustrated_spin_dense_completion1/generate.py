"""Generate complete graph sources; no target density-of-states solve."""
from pathlib import Path
import sys,json,hashlib,random,itertools,time
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'frustrated_spin_learning1/runtime'))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import validate_source

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')

class Generator:
    def __init__(self,base):self.base=base
    def close(self):self.base.close()
    def execute(self,op,payload):
        if op!='GEN4_DENSE_GRAPH_SOURCE_COMPLETION':return self.base.execute(op,payload)
        assert payload['generator_sha256']==filehash(P/'generate.py')
        source_path=P/payload['input'];assert filehash(source_path)==payload['input_sha256']
        c=json.loads(source_path.read_text());old=c['source'];n=old['N'];j0=payload['fill_coupling']
        assert j0 in (-1,1) and n==300
        oldedges={tuple(e[:2]):e[2] for e in old['edges']}
        edges=[[u,v,oldedges.get((u,v),j0)] for u in range(n) for v in range(u+1,n)]
        dense=validate_source(dict(N=n,edges=edges,fields=old['fields'],parent_vertices=old['parent_vertices'],
            parent_instance_sha256=old['source_sha256'],family=f"DENSE_COMPLETION1_{c['family']}_FILL_{j0:+d}"))
        assert len(edges)==n*(n-1)//2 and all(j!=0 for u,v,j in edges)
        densemap={tuple(e[:2]):e[2] for e in edges}
        assert all(densemap[(u,v)]==j for u,v,j in old['edges'])
        corrections=[[u,v,j-j0] for u,v,j in old['edges'] if j!=j0]
        # Independent integer evaluation of the derived identity, not a DOS solve.
        rng=random.Random(20260926);spins=[[1]*n,[-1]*n,[1 if i%2 else -1 for i in range(n)]]
        spins += [[rng.choice((-1,1)) for _ in range(n)] for _ in range(13)]
        evaluations=[]
        for z in spins:
            direct=-sum(j*z[u]*z[v] for u,v,j in edges)-sum(h*s for h,s in zip(old['fields'],z))
            m=sum(z);collective=-j0*((m*m-n)//2)
            rewritten=collective-sum(d*z[u]*z[v] for u,v,d in corrections)-sum(h*s for h,s in zip(old['fields'],z))
            assert direct==rewritten
            evaluations.append(dict(spin_assignment_hash=digest(z),magnetization=m,energy=direct))
        key=f"{c['family']}_N300_fill_{'plus' if j0==1 else 'minus'}"
        record=dict(schema='GEN4_DENSE_COMPLETION_SOURCE_V1',key=key,status='SOURCE_GENERATED_NOT_DOS_SOLVED',
            source=dense,ordered_ports=c['ports'],parent_source_hash=old['source_sha256'],fill_coupling=j0,
            inherited_packet_partition=c['blocks'],inherited_bridges=c['bridges'],
            correction_edges=corrections,canonical_replacement=False,
            construction='Preserve every parent coupling and field; assign the declared nonzero coupling to every previously absent pair',
            identity='E=-J0*(M^2-N)/2-sum_parent((Juv-J0)*su*sv)-sum(hv*sv)',
            identity_evaluations=evaluations,identity_derivation='M^2=N+2*sum_{u<v}su*sv. Subtract the uniform J0 interaction, then restore each parent coupling with its exact difference Juv-J0.')
        save(P/'sources'/f'{key}.json',record)
        return dict(key=key,status=record['status'],N=n,edges=len(edges),inherited_edges=len(oldedges),added_edges=len(edges)-len(oldedges),
            correction_edges=len(corrections),fill_coupling=j0,source_hash=dense['source_sha256'],
            artifact=f'sources/{key}.json',artifact_sha256=filehash(P/'sources'/f'{key}.json'),
            preserved_every_parent_coupling=True,identity_checks=len(evaluations),full_DOS_solved=False)

def main():
    assert not (P/'RESULTS.json').exists(),'Add a successor instead of overwriting this construction'
    entries=[]
    with DomainSession.start('MATTER_SEARCH',objective='Generate fully connected N300 graph completions preserving packet source couplings; derive the collective magnetization representation',output_root=P/'sessions',receipt_storage='gzip') as session:
        print(session.announcement(),flush=True);session.consumer=Generator(session.consumer)
        for family in ('packet','signed_packet','signed_packet_chain'):
            for j0 in (1,-1):
                name=f'inputs/{family}_N300.json';payload=dict(input=name,input_sha256=filehash(P/name),fill_coupling=j0,generator_sha256=filehash(P/'generate.py'))
                save(P/'precommits'/f"{family}_{j0:+d}.json",dict(created_unix=time.time(),payload=payload,scope='Graph generation and exact algebraic identity checks; no density-of-states solve'))
                entries.append(session.execute('GEN4_DENSE_GRAPH_SOURCE_COMPLETION',payload,purpose='Account for every pair and preserve existing couplings; verify the exact uniform-background plus source-correction energy identity'))
        save(P/'RESULTS.json',dict(status='SIX_COMPLETE_GRAPH_SOURCES_GENERATED',entries=entries,session=str(session.directory),full_DOS_calculations=0,current_pod_campaign_changed=False))
    print(json.dumps(entries,indent=2))

if __name__=='__main__':main()
