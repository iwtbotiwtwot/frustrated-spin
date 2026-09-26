"""Read-only transport and retained N300 evidence verification; no new solves."""
from pathlib import Path
import csv, gzip, hashlib, json, statistics

ROOT = Path(__file__).resolve().parent

def load(path):
    return json.loads(path.read_text())

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def main():
    manifest = load(ROOT/'provenance/PUBLIC_MANIFEST.json')
    for row in manifest['files']:
        p = ROOT/row['path']
        assert p.is_file() and p.stat().st_size == row['bytes'], row['path']
        assert sha(p) == row['sha256'], row['path']
    p = ROOT/'GEN4/frustrated_spin_n300_courtroom1'
    frozen = load(p/'FROZEN_MANIFEST.json')
    for name, expected in frozen.items():
        assert sha(p/name) == expected, name
    seal = load(p/'PRECOMMIT_SEAL.json')
    assert sha(p/'FROZEN_MANIFEST.json') == seal['manifest_sha256']
    assert sha(p/'PRECOMMIT.json') == seal['precommit_sha256']
    assert sha(p/'PROTOCOL.md') == seal['protocol_sha256']
    witness = load(p/'WITNESS.json')
    assert sha(p/'PRECOMMIT.tar.gz') == witness['precommit_archive_sha256']
    previous = None
    events = []
    for line in (p/'EVENTS.jsonl').read_text().splitlines():
        row = json.loads(line)
        claimed = row.pop('hash')
        assert row['previous_hash'] == previous and digest(row) == claimed
        previous = claimed
        events.append(row)
    assert previous == load(p/'EVENT_HEAD.json')['hash']
    first = next(x for x in events if x['event']=='FIRST_N300_SOLVE_ABOUT_TO_EXECUTE')
    assert seal['sealed_utc'] < witness['received_utc'] < first['utc']
    families = ('packet','signed_packet','signed_packet_chain')
    scores = load(p/'SCORECARD.json')
    rows = list(csv.DictReader((p/'TIMINGS.csv').open()))
    for family in families:
        with gzip.open(p/'artifacts'/f'{family}_WARM.json.gz','rt') as f:
            warm = json.load(f)
        with gzip.open(p/'artifacts'/f'{family}_INDEPENDENT_VE.json.gz','rt') as f:
            independent = json.load(f)['answer']
        assert warm == independent, family
        assert int(warm['configuration_count']) == 2**300
        trials = [r for r in rows if r['family']==family and r['method']=='PACKET_WARM']
        assert len(trials)==31
        values = [int(r['duration_ns'])/1e6 for r in trials]
        assert statistics.median(values)==scores[family]['median_ms']
        assert sum(v<25 for v in values)==scores[family]['trials_below_25ms']
    controls = load(p/'WRONG_CONTROLS.json')['controls']
    assert len(controls)==6 and all(c['rejected'] for c in controls.values())
    atlas = ROOT/'GEN4/frustrated_spin_learning1/canonical'
    assert len(list(atlas.glob('N*.json')))==120
    for n in range(1,121):
        assert load(atlas/f'N{n:03d}.json')['N']==n
    packet = ROOT/'GEN4/frustrated_spin_packet_catalog1'
    for family in families:
        for n in range(1,121):
            assert (packet/'sources'/f'{family}_N{n:03d}.json').is_file()
            assert (packet/'results'/f'{family}_N{n:03d}.json.gz').is_file()
    print(json.dumps(dict(status='PASS',public_files=len(manifest['files']),
        frozen_N300_files=len(frozen),event_chain=len(events),
        independent_full_N300_answers=3,wrong_controls=6,
        canonical_sources=120,packet_sources=360,new_calculations=0),indent=2))

if __name__ == '__main__':
    main()
