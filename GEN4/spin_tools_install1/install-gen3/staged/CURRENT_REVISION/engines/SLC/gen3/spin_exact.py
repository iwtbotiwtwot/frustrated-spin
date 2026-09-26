"""Exact reusable spin spectra, signed finite-factor contraction and readout.

All coefficient arithmetic is native FLINT. Python owns source checks, graph
structure, finite indices, admission, persistence and serialized receipts.
"""
from collections import defaultdict
from copy import deepcopy
import hashlib
import itertools
import json
import time

from flint import fmpz, fmpq, fmpz_poly

OPS = ('GEN3_SPIN_SOLVE', 'GEN3_SPIN_CONTRACT', 'GEN3_SPIN_READOUT')
SCHEMA = 'GEN3_EXACT_SPIN_DOS_V1'
ENERGY = 'E=-sum(J_uv*s_u*s_v)-sum(h_u*s_u); s_u in {-1,+1}'
DEFAULTS = {'method': 'auto', 'max_component_size': 20,
            'max_assignments': 2000000, 'max_factor_work': 10000000,
            'max_intermediate_entries': 1000000, 'max_output_rows': 1000000,
            'max_energy_span': 200000, 'max_port_states': 256,
            'max_seconds': 120}


class CapacityError(ValueError):
    """Explicit computational admission limit, not a mathematical exclusion."""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def integer(value, name='integer'):
    if type(value) is not int:
        raise ValueError(name+' must be a Python integer, not a float or bool')
    return value


def coefficient(value):
    if type(value) is int:
        return fmpz(value)
    if isinstance(value, fmpz):
        return value
    if isinstance(value, str) and len(value) <= 4096:
        digits = value[1:] if value[:1] in ('+', '-') else value
        if digits and digits.isascii() and digits.isdigit():
            return fmpz(value)
    raise ValueError('Finite-factor coefficients must be exact integer strings or integers')


def rational(value):
    if type(value) is int:
        return fmpq(value)
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError('Exact rational integer or numerator/denominator string required')
    pieces = value.split('/')
    if len(pieces) == 1:
        return fmpq(coefficient(pieces[0]))
    if len(pieces) != 2:
        raise ValueError('Invalid rational coefficient')
    numerator, denominator = map(coefficient, pieces)
    if denominator == 0:
        raise ValueError('Rational denominator is zero')
    return fmpq(numerator, denominator)


def options_checked(options=None):
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise ValueError('options must be a dictionary')
    permitted = set(DEFAULTS) | {'elimination_order'}
    if set(options)-permitted:
        raise ValueError('Unknown CPU options: '+','.join(sorted(set(options)-permitted)))
    out = dict(DEFAULTS, **options)
    if out['method'] not in ('auto', 'components', 'variable_elimination'):
        raise ValueError('Unknown CPU exact method')
    for name in DEFAULTS:
        if name == 'method':
            continue
        if integer(out[name], name) < 1:
            raise ValueError(name+' must be positive')
    return out


class Budget:
    def __init__(self, options):
        self.options = options
        self.started = time.perf_counter_ns()
        self.work = 0
        self.peak_entries = 0

    def check(self):
        if time.perf_counter_ns()-self.started > self.options['max_seconds']*1000000000:
            raise CapacityError('Declared wall-time admission limit reached')

    def charge(self, work, entries=0):
        self.check()
        if entries > self.options['max_intermediate_entries']:
            raise CapacityError('Finite-factor intermediate table exceeds max_intermediate_entries')
        if self.work+work > self.options['max_factor_work']:
            raise CapacityError('Exact finite-factor work exceeds max_factor_work')
        self.work += work
        self.peak_entries = max(self.peak_entries, entries)


def validate_source(source):
    # Campaign module and installed module share the current source normalizer.
    try:
        from .spin_catalog import validate_source as normalize
    except ImportError:
        from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import validate_source as normalize
    if not isinstance(source, dict):
        raise ValueError('Supply an explicit spin graph')
    if source.get('constant', 0) != 0 or source.get('native_factors'):
        raise ValueError('This graph API accepts pair interactions and fields only; use explicit factor contraction for higher-order tables')
    if integer(source.get('N'), 'N') > 4096:
        raise CapacityError('Source exceeds the declared 4096-variable admission ceiling')
    return normalize(source)


