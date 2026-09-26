"""Read source-family identities and exact completed spin records."""
import json
from pathlib import Path
from . import retained

OPS = ('GEN3_SPIN_SOURCES', 'GEN3_SPIN_SOURCE')
HERE = Path(__file__).resolve().parent / 'spin_data'


def metadata():
    return json.loads((HERE / 'SOURCES.json').read_text())


def dispatch(runtime, operation, payload):
    meta = metadata()
    if operation == 'GEN3_SPIN_SOURCES':
        retained.fields(payload)
        return dict(**meta, recomputed=False, arithmetic_calls=0)
    if operation != 'GEN3_SPIN_SOURCE':
        raise ValueError('Unknown source registry operation')
    retained.fields(payload, (), ('N', 'family', 'source_sha256'))
    if not payload:
        raise ValueError('Select a source by N, family, or source_sha256')
    if 'N' in payload and (type(payload['N']) is not int or payload['N'] < 1):
        raise ValueError('N must be a positive integer')
    if 'family' in payload and (not isinstance(payload['family'], str) or not payload['family']):
        raise ValueError('family must be a nonempty source-family identifier')
    if 'source_sha256' in payload:
        retained.reference(payload['source_sha256'])
    rows = [r for r in meta['sources'] if all(r[k] == v for k, v in payload.items())]
    if set(payload) == {'N'}:
        rows = [r for r in rows if r['default_for_N']]
    if len(rows) != 1:
        raise ValueError('No matching source' if not rows else 'Source selector is ambiguous; add N or source_sha256')
    row = rows[0]
    obj = retained.get(runtime.machine, row['result_ref'], kind='mathematical_result')
    value = obj['value']
    if any(value['source'][k] != row[k] for k in ('N', 'family', 'source_sha256')):
        raise ValueError('Source registry identity differs from retained object')
    return dict(result_ref=row['result_ref'], **value, source_identity=row,
                recomputed=False, arithmetic_calls=0)
