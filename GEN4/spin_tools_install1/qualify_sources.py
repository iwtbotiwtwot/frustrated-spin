"""Read-only source adoption and fresh-process checkpoint recovery checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--recover-session', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(); args.root = args.root.resolve(); args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True); sys.path.insert(0, str(args.root))
    from SAM_PROJECT.session import DomainSession
    if args.recover_session:
        expected = json.loads((args.out/'EXPECTED_RECOVERY.json').read_text())
        checks = {}
        with DomainSession(args.recover_session) as session:
            print(session.announcement(), file=sys.stderr)
            for key, row in expected.items():
                value = session.execute('GEN3_SPIN_SOURCE', row['selector'], purpose='Recover exact source-family record from the saved session in a new process')
                checks[key] = fingerprint(value) == row['fingerprint']
        result = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks, fresh_process=True)
        write(args.out/'RECOVERY.json', result); print(json.dumps(result))
        if not all(checks.values()): raise RuntimeError('Fresh-process recovery differs')
        return
    checks, recovery = {}, {}
    with DomainSession.start('MATTER_SEARCH', objective='Adopt all installed spin sources and recover exact source-family records', output_root=args.out/'sessions', receipt_storage='gzip') as session:
        print(session.announcement(), str(session.directory), file=sys.stderr)
        catalog = session.execute('GEN3_SPIN_SOURCES', {}, purpose='Read installed source-family registry')
        defaults = [r for r in catalog['sources'] if r['default_for_N']]
        checks['all_99_default_sizes'] = sorted(r['N'] for r in defaults) == list(range(1,97))+[100,105,120]
        checks['all_100_family_records'] = len(catalog['sources']) == 100
        for row in defaults:
            value = session.execute('GEN3_SPIN_SOURCE', dict(N=row['N']), purpose='Read completed exact source without recomputation')
            checks['source_'+str(row['N'])] = (value['result_ref']==row['result_ref'] and value['source']['source_sha256']==row['source_sha256'] and not value['recomputed'] and value['arithmetic_calls']==0)
            if row['N'] in (100,105,120):
                recovery[str(row['N'])] = dict(selector=dict(N=row['N']), fingerprint=fingerprint(value))
            if row['N'] in (100,105):
                legacy = session.execute('GEN3_SPIN_ENTRY', dict(N=row['N']), purpose='Check additive legacy entry retrieval for completed packet source')
                checks['legacy_entry_'+str(row['N'])] = legacy['result_ref']==row['result_ref'] and len(legacy['spectrum']['closed_port_rows'])==16
        ring = next(r for r in catalog['sources'] if r['N']==120 and not r['default_for_N'])
        ring_selector = dict(N=120, family=ring['family'])
        named = session.execute('GEN3_SPIN_SOURCE', ring_selector, purpose='Retrieve the separately named historical N120 ring')
        current = next(r for r in defaults if r['N']==120)
        checks['two_N120_families_distinct'] = ring['source_sha256'] != current['source_sha256'] and ring['result_ref'] != current['result_ref']
        checks['ring_scalar_availability_explicit'] = named['spectrum']['closed_port_rows'] is None and not ring['output_availability']['closed_port_rows']
        recovery['historical_ring'] = dict(selector=ring_selector, fingerprint=fingerprint(named))
        by_hash = session.execute('GEN3_SPIN_SOURCE', dict(source_sha256=ring['source_sha256']), purpose='Resolve exact source identity by canonical graph hash')
        checks['hash_selector'] = by_hash['result_ref']==ring['result_ref']
        wrong = next(r for r in defaults if r['N']==105)['source_sha256']
        controls = {'source_hash_mismatch':dict(N=100, source_sha256=wrong),
                    'ambiguous_family':dict(family=next(r for r in defaults if r['N']==1)['family'])}
        for name, payload in controls.items():
            try:
                session.execute('GEN3_SPIN_SOURCE', payload, purpose='Reject a mismatched or ambiguous source selector')
            except ValueError:
                checks[name] = True
            else:
                checks[name] = False
        checkpoint = session.execute('GEN3_CHECKPOINT', {}, purpose='Persist adopted source records before independent-process recovery')
        directory = session.directory
    write(args.out/'EXPECTED_RECOVERY.json', recovery)
    process = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--root', str(args.root), '--out', str(args.out), '--recover-session', str(directory)], cwd=args.root, capture_output=True, text=True)
    (args.out/'RECOVERY.stdout').write_text(process.stdout); (args.out/'RECOVERY.stderr').write_text(process.stderr)
    checks['fresh_process_recovery'] = process.returncode == 0
    result = dict(status='PASS' if all(checks.values()) else 'FAIL', check_count=len(checks), checks=checks, session=str(directory), checkpoint=checkpoint, scientific_spectra_recomputed=0)
    write(args.out/'RESULT.json', result)
    print(json.dumps(dict(status=result['status'], checks=len(checks), session=str(directory), result=str(args.out/'RESULT.json'))))
    if not all(checks.values()): raise RuntimeError('Source adoption checks failed')


if __name__ == '__main__':
    main()