def check_ports(source, ports, options):
    if not isinstance(ports, list) or any(type(v) is not int for v in ports):
        raise ValueError('ports must be a list of local integer vertex indices')
    if len(set(ports)) != len(ports) or any(v < 0 or v >= source['N'] for v in ports):
        raise ValueError('Ports must be distinct existing local vertices')
    if (1 << len(ports)) > options['max_port_states']:
        raise CapacityError('Retained port table exceeds max_port_states')
    return list(ports)


def components(source):
    adjacent = [set() for _ in range(source['N'])]
    for u, v, j in source['edges']:
        if j != 0:
            adjacent[u].add(v)
            adjacent[v].add(u)
    unseen = set(range(source['N']))
    groups = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        todo, group = [seed], []
        while todo:
            u = todo.pop()
            group.append(u)
            new = adjacent[u] & unseen
            unseen.difference_update(new)
            todo.extend(sorted(new, reverse=True))
        groups.append(sorted(group))
    return groups


def finalize_answer(source, ports, port_dos):
    """Canonical closed-energy answer shared with the GPU adapter.

    port_dos maps bitmask -> {energy: exact count}; bit i=1 means s_ports[i]=+1.
    """
    expected_states = set(range(1 << len(ports)))
    if set(port_dos) != expected_states:
        raise ArithmeticError('A complete spectrum must retain every requested port state')
    scalar = defaultdict(fmpz)
    rows = []
    expected_row = fmpz(1) << (source['N']-len(ports))
    for mask in sorted(port_dos):
        counts = {integer(e, 'energy'): coefficient(n) for e, n in port_dos[mask].items() if n != 0}
        if any(n < 0 for n in counts.values()):
            raise ArithmeticError('A spin density of states cannot have negative multiplicities')
        total = sum(counts.values(), fmpz(0))
        if total != expected_row:
            raise ArithmeticError('Conditional configuration count differs from 2^(N-number_of_ports)')
        for e, n in counts.items():
            scalar[e] += n
        rows.append({'state': [1 if mask & (1 << i) else -1 for i in range(len(ports))],
                     'dos': [[e, str(n)] for e, n in sorted(counts.items())],
                     'configuration_count': str(total)})
    moments = [sum((n*fmpz(e)**k for e, n in scalar.items()), fmpz(0)) for k in range(3)]
    expected = fmpz(1) << source['N']
    square_sum = sum((fmpz(h)**2 for h in source['fields']), fmpz(0))
    square_sum += sum((fmpz(j)**2 for _, _, j in source['edges']), fmpz(0))
    if moments != [expected, fmpz(0), expected*square_sum]:
        raise ArithmeticError('Exact count/first/second moment identities failed')
    ground = min(scalar)
    answer = {'schema': SCHEMA, 'source_sha256': source['source_sha256'], 'N': source['N'],
              'energy_convention': ENERGY, 'ports': list(ports),
              'port_state_convention': 'bit i=1 is +1 at local vertex ports[i]; bit i=0 is -1',
              'scalar_dos': [[e, str(n)] for e, n in sorted(scalar.items())],
              'port_rows': rows, 'configuration_count': str(expected),
              'ground_energy': ground, 'ground_degeneracy': str(scalar[ground]),
              'energy_moments': {str(k): str(v) for k, v in enumerate(moments)}}
    answer['spectrum_sha256'] = digest(answer)
    return answer


