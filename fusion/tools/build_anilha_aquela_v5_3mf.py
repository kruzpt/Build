"""Build and validate the revised V5 wolf front in native Bambu format."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from generate_anilha_aquela_v5 import ROOT, FOLDER, PREFIX, BLACK, GRAY, BROWN, WHITE, GREEN


def build(args, accessory):
    kind = 'acessorios' if accessory else 'lobo'
    work = args.work_dir/kind
    work.mkdir(parents=True, exist_ok=True)
    profiles = args.bambu_bin.parent.parent/'resources/profiles/BBL'
    geometry = json.loads((FOLDER/'geometry.json').read_text())
    parts = {p['key']: p for p in geometry['parts']}
    machine = flatten_profile(profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(profiles, 'process', '0.12mm Fine @BBL A1')
    process.update({
        'name': f'Aquelá V5 {kind} A1 0.12', 'from': 'User',
        'layer_height': '0.12', 'initial_layer_print_height': '0.20',
        'wall_loops': '3', 'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
        'top_shell_layers': '6', 'top_shell_thickness': '0.72',
        'bottom_shell_layers': '5', 'bottom_shell_thickness': '0.60',
        'top_surface_pattern': 'monotonicline', 'wall_generator': 'arachne',
        'outer_wall_speed': ['25'], 'inner_wall_speed': ['45'],
        'internal_solid_infill_speed': ['40'], 'top_surface_speed': ['18'],
        'small_perimeter_speed': ['50%'], 'bridge_speed': ['20'],
        'overhang_1_4_speed': ['25'], 'overhang_2_4_speed': ['25'],
        'overhang_3_4_speed': ['15'], 'overhang_4_4_speed': ['10'],
        'default_acceleration': ['1000'], 'outer_wall_acceleration': ['800'],
        'top_surface_acceleration': ['600'], 'initial_layer_speed': ['20'],
        'initial_layer_infill_speed': ['25'], 'enable_support': ['0'],
        'brim_type': 'no_brim', 'brim_width': '0', 'elefant_foot_compensation': '0.1',
        'enable_prime_tower': '0' if accessory else '1', 'prime_tower_width': '25',
        'prime_tower_brim_width': '0', 'prime_tower_extra_rib_length': '0',
        'flush_into_infill': '0', 'flush_into_support': '0', 'flush_into_objects': '0',
        'interface_shells': '1', 'reduce_crossing_wall': '1', 'seam_position': 'back',
        'ironing_type': 'no ironing', 'resolution': '0.008',
        'curr_bed_type': 'Textured PEI Plate',
    })
    setting_files = []
    for label, value in [('machine', machine), ('process', process)]:
        path = work/f'{label}.json'; path.write_text(json.dumps(value))
        setting_files.append(str(path))
    colors = [BROWN, GREEN] if accessory else [BLACK, GRAY, BROWN, WHITE]
    names = ['Castanho', 'Verde'] if accessory else ['Preto', 'Cinzento', 'Castanho', 'Branco']
    filament_files = []
    for i, (color, label) in enumerate(zip(colors, names), 1):
        filament = flatten_profile(profiles, 'filament', 'Generic PLA @BBL A1')
        filament.update({'name': f'Generic PLA {label} @BBL A1 0.4', 'from': 'User',
                         'filament_colour': [color], 'filament_max_volumetric_speed': ['8'],
                         'filament_scarf_seam_type': ['none']})
        path = work/f'filament-{i}.json'; path.write_text(json.dumps(filament))
        filament_files.append(str(path))
    def item(key, color, assembly=None, overrides=None):
        result = {'path': str(ROOT/'downloads'/parts[key]['file']), 'count': 1, 'filaments': [color]}
        if assembly: result['assemble_index'] = [assembly]
        if overrides: result['print_params'] = overrides
        return result
    if accessory:
        keys = ['anilha-castanha', 'folhas-verdes']
        plan = {'plates': [
            {'plate_name': '01 Anilha castanha - passagem 25 x 18 mm', 'need_arrange': True,
             'objects': [item(keys[0], 1, overrides={'wall_loops': '4', 'sparse_infill_density': '30%'})]},
            {'plate_name': '02 Folhas verdes - peca unica para colar', 'need_arrange': True,
             'objects': [item(keys[1], 2)]}]}
        name = f'{PREFIX}-ACESSORIOS-A1-04-2-pratos.3mf'
    else:
        keys = ['lobo-preto', 'lobo-cinzento', 'lobo-castanho', 'lobo-branco']
        plan = {'plates': [{'plate_name': 'Aquela V5 - lobo e tabuleta - 4 cores', 'need_arrange': True,
                           'objects': [item(key, i+1, 1) for i, key in enumerate(keys)]}]}
        name = f'{PREFIX}-LOBO-A1-04-AMS-4-cores.3mf'
    path = work/'assembly.json'; path.write_text(json.dumps(plan, indent=2))
    common = ['--datadir', str(work/'user'), '--debug', '2']
    run_cli(args.bambu_bin, common+[
        '--load-settings', ';'.join(setting_files), '--load-filaments', ';'.join(filament_files),
        '--load-assemble-list', str(path), '--allow-multicolor-oneplate',
        '--orient', '0', '--arrange', '1', '--outputdir', str(work), '--export-3mf', 'native.3mf'
    ], work/'export.log')
    target = ROOT/'downloads'/name
    native = annotate(work/'native.3mf', target, colors, PREFIX+'-'+kind)
    blobs, settings, plates = read_project(target)
    # The front now starts in brown; do not prime black before layer one.
    for obj in settings.findall('object'):
        if len(obj.findall('part'))==4:
            meta=obj.find("metadata[@key='extruder']")
            if meta is None:meta=ET.SubElement(obj,'metadata',key='extruder')
            meta.set('value','3')
            obj.find("metadata[@key='name']").set('value','Aquelá V5 — nome sem contorno preto')
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as archive:
        for member,data in blobs.items():archive.writestr(member,data)
    project = json.loads(blobs['Metadata/project_settings.config'])
    assert all(project[k]=='0' for k in ('flush_into_infill','flush_into_objects','flush_into_support'))
    assert float(project['flush_multiplier'][0])>=1
    assert float(project['flush_volumes_matrix'][3])>=587

    assert project['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert project['layer_height'] == '0.12' and project['brim_type'] == 'no_brim'
    assert project['seam_position'] == 'back'
    assert [len(p['items']) for p in plates] == ([1, 1] if accessory else [1])
    # Match native meshes to the source geometry, including their actual colors.
    remaining = [(col, mesh) for plate in native for _, col, mesh in plate]
    for key in keys:
        ref = trimesh.load(ROOT/'downloads'/parts[key]['file'], force='mesh')
        matches = [(i, col, m) for i, (col, m) in enumerate(remaining)
                   if abs(m.volume-ref.volume) < .08 and
                   np.allclose(np.linalg.eigvalsh(m.moment_inertia), np.linalg.eigvalsh(ref.moment_inertia),
                               rtol=.0003, atol=.1)]
        assert len(matches) == 1, key
        i, col, mesh = matches[0]; remaining.pop(i)
        assert colors[col-1] == parts[key]['color']
        assert mesh.is_watertight and mesh.is_winding_consistent
        assert mesh.bounds[0, :2].min() > 0 and mesh.bounds[1, :2].max() < 253
        assert mesh.bounds[0, 2] >= -.002
    assert not remaining
    if not accessory:
        lo = np.min([m.bounds[0] for _, _, m in native[0]], axis=0)
        hi = np.max([m.bounds[1] for _, _, m in native[0]], axis=0)
        assert abs(lo[2]) < .002 and abs(hi[2]-4.88) < .002
        # Relative placements survive the 3MF assembly, not just individual volumes.
        assert np.allclose(sorted((hi-lo)[:2]), [geometry['front_dimensions_mm'][0], 55], atol=.2)
    with ZipFile(target) as archive: assert archive.testzip() is None
    run_cli(args.bambu_bin, common+['--info', '--outputdir', str(work/'reopen'), str(target)], work/'reopen.log')
    run_cli(args.bambu_bin, common+[
        '--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(work/'slice'),
        '--export-3mf', 'validation.3mf', str(target)
    ], work/'slice.log')
    result = json.loads((work/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == len(native)
    report = {'project': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'printer': project['printer_settings_id'], 'bambu_version': '02.09.01.70',
              'native_export_exit': 0, 'native_reopen_exit': 0, 'native_slice_exit': 0,
              'source_meshes_and_color_mapping_verified': True,
              'layer_height_mm': .12, 'first_layer_height_mm': .20, 'brim': False,
              'supports': False, 'seam_position': 'back', 'plates': [],
              'filament_profiles': 'Generic PLA starting points, not a new spool calibration',
              'physical_print_tested': False, 'physical_fit_tested': False}
    with ZipFile(work/'slice/validation.3mf') as archive:
        for i, plate in enumerate(result['sliced_plates']):
            code = archive.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert not plate.get('warning_message'), plate.get('warning_message')
            assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
            assert len(plate['filaments']) == (1 if accessory else 4)
            assert plate['filament_change_times'] == 0 if accessory else plate['filament_change_times'] > 0
            report['plates'].append({
                'plate': i+1, 'name': plan['plates'][i]['plate_name'],
                'estimated_seconds': plate['total_predication'],
                'estimated_main_grams': sum(f['main_used_g'] for f in plate['filaments']),
                'estimated_grams_including_flush_and_tower': sum(f['total_used_g'] for f in plate['filaments']),
                'filament_changes': plate['filament_change_times'], 'warnings': plate.get('warning_message'),
                'gcode_sha256': hashlib.sha256(code.encode()).hexdigest(),
            })
    (FOLDER/f'bambu-validation-{kind}.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    os.environ['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    build(args, False)
