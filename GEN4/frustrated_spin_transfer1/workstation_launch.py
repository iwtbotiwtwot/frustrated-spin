"""Workstation successor: same exact packet methods, local resource/write policy."""
import sys,json,hashlib,os
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'runtime'))
from gen4 import resources
import memory_policy

def main():
    root=P/('qualification' if '--qualify' in sys.argv else 'packet')
    sys.path.insert(0,str(root));import campaign,profile_hooks,fast_io
    identity=dict(project=str(P),backend='LOCAL_FLINT_CPU',hardware='WORKSTATION_RESOURCE_DISCOVERY',gzip_level=1,
        code={f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ['workstation_launch.py','memory_policy.py','profile_hooks.py','fast_io.py']})
    memory_policy.install(resources,identity)
    campaign.worker_init=fast_io.initialize;campaign.work=profile_hooks.work
    return campaign.main()
if __name__=='__main__':raise SystemExit(main())