def _enumerate_component(source, group, ports, budget):
    local = {v: i for i, v in enumerate(group)}
    fields = [fmpz(source['fields'][v]) for v in group]
    adjacent = [[] for _ in group]
    energy = sum(fields, fmpz(0))
    for u, v, j in source['edges']:
        if j and u in local and v in local:
            weight = fmpz(j)
            adjacent[local[u]].append((local[v], weight))
            adjacent[local[v]].append((local[u], weight))
            energy -= weight
    local_ports = {local[v]: i for i, v in enumerate(ports) if v in local}
    spins = [-1]*len(group)
    state = 0
    out = defaultdict(lambda: defaultdict(fmpz))
    size = 1 << len(group)
    budget.charge(size, 1 << len(local_ports))
    for step in range(size):
        out[state][int(energy)] += fmpz(1)
        if step+1 == size:
            break
        flip = ((step+1) & -(step+1)).bit_length()-1
        field = fields[flip] + sum((j*spins[v] for v, j in adjacent[flip]), fmpz(0))
        energy += 2*spins[flip]*field
        spins[flip] = -spins[flip]
        if flip in local_ports:
            state ^= 1 << local_ports[flip]
        if (step & 4095) == 0:
            budget.check()
    return out


def _polynomial(histogram, options):
    lo, hi = min(histogram), max(histogram)
    if hi-lo > options['max_energy_span']:
        raise CapacityError('Energy support exceeds max_energy_span')
    coefficients = [fmpz(0)]*(hi-lo+1)
    for e, n in histogram.items():
        coefficients[e-lo] = n
    return lo, fmpz_poly(coefficients)


def _component_solve(source, ports, options, budget, groups):
    sizes = [len(g) for g in groups]
    if max(sizes) > options['max_component_size']:
        raise CapacityError('A component exceeds max_component_size; choose bounded elimination or GPU')
    assignments = sum(1 << size for size in sizes)
    if assignments > options['max_assignments']:
        raise CapacityError('Component enumeration exceeds max_assignments')
    accumulated = {0: (0, fmpz_poly([1]))}
    for group in groups:
        histograms = _enumerate_component(source, group, ports, budget)
        local = {state: _polynomial(hist, options) for state, hist in histograms.items()}
        if len(accumulated)*len(local) > options['max_port_states']:
            raise CapacityError('Conditional convolution exceeds max_port_states')
        combined = {}
        for mask_a, (offset_a, poly_a) in accumulated.items():
            for mask_b, (offset_b, poly_b) in local.items():
                if mask_a & mask_b:
                    raise ArithmeticError('Disconnected component port masks overlap')
                length = len(poly_a)+len(poly_b)-1
                if length-1 > options['max_energy_span']:
                    raise CapacityError('Convolution support exceeds max_energy_span')
                budget.charge(1, length)
                combined[mask_a | mask_b] = (offset_a+offset_b, poly_a*poly_b)
        accumulated = combined
    count_rows = sum(len(poly) for _, poly in accumulated.values())
    if count_rows > options['max_output_rows']:
        raise CapacityError('Exact output exceeds max_output_rows')
    result = {state: {offset+i: poly[i] for i in range(len(poly)) if poly[i] != 0}
              for state, (offset, poly) in accumulated.items()}
    return result, {'method': 'NATIVE_FLINT_GRAY_COMPONENTS_AND_POLYNOMIAL_CONVOLUTION',
                    'component_sizes': sizes, 'enumerated_assignments': assignments,
                    'polynomial_backend': 'FLINT fmpz_poly multiplication'}


def _product(values):
    result = 1
    for value in values:
        result *= value
    return result


def _strides(scope, sizes):
    out, size = {}, 1
    for variable in reversed(scope):
        out[variable] = size
        size *= sizes[variable]
    return out


def _elimination_order(factors, sizes, keep, supplied=None):
    remaining = set(sizes)-set(keep)
    if supplied is not None:
        if not isinstance(supplied, list) or len(supplied) != len(remaining) or set(supplied) != remaining:
            raise ValueError('elimination_order must list every nonretained variable exactly once')
        return list(supplied)
    scopes = [set(f['scope']) for f in factors]
    order = []
    while remaining:
        def score(v):
            neighbors = set().union(*(s for s in scopes if v in s))
            return _product(sizes[w] for w in neighbors), len(neighbors), str(v)
        v = min(remaining, key=score)
        selected = [s for s in scopes if v in s]
        merged = set().union(*selected)-{v}
        scopes = [s for s in scopes if v not in s]+[merged]
        order.append(v)
        remaining.remove(v)
    return order


