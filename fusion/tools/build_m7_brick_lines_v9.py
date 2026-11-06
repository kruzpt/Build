"""Apply physically promising V6 line-fill strategy to the existing M7 plaque.

Preserves geometry and seam painting bytes, profiles and body extrusion segments.
Prepares files only; never starts a physical print.
"""
import argparse
from collections import Counter
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
from build_m7_gold_lines_v6 import CHANGES, GLOBAL_CHANGES, diagonal_fill_fraction, put
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'm7-tijolo-v9-relevos-em-linhas'
FOLDER = ROOT / 'fusion/M7TijoloV9'
SOURCE = ROOT / 'downloads/m7-tijolo-v8-uma-parede-A1-AMS-2-pratos.3mf'
TEST = ROOT / 'downloads/m7-dourado-linhas-v6-A1-AMS-1-prato.3mf'
TARGET = ROOT / 'downloads' / f'{PREFIX}-A1-AMS-2-pratos.3mf'
SPEEDS = {k: '25' for k in ('outer_wall_speed', 'inner_wall_speed', 'internal_solid_infill_speed', 'gap_infill_speed', 'top_surface_speed')}
SPEEDS.update({k: '25' for k in ('overhang_1_4_speed', 'overhang_2_4_speed', 'overhang_3_4_speed')})


def props(node):
    return {m.get('key'): m.get('value') for m in node.findall('metadata') if m.get('key')}


def write(path, blobs):
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items():
            z.writestr(name, data)


