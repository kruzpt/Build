"""Build a reusable user filament preset from the calibrated orange material."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/FilamentLibraryA1'
NAME = 'SUNLU PLA+ Laranja 0.931 @BBL A1 0.4'
PARENT = 'Generic PLA @BBL A1'
PRESET = ROOT / 'downloads/sunlu-pla-plus-laranja-0931-A1-04.json'
PROJECT = ROOT / 'downloads/gallardo-tomas-v4-A1-04-laranja-0931-suportes-ON.3mf'
MATERIAL_SOURCE = ROOT / 'downloads/m7-tijolo-v9-relevos-em-linhas-A1-AMS-2-pratos.3mf'
CAR_SOURCE = ROOT / 'downloads/gallardo-tomas-v4-A1-04-texto-direito-suportes-ON.3mf'
META = {'name', 'type', 'from', 'setting_id', 'inherits', 'instantiation', 'filament_id', 'version',
        'filament_settings_id', 'compatible_printers', 'compatible_printers_condition',
        'compatible_prints', 'compatible_prints_condition'}


def png(im):
    s = io.BytesIO(); im.save(s, format='PNG'); return s.getvalue()


def main(a):
    FOLDER.mkdir(exist_ok=True)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    (a.work_dir / 'slice').mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    parent = flatten_profile(a.profiles, 'filament', PARENT)
    with ZipFile(MATERIAL_SOURCE) as z: material = json.loads(z.read('Metadata/project_settings.config'))
    preset = {}
    for key, value in parent.items():
        if key in META: continue
        if key in material:
            saved = material[key]
            if isinstance(saved, list) and len(saved) == 4: value = [saved[0]]
            elif isinstance(saved, list) and len(saved) == 1: value = saved
            elif isinstance(value, list) and not isinstance(saved, list): value = [str(saved)]
        preset[key] = value
    color = material['filament_colour'][0]
    preset.update(type='filament', name=NAME, **{'from': 'User'}, inherits=PARENT,
                  version='2.8.2.61', instantiation='true', filament_settings_id=[NAME],
                  compatible_printers=['Bambu Lab A1 0.4 nozzle'], compatible_printers_condition='',
                  compatible_prints=[], compatible_prints_condition='',
                  default_filament_colour=[color], filament_vendor=['SUNLU'])
    assert preset['filament_flow_ratio'] == ['0.931'] and preset['nozzle_temperature'] == ['220']
    assert preset['textured_plate_temp'] == ['65'] and preset['filament_max_volumetric_speed'] == ['8']
    PRESET.write_text(json.dumps(preset, ensure_ascii=False, indent=2) + '\n')
    # Native loading verifies the real filament schema and effective parameters.
    run_cli(a.bambu_bin, ['--datadir', str(a.work_dir / 'user'), '--debug', '3', '--load-filaments', str(PRESET),
                         '--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir),
                         '--export-3mf', 'loaded.3mf', str(CAR_SOURCE)], a.work_dir / 'load.log')
    loaded, _, _ = read_project(a.work_dir / 'loaded.3mf')
    effective = json.loads(loaded['Metadata/project_settings.config'])
    for key in ('filament_flow_ratio', 'nozzle_temperature', 'textured_plate_temp',
                'fan_min_speed', 'fan_max_speed', 'filament_max_volumetric_speed'):
        assert effective[key] == preset[key], key
    b, settings, plates = read_project(CAR_SOURCE)
    original = dict(b)
    cfg = json.loads(b['Metadata/project_settings.config'])
    previous = dict(cfg)
    for key in preset:
        if key not in META and key in effective: cfg[key] = effective[key]
    cfg['filament_settings_id'] = [NAME]
    cfg['filament_colour'] = [color]
    cfg['default_filament_colour'] = [color]
    cfg['inherits_group'][1] = PARENT
    cfg['different_settings_to_system'][1] = ';'.join(sorted(k for k in preset if k not in META))
    for key in ('enable_support', 'support_style', 'support_type', 'nozzle_diameter', 'print_settings_id',
                'layer_height', 'wall_generator', 'brim_type', 'overhang_2_4_speed'):
        assert cfg[key] == previous[key], key
    b['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    assert all(b[n] == value for n, value in original.items() if n.startswith('3D/'))
    assert b['Metadata/model_settings.config'] == original['Metadata/model_settings.config']
    # Use an orange thumbnail without changing any mesh or object placement.
    im = Image.new('RGB', (700, 500), '#f5f7fa'); d = ImageDraw.Draw(im)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    d.text((25, 22), 'Gallardo TOMAS V4 - Laranja', font=font(28), fill='#17344a')
    mesh = plates[0]['items'][0]['mesh']; lo = mesh.bounds[0]
    for tri in mesh.triangles:
        d.polygon([(30 + (p[0] - lo[0]) * 4.2, 300 - (p[1] - lo[1]) * 4.2) for p in tri], fill=color)
    d.text((25, 365), 'SUNLU PLA+ / fluxo 0,931 / 220 C', font=font(25), fill='#17344a')
    d.text((25, 410), 'A1 0,4 / Tree Slim ON', font=font(25), fill='#17344a')
    for path, size in [('Metadata/plate_1.png', (700, 500)), ('Metadata/plate_1_small.png', (140, 100)),
                       ('Auxiliaries/.thumbnails/thumbnail_3mf.png', (700, 500)),
                       ('Auxiliaries/.thumbnails/thumbnail_middle.png', (700, 500)),
                       ('Auxiliaries/.thumbnails/thumbnail_small.png', (140, 100))]:
        b[path] = png(im.resize(size, Image.Resampling.LANCZOS))
    with ZipFile(PROJECT, 'w', ZIP_DEFLATED) as z:
        for name, data in b.items(): z.writestr(name, data)
    run_cli(a.bambu_bin, ['--datadir', str(a.work_dir / 'user'), '--debug', '2', '--slice', '0',
                         '--orient', '0', '--arrange', '0', '--outputdir', str(a.work_dir / 'slice'),
                         '--export-3mf', 'validation.3mf', str(PROJECT)], a.work_dir / 'slice.log')
    result = json.loads((a.work_dir / 'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    p = result['sliced_plates'][0]; assert not p['warning_message']
    with ZipFile(a.work_dir / 'slice/validation.3mf') as z: code = z.read('Metadata/plate_1.gcode').decode()
    rows = paths(code)
    assert set(r['tool'] for r in rows) == {1}
    assert any(r['feature'].startswith('Support') for r in rows)
    assert '; FEATURE: Brim' not in code
    actual_outer_max = max(r['speed'] for r in rows if r['feature'] == 'Outer wall')
    assert actual_outer_max <= 30.001
    report = dict(profile_name=NAME, profile_file=PRESET.name, profile_sha256=hashlib.sha256(PRESET.read_bytes()).hexdigest(),
                  preset_kind='User filament JSON', parent=PARENT, compatible_printers=preset['compatible_printers'],
                  flow_ratio=.931, nozzle_c=220, textured_pei_c=65, maximum_volumetric_speed_mm3_s=8,
                  color_hex=color, source_project=MATERIAL_SOURCE.name, source_material_slot=1,
                  official_import_format_reviewed=True, native_profile_load_exit=0,
                  windows_library_install_performed=False, gui_import_test_performed=False,
                  project=PROJECT.name, project_sha256=hashlib.sha256(PROJECT.read_bytes()).hexdigest(),
                  all_3d_geometry_placement_and_object_settings_bytes_unchanged=True,
                  support_enabled_global=cfg['enable_support'],
                  support_enabled_object=settings.find("object/metadata[@key='enable_support']").get('value'),
                  native_slice_exit=0, warnings=p['warning_message'], actual_outer_wall_max_speed_mm_s=actual_outer_max,
                  estimated_seconds=p['total_predication'],
                  estimated_grams_including_support=sum(f['total_used_g'] for f in p['filaments']),
                  physical_print_tested=False, dynamic_flow_K_not_claimed_as_saved_in_filament=True)
    (FOLDER / 'orange-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('profile_name', 'project', 'estimated_seconds', 'estimated_grams_including_support')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args())
