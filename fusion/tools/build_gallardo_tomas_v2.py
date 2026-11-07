"""Build and slice the approved single-piece TOMAS/Gallardo illusion.

Requires the user's pre-Boolean 3MF; retains its complete A1/0.2 profiles and
base-model attribution. No Fusion connection or physical printer operation.
"""
import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import NS, matrix, read_project, run_cli
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'gallardo-tomas-v2'
FOLDER = ROOT / 'fusion/GallardoTomasV2'
TARGET = ROOT / 'downloads' / (PREFIX + '-A1-02-PLA.3mf')
PARAMS = {
    'brim_type': 'no_brim', 'layer_height': '0.1',
    'initial_layer_print_height': '0.1', 'wall_loops': '4',
    'sparse_infill_density': '20%', 'sparse_infill_pattern': 'gyroid',
    'outer_wall_speed': '30', 'inner_wall_speed': '50',
    'top_surface_speed': '25', 'internal_solid_infill_speed': '50',
    'sparse_infill_speed': '70', 'bridge_speed': '20', 'gap_infill_speed': '25',
    'initial_layer_speed': '20', 'initial_layer_infill_speed': '25',
    'outer_wall_acceleration': '800', 'top_surface_acceleration': '800',
    'enable_support': '1', 'support_type': 'normal(auto)', 'support_style': 'snug',
    'support_threshold_angle': '35', 'support_on_build_plate_only': '0',
    'support_top_z_distance': '0.2', 'support_bottom_z_distance': '0.2',
    'support_interface_top_layers': '3', 'support_interface_bottom_layers': '2',
    'support_interface_spacing': '0.3', 'support_object_xy_distance': '0.35',
    'support_base_pattern_spacing': '3', 'support_filament': '0',
    'support_interface_filament': '0', 'top_surface_pattern': 'monotonicline',
    'bottom_surface_pattern': 'monotonic',
    'detect_narrow_internal_solid_infill': '0',
    'internal_solid_infill_pattern': 'monotonic', 'enable_prime_tower': '0',
    'overhang_1_4_speed': ['30'], 'overhang_2_4_speed': ['25'],
    'overhang_3_4_speed': ['20'], 'overhang_4_4_speed': ['15'],
    'overhang_totally_speed': ['10'],
}


def solid(m):
    out = md.Manifold(md.Mesh64(np.asarray(m.vertices, dtype=np.float64),
                                np.asarray(m.faces, dtype=np.uint64)))
    assert out.status() == md.Error.NoError
    return out


def as_mesh(s):
    r = s.to_mesh64()
    return trimesh.Trimesh(r.vert_properties[:, :3], r.tri_verts, process=True)


def xml_mesh(m):
    vertices = ''.join('<vertex x="%.12g" y="%.12g" z="%.12g"/>' % tuple(p)
                       for p in m.vertices)
    faces = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in m.faces)
    return ('<mesh><vertices>' + vertices + '</vertices><triangles>' + faces +
            '</triangles></mesh>').encode()


def png(im):
    stream = io.BytesIO()
    im.save(stream, format='PNG')
    return stream.getvalue()


def make_geometry(blobs, plates):
    car, text = [item['mesh'].copy() for item in plates[0]['items']]
    root = ET.fromstring(blobs['3D/3dmodel.model'])
    pose = matrix(root.find(f'{{{NS}}}build/{{{NS}}}item').get('transform'))
    # Remove the source's unintended ~0.04-degree tilt; retain overall envelope.
    car.apply_transform(np.linalg.inv(pose))
    car.apply_translation(-car.bounds.mean(axis=0))
    car.apply_scale(np.array([-150, 30, -37.3]) / car.extents)
    car.apply_translation([0, 0, 18.65])
    car_section = solid(car).rotate((90, 0, 0)).slice(0).simplify(.001)
    car_solid = car_section.extrude(30).translate((0, 0, -15)).rotate((-90, 0, 0))
    glyphs = [solid(g) for g in text.split()]
    united = md.Manifold.batch_boolean(glyphs, md.OpType.Add)
    section = united.slice(18).offset(1.6).simplify(.001)
    b = section.bounds()
    section = section.translate((-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2))
    section = section.scale((150 / (b[2] - b[0]), 30 / (b[3] - b[1])))
    # Extend beyond both car caps to avoid almost coincident Boolean faces.
    text_solid = section.extrude(37.5).translate((0, 0, -.1))
    result = (car_solid ^ text_solid).set_tolerance(.001)
    final = as_mesh(result)
    assert result.status() == md.Error.NoError and len(result.decompose()) == 1
    assert final.is_watertight and final.is_winding_consistent
    assert len(final.split(only_watertight=False)) == 1
    np.testing.assert_allclose(final.extents, [150, 30, 37.3], atol=.003)
    # Check both intended views, allowing only the numerical cleanup tolerance.
    car_shadow = result.rotate((90, 0, 0)).project()
    car_area_error = (car_section - car_shadow).area() + (car_shadow - car_section).area()
    name_shadow = result.project()
    name_area_error = (section - name_shadow).area() + (name_shadow - section).area()
    assert car_area_error < .1 and name_area_error < .1
    return final, dict(
        text_outline_offset_before_normalization_mm=1.6,
        text_footprint_after_normalization_mm=[150, 30],
        source_text_closed_shells=len(glyphs), fused_text_components=len(united.decompose()),
        assembly_extents_xyz_mm=final.extents.tolist(), volume_mm3=final.volume,
        source_car_section_area_mm2=car_section.area(), name_projection_area_mm2=name_shadow.area(),
        car_projection_symmetric_difference_mm2=car_area_error,
        name_projection_symmetric_difference_mm2=name_area_error,
        outline_simplification_tolerance_mm=.001, final_solid_tolerance_mm=.001,
        source_unintended_tilt_removed=True, connected_components=1,
        watertight=True, winding_consistent=True)


