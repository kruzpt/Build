"""One approved tree coupon: one wall and line fill, using the V5 profiles.

This prepares and verifies a project; it never starts a physical print.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_pintos_pla_3mf import read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'm7-dourado-linhas-v6'
SOURCE = ROOT / 'downloads/m7-dourado-paredes-v5-A1-AMS-1-prato.3mf'
TARGET = ROOT / 'downloads' / f'{PREFIX}-A1-AMS-1-prato.3mf'
FOLDER = ROOT / 'fusion/M7DouradoLinhasV6'
CHANGES = {
    'wall_loops': '1',
    'top_surface_pattern': 'monotonicline',
    'bottom_surface_pattern': 'monotonicline',
    'top_shell_layers': '5',
    'top_shell_thickness': '1',
    'bottom_shell_layers': '0',
    'bottom_shell_thickness': '0',
}
GLOBAL_CHANGES = {
    'internal_solid_infill_pattern': 'monotonic',
    'detect_narrow_internal_solid_infill': '0',
}


def put(node, key, value):
    child = node.find(f"metadata[@key='{key}']")
    if child is None:
        child = ET.SubElement(node, 'metadata', key=key)
    child.set('value', str(value))


def write(path, blobs):
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items():
            z.writestr(name, data)


def diagonal_fill_fraction(rows, height):
    total = aligned = 0.
    for r in rows:
        if r['feature'] != 'Internal solid infill' or abs(r['layer'] - height) > .0001:
            continue
        for a, b in zip(r['points'], r['points'][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            if length < .7:
                continue
            angle = math.degrees(math.atan2(dy, dx)) % 180
            total += length
            if min(abs(angle - 45), abs(angle - 135)) < .2:
                aligned += length
    assert total > 0
    return aligned / total


def draw_paths(rows, bounds):
    im = Image.new('RGB', (1320, 920), '#f5f7fa')
    d = ImageDraw.Draw(im)
    font = lambda size: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    d.text((30, 20), 'V6 — uma parede e preenchimento em linhas', font=font(30), fill='#17344a')
    d.text((30, 70), 'Percursos reais do Bambu · mesma árvore e perfis do V5 · acabamento por testar', font=font(21), fill='#455d70')
    colors = {'Outer wall': '#778894', 'Internal solid infill': '#247ba0', 'Top surface': '#247ba0', 'Gap infill': '#d65a3b'}
    for i, (height, label) in enumerate(((1.0, 'Camada interna — Z 1,00 mm'), (1.6, 'Última camada — Z 1,60 mm'))):
        left = 35 + i * 650
        d.text((left, 135), label, font=font(24), fill='#17344a')
        scale = 19
        xy = lambda p: (left + 35 + (p[0] - bounds[0, 0]) * scale, 770 - (p[1] - bounds[0, 1]) * scale)
        for r in rows:
            if abs(r['layer'] - height) < .0001:
                d.line([xy(p) for p in r['points']], fill=colors.get(r['feature'], '#333333'), width=2)
    d.text((30, 820), 'Cinza: parede · Azul: preenchimento em linhas · Vermelho: preenchimento de lacunas', font=font(21), fill='#17344a')
    d.text((30, 865), 'Ainda existem pequenos percursos no topo. A direção e os inícios podem variar entre camadas.', font=font(20), fill='#455d70')
    im.save(ROOT / 'designs' / f'{PREFIX}-percursos.png')


def main(a):
    FOLDER.mkdir(exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    original, settings, _ = read_project(SOURCE)
    blobs = dict(original)
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    source_cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert cfg['filament_flow_ratio'][:2] == ['0.931', '0.9702']
    assert cfg['nozzle_temperature'][:2] == ['220', '215']
    cfg.update(GLOBAL_CHANGES)
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    obj = next(o for o in settings.findall('object') if any('-D-arvore-' in m.get('value', '') for p in o.findall('part') for m in p.findall("metadata[@key='name']")))
    obj_id = obj.get('id')
    original_parts = {ident: (col, mesh) for ident, col, mesh in plate_meshes(original, settings)[0]}
    refs = [(int(p.get('id')), *original_parts[int(p.get('id'))]) for p in obj.findall('part')]
    for other in settings.findall('object'):
        if other is not obj:
            settings.remove(other)
    put(obj, 'name', 'V6 - mesma arvore D - 1 parede - linhas')
    tree = next(p for p in obj.findall('part') if p.find("metadata[@key='extruder'][@value='2']") is not None)
    old_tree_props = {m.get('key'): m.get('value') for m in tree.findall('metadata')}
    for key, value in CHANGES.items():
        put(tree, key, value)
    plate = settings.find('plate')
    put(plate, 'plater_name', '01 V6 - 1 parede e linhas')
    for inst in plate.findall('model_instance'):
        if inst.find("metadata[@key='object_id']").get('value') != obj_id:
            plate.remove(inst)
    # Preserve production namespaces and external component references byte-for-byte.
    source_model = blobs['3D/3dmodel.model']
    build = re.search(rb'(<build\b[^>]*>)(.*?)(</build>)', source_model, re.S)
    assert build
    item = next(m.group(0) for m in re.finditer(rb'<item\b[^>]*/>', build[2]) if re.search(rb'objectid="' + obj_id.encode() + rb'"', m.group(0)))
    item = re.sub(rb'transform="[^"]*"', b'transform="1 0 0 0 1 0 0 0 1 112 110 0"', item)
    blobs['3D/3dmodel.model'] = source_model[:build.start()] + build[1] + b'\n  ' + item + b'\n ' + build[3] + source_model[build.end():]
    blobs['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    write(a.work_dir / 'input.3mf', blobs)
    common = ['--datadir', str(a.work_dir / 'user'), '--debug', '2']
    run_cli(a.bambu_bin, common + ['--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir), '--export-3mf', 'native.3mf', str(a.work_dir / 'input.3mf')], a.work_dir / 'export.log')
    annotate(a.work_dir / 'native.3mf', TARGET, cfg['filament_colour'], PREFIX)
    actual, actual_settings, plates = read_project(TARGET)
    actual_cfg = json.loads(actual['Metadata/project_settings.config'])
    for key, value in GLOBAL_CHANGES.items():
        assert actual_cfg[key] == value
    for key, value in cfg.items():
        if key.startswith('filament_') or 'temperature' in key or key in ('printer_settings_id', 'layer_height', 'initial_layer_print_height', 'wall_generator', 'brim_type', 'enable_support'):
            assert actual_cfg.get(key) == value, key
    assert len(plates) == 1 and len(plates[0]['items']) == 1
    native = plate_meshes(actual, actual_settings)[0]
    assert len(native) == 2
    for ident, col, ref in refs:
        mesh = next(m for key, color, m in native if color == col)
        assert mesh.is_watertight and mesh.is_winding_consistent
        assert abs(mesh.volume - ref.volume) < .001
        assert np.allclose(mesh.extents, ref.extents, atol=.001)
        # Compare actual vertex coordinates after removing placement translation.
        p = np.round(mesh.vertices - mesh.bounds[0], 4)
        q = np.round(ref.vertices - ref.bounds[0], 4)
        assert p.shape == q.shape
        assert np.allclose(p[np.lexsort(p.T)], q[np.lexsort(q.T)], atol=.0002)
        mesh.apply_translation([-112, -110, 0])
        suffix = 'base-laranja.stl' if col == 1 else 'arvore-dourada.stl'
        mesh.export(ROOT / 'downloads' / f'{PREFIX}-{suffix}')
        mesh.apply_translation([112, 110, 0])
    final_tree = next(p for o in actual_settings.findall('object') for p in o.findall('part') if p.find("metadata[@key='extruder'][@value='2']") is not None)
    props = {m.get('key'): m.get('value') for m in final_tree.findall('metadata')}
    for key, value in CHANGES.items():
        assert props[key] == value, key
    run_cli(a.bambu_bin, common + ['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir / 'slice'), '--export-3mf', 'validation.3mf', str(TARGET)], a.work_dir / 'slice.log')
    result = json.loads((a.work_dir / 'slice/result.json').read_text())
    assert result['return_code'] == 0
    p = result['sliced_plates'][0]
    assert not p.get('warning_message') and p['filament_change_times'] == 1
    with ZipFile(a.work_dir / 'slice/validation.3mf') as z:
        code = z.read('Metadata/plate_1.gcode').decode()
    assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
    rows = paths(code)
    assert set(r['tool'] for r in rows) == {1, 2}
    model_rows = [r for r in rows if r['feature'] != 'Prime tower']
    assert all(r['tool'] == 1 for r in model_rows if r['layer'] <= .60001)
    assert all(r['tool'] == 2 for r in model_rows if r['layer'] > .60001)
    tree_mesh = next(m for key, col, m in native if col == 2)
    gold_rows = [r for r in model_rows if r['tool'] == 2]
    assert all(abs(r['speed'] - 25) < .001 for r in gold_rows)
    assert all(r['feature'] != 'Inner wall' for r in gold_rows)
    layers = []
    for height in sorted(set(r['layer'] for r in gold_rows)):
        rr = [r for r in gold_rows if r['layer'] == height]
        layers.append({'z_mm': height, 'features': sorted(set(r['feature'] for r in rr))})
    assert len(layers) == 5
    assert all('Internal solid infill' in l['features'] for l in layers[:-1])
    for layer in layers[:-1]:
        fraction = diagonal_fill_fraction(gold_rows, layer['z_mm'])
        assert fraction > .8, 'Narrow-area conversion defeated the requested line fill'
        layer['long_internal_segment_length_fraction_along_45_or_135_degrees'] = fraction
    assert 'Top surface' in layers[-1]['features']
    draw_paths(gold_rows, tree_mesh.bounds)
    report = dict(project=TARGET.name, sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(), source=SOURCE.name,
        approved_coupon_geometry_reused='V5 sample D: one notch, identical base and tree', original_tree_and_base_geometry_verified=True,
        printer=actual_cfg['printer_settings_id'], bambu_version=actual_cfg['version'], nozzle_mm=.4,
        layer_height_mm=.2, base_mm=[32, 34, .6], tree_mm=tree_mesh.extents.tolist(),
        material_slots={'1': 'orange, source V5 profile', '2': 'Amazon Basics Silk PLA gold, source V5 profile'},
        flow=actual_cfg['filament_flow_ratio'][:2], nozzle_temperature_c=actual_cfg['nozzle_temperature'][:2],
        requested_tree_settings=CHANGES, requested_global_settings=GLOBAL_CHANGES,
        differences_from_V5_D={k: {'old_effective': old_tree_props.get(k, source_cfg.get(k)), 'new': v} for k, v in {**CHANGES, **GLOBAL_CHANGES}.items() if old_tree_props.get(k, source_cfg.get(k)) != v},
        tree_nominal_width_mm={k: actual_cfg[k] for k in ('outer_wall_line_width', 'top_surface_line_width', 'internal_solid_infill_line_width')},
        arachne_can_vary_actual_wall_width=True, all_tree_extrusion_speeds_verified_mm_s=25,
        no_inner_wall_extrusion_verified=True, layers=layers,
        gap_fill_still_present=any(r['feature']=='Gap infill' for r in gold_rows), identical_layer_paths_claimed=False,
        native_slice_exit=0, warnings=p.get('warning_message'), brim=False, supports=False,
        filament_changes=p['filament_change_times'], estimated_seconds=p['total_predication'],
        estimated_grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']), filaments=p['filaments'],
        physical_print_tested=False, physical_print_started=False)
    (FOLDER / 'bambu-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
