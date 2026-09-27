"""Extend the qualified complete-graph source catalog from N1350 to N1408."""
import os,sys,json,time,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent/'frustrated_spin_workstation1'
os.environ['GEN4_DENSE_RUNTIME']=str(ROOT/'runtime')
import follower as f
f.P=P

def main():
 producer=ROOT/'packet';checkpoint=f.load(producer/'CHECKPOINT.json');assert checkpoint['last_completed_N']>=1408
 profile=f.resources.inspect(scratch=P,persistent_root=P/'persistent')
 assert profile['memory_admission_bytes']>2*1024**3 and shutil.disk_usage(P).free>20*1024**3
 f.atomic(P/'RESOURCES.json',profile)
 manifest={name:f.filehash(P/name) for name in ['run.py','follower.py','dense_format.py']}
 f.atomic(P/'CODE_MANIFEST.json',manifest)
 f.CONFIG=dict(producer=str(producer),output_dir='graphs',qualification=False,code_manifest_sha256=f.filehash(P/'CODE_MANIFEST.json'))
 receipts={};f.refresh_receipts(producer/'CATALOG.jsonl',0,receipts)
 f.atomic(P/'PRECOMMIT.json',dict(first_N=1351,last_N=1408,variants_per_N=6,producer_checkpoint_sha256=f.filehash(producer/'CHECKPOINT.json'),
  historical_graphs_through_1350='/home/sam/mnt/lilhelper-t500/SAM_POD_BACKUPS/frustrated-spin-20260926/restored/follower/graphs',source_generation_only=True))
 started=time.time();total=0
 with f.DomainSession.start('MATTER_SEARCH',objective='Extend every explicit complete signed graph source through N1408 from verified workstation packet parents',output_root=P/'sessions',receipt_storage='gzip') as session:
  print(session.announcement(),flush=True);session.consumer=f.Adapter(session.consumer)
  for n in range(1351,1409):
   payload=dict(N=n,code_manifest_sha256=f.CONFIG['code_manifest_sha256'],receipts={family:receipts[n,family] for family in f.FAMILIES})
   f.append(P/'QUESTION_LEDGER.jsonl',dict(event='PRECOMMIT',N=n,payload=payload))
   result=session.execute('GEN4_DENSE_FOLLOWER_GENERATE',payload,purpose='Store every pair coupling explicitly; preserve exact parent provenance; read back and verify every inherited and filled coupling')
   total+=len(result['variants']);f.append(P/'INDEX.jsonl',result)
   f.atomic(P/'STATUS.json',dict(status='RUNNING',pid=os.getpid(),last_completed_N=n,new_graphs=total))
 f.atomic(P/'STATUS.json',dict(status='COMPLETE',first_N=1351,last_completed_N=1408,new_graphs=total,
  combined_catalog_graphs=1408*6,edges_per_N1408_graph=1408*1407//2,seconds=time.time()-started,full_DOS_solves=0))
 print((P/'STATUS.json').read_text(),flush=True)

if __name__=='__main__':main()
