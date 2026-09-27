import math, collections
from flint import fmpz_poly
from ..spin_exact import digest

def plan(c, fill):
    s = c['source']
    n = s['N']
    blocks = c['blocks']
    labels = {v: i for i, b in enumerate(blocks) for v in b}
    if not sorted((v for b in blocks for v in b)) == list(range(n)):
        raise ValueError('BAD_PARTITION')
    if not all((v in blocks[0] for v in c['ports'])):
        raise ValueError('PORTS_OUTSIDE_FIRST_PACKET')
    seen = set()
    for u, v, j in s['edges']:
        if not (0 <= u < v < n and (u, v) not in seen and (type(j) is int)):
            raise ValueError('Exact source/closure guard failed')
        seen.add((u, v))
    cross = sorted((e for e in s['edges'] if labels[e[0]] != labels[e[1]]))
    if not cross == sorted(([min(u, v), max(u, v), j] for u, v, j in c['bridges'])):
        raise ValueError('UNACCOUNTED_CROSS_EDGE')
    if c['bridges']:
        if not len(c['bridges']) == len(blocks) - 1:
            raise ValueError('Exact source/closure guard failed')
        if not all(([u, v] == [blocks[i][0], blocks[i + 1][0]] for i, (u, v, j) in enumerate(c['bridges']))):
            raise ValueError('Exact source/closure guard failed')
    bridges = [j - fill for u, v, j in c['bridges']]
    pieces = []
    for bi, b in enumerate(blocks):
        mp = {v: i for i, v in enumerate(b)}
        ports = [v for v in c['ports'] if v in mp]
        if c['bridges'] and b[0] not in ports:
            ports.append(b[0])
        edges = [[mp[u], mp[v], j - fill] for u, v, j in s['edges'] if u in mp and v in mp and (j != fill)]
        fields = [s['fields'][v] for v in b]
        bound = sum((abs(e[2]) for e in edges)) + sum(map(abs, fields))
        piece = dict(n=len(b), edges=edges, fields=fields, ports=[mp[v] for v in ports], bound=bound, global_ports=ports, gateway_index=ports.index(b[0]) if c['bridges'] else None)
        piece['table_key'] = digest({k: piece[k] for k in ['n', 'edges', 'fields', 'ports', 'bound']})
        pieces.append(piece)
    bound = sum((p['bound'] for p in pieces)) + sum(map(abs, bridges))
    return dict(N=n, fill=fill, ports=c['ports'], pieces=pieces, bridges=bridges, correction_bound=bound, identity='E=2*t-B-J0*((2*k-N)^2-N)/2; polynomial encodes k=number of positive spins and t=(correction_energy+B)/2', maximum_degree=(n + 1) * (bound + 1) - 1)

def cpu_local(p):
    """Independent Gray-code exact enumeration; GPU uses direct binary evaluation."""
    n = p['n']
    adj = [[] for _ in range(n)]
    for u, v, j in p['edges']:
        adj[u].append((v, j))
        adj[v].append((u, j))
    spins = [-1] * n
    energy = -sum((j for u, v, j in p['edges'])) + sum(p['fields'])
    port_index = {v: i for i, v in enumerate(p['ports'])}
    mask = 0
    k = 0
    rows = {}
    for step in range(1 << n):
        if not (energy + p['bound']) % 2 == 0:
            raise ValueError('Exact source/closure guard failed')
        key = (k, (energy + p['bound']) // 2)
        r = rows.setdefault(mask, {})
        r[key] = r.get(key, 0) + 1
        if step + 1 == 1 << n:
            break
        flip = (step + 1 & -(step + 1)).bit_length() - 1
        energy += 2 * spins[flip] * (p['fields'][flip] + sum((j * spins[v] for v, j in adj[flip])))
        k -= spins[flip]
        spins[flip] *= -1
        if flip in port_index:
            mask ^= 1 << port_index[flip]
    return rows

def encode(rows, n, bound, orientation):
    out = {}
    for state, row in rows.items():
        entries = {k * (bound + 1) + t if orientation == 'K_MAJOR' else t * (n + 1) + k: v for (k, t), v in row.items()}
        coeff = [0] * (max(entries) + 1)
        for index, count in entries.items():
            coeff[index] = count
        out[state] = fmpz_poly(coeff)
    return out
