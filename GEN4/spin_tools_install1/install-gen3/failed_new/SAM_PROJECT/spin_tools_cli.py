"""Portable DomainSession front end for installed exact spin tools."""
import argparse
import json
from pathlib import Path
import sys
from uuid import uuid4


def default_root():
    return next((p for p in Path(__file__).resolve().parents if (p/'CURRENT_REVISION').is_dir()), Path.cwd())


def globals_for(parser, suppress=False):
    default = argparse.SUPPRESS if suppress else None
    parser.add_argument('--root', type=Path, default=argparse.SUPPRESS if suppress else default_root())
    parser.add_argument('--session', type=Path, default=default)
    parser.add_argument('--output', type=Path, default=default)
    parser.add_argument('--full', action='store_true', default=argparse.SUPPRESS if suppress else False)


def selector(parser):
    parser.add_argument('--N', type=int)
    parser.add_argument('--family')
    parser.add_argument('--hash', dest='source_sha256')


def json_input(value):
    if value == '-':
        data = json.load(sys.stdin)
    elif value.lstrip().startswith('{'):
        data = json.loads(value)
    else:
        data = json.loads(Path(value).read_text())
    if not isinstance(data, dict):
        raise ValueError('JSON input must be an object')
    return data


def compact(value, depth=0):
    """Keep short results legible and replace bulk arrays with size metadata."""
    if isinstance(value, list):
        if len(value) > 20 or depth > 3:
            return {'items': len(value), 'full_result_retained': True}
        return [compact(x, depth+1) for x in value]
    if isinstance(value, dict):
        if depth > 4:
            return {'keys': list(value), 'full_result_retained': True}
        return {k: compact(v, depth+1) for k, v in value.items()}
    return value


def summary(operation, result):
    if operation == 'GEN3_SPIN_SOURCES':
        result_summary = {k: result[k] for k in ('source_count', 'default_size_count', 'selection') if k in result}
        families = {}
        for row in result['sources']:
            families.setdefault(row['family'], []).append(row['N'])
        result_summary['families'] = families
        return result_summary
    if operation == 'GEN3_SPIN_SOURCE':
        source, spectrum = result['source'], result['spectrum']
        return dict(N=source['N'], family=source['family'], source_sha256=source['source_sha256'],
                    result_ref=result['result_ref'], edges=len(source['edges']),
                    configuration_count=spectrum['configuration_count'], ground_energy=spectrum['ground_energy'],
                    ground_degeneracy=spectrum['ground_degeneracy'], occupied_bins=len(spectrum['scalar_dos']),
                    output_availability=result['source_identity']['output_availability'], recomputed=False)
    return compact(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    globals_for(parser)
    sub = parser.add_subparsers(dest='command', required=True)
    commands = {}
    for name in ('sources', 'source', 'select', 'solve', 'contract', 'readout', 'call'):
        commands[name] = sub.add_parser(name)
        globals_for(commands[name], True)
    selector(commands['source'])
    for name in ('select', 'solve'):
        q = commands[name]; selector(q)
        q.add_argument('graph', nargs='?', help='Explicit graph JSON file, inline object, or - for stdin')
        q.add_argument('--payload', help='Additional operation payload JSON file/object; fields pass through unchanged')
    commands['select'].add_argument('--policy', choices=['auto', 'structural', 'focused_pairwise'])
    for name in ('contract', 'readout'):
        commands[name].add_argument('payload', help='Operation payload JSON file, inline object, or - for stdin')
    commands['call'].add_argument('operation')
    commands['call'].add_argument('payload', help='Unmodified operation payload JSON file/object or -')
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.output and args.output.exists():
        parser.error('Output file already exists; choose a new path')
    sys.path.insert(0, str(args.root))
    from SAM_PROJECT.session import DomainSession, exact_json
    operation = args.operation if args.command == 'call' else 'GEN3_SPIN_' + args.command.upper()
    if args.command in ('contract', 'readout', 'call'):
        payload = json_input(args.payload)
    elif args.command == 'sources':
        payload = {}
    else:
        if getattr(args, 'graph', None) == '-' and getattr(args, 'payload', None) == '-':
            parser.error('Only one input can read stdin')
        payload = json_input(args.payload) if getattr(args, 'payload', None) else {}
        selected = {k: getattr(args, k) for k in ('N', 'family', 'source_sha256') if getattr(args, k) is not None}
        if getattr(args, 'graph', None):
            if selected:
                parser.error('Choose an explicit graph or a catalog source selector')
            payload['source'] = json_input(args.graph)
        for key, value in selected.items():
            if key in payload and payload[key] != value:
                parser.error('Conflicting selector field: ' + key)
            payload[key] = value
        if getattr(args, 'policy', None):
            payload['policy'] = args.policy
        if not payload:
            parser.error('Supply a graph, source selector, or operation payload')
    session = DomainSession(args.session) if args.session else DomainSession.start(
        'MATTER_SEARCH', objective='Use installed exact spin tools: ' + operation,
        output_root=args.root/'SAM_RUNTIME/SPIN_TOOLS', receipt_storage='gzip')
    with session:
        print(session.announcement(), file=sys.stderr)
        print('Session: ' + str(session.directory), file=sys.stderr)
        result = session.execute(operation, payload, purpose='Execute explicit spin-tool request with source-bound native receipts')
        full = dict(operation=operation, session=str(session.directory), result=result)
        destination = args.output or session.directory / ('SPIN_TOOL_RESULT_' + uuid4().hex + '.json')
        destination = destination.resolve(); destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x') as stream:
            json.dump(full, stream, indent=2, sort_keys=True, default=exact_json, allow_nan=False)
            stream.write('\n')
        if args.command in ('solve', 'contract', 'readout', 'select', 'call'):
            session.execute('GEN3_CHECKPOINT', {}, purpose='Retain spin-tool results for explicit session reuse')
        output = full if args.full else dict(operation=operation, session=str(session.directory),
                                            full_result_file=str(destination), result=summary(operation, result))
        print(json.dumps(output, indent=2, sort_keys=True, default=exact_json, allow_nan=False))


if __name__ == '__main__':
    main()
