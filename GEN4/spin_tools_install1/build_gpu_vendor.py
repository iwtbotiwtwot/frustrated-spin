"""Extract pinned arithmetic fragments into a portable, relative-import package."""
import ast
import hashlib
import json
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESTART = ROOT/'GEN4/frustrated_spin_focused_training1/restart'


def build():
    out = HERE/'vendor'
    out.mkdir(parents=True, exist_ok=True)
    records = {}
    archives = {}
    def read(archive, suffix):
        path = RESTART/archive
        archives[archive] = hashlib.sha256(path.read_bytes()).hexdigest()
        with tarfile.open(path) as tar:
            members = [m for m in tar.getmembers() if m.isfile() and m.name.endswith(suffix)]
            if len(members) != 1: raise ValueError((archive, suffix, len(members)))
            member = members[0]
            value = tar.extractfile(member).read()
        records[member.name] = {'archive': archive, 'sha256': hashlib.sha256(value).hexdigest()}
        return value.decode()
    def definitions(text, names):
        lines = text.splitlines()
        pieces = []
        for node in ast.parse(text).body:
            if getattr(node, 'name', None) in names:
                start = min([node.lineno]+[d.lineno for d in getattr(node, 'decorator_list', [])])
                pieces.append('\n'.join(lines[start-1:node.end_lineno]))
        if len(pieces) != len(names): raise ValueError('Missing pinned definition')
        return '\n\n'.join(pieces)+'\n'
    exact = read('exact-source.tar.gz', '/slcx023_exact_engine.py')
    roots = read('exact-source.tar.gz', '/slcx032_engine.py')
    code = '"""Unchanged retained exact arithmetic definitions; see MANIFEST.json."""\nfrom __future__ import annotations\nfrom dataclasses import dataclass\nfrom typing import Any, Mapping\nimport numpy as np\nPRIMITIVE_ROOT = 3\nclass SLCX032ArithmeticError(ValueError): pass\n\n'
    code += definitions(exact, {'_weighted_edges', '_Factor', '_root_power_table', '_initial_factors'})
    code += '\n'+definitions(roots, {'_zeta_points', '_project_indices'})
    (out/'exact_factors.py').write_text(code)
    (out/'util.py').write_text('import hashlib,json\ndef digest(v):\n    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(\",\",\":\")).encode()).hexdigest()\n')
    (out/'compat.py').write_text('from types import SimpleNamespace\nfrom . import exact_factors as exact\nfrom .util import digest\nretained=SimpleNamespace(_modules=lambda:(None,exact),_project_indices=exact._project_indices)\nengine=SimpleNamespace(retained_engine=retained,zeta_points=exact._zeta_points)\na=SimpleNamespace(n96_engine=engine,canonical_sha256=digest)\n')
    arithmetic = read('catalog-code.tar.gz', 'catalog-code/arithmetic.py')
    text = '"""Unchanged conditioning/index-cache definitions with installed-relative imports."""\nimport time\nfrom types import SimpleNamespace\nimport numpy as np\nfrom .util import digest\nfrom .compat import exact\n\n'
    text += definitions(arithmetic, {'templates', 'IndexCache'})
    (out/'arithmetic.py').write_text(text)
    (out/'catalog_gpu.py').write_text(read('catalog-code.tar.gz', 'catalog-code/catalog_gpu.py'))
    (out/'kernel.cu').write_text(read('catalog-code.tar.gz', 'catalog-code/kernel.cu'))
    fast = read('focused-code.tar.gz', 'spin-focused1/fast_readout.py')
    if fast.count('from planning import digest') != 1: raise ValueError('Readout import changed')
    fast=fast.replace('from planning import digest', 'from .util import digest')
    fast=fast.replace('(1,004,535,809-1)^2', '(1,224,736,769-1)^2')
    (out/'fast_readout.py').write_text(fast)
    (out/'__init__.py').write_text('"""Pinned exact spin CUDA/NTT arithmetic dependencies."""\n')
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name != 'MANIFEST.json'}
    manifest = {'schema': 'GEN3_SPIN_GPU_VENDOR_V1', 'archives': archives, 'source_members': records,
                'files': files, 'changes': ['AST extraction of unchanged named arithmetic definitions',
                'installed-relative import wiring and compatibility namespace',
                'readout documentation bound includes already-qualified fifth prime',
                'no frozen campaign startup or filesystem/environment paths']}
    (out/'MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'vendor': str(out), 'files': len(files), 'manifest_sha256': hashlib.sha256((out/'MANIFEST.json').read_bytes()).hexdigest()}))


if __name__ == '__main__': build()