def _contract(factors, sizes, keep, options, budget, zero, one):
    factors = [dict(scope=tuple(f['scope']), table=list(f['table'])) for f in factors]
    # Isolated variables contribute their domain cardinality when summed out.
    touched = set().union(*(set(f['scope']) for f in factors)) if factors else set()
    for variable in sizes:
        if variable not in touched:
            factors.append({'scope': (variable,), 'table': [one]*sizes[variable]})
    order = _elimination_order(factors, sizes, keep, options.get('elimination_order'))
    # Preflight the complete dense table schedule before native arithmetic.
    scopes = [set(f['scope']) for f in factors]
    predicted = 0
    for variable in order:
        selected = [s for s in scopes if variable in s]
        union = set().union(*selected)
        count = _product(sizes[v] for v in union)
        predicted += count*(len(selected)+1)
        if count > options['max_intermediate_entries'] or predicted > options['max_factor_work']:
            raise CapacityError('Elimination schedule exceeds declared finite-factor admission')
        scopes = [s for s in scopes if variable not in s]+[union-{variable}]
    final_count = _product(sizes[v] for v in keep)
    if final_count > options['max_output_rows']:
        raise CapacityError('Retained factor table exceeds max_output_rows')
    for variable in order:
        selected = [f for f in factors if variable in f['scope']]
        factors = [f for f in factors if variable not in f['scope']]
        union = set().union(*(set(f['scope']) for f in selected))
        output_scope = tuple(v for v in sizes if v in union and v != variable)
        assignments = _product(sizes[v] for v in union)
        budget.charge(assignments*(len(selected)+1), assignments)
        descriptors = [(f, _strides(f['scope'], sizes)) for f in selected]
        table = []
        for state in itertools.product(*(range(sizes[v]) for v in output_scope)):
            assigned = dict(zip(output_scope, state))
            total = zero
            for value in range(sizes[variable]):
                assigned[variable] = value
                term = one
                for factor, strides in descriptors:
                    index = sum(assigned[v]*strides[v] for v in factor['scope'])
                    term = term*factor['table'][index]
                total = total+term
            table.append(total)
        factors.append({'scope': output_scope, 'table': table})
    budget.charge(final_count*max(1, len(factors)), final_count)
    descriptors = [(f, _strides(f['scope'], sizes)) for f in factors]
    table = []
    for state in itertools.product(*(range(sizes[v]) for v in keep)):
        assigned = dict(zip(keep, state))
        value = one
        for factor, strides in descriptors:
            value = value*factor['table'][sum(assigned[v]*strides[v] for v in factor['scope'])]
        table.append(value)
    return table, order


def _elimination_solve(source, ports, options, budget):
    bound = source['energy_bound_B']
    if 2*bound > options['max_energy_span']:
        raise CapacityError('Shifted exact energy polynomial exceeds max_energy_span')
    def monomial(power):
        return fmpz_poly([0]*power+[1])
    factors = []
    for v, h in enumerate(source['fields']):
        factors.append({'scope': (v,), 'table': [monomial(abs(h)+h), monomial(abs(h)-h)]})
    for u, v, j in source['edges']:
        factors.append({'scope': (u, v), 'table': [monomial(abs(j)-j), monomial(abs(j)+j),
                                                  monomial(abs(j)+j), monomial(abs(j)-j)]})
    table, order = _contract(factors, dict.fromkeys(range(source['N']), 2), ports,
                             options, budget, fmpz_poly([]), fmpz_poly([1]))
    if sum(len(poly) for poly in table) > options['max_output_rows']:
        raise CapacityError('Exact polynomial output exceeds max_output_rows')
    result = {}
    for state, poly in zip(itertools.product(range(2), repeat=len(ports)), table):
        mask = sum(bit << i for i, bit in enumerate(state))
        result[mask] = {i-bound: poly[i] for i in range(len(poly)) if poly[i] != 0}
    return result, {'method': 'NATIVE_FLINT_POLYNOMIAL_VARIABLE_ELIMINATION',
                    'elimination_order': order, 'energy_shift': bound,
                    'polynomial_backend': 'FLINT fmpz_poly sum/product'}


