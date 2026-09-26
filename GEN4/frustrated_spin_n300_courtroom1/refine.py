"""Exact boundary-equality refinement of the newly executed connected family."""
import gzip,time,statistics,csv,copy
from packet import *
from SAM_PROJECT.session import DomainSession

def load_tables():
    assert sha(P/'PACKET_TABLES.json.gz')==load(P/'PACKET_TABLES_MANIFEST.json')['sha256']
    raw=json.load(gzip.open(P/'PACKET_TABLES.json.gz','rt'))
    return {key:{tuple(r['state']):fmpz_poly([int(x) for x in r['coefficients']]) for r in rows} for key,rows in raw.items()}

def collapse(c,plan,cache):
    assert digest(c)==plan['source_record_hash']
    if not c['bridges']:return packet_solve(c,plan,cache)
    tables=[cache[p['key']] for p in plan['pieces']]
    if not all(t[(-1,)]==t[(1,)] for t in tables[1:]):
        r=packet_solve(c,plan,cache);r['execution']['reduction']='NOT_ADMITTED_BOUNDARY_SPECTRA_DIFFER';return r
    start=time.perf_counter();counts=collections.Counter(p['key'] for p in plan['pieces'][1:]);powers=[cache[key][(-1,)]**count for key,count in counts.items()]
    for magnitude,count in collections.Counter(abs(j) for u,v,j in c['bridges']).items():
        coeff=[0]*(magnitude+1);coeff[0]=coeff[-1]=1;powers.append(fmpz_poly(coeff)**count)
    common=balanced_product(powers);hist={}
    for state,poly in tables[0].items():
        result=poly*common;mask=sum(1<<i for i,z in enumerate(state) if z==1);hist[mask]={2*k-plan['bound']:int(v) for k,v in enumerate(result) if v}
    a=exact.finalize_answer(c['source'],c['ports'],hist)
    return dict(answer=a,execution=dict(reduction='EXACT_EQUAL_BOUNDARY_SPECTRA',conditional_tables_compared=len(tables)-1,bridge_factors=len(c['bridges']),seconds=time.perf_counter()-start,cache_hits=len(tables),cache_misses=0,recomputed_global_spectrum=True))

class RefineAdapter(Adapter):
    def execute(self,op,payload):
        if op=='GEN4_PACKET_FRESH_SOLVE' and payload.get('boundary_refinement'):
            assert payload['refinement_hash']==sha(__file__) and payload['code_hash']==sha(P/'packet.py')
            c=load(P/'sources'/f"{payload['key']}.json");assert c['source']['source_sha256']==payload['source_hash']
            t=time.perf_counter();plan=compile_source(c);planning=time.perf_counter()-t
            t=time.perf_counter();r=collapse(c,plan,self.cache);r.update(status='EXACT',fresh_global_calculation=True,solve_seconds=time.perf_counter()-t,planning_seconds=planning,plan_hash=digest(plan));return r
        if op!='GEN4_PACKET_BRIDGE_REFINEMENT':return super().execute(op,payload)
        assert payload['code_hash']==sha(__file__);c=load(P/'sources'/f"{payload['key']}.json");assert c['source']['source_sha256']==payload['source_hash'];plan=compile_source(c);times=[]
        ref=json.load(gzip.open(P/'results'/(c['key']+'.json.gz'),'rt'))['answers']['variable_elimination']
        for repeat in range(3):
            start=time.perf_counter();r=collapse(c,plan,self.cache);times.append(time.perf_counter()-start);vh=compare(r['answer'],ref)
        return dict(status='EXACT',source_hash=c['source']['source_sha256'],plan_hash=digest(plan),method='EXACT_BOUNDARY_EQUALITY_COLLAPSE',times_seconds=times,median_ms=1000*statistics.median(times),verification_hash=vh,execution=r['execution'],answer=r['answer'])

