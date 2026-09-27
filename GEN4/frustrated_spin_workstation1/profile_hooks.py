"""Read-only timing instrumentation around unchanged exact computation and writes."""
import time,os
MEASURE={}

def counters():
    from pathlib import Path
    return {k.rstrip(':'):int(v) for k,v in (line.split() for line in Path('/proc/self/io').read_text().splitlines())}

def initialize(config):
    import campaign
    campaign.worker_init(config)
    original_write=campaign.write_gz
    def write(*args,**kwargs):
        t=time.perf_counter();c=time.process_time()
        try:return original_write(*args,**kwargs)
        finally:
            MEASURE['result_serialize_compress_fsync_seconds']=time.perf_counter()-t
            MEASURE['result_serialize_compress_cpu_seconds']=time.process_time()-c
    campaign.write_gz=write
    original_fsync=os.fsync
    def fsync(fd):
        t=time.perf_counter()
        try:return original_fsync(fd)
        finally:
            MEASURE['fsync_seconds']=MEASURE.get('fsync_seconds',0)+time.perf_counter()-t
            MEASURE['fsync_calls']=MEASURE.get('fsync_calls',0)+1
    os.fsync=fsync
    original_execute=campaign.SESSION.execute
    def execute(*args,**kwargs):
        t=time.perf_counter();c=time.process_time()
        try:return original_execute(*args,**kwargs)
        finally:
            MEASURE['native_execute_including_receipts_seconds']=time.perf_counter()-t
            MEASURE['native_execute_cpu_seconds']=time.process_time()-c
    campaign.SESSION.execute=execute

def work(payload):
    import campaign
    MEASURE.clear();before=counters();t=time.perf_counter();cpu=time.process_time()
    result=campaign.work(payload)
    after=counters();measurement=dict(MEASURE,whole_worker_seconds=time.perf_counter()-t,
        whole_worker_cpu_seconds=time.process_time()-cpu,proc_io_delta={k:after[k]-before[k] for k in before})
    if result['status']=='EXACT_VERIFIED':
        tm=result['timing'];inside=tm['planning_seconds']+tm['preparation_seconds']+sum(tm['warm_solve_seconds'])+tm['independent_full_graph_VE_seconds']+tm['full_comparison_seconds']
        measurement['instrumented_solver_seconds']=inside
        measurement['native_overhead_estimate_seconds']=measurement['native_execute_including_receipts_seconds']-inside
    result['persistence_profile']=measurement
    return result
