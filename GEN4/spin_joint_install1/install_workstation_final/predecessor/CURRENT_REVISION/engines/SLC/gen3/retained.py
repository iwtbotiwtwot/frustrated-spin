"""Typed mathematical operands in the existing native Store.

The installed collection is immutable seed material. Objects are adopted lazily
into a session's authenticated checkpoint, including their dependency closure.
No process, discovery service, or external database is needed.
"""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import re

from CURRENT_REVISION.engines.SLC.gen2.exact import canonical, canonical_bytes, digest

SCHEMA = 'SLC_MATHEMATICAL_OBJECT_V1'
PREFIX = 'capability:math-object:'
KINDS = {'polynomial', 'matrix', 'exchange_spectrum', 'mathematical_result',
         'source_record', 'calculation'}
OPS = tuple('GEN3_RESULT_' + x for x in (
    'DISCOVER', 'SELECT', 'GET', 'PUBLISH', 'APPLY', 'MOMENTS', 'COMPARE',
    'COMPOSE', 'DEPENDENCIES', 'EXPORT', 'IMPORT'))
LIBRARY = Path(__file__).resolve().parents[1] / 'mathematical_library'
LIBRARY_INDEX_SHA256 = 'da2f7eb67ac3c996bc853db09bbe0abb0ab703639d611d7cc285628cb652c6d1'  # Installed collection binding.