def main():
    assert load(P/'STATUS.json')['status']=='COMPLETE';tables=load_tables();rows=[];(P/'refinement').mkdir(exist_ok=True)
    with DomainSession.start('MATTER_SEARCH',objective='Convert equal packet boundary spectra into an exact source-bound bridge reduction',output_root=P/'refinement_sessions',receipt_storage='gzip') as session:
        print(session.announcement(),flush=True);adapter=RefineAdapter(session.consumer);session.consumer=adapter;adapter.cache=tables
        for n in range(1,121):
            key=f'signed_packet_chain_N{n:03d}';c=load(P/'sources'/f'{key}.json');q=dict(key=key,source_hash=c['source']['source_sha256'],code_hash=sha(__file__),hypothesis='Equal full conditional spectra make a one-gateway bridge contribution independent of its parent spin',exact_contract='Compare full boundary polynomials before reduction and full output against independent variable elimination')
            save(P/'refinement'/(key+'_PRECOMMIT.json'),q);r=session.execute('GEN4_PACKET_BRIDGE_REFINEMENT',q,purpose='Test exact boundary equality, contract bridge factors, and verify all DOS/ordered-port coefficients')
            with gzip.open(P/'refinement'/(key+'.json.gz'),'wt') as f:json.dump(r,f)
            rows.append(dict(N=n,key=key,source_hash=r['source_hash'],median_ms=r['median_ms'],verification_hash=r['verification_hash'],reduction=r['execution'].get('reduction','NO_BRIDGES')))
        session.execute('GEN3_CHECKPOINT',{},purpose='Retain 120 exact boundary-refinement results')
    # Independent negative controls: a field breaks boundary equality; an extra edge breaks the declared partition.
    c=copy.deepcopy(load(P/'sources/signed_packet_chain_N012.json'));c['source']['fields'][c['blocks'][-1][0]]=2;c['source']=norm(c['N'],c['source']['edges'],c['source']['fields'],'BOUNDARY_FIELD_CONTROL');plan=compile_source(c);cache={};plain=packet_solve(c,plan,cache);r=collapse(c,plan,cache)
    assert r['execution']['reduction']=='NOT_ADMITTED_BOUNDARY_SPECTRA_DIFFER';compare(r['answer'],plain['answer']);compare(r['answer'],exact.solve_cpu(c['source'],c['ports'],dict(method='variable_elimination'))['answer'])
    bad=copy.deepcopy(c);bad['source']['edges'].append([bad['blocks'][0][0],bad['blocks'][2][0],1]);bad['source']=norm(bad['N'],bad['source']['edges'],bad['source']['fields'],'UNDECLARED_CROSS_EDGE_CONTROL')
    try:compile_source(bad)
    except AssertionError as e:assert str(e)=='UNACCOUNTED_INTERPACKET_INTERACTION'
    else:raise AssertionError('Cross-edge guard failed')
    save(P/'refinement/NEGATIVE_CONTROLS.json',dict(field_control=dict(source=c,answer=r['answer'],execution=r['execution']),extra_edge_source=bad,extra_edge_rejected=True))
    with (P/'BRIDGE_REFINEMENT.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    save(P/'BOUNDARY_CERTIFICATE.json',dict(status='EXACT_SOURCE_BOUND_REDUCTION',statement='For every non-root packet whose complete gateway-conditioned energy polynomials obey A_minus=A_plus=A, summing its gateway spin across a bridge J contributes A(q)*(1+q^abs(J)), independent of the parent spin. Recursion along the declared tree gives the exact root-conditioned spectrum.',derivation='The bridge exponent is (abs(J)-J*s*t)/2. As t ranges over -1,+1, these exponents are 0 and abs(J) in either order. Equality of the two full packet messages makes the sum independent of s. The tree recursion preserves equality. All local energy bounds and bridge bounds add to the global bound.',supporting_cases=rows,independent_verification='Every full scalar and ordered-port coefficient compared with separately executed full-graph variable elimination',controls=dict(nonzero_field='Boundary equality rejected; complete two-state message solver agrees with full-graph VE',undeclared_cross_edge='Partition compiler rejects the extra interaction'),global_installation=False))
    print('REFINEMENT PASS',len(rows),'max_ms',max(r['median_ms'] for r in rows),flush=True)

if __name__=='__main__':main()
