"""Continue gyroid through the first two gold layers; retain six closing layers.

Revise the known-good V9 project in place within a new archive. Geometry,
orientation, materials and other process settings must remain unchanged.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_pintos_pla_3mf import read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from build_m7_gold_lines_v6 import put
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'essencial-compacto-v10-dourado-infill'
FOLDER = ROOT/'fusion/EssencialCompactoV10DouradoInfill'
SOURCE = ROOT/'downloads/essencial-compacto-v9-costura-traseira-A1-AMS-2-pratos.3mf'
TARGET = ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'


def props(node):
    return {p.get('key'): p.get('value') for p in node.findall('metadata')}


def preview(rows, bounds):
    sheet = Image.new('RGB', (1520, 1080), '#f5f7fa'); draw = ImageDraw.Draw(sheet)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    draw.text((35, 25), 'Base QR V10 · duas camadas douradas em infill + seis de fecho', font=font(30), fill='#17344a')
    draw.text((35, 75), 'Percursos reais do Bambu Studio · base completa · camada de 0,16 mm', font=font(24), fill='#455d70')
    examples = [(8.48, '1.ª dourada · Gyroid 15%'), (8.64, '2.ª dourada · Gyroid 15%'),
                (8.8, '3.ª dourada · fecho em ponte'), (9.6, '8.ª dourada · superfície final')]
    lo, hi = bounds[:, :2]
    scale = min(680/(hi[0]-lo[0]), 350/(hi[1]-lo[1]))
    for i, (height, title) in enumerate(examples):
        x0 = 35+(i % 2)*755; y0 = 145+(i//2)*440
        draw.text((x0, y0), f'{title} · Z {height:.2f}', font=font(24), fill='#17344a')
        center = np.array([x0+350, y0+225])
        for row in rows:
            if row['tool'] != 3 or abs(row['layer']-height) > .0001: continue
            pp = (np.array(row['points'])[:, :2]-(lo+hi)/2)*scale
            pp[:, 1] *= -1; pp += center
            feature = row['feature']
            color = '#326f9b' if feature == 'Sparse infill' else '#bb6d2f' if feature == 'Bridge' else '#a6812e' if feature in ('Internal solid infill', 'Top surface') else '#536d81'
            draw.line([tuple(p) for p in pp], fill=color, width=1)
    draw.text((35, 1030), 'Azul: infill · laranja: ponte · dourado: topo · cinzento: paredes', font=font(24), fill='#17344a')
    sheet.save(ROOT/'designs'/f'{PREFIX}-percursos.png')


def main(args):
    work = args.work_dir; work.mkdir(parents=True, exist_ok=True)
    FOLDER.mkdir(parents=True, exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    help_result = subprocess.run([str(args.bambu_bin), '--help'], capture_output=True, text=True, check=True)
    version = re.search(r'BambuStudio-([\d.]+)', help_result.stdout+help_result.stderr).group(1)
    source, settings, source_plates = read_project(SOURCE)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    v9_report = json.loads((ROOT/'fusion/EssencialCompactoV9CosturaTraseira/bambu-validation.json').read_text())
    assert source_hash == v9_report['sha256']
    cfg = json.loads(source['Metadata/project_settings.config'])
    assert cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert cfg['layer_height'] == '0.16' and cfg['seam_position'] == 'back'
    before = {p.get('id'): props(p) for o in settings.findall('object') for p in o.findall('part')}
    changed = []
    for obj in settings.findall('object'):
        assert props(obj)['seam_position'] == 'back'
        for part in obj.findall('part'):
            if props(part).get('extruder') == '3':
                assert props(part)['top_shell_layers'] == '6' and props(part)['top_shell_thickness'] == '0.96'
                for key in ('bottom_shell_layers', 'bottom_shell_thickness'): put(part, key, '0')
                changed.append(part.get('id'))
            after = props(part)
            delta = {k: [before[part.get('id')].get(k), v] for k, v in after.items() if before[part.get('id')].get(k) != v}
            assert set(delta) == ({'bottom_shell_layers', 'bottom_shell_thickness'} if after.get('extruder') == '3' else set())
    assert set(changed) == {'8', '11'}
    titles = ['01 BASE V10 - dourado 2 infill + 6 fecho', '02 AMOSTRA V10 - imprimir primeiro']
    for plate, title in zip(settings.findall('plate'), titles): put(plate, 'plater_name', title)
    blobs = dict(source)
    blobs['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as archive:
        for name, data in blobs.items(): archive.writestr(name, data)
    annotate(TARGET, TARGET, cfg['filament_colour'], PREFIX)
    actual, current_settings, current_plates = read_project(TARGET)
    assert [len(p['items']) for p in current_plates] == [1, 2]
    assert json.loads(actual['Metadata/project_settings.config']) == cfg
    assert all(actual[n] == data for n, data in source.items() if n.startswith('3D/'))
    native = plate_meshes(actual, current_settings)
    assert all(m.is_watertight and m.is_winding_consistent for plate in native for _, _, m in plate)
    with ZipFile(TARGET) as archive: assert archive.testzip() is None
    common = ['--datadir', str(work/'user'), '--debug', '2']
    run_cli(args.bambu_bin, common+['--info', '--outputdir', str(work/'reopen'), str(TARGET)], work/'reopen.log')
    run_cli(args.bambu_bin, common+['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(work/'slice'),
        '--export-3mf', 'validation.3mf', str(TARGET)], work/'slice.log')
    result = json.loads((work/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 2
    reports = []
    with ZipFile(work/'slice/validation.3mf') as archive:
        for i, plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message') and plate['filament_change_times'] == 1
            code = archive.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Brim' not in code and '; FEATURE: Support' not in code
            assert '; seam_position = back' in code
            rows = [r for r in paths(code) if r['feature'] != 'Prime tower']
            assert {r['tool'] for r in rows} == {2, 3}
            assert len({r['layer'] for r in rows}) == 60
            assert all(r['tool'] == 2 for r in rows if r['layer'] <= 8.32001)
            assert all(r['tool'] == 3 for r in rows if r['layer'] > 8.32001)
            gold = [r for r in rows if r['tool'] == 3]
            green_base = [r for r in rows if r['tool'] == 2 and r['layer'] > 4]
            assert not any(r['feature'] == 'Top surface' for r in green_base)
            layers = sorted({r['layer'] for r in gold})
            assert np.allclose(layers, np.arange(8.48, 9.601, .16))
            layer_report = []
            for j, height in enumerate(layers):
                layer_rows = [r for r in gold if abs(r['layer']-height) < .00001]
                features = {r['feature'] for r in layer_rows}
                if j < 2:
                    assert 'Sparse infill' in features
                    assert not features.intersection({'Internal solid infill', 'Top surface', 'Bottom surface', 'Bridge'})
                elif j == 2:
                    assert 'Bridge' in features and 'Sparse infill' not in features
                elif j < 7:
                    assert 'Internal solid infill' in features and 'Sparse infill' not in features
                else:
                    assert 'Top surface' in features and 'Sparse infill' not in features and 'Inner wall' not in features
                extrusion = defaultdict(float)
                for r in layer_rows: extrusion[r['feature']] += r['extrusion_mm']
                layer_report.append({'gold_layer': j+1, 'z_mm': height, 'features': sorted(features),
                                     'extrusion_mm_by_feature': dict(extrusion)})
            assert max(r['speed'] for r in gold if r['feature'] in ('Outer wall', 'Inner wall', 'Internal solid infill', 'Gap infill')) <= 25.001
            assert max(r['speed'] for r in gold if r['feature'] == 'Top surface') <= 20.001
            assert max(r['speed'] for r in gold if r['feature'] == 'Bridge') <= 20.001
            previous = v9_report['plates'][i]
            grams = sum(f['total_used_g'] for f in plate['filaments'])
            reports.append({'plate': i+1, 'name': titles[i], 'warnings': plate.get('warning_message'),
                'estimated_seconds': plate['total_predication'], 'estimated_grams_including_flush_and_tower': grams,
                'seconds_saved_vs_v9': previous['estimated_seconds']-plate['total_predication'],
                'grams_saved_vs_v9': previous['estimated_grams_including_flush_and_tower']-grams,
                'filament_changes': 1, 'green_top_skin_absent': True, 'gold_layers': layer_report,
                'gold_sparse_layers': 2, 'gold_closing_layers_including_bridge': 6,
                'last_layer_one_outer_wall_no_inner_walls': True,
                'gold_speeds_mm_s': {f: sorted({r['speed'] for r in gold if r['feature'] == f}) for f in sorted({r['feature'] for r in gold})},
                'gcode_sha256': hashlib.sha256(code.encode()).hexdigest()})
            if i == 0:
                preview(rows, next(m for _, col, m in native[0] if col == 3).bounds)
    report = {'project': TARGET.name, 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        'source': SOURCE.name, 'source_sha256': source_hash, 'printer': cfg['printer_settings_id'],
        'bambu_version': version, 'native_reopen_exit': 0, 'native_slice_exit': 0,
        'all_3d_archive_entries_byte_identical_to_v9': True, 'all_global_and_filament_settings_unchanged': True,
        'only_print_setting_changes': {'gold_bottom_shell_layers': ['5', '0'], 'gold_bottom_shell_thickness': ['0.8', '0']},
        'layer_height_mm': .16, 'gold_thickness_mm': 1.28, 'gold_top_shell_layers': 6,
        'gold_top_shell_thickness_mm': .96, 'seam_position': 'back', 'wall_loops': 3,
        'top_one_wall_type': cfg.get('top_one_wall_type'), 'sparse_infill': '15% gyroid',
        'gold_flow_ratio': cfg['filament_flow_ratio'][2], 'gold_nozzle_temperature_c': cfg['nozzle_temperature'][2],
        'supports': False, 'brim': False, 'plates': reports,
        'physical_surface_tested': False, 'physical_print_started': False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
