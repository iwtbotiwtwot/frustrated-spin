"""Explicit-family catalog access or fresh exact solve using retained local tables."""
import argparse,gzip,time
from packet import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('family',choices=['packet','signed_packet','signed_packet_chain']);ap.add_argument('N',type=int,choices=range(1,121));ap.add_argument('--solve',action='store_true');ap.add_argument('--empty-cache',action='store_true');args=ap.parse_args()
    key=f'{args.family}_N{args.N:03d}';c=load(P/'sources'/f'{key}.json')
    if not args.solve:
        r=json.load(gzip.open(P/'results'/(key+'.json.gz'),'rt'));a=r['answers']['packet_warm'];print(json.dumps(dict(mode='RETAINED_RESULT_LOOKUP',key=key,source_hash=c['source']['source_sha256'],ports=c['ports'],ground_energy=a['ground_energy'],ground_degeneracy=a['ground_degeneracy'],configuration_count=a['configuration_count'],result=str(P/'results'/(key+'.json.gz'))),indent=2));return
    from SAM_PROJECT.session import DomainSession
    with DomainSession.start('MATTER_SEARCH',objective='Fresh source-bound packet catalog solve '+key,output_root=P/'query_sessions',receipt_storage='gzip') as session:
        from refine import RefineAdapter
        print(session.announcement(),flush=True);adapter=RefineAdapter(session.consumer);session.consumer=adapter
        if not args.empty_cache:
            assert sha(P/'PACKET_TABLES.json.gz')==load(P/'PACKET_TABLES_MANIFEST.json')['sha256']
            raw=json.load(gzip.open(P/'PACKET_TABLES.json.gz','rt'))
            adapter.cache={key:{tuple(row['state']):fmpz_poly([int(v) for v in row['coefficients']]) for row in rows} for key,rows in raw.items()}
        refined=not args.empty_cache and c['family']=='signed_packet_chain' and (P/'BOUNDARY_CERTIFICATE.json').exists()
        r=session.execute('GEN4_PACKET_FRESH_SOLVE',dict(key=key,source_hash=c['source']['source_sha256'],code_hash=sha(P/'packet.py'),boundary_refinement=refined,refinement_hash=sha(P/'refine.py')),purpose='Recompute the global spectrum from exact local packet messages; no full-result lookup')
        retained=json.load(gzip.open(P/'results'/(key+'.json.gz'),'rt'))['answers']['variable_elimination'];r['verification_hash']=compare(r['answer'],retained)
        save(P/'query_results'/(key+'_'+str(time.time_ns())+'.json'),r);session.execute('GEN3_CHECKPOINT',{},purpose='Retain fresh packet execution and full equality check')
        print(json.dumps(dict(mode='FRESH_GLOBAL_SOLVE',key=key,solve_ms=1000*r['solve_seconds'],execution=r['execution'],verified=True,session=str(session.directory)),indent=2))

if __name__=='__main__':main()
