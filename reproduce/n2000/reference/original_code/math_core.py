import collections, math, sys, hashlib, json
from pathlib import Path
sys.path.insert(0, '/opt/gen4-n2000-joint1/runtime')
from CURRENT_REVISION.engines.SLC.gen3 import spin_joint as j, spin_exact as x
from CURRENT_REVISION.engines.SLC.gen3.spin_joint_core import baseline as b, optimized as o
from flint import ctx, fmpz_poly


def prepare(c, fill, orientation):
    pl = b.plan(c, fill); tables = {}
    # Independent local enumeration on each host; the opposite global encoding also
    # reverses component contraction. Small qualification checks against joint VE.
    for piece in pl['pieces']:
        if piece['table_key'] not in tables: tables[piece['table_key']] = local_table(piece)
    parts = o.components(pl, tables, orientation == 'K_MAJOR')
    step = 0
    for _, part in parts:
        for row in part['rows'].values():
            for k, t in row: step = math.gcd(step, t)
    step = math.gcd(step, pl['correction_bound']) or 1
    return pl, parts, step

def encode(row, n, bound, orientation, step):
    if bound % step or any(t % step for k, t in row): raise ArithmeticError('Nonintegral lattice')
    stride = bound // step + 1
    sparse = {(k * stride + t // step if orientation == 'K_MAJOR' else (t // step) * (n + 1) + k): v
              for (k, t), v in row.items()}
    coeff = [0] * (max(sparse) + 1)
    for index, count in sparse.items(): coeff[index] = count
    return fmpz_poly(coeff)

def scalar(pl, parts, orientation, step):
    counts = collections.Counter(key for key, part in parts[1:]); by_key = dict(parts)
    return o.balanced([encode(by_key[key]['rows'][0], pl['N'], pl['correction_bound'], orientation, step) ** count
                       for key, count in counts.items()])

def decode(poly, pl, orientation, step, state):
    n = pl['N']; bound = pl['correction_bound']; entries = []; marginal = collections.Counter(); dos = collections.Counter()
    for index, value in enumerate(poly):
        if not value: continue
        if orientation == 'K_MAJOR': k, t = divmod(index, bound // step + 1)
        else: t, k = divmod(index, n + 1)
        t *= step; count = int(value)
        if not (0 <= k <= n and 0 <= t <= bound and count > 0): raise ArithmeticError('Coefficient closure')
        ec = 2*t-bound; m = 2*k-n; e = ec-pl['fill']*((m*m-n)//2)
        entries.append((k, ec, count)); marginal[k] += count; dos[e] += count
    expected = {k+state.bit_count(): math.comb(n-len(pl['ports']), k) for k in range(n-len(pl['ports'])+1)}
    if dict(marginal) != expected: raise ArithmeticError('Conditional magnetization closure')
    entries.sort()
    return entries, dict(dos)

def row_digest(state, entries):
    h = hashlib.sha256(('['+str(state)+',[').encode())
    for i, entry in enumerate(entries):
        if i: h.update(b',')
        h.update(json.dumps(entry, separators=(',', ':')).encode())
    h.update(b']]')
    return h.hexdigest()


def local_table(piece):
    root=Path('/opt/gen4-n2000-joint1')
    catalog=root/'GPU_TABLES.json'
    if catalog.exists():
        d=json.loads(catalog.read_text()).get(piece['table_key'])
        if d is not None:
            path=root/d['file']
            with path.open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
            if actual!=d['sha256']: raise ValueError('GPU table custody mismatch')
            table=json.loads(path.read_text())
            if table['table_key']!=piece['table_key']:raise ValueError('GPU table source mismatch')
            return {state:{(k,t):count for k,t,count in row} for state,row in table['rows']}
    return b.cpu_local(piece)
