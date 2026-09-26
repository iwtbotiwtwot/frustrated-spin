"""Qualify installed spin tools through DomainSession; no direct solver shortcut.

Run with the project's resource wrapper. Independent tiny reference arithmetic
is a source-bound qualification adapter; all production calls use the installed
runtime operations without substituting this campaign's implementation.
"""
import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys


class ReferenceAdapter:
    def __init__(self, base, binding):
        self.base, self.binding = base, binding

    def close(self):
        self.base.close()

    def execute(self, operation, payload):
        if operation != 'GEN4_SPIN_EXACT_QUALIFICATION_REFERENCE':
            return self.base.execute(operation, payload)
        if payload.get('source_binding') != self.binding:
            raise ValueError('Independent qualification source binding differs')
        from flint import fmpz
        from CURRENT_REVISION.engines.SLC.gen3.spin_exact import finalize_answer
        if payload['kind'] == 'spin_bruteforce':
            source, ports = payload['source'], payload['ports']
            if source['N'] > 10:
                raise ValueError('Independent qualification enumeration is limited to10 variables')
            rows = {mask: {} for mask in range(1 << len(ports))}
            for spins in itertools.product((-1, 1), repeat=source['N']):
                energy = -sum((fmpz(h)*spins[i] for i, h in enumerate(source['fields'])), fmpz(0))
                energy -= sum((fmpz(j)*spins[u]*spins[v] for u, v, j in source['edges']), fmpz(0))
                state = sum((1 if spins[v] == 1 else 0) << i for i, v in enumerate(ports))
                e = int(energy)
                rows[state][e] = rows[state].get(e, fmpz(0))+1
            return {'backend': 'INDEPENDENT_NATIVE_FLINT_DIRECT_ENUMERATION',
                    'answer': finalize_answer(source, ports, rows)}
        if payload['kind'] == 'chain_formula':
            n = payload['N']
            if type(n) is not int or not 2 <= n <= 100:
                raise ValueError('Invalid qualification chain size')
            choose = fmpz(1)
            rows = []
            for k in range(n):
                rows.append([2*k-(n-1), str(2*choose)])
                if k+1 < n:
                    choose = choose*(n-1-k)//(k+1)
            return {'backend': 'NATIVE_FLINT_INDEPENDENT_OPEN_CHAIN_BINOMIAL_FORMULA', 'scalar_dos': rows}
        if payload['kind'] == 'factor_bruteforce':
            variables, factors, keep = payload['variables'], payload['factors'], payload['keep']
            names = [v['name'] for v in variables]
            sizes = {v['name']: len(v['domain']) for v in variables}
            if sum(sizes.values()) > 30:
                raise ValueError('Reference factor source exceeds tiny qualification scope')
            output = {}
            for values in itertools.product(*(range(sizes[v]) for v in names)):
                state = dict(zip(names, values))
                value = fmpz(1)
                for factor in factors:
                    index = 0
                    for v in factor['scope']:
                        index = index*sizes[v]+state[v]
                    value *= fmpz(factor['table'][index])
                key = tuple(state[v] for v in keep)
                output[key] = output.get(key, fmpz(0))+value
            return {'backend': 'INDEPENDENT_NATIVE_FLINT_FULL_FACTOR_ENUMERATION',
                    'table': [str(output[state]) for state in itertools.product(*(range(sizes[v]) for v in keep))]}
        raise ValueError('Unknown independent qualification kind')


