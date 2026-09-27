"""Compare source-bound readout queries with direct dense configuration energies."""
import readout as r
import baseline as b
import json,collections,itertools,shutil
from fractions import Fraction
P=r.P
def main():
 checks=[]
 with r.DomainSession.start('MATTER_SEARCH',objective='Qualify retained joint field and boundary readout against direct dense enumeration',output_root=P/'query_sessions',receipt_storage='gzip') as session:
  session.consumer=r.Adapter(session.consumer)
  for family in ['packet','signed_packet','signed_packet_chain']:
   for fill in [1,-1]:
    c,j,source,identity=b.load_bound(P/'inputs/N000012'/f'{family}_N000012_fill_{"plus" if fill==1 else "minus"}.json')
    manifest=P/'joint'/f'qualification_{family}_N000012_{fill:+d}'/'MANIFEST.json';states=[];ports=c['ports']
    for mask in range(1<<12):
     spins=[1 if mask&(1<<i) else -1 for i in range(12)]
     e=-sum(j*spins[u]*spins[v] for u,v,j in source['edges'])-sum(h*s for h,s in zip(source['fields'],spins));m=sum(spins)
     states.append((e,m,[spins[v] for v in ports]))
    for boundary in [[None]*len(ports),[1,-1]+[None]*(len(ports)-2)]:
     selected=[(e,m) for e,m,bs in states if all(x is None or x==s for x,s in zip(boundary,bs))]
     for field in ['0','1/2','-1']:
      h=Fraction(field);energies=[Fraction(e)-h*m for e,m in selected];ground=min(energies)
      expected=collections.Counter(m for (e,m),v in zip(selected,energies) if v==ground)
      got=session.execute('GEN4_JOINT_FIELD_BOUNDARY_READOUT',dict(manifest=str(manifest),sha256=r.joint.sha(manifest),field=field,boundary=boundary),purpose='Compare stored joint readout against all 4096 explicitly enumerated dense configurations with exact rational field')
      assert Fraction(got['ground_energy'])==ground and int(got['ground_degeneracy'])==sum(expected.values())
      assert {int(k):int(v) for k,v in got['ground_magnetization_counts'].items()}==dict(expected)
      assert int(got['configurations'])==len(selected) and Fraction(got['energy_sum'])==sum(energies) and Fraction(got['energy_square_sum'])==sum(e*e for e in energies)
      checks.append(dict(family=family,fill=fill,field=field,boundary=boundary,status='PASS'))
    # Verify every returned crossing against direct source energies, including
    # magnetization sectors that can coexist on a straight hull segment.
    got=r.joint.query(manifest)
    for crossing in got['ground_state_crossing_fields']:
     h=Fraction(crossing['field']);g=min(Fraction(e)-h*m for e,m,bs in states)
     counts=collections.Counter(m for e,m,bs in states if Fraction(e)-h*m==g)
     assert counts=={x['M']:int(x['degeneracy']) for x in crossing['coexisting_magnetizations']}
  bad=P/'wrong_joint_control';shutil.copytree(manifest.parent,bad)
  d=json.loads((bad/'MANIFEST.json').read_text());f=bad/d['shards'][0]['file'];data=bytearray(f.read_bytes());data[len(data)//2]^=1;f.write_bytes(data)
  try:r.joint.query(bad/'MANIFEST.json')
  except AssertionError:rejected=True
  else:rejected=False
  assert rejected
 r.joint.atomic(P/'READOUT_QUALIFICATION.json',dict(status='PASS',queries=len(checks),direct_dense_configurations_per_source=4096,exact_crossing_checks=True,corrupt_shard_rejected=True,checks=checks))
 print('PASS',len(checks),'exact field/boundary queries; all returned crossings; corrupt shard rejected')
if __name__=='__main__':main()
