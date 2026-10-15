"""Export, reopen and slice a single-plate A1 project for the V5 base."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from generate_universo_base_v5 import BLUE, ROOT, FOLDER, PREFIX

TARGET = ROOT/'downloads'/f'{PREFIX}-A1-PLA.3mf'


def package():
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip', 'w', ZIP_DEFLATED) as z:
        for p in sorted(FOLDER.iterdir()):
            if p.is_file():
                z.write(p, f'{FOLDER.name}/{p.name}')
        for p in (TARGET, ROOT/'downloads'/f'{PREFIX}.stl'):
            z.write(p, p.name)
        for p in sorted((ROOT/'designs').glob(PREFIX+'-*.png')):
            z.write(p, 'imagens/'+p.name)


def finish(source):
    blobs, settings, plates = read_project(source)
    assert len(plates) == 1 and len(plates[0]['items']) == 1
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    cfg['filament_colour'] = [BLUE]
    cfg['filament_multi_colour'] = [BLUE]
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    out = Image.new('RGB', (600, 660), 'white')
    d = ImageDraw.Draw(out)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
    d.rectangle((40, 80, 560, 600), fill='#eceff2', outline='#939ba3', width=2)
    for item in plates[0]['items']:
        for triangle in item['mesh'].triangles:
            d.polygon([(40+x*520/256, 600-y*520/256) for x, y, z in triangle], fill=BLUE)
    d.text((25, 20), 'Base V5 reforcada - compativel V4', font=font, fill=BLUE)
    d.text((25, 618), 'Um prato / apenas azul / A1 0,4 mm', font=font, fill=BLUE)
    for name, size in [('plate_1.png', out.size), ('plate_1_small.png', (128, 141))]:
        stream = io.BytesIO()
        out.resize(size).save(stream, format='PNG')
        blobs['Metadata/'+name] = stream.getvalue()
    node = settings.find('plate/metadata[@key="thumbnail_file"]')
    if node is None:
        node = ET.SubElement(settings.find('plate'), 'metadata', key='thumbnail_file')
    node.set('value', 'Metadata/plate_1.png')
    blobs['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items():
            z.writestr(name, data)
    out.save(ROOT/'designs'/f'{PREFIX}-prato.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir', type=Path, default=Path('/tmp/universo-base-v5-bambu'))
    parser.add_argument('--bambu-bin', type=Path, default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles', type=Path, default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    args = parser.parse_args()
    w = args.work_dir
    w.mkdir(exist_ok=True)
    machine = flatten_profile(args.profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(args.profiles, 'process', '0.20mm Standard @BBL A1')
    process.update({
        'name': 'Universo base V5 reforcada - A1 PLA 0.20', 'from': 'User',
        'wall_loops': '4', 'sparse_infill_density': '25%', 'sparse_infill_pattern': 'gyroid',
        'layer_height': '0.2', 'initial_layer_print_height': '0.2',
        'top_shell_layers': '5', 'bottom_shell_layers': '4', 'top_shell_thickness': '1',
        'top_surface_pattern': 'monotonicline', 'wall_generator': 'arachne',
        'outer_wall_speed': ['70'], 'inner_wall_speed': ['150'], 'top_surface_speed': ['40'],
        'initial_layer_speed': ['30'], 'initial_layer_infill_speed': ['50'],
        'brim_type': 'outer_only', 'brim_width': '3', 'brim_object_gap': '0.15',
        'elefant_foot_compensation': '0.1', 'enable_prime_tower': '0',
        'interface_shells': '1', 'flush_into_infill': '0', 'flush_into_support': '0',
        'enable_support': ['1'], 'support_type': ['normal(auto)'],
        'support_style': ['snug'], 'support_on_build_plate_only': ['1'],
        'support_threshold_angle': ['30'], 'support_top_z_distance': ['0.2'],
        'support_bottom_z_distance': ['0.2'], 'curr_bed_type': 'Textured PEI Plate',
    })
    filament = flatten_profile(args.profiles, 'filament', 'Generic PLA @BBL A1')
    filament.update({'name': 'Universo PLA azul - base V5', 'from': 'User',
                     'filament_colour': [BLUE], 'filament_max_volumetric_speed': ['8']})
    for name, cfg in [('machine', machine), ('process', process), ('filament', filament)]:
        (w/f'{name}.json').write_text(json.dumps(cfg))
    plan = {'plates': [{'plate_name': 'Base V5 reforcada - usar com costas V4',
                       'need_arrange': True, 'objects': [{
                           'path': str(ROOT/'downloads'/f'{PREFIX}.stl'),
                           'count': 1, 'filaments': [1]}]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common = ['--datadir', str(w/'bambu-user'), '--debug', '2']
    run_cli(args.bambu_bin, common+[
        '--load-settings', str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments', str(w/'filament.json'), '--load-assemble-list', str(w/'assembly.json'),
        '--orient', '0', '--arrange', '1', '--outputdir', str(w),
        '--export-3mf', 'native.3mf'], w/'export.log')
    finish(w/'native.3mf')
    blobs, settings, plates = read_project(TARGET)
    config = json.loads(blobs['Metadata/project_settings.config'])
    assert config['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert config['filament_colour'] == [BLUE]
    assert config['wall_loops'] == '4' and config['sparse_infill_density'] == '25%'
    actual = plates[0]['items'][0]['mesh']
    reference = trimesh.load(ROOT/'downloads'/f'{PREFIX}.stl', force='mesh')
    assert actual.is_watertight and actual.is_winding_consistent
    assert abs(actual.volume-reference.volume) < 0.1
    np.testing.assert_allclose(sorted(actual.extents), sorted(reference.extents), atol=.01)
    assert actual.bounds[0].min() > -.001 and np.all(actual.bounds[1, :2] < 253)
    run_cli(args.bambu_bin, common+['--info', '--outputdir', str(w/'reopen'), str(TARGET)], w/'reopen.log')
    run_cli(args.bambu_bin, common+['--slice', '0', '--orient', '0', '--arrange', '0',
        '--outputdir', str(w/'slicing'), '--export-3mf', 'validation-only.3mf', str(TARGET)], w/'slice.log')
    result = json.loads((w/'slicing/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    plate = result['sliced_plates'][0]
    assert not plate.get('warning_message') and plate['filament_change_times'] == 0
    with ZipFile(w/'slicing/validation-only.3mf') as z:
        code = z.read('Metadata/plate_1.gcode').decode()
    markers = re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)', code)
    assert markers[-1] == ('50', '50')
    assert '; FEATURE: Support' in code
    report = {
        'printer': 'Bambu Lab A1 0.4 nozzle', 'native_cli_version': config['version'],
        'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        'editable_unsliced_project': True, 'plate_count': 1, 'filament_colour': BLUE,
        'filament_changes': 0, 'layers_mm': .2, 'layers': 50,
        'wall_loops': 4, 'sparse_infill': '25% gyroid',
        'native_export_exit': 0, 'native_reopen_exit': 0, 'native_slice_exit': 0,
        'warnings': [], 'estimated_seconds': plate['total_predication'],
        'estimated_grams': sum(f['total_used_g'] for f in plate['filaments']),
        'physical_strength_tested': False, 'physical_cable_fit_tested': False,
        'filaments': plate['filaments'],
    }
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    package()
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