def graph(fields, edges, family):
    return {'N': len(fields), 'fields': fields, 'edges': edges,
            'parent_vertices': list(range(len(fields))), 'family': family,
            'parent_instance_sha256': None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--domain', default='MATTER_SEARCH')
    args = parser.parse_args()
    sys.path.insert(0, str(args.root.resolve()))
    from SAM_PROJECT.session import DomainSession
    import CURRENT_REVISION.engines.SLC.gen3.spin_exact as installed
    args.out.mkdir(parents=True, exist_ok=False)
    binding = {'campaign': 'GEN4_SPIN_TOOLS_EXACT_QUALIFICATION_V1',
               'qualification_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'installed_spin_exact_sha256': hashlib.sha256(Path(installed.__file__).read_bytes()).hexdigest(),
               'scope': 'Independent tiny native checks, installed production calls and checkpoint recovery'}
    checks, returned = {}, {}
    session = DomainSession.start(args.domain, objective='Qualify installed exact spin and signed finite-factor capabilities',
                                   output_root=args.out/'sessions', receipt_storage='gzip')
    session.consumer = ReferenceAdapter(session.consumer, binding)
    print(session.announcement(), str(session.directory), flush=True)

    def call(label, operation, payload):
        result = session.execute(operation, payload, purpose=label)
        returned[label] = result
        return result

    def reject(label, payload):
        try:
            call(label, 'GEN3_SPIN_SOLVE', payload)
        except ValueError as error:
            checks[label] = True
            returned[label] = {'expected_error': type(error).__name__, 'message': str(error)}
        else:
            checks[label] = False

    try:
        first = graph([1, -2, 0, 3, 0, -1], [[0,1,2],[1,2,-1],[0,2,3],[3,4,-2],[4,5,1]],
                      'QUALIFICATION_DISCONNECTED_SIGNED_FIELDS_V1')
        second = graph([-1,0,1,0,2,0,-2], [[i,i+1,1 if i%2 else -2] for i in range(6)]+[[0,6,3]],
                       'QUALIFICATION_CONNECTED_FRUSTRATED_CYCLE_V1')
        completed = []
        for i, (source, ports) in enumerate([(first, [5,0,2]), (second, [6,1])]):
            component = call('fresh_components_'+str(i), 'GEN3_SPIN_SOLVE',
                             {'source': source, 'ports': ports, 'backend': 'cpu', 'options': {'method': 'components'}})
            elimination = call('fresh_elimination_'+str(i), 'GEN3_SPIN_SOLVE',
                               {'source': source, 'ports': ports, 'backend': 'cpu', 'options': {'method': 'variable_elimination'}})
            reference = call('independent_spin_reference_'+str(i), 'GEN4_SPIN_EXACT_QUALIFICATION_REFERENCE',
                             {'kind': 'spin_bruteforce', 'source': component['source'], 'ports': ports, 'source_binding': binding})
            checks['complete_coefficients_agree_'+str(i)] = component['answer'] == elimination['answer'] == reference['answer']
            checks['fresh_receipts_'+str(i)] = component['recomputed'] and elimination['recomputed'] and not component['execution']['retained_outcome_used']
            completed.append(component)
        chain = graph([0]*30, [[i,i+1,1] for i in range(29)], 'QUALIFICATION_CONNECTED_CHAIN30_V1')
        chain_result = call('large_connected_chain_elimination', 'GEN3_SPIN_SOLVE',
                            {'source': chain, 'ports': [], 'backend': 'cpu', 'options': {'method': 'variable_elimination'}})
        chain_reference = call('independent_chain_formula', 'GEN4_SPIN_EXACT_QUALIFICATION_REFERENCE',
                               {'kind': 'chain_formula', 'N': 30, 'source_binding': binding})
        checks['connected_N30_exact_binomial_spectrum'] = chain_result['answer']['scalar_dos'] == chain_reference['scalar_dos']
        variables = [{'name': 'x', 'domain': [-1,1]}, {'name': 'y', 'domain': ['a','b','c']},
                     {'name': 'z', 'domain': [0,1]}]
        factors = [{'scope': ['x','y'], 'table': [1,-2,3,4,0,-1]},
                   {'scope': ['y','z'], 'table': [2,-1,1,3,-2,5]},
                   {'scope': ['z'], 'table': [1,-1]}]
        contracted = call('signed_nonbinary_contraction', 'GEN3_SPIN_CONTRACT',
                          {'variables': variables, 'factors': factors, 'keep': ['x'], 'source_binding': binding})
        factor_reference = call('independent_signed_factor_reference', 'GEN4_SPIN_EXACT_QUALIFICATION_REFERENCE',
                                {'kind': 'factor_bruteforce', 'variables': variables, 'factors': factors,
                                 'keep': ['x'], 'source_binding': binding})
        checks['signed_nonbinary_coefficients'] = contracted['answer']['table'] == factor_reference['table']
        cancelled = call('exact_signed_cancellation', 'GEN3_SPIN_CONTRACT',
                         {'variables': variables[:2], 'factors': [{'scope':['x'],'table':[1,-1]}], 'source_binding': binding})
        checks['signed_cancellation_with_isolated_ternary_variable'] = cancelled['answer']['table'] == ['0']
        scalar = call('empty_factor_isolated_domain', 'GEN3_SPIN_CONTRACT',
                      {'variables': variables[:2], 'factors': [], 'source_binding': binding})
        checks['isolated_domain_cardinality'] = scalar['answer']['table'] == ['6']
        selected = call('conditional_exact_readout', 'GEN3_SPIN_READOUT',
                        {'result_ref': completed[0]['result_ref'], 'conditioning': {'5':1}, 'moment_orders':[0,1,2,3]})
        checks['conditioned_count'] = selected['answer']['unweighted_configuration_count'] == '32'
        a, b = completed[0]['answer']['scalar_dos'][:2]
        rational_read = call('zero_mass_rational_readout', 'GEN3_SPIN_READOUT',
                             {'result_ref': completed[0]['result_ref'], 'moment_orders':[0,1],
                              'energy_weights': [{'energy':a[0],'weight':'1/'+a[1]},
                                                 {'energy':b[0],'weight':'-1/'+b[1]}]})
        checks['rational_cancellation_and_undefined_normalization'] = (
            rational_read['answer']['weighted_mass'] == '0'
            and rational_read['answer']['normalized_moments'] is None)
        reject('component_limit_rejected', {'source':first,'ports':[5,0,2],'backend':'cpu',
                                           'options':{'method':'components','max_component_size':2}})
        reject('factor_work_limit_rejected', {'source':first,'backend':'cpu',
                                             'options':{'method':'variable_elimination','max_factor_work':1}})
        malformed = deepcopy(first)
        malformed['edges'].append(deepcopy(malformed['edges'][0]))
        reject('duplicate_relation_rejected', {'source':malformed,'backend':'cpu'})
        changed = deepcopy(first)
        changed['fields'][0] = 2
        reject('wrong_source_recovery_rejected', {'source':changed,'ports':[5,0,2],'mode':'recover',
                                                'result_ref':completed[0]['result_ref']})
        session.execute('GEN3_CHECKPOINT', {}, purpose='Persist fresh exact spectra and readout dependency closure')
        directory = session.directory
    finally:
        session.close()
    with DomainSession(directory) as recovered:
        print(recovered.announcement(), str(recovered.directory), flush=True)
        saved = recovered.execute('GEN3_SPIN_SOLVE', {'source':completed[0]['source'], 'ports':[5,0,2],
                                  'mode':'recover','result_ref':completed[0]['result_ref']},
                                  purpose='Explicit source-matched exact result recovery without a fresh solve')
        checks['checkpoint_recovery'] = saved['answer'] == completed[0]['answer'] and saved['recomputed'] is False
        readback = recovered.execute('GEN3_RESULT_GET', {'result_ref':rational_read['result_ref'], 'kind':'mathematical_result'},
                                     purpose='Recover exact rational readout and its declared result dependency')
        checks['readout_dependency_recovery'] = readback['value']['answer'] == rational_read['answer']
        returned['recovered_solve'] = saved
        returned['recovered_readout'] = readback
    status = {'status':'PASS' if all(checks.values()) else 'FAIL', 'checks':checks, 'check_count':len(checks),
              'session':str(directory), 'domain':args.domain, 'source_binding':binding,
              'installed_module':str(Path(installed.__file__).resolve()),
              'scope':'Installed production operations; reference arithmetic executed separately through DomainSession'}
    (args.out/'RETURNED.json').write_text(json.dumps(returned, indent=2)+'\n')
    (args.out/'QUALIFICATION.json').write_text(json.dumps(status, indent=2)+'\n')
    print(json.dumps(status, indent=2))
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])


if __name__ == '__main__':
    main()
