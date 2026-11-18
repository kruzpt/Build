"""Cria o 3MF V3 em três pratos: cupão, estrutura e TPU."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INSTALL = Path('/tmp/bambu291/squashfs-root')
BBL = INSTALL / 'resources/profiles/BBL'
BIN = INSTALL / 'bin/bambu-studio'
WORK = Path('/tmp/suporte-cana-mola-v3-bambu')
TARGET = ROOT / 'downloads/suporte-cana-mola-v3-A1-PETG-TPU-3-pratos.3mf'


def flatten(kind, name):
    data = json.loads((BBL / kind / f'{name}.json').read_text())
    result = flatten(kind, data['inherits']) if data.get('inherits') else {}
    for included in data.get('include', []):
        result.update(flatten(kind, included))
    result.update(data); result.pop('include', None)
    return result


def run(args, log):
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(BIN.parent)
    done = subprocess.run([str(BIN), '--datadir', str(WORK / 'user'), '--debug', '2', *args],
                          cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    (WORK / log).write_text(done.stdout)
    if done.returncode:
        raise RuntimeError(f'Bambu Studio {done.returncode}: {done.stdout[-2500:]}')


def item(name, filament):
    return {'path': str(HERE / 'stl' / f'{name}.stl'), 'count': 1,
            'filaments': [filament]}


def main():
    if not BIN.exists() or not BBL.exists():
        raise FileNotFoundError('Bambu Studio/perfis indisponíveis')
    WORK.mkdir(parents=True, exist_ok=True); TARGET.parent.mkdir(exist_ok=True)
    machine = flatten('machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten('process', '0.20mm Standard @BBL A1')
    petg = flatten('filament', 'Generic PETG @BBL A1')
    tpu = flatten('filament', 'Generic TPU @BBL A1')
    process.update({
        'name': 'Suporte cana V3 PETG TPU prototipo A1 0.4', 'from': 'User',
        'layer_height': '0.20', 'initial_layer_print_height': '0.20',
        'wall_loops': '5', 'top_shell_layers': '6', 'bottom_shell_layers': '6',
        'sparse_infill_density': '35%', 'sparse_infill_pattern': 'gyroid',
        'enable_support': '1', 'support_type': 'tree(auto)',
        'support_threshold_angle': '45', 'support_top_z_distance': '0.2',
        'support_object_xy_distance': '0.35',
        'brim_type': 'no_brim', 'brim_width': '0',
        'curr_bed_type': 'Textured PEI Plate',
        'outer_wall_speed': ['40'], 'top_surface_speed': ['30'],
        'outer_wall_acceleration': ['900'], 'top_surface_acceleration': ['700'],
    })
    petg.update({'name': 'Generic PETG @BBL A1', 'filament_colour': ['#34454D']})
    tpu.update({'name': 'Generic TPU @BBL A1 - usar bobina externa',
                'filament_colour': ['#168BD2']})
    for name, data in (('machine', machine), ('process', process),
                       ('petg', petg), ('tpu', tpu)):
        (WORK / f'{name}.json').write_text(json.dumps(data, indent=2) + '\n')

    plan = {'plates': [
        {'plate_name': '01 - Cupao eixo oculto e mola - PETG', 'need_arrange': True,
         'objects': [item('cupao_corpo_fixo', 1), item('cupao_braco_movel', 1)]},
        {'plate_name': '02 - Estrutura completa - PETG', 'need_arrange': True,
         'objects': [item('corpo_fixo', 1), item('braco_movel', 1)]},
        {'plate_name': '03 - Insertos de contacto - TPU bobina externa', 'need_arrange': True,
         'objects': [item('tpu_superior', 2), item('tpu_inferior', 2)]},
    ]}
    (WORK / 'assembly.json').write_text(json.dumps(plan, indent=2) + '\n')
    run(['--load-settings', str(WORK/'machine.json') + ';' + str(WORK/'process.json'),
         '--load-filaments', str(WORK/'petg.json') + ';' + str(WORK/'tpu.json'),
         '--load-assemble-list', str(WORK/'assembly.json'), '--orient', '0',
         '--arrange', '1', '--outputdir', str(WORK), '--export-3mf', 'native.3mf'], 'export.log')
    TARGET.write_bytes((WORK / 'native.3mf').read_bytes())
    with ZipFile(TARGET) as archive:
        assert archive.testzip() is None
        cfg = json.loads(archive.read('Metadata/project_settings.config'))
        assert cfg['printer_model'] == 'Bambu Lab A1'
        assert cfg['wall_loops'] == '5' and cfg['brim_type'] == 'no_brim'
        assert not any(name.endswith('.gcode') for name in archive.namelist())

    sliced = WORK / 'slice'; sliced.mkdir(exist_ok=True)
    run(['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(sliced),
         '--export-3mf', 'validation-only.3mf', str(TARGET)], 'slice.log')
    result = json.loads((sliced / 'result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 3
    report = {
        'project': TARGET.name,
        'printer_assumed': 'Bambu Lab A1 0.4 mm',
        'structural_filament': 'Generic PETG @BBL A1',
        'liner_filament': 'Generic TPU @BBL A1; bobina externa, não AMS Lite',
        'physical_fit_tested': False,
        'spring_tested': False,
        'hidden_snap_axle_tested': False,
        'plates': [{
            'name': plan['plates'][i]['plate_name'],
            'warnings': plate.get('warning_message'),
            'estimated_seconds': plate.get('total_predication'),
            'estimated_grams': sum(f.get('total_used_g', 0) for f in plate.get('filaments', [])),
        } for i, plate in enumerate(result['sliced_plates'])],
    }
    assert all(not p['warnings'] for p in report['plates'])
    (HERE / 'bambu-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
