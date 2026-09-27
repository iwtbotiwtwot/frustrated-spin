"""Project-local resource admission; unchanged global GEN4 resource manager."""
from pathlib import Path
GIB=1024**3

def available_from_readings(host_available,limit,current,inactive_file,dirty=0,writeback=0,shmem=0):
    reclaim=max(0,min(current,inactive_file)-dirty-writeback-shmem)
    gross=min(host_available,max(0,limit-current)+reclaim)
    return max(0,gross-max(8*GIB,limit//12))

def observation(profile):
    info=dict((line.split(':')[0],int(line.split()[1])*1024) for line in Path('/proc/meminfo').read_text().splitlines())
    host=info['MemAvailable'];candidates=[];details=[]
    for row in profile['cgroups']:
        if row.get('memory.max','max')=='max':continue
        p=Path(row['path']);current_path=Path(row.get('memory_current_path',str(p/'memory.current')))
        if not current_path.exists():continue
        limit=int(row['memory.max']);current=int(current_path.read_text())
        try:stat=dict(line.split() for line in (p/'memory.stat').read_text().splitlines())
        except OSError:stat={}
        inactive=int(stat.get('inactive_file',stat.get('total_inactive_file',0)))
        dirty=int(stat.get('file_dirty',stat.get('total_dirty',0)))
        writeback=int(stat.get('file_writeback',stat.get('total_writeback',0)))
        shmem=int(stat.get('shmem',stat.get('total_shmem',0)))
        value=available_from_readings(host,limit,current,inactive,dirty,writeback,shmem)
        candidates.append(value);details.append(dict(path=str(p),limit=limit,current=current,inactive_file=inactive,
            dirty=dirty,writeback=writeback,shmem=shmem,admission=value))
    fallback=max(0,host-max(8*GIB,profile['memory_limit_bytes']//12))
    return dict(policy='CLEAN_INACTIVE_FILE_CACHE_WITH_EXISTING_RESERVE_V1',available_bytes=min([fallback,*candidates]),
        host_available_bytes=host,cgroups=details,swap_not_counted=True)

def install(resources,identity):
    original=resources.inspect
    def inspect(*args,**kwargs):
        profile=original(*args,**kwargs);obs=observation(profile)
        profile['original_memory_admission_bytes']=profile['memory_admission_bytes']
        profile['memory_admission_bytes']=obs['available_bytes']
        profile['resume_policy']=dict(identity=identity,initial_memory_observation=obs)
        return profile
    resources.inspect=inspect
    resources.live_memory_available=lambda profile:observation(profile)['available_bytes']

def test():
    # File cache is recoverable; anonymous, dirty, shmem and swap are not credited.
    assert available_from_readings(100*GIB,40*GIB,35*GIB,30*GIB)==27*GIB
    assert available_from_readings(100*GIB,40*GIB,35*GIB,0)==0
    assert available_from_readings(100*GIB,40*GIB,35*GIB,30*GIB,5*GIB,2*GIB,3*GIB)==17*GIB
    assert available_from_readings(10*GIB,40*GIB,35*GIB,30*GIB)==2*GIB
    return {'status':'PASS','controls':4}
