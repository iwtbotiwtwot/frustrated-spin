"""Native query operation for retained exact joint tables; no spin re-enumeration."""
import os,sys,json,argparse
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,os.environ.get('GEN4_DENSE_RUNTIME','/opt/gen4-spin-continuation1/runtime'))
import joint
from SAM_PROJECT.session import DomainSession
class Adapter:
 def __init__(self,base):self.base=base
 def close(self):self.base.close()
 def execute(self,op,payload):
  if op!='GEN4_JOINT_FIELD_BOUNDARY_READOUT':return self.base.execute(op,payload)
  assert joint.sha(payload['manifest'])==payload['sha256']
  return joint.query(payload['manifest'],payload.get('field','0'),payload.get('boundary'))
def main():
 a=argparse.ArgumentParser();a.add_argument('manifest');a.add_argument('--field',default='0');a.add_argument('--boundary');a.add_argument('--output',required=True);args=a.parse_args()
 with DomainSession.start('MATTER_SEARCH',objective='Exact rational uniform-field and conditional-boundary response from retained joint counts',output_root=P/'query_sessions',receipt_storage='gzip') as session:
  session.consumer=Adapter(session.consumer);print(session.announcement())
  result=session.execute('GEN4_JOINT_FIELD_BOUNDARY_READOUT',dict(manifest=str(Path(args.manifest).resolve()),sha256=joint.sha(args.manifest),field=args.field,boundary=json.loads(args.boundary) if args.boundary else None),purpose='Read retained exact g(E,M,b); compute exact field-dependent ground states, degeneracy, moments and crossing fields without enumerating spins again')
 joint.atomic(args.output,result);print(json.dumps(result))
if __name__=='__main__':main()
