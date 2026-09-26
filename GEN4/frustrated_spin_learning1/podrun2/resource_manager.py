"""One aggregate host budget, sampled once before an exclusive R3 run.

The coordinator and every descendant share sam-r3.slice. This is a resource
launcher, not an additional research agent or a background training service.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import uuid

HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'SAM_TRAINING').is_dir()),Path.cwd())
PROFILE=HERE/'RESOURCE_PROFILE.json'
STATE=ROOT/'SAM_RUNTIME/R3'
SLICE='sam-r3.slice'
THREAD_ENV={name:'1' for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')}


def host_name():
    return 'ryzen' if Path.home().name=='lilhelper' else 'i9'


def cpu_sample():
    fields=Path('/proc/stat').read_text().splitlines()[0].split()[1:9]
    values=list(map(int,fields))
    return sum(values),values[3]+values[4]


def snapshot(profile,host):
    h=profile['hosts'][host]; first=cpu_sample();time.sleep(.25);second=cpu_sample()
    idle=(second[1]-first[1])/max(1,second[0]-first[0])
    available=set(os.sched_getaffinity(0))
    allowed=sorted(available & set(h['allowed_cpus']))
    memory={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()}
    fraction=h['fraction_of_available']
    quota=min(len(allowed),len(available)*idle*fraction)
    if not allowed or quota<=0 or memory['MemAvailable']<=0:
        raise ValueError('No available resource budget for R3')
    maximum=int(memory['MemAvailable']*fraction)
    return {'host':host,'fraction_of_available':fraction,'prelaunch_mem_available':memory['MemAvailable'],
        'prelaunch_available_cpu_equivalents':len(available)*idle,'cpu_equivalents':quota,
        'cpu_quota_percent':round(quota*100,2),'allowed_cpus':allowed,
        'memory_max_bytes':maximum,'memory_high_bytes':maximum*9//10,'memory_swap_max_bytes':0,
        'cpu_worker_order':[c for c in h['worker_order'] if c in allowed],
        'controller_cpus':[c for c in h['critical_path_preferred_cpus'] if c in allowed],
        'io_cpus':[c for c in h['io_cpus'] if c in allowed],
        'initial_workers':min(4,len(allowed)), 'sampled_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}


def properties(budget):
    return {'CPUQuota':str(budget['cpu_quota_percent'])+'%',
        'AllowedCPUs':','.join(map(str,budget['allowed_cpus'])),
        'MemoryMax':str(budget['memory_max_bytes']),'MemoryHigh':str(budget['memory_high_bytes']),
        'MemorySwapMax':'0','TasksMax':'256','CPUWeight':'100','IOWeight':'100'}


def configure(budget):
    folder=Path.home()/'.config/systemd/user';folder.mkdir(parents=True,exist_ok=True)
    unit=folder/SLICE
    if not unit.exists():
        unit.write_text('[Unit]\nDescription=SLC-GEN3-R3 aggregate host resources\n\n[Slice]\nCPUAccounting=yes\nMemoryAccounting=yes\nIOAccounting=yes\n')
        subprocess.run(['systemctl','--user','daemon-reload'],check=True)
    subprocess.run(['systemctl','--user','set-property','--runtime',SLICE,
                    *[key+'='+value for key,value in properties(budget).items()]],check=True)
    subprocess.run(['systemctl','--user','start',SLICE],check=True)


def readback():
    return subprocess.run(['systemctl','--user','show',SLICE,'-p','ActiveState',
        '-p','CPUQuotaPerSecUSec','-p','AllowedCPUs','-p','MemoryMax','-p','MemoryHigh',
        '-p','MemorySwapMax','-p','MemoryCurrent','-p','TasksCurrent'],check=True,capture_output=True,text=True).stdout


def launch(argv,role='controller',name=None,seconds=86400):
    if os.environ.get('SAM_R3_RUN_ID') and 'sam-r3.slice' in Path('/proc/self/cgroup').read_text():
        # Nested managed entrypoints inherit the same host allowance and lock.
        # They must not resample free RAM or try to acquire another full budget.
        return subprocess.run(argv).returncode
    profile=json.loads(PROFILE.read_text());STATE.mkdir(parents=True,exist_ok=True)
    with (STATE/'run.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('R3 or cooperating maintenance already owns the host') from None
        budget=snapshot(profile,host_name());configure(budget)
        budget['enforcement_readback']=readback()
        stamp=name or 'run-'+uuid.uuid4().hex[:16]
        if re.fullmatch('[a-z0-9][a-z0-9-]{0,70}',stamp) is None:
            raise ValueError('Use a plain lowercase run name')
        run=STATE/'runs'/stamp;run.mkdir(parents=True,exist_ok=False)
        (run/'BUDGET.json').write_text(json.dumps(budget,indent=2)+'\n')
        env={**THREAD_ENV,'PYTHONUNBUFFERED':'1','PYTHONDONTWRITEBYTECODE':'1','RUSTICL_ENABLE':'radeonsi',
            'SAM_R3_RUN_ID':stamp,'SAM_R3_BUDGET':str(run/'BUDGET.json'),
            'SAM_R3_ALLOWED_CPUS':','.join(map(str,budget['allowed_cpus'])),
            'SAM_R3_CPU_ORDER':','.join(map(str,budget['cpu_worker_order'])),
            'SAM_R3_WORKERS':str(budget['initial_workers']),
            'SAM_GPU_BUFFER_BUDGET_BYTES':str(2**30),'SAM_GPU_MAX_ALLOCATION_BYTES':str(2**28)}
        cpus=budget['controller_cpus'] if role=='controller' else budget['io_cpus'] if role=='io' else budget['allowed_cpus']
        command=['systemd-run','--user','--wait','--pipe','--collect','--quiet',
            '--unit','sam-r3-'+stamp,'--slice',SLICE,'--working-directory',str(ROOT),
            '--property','Type=exec','--property','KillMode=control-group',
            '--property','RuntimeMaxSec='+str(seconds),'--property','TimeoutStopSec=30']
        for key,value in env.items():command+=['--setenv',key+'='+value]
        result=subprocess.run([*command,'--','taskset','-c',','.join(map(str,cpus)),*argv])
        (run/'EXIT.json').write_text(json.dumps({'returncode':result.returncode,'role':role,'command':argv,
            'budget':str(run/'BUDGET.json'),'slice':SLICE,'readback':readback()},indent=2)+'\n')
        return result.returncode


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('status');sub.add_parser('install-host')
    run=sub.add_parser('run');run.add_argument('--name');run.add_argument('--role',choices=('controller','cpu','gpu','io'),default='controller')
    run.add_argument('--seconds',type=int,default=86400);run.add_argument('argv',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    if args.action=='status':
        print(json.dumps({'host':host_name(),'profile':str(PROFILE),'slice':SLICE,'readback':readback()},indent=2))
    elif args.action=='install-host':
        STATE.mkdir(parents=True,exist_ok=True)
        budget=snapshot(json.loads(PROFILE.read_text()),host_name());configure(budget)
        print(json.dumps({'budget':budget,'readback':readback()},indent=2))
    else:
        argv=args.argv[1:] if args.argv[:1]==['--'] else args.argv
        if not argv:parser.error('run needs a command after --')
        if not 1<=args.seconds<=604800:parser.error('seconds must be between 1 and 604800')
        if args.role=='gpu' and host_name()!='ryzen':parser.error('The 780M lane is on lilhelper')
        if args.role=='gpu':
            argv=['flock','--exclusive',str(ROOT/'SAM_TRAINING/780m.lock'),*argv]
        raise SystemExit(launch(argv,args.role,args.name,args.seconds))

if __name__=='__main__':main()
