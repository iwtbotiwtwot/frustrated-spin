"""Installed-relative exact CUDA spin solver with adaptive device scheduling."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import queue
import threading
import time
import traceback

PRIMES = (998244353, 1004535809, 469762049, 167772161, 1224736769)
OPTIONS = {'ports', 'max_output_rows', 'max_energy_span', 'max_seconds', 'devices',
           'workers', 'root_batch', 'branch_group', 'max_width', 'max_map_bytes',
           'max_vram_bytes', 'checkpoint_dir', 'resume', 'max_branches', 'max_tasks',
           'max_port_states'}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _vendor():
    folder = Path(__file__).resolve().parent/'spin_vendor'
    manifest = json.loads((folder/'MANIFEST.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((folder/name).read_bytes()).hexdigest() != expected:
            raise ValueError('GPU arithmetic vendor hash mismatch: '+name)
    return hashlib.sha256((folder/'MANIFEST.json').read_bytes()).hexdigest()


def _positive(options, key, default):
    value = options.get(key, default)
    if type(value) is not int or value < 1: raise ValueError(key+' must be a positive integer')
    return value


def _structure(n, edges, ports, fixed, supplied_order=None):
    adjacency = {v: set() for v in range(n) if v not in fixed}
    for u, v, _ in edges:
        if u in adjacency and v in adjacency:
            adjacency[u].add(v); adjacency[v].add(u)
    remaining = set(adjacency)-set(ports)
    if supplied_order is not None and (len(supplied_order) != len(remaining) or set(supplied_order) != remaining):
        raise ValueError('GPU elimination order does not cover the unfixed non-port vertices')
    order, width, entries = [], 0, 0
    while remaining:
        if supplied_order is None:
            def score(v):
                ns = adjacency[v]
                return sum(len(ns-adjacency[w]-{w}) for w in ns)//2, len(ns), v
            vertex = min(remaining, key=score)
        else: vertex = supplied_order[len(order)]
        ns = adjacency[vertex]
        width = max(width, len(ns)); entries += 1 << len(ns)
        for other in ns:
            adjacency[other].update(ns-{other}); adjacency[other].discard(vertex)
        del adjacency[vertex]; remaining.remove(vertex); order.append(vertex)
    return {'order': order, 'width': width, 'output_entries': entries}


def _map_byte_estimate(source, plan):
    """Exact projection-map payload size before any exponential arrays exist."""
    fixed=set(plan['selected']['cutset'])
    factors=[(v,) for v in range(source['N']) if v not in fixed]
    factors += [(u,v) for u,v,j in source['edges'] if u not in fixed and v not in fixed and [u,v,j] not in plan['glue']]
    initial_entries=sum(1<<len(f) for f in factors);recipes=set()
    for vertex in plan['selected']['order']:
        chosen=[f for f in factors if vertex in f];factors=[f for f in factors if vertex not in f]
        scope=tuple(sorted(set().union(*map(set,chosen))-{vertex}))
        for factor in chosen:recipes.add((len(scope),tuple(-1 if v==vertex else scope.index(v) for v in factor)))
        factors.append(scope)
    return sum(4*(1<<width) for width,positions in recipes),initial_entries


def prepare_plan(source, plan, options):
    """Recompute mathematical plan premises; no source-result lookup occurs."""
    n = source['N']; ports = options.get('ports', list(range(min(n, 4))))
    if not isinstance(ports, list) or any(type(v) is not int or not 0 <= v < n for v in ports) or len(set(ports)) != len(ports):
        raise ValueError('GPU ports must be distinct local vertices')
    if 1 << len(ports) > _positive(options, 'max_port_states', 256): raise ValueError('GPU port-state bound exceeded')
    p = deepcopy(plan) if plan is not None else {'ports': ports, 'glue': [], 'selected': {'cutset': []}}
    if p.get('ports') != ports: raise ValueError('GPU requested ports differ from the supplied plan')
    if 'selected' not in p or p.get('generic_cutset_plan') is False or (plan is not None and not {'order','cutset'}<=set(p.get('selected',{}))):
        raise ValueError('Component-route plan requires the CPU component backend or a fresh CUDA plan')
    if p.get('source_sha256', source['source_sha256']) != source['source_sha256']: raise ValueError('GPU plan belongs to a different source')
    fixed = p['selected'].get('cutset', [])
    if not isinstance(fixed, list) or any(type(v) is not int or not 0 <= v < n for v in fixed) or len(set(fixed)) != len(fixed) or set(fixed)&set(ports):
        raise ValueError('Invalid GPU conditioning cutset')
    branches = 1 << len(fixed)
    if branches > _positive(options, 'max_branches', 4096): raise ValueError('GPU branch bound exceeded')
    glue = p.get('glue', [])
    if not isinstance(glue, list) or len({tuple(e) for e in glue}) != len(glue) or any(e not in source['edges'] or not set(e[:2]) <= set(ports) for e in glue):
        raise ValueError('Removed glue must be distinct source edges entirely inside the retained ports')
    edges = [e for e in source['edges'] if e not in glue]
    shape = _structure(n, edges, ports, fixed, p['selected'].get('order'))
    if shape['width'] > _positive(options, 'max_width', 22): raise ValueError('GPU plan exceeds admitted elimination width')
    bound = source['energy_bound_B']-sum(abs(e[2]) for e in glue)
    if 2*source['energy_bound_B']+1 > _positive(options, 'max_energy_span', 200000): raise ValueError('GPU energy span exceeds bound')
    length = 1 << max(0, bound.bit_length())
    primes = p.get('primes')
    if primes is None:
        primes, product = [], 1
        for prime in PRIMES:
            primes.append(prime); product *= prime
            if product > 1 << n: break
    if not isinstance(primes, list) or len(set(primes)) != len(primes) or any(type(q) is not int or q not in PRIMES or (q-1) % (2*length) for q in primes):
        raise ValueError('GPU plan requires distinct qualified primes supporting order2L')
    if math.prod(primes) <= 1 << n: raise ValueError('GPU CRT capacity must strictly exceed2^N')
    for key, expected in [('N', n), ('local_bound', bound), ('root_count', length)]:
        if key in p and p[key] != expected: raise ValueError('GPU plan '+key+' differs from recomputed source')
    p.update(N=n, source_sha256=source['source_sha256'], ports=ports, glue=glue,
             local_bound=bound, root_count=length, primes=primes)
    p['selected'].update(shape, cutset=fixed, branches=branches, weighted_entries=shape['output_entries']*branches)
    p['execution_plan_sha256'] = _digest({k:p[k] for k in ['N','source_sha256','ports','glue','local_bound','root_count','primes','selected']})
    return p


def solve_gpu(source, plan=None, options=None):
    """Compute fresh exact counts; resume only source/plan-bound task residues."""
    started = time.perf_counter_ns(); options = {} if options is None else dict(options)
    unknown = set(options)-OPTIONS
    if unknown: raise ValueError('Unknown GPU options: '+str(sorted(unknown)))
    vendor_hash = _vendor()
    from .spin_catalog import validate_source
    source = validate_source(source)
    p = prepare_plan(source, plan, options)
    import numpy as np
    import cupy as cp
    from .spin_vendor.arithmetic import templates, IndexCache
    from .spin_vendor.catalog_gpu import GPUWorker
    from .spin_vendor.compat import a
    from .spin_vendor.fast_readout import reconstruct
    visible = int(cp.cuda.runtime.getDeviceCount())
    devices = options.get('devices', list(range(visible)))
    if not isinstance(devices, list) or not devices or len(set(devices)) != len(devices) or any(type(d) is not int or not 0 <= d < visible for d in devices):
        raise ValueError('GPU devices must be distinct visible CUDA ordinals')
    devices = devices[:_positive(options, 'workers', len(devices))]
    batch = min(_positive(options, 'root_batch', 16), p['root_count'])
    chunk = min(_positive(options, 'branch_group', 16), p['selected']['branches'])
    if batch & (batch-1) or chunk & (chunk-1): raise ValueError('GPU root/branch batches must be powers of two')
    max_seconds = _positive(options, 'max_seconds', 120)
    deadline = time.monotonic()+max_seconds
    map_bytes,initial_entries = _map_byte_estimate(source,p)
    if map_bytes > _positive(options, 'max_map_bytes', 2 << 30): raise ValueError('GPU projection-map byte bound exceeded')
    states = 1 << len(p['ports']); groups = p['selected']['branches']//chunk; root_batches = p['root_count']//batch
    total = groups*len(p['primes'])*root_batches
    if total > _positive(options, 'max_tasks', 1000000): raise ValueError('GPU task bound exceeded')
    # Count resident arithmetic arrays before device allocation; CUDA graph/pointer
    # overhead is checked additionally by the CUDA allocator and actual free VRAM.
    output_bytes = p['selected']['output_entries']*batch*4*2
    estimated_vram = map_bytes+output_bytes+2*(chunk*initial_entries*batch*4+chunk*batch*4+states*batch*8)
    info = []
    for device in devices:
        with cp.cuda.Device(device):
            free, capacity = cp.cuda.runtime.memGetInfo(); props = cp.cuda.runtime.getDeviceProperties(device)
        limit = options.get('max_vram_bytes', int(free)*9//10)
        if type(limit) is not int or limit < 1 or estimated_vram > min(limit, int(free)*9//10): raise ValueError('GPU plan exceeds available/configured VRAM on device '+str(device))
        name = props.get('name', b'')
        info.append({'device':device, 'name':name.decode() if isinstance(name,bytes) else str(name), 'total_bytes':int(capacity), 'free_bytes_at_admission':int(free)})
    ts = templates(source, p)
    index = IndexCache(); desc, cache, map_stats = index.compile(ts[0])
    if sum(v.nbytes for v in index.values.values()) != map_bytes:raise ArithmeticError('Projection-map preallocation estimate differs')
    values = [np.zeros((states,p['root_count']),dtype=np.int64) for _ in p['primes']]
    coverage = np.zeros((groups,len(p['primes']),root_batches),dtype=np.uint8)
    checkpoint = Path(options['checkpoint_dir']).expanduser().resolve() if options.get('checkpoint_dir') else None
    binding = {'schema':'GEN3_SPIN_GPU_TASK_CHECKPOINT_V1','source_sha256':source['source_sha256'],
               'execution_plan_sha256':p['execution_plan_sha256'],'vendor_sha256':vendor_hash,'root_batch':batch,'branch_group':chunk}
    if checkpoint:
        checkpoint.mkdir(parents=True,exist_ok=True)
        if (checkpoint/'BINDING.json').exists():
            if json.loads((checkpoint/'BINDING.json').read_text()) != binding: raise ValueError('GPU checkpoint source/plan/backend differs')
            if not options.get('resume',True): raise ValueError('Existing GPU checkpoint requires resume=true or a fresh directory')
            if (checkpoint/'STATE.json').exists():
                state=json.loads((checkpoint/'STATE.json').read_text())
                expected_name='RESIDUES.'+state['sha256']+'.npz'
                if state['file']!=expected_name or state['binding_sha256']!=_digest(binding):raise ValueError('GPU checkpoint manifest binding differs')
                file=checkpoint/expected_name
                if hashlib.sha256(file.read_bytes()).hexdigest()!=state['sha256']:raise ValueError('GPU checkpoint residue integrity mismatch')
                with np.load(file,allow_pickle=False) as old:
                    cv=old['coverage']; vv=old['values']
                    if cv.dtype!=np.uint8 or vv.dtype!=np.int64 or cv.shape != coverage.shape or vv.shape != np.asarray(values).shape or not np.all((cv==0)|(cv==1)): raise ValueError('GPU checkpoint shape/coverage differs')
                    if int(cv.sum())!=state['completed_tasks'] or any(np.any(row<0) or np.any(row>=prime) for row,prime in zip(vv,p['primes'])):raise ValueError('GPU checkpoint residues/coverage range differs')
                    coverage=cv.copy();values=[row.copy() for row in vv]
        else: (checkpoint/'BINDING.json').write_text(json.dumps(binding,sort_keys=True)+'\n')
    resumed = int(coverage.sum()); profiles=[]; task_counts={d:0 for d in devices}
    def save_checkpoint():
        if checkpoint:
            tmp=checkpoint/'RESIDUES.part'
            with tmp.open('wb') as stream: np.savez(stream,values=np.asarray(values),coverage=coverage)
            checksum=hashlib.sha256(tmp.read_bytes()).hexdigest();name='RESIDUES.'+checksum+'.npz'
            tmp.replace(checkpoint/name)
            state={'file':name,'sha256':checksum,'binding_sha256':_digest(binding),'completed_tasks':int(coverage.sum())}
            pending=checkpoint/'STATE.part';pending.write_text(json.dumps(state,sort_keys=True)+'\n');pending.replace(checkpoint/'STATE.json')
            (checkpoint/'PROGRESS.json').write_text(json.dumps({'completed_tasks':int(coverage.sum()),'total_tasks':total,'binding':binding},sort_keys=True)+'\n')
    jobs=queue.Queue(); answers=queue.Queue(maxsize=max(4,4*len(devices))); stop=threading.Event()
    for g in range(groups):
        for lo in range(0,p['root_count'],batch):
            for pi in range(len(p['primes'])):
                if not coverage[g,pi,lo//batch]: jobs.put((pi,lo,lo+batch,g*chunk))
    def worker(device):
        try:
            cp.cuda.Device(device).use(); resident={}
            boot_start=time.perf_counter_ns()
            gpu=GPUWorker(device,a,ts[:chunk],desc,cache,batch,p,resident)
            answers.put(('READY',device,{'initialization_ns':time.perf_counter_ns()-boot_start,'map_hits':gpu.map_hits,'map_misses':gpu.map_misses}))
            while not stop.is_set() and time.monotonic()<deadline:
                try: task=jobs.get_nowait()
                except queue.Empty: break
                pi,lo,hi,branchlo=task;gpu.templates=ts[branchlo:branchlo+chunk]
                tick=time.perf_counter_ns();prepared=gpu.prepare((pi,lo,hi));events=gpu.launch(prepared)
                result,milliseconds=gpu.result(prepared,events)
                answers.put(('BATCH',device,{'task':task,'values':result,'elapsed_ns':time.perf_counter_ns()-tick,'cuda_event_ns':round(milliseconds*1000000)}))
            del gpu
            cp.cuda.get_current_stream().synchronize()
        except BaseException:
            stop.set();answers.put(('ERROR',device,traceback.format_exc()))
        finally: answers.put(('DONE',device,None))
    threads=[threading.Thread(target=worker,args=(d,),name='spin-cuda-'+str(d)) for d in devices]
    launch=time.perf_counter_ns();boot=[];errors=[];last_flush=time.monotonic()
    for thread in threads:thread.start()
    done=0
    try:
        while done<len(threads):
            kind,device,data=answers.get(timeout=max_seconds+60)
            if kind=='DONE':done+=1
            elif kind=='READY':boot.append({'device':device,**data})
            elif kind=='ERROR':errors.append(data)
            elif kind=='BATCH':
                pi,lo,hi,branchlo=data.pop('task');g=branchlo//chunk
                if coverage[g,pi,lo//batch]:raise ArithmeticError('Duplicate GPU prime/root/branch task')
                values[pi][:,lo:hi]=(values[pi][:,lo:hi]+data.pop('values'))%p['primes'][pi]
                coverage[g,pi,lo//batch]=1;task_counts[device]+=1;profiles.append({'device':device,'task':[pi,lo,hi,branchlo],**data})
            if time.monotonic()-last_flush>=30:save_checkpoint();last_flush=time.monotonic()
    finally:
        stop.set()
        for thread in threads:thread.join(timeout=max_seconds+60)
        save_checkpoint()
    if errors:raise RuntimeError('CUDA spin worker failed: '+'\n'.join(errors))
    execution={'backend':'ADAPTIVE_CUDA_BRANCH_GROUP_EXACT_NTT_CRT','visible_device_count':visible,'devices':info,
               'worker_count':len(devices),'root_batch':batch,'branches_per_task':chunk,'branch_count':len(ts),
               'total_tasks':total,'completed_tasks':int(coverage.sum()),'resumed_tasks':resumed,
               'tasks_per_device':{str(k):v for k,v in task_counts.items()},'initialization':boot,
               'preparation_ns':launch-started,'gpu_phase_ns':time.perf_counter_ns()-launch,
               'map_bytes':map_bytes,'estimated_resident_array_bytes_per_device':estimated_vram,
               'vendor_manifest_sha256':vendor_hash,'execution_plan_sha256':p['execution_plan_sha256'],
               'task_event_elapsed_ns':sum(r['cuda_event_ns'] for r in profiles),
               'task_host_elapsed_ns':sum(r['elapsed_ns'] for r in profiles),
               'hardware_cost_model_applied':False,'checkpoint_directory':str(checkpoint) if checkpoint else None,
               'checkpoint_state_sha256':hashlib.sha256((checkpoint/'STATE.json').read_bytes()).hexdigest() if checkpoint else None,
               'fresh_arithmetic_tasks':len(profiles)}
    if not np.all(coverage==1):
        execution['elapsed_ns']=time.perf_counter_ns()-started
        if checkpoint:return {'status':'CHECKPOINTED','answer':None,'execution':execution}
        raise TimeoutError('GPU deadline reached; supply checkpoint_dir to retain resumable residues')
    raw=reconstruct(source,p,values)
    if sum(len(row) for row in raw['closed_port_rows'])>_positive(options,'max_output_rows',1000000):raise ValueError('GPU output-row bound exceeded')
    from .spin_exact import finalize_answer
    answer=finalize_answer(source,p['ports'],{i:{int(e):c for e,c in row} for i,row in enumerate(raw['closed_port_rows'])})
    execution.update(reconstruction_ns=raw['reconstruction_ns'],elapsed_ns=time.perf_counter_ns()-started,
                     complete_task_coverage=True,retained_readout_checks=raw['checks'])
    return {'status':'EXACT','answer':answer,'execution':execution,
            'retained_operator':{'open_y_operator':raw['open_y_operator'],'local_energy_bound':raw['local_energy_bound'],
                                 'removed_glue_edges':raw['removed_glue_edges'],'parent_port_vertices':raw['parent_port_vertices']}}