def solve_cpu(source, ports=None, options=None):
    source = validate_source(source)
    options = options_checked(options)
    ports = check_ports(source, list(range(min(4, source['N']))) if ports is None else ports, options)
    groups = components(source)
    method = options['method']
    component_admitted = (max(map(len, groups)) <= options['max_component_size']
                          and sum(1 << len(g) for g in groups) <= options['max_assignments'])
    if method == 'auto':
        method = 'components' if component_admitted else 'variable_elimination'
    budget = Budget(options)
    if method == 'components':
        histograms, execution = _component_solve(source, ports, options, budget, groups)
    else:
        histograms, execution = _elimination_solve(source, ports, options, budget)
    answer = finalize_answer(source, ports, histograms)
    execution.update(backend='PROJECT_LOCAL_NATIVE_FLINT_CPU', elapsed_ns=time.perf_counter_ns()-budget.started,
                     recomputed=True, arithmetic_work_units=budget.work,
                     peak_factor_entries=budget.peak_entries, limits=options,
                     source_sha256=source['source_sha256'], retained_outcome_used=False)
    return {'status': 'EXACT', 'answer': answer, 'execution': execution}


def contract_exact(variables, factors, keep=None, options=None):
    options = options_checked(options)
    if not isinstance(variables, list) or not variables or len(variables) > 4096:
        raise ValueError('Supply 1..4096 explicit finite variables')
    sizes, domains = {}, {}
    for variable in variables:
        if not isinstance(variable, dict) or set(variable) != {'name', 'domain'}:
            raise ValueError('Each variable has exactly name and domain')
        name, domain = variable['name'], variable['domain']
        if not isinstance(name, str) or not name or name in sizes:
            raise ValueError('Variable names must be distinct nonempty strings')
        if not isinstance(domain, list) or not 1 <= len(domain) <= 256:
            raise ValueError('Each explicit finite domain needs 1..256 states')
        if any(type(v) not in (int, str) for v in domain) or len({(type(v).__name__, v) for v in domain}) != len(domain):
            raise ValueError('Finite domain labels must be distinct integer/string states')
        sizes[name], domains[name] = len(domain), domain
    keep = [] if keep is None else keep
    if not isinstance(keep, list) or len(set(keep)) != len(keep) or any(v not in sizes for v in keep):
        raise ValueError('keep must name distinct declared variables')
    if not isinstance(factors, list) or len(factors) > 10000:
        raise ValueError('Supply at most10000 explicit finite factors')
    normalized = []
    for factor in factors:
        if not isinstance(factor, dict) or set(factor) != {'scope', 'table'}:
            raise ValueError('Each factor has exactly scope and table')
        scope, table = factor['scope'], factor['table']
        if not isinstance(scope, list) or len(set(scope)) != len(scope) or any(v not in sizes for v in scope):
            raise ValueError('Factor scope must name distinct declared variables')
        required = _product(sizes[v] for v in scope)
        if required > options['max_intermediate_entries']:
            raise CapacityError('Input factor table exceeds max_intermediate_entries')
        if not isinstance(table, list) or len(table) != required:
            raise ValueError('Factor table shape differs from explicit domains')
        normalized.append({'scope': scope, 'table': [coefficient(v) for v in table]})
    budget = Budget(options)
    table, order = _contract(normalized, sizes, keep, options, budget, fmpz(0), fmpz(1))
    source = {'variables': variables, 'factors': [{'scope': f['scope'], 'table': [str(v) for v in f['table']]} for f in normalized], 'keep': keep}
    return {'status': 'EXACT', 'answer': {'schema': 'GEN3_EXACT_SIGNED_FACTOR_V1',
            'input_sha256': digest(source), 'variables': variables, 'keep': keep,
            'shape': [sizes[v] for v in keep], 'table': [str(v) for v in table],
            'table_order': 'row-major in keep order; last variable varies fastest',
            'total': str(sum(table, fmpz(0))), 'signed': any(v < 0 for f in normalized for v in f['table']),
            'meaning': 'Exact finite sum of products; no probability or physical interpretation is implied'},
            'execution': {'backend': 'PROJECT_LOCAL_NATIVE_FLINT_FMPZ', 'elapsed_ns': time.perf_counter_ns()-budget.started,
                          'elimination_order': order, 'arithmetic_work_units': budget.work,
                          'peak_factor_entries': budget.peak_entries, 'limits': options, 'recomputed': True}}


