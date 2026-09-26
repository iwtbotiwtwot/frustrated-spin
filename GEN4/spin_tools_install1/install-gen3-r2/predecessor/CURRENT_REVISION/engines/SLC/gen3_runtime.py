"""SLC-GEN3-R4: one native learning and executing machine.

GEN2 operation names remain compatibility calls into this runtime. Acquired
support executes the actual forward path and stays with exact state, history,
log readouts and persistent knowledge in one authenticated checkpoint.
"""
from copy import deepcopy
from .gen2_runtime import (GEN2Runtime, CandidateGroupInput, FrozenSLCQ3RZModel,
    RankOutcome, SLCQ3RZError, SourceVisibleChoice, load_frozen_model)
from . import gen2
from .gen3 import VERSION, BUILD, GENERATION
from .gen3.machine import Machine, LearnedBlock
from .gen2.exact import canonical_bytes, digest
from threading import RLock

_FOUNDATION_LOCK = RLock()
_SHARED_FOUNDATION = None
_FOUNDATION_USERS = 0

if __package__.startswith('CURRENT_REVISION.'):
    from CURRENT_REVISION.runtime import current_generation
    __current_generation__ = current_generation()


class GEN3Runtime(GEN2Runtime):
    def __init__(self, model=None, *, cache_size=128, installed=False, store_root=None, seeds=True):
        import sys
        # Exact project operands can exceed Python's generic decimal conversion
        # threshold. Host memory/CPU admission supplies the execution bound.
        sys.set_int_max_str_digits(0)
        try:
            super().__init__(model, cache_size=cache_size, installed=installed)
            self.machine = Machine()
            if seeds:
                from .gen3.memory import load
                self.machine.import_relations(load('relations'), self.compile)
            if store_root is not None:
                self.configure_storage(store_root)
        except BaseException:
            if hasattr(self, '_stack'):
                self.close()
            raise

    def quality(self):
        # The retained foundation owns process-wide custody modules. Warm domain
        # consumers share that exact component instead of opening conflicting stacks.
        global _SHARED_FOUNDATION, _FOUNDATION_USERS
        self._active()
        with _FOUNDATION_LOCK:
            if self._quality is None:
                from CURRENT_REVISION.engines.SLC import slcq3_rz_current as module
                if _SHARED_FOUNDATION is None:
                    context = module.open_runtime(self.model)
                    context.__enter__()
                    _SHARED_FOUNDATION = context
                elif self.model is not None and self.model != _SHARED_FOUNDATION.model:
                    raise ValueError('Shared foundation model binding differs')
                self._quality = _SHARED_FOUNDATION
                self.quality_module = module
                _FOUNDATION_USERS += 1
            return self._quality

    def configure_storage(self, directory):
        self._active()
        self.machine.attach(directory)

    def compile(self, *args, **kwargs):
        source = super().compile(*args, **kwargs)
        self.machine.active_contract = source.contract.to_dict()
        return LearnedBlock(source, self.machine)

    def execute(self, operation, payload):
        self._active()
        if not isinstance(payload, dict):
            raise ValueError('R3 payload must be an object')
        machine = self.machine
        if operation.startswith('GEN3_SPIN_'):
            from .gen3.spin_catalog import dispatch
            result = dispatch(self, operation, payload)
            if machine.store is not None:
                machine.checkpoint()
            return result
        if operation == 'GEN3_EXCHANGE_MATTER_SPECTRUM':
            exchange = payload.get('data', {}).get('exchange', {})
            if isinstance(exchange, dict) and 'result_ref' in exchange and exchange.get('field'):
                raise ValueError('Matter composition requires a whole exchange-spectrum reference')
        if operation.startswith('GEN3_RESULT_'):
            from .gen3.retained import dispatch
            result = dispatch(self, operation, payload)
            if machine.store is not None:
                machine.checkpoint()
            return result
        if operation in ('GEN3_CAPABILITIES','GEN3_SIGNED_ENERGY','GEN3_COMMON_MINIMA','GEN3_TREE_FIT','GEN3_TREE_PREDICT','GEN3_TREE_EXPORT','GEN3_CONSTRUCTION_PLAN','GEN3_OPERATOR_OBSTRUCTION','GEN3_COMMUTING_LOG','GEN3_OPERATOR_EXPORT','GEN3_SPECTRAL_ADMIT','GEN3_LOG1P_ENCLOSURE','GEN3_SPECTRAL_LOG_PROFILE','GEN3_SPECTRAL_REFINE','GEN3_SIGNED_TRANSPORT_LOG','GEN3_SPECTRAL_EXPORT','GEN3_SOURCE_OPERATOR_WORD','GEN3_SOURCE_SUBSPACE','GEN3_NATIVE_PAIR_ROOTS','GEN3_BLOCK_SOURCE_RECURRENCE','GEN3_SOURCE_SPECTRAL_CREATION','GEN3_SOURCE_WORD_EXCHANGE','GEN3_SOURCE_TERMINAL_ACTION','GEN3_SOURCE_SPECTRAL_EXPORT','GEN3_OPERATOR_MODULE','GEN3_OPERATOR_PRODUCT','GEN3_LOCAL_EXCHANGE_OBSTRUCTION','GEN3_CONSTRUCTION_EVALUATE','GEN3_BETHE_EXPORT','GEN3_RATIONAL_PERMUTATION_R','GEN3_TRANSFER_MATRIX','GEN3_TRANSFER_LOG_DERIVATIVE','GEN3_NESTED_BETHE_QSYSTEM','GEN3_PERMUTATION_CHAIN_SPECTRUM','GEN3_PERMUTATION_FAMILY_DIAGNOSTIC','GEN3_INTEGRABLE_EXCHANGE_EXPORT','GEN3_EXCHANGE_MOMENTUM_CENSUS','GEN3_EXCHANGE_MOMENTUM_SECTOR','GEN3_PARAMETRIC_CHARPOLY','GEN3_EXACT_PENCIL_SPECTRUM','GEN3_OPERATOR_FAMILY_EQUIVALENCE','GEN3_SCHUR_WEIGHT_DECOMPOSITION','GEN3_INDUCED_LOCAL_OPERATOR','GEN3_UNIFORM_FIELD_COMPATIBILITY','GEN3_EXCHANGE_MATTER_SPECTRUM','GEN3_TRANSFER_CHARGES','GEN3_COMMUTING_CHARGE_REDUCTION','GEN3_HOOK_EXCHANGE_SPECTRUM','GEN3_FUSED_R','GEN3_INTERACTION_COMPATIBILITY','GEN3_MATHEMATICAL_EXPORT'):
            from .gen3.capabilities import Capabilities
            if not hasattr(self, '_capabilities'):
                self._capabilities = Capabilities(machine)
            result = self._capabilities.execute(operation, payload)
            if operation == 'GEN3_CAPABILITIES':
                from .gen3.spin_catalog import OPS as spin_ops
                result['operations'] = list(dict.fromkeys(result['operations'] + list(spin_ops)))
                from .gen3.retained import OPS as retained_ops
                result['operations'] = list(dict.fromkeys(result['operations'] + list(retained_ops)))
                result['retained_mathematics'] = dict(operations=list(retained_ops),
                    schema='SLC_MATHEMATICAL_OBJECT_V1', source_required=True,
                    persistence='SHARED_NATIVE_STORE', references_in_existing_operations=True)
            from .gen3.capabilities.mathematical import OPS as math_ops
            if operation in math_ops[:-1]:
                from .gen3.retained import capture
                capture(machine, operation, payload, result)
            if machine.store is not None:
                machine.checkpoint()
            return result
        if operation == 'GEN3_STATUS':
            if payload: raise ValueError('Status takes no payload fields')
            return machine.status()
        if operation == 'GEN3_CHECKPOINT':
            if payload: raise ValueError('Checkpoint uses the attached managed store')
            return machine.checkpoint()
        if operation == 'GEN3_REPLICATE':
            if payload: raise ValueError('Replication uses the configured T500 service')
            from .gen3.replication import replicate
            return replicate(machine)
        if operation == 'GEN3_READOUT':
            if set(payload) != {'account'}: raise ValueError('Readout needs an account identity')
            return machine.accounts[payload['account']].readout()
        if operation == 'GEN3_HISTORY_EXPORT':
            if set(payload) != {'account'}: raise ValueError('History export needs an account identity')
            return machine.accounts[payload['account']].history(machine.store)
        if operation.startswith('GEN3_MEMORY_'):
            from .gen3.memory import dispatch
            result = dispatch(machine, operation, payload)
        elif operation == 'GEN3_LOG_COMPOSE':
            if set(payload) != {'account','left','right'}:
                raise ValueError('Composition needs an unused account identity and two adjacent accounts')
            name=payload['account']
            if not isinstance(name,str) or not name or name in machine.accounts:
                raise ValueError('Composition needs an unused nonempty account identity')
            from .gen3.logs import LogAccount
            left,right=machine.accounts[payload['left']],machine.accounts[payload['right']]
            if machine.store is not None:
                machine.checkpoint()
            account=LogAccount.compose(left,right)
            machine.accounts[name]=account;machine.dirty['accounts'].add(name)
            machine.stats['log_chunk_compositions']+=1
            result=account.readout()
        elif operation in ('GEN3_LOG_OPEN', 'GEN3_LOG_IMPORT'):
            if set(payload) != {'account','quantity','source_binding','points','edges'}:
                raise ValueError('A source account needs its quantity, binding and ordered source history')
            result = machine.account(payload['account'], payload)
        elif operation == 'GEN3_LOG_APPEND':
            if set(payload) != {'account','points','edges'}: raise ValueError('Append only the new source suffix')
            result = machine.append(payload['account'], payload['points'], payload['edges'])
        elif operation == 'GEN3_IMPORT_RELATIONS':
            if set(payload) != {'package'}: raise ValueError('Supply the original sealed acquired package')
            result = machine.import_relations(payload['package'], self.compile)
        else:
            original_operation = operation
            if operation in ('GEN3_EXECUTE', 'GEN3_RUN'):
                if 'initial' not in payload and operation == 'GEN3_EXECUTE':
                    if machine.state is None:
                        raise ValueError('The first execution needs an explicit initial source state')
                    payload = {**payload, 'initial': machine.state['state']}
                    if 'contract' not in payload and 'rho' not in payload and 'blocks' not in payload:
                        payload['contract'] = machine.state['contract']
                operation = 'GEN2_RUN'
            before = set(machine.relations)
            before_stats = machine.stats.copy()
            machine.support = []
            # Source observation and its complete conditioned result are paired.
            # A remembered report is never injected in place of an actual input.
            observation = operation in ('GEN2_INVERSE_OPEN', 'GEN2_OBSERVATION_PLAN',
                'GEN2_OBSERVATION_APPLY', 'GEN2_OBSERVATION_POLICY_PLAN',
                'GEN2_OBSERVATION_POLICY_APPLY')
            key = digest({'operation': operation, 'payload': payload}) if observation else None
            try:
                if key is not None and key in machine.observations:
                    row = machine.observations[key]
                    if row['operation'] != operation or canonical_bytes(row['payload']) != canonical_bytes(payload):
                        raise ValueError('Observation support identity differs')
                    result = deepcopy(row['result'])
                    machine.stats['learned_observation_branches_executed'] += 1
                else:
                    result = super().execute(operation, payload)
                    if key is not None:
                        machine.observations[key] = {'operation': operation,
                            'payload': deepcopy(payload), 'result': deepcopy(result)}
                        machine.dirty['observations'].add(key)
                        machine.stats['observation_branches_acquired'] += 1
                if operation in ('GEN2_RUN', 'GEN2_MOTION_RESUME'):
                    result['r3'] = machine.record_run(result)
            except BaseException:
                for key in set(machine.relations) - before:
                    del machine.relations[key]; machine.new_relations.discard(key)
                machine.stats = before_stats
                machine.support = []
                raise
        if machine.store is not None:
            machine.checkpoint()
        return result

    def close(self):
        global _SHARED_FOUNDATION, _FOUNDATION_USERS
        if getattr(self, '_closed', False):
            return
        if hasattr(self, '_capabilities'):
            self._capabilities.close()
        if hasattr(self, 'machine'):
            self.machine.close()
        super().__exit__(None, None, None)
        with _FOUNDATION_LOCK:
            if self._quality is not None:
                _FOUNDATION_USERS -= 1
                self._quality = None
                if _FOUNDATION_USERS == 0:
                    _SHARED_FOUNDATION.__exit__(None, None, None)
                    _SHARED_FOUNDATION = None

    def __exit__(self, *args):
        self.close()


SLCQ3RZRuntime = GEN3Runtime


def open_runtime(model=None, *, cache_size=128, installed=None, store_root=None, seeds=True):
    if installed is None:
        installed = __package__.startswith('CURRENT_REVISION.')
    return GEN3Runtime(model, cache_size=cache_size, installed=installed, store_root=store_root, seeds=seeds)


def derive_r3_graph(query, candidate, *, model=None):
    with open_runtime(model) as runtime:
        return runtime.derive_r3_graph(query, candidate)


def score(query, candidate, *, model=None):
    with open_runtime(model) as runtime:
        return runtime.score(query, candidate)


def rank(query, candidates, *, model=None):
    with open_runtime(model) as runtime:
        return runtime.rank(query, candidates)