def preview(assembly, placed):
    im = Image.new('RGB', (2800, 2220), '#f5f7fa')
    d = ImageDraw.Draw(im)
    def label(x, y, text, n=22):
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n * 2)
        d.text((x * 2, y * 2), text, font=f, fill='#17344a')
    label(35, 22, 'Gallardo + TOMAS V2 — uma única peça', 32)
    label(35, 75, '150 × 30 × 37,3 mm · traço reforçado · sem fragmentos soltos')
    label(35, 126, 'Vista de lado — Gallardo')
    for tri in assembly.triangles:
        d.polygon([((45 + (v[0] + 75) * 8.7) * 2,
                    (185 + (37.3 - v[2]) * 8.7) * 2) for v in tri], fill='#304d5c')
    label(35, 545, 'Vista de cima — TOMAS')
    for tri in assembly.triangles:
        d.polygon([((45 + (75 - v[0]) * 8.7) * 2,
                    (595 + (v[1] + 15) * 8.7) * 2) for v in tri], fill='#304d5c')
    label(35, 915, 'Impressão: deitado sobre um lado · A1, bico 0,2 mm · camadas de 0,10 mm')
    label(35, 958, '4 paredes · 20% Gyroid · suportes normais Snug · sem brim')
    label(35, 1001, 'Cor do projeto: PLA preto, posição 3 do ficheiro enviado.')
    label(35, 1054, 'Projeções do modelo real; não é uma fotografia de uma impressão.', 19)
    im = im.resize((1400, 1110), Image.Resampling.LANCZOS)
    im.save(ROOT / 'designs' / (PREFIX + '-vistas.png'))
    thumb = Image.new('RGB', (512, 512), '#f5f7fa')
    dr = ImageDraw.Draw(thumb)
    for tri in placed.triangles:
        dr.polygon([(30 + (v[0] - 53) * 3, 330 - (v[1] - 109.35) * 3) for v in tri],
                   fill='#304d5c')
    dr.text((25, 45), 'Gallardo TOMAS V2', fill='#17344a',
            font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 29))
    dr.text((25, 410), 'A1 / 0.2 / PLA / 0.10 mm', fill='#17344a',
            font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23))
    return thumb