def fields(value, required=(), optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        raise ValueError('Supply exactly the declared retained-result fields')


def reference(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('A mathematical reference is a SHA256 content identity')
    return value


def index():
    path = LIBRARY / 'INDEX.json'
    if not path.exists():
        if LIBRARY_INDEX_SHA256 is not None:
            raise ValueError('Installed mathematical collection is missing')
        return {'objects': {}, 'exchange': {}, 'collections': {}}
    raw = path.read_bytes()
    if LIBRARY_INDEX_SHA256 is not None and hashlib.sha256(raw).hexdigest() != LIBRARY_INDEX_SHA256:
        raise ValueError('Installed mathematical collection binding differs')
    return json.loads(raw)


def nested_refs(value):
    refs = set()
    if isinstance(value, dict):
        if 'result_ref' in value:
            refs.add(reference(value['result_ref']))
        for item in value.values():
            refs.update(nested_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(nested_refs(item))
    return refs


def validate(obj):
    fields(obj, ('schema', 'kind', 'source_binding', 'value', 'dependencies', 'provenance'))
    if obj['schema'] != SCHEMA or obj['kind'] not in KINDS:
        raise ValueError('Unsupported mathematical object type')
    if not isinstance(obj['source_binding'], dict) or not obj['source_binding']:
        raise ValueError('Retained mathematics requires an explicit source binding')
    if not isinstance(obj['provenance'], dict) or not obj['provenance']:
        raise ValueError('Retained mathematics requires provenance')
    if not isinstance(obj['dependencies'], list) or obj['dependencies'] != sorted(set(obj['dependencies'])):
        raise ValueError('Dependencies must be unique and sorted')
    for ref in obj['dependencies']:
        reference(ref)
    if not nested_refs(obj['value']) <= set(obj['dependencies']):
        raise ValueError('An operand reference is missing from the dependency closure')
    canonical_bytes(obj)
    if obj['kind'] == 'polynomial':
        fields(obj['value'], ('coefficients_ascending',))
        cs = obj['value']['coefficients_ascending']
        if not isinstance(cs, list) or len(cs) < 2:
            raise ValueError('A polynomial needs ascending exact coefficients')
        for c in cs:
            if type(c) not in (int, str) or not re.fullmatch(r'[+-]?\d+', str(c)):
                raise ValueError('Integer polynomial coefficients required')
        if int(cs[-1]) != 1:
            raise ValueError('Retained spectral polynomials must be monic')
    if obj['kind'] == 'matrix':
        a = obj['value']
        if not isinstance(a, list) or not a or not isinstance(a[0], list) or not a[0]:
            raise ValueError('A matrix needs nonempty rows')
        for row in a:
            if not isinstance(row, list) or len(row) != len(a[0]):
                raise ValueError('Matrix rows differ')
            for c in row:
                if type(c) not in (int, str):
                    raise ValueError('Exact matrix entries required')
                Fraction(c)


def put(machine, kind, value, source, provenance, dependencies=()):
    obj = canonical(dict(schema=SCHEMA, kind=kind, value=value, source_binding=source,
                         provenance=provenance, dependencies=sorted(set(dependencies))))
    validate(obj)
    for ref in obj['dependencies']:
        get(machine, ref)
    ref = digest(obj)
    key = PREFIX + ref
    if key in machine.origins and machine.origins[key] != obj:
        raise ValueError('Immutable mathematical object collision')
    machine.origins[key] = obj
    machine.dirty['origins'].add(key)
    return ref


def get(machine, ref, kind=None, source=None, visiting=None):
    reference(ref)
    key = PREFIX + ref
    obj = machine.origins.get(key)
    if obj is None:
        path = LIBRARY / 'objects' / ref[:2] / ref[2:]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref:
            raise ValueError('Installed mathematical object hash differs')
        obj = json.loads(raw)
    verified = getattr(machine, '_retained_verified', None)
    if verified is None:
        verified = machine._retained_verified = set()
    if ref not in verified:
        if digest(obj) != ref:
            raise ValueError('Retained mathematical object hash differs')
        validate(obj)
        verified.add(ref)
    if kind is not None and obj['kind'] != kind:
        raise ValueError('Retained operand type differs: expected ' + kind)
    if source is not None and obj['source_binding'] != source:
        raise ValueError('Retained operand source differs')
    visiting = set() if visiting is None else visiting
    if ref in visiting:
        raise ValueError('Cyclic mathematical dependencies')
    if key not in machine.origins:
        visiting.add(ref)
        for dep in obj['dependencies']:
            get(machine, dep, visiting=visiting)
        visiting.remove(ref)
        machine.origins[key] = deepcopy(obj)
        machine.dirty['origins'].add(key)
        machine.stats['retained_objects_adopted'] += 1
    return deepcopy(obj)


def resolve(machine, value, dependencies=None):
    dependencies = [] if dependencies is None else dependencies
    if isinstance(value, dict) and 'result_ref' in value:
        fields(value, ('result_ref',), ('field', 'kind', 'source_binding'))
        obj = get(machine, value['result_ref'], value.get('kind'), value.get('source_binding'))
        dependencies.append(dict(result_ref=value['result_ref'], kind=obj['kind'], source_binding=obj['source_binding']))
        result = obj['value']
        path = value.get('field', [])
        if not isinstance(path, list):
            raise ValueError('Reference field must be a list of keys/indices')
        for key in path:
            if not ((isinstance(result, dict) and isinstance(key, str) and key in result) or
                    (isinstance(result, list) and type(key) is int and 0 <= key < len(result))):
                raise ValueError('Unknown retained result field')
            result = result[key]
        return deepcopy(result)
    if isinstance(value, dict):
        return {k: resolve(machine, v, dependencies) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(machine, v, dependencies) for v in value]
    return deepcopy(value)


def capture(machine, operation, payload, result):
    source = payload.get('source_binding')
    if not isinstance(source, dict) or not source:
        return None
    deps = nested_refs(payload) | nested_refs(result)
    for ref in deps:
        get(machine, ref)
    return put(machine, 'mathematical_result', result, source,
               dict(operation=operation, request=payload, origin='NATIVE_MATHEMATICAL_OPERATION'), deps)


def spectrum(machine, ref):
    obj = get(machine, ref, 'exchange_spectrum')
    data = obj['value']
    fields(data, ('schema', 'L', 'local_dimension', 'physical_dimension', 'partitions', 'global_factors'))
    if data['schema'] != 'SLC_EXCHANGE_SPECTRUM_V1':
        raise ValueError('Unsupported exchange spectrum')
    if type(data['L']) is not int or not 2 <= data['L'] <= 32 or type(data['local_dimension']) is not int or not 1 <= data['local_dimension'] <= 8:
        raise ValueError('Invalid exchange dimensions')
    if data['physical_dimension'] != data['local_dimension'] ** data['L']:
        raise ValueError('Exchange physical dimension differs')
    total = 0
    for f in data['global_factors']:
        p = get(machine, f['result_ref'], 'polynomial')['value']['coefficients_ascending']
        if type(f['multiplicity']) is not int or f['multiplicity'] <= 0:
            raise ValueError('Positive integral factor multiplicity required')
        total += (len(p) - 1) * f['multiplicity']
    if total != data['physical_dimension']:
        raise ValueError('Global factor multiplicities do not close')
    return obj


def moments(machine, ref, order):
    if type(order) is not int or not 0 <= order <= 64:
        raise ValueError('Moment order must be in 0..64')
    obj = spectrum(machine, ref)
    values = [0] * (order + 1)
    for f in obj['value']['global_factors']:
        cs = get(machine, f['result_ref'], 'polynomial')['value']['coefficients_ascending']
        n = len(cs) - 1
        # Newton sums need only the requested number of leading coefficients.
        c = [1] + [int(cs[n - i]) for i in range(1, min(n, order) + 1)]
        power = [n]
        for k in range(1, order + 1):
            v = -sum(c[j] * power[k-j] for j in range(1, min(k, n+1)))
            if k <= n:
                v -= k * c[k]
            power.append(v)
        for k, v in enumerate(power):
            values[k] += f['multiplicity'] * v
    dim = obj['value']['physical_dimension']
    return dict(L=obj['value']['L'], physical_dimension=dim, trace_powers=[str(v) for v in values],
                normalized_moments=[str(Fraction(v, dim)) for v in values],
                method='EXACT_NEWTON_SUMS_FROM_RETAINED_FACTORS', spectral_solves=0)


def compose(machine, ref, local_family, collective=False):
    from .capabilities.mathematical import parametric, schur, pol, g
    import sympy as s
    obj = spectrum(machine, ref)
    ex = obj['value']
    if type(collective) is not bool:
        raise ValueError('collective must be Boolean')
    local = (deepcopy(local_family) if isinstance(local_family, dict) and 'characteristic_coefficients' in local_family
             else parametric(dict(**local_family, discriminant=False)))
    n = local['dimension']
    cs = local['characteristic_coefficients']
    if n != ex['local_dimension'] or len(cs) != n + 1 or pol(cs[-1]).as_expr() != 1:
        raise ValueError('Local and exchange carriers differ')
    for row in cs:
        pol(row)
    sectors = []
    total = terms = 0
    seen = set()
    for row in ex['partitions']:
        shape = row['partition']
        if tuple(shape) in seen or sum(shape) != ex['L']:
            raise ValueError('Duplicate or wrong-length partition')
        seen.add(tuple(shape))
        weights = schur(dict(partition=shape, local_dimension=n))
        dimension = 0
        for factor in row['factors']:
            p = get(machine, factor['result_ref'], 'polynomial')['value']['coefficients_ascending']
            mult = factor['multiplicity']
            if type(mult) is not int or mult < 1:
                raise ValueError('Positive factor multiplicity required')
            dimension += (len(p) - 1) * mult
        if dimension != weights['Specht_dimension']:
            raise ValueError('Retained partition dimensions do not close')
        total += dimension * weights['GL_dimension']
        terms += len(row['factors']) * len(weights['weights'])
        sectors.append(dict(partition=shape, factors=row['factors'], weights=weights['weights'],
                            GL_dimension=weights['GL_dimension'], Specht_dimension=dimension))
    if total != ex['physical_dimension']:
        raise ValueError('Complete matter composition does not close')
    return dict(schema='SLC_COMPACT_MATTER_SPECTRUM_V1', L=ex['L'], local_dimension=n,
                exchange={'result_ref': ref}, local_characteristic=cs, sectors=sectors,
                physical_dimension=total, dimension_closed=True, factor_weight_terms=terms,
                energy_formula='J*e + mu*s + nu*(s^2-r)/2' if collective else 'J*e + mu*s',
                s='sum_i occupation_i*q_i(g)', r='sum_i occupation_i*q_i(g)^2',
                multiplicity='factor multiplicity times Schur weight multiplicity per root; add coincident energies',
                parameters=['J', 'mu', 'g'] + (['nu'] if collective else []),
                collective_geometry='Equal all-to-all unordered pairs' if collective else None,
                exchange_arithmetic_reexecuted=False, representation='FACTOR_REFERENCES_TIMES_SCHUR_WEIGHTS')


def closure(machine, roots):
    objects = {}
    def visit(ref):
        if ref in objects:
            return
        obj = get(machine, ref)
        objects[ref] = obj
        for dep in obj['dependencies']:
            visit(dep)
    for ref in roots:
        visit(ref)
    return objects


def persist_calculation(machine, operation, request, result, deps):
    deps = sorted(set(deps) | nested_refs(result))
    source = dict(operation=operation, request_sha256=digest(request))
    ref = put(machine, 'mathematical_result', result, source,
              dict(operation=operation, request=request, backend='SHARED_SLC_EXACT'), deps)
    return ref


def engine_identity():
    paths = [Path(__file__), Path(__file__).parent/'capabilities/mathematical.py']
    sources = {}
    for path in paths:
        raw = path.read_bytes()
        if path.name == 'retained.py':
            raw = ('\n'.join(line for line in raw.decode().splitlines()
                              if not line.startswith('LIBRARY_INDEX_SHA256 =')) + '\n').encode()
        sources[path.name] = hashlib.sha256(raw).hexdigest()
    return digest(sources)


def dispatch(runtime, operation, payload):
    machine = runtime.machine
    if operation not in OPS:
        raise ValueError('Unknown retained-result operation')
    if operation == 'GEN3_RESULT_DISCOVER':
        fields(payload, (), ('kind', 'L', 'scope'))
        if payload.get('scope', 'all') not in ('all', 'installed', 'session'):
            raise ValueError('Unknown discovery scope')
        seed = index()
        found = {} if payload.get('scope') == 'session' else deepcopy(seed['objects'])
        if payload.get('scope') != 'installed':
            for key, obj in machine.origins.items():
                if key.startswith(PREFIX):
                    found[key[len(PREFIX):]] = dict(kind=obj['kind'], source_binding=obj['source_binding'],
                                                   L=obj['value'].get('L') if isinstance(obj['value'], dict) else None)
        rows = [dict(result_ref=ref, **meta) for ref, meta in sorted(found.items())
                if ('kind' not in payload or meta['kind'] == payload['kind'])
                and ('L' not in payload or meta.get('L') == payload['L'])]
        return dict(objects=rows, count=len(rows), collections=seed.get('collections', {}),
                    exchange_levels=sorted(map(int, seed.get('exchange', {}))))
    if operation == 'GEN3_RESULT_GET':
        fields(payload, ('result_ref',), ('kind', 'source_binding', 'field'))
        deps = []
        value = resolve(machine, payload, deps)
        return dict(result_ref=payload['result_ref'], value=value, dependencies=deps, recomputed=False)
    if operation == 'GEN3_RESULT_SELECT':
        fields(payload, ('kind', 'source_binding'))
        matches = []
        for ref, meta in index()['objects'].items():
            if meta['kind'] == payload['kind'] and meta.get('source_binding') == payload['source_binding']:
                matches.append(ref)
        for key, obj in machine.origins.items():
            if key.startswith(PREFIX) and obj['kind'] == payload['kind'] and obj['source_binding'] == payload['source_binding']:
                matches.append(key[len(PREFIX):])
        return dict(matches=sorted(set(matches)), available=bool(matches), arithmetic_calls=0,
                    meaning='Exact type and complete source-binding match; no substitute source selected')
    if operation == 'GEN3_RESULT_PUBLISH':
        fields(payload, ('kind', 'value', 'source_binding', 'provenance'), ('dependencies',))
        # Arbitrary publications remain explicit declarations; they cannot forge a solver receipt.
        if payload['kind'] in ('exchange_spectrum', 'calculation'):
            raise ValueError('Use source-bound collection ingestion for exchange and native execution for calculations')
        ref = put(machine, payload['kind'], payload['value'], payload['source_binding'],
                  dict(admission='CALLER_DECLARED_EXACT_INPUT', evidence=payload['provenance']),
                  payload.get('dependencies', []))
        return dict(result_ref=ref, kind=payload['kind'])
    if operation in ('GEN3_RESULT_DEPENDENCIES', 'GEN3_RESULT_EXPORT'):
        fields(payload, ('roots',))
        if not isinstance(payload['roots'], list) or not payload['roots']:
            raise ValueError('Supply nonempty root references')
        objects = closure(machine, payload['roots'])
        if operation.endswith('DEPENDENCIES'):
            return dict(roots=payload['roots'], objects=[dict(result_ref=k, kind=v['kind'], dependencies=v['dependencies'])
                                                        for k, v in sorted(objects.items())])
        calculations = {k: deepcopy(v) for k, v in machine.origins.items()
                        if k.startswith('capability:math-request:') and v['result_ref'] in objects}
        body = dict(schema='SLC_MATHEMATICAL_BUNDLE_V1', roots=payload['roots'], objects=objects,
                    calculations=calculations)
        external=[dict(result_ref=ref,**obj['value']['joint']['external_archive']) for ref,obj in sorted(objects.items())
                  if isinstance(obj.get('value'),dict) and obj['value'].get('joint',{}).get('external_archive')]
        if external:body['external_artifacts']=external
        return dict(bundle=body, sha256=digest(body), object_count=len(objects),
                    portability='REQUIRES_HASH_BOUND_EXTERNAL_DATA' if external else 'SELF_CONTAINED')
    if operation == 'GEN3_RESULT_IMPORT':
        fields(payload, ('bundle', 'sha256'))
        body = payload['bundle']
        fields(body, ('schema', 'roots', 'objects'), ('calculations','external_artifacts'))
        if body['schema'] != 'SLC_MATHEMATICAL_BUNDLE_V1' or digest(body) != payload['sha256']:
            raise ValueError('Portable mathematical bundle identity differs')
        if not isinstance(body['roots'], list) or not body['roots'] or not isinstance(body['objects'], dict):
            raise ValueError('Portable closure requires roots and objects')
        for ref, obj in body['objects'].items():
            validate(obj)
            if digest(obj) != reference(ref) or not set(obj['dependencies']) <= body['objects'].keys():
                raise ValueError('Portable object hash or dependency closure differs')
        expected_external=[dict(result_ref=ref,**obj['value']['joint']['external_archive']) for ref,obj in sorted(body['objects'].items())
                           if isinstance(obj.get('value'),dict) and obj['value'].get('joint',{}).get('external_archive')]
        if body.get('external_artifacts',[])!=expected_external:
            raise ValueError('Portable external custody inventory differs')
        if not set(body['roots']) <= body['objects'].keys():
            raise ValueError('Portable root missing')
        for key, row in body.get('calculations', {}).items():
            fields(row, ('binding', 'result_ref'))
            if key != 'capability:math-request:' + digest(row['binding']) or row['result_ref'] not in body['objects']:
                raise ValueError('Portable calculation index differs')
            obj = body['objects'][row['result_ref']]
            if obj['provenance'].get('request') != row['binding'].get('request'):
                raise ValueError('Portable calculation and derivation differ')
        # Admission preserves evidence labels; imported objects are never labelled newly solved.
        for ref, obj in body['objects'].items():
            key = PREFIX + ref
            if key in machine.origins and machine.origins[key] != obj:
                raise ValueError('Portable object conflicts with retained state')
        for ref, obj in body['objects'].items():
            machine.origins[PREFIX + ref] = deepcopy(obj)
            machine.dirty['origins'].add(PREFIX + ref)
        for key, row in body.get('calculations', {}).items():
            machine.origins[key] = deepcopy(row)
            machine.dirty['origins'].add(key)
        return dict(roots=body['roots'], objects_imported=len(body['objects']), arithmetic_calls=0)
    if operation == 'GEN3_RESULT_APPLY':
        fields(payload, ('operation', 'payload'))
        if payload['operation']=='GEN3_SPIN_READOUT':
            from . import spin_joint
            request=deepcopy(payload)
            code={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                  (Path(spin_joint.__file__),Path(__file__).parent/'spin_exact.py')}
            binding=dict(engine=digest(code),request=request)
            key='capability:math-request:'+digest(binding)
            saved=machine.origins.get(key) or index().get('calculations',{}).get(key)
            if saved is not None:
                machine.origins[key]=deepcopy(saved);machine.dirty['origins'].add(key)
                result=get(machine,saved['result_ref'])['value']
                machine.stats['retained_calculations_reused']+=1
                return dict(result_ref=saved['result_ref'],result=result,reused=True,arithmetic_calls=0)
            result=runtime.execute(payload['operation'],payload['payload'])
            ref=persist_calculation(machine,payload['operation'],request,result,nested_refs(request))
            machine.origins[key]=dict(binding=binding,result_ref=ref);machine.dirty['origins'].add(key)
            machine.stats['retained_calculations_executed']+=1
            return dict(result_ref=ref,result=result,reused=False,arithmetic_calls=1)
        from .capabilities.mathematical import OPS as math_ops
        if payload['operation'] not in math_ops[:-1]:
            raise ValueError('Apply accepts registered pure mathematical operations')
        request = deepcopy(payload)
        fields(request['payload'], ('name', 'source_binding', 'data'), ('context',))
        request['payload'].pop('name')
        binding = dict(engine=engine_identity(), request=request)
        cache_key = 'capability:math-request:' + digest(binding)
        saved = machine.origins.get(cache_key) or index().get('calculations', {}).get(cache_key)
        if saved is not None:
            machine.origins[cache_key] = deepcopy(saved)
            machine.dirty['origins'].add(cache_key)
            result = get(machine, saved['result_ref'])['value']
            machine.stats['retained_calculations_reused'] += 1
            return dict(result_ref=saved['result_ref'], result=result, reused=True, arithmetic_calls=0)
        call = deepcopy(payload['payload'])
        call['name'] = 'retained-' + digest(binding)[:48]
        result = runtime.execute(payload['operation'], call)
        ref = persist_calculation(machine, payload['operation'], request, result, nested_refs(call))
        machine.origins[cache_key] = dict(binding=binding, result_ref=ref)
        machine.dirty['origins'].add(cache_key)
        machine.stats['retained_calculations_executed'] += 1
        return dict(result_ref=ref, result=result, reused=False, arithmetic_calls=1)
    if operation == 'GEN3_RESULT_MOMENTS':
        fields(payload, ('result_ref',), ('order',))
        result = moments(machine, payload['result_ref'], payload.get('order', 4))
    elif operation == 'GEN3_RESULT_COMPARE':
        fields(payload, ('left', 'right'))
        a, b = (spectrum(machine, payload[k])['value'] for k in ('left', 'right'))
        aa = {f['result_ref']: f['multiplicity'] for f in a['global_factors']}
        bb = {f['result_ref']: f['multiplicity'] for f in b['global_factors']}
        # Polynomial content, not its acquisition provenance, determines algebraic equality.
        def algebraic(fs):
            return {digest(get(machine, r, 'polynomial')['value']): dict(result_ref=r, multiplicity=m)
                    for r, m in fs.items()}
        aa, bb = algebraic(aa), algebraic(bb)
        result = dict(left_L=a['L'], right_L=b['L'], shared=[dict(left=aa[k], right=bb[k]) for k in sorted(aa.keys() & bb.keys())],
                      left_only=[aa[k] for k in sorted(aa.keys()-bb.keys())],
                      right_only=[bb[k] for k in sorted(bb.keys()-aa.keys())],
                      meaning='Exact shared polynomial factors; multiplicities retain their own source level')
    elif operation == 'GEN3_RESULT_COMPOSE':
        fields(payload, ('result_ref', 'local_family'), ('collective',))
        deps = []
        local = resolve(machine, payload['local_family'], deps)
        result = compose(machine, payload['result_ref'], local, payload.get('collective', False))
    else:
        raise ValueError('Unimplemented retained-result operation')
    deps = nested_refs(payload)
    if operation.endswith('COMPARE'):
        deps.update([payload['left'], payload['right']])
    ref = persist_calculation(machine, operation, payload, result, deps)
    return dict(result_ref=ref, result=result, spectral_solves=0)
