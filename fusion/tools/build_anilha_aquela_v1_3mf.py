"""Create and verify the editable three-plate Bambu A1 project for Aquelá."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import trimesh

from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from generate_anilha_aquela_v1 import BROWN, CHARCOAL, CREAM, COLORS, FOLDER, GREEN, PREFIX, ROOT

TARGET = ROOT / 'downloads' / f'{PREFIX}-A1-AMS-3-pratos.3mf'


def main(args):
    work = args.work_dir
    work.mkdir(parents=True, exist_ok=True)
    libs = Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu')
    os.environ['LD_LIBRARY_PATH'] = str(libs) + ':' + str(args.bambu_bin.parent)
    profiles = args.bambu_bin.parent.parent / 'resources/profiles/BBL'
    geometry = json.loads((FOLDER / 'geometry.json').read_text())
    parts = {part['key']: part for part in geometry['parts']}

    machine = flatten_profile(profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(profiles, 'process', '0.12mm Fine @BBL A1')
    process.update({
        'name': 'Anilha Aquelá V1 A1 0.12', 'from': 'User',
        'layer_height': '0.12', 'initial_layer_print_height': '0.20',
        'wall_loops': '3', 'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
        'top_shell_layers': '6', 'top_shell_thickness': '0.72',
        'bottom_shell_layers': '5', 'bottom_shell_thickness': '0.60',
        'top_surface_pattern': 'monotonicline', 'wall_generator': 'arachne',
        'outer_wall_speed': ['30'], 'inner_wall_speed': ['50'],
        'internal_solid_infill_speed': ['45'], 'top_surface_speed': ['20'],
        'small_perimeter_speed': ['50%'], 'bridge_speed': ['20'],
        'overhang_1_4_speed': ['30'], 'overhang_2_4_speed': ['25'],
        'overhang_3_4_speed': ['15'], 'overhang_4_4_speed': ['10'],
        'default_acceleration': ['1000'], 'outer_wall_acceleration': ['800'],
        'top_surface_acceleration': ['800'], 'initial_layer_speed': ['20'],
        'initial_layer_infill_speed': ['25'], 'enable_support': ['0'],
        'brim_type': 'no_brim', 'brim_width': '0', 'elefant_foot_compensation': '0.1',
        'enable_prime_tower': '1', 'prime_tower_width': '25',
        'flush_into_infill': '0', 'flush_into_support': '0', 'seam_position': 'back',
        'ironing_type': 'no ironing', 'resolution': '0.008',
        'curr_bed_type': 'Textured PEI Plate',
    })
    settings = []
    for kind, value in [('machine', machine), ('process', process)]:
        target = work / f'{kind}.json'
        target.write_text(json.dumps(value, indent=2) + '\n')
        settings.append(str(target))

    filament_files = []
    for index, (colour, label) in enumerate(zip(COLORS, ['castanho', 'verde', 'carvão', 'creme']), 1):
        filament = flatten_profile(profiles, 'filament', 'Generic PLA @BBL A1')
        filament.update({'name': f'PLA {label} — Anilha Aquelá', 'from': 'User',
                         'filament_colour': [colour], 'filament_max_volumetric_speed': ['8'],
                         'filament_scarf_seam_type': ['none']})
        target = work / f'filament-{index}.json'
        target.write_text(json.dumps(filament, indent=2) + '\n')
        filament_files.append(str(target))

    # Slots are intentionally reused: brown is both the ring and the plaque;
    # charcoal is both the backing and its top wolf area.  The project therefore
    # stays within one four-slot A1 AMS.
    def item(key, slot, assembly=None, overrides=None):
        result = {'path': str(ROOT / 'downloads' / parts[key]['file']), 'count': 1, 'filaments': [slot]}
        if assembly is not None:
            result['assemble_index'] = [assembly]
        if overrides:
            result['print_params'] = overrides
        return result

    plan = {'plates': [
        {'plate_name': '01 Anilha castanha — 25 × 18 mm livres', 'need_arrange': True,
         'objects': [item('anilha-castanha', 1, overrides={'wall_loops': '4', 'sparse_infill_density': '30%'})]},
        {'plate_name': '02 Folhas verdes — uma peça', 'need_arrange': True,
         'objects': [item('folhas-verdes', 2)]},
        {'plate_name': '03 Lobo e tabuleta Aquelá — AMS 3 cores', 'need_arrange': True,
         'objects': [item('lobo-carvao', 3, 1), item('lobo-castanho', 1, 1),
                     item('lobo-cinzento', 3, 1), item('lobo-creme', 4, 1)]},
    ]}
    (work / 'assembly.json').write_text(json.dumps(plan, indent=2) + '\n')
    common = ['--datadir', str(work / 'user'), '--debug', '2']
    run_cli(args.bambu_bin, common + [
        '--load-settings', ';'.join(settings), '--load-filaments', ';'.join(filament_files),
        '--load-assemble-list', str(work / 'assembly.json'), '--allow-multicolor-oneplate',
        '--orient', '0', '--arrange', '1', '--outputdir', str(work), '--export-3mf', 'native.3mf'
    ], work / 'export.log')
    native = annotate(work / 'native.3mf', TARGET, COLORS, PREFIX)
    assert [len(plate) for plate in native] == [1, 1, 4]
    for plate in native:
        for _, _, mesh in plate:
            assert mesh.is_watertight and mesh.is_winding_consistent
            assert mesh.bounds[0, :2].min() > 0 and mesh.bounds[1, :2].max() < 253
            assert mesh.bounds[0, 2] >= -.002

    blobs, settings_xml, plates = read_project(TARGET)
    project = json.loads(blobs['Metadata/project_settings.config'])
    assert project['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert project['layer_height'] == '0.12'
    assert len(plates) == 3 and [len(plate['items']) for plate in plates] == [1, 1, 1]
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as archive:
        for name, data in blobs.items():
            archive.writestr(name, data)
    assert ZipFile(TARGET).testzip() is None

    run_cli(args.bambu_bin, common + ['--info', '--outputdir', str(work / 'reopen'), str(TARGET)], work / 'reopen.log')
    run_cli(args.bambu_bin, common + [
        '--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(work / 'slice'),
        '--export-3mf', 'validation.3mf', str(TARGET)
    ], work / 'slice.log')
    result = json.loads((work / 'slice' / 'result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 3
    reports = []
    with ZipFile(work / 'slice' / 'validation.3mf') as archive:
        for index, plate in enumerate(result['sliced_plates']):
            code = archive.read(f'Metadata/plate_{index + 1}.gcode').decode()
            assert not plate.get('warning_message'), plate.get('warning_message')
            assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
            assert '; seam_position = back' in code
            reports.append({
                'plate': index + 1, 'name': plan['plates'][index]['plate_name'],
                'estimated_seconds': plate['total_predication'],
                'estimated_grams_including_flush_and_tower': sum(f['total_used_g'] for f in plate['filaments']),
                'filament_changes': plate['filament_change_times'], 'warnings': plate.get('warning_message'),
                'gcode_sha256': hashlib.sha256(code.encode()).hexdigest(),
            })
    report = {
        'project': TARGET.name, 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        'printer': project['printer_settings_id'], 'bambu_version': '02.09.01.70',
        'native_export_exit': 0, 'native_reopen_exit': 0, 'native_slice_exit': 0,
        'geometry_watertight': True, 'plate_object_counts': [1, 1, 1],
        'layer_height_mm': .12, 'first_layer_height_mm': .20, 'brim': False,
        'supports': False, 'seam_position': 'back', 'plates': reports,
        'total_seconds': sum(row['estimated_seconds'] for row in reports),
        'total_grams': sum(row['estimated_grams_including_flush_and_tower'] for row in reports),
        'physical_print_tested': False, 'physical_fit_tested': False,
    }
    (FOLDER / 'bambu-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