def slice_project(binary, source, work):
    work.mkdir(parents=True, exist_ok=True)
    run_cli(binary, ['--datadir', str(work / 'user'), '--debug', '2', '--slice', '0', '--orient', '0', '--arrange', '0',
        '--outputdir', str(work / 'slice'), '--export-3mf', 'validation.3mf', str(source)], work / 'slice.log')
    result = json.loads((work / 'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 2
    rr = []
    with ZipFile(work / 'slice/validation.3mf') as z:
        for i, plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message')
            code = z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Brim' not in code and '; FEATURE: Support' not in code
            rr.append([r for r in paths(code) if r['feature'] != 'Prime tower'])
    return result, rr


def preview(rows, bounds):
    im = Image.new('RGB', (1320, 1060), '#f5f7fa')
    d = ImageDraw.Draw(im)
    font = lambda size: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    d.text((30, 25), 'Placa M7 V9 — estratégia em linhas nos relevos', font=font(30), fill='#17344a')
    d.text((30, 75), 'Percursos reais do Bambu · árvore, estrela, logótipo e Natal 2026', font=font(23), fill='#455d70')
    colors = {2: '#af8525', 3: '#60758d', 4: '#1785ae'}
    for i, (height, title) in enumerate(((1., 'Camada interna — Z 1,00 mm'), (1.6, 'Última camada — Z 1,60 mm'))):
        left = 45 + i * 650
        d.text((left, 145), title, font=font(24), fill='#17344a')
        xy = lambda p: (left + 45 + (p[0]-bounds[0, 0])*10, 930-(p[1]-bounds[0, 1])*10)
        for r in sorted(rows, key=lambda r: r['feature'] == 'Gap infill'):
            if r['tool'] == 1 or abs(r['layer']-height) > .0001:
                continue
            color = '#d34b36' if r['feature'] == 'Gap infill' else colors[r['tool']]
            d.line([xy(p) for p in r['points']], fill=color, width=2)
    d.text((30, 975), 'Branco representado a cinzento · Vermelho: lacunas ainda presentes · estrela com geometria original', font=font(20), fill='#17344a')
    d.text((30, 1015), 'Estratégia testada fisicamente na árvore V6; conjunto V9 e estrela ainda por testar.', font=font(21), fill='#455d70')
    im.save(ROOT / 'designs' / f'{PREFIX}-percursos.png')


def main(a):
    a.work_dir.mkdir(parents=True, exist_ok=True)
    FOLDER.mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    help_result = subprocess.run([str(a.bambu_bin), '--help'], capture_output=True, text=True, check=True)
    engine_version = re.search(r'BambuStudio-([\d.]+)', help_result.stdout + help_result.stderr).group(1)
    original, settings, _ = read_project(SOURCE)
    blobs = dict(original)
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    source_cfg = dict(cfg)
    test_blobs, _, _ = read_project(TEST)
    test_cfg = json.loads(test_blobs['Metadata/project_settings.config'])
    for key in set(cfg) | set(test_cfg):
        if key.startswith('filament_') or 'temperature' in key or 'retract' in key or 'fan' in key or 'volumetric' in key:
            assert cfg.get(key) == test_cfg.get(key), ('V8 and successful V6 material settings differ', key)
    cfg.update(GLOBAL_CHANGES)
    assert cfg['filament_flow_ratio'] == ['0.931', '0.9702', '0.98', '0.98']
    assert cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    body = next(o for o in settings.findall('object') if any('corpo-reforcado' in p.get('source_file', '') for p in map(props, o.findall('part'))))
    plaque = next(o for o in settings.findall('object') if any('placa-laranja' in p.get('source_file', '') for p in map(props, o.findall('part'))))
    # Global line-fill changes are needed by the plaque. Restore the original
    # settings at body-object scope; verify with a native G-code comparison.
    for key in GLOBAL_CHANGES:
        put(body, key, source_cfg[key])
    relief_ids = []
    for part in plaque.findall('part'):
        p = props(part)
        if p.get('extruder') not in ('2', '3', '4'):
            continue
        relief_ids.append(int(part.get('id')))
        for key, value in {**CHANGES, **SPEEDS}.items():
            put(part, key, value)
    assert len(relief_ids) == 3
    put(plaque, 'name', 'Placa V9 - relevos em linhas')
    put(settings.findall('plate')[1], 'plater_name', '02 Placa V9 - relevos em linhas')
    blobs['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    write(TARGET, blobs)
    native = annotate(TARGET, TARGET, cfg['filament_colour'], PREFIX)
    actual, actual_settings, actual_plates = read_project(TARGET)
    assert len(actual_plates) == 2
    assert all(actual[name] == data for name, data in original.items() if name.startswith('3D/'))
    actual_cfg = json.loads(actual['Metadata/project_settings.config'])
    assert actual_cfg == cfg
    assert {k for k in set(cfg) | set(source_cfg) if cfg.get(k) != source_cfg.get(k)} == set(GLOBAL_CHANGES)
    before_native = plate_meshes(original, ET.fromstring(original['Metadata/model_settings.config']))
    for before_plate, after_plate in zip(before_native, native):
        assert len(before_plate) == len(after_plate)
        for (oid, color, before), (aid, ac, after) in zip(before_plate, after_plate):
            assert (oid, color) == (aid, ac)
            assert np.array_equal(before.vertices, after.vertices) and np.array_equal(before.faces, after.faces)
    ref_result, ref_rows = slice_project(a.bambu_bin, SOURCE, a.work_dir / 'reference')
    result, rows = slice_project(a.bambu_bin, TARGET, a.work_dir / 'candidate')
    # Travel optimisation may reorder otherwise identical extrusion segments.
    body_key = lambda r: (r['layer'], r['feature'], r['tool'], r['speed'], r['extrusion_mm'], tuple(tuple(p) for p in r['points']))
    assert Counter(map(body_key, ref_rows[0])) == Counter(map(body_key, rows[0])), 'Body extrusion segments changed despite restoring object overrides'
    plate_rows = rows[1]
    layer_tools = {str(z): sorted(set(r['tool'] for r in plate_rows if r['layer']==z)) for z in sorted(set(r['layer'] for r in plate_rows))}
    assert len(layer_tools) == 8
    assert all(r['tool']==1 for r in plate_rows if r['layer']<=.60001)
    assert all(r['tool'] in (2, 3, 4) for r in plate_rows if r['layer']>.60001)
    relief_rows = [r for r in plate_rows if r['tool'] in (2, 3, 4)]
    assert all(r['feature'] != 'Inner wall' for r in relief_rows)
    assert all(r['speed']<=25.001 for r in relief_rows)
    gold = next(m for oid, color, m in native[1] if color==2)
    components = gold.split()
    assert len(components) == 2
    tree, star = sorted(components, key=lambda m: m.bounds[0, 1])
    assert np.allclose(star.extents, [30., 28.531700167, 1.], atol=.0001)
    component_reports = []
    for name, component in [('tree', tree), ('star', star)]:
        rr = [r for r in relief_rows if r['tool']==2 and all(np.all(np.array(p)[:2]>=component.bounds[0,:2]-.01) and np.all(np.array(p)[:2]<=component.bounds[1,:2]+.01) for p in r['points'])]
        layers = []
        for height in (.8, 1., 1.2, 1.4, 1.6):
            layer = [r for r in rr if abs(r['layer']-height)<.0001]
            assert layer and any(r['feature']=='Outer wall' for r in layer)
            info = {'z_mm': height, 'features': sorted(set(r['feature'] for r in layer))}
            if height<1.6:
                info['long_internal_fill_fraction_along_diagonals'] = diagonal_fill_fraction(rr, height)
                # The thin star has many connectors and short diagonal strokes;
                # the long-segment majority check is meaningful for the wider tree.
                assert info['long_internal_fill_fraction_along_diagonals'] > (.8 if name == 'tree' else 0)
            layers.append(info)
        component_reports.append({'name': name, 'bounds_mm': component.bounds.tolist(), 'dimensions_mm': component.extents.tolist(), 'volume_mm3': float(component.volume), 'layers': layers})
    carrier = next(m for oid, color, m in native[1] if color==1)
    preview(plate_rows, carrier.bounds)
    plates = []
    for i, p in enumerate(result['sliced_plates']):
        plates.append({'plate': i+1, 'estimated_seconds': p['total_predication'], 'estimated_grams_including_flush_and_tower': sum(f['total_used_g'] for f in p['filaments']), 'filament_changes': p['filament_change_times'], 'warnings': p.get('warning_message'), 'filaments': p['filaments']})
    report = dict(project=TARGET.name, sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(), source=SOURCE.name,
        strategy_source=TEST.name, strategy_user_reported_good_physical_result=True,
        slicer_version_actually_executed=engine_version, project_profile_version=cfg['version'], printer=cfg['printer_settings_id'],
        geometry_and_seam_paint_bytes_identical=True, transformed_meshes_identical=True,
        star_thickened=False, star_width_mm=30., body_model_extrusion_segment_multisets_identical_to_V8_on_same_slicer=True,
        body_ordered_extrusion_paths_identical=ref_rows[0] == rows[0],
        body_original_process_restored_by_object_overrides={k: source_cfg[k] for k in GLOBAL_CHANGES},
        changed_global_settings=GLOBAL_CHANGES, relief_part_overrides={**CHANGES, **SPEEDS},
        relief_material_slots=[2, 3, 4], relief_no_inner_wall_extrusion_verified=True,
        relief_extrusion_speed_limit_verified_mm_s=25,
        actual_relief_speeds_by_material_mm_s={str(t): sorted(set(r['speed'] for r in relief_rows if r['tool']==t)) for t in (2,3,4)},
        relief_features_by_material={str(t): sorted(set(r['feature'] for r in relief_rows if r['tool']==t)) for t in (2,3,4)},
        flow=cfg['filament_flow_ratio'], nozzle_temperatures_c=cfg['nozzle_temperature'], material_profiles_identical_to_successful_V6=True,
        layer_height_mm=.2, carrier_mm=carrier.extents.tolist(), material_slots_by_plaque_layer=layer_tools,
        gold_components=component_reports, plates=plates, native_slice_exit=0, supports=False, brim=False,
        small_gap_fills_still_present=any(r['feature']=='Gap infill' for r in relief_rows),
        physical_V9_print_tested=False, physical_star_print_tested=False, physical_fit_tested=False, physical_print_started=False)
    (FOLDER / 'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