def readout_exact(answer, conditioning=None, moment_orders=None, energy_weights=None):
    if not isinstance(answer, dict) or answer.get('schema') != SCHEMA:
        raise ValueError('READOUT requires a canonical exact spin spectrum')
    body = {k: v for k, v in answer.items() if k != 'spectrum_sha256'}
    if answer.get('spectrum_sha256') != digest(body):
        raise ValueError('Spectrum content hash differs')
    conditioning = {} if conditioning is None else conditioning
    moment_orders = [0, 1, 2] if moment_orders is None else moment_orders
    if not isinstance(conditioning, dict):
        raise ValueError('conditioning maps retained local vertex IDs to spins +/-1')
    selected = {}
    for raw, spin in conditioning.items():
        if not isinstance(raw, str) or not raw.isascii() or not raw.isdigit() or str(int(raw)) != raw:
            raise ValueError('Conditioning vertex keys must be canonical nonnegative integer strings')
        vertex = int(raw)
        if vertex not in answer['ports'] or type(spin) is not int or spin not in (-1, 1):
            raise ValueError('Conditioning requires retained ports and spins +/-1')
        selected[answer['ports'].index(vertex)] = spin
    if (not isinstance(moment_orders, list) or len(set(moment_orders)) != len(moment_orders)
            or any(type(k) is not int or not 0 <= k <= 16 for k in moment_orders)):
        raise ValueError('Distinct moment orders in0..16 required')
    weights = {}
    if energy_weights is not None:
        if not isinstance(energy_weights, list):
            raise ValueError('energy_weights must be an explicit list; omitted energies receive weight zero')
        for row in energy_weights:
            if not isinstance(row, dict) or set(row) != {'energy', 'weight'}:
                raise ValueError('Each energy weight has exactly energy and weight')
            energy = integer(row['energy'], 'energy')
            if energy in weights:
                raise ValueError('Duplicate energy weight')
            weights[energy] = rational(row['weight'])
    histogram = defaultdict(fmpz)
    for row in answer['port_rows']:
        if all(row['state'][position] == spin for position, spin in selected.items()):
            for energy, count in row['dos']:
                histogram[energy] += coefficient(count)
    weighted = {energy: fmpq(count)*(weights.get(energy, fmpq(0)) if energy_weights is not None else fmpq(1))
                for energy, count in histogram.items()}
    mass = sum(weighted.values(), fmpq(0))
    raw_moments = {str(k): sum((weight*fmpz(energy)**k for energy, weight in weighted.items()), fmpq(0)) for k in moment_orders}
    return {'schema': 'GEN3_EXACT_SPIN_READOUT_V1', 'source_sha256': answer['source_sha256'],
            'spectrum_sha256': answer['spectrum_sha256'], 'conditioning': conditioning,
            'unweighted_configuration_count': str(sum(histogram.values(), fmpz(0))),
            'weighted_mass': str(mass), 'raw_moments': {k: str(v) for k, v in raw_moments.items()},
            'normalized_moments': {k: str(v/mass) for k, v in raw_moments.items()} if mass != 0 else None,
            'normalization_defined': mass != 0,
            'weights_are_nonnegative': all(v >= 0 for v in weighted.values()),
            'weight_convention': 'Explicit rational energy weights; absent listed energies have zero weight' if energy_weights is not None else 'Uniform configuration counting',
            'weighted_dos': [[energy, str(value)] for energy, value in sorted(weighted.items()) if value != 0],
            'interpretation': 'Exact user-declared finite readout; signed weights are not probability weights'}


def _fields(payload, required, optional=()):
    if not isinstance(payload, dict) or not set(required) <= set(payload) or set(payload)-set(required)-set(optional):
        raise ValueError('Supply exactly the documented operation fields')


def _publish(runtime, operation, value, binding, dependencies=()):
    publication = runtime.execute('GEN3_RESULT_PUBLISH', {'kind': 'mathematical_result', 'value': value,
        'source_binding': dict(capability='GEN3_EXACT_SPIN_TOOLS_V1', operation=operation, **binding),
        'provenance': {'origin': 'SOURCE_BOUND_NATIVE_OPERATION',
                       'implementation': 'spin_exact.py', 'operation': operation},
        'dependencies': sorted(set(dependencies))})
    runtime.execute('GEN3_CHECKPOINT', {})
    return publication['result_ref']


