"""Publish completed spin source normalization; never rerun a spin solver."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sys.path.insert(0, str(ROOT))
from SAM_PROJECT.session import DomainSession
from CURRENT_REVISION.engines.SLC.gen3.spin_catalog import metadata, validate_source
from CURRENT_REVISION.engines.SLC.gen3.spin_planning import digest as graph_digest
from CURRENT_REVISION.engines.SLC.gen3.retained import digest

BASE = Path('SLC/SAM_LANGUAGE/SAM_LANGUAGE_CONTACT_NATIVE_SUCCESSOR_DESIGN')
N105 = BASE / 'SLC_N105_P9G0_RESTORATION_TIMING_DIAGNOSTIC_V1'
RING = Path('SLC/18_SAM_NATIVE_QC/SLCX028_EXACT_N96_N120_BOUNDARY_TRANSFER_RING_SCALING')
RING_RESULT = Path('SLC/18_SAM_NATIVE_QC/SLCX028A_IMPLEMENTATION_CORRECTED_N96_N120_BOUNDARY_TRANSFER_RING_SCALING/release')
ENERGY = 'E=-sum(J*s_u*s_v)-sum(h*s_u); spin bit 0=-1,1=+1'


def read(path):
    return json.loads((ROOT / path).read_text())


def custody(path):
    p = ROOT / path
    return dict(path=str(path), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def save(name, value):
    (P / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def exact_metadata(value):
    """Losslessly tag archived timing floats for the exact native object store."""
    if isinstance(value, float):
        return {'float64_hex': value.hex()}
    if isinstance(value, dict):
        return {k: exact_metadata(v) for k, v in value.items()}
    if isinstance(value, list):
        return [exact_metadata(v) for v in value]
    return value


def graph(instance, family):
    if instance.get('constant', 0) != 0:
        raise ValueError('Nonzero constant requires a separate energy-offset representation')
    for factor in instance.get('native_factors', []):
        if any(factor['energy_table']):
            raise ValueError('Nonzero native-factor energy cannot be dropped')
    edges = [[e['u'], e['v'], e['J']] if isinstance(e, dict) else e for e in instance['edges']]
    return validate_source(dict(N=instance['N'], fields=instance['fields'], edges=edges,
                                parent_vertices=list(range(instance['N'])), family=family,
                                parent_instance_sha256=instance.get('instance_semantic_sha256', instance.get('instance_sha256'))))


def packet_record(n):
    if n == 100:
        source_path = Path('CURRENT_REVISION/domains/ATOM3D/source/N100_INSTANCE.json')
        result_path = Path('CURRENT_REVISION/domains/ATOM3D/source/N100_REFERENCE.json')
        family = 'N100_P2_PACKET_PLUS_DEPTH_V1'
    else:
        source_path = N105 / 'N105_P9G0_RESTORED_INSTANCE.json'
        result_path = N105 / 'N105_P9G0_RESTORATION_RESULT.json'
        family = 'N105_P9G0_HISTORICAL_PACKET_RESTORATION_V1'
    original, result = read(source_path), read(result_path)
    exact = result if n == 100 else result['exact_n105']
    source = graph(original, family)
    bound, ports = exact['energy_bound'], exact['port_order']
    assert bound == source['energy_bound_B'] and ports == [0, 1, 60, 61]
    coefficients = exact['port_coefficients']
    assert len(coefficients) == 16 and all(len(row) == bound + 1 for row in coefficients)
    rows = [[[2*k-bound, str(c)] for k, c in enumerate(row) if c] for row in coefficients]
    scalar = [[r['energy'], str(r['count'])] for r in exact['scalar_dos']]
    closure = Counter()
    for row in rows:
        assert all(int(c) > 0 for _, c in row)
        assert sum(int(c) for _, c in row) == 1 << (n - len(ports))
        closure.update({e: int(c) for e, c in row})
    assert sorted(closure.items()) == [(e, int(c)) for e, c in scalar]
    assert sum(closure.values()) == 1 << n
    spectrum = dict(N=n, source_sha256=source['source_sha256'], energy_convention=ENERGY,
                    retained_ports=ports, parent_port_vertices=ports, port_roles=exact['port_roles'],
                    removed_glue_edges=[], local_energy_bound=bound,
                    open_y_operator=[[[k, str(c)] for k, c in enumerate(row) if c] for row in coefficients],
                    closed_port_rows=rows, scalar_dos=scalar, configuration_count=str(1 << n),
                    ground_energy=scalar[0][0], ground_degeneracy=scalar[0][1],
                    spectrum_sha256=graph_digest(scalar),
                    output_availability=dict(scalar_dos=True, closed_port_rows=True, open_y_operator=True),
                    checks=dict(count=True, port_counts=True, archived_scalar_closure=True,
                                source_energy_tables_zero=True, port_convention_preserved=True),
                    archived_port_tensor_sha256=exact['port_tensor_semantic_sha256'],
                    archived_scalar_dos_sha256=exact['scalar_dos_semantic_sha256'],
                    normalization='Existing coefficients at E=2*k-B; no new spin solve')
    components = exact.get('components', exact.get('component_records'))
    if components is None:
        components = result['components']
    return dict(source=source, spectrum=spectrum,
                plan=dict(route='EXACT_COMPONENT_CONDITIONAL_CONVOLUTION', executed=True,
                          planning_capability='RETAINED_COMPONENT_ROUTE_METADATA',
                          selected=dict(width=5), component_records=components,
                          timing=result['timing'], generic_cutset_plan=False),
                archived_instance=original,
                archived_identity=dict(instance_sha256=source['parent_instance_sha256'],
                                       result_sha256=result['result_sha256']),
                source_custody=[custody(source_path), custody(result_path)],
                source_group=family, method='RETAINED_EXACT_SOURCE_NORMALIZATION',
                result_scope='Completed packet source and all16 retained conditional rows; no new solve')


def ring_record():
    sp = RING / 'SLCX028_MOTIF_FAMILY_VAULT.json'
    rp = RING_RESULT / 'SLCX028A_N120_FINAL_SCALING_HOLDOUT_DOS.json'
    vault, result = read(sp), read(rp)
    original = next(x for x in vault['instances'] if x['N'] == 120)
    source = graph(original, 'SLCX028_N120_REPEATED_MOTIF_RING_V1')
    assert original['instance_sha256'] == result['instance_sha256']
    scalar = [[e, str(c)] for e, c in result['dos']]
    assert sum(int(c) for _, c in scalar) == 1 << 120
    spectrum = dict(N=120, source_sha256=source['source_sha256'], energy_convention=ENERGY,
                    scalar_dos=scalar, configuration_count=str(1 << 120),
                    ground_energy=scalar[0][0], ground_degeneracy=scalar[0][1],
                    spectrum_sha256=graph_digest(scalar), retained_ports=[], parent_port_vertices=[],
                    closed_port_rows=None, open_y_operator=None,
                    output_availability=dict(scalar_dos=True, closed_port_rows=False, open_y_operator=False),
                    port_availability_reason='Archived full ring release retains scalar DOS;16 transfer states are not full-source conditional rows',
                    archived_scalar_dos_sha256=result['dos_sha256'], checks=dict(archived_count=True))
    return dict(source=source, spectrum=spectrum, archived_instance=original,
                plan=dict(route='REPEATED_MOTIF_BOUNDARY_TRANSFER_RING', executed=True,
                          selected=dict(width=6), transfer_state_count=16, cell_count=10,
                          generic_cutset_plan=False),
                archived_identity=dict(instance_sha256=original['instance_sha256']),
                source_custody=[custody(sp), custody(rp)], source_group=source['family'],
                method='RETAINED_EXACT_SOURCE_NORMALIZATION',
                result_scope='Historical full ring scalar DOS, separate from current frontier and port tensor')


def registry_row(ref, value, default):
    source, spectrum = value['source'], value['spectrum']
    return dict(N=source['N'], family=source['family'], source_sha256=source['source_sha256'],
                result_ref=ref, default_for_N=default,
                output_availability=spectrum.get('output_availability', dict(scalar_dos=True, closed_port_rows=True, open_y_operator=True)),
                retained_port_count=len(spectrum.get('retained_ports', [])))


def main():
    P.mkdir(parents=True, exist_ok=True)
    meta = deepcopy(metadata())
    old_entries = deepcopy(meta['entries'])
    records = [exact_metadata(x) for x in (packet_record(100), packet_record(105), ring_record())]
    rows, roots, newrefs = [], [], []
    with DomainSession.start('MATTER_SEARCH', objective='Publish completed source-family spin records without recomputing historical spectra', output_root=P/'publication', receipt_storage='gzip') as session:
        print(session.announcement(), session.directory, flush=True)
        for n, ref in sorted(old_entries.items(), key=lambda x: int(x[0])):
            value = session.execute('GEN3_SPIN_ENTRY', dict(N=int(n)), purpose='Carry installed source identity and exact reference into additive family registry')
            assert value['result_ref'] == ref
            rows.append(registry_row(ref, value, True)); roots.append(ref)
        for value in records:
            source = value['source']
            pub = session.execute('GEN3_RESULT_PUBLISH', dict(kind='mathematical_result', value=value,
                                  source_binding=dict(campaign='GEN4_SPIN_TOOLS_INSTALL1', N=source['N'], family=source['family'], source_sha256=source['source_sha256']),
                                  provenance=dict(source_custody=value['source_custody'], method='Normalization and adoption of completed exact result; no spin rerun'), dependencies=[]),
                                  purpose='Publish archived complete source and exact available spectra with normalized port/energy convention')
            ref = pub['result_ref']; default = source['N'] in (100, 105)
            roots.append(ref); newrefs.append(ref); rows.append(registry_row(ref, value, default))
            if default: meta['entries'][str(source['N'])] = ref
            print('published', source['N'], source['family'], ref, flush=True)
        bundle = session.execute('GEN3_RESULT_EXPORT', dict(roots=sorted(set(roots))), purpose='Export all registry roots and dependency closure for GEN3/GEN4 installation')
        assert digest(bundle['bundle']) == bundle['sha256']
        with gzip.open(P/'BUNDLE.json.gz', 'wt') as output:
            json.dump(bundle, output, sort_keys=True, separators=(',', ':'))
        checkpoint = session.execute('GEN3_CHECKPOINT', {}, purpose='Retain complete source-registry publication for installed adoption')
        save('PUBLICATION.json', dict(session=str(session.directory), new_result_refs=newrefs,
                                     roots=len(roots), object_count=bundle['object_count'], checkpoint=checkpoint))
    assert all(meta['entries'][n] == ref for n, ref in old_entries.items())
    meta['sizes'] = sorted(map(int, meta['entries']))
    meta['source_registry'] = dict(path='spin_data/SOURCES.json', operation='GEN3_SPIN_SOURCE', source_count=len(rows), identity='family plus canonical source_sha256')
    registry = dict(schema='GEN3_GEN4_SPIN_SOURCE_REGISTRY_V1', sources=sorted(rows, key=lambda r:(r['N'], not r['default_for_N'], r['family'])),
                    source_count=len(rows), default_size_count=len(meta['entries']),
                    selection='N alone selects default; additional selectors identify exact family/hash; ambiguous requests reject',
                    source_identity='Canonical validate_source graph hash; archived identities preserved separately')
    save('SOURCES.json', registry); save('CATALOG.json', meta)
    print(json.dumps(dict(source_count=len(rows), default_entries=len(meta['entries']), new_objects=len(newrefs), bundle_objects=bundle['object_count'])), flush=True)


if __name__ == '__main__':
    main()
