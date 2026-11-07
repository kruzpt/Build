"""Prepare the unchanged V2 mesh for A1/0.4 with removable Tree Slim support.

Uses fully resolved official 0.4 machine/process/filament profiles, not a
diameter edit of the 0.2 project. No physical print operation.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_gallardo_tomas_v2 import PARAMS as V2_PARAMS
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'gallardo-tomas-v3'
FOLDER = ROOT / 'fusion/GallardoTomasV3'
TARGET = ROOT / 'downloads' / (PREFIX + '-A1-04-PLA-suportes.3mf')
SOURCE = ROOT / 'downloads/gallardo-tomas-v2-A1-02-PLA.3mf'
SOURCE_STL = ROOT / 'downloads/gallardo-tomas-v2.stl'
NAMES = {'machine': 'Bambu Lab A1 0.4 nozzle',
         'process': '0.12mm High Quality @BBL A1',
         'filament': 'Bambu PLA Basic @BBL A1'}
PARAMS = dict(V2_PARAMS, initial_layer_print_height='0.2',
              wall_generator='arachne', min_bead_width='65%',
              support_type='tree(auto)', support_style='tree_slim',
              support_on_build_plate_only='1', support_interface_top_layers='2',
              support_interface_spacing='0.45', support_object_xy_distance='0.4',
              support_speed=['80'], support_interface_speed=['40'],
              curr_bed_type='Textured PEI Plate')


def archive(file):
    with ZipFile(file) as z:
        assert z.testzip() is None
        return {n: z.read(n) for n in z.namelist()}


def write(file, blobs):
    with ZipFile(file, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items(): z.writestr(name, data)


def png(im):
    stream = io.BytesIO()
    im.save(stream, format='PNG')
    return stream.getvalue()


def thumbnails(blobs, settings, mesh):
    im = Image.new('RGB', (700, 500), '#f5f7fa')
    d = ImageDraw.Draw(im)
    f = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    d.text((25, 22), 'Gallardo TOMAS V3', font=f(30), fill='#17344a')
    lo = mesh.bounds[0]
    for tri in mesh.triangles:
        d.polygon([(30 + (p[0] - lo[0]) * 4.2, 300 - (p[1] - lo[1]) * 4.2)
                   for p in tri], fill='#304d5c')
    d.text((25, 365), 'A1 / bico 0,4 / PLA / 0,10 mm', font=f(26), fill='#17344a')
    d.text((25, 415), 'Tree Slim / sem brim', font=f(25), fill='#17344a')
    for name, size in [('Metadata/plate_1.png', (700, 500)),
                       ('Metadata/plate_1_small.png', (140, 100)),
                       ('Auxiliaries/.thumbnails/thumbnail_3mf.png', (700, 500)),
                       ('Auxiliaries/.thumbnails/thumbnail_middle.png', (700, 500)),
                       ('Auxiliaries/.thumbnails/thumbnail_small.png', (140, 100))]:
        blobs[name] = png(im.resize(size, Image.Resampling.LANCZOS))
    plate = settings.find('plate')
    for key in ('thumbnail_no_light_file', 'top_file', 'pick_file'):
        node = plate.find(f"metadata[@key='{key}']")
        if node is not None: plate.remove(node)
    for name in ('Metadata/plate_no_light_1.png', 'Metadata/top_1.png', 'Metadata/pick_1.png'):
        blobs.pop(name, None)


def support_preview(rows):
    im = Image.new('RGB', (1400, 1030), '#f5f7fa')
    d = ImageDraw.Draw(im)
    f = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    d.text((30, 20), 'Gallardo TOMAS V3 — 0,4 mm / Tree Slim', font=f(30), fill='#17344a')
    d.text((30, 65), 'Azul: suportes em árvore · cinzento: peça · percursos reais do G-code',
           font=f(21), fill='#526476')
    available = sorted(set(r['layer'] for r in rows))
    for j, wanted in enumerate((.2, 2, 12, 26)):
        z = min(available, key=lambda v: abs(v - wanted))
        rr = [r for r in rows if r['layer'] == z]
        left, top = 30 + j % 2 * 700, 125 + j // 2 * 405
        d.text((left, top), f'Z = {z:.2f} mm', font=f(22), fill='#17344a')
        for r in sorted(rr, key=lambda r: not r['feature'].startswith('Support')):
            support = r['feature'].startswith('Support')
            xy = [(left + 20 + (p[0] - 48) * 3.8, top + 300 - (p[1] - 100) * 3.8)
                  for p in r['points']]
            d.line(xy, fill='#278bc1' if support else '#364b58', width=1)
    d.text((30, 965), 'Folga Z 0,20 mm · folga lateral 0,40 mm · 2 camadas de interface / espaçamento 0,45 mm',
           font=f(20), fill='#526476')
    im.save(ROOT / 'designs' / (PREFIX + '-04-suportes.png'))


def main(a):
    FOLDER.mkdir(exist_ok=True)
    w = a.work_dir
    w.mkdir(parents=True, exist_ok=True)
    (w / 'slice').mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    help_result = subprocess.run([str(a.bambu_bin), '--help'], capture_output=True, text=True, check=True)
    version = re.search(r'BambuStudio-([\d.]+)', help_result.stdout + help_result.stderr).group(1)
    for kind, name in NAMES.items():
        profile = flatten_profile(a.profiles, kind, name)
        if kind == 'process': profile.update(PARAMS)
        if kind == 'filament':
            profile['filament_colour'] = ['#000000']
            for key, val in [('filament_overhang_1_4_speed', '30'), ('filament_overhang_2_4_speed', '25'),
                             ('filament_overhang_3_4_speed', '20'), ('filament_overhang_4_4_speed', '15'),
                             ('filament_overhang_totally_speed', '10')]: profile[key] = [val]
        (w / (kind + '.json')).write_text(json.dumps(profile, indent=2) + '\n')
    assembly = {'plates': [{'plate_name': 'Gallardo TOMAS V3 - 0.4 Tree Slim', 'need_arrange': True,
                            'objects': [{'path': str(SOURCE_STL), 'count': 1,
                                         'filaments': [1], 'print_params': {}}]}]}
    (w / 'assembly.json').write_text(json.dumps(assembly, indent=2))
    common = ['--datadir', str(w / 'user'), '--debug', '2']
    run_cli(a.bambu_bin, common + ['--load-settings', str(w / 'machine.json') + ';' + str(w / 'process.json'),
                                  '--load-filaments', str(w / 'filament.json'),
                                  '--load-assemble-list', str(w / 'assembly.json'), '--orient', '0', '--arrange', '1',
                                  '--outputdir', str(w), '--export-3mf', 'native.3mf'], w / 'export.log')
    b, settings, plates = read_project(w / 'native.3mf')
    assert len(plates) == 1 and len(plates[0]['items']) == 1
    mesh = plates[0]['items'][0]['mesh']
    reference = trimesh.load(SOURCE_STL, force='mesh')
    assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
    np.testing.assert_allclose(mesh.extents, reference.extents, atol=.002)
    np.testing.assert_allclose(mesh.volume, reference.volume, atol=.1)
    assert abs(mesh.bounds[0, 2]) < .001 and mesh.bounds[0, :2].min() > 45 and mesh.bounds[1, :2].max() < 210
    cfg = json.loads(b['Metadata/project_settings.config'])
    assert cfg['printer_settings_id'] == NAMES['machine'] and cfg['nozzle_diameter'] == ['0.4']
    assert cfg['filament_type'] == ['PLA'] and cfg['brim_type'] == 'no_brim'
    def normalized(value):
        if isinstance(value, list) and len(value) == 1: return normalized(value[0])
        if isinstance(value, str) and re.fullmatch(r'-?\d+(?:\.\d+)?', value): return float(value)
        return value
    for key, value in PARAMS.items():
        assert normalized(cfg[key]) == normalized(value), (key, cfg[key], value)
    # Preserve the source designer/license and identify this derived profile.
    source = archive(SOURCE)['3D/3dmodel.model']
    for key in ('Designer', 'DesignerCover', 'DesignerUserId', 'License', 'Description',
                'DesignModelId', 'DesignProfileId', 'DesignRegion'):
        pattern = rb'<metadata name="' + key.encode() + rb'">.*?</metadata>'
        item = re.search(pattern, source, re.S)
        if item:
            if re.search(pattern, b['3D/3dmodel.model'], re.S):
                b['3D/3dmodel.model'] = re.sub(pattern, lambda _: item[0], b['3D/3dmodel.model'], flags=re.S)
            else:
                b['3D/3dmodel.model'] = b['3D/3dmodel.model'].replace(b'<resources>', item[0] + b'\n <resources>')
    for key, val in [('Title', 'Gallardo TOMAS V3 - A1 0.4 - Tree Slim'),
                     ('Origin', 'modified'), ('ProfileTitle', '0.10mm, 4 walls, Tree Slim support')]:
        pattern = rb'(<metadata name="' + key.encode() + rb'">).*?(</metadata>)'
        b['3D/3dmodel.model'] = re.sub(pattern, lambda m: m[1] + val.encode() + m[2], b['3D/3dmodel.model'], flags=re.S)
    settings.find('object').find("metadata[@key='name']").set('value', 'Gallardo TOMAS V3 - bico 0.4')
    thumbnails(b, settings, mesh)
    b['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    write(TARGET, b)
    run_cli(a.bambu_bin, common + ['--slice', '0', '--orient', '0', '--arrange', '0',
                                  '--outputdir', str(w / 'slice'), '--export-3mf', 'validation.3mf', str(TARGET)],
            w / 'slice.log')
    result = json.loads((w / 'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    plate = result['sliced_plates'][0]
    assert not plate.get('warning_message')
    with ZipFile(w / 'slice/validation.3mf') as z: code = z.read('Metadata/plate_1.gcode').decode()
    rows = paths(code)
    assert rows and set(r['tool'] for r in rows) == {1}
    assert '; FEATURE: Brim' not in code
    model = [r for r in rows if not r['feature'].startswith('Support')]
    supports = [r for r in rows if r['feature'].startswith('Support')]
    assert supports
    layers = sorted(set(r['layer'] for r in model))
    assert abs(layers[0] - .2) < .0001 and max(np.diff(layers)) < .10001
    outer = [r['speed'] for r in model if r['feature'] == 'Outer wall']
    assert outer and max(outer) <= 30.001
    support_preview(rows)
    report = dict(project=TARGET.name, project_sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                  source_mesh_sha256=hashlib.sha256(SOURCE_STL.read_bytes()).hexdigest(),
                  geometry_unchanged_from_v2=True, connected_watertight_components=1,
                  dimensions_in_print_position_mm=mesh.extents.tolist(), source_model_volume_mm3=reference.volume,
                  native_imported_volume_mm3=mesh.volume, official_profile_names=NAMES,
                  printer=cfg['printer_settings_id'], native_slicer_version=version,
                  nozzle_mm=.4, layer_height_mm=.1, first_layer_mm=.2,
                  filaments=cfg['filament_settings_id'], filament_slot=1, settings_changes=PARAMS,
                  native_slice_exit=0, warnings=plate.get('warning_message'),
                  estimated_seconds=plate['total_predication'],
                  estimated_grams_including_support=sum(f['total_used_g'] for f in plate['filaments']),
                  support_extrusion_mm=sum(r['extrusion_mm'] for r in supports),
                  actual_outer_wall_max_speed_mm_s=max(outer), actual_model_layer_count=len(layers),
                  brim_present=False, supports_present=True, filament_changes=plate['filament_change_times'],
                  physical_print_or_support_removal_tested=False)
    (FOLDER / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    (FOLDER / 'process-overrides.json').write_text(json.dumps(PARAMS, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('project', 'estimated_seconds', 'estimated_grams_including_support',
                                           'actual_model_layer_count', 'warnings')}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--bambu-bin', type=Path, required=True)
    p.add_argument('--profiles', type=Path, required=True)
    p.add_argument('--work-dir', type=Path, required=True)
    main(p.parse_args())