def _get(runtime, reference):
    return runtime.execute('GEN3_RESULT_GET', {'result_ref': reference, 'kind': 'mathematical_result'})['value']


def canonical_retained(value):
    """Adopt an exact catalog spectrum for readout without claiming a new solve."""
    if value.get('answer', {}).get('schema') == SCHEMA:
        return value['answer']
    if not isinstance(value.get('source'), dict) or not isinstance(value.get('spectrum'), dict):
        raise ValueError('Retained object has neither a canonical solve nor a source-bound catalog spectrum')
    source = validate_source(value['source'])
    spectrum = value['spectrum']
    if spectrum.get('source_sha256', source['source_sha256']) != source['source_sha256']:
        raise ValueError('Retained catalog source and spectrum identities differ')
    def histogram(rows):
        if not isinstance(rows, list):
            raise ValueError('Retained exact density of states must be an explicit list')
        result = {}
        for row in rows:
            if isinstance(row, dict):
                energy, count = row['energy'], row['count']
            else:
                energy, count = row
            energy = integer(energy, 'energy')
            if energy in result:
                raise ValueError('Retained density of states repeats an energy')
            result[energy] = coefficient(count)
        return result
    closed = spectrum.get('closed_port_rows')
    if closed is None:
        ports, rows = [], {0: histogram(spectrum['scalar_dos'])}
    else:
        ports = spectrum.get('retained_ports')
        if ports is None:
            parent = spectrum.get('parent_port_vertices')
            if parent is None:
                raise ValueError('Retained port vertex identities are missing')
            ports = [source['parent_vertices'].index(v) for v in parent]
        if not isinstance(ports, list) or any(type(v) is not int for v in ports):
            raise ValueError('Retained port indices must be explicit local vertex indices')
        check_ports(source, ports, {'max_port_states': 256})
        rows = {mask: histogram(row) for mask, row in enumerate(closed)}
    answer = finalize_answer(source, ports, rows)
    original_scalar = [[e, str(n)] for e, n in sorted(histogram(spectrum['scalar_dos']).items()) if n != 0]
    if answer['scalar_dos'] != original_scalar:
        raise ArithmeticError('Retained scalar spectrum differs from its conditional rows')
    return answer


