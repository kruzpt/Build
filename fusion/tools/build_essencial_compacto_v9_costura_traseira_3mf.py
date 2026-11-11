"""V5-compatible clinic base with a 1.28 mm gold finish and rear seam.

Retains the approved geometry and inverted orientation; no physical print.
"""
import argparse
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

ET.register_namespace('', 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02')
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'essencial-compacto-v9-costura-traseira'
FOLDER = ROOT / 'fusion/EssencialCompactoV9CosturaTraseira'
SOURCE = ROOT / 'downloads/essencial-compacto-v5-azeitona-A1-AMS-4-pratos.3mf'
TARGET = ROOT / 'downloads' / f'{PREFIX}-A1-AMS-2-pratos.3mf'
INTERFACE_SHIFT_MM = 0.32
GOLD_CHANGES = {
    'top_surface_pattern': 'monotonicline',
    'bottom_surface_pattern': 'monotonicline',
    'top_shell_layers': '6',
    'top_shell_thickness': '0.96',
    'outer_wall_speed': '25',
    'inner_wall_speed': '25',
    'internal_solid_infill_speed': '25',
    'gap_infill_speed': '25',
    'top_surface_speed': '20',
    'seam_position': 'back',
    'overhang_1_4_speed': '25',
    'overhang_2_4_speed': '25',
    'overhang_3_4_speed': '25',
}
GREEN_CHANGES = {
    'top_surface_pattern': 'monotonicline',
    'bottom_surface_pattern': 'monotonicline',
    'outer_wall_speed': '25',
    'inner_wall_speed': '25',
    'internal_solid_infill_speed': '25',
    'gap_infill_speed': '25',
    'top_surface_speed': '20',
    'top_shell_layers': '0',
    'top_shell_thickness': '0',
    'seam_position': 'back',
}
GLOBAL_CHANGES = {'internal_solid_infill_pattern': 'monotonic', 'detect_narrow_internal_solid_infill': '0'}


def props(node):
    return {m.get('key'): m.get('value') for m in node.findall('metadata') if m.get('key')}


def archive_write(file, blobs):
    with ZipFile(file, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items():
            z.writestr(name, data)


def shift_colour_interface(blob, green_id, gold_id):
    """Move the shared horizontal colour boundary down by 0.32 mm."""
    root = ET.fromstring(blob)
    changed = {}
    for obj in root.iter():
        if not obj.tag.endswith('object') or obj.get('id') not in (green_id, gold_id):
            continue
        vertices = [v for v in obj.iter() if v.tag.endswith('vertex')]
        z_values = [float(v.get('z')) for v in vertices]
        edge = max(z_values) if obj.get('id') == green_id else min(z_values)
        # Both local edges move down in Z: the green top lowers and the
        # gold bottom extends downward, while the gold outer top stays fixed.
        direction = -1
        count = 0
        for vertex in vertices:
            z = float(vertex.get('z'))
            if np.isclose(z, edge, atol=1e-6):
                vertex.set('z', format(z + direction * INTERFACE_SHIFT_MM, '.9g'))
                count += 1
        assert count
        changed[obj.get('id')] = (edge, edge + direction * INTERFACE_SHIFT_MM, count)
    assert set(changed) == {green_id, gold_id}
    return ET.tostring(root, encoding='utf-8', xml_declaration=True), changed


def preview(rows, bounds):
    im = Image.new('RGB', (1480, 980), '#f5f7fa')
    d = ImageDraw.Draw(im)
    font = lambda size: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    d.text((30, 25), 'Essencial V9 — dourado de 1,28 mm e costura traseira', font=font(30), fill='#17344a')
    d.text((30, 80), 'Mesma base invertida · verde sem pele superior · costura global e por objeto na traseira', font=font(23), fill='#455d70')
    for i, (height, title) in enumerate(((8.96, 'Camada dourada interna — Z 8,96 mm'), (9.6, 'Superfície final — Z 9,60 mm'))):
        top = 180 + i * 355
        d.text((35, top-40), title, font=font(24), fill='#17344a')
        scale = 6.6
        xy = lambda p: (65+(p[0]-bounds[0, 0])*scale, top+285-(p[1]-bounds[0, 1])*scale)
        # Show a 40 mm deep strip at the same model corner so the lines are readable.
        corner_max_y = bounds[0, 1]+40
        for r in rows:
            if r['tool'] != 3 or r['feature']=='Prime tower' or abs(r['layer']-height)>.0001:
                continue
            for a, b in zip(r['points'], r['points'][1:]):
                if a[1] > corner_max_y and b[1] > corner_max_y:
                    continue
                a, b = np.array(a), np.array(b)
                if a[1] > corner_max_y:
                    a = b+(a-b)*(corner_max_y-b[1])/(a[1]-b[1])
                if b[1] > corner_max_y:
                    b = a+(b-a)*(corner_max_y-a[1])/(b[1]-a[1])
                color = '#d34b36' if r['feature']=='Gap infill' else '#a6812e' if r['feature'] in ('Top surface', 'Internal solid infill', 'Bottom surface') else '#536d81'
                d.line([xy(a), xy(b)], fill=color, width=1)
    d.text((35, 900), 'Faixa da base real · cinzento: paredes · dourado: preenchimento · vermelho: lacunas, se existirem', font=font(21), fill='#17344a')
    d.text((35, 940), 'A amostra usa as mesmas definições; confirmar fisicamente antes da base completa.', font=font(22), fill='#455d70')
    im.save(ROOT / 'designs' / f'{PREFIX}-percursos.png')


def main(a):
    a.work_dir.mkdir(parents=True, exist_ok=True)
    FOLDER.mkdir(exist_ok=True)
    bundled_libs = Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu')
    if not bundled_libs.is_dir():
        bundled_libs = ROOT / 'bambu-libs/usr/lib/x86_64-linux-gnu'
    os.environ['LD_LIBRARY_PATH'] = str(bundled_libs) + ':' + str(a.bambu_bin.parent)
    h = subprocess.run([str(a.bambu_bin), '--help'], capture_output=True, text=True, check=True)
    version = re.search(r'BambuStudio-([\d.]+)', h.stdout+h.stderr).group(1)
    source_blobs, settings, source_plates = read_project(SOURCE)
    source_meshes = plate_meshes(source_blobs, settings)
    blobs = dict(source_blobs)
    interface_changes = {}
    for name, green_id, gold_id in (
        ('3D/Objects/object_3.model', '7', '8'),
        ('3D/Objects/object_4.model', '10', '11'),
    ):
        blobs[name], interface_changes[name] = shift_colour_interface(blobs[name], green_id, gold_id)
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    before_cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle' and cfg['layer_height']=='0.16'
    cfg.update(GLOBAL_CHANGES)
    # Bambu's stored value for the UI option "rear" is "back".  "rear"
    # is silently discarded by the slicer, so do not use the UI label here.
    cfg['seam_position'] = 'back'
    cfg['filament_flow_ratio'][2] = '0.9702'
    cfg['nozzle_temperature'][2] = '215'
    cfg['nozzle_temperature_initial_layer'][2] = '215'
    # Retain the source purge-tower positions for old plates 3/4, now 1/2.
    for key in ('wipe_tower_x', 'wipe_tower_y'):
        values = cfg[key]
        cfg[key] = [values[min(i, len(values)-1)] for i in (2, 3)]
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    keep_plates = settings.findall('plate')[2:]
    keep_ids = {p['id'] for plate in source_plates[2:] for p in plate['items']}
    # read_project represents ids as integers; settings attributes are strings.
    keep_ids = {str(i) for i in keep_ids}
    for obj in settings.findall('object'):
        if obj.get('id') not in keep_ids:
            settings.remove(obj)
            continue
        put(obj, 'seam_position', 'back')
        for part in obj.findall('part'):
            if props(part).get('extruder')=='2':
                for key, value in GREEN_CHANGES.items():
                    put(part, key, value)
            if props(part).get('extruder')=='3':
                for key, value in GOLD_CHANGES.items():
                    put(part, key, value)
        assert props(obj).get('wall_loops')=='3'
        assert props(obj).get('sparse_infill_density')=='15%'
    for plate in settings.findall('plate')[:2]:
        settings.remove(plate)
    for i, plate in enumerate(keep_plates):
        put(plate, 'plater_id', i+1)
        put(plate, 'plater_name', '01 Base V9 - costura traseira' if i==0 else '02 AMOSTRA V9 - imprimir primeiro')
    blobs['Metadata/model_settings.config'] = ET.tostring(settings, encoding='utf-8', xml_declaration=True)
    model = blobs['3D/3dmodel.model']
    build = re.search(rb'(<build\b[^>]*>)(.*?)(</build>)', model, re.S)
    assert build
    items = []
    for match in re.finditer(rb'<item\b[^>]*/>', build[2]):
        item = match[0]
        oid = re.search(rb'objectid="([^"]*)"', item)[1].decode()
        if oid not in keep_ids:
            continue
        transform = [float(v) for v in re.search(rb'transform="([^"]*)"', item)[1].split()]
        transform[10] += 307.2
        replacement = ('transform="'+' '.join(format(v, '.12g') for v in transform)+'"').encode()
        item = re.sub(rb'transform="[^"]*"', replacement, item)
        items.append(item)
    assert len(items)==3
    blobs['3D/3dmodel.model'] = model[:build.start()] + build[1] + b'\n  ' + b'\n  '.join(items) + b'\n ' + build[3] + model[build.end():]
    if 'Metadata/filament_sequence.json' in blobs:
        seq = json.loads(blobs['Metadata/filament_sequence.json'])
        seq = {f'plate_{i+1}': seq.get(f'plate_{i+3}', {'nozzle_sequence': [], 'optimal_assignment': [], 'sequence': []}) for i in (0,1)}
        blobs['Metadata/filament_sequence.json'] = json.dumps(seq).encode()
    archive_write(TARGET, blobs)
    native = annotate(TARGET, TARGET, cfg['filament_colour'], PREFIX)
    actual, actual_settings, actual_plates = read_project(TARGET)
    assert [len(p['items']) for p in actual_plates]==[1,2]
    expected_bounds = {
        7: (0.0, 8.32), 8: (8.32, 9.6),
        10: (0.0, 8.32), 11: (8.32, 9.6),
    }
    for old_parts, new_parts in zip(source_meshes[2:], native):
        assert len(old_parts)==len(new_parts)
        for (oid, col, old), (nid, nc, new) in zip(old_parts, new_parts):
            assert (oid, col)==(nid,nc)
            assert np.array_equal(old.faces, new.faces)
            assert np.allclose(old.bounds[:, :2], new.bounds[:, :2], atol=1e-8)
            if oid in expected_bounds:
                assert np.allclose(new.bounds[:, 2], expected_bounds[oid], atol=1e-5)
            else:
                assert np.allclose(old.vertices, new.vertices, atol=1e-8)
    assert all(
        actual[n] == data for n, data in source_blobs.items()
        if n.startswith('3D/') and n not in ('3D/3dmodel.model', '3D/Objects/object_3.model', '3D/Objects/object_4.model')
    )
    assert json.loads(actual['Metadata/project_settings.config'])==cfg
    assert all(props(obj).get('seam_position') == 'back' for obj in actual_settings.findall('object'))
    common = ['--datadir', str(a.work_dir/'user'), '--debug', '2']
    run_cli(a.bambu_bin, common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(a.work_dir/'slice'),'--export-3mf','validation.3mf',str(TARGET)], a.work_dir/'slice.log')
    result=json.loads((a.work_dir/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==2
    reports=[]
    with ZipFile(a.work_dir/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            assert not p.get('warning_message') and p['filament_change_times']==1
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Brim' not in code and '; FEATURE: Support' not in code
            rows=[r for r in paths(code) if r['feature']!='Prime tower']
            assert {r['tool'] for r in rows}=={2,3}
            assert len(set(r['layer'] for r in rows))==60
            assert all(r['tool']==2 for r in rows if r['layer']<=8.32001)
            assert all(r['tool']==3 for r in rows if r['layer']>8.32001)
            gold=[r for r in rows if r['tool']==3]
            green=[r for r in rows if r['tool']==2]
            assert len(set(r['layer'] for r in gold))==8
            assert all(r['speed']<=25.001 for r in gold)
            assert all(abs(r['speed']-20)<.001 for r in gold if r['feature']=='Top surface')
            green_base = [r for r in green if r['layer'] > 4]
            assert not [r for r in green_base if r['feature']=='Top surface']
            assert all(r['speed']<=25.001 for r in green_base if r['feature'] in ('Inner wall', 'Internal solid infill', 'Gap infill', 'Outer wall', 'Top surface'))
            assert any(r['feature']=='Inner wall' for r in gold)
            bridges=[r for r in rows if r['feature']=='Bridge']
            assert bridges and max(r['speed'] for r in bridges)<=20.001
            assert any(abs(r['layer']-6.56)<.0001 for r in bridges)
            report={'plate':i+1,'original_V5_plate':i+3,'estimated_seconds':p['total_predication'],
                'estimated_grams_including_flush_and_tower':sum(f['total_used_g'] for f in p['filaments']),
                'filament_changes':p['filament_change_times'],'warnings':p.get('warning_message'),
                'green_layers':52,
                'green_base_top_surface_removed':not any(r['feature']=='Top surface' for r in green_base),
                'gold_layers':8,'gold_first_z_mm':8.48,'gold_last_z_mm':9.6,
                'green_speeds_by_feature_mm_s':{f:sorted({r['speed'] for r in green if r['feature']==f}) for f in sorted({r['feature'] for r in green})},
                'gold_speeds_by_feature_mm_s':{f:sorted({r['speed'] for r in gold if r['feature']==f}) for f in sorted({r['feature'] for r in gold})},
                'slot_bridge_z_mm':sorted({r['layer'] for r in bridges}),'max_bridge_speed_mm_s':max(r['speed'] for r in bridges),'filaments':p['filaments']}
            reports.append(report)
            if i==0:
                preview(rows, next(m for oid,col,m in native[0] if col==2).bounds)
    report={'project':TARGET.name,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'source':SOURCE.name,
        'printer':cfg['printer_settings_id'],'slicer_version':version,'source_project_confirmed_by_user':True,
        'orientation':'Unchanged from V5: inverted base, green starts on bed, gold face is printed facing up last.',
        'interface_shift_mm':INTERFACE_SHIFT_MM,
        'interface_changes':interface_changes,
        'only_geometry_change':'Move the green/gold boundary down by 0.32 mm; exterior XY shape and final height are unchanged.',
        'QR_front_and_rear_not_included_and_not_modified':True,'structural_walls':3,'sparse_infill':'15% gyroid','layer_height_mm':.16,
        'gold_material_changes':{k:{'old':before_cfg[k][2],'new':cfg[k][2]} for k in ('filament_flow_ratio','nozzle_temperature','nozzle_temperature_initial_layer')},
        'other_material_flow_ratios_unchanged':True,'global_process_changes':GLOBAL_CHANGES,
        'seam_position':'back',
        'green_part_changes':GREEN_CHANGES,'gold_part_changes':GOLD_CHANGES,
        'native_slice_exit':0,'brim':False,'supports':False,'plates':reports,
        'physical_surface_tested':False,'physical_fit_tested':False,'physical_print_started':False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,required=True)
    main(p.parse_args())
