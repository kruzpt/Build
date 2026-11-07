"""Rotate only the name 180 degrees and persist explicit support settings."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import NS, matrix, read_project, run_cli
from build_gallardo_tomas_v2 import solid, as_mesh, xml_mesh
from build_gallardo_tomas_v3_04 import PARAMS
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'gallardo-tomas-v4'
FOLDER = ROOT / 'fusion/GallardoTomasV4'
BASE = ROOT / 'downloads/gallardo-tomas-v3-A1-04-PLA-suportes.3mf'
TARGET = ROOT / 'downloads' / (PREFIX + '-A1-04-texto-direito-suportes-ON.3mf')
PRESET = 'Gallardo TOMAS V4 - 0.10mm A1 0.4 - Tree Slim ON'
SUPPORT_KEYS = ('enable_support', 'support_type', 'support_style', 'support_on_build_plate_only',
                'support_top_z_distance', 'support_bottom_z_distance', 'support_object_xy_distance',
                'support_interface_top_layers', 'support_interface_spacing')


def build_geometry(source):
    blobs, _, plates = read_project(source)
    car, text = [i['mesh'].copy() for i in plates[0]['items']]
    root = ET.fromstring(blobs['3D/3dmodel.model'])
    pose = matrix(root.find(f'{{{NS}}}build/{{{NS}}}item').get('transform'))
    car.apply_transform(np.linalg.inv(pose))
    car.apply_translation(-car.bounds.mean(axis=0))
    car.apply_scale(np.array([-150, 30, -37.3]) / car.extents)
    car.apply_translation([0, 0, 18.65])
    profile = solid(car).rotate((90, 0, 0)).slice(0).simplify(.001)
    car_solid = profile.extrude(30).translate((0, 0, -15)).rotate((-90, 0, 0))
    letters = md.Manifold.batch_boolean([solid(g) for g in text.split()], md.OpType.Add)
    name = letters.slice(18).offset(1.6).simplify(.001)
    b = name.bounds()
    name = name.translate((-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2))
    name = name.scale((150 / (b[2] - b[0]), 30 / (b[3] - b[1]))).rotate(180)
    name_solid = name.extrude(37.5).translate((0, 0, -.1))
    raw = car_solid ^ name_solid
    # Rotation changes crossings: connect the newly isolated lower door detail.
    connector = md.Manifold.cylinder(1.2, .6, .6, 32, True).translate((8.45, -13.7, 4.1))
    connector = connector ^ name_solid  # preserve the exact new name silhouette
    result = (raw + connector).set_tolerance(.001)
    m = as_mesh(result)
    assert len(result.decompose()) == 1 and m.is_watertight and m.is_winding_consistent
    assert len(m.split(only_watertight=False)) == 1
    shadow = result.project()
    name_error = (name - shadow).area() + (shadow - name).area()
    assert name_error < .1
    np.testing.assert_allclose(m.extents, [150, 30, 37.3], atol=.002)
    report = dict(text_rotation_relative_to_v3_degrees=180, car_orientation_preserved=True,
                  assembly_extents_mm=m.extents.tolist(), text_contour_offset_mm=1.6,
                  connector_center_assembly_mm=[8.45, -13.7, 4.1], connector_diameter_mm=1.2,
                  connector_height_mm=1.2, connector_added_volume_mm3=result.volume() - raw.volume(),
                  name_projection_symmetric_difference_mm2=name_error, watertight_single_component=True,
                  volume_mm3=result.volume(), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    return m, report


def png(im):
    stream = io.BytesIO()
    im.save(stream, format='PNG')
    return stream.getvalue()


def render_views(m):
    im = Image.new('RGB', (2800, 1960), '#f5f7fa')
    d = ImageDraw.Draw(im)
    def label(x, y, s, size=24):
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size * 2)
        d.text((x * 2, y * 2), s, font=f, fill='#17344a')
    label(35, 20, 'V4 — texto rodado 180° em relação ao carro', 32)
    label(35, 80, '1. Olhar para o carro de lado')
    for tri in m.triangles:
        d.polygon([((40 + (x + 75) * 8.7) * 2, (150 + (37.3 - z) * 8.7) * 2)
                   for x, y, z in tri], fill='#304d5c')
    label(35, 535, '2. Inclinar para ver o topo — mantendo a mesma esquerda e direita')
    for tri in m.triangles:
        d.polygon([((40 + (x + 75) * 8.7) * 2, (605 + (15 - y) * 8.7) * 2)
                   for x, y, z in tri], fill='#304d5c')
    label(35, 920, 'Mesma orientação do observador nas duas vistas · projeções da geometria real', 20)
    im = im.resize((1400, 980), Image.Resampling.LANCZOS)
    im.save(ROOT / 'designs' / (PREFIX + '-orientacao.png'))
    return im


def setmeta(node, key, value):
    item = node.find(f"metadata[@key='{key}']")
    if item is None: item = ET.SubElement(node, 'metadata', key=key)
    item.set('value', str(value))


def write(file, blobs):
    with ZipFile(file, 'w', ZIP_DEFLATED) as z:
        for name, value in blobs.items(): z.writestr(name, value)


def main(a):
    FOLDER.mkdir(exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    (a.work_dir / 'slice').mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    m, geo = build_geometry(a.source)
    views = render_views(m)
    placed = m.copy()
    placed.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    placed.apply_translation([128 - placed.bounds.mean(axis=0)[0],
                              128 - placed.bounds.mean(axis=0)[1], -placed.bounds[0, 2]])
    placed = as_mesh(solid(placed).set_tolerance(.001))
    stl = ROOT / 'downloads' / (PREFIX + '-texto-direito.stl')
    placed.export(stl)
    check = trimesh.load(stl, force='mesh')
    assert check.is_watertight and check.is_winding_consistent and len(check.split()) == 1
    np.testing.assert_allclose(check.extents, [150, 37.3, 30], atol=.002)
    b, settings, _ = read_project(BASE)
    b['3D/Objects/object_1.model'] = re.sub(rb'<mesh>.*?</mesh>', lambda _: xml_mesh(placed),
                                             b['3D/Objects/object_1.model'], flags=re.S)
    ET.register_namespace('', NS)
    ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
    root = ET.fromstring(b['3D/3dmodel.model'])
    identity = '1 0 0 0 1 0 0 0 1 0 0 0'
    root.find(f'{{{NS}}}resources/{{{NS}}}object/{{{NS}}}components/{{{NS}}}component').set('transform', identity)
    root.find(f'{{{NS}}}build/{{{NS}}}item').set('transform', identity)
    for node in root.findall(f'{{{NS}}}metadata'):
        if node.get('name') == 'Title': node.text = 'Gallardo TOMAS V4 - texto direito - suportes ON'
        if node.get('name') == 'ProfileTitle': node.text = PRESET
    b['3D/3dmodel.model'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    cfg = json.loads(b['Metadata/project_settings.config'])
    cfg['print_settings_id'] = PRESET
    cfg['enable_support'] = '1'
    cfg['inherits_group'][0] = '0.12mm High Quality @BBL A1'
    cfg['different_settings_to_system'][0] = ';'.join(sorted(PARAMS))
    obj = settings.find('object')
    setmeta(obj, 'name', 'Gallardo TOMAS V4 - texto direito - suportes ON')
    obj.find('metadata[@face_count]').set('face_count', str(len(placed.faces)))
    for key in SUPPORT_KEYS: setmeta(obj, key, cfg[key])
    part = obj.find('part')
    for node in list(part):
        if node.tag == 'metadata' and node.get('key', '').startswith('source_'): part.remove(node)
    setmeta(part, 'name', 'Gallardo TOMAS V4 - corpo unico')
    setmeta(part, 'matrix', '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    part.find('mesh_stat').set('face_count', str(len(placed.faces)))
    plate = settings.find('plate')
    setmeta(plate, 'plater_name', 'Gallardo TOMAS V4 - 0.4 Tree Slim ON')
    setmeta(plate, 'thumbnail_file', 'Metadata/plate_1.png')
    for name, size in [('Metadata/plate_1.png', (700, 490)), ('Metadata/plate_1_small.png', (140, 98)),
                       ('Auxiliaries/.thumbnails/thumbnail_3mf.png', (700, 490)),
                       ('Auxiliaries/.thumbnails/thumbnail_middle.png', (700, 490)),
                       ('Auxiliaries/.thumbnails/thumbnail_small.png', (140, 98))]:
        b[name] = png(views.resize(size, Image.Resampling.LANCZOS))
    b['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    b['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    write(TARGET, b)
    fresh, fresh_settings, fresh_plates = read_project(TARGET)
    assert json.loads(fresh['Metadata/project_settings.config'])['enable_support'] == '1'
    assert fresh_settings.find("object/metadata[@key='enable_support']").get('value') == '1'
    assert fresh_plates[0]['items'][0]['mesh'].is_watertight
    run_cli(a.bambu_bin, ['--datadir', str(a.work_dir / 'user'), '--debug', '2', '--slice', '0',
                         '--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir / 'slice'),
                         '--export-3mf', 'validation.3mf', str(TARGET)], a.work_dir / 'slice.log')
    result = json.loads((a.work_dir / 'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    p = result['sliced_plates'][0]
    assert not p.get('warning_message')
    native, native_settings, native_plates = read_project(a.work_dir / 'slice/validation.3mf')
    nc = json.loads(native['Metadata/project_settings.config'])
    assert nc['enable_support'] == '1' and nc['print_settings_id'] == PRESET
    assert native_settings.find("object/metadata[@key='enable_support']").get('value') == '1'
    assert len(native_plates[0]['items'][0]['mesh'].split()) == 1
    with ZipFile(a.work_dir / 'slice/validation.3mf') as z: code = z.read('Metadata/plate_1.gcode').decode()
    rows = paths(code)
    supports = [r for r in rows if r['feature'].startswith('Support')]
    assert supports and set(r['tool'] for r in rows) == {1}
    assert '; FEATURE: Brim' not in code
    # Reuse the path renderer with its title changed for this revision.
    import build_gallardo_tomas_v3_04 as drawing
    drawing.PREFIX = PREFIX
    drawing.support_preview(rows)
    # Correct the renderer's fixed old title by creating a clean title strip.
    image_path = ROOT / 'designs' / (PREFIX + '-04-suportes.png')
    im = Image.open(image_path).convert('RGB'); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1399, 60), fill='#f5f7fa')
    d.text((30, 20), 'Gallardo TOMAS V4 — 0,4 mm / suportes ON', fill='#17344a',
           font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30))
    im.save(image_path)
    report = dict(project=TARGET.name, sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(), geometry=geo,
                  printer=cfg['printer_settings_id'], profile=PRESET, layer_height_mm=.1,
                  support_enabled_in_global_project=True, support_enabled_in_object=True,
                  native_reexport_preserves_profile_and_both_support_flags=True,
                  support_type=cfg['support_type'], support_style=cfg['support_style'],
                  support_settings={k: cfg[k] for k in SUPPORT_KEYS}, native_slice_exit=0,
                  warnings=p['warning_message'], support_extrusion_mm=sum(r['extrusion_mm'] for r in supports),
                  estimated_seconds=p['total_predication'],
                  estimated_grams_including_support=sum(f['total_used_g'] for f in p['filaments']),
                  brim_present=False, physical_print_tested=False, user_gui_support_state_reproduced=False)
    (FOLDER / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('project', 'estimated_seconds', 'estimated_grams_including_support', 'warnings')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