def dispatch(runtime, operation, payload):
    if operation == 'GEN3_SPIN_SOLVE':
        _fields(payload, ['source'], ['ports', 'backend', 'options', 'plan', 'previous_N', 'mode', 'result_ref', 'policy', 'search'])
        source = validate_source(payload['source'])
        ports = payload.get('ports', list(range(min(4, source['N']))))
        # GPU owns its further options. Shared port validity is checked here.
        if not isinstance(payload.get('options', {}), dict):
            raise ValueError('options must be a dictionary')
        port_limit = payload.get('options', {}).get('max_port_states', 256)
        if integer(port_limit, 'max_port_states') < 1:
            raise ValueError('max_port_states must be positive')
        ports = check_ports(source, ports, {'max_port_states': port_limit})
        mode = payload.get('mode', 'fresh')
        if mode == 'recover':
            if 'result_ref' not in payload:
                raise ValueError('Explicit recovery requires result_ref')
            old = _get(runtime, payload['result_ref'])
            if (old.get('operation') != operation or old.get('answer', {}).get('source_sha256') != source['source_sha256']
                    or old['answer'].get('ports') != ports):
                raise ValueError('Retained exact calculation differs from requested source or ports')
            return dict(old, result_ref=payload['result_ref'], recomputed=False,
                        recovery='EXPLICIT_EXACT_RESULT_REFERENCE')
        if mode != 'fresh' or 'result_ref' in payload:
            raise ValueError('Fresh solve cannot consume a retained outcome reference')
        backend = payload.get('backend', 'auto')
        options = payload.get('options', {})
        if not isinstance(options, dict):
            raise ValueError('options must be a dictionary')
        if backend == 'auto':
            groups = components(source)
            small = (max(map(len, groups)) <= options.get('max_component_size', 20)
                     and sum(1 << len(g) for g in groups) <= options.get('max_assignments', 2000000))
            visible = 0
            if not small:
                try:
                    import cupy as cp
                    visible = int(cp.cuda.runtime.getDeviceCount())
                except (ImportError, RuntimeError, OSError):
                    visible = 0
            backend = 'cpu' if small or visible == 0 else 'gpu'
        if backend not in ('cpu', 'gpu'):
            raise ValueError('backend must be auto, cpu or gpu')
        selection = None
        plan = payload.get('plan')
        if plan is None:
            selection = runtime.execute('GEN3_SPIN_SELECT', {'source': source, 'ports': ports,
                'previous_N': payload.get('previous_N', 96), 'policy': payload.get('policy', 'auto'),
                'search': payload.get('search', 'standard'), 'execution_backend': backend})
            plan = selection['plan']
        elif not isinstance(plan, dict) or plan.get('source_sha256', source['source_sha256']) != source['source_sha256'] or plan.get('ports', ports) != ports:
            raise ValueError('Supplied plan must match the exact source and requested ports')
        if backend == 'cpu':
            result = solve_cpu(source, ports, options)
        elif backend == 'gpu':
            try:
                from .spin_gpu import solve_gpu
            except ImportError:
                from spin_gpu import solve_gpu
            result = solve_gpu(source, plan, dict(options, ports=ports))
        if result.get('status') == 'CHECKPOINTED':
            return dict(result, source_sha256=source['source_sha256'], recomputed=True)
        if result.get('answer') is None:
            raise ArithmeticError('Solver returned no exact answer')
        value = dict(result, operation=operation, source=source, selection=selection)
        dependencies = [selection[key] for key in ('retained_plan_ref', 'previous_ref') if selection and selection.get(key)]
        reference = _publish(runtime, operation, value, {'source_sha256': source['source_sha256'], 'ports': ports}, dependencies)
        return dict(value, result_ref=reference, recomputed=True)
    if operation == 'GEN3_SPIN_CONTRACT':
        _fields(payload, ['variables', 'factors', 'source_binding'], ['keep', 'options'])
        if not isinstance(payload['source_binding'], dict) or not payload['source_binding']:
            raise ValueError('Explicit domain/source binding required for finite-factor contraction')
        result = contract_exact(payload['variables'], payload['factors'], payload.get('keep'), payload.get('options'))
        value = dict(result, operation=operation, declared_source_binding=payload['source_binding'])
        reference = _publish(runtime, operation, value, {'input_sha256': result['answer']['input_sha256'],
                                                        'declared_source_binding': payload['source_binding']})
        return dict(value, result_ref=reference, recomputed=True)
    if operation == 'GEN3_SPIN_READOUT':
        _fields(payload, ['result_ref'], ['conditioning', 'moment_orders', 'energy_weights'])
        original = _get(runtime, payload['result_ref'])
        started = time.perf_counter_ns()
        canonical = canonical_retained(original)
        answer = readout_exact(canonical, payload.get('conditioning'), payload.get('moment_orders'), payload.get('energy_weights'))
        value = {'operation': operation, 'answer': answer, 'input_result_ref': payload['result_ref'],
                 'execution': {'backend': 'PROJECT_LOCAL_NATIVE_FLINT_FMPQ',
                               'elapsed_ns': time.perf_counter_ns()-started, 'spectrum_recomputed': False}}
        reference = _publish(runtime, operation, value, {'source_sha256': answer['source_sha256'],
                'readout_request_sha256': digest(payload)}, [payload['result_ref']])
        return dict(value, result_ref=reference, recomputed=True, spectrum_recomputed=False)
    raise ValueError('Unknown exact spin operation')


class SpinExactAdapter:
    """Successor seam for source-bound project qualification before installation."""
    def __init__(self, base):
        self.base = base

    def close(self):
        return self.base.close()

    def execute(self, operation, payload):
        return dispatch(self.base, operation, payload) if operation in OPS else self.base.execute(operation, payload)
