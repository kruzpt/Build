"""Prepare A1 accessories with the revised two-color foliage; reuse the V2 wolf."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from check_anilha_lobito_v5_toolpaths import paths
from generate_anilha_aquela_v2 import ROOT, BROWN, GREEN, BLACK
from generate_anilha_aquela_v3 import FOLDER, PREFIX, WOLF_PROJECT

COLORS = [BROWN, GREEN, BLACK]


def main(args):
    work = args.work_dir; work.mkdir(parents=True, exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    profiles = args.bambu_bin.parent.parent/'resources/profiles/BBL'
    geometry = json.loads((FOLDER/'geometry.json').read_text())
    parts = {p['key']: p for p in geometry['parts']}
    for name, digest in geometry['reused_unchanged_sha256'].items():
        assert hashlib.sha256((ROOT/'downloads'/name).read_bytes()).hexdigest() == digest
    old, _, _ = read_project(ROOT/'downloads/anilha-aquela-v2-ACESSORIOS-A1-04-2-pratos.3mf')
    cfg = json.loads(old['Metadata/project_settings.config'])
    machine = flatten_profile(profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(profiles, 'process', '0.12mm Fine @BBL A1')
    # Carry the reviewed V2 process values forward. Only the multicolor tower
    # is enabled, because the new foliage uses green and black on one plate.
    keys = '''layer_height initial_layer_print_height wall_loops sparse_infill_density
        sparse_infill_pattern top_shell_layers top_shell_thickness bottom_shell_layers
        bottom_shell_thickness top_surface_pattern wall_generator outer_wall_speed
        inner_wall_speed internal_solid_infill_speed top_surface_speed small_perimeter_speed
        bridge_speed overhang_1_4_speed overhang_2_4_speed overhang_3_4_speed overhang_4_4_speed
        default_acceleration outer_wall_acceleration top_surface_acceleration initial_layer_speed
        initial_layer_infill_speed enable_support brim_type brim_width elefant_foot_compensation
        prime_tower_width prime_tower_brim_width prime_tower_extra_rib_length flush_into_infill
        flush_into_support flush_into_objects interface_shells reduce_crossing_wall seam_position
        ironing_type resolution curr_bed_type'''.split()
    process.update({k: cfg[k] for k in keys})
    process.update({'name': 'Aquelá V3 folhas com nervuras A1 0.12', 'from': 'User', 'enable_prime_tower': '1'})
    settings = []
    for key, obj in [('machine', machine), ('process', process)]:
        p = work/f'{key}.json'; p.write_text(json.dumps(obj)); settings.append(str(p))
    filaments = []
    for i, (color, label) in enumerate(zip(COLORS, ['Castanho', 'Verde', 'Preto']), 1):
        obj = flatten_profile(profiles, 'filament', 'Generic PLA @BBL A1')
        obj.update({'name': f'Generic PLA {label} @BBL A1 0.4', 'from': 'User',
                    'filament_colour': [color], 'filament_max_volumetric_speed': ['8'],
                    'filament_scarf_seam_type': ['none']})
        p = work/f'filament-{i}.json'; p.write_text(json.dumps(obj)); filaments.append(str(p))
    def item(key, col, assembly=False, overrides=None):
        o = {'path': str(ROOT/'downloads'/parts[key]['file']), 'count': 1, 'filaments': [col]}
        if assembly: o['assemble_index'] = [1]
        if overrides: o['print_params'] = overrides
        return o
    plan = {'plates': [
        {'plate_name': '01 Anilha castanha - modelo aprovado', 'need_arrange': True,
         'objects': [item('anilha-castanha', 1, overrides={'wall_loops': '4', 'sparse_infill_density': '30%'})]},
        {'plate_name': '02 Folhas V3 - verde e nervuras pretas', 'need_arrange': True,
         'objects': [item('folhas-verdes', 2, True), item('folhas-nervuras-pretas', 3, True)]}]}
    p = work/'assembly.json'; p.write_text(json.dumps(plan))
    common = ['--datadir', str(work/'user'), '--debug', '2']
    run_cli(args.bambu_bin, common+['--load-settings', ';'.join(settings), '--load-filaments', ';'.join(filaments),
        '--load-assemble-list', str(p), '--allow-multicolor-oneplate', '--orient', '0', '--arrange', '1',
        '--outputdir', str(work), '--export-3mf', 'native.3mf'], work/'export.log')
    target = ROOT/'downloads'/f'{PREFIX}-ACESSORIOS-A1-04-AMS-2-pratos.3mf'
    annotate(work/'native.3mf', target, COLORS, PREFIX+'-acessorios')
    blobs, config, plates = read_project(target)
    # Set the parent of the two-volume leaf object to green, avoiding a phantom
    # brown first tool/prime tower on the leaf plate.
    for obj in config.findall('object'):
        if len(obj.findall('part')) == 2:
            meta = obj.find("metadata[@key='extruder']")
            if meta is None: meta = ET.SubElement(obj, 'metadata', key='extruder')
            meta.set('value', '2')
            obj.find("metadata[@key='name']").set('value', 'Folhas Aquelá V3 — verde + nervuras pretas')
    blobs['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
        for name, data in blobs.items(): archive.writestr(name, data)
    with ZipFile(target) as archive: assert archive.testzip() is None
    native = plate_meshes(blobs, config)
    assert [len(p) for p in native] == [1, 2]
    assert [len(p['items']) for p in plates] == [1, 1]
    final_cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert final_cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert final_cfg['layer_height'] == '0.12' and final_cfg['brim_type'] == 'no_brim'
    fits = {}; errors = []
    for key, col in [('anilha-castanha', 1), ('folhas-verdes', 2), ('folhas-nervuras-pretas', 3)]:
        p = parts[key]; ref = trimesh.load(ROOT/'downloads'/p['file'], force='mesh')
        assert hashlib.sha256((ROOT/'downloads'/p['file']).read_bytes()).hexdigest() == p['sha256']
        mesh = next(m for plate in native for _, c, m in plate if c == col)
        assert mesh.is_watertight and mesh.is_winding_consistent
        assert np.array_equal(mesh.faces, ref.faces)
        fit = np.linalg.lstsq(np.c_[ref.vertices, np.ones(len(ref.vertices))], mesh.vertices, rcond=None)[0]
        err = float(np.max(np.linalg.norm(np.c_[ref.vertices, np.ones(len(ref.vertices))]@fit-mesh.vertices, axis=1)))
        assert err < .003 and np.allclose(fit[:3].T@fit[:3], np.eye(3), atol=.00001)
        if p['piece'] in fits: assert np.allclose(fit, fits[p['piece']], atol=.003)
        fits[p['piece']] = fit; errors.append(err)
        assert mesh.bounds[0, :2].min() > 0 and mesh.bounds[1, :2].max() < 253
        assert mesh.bounds[0, 2] >= -.002
    run_cli(args.bambu_bin, common+['--info', '--outputdir', str(work/'reopen'), str(target)], work/'reopen.log')
    run_cli(args.bambu_bin, common+['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(work/'slice'),
        '--export-3mf', 'validation.3mf', str(target)], work/'slice.log')
    result = json.loads((work/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 2
    review = []
    with ZipFile(work/'slice/validation.3mf') as archive:
        for i, plate in enumerate(result['sliced_plates']):
            code = archive.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert not plate.get('warning_message')
            assert len(plate['filaments']) == i+1
            rows = [r for r in paths(code) if r['feature'] != 'Prime tower']
            assert {r['tool'] for r in rows} == ({1} if i == 0 else {2, 3})
            assert not any(r['feature'].startswith(('Support', 'Brim')) for r in rows)
            outer = max(r['speed'] for r in rows if r['feature'] == 'Outer wall')
            top = max(r['speed'] for r in rows if r['feature'] == 'Top surface')
            assert outer <= 25.001 and top <= 18.001
            if i == 1:
                pose = np.eye(4); pose[:3] = fits['folhas'].T
                inverse = np.linalg.inv(pose)
                for r in rows:
                    p = np.array(r['points'])
                    r['points'] = (np.c_[p, np.ones(len(p))]@inverse.T)[:, :3]
                black = [r for r in rows if r['tool'] == 3]
                assert black and min(r['layer'] for r in black) >= 1.6
                assert max(r['layer'] for r in black) >= 2.6
                # Detail reaches all four corners of the foliage, not just its carrier.
                pp = np.concatenate([r['points'] for r in black if r['layer'] > 2])
                assert pp[:, 0].min() < -28 and pp[:, 0].max() > 28
                assert pp[:, 1].max() > 46 and pp[:, 1].min() < 2
                draw_paths(rows)
            review.append({'plate': i+1, 'colors_used': i+1, 'warnings': plate.get('warning_message'),
                'estimated_seconds': plate['total_predication'],
                'estimated_main_grams': sum(f['main_used_g'] for f in plate['filaments']),
                'estimated_total_grams': sum(f['total_used_g'] for f in plate['filaments']),
                'filament_changes': plate['filament_change_times'], 'outer_speed_max_mm_s': outer,
                'top_speed_max_mm_s': top, 'gcode_sha256': hashlib.sha256(code.encode()).hexdigest()})
    report = {'project': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'bambu_version': '02.09.01.70', 'native_export_reopen_slice_exit': [0, 0, 0],
        'printer': final_cfg['printer_settings_id'], 'layer_height_mm': .12, 'first_layer_mm': .2,
        'geometry_and_relative_positions_verified': True, 'max_transform_error_mm': max(errors),
        'black_detail_extrusion_verified': True, 'supports': False, 'brim': False,
        'plates': review, 'wolf_project_unchanged': WOLF_PROJECT,
        'filament_profile': 'Generic PLA, not calibrated for a new spool', 'physical_print_tested': False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


def draw_paths(rows):
    sheet = Image.new('RGB', (1200, 1040), '#f4f6f8'); draw = ImageDraw.Draw(sheet)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    draw.text((35, 25), 'Folhas V3 · percursos reais do Bambu Studio', font=font(32), fill='#23384C')
    scale = 16.5
    for row in sorted(rows, key=lambda r: r['layer']):
        pp = np.array(row['points'])[:, :2]*scale
        pp[:, 0] += 600; pp[:, 1] = 920-pp[:, 1]
        draw.line([tuple(p) for p in pp], fill=COLORS[row['tool']-1], width=round(.4*scale))
    draw.text((35, 985), 'Verde + preto · traços representados com largura de 0,4 mm', font=font(26), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-folhas-percursos.png')


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--bambu-bin', type=Path, required=True)
    p.add_argument('--work-dir', type=Path, required=True)
    main(p.parse_args())