def prepare(source):
    blobs, settings, plates = read_project(source)
    assert len(plates) == 1 and len(plates[0]['items']) == 2
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id'] == 'Bambu Lab A1 0.2 nozzle'
    assert cfg['filament_type'][2] == 'PLA'
    assembly, geo = make_geometry(blobs, plates)
    placed = assembly.copy()
    placed.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    placed.apply_translation([128 - placed.bounds.mean(axis=0)[0],
                              128 - placed.bounds.mean(axis=0)[1], -placed.bounds[0, 2]])
    placed = as_mesh(solid(placed).set_tolerance(.001))
    assert placed.is_watertight and len(placed.split(only_watertight=False)) == 1
    np.testing.assert_allclose(placed.extents, [150, 37.3, 30], atol=.003)
    assert abs(placed.bounds[0, 2]) < .001
    assert placed.bounds[0, :2].min() > 50 and placed.bounds[1, :2].max() < 206
    stl_path = ROOT / 'downloads' / (PREFIX + '.stl')
    placed.export(stl_path)
    reloaded = trimesh.load(stl_path, force='mesh')
    assert reloaded.is_watertight and reloaded.is_winding_consistent
    assert len(reloaded.split(only_watertight=False)) == 1
    np.testing.assert_allclose(reloaded.extents, placed.extents, atol=.0001)
    geo['stl_roundtrip_watertight_single_component'] = True
    geo['print_extents_xyz_mm'] = placed.extents.tolist()
    geo['print_rotation_from_assembly_x_degrees'] = -90
    geo['print_triangle_count'] = len(placed.faces)

    b = copy.deepcopy(blobs)
    b['3D/Objects/object_1.model'] = re.sub(rb'<mesh>.*?</mesh>', lambda _: xml_mesh(placed),
                                             b['3D/Objects/object_1.model'], flags=re.S)
    b.pop('3D/Objects/object_2.model')
    ET.register_namespace('', NS)
    ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
    root = ET.fromstring(b['3D/3dmodel.model'])
    res = root.find(f'{{{NS}}}resources')
    res.remove(res.findall(f'{{{NS}}}object')[1])
    build = root.find(f'{{{NS}}}build')
    build.remove(build.findall(f'{{{NS}}}item')[1])
    build.find(f'{{{NS}}}item').set('transform', '1 0 0 0 1 0 0 0 1 0 0 0')
    for node in root.findall(f'{{{NS}}}metadata'):
        if node.get('name') == 'Title': node.text = 'Gallardo TOMAS V2 - one piece'
        if node.get('name') == 'Origin': node.text = 'modified'
        if node.get('name') == 'ProfileTitle': node.text = '0.10mm, 4 walls, 20% Gyroid, supports'
    b['3D/3dmodel.model'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    # Keep OPC Relationship elements unprefixed for native Bambu's reader.
    key = '3D/_rels/3dmodel.model.rels'
    b[key] = re.sub(rb'<Relationship\b[^>]*Target="/3D/Objects/object_2.model"[^>]*/>', b'', b[key])
    settings.remove(settings.findall('object')[1])
    obj = settings.find('object')
    obj.find("metadata[@key='name']").set('value', 'Gallardo TOMAS V2')
    obj.find('metadata[@face_count]').set('face_count', str(len(placed.faces)))
    part = obj.find('part')
    part.find("metadata[@key='name']").set('value', 'Gallardo TOMAS V2 - single solid')
    for node in list(part):
        if node.tag == 'metadata' and node.get('key', '').startswith('source_'): part.remove(node)
    part.find('mesh_stat').set('face_count', str(len(placed.faces)))
    plate = settings.find('plate')
    plate.remove(plate.findall('model_instance')[1])
    plate.find("metadata[@key='plater_name']").set('value', 'Gallardo TOMAS V2 - PLA 0.10')
    for key in ('thumbnail_no_light_file', 'top_file', 'pick_file'):
        node = plate.find(f"metadata[@key='{key}']")
        if node is not None: plate.remove(node)
    if settings.find('assemble') is not None: settings.remove(settings.find('assemble'))
    b['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    for name in ('Metadata/plate_no_light_1.png', 'Metadata/top_1.png', 'Metadata/pick_1.png',
                 'Metadata/cut_information.xml', 'Metadata/slice_info.config'):
        b.pop(name, None)
    cfg.update(PARAMS)
    # The supplied filament profile can override process overhang speeds.
    # Limit only the active black PLA, retaining its calibrated flow/temperature.
    for key, value in [('filament_overhang_1_4_speed', '30'),
                       ('filament_overhang_2_4_speed', '25'),
                       ('filament_overhang_3_4_speed', '20'),
                       ('filament_overhang_4_4_speed', '15'),
                       ('filament_overhang_totally_speed', '10')]:
        cfg[key] = list(cfg[key])
        cfg[key][2] = value
    b['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    source_cfg = json.loads(blobs['Metadata/project_settings.config'])
    for key in ('nozzle_temperature', 'nozzle_temperature_initial_layer', 'filament_flow_ratio',
                'pressure_advance', 'filament_settings_id', 'printer_settings_id',
                'curr_bed_type', 'filament_colour', 'filament_type'):
        assert cfg.get(key) == source_cfg.get(key), key
    thumb = preview(assembly, placed)
    for name, size in [('Metadata/plate_1.png', 512), ('Metadata/plate_1_small.png', 128),
                       ('Auxiliaries/.thumbnails/thumbnail_3mf.png', 512),
                       ('Auxiliaries/.thumbnails/thumbnail_middle.png', 512),
                       ('Auxiliaries/.thumbnails/thumbnail_small.png', 128)]:
        b[name] = png(thumb.resize((size, size), Image.Resampling.LANCZOS))
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as z:
        for name, data in b.items(): z.writestr(name, data)
    actual, _, ps = read_project(TARGET)
    check = ps[0]['items'][0]['mesh']
    assert len(ps[0]['items']) == 1 and check.is_watertight and len(check.split()) == 1
    assert not any(n.endswith('.gcode') for n in actual)
    geo['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    geo['source_filename'] = source.name
    geo['source_designer'] = 'Dava'
    geo['source_license'] = 'Standard Digital File License'
    return geo, cfg


def toolpath_preview(rows):
    im = Image.new('RGB', (1400, 1100), '#f5f7fa')
    d = ImageDraw.Draw(im)
    f = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    d.text((30, 20), 'Gallardo TOMAS V2 — percursos de impressão', font=f(30), fill='#17344a')
    d.text((30, 68), 'Azul: suportes · cinzento: peça · camadas reais do G-code', font=f(22), fill='#526476')
    layers = sorted(set(r['layer'] for r in rows))
    for j, wanted in enumerate((.1, 2, 12, 26)):
        z = min(layers, key=lambda v: abs(v - wanted))
        rr = [r for r in rows if r['layer'] == z]
        left = 30 + j % 2 * 700
        top = 130 + j // 2 * 450
        d.text((left, top), f'Z = {z:.2f} mm', font=f(23), fill='#17344a')
        for r in sorted(rr, key=lambda r: not r['feature'].startswith('Support')):
            pts = [(left + 20 + (p[0] - 48) * 3.8, top + 330 - (p[1] - 100) * 3.8)
                   for p in r['points']]
            support = r['feature'].startswith('Support')
            d.line(pts, fill='#298fc4' if support else '#364b58', width=1)
    d.text((30, 1050), 'Suportes com folga Z de 0,20 mm; retirar por secções após arrefecer.',
           font=f(21), fill='#526476')
    im.save(ROOT / 'designs' / (PREFIX + '-suportes.png'))


def main(a):
    FOLDER.mkdir(exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    (a.work_dir / 'slice').mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    help_result = subprocess.run([str(a.bambu_bin), '--help'], capture_output=True, text=True, check=True)
    version = re.search(r'BambuStudio-([\d.]+)', help_result.stdout + help_result.stderr).group(1)
    geo, cfg = prepare(a.source)
    run_cli(a.bambu_bin, ['--datadir', str(a.work_dir / 'user'), '--debug', '2', '--allow-newer-file',
                         '--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir / 'slice'),
                         '--export-3mf', 'validation.3mf', str(TARGET)], a.work_dir / 'slice.log')
    result = json.loads((a.work_dir / 'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    plate = result['sliced_plates'][0]
    assert not plate.get('warning_message')
    with ZipFile(a.work_dir / 'slice/validation.3mf') as z:
        code = z.read('Metadata/plate_1.gcode').decode()
    _, _, native_plates = read_project(a.work_dir / 'slice/validation.3mf')
    native_mesh = native_plates[0]['items'][0]['mesh']
    assert native_mesh.is_watertight and native_mesh.is_winding_consistent
    assert len(native_mesh.split(only_watertight=False)) == 1
    np.testing.assert_allclose(native_mesh.extents, [150, 37.3, 30], atol=.002)
    rows = paths(code)
    assert rows and set(r['tool'] for r in rows) == {3}
    assert '; FEATURE: Brim' not in code
    support = [r for r in rows if r['feature'].startswith('Support')]
    assert support
    layers = sorted(set(r['layer'] for r in rows))
    assert abs(layers[0] - .1) < .0001 and max(np.diff(layers)) < .10001
    outer = [r['speed'] for r in rows if r['feature'] == 'Outer wall']
    assert max(outer) <= 30.001
    toolpath_preview(rows)
    report = dict(geometry=geo, project=TARGET.name, project_sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                  printer=cfg['printer_settings_id'], nozzle_diameter_mm=.2, filament_slot=3,
                  filament=cfg['filament_settings_id'][2], material='PLA', plate=cfg['curr_bed_type'],
                  settings_changes=PARAMS, native_slicer_version=version, native_slice_exit=0,
                  warning_message=plate.get('warning_message'), estimated_seconds=plate['total_predication'],
                  estimated_grams_including_support=sum(f['total_used_g'] for f in plate['filaments']),
                  filament_changes=plate['filament_change_times'], first_layer_mm=layers[0],
                  actual_maximum_layer_step_mm=float(max(np.diff(layers))), layer_count=len(layers),
                  actual_outer_wall_maximum_speed_mm_s=max(outer), supports_present=True,
                  actual_support_extrusion_mm=sum(r['extrusion_mm'] for r in support), brim_present=False,
                  native_exported_mesh_watertight_single_component=True,
                  source_material_temperatures_flow_and_printer_preserved=True,
                  active_filament_overhang_speed_limits_mm_s={
                      k: cfg[k][2] for k in cfg
                      if k.startswith('filament_overhang_') and k.endswith('_speed')},
                  print_bbox=plate['objects'][0]['bbox'], physical_print_tested=False)
    (FOLDER / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('project', 'estimated_seconds',
                                           'estimated_grams_including_support', 'layer_count', 'warning_message')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
