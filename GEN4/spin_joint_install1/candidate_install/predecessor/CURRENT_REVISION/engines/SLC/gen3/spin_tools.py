"""One shared entry point for exact source-aware spin and finite-factor tools."""
from . import retained,spin_catalog,spin_sources

NEW_OPS=tuple('GEN3_SPIN_'+s for s in ['TOOLS','SOURCES','SOURCE','SELECT','SOLVE','CONTRACT','READOUT'])
OPS=tuple(dict.fromkeys(spin_catalog.OPS+NEW_OPS))

def dispatch(runtime,operation,payload):
    if operation=='GEN3_SPIN_TOOLS':
        retained.fields(payload)
        registry=spin_sources.metadata()
        return dict(schema='GEN3_GEN4_SHARED_SPIN_TOOLS_V1',operations=list(OPS),
                    default_sizes=spin_catalog.metadata()['sizes'],source_count=registry['source_count'],
                    source_identity='Explicit family and canonical graph hash; N alone selects the retained default',
                    exact_backends=['CPU_FLINT_COMPONENT_POLYNOMIAL','CPU_FLINT_FACTOR_ELIMINATION','CUDA_MODULAR_FACTOR_ELIMINATION'],
                    scope='Exact finite integer-coupled binary graphs and explicit finite signed factors; domain-to-source mappings supplied by the caller',
                    planning='Identical-source caches, structural plans and explicit native focused pairwise selection',
                    timing_scope='Retained fitted cost models describe fourteen Blackwell MIG workers; this installation does not relabel them as current-host timings',
                    recovery='Published exact result references and existing authenticated DomainSession checkpoints',
                    external_services_started=False)
    if operation in spin_sources.OPS:
        return spin_sources.dispatch(runtime,operation,payload)
    if operation in ['GEN3_SPIN_SELECT','GEN3_SPIN_SOLVE','GEN3_SPIN_READOUT']:
        p=dict(payload)
        selector_keys=['N','family']
        if 'source' not in p:selector_keys.append('source_sha256')
        selector={k:p.pop(k) for k in selector_keys if k in p}
        if selector:
            if 'source' in p:raise ValueError('Choose an explicit graph or registry selectors, not both')
            record=spin_sources.dispatch(runtime,'GEN3_SPIN_SOURCE',selector)
            if operation=='GEN3_SPIN_READOUT':
                if 'result_ref' in p:raise ValueError('Choose a result reference or source selectors, not both')
                p['result_ref']=record['result_ref']
            else:
                p['source']=record['source']
                if 'ports' not in p:
                    ports=record.get('spectrum',{}).get('retained_ports')
                    if ports is not None:p['ports']=ports
        if operation=='GEN3_SPIN_SELECT':
            from .spin_select import dispatch as select_dispatch
            return select_dispatch(runtime,operation,p)
        from .spin_exact import dispatch as exact_dispatch
        return exact_dispatch(runtime,operation,p)
    if operation=='GEN3_SPIN_CONTRACT':
        from .spin_exact import dispatch as exact_dispatch
        return exact_dispatch(runtime,operation,payload)
    return spin_catalog.dispatch(runtime,operation,payload)
