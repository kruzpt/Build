"""Cria e fatia o projeto Bambu Studio V2 em dois pratos."""
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
WORK = Path('/tmp/suporte-cana-mola-v2-bambu')
TARGET = ROOT / 'downloads/suporte-cana-mola-v2-A1-PETG-2-pratos.3mf'


def flatten(kind, name):
    data = json.loads((BBL / kind / f'{name}.json').read_text())
    result = flatten(kind, data['inherits']) if data.get('inherits') else {}
    for included in data.get('include', []):
        result.update(flatten(kind, included))
    result.update(data)
    result.pop('include', None)
    return result


def run(args, log):
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(BIN.parent)
    completed = subprocess.run(
        [str(BIN), '--datadir', str(WORK / 'user'), '--debug', '2', *args],
        cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    (WORK / log).write_text(completed.stdout)
    if completed.returncode:
        raise RuntimeError(f'Bambu CLI {completed.returncode}: {completed.stdout[-2200:]}')


def item(name):
    return {'path': str(HERE / 'stl' / f'{name}.stl'), 'count': 1, 'filaments': [1]}


def main():
    if not BIN.exists() or not BBL.exists():
        raise FileNotFoundError('Bambu Studio CLI/perfis não disponíveis')
    WORK.mkdir(parents=True, exist_ok=True)
    TARGET.parent.mkdir(exist_ok=True)
    machine = flatten('machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten('process', '0.20mm Standard @BBL A1')
    filament = flatten('filament', 'Generic PETG @BBL A1')
    process.update({
        'name': 'Suporte cana V2 PETG estrutural A1 0.4', 'from': 'User',
        'layer_height': '0.20', 'initial_layer_print_height': '0.20',
        'wall_loops': '5', 'top_shell_layers': '6', 'bottom_shell_layers': '6',
        'sparse_infill_density': '35%', 'sparse_infill_pattern': 'gyroid',
        'enable_support': '1', 'support_type': 'tree(auto)',
        'support_threshold_angle': '45', 'support_top_z_distance': '0.2',
        'support_object_xy_distance': '0.35',
        'brim_type': 'no_brim', 'brim_width': '0',
        'curr_bed_type': 'Textured PEI Plate',
        'outer_wall_speed': ['45'], 'top_surface_speed': ['35'],
    })
    filament.update({'name': 'Generic PETG @BBL A1', 'filament_colour': ['#405A65']})
    for name, data in (('machine', machine), ('process', process), ('filament', filament)):
        (WORK / f'{name}.json').write_text(json.dumps(data, indent=2) + '\n')
    plan = {'plates': [
        {'plate_name': '01 - Teste eixo oculto e mola', 'need_arrange': True,
         'objects': [item('cupao_corpo_fixo'), item('cupao_braco_movel')]},
        {'plate_name': '02 - Suporte completo', 'need_arrange': True,
         'objects': [item('corpo_fixo'), item('braco_movel')]},
    ]}
    (WORK / 'assembly.json').write_text(json.dumps(plan, indent=2) + '\n')
    run(['--load-settings', str(WORK / 'machine.json') + ';' + str(WORK / 'process.json'),
         '--load-filaments', str(WORK / 'filament.json'),
         '--load-assemble-list', str(WORK / 'assembly.json'), '--orient', '0',
         '--arrange', '1', '--outputdir', str(WORK), '--export-3mf', 'native.3mf'], 'export.log')
    TARGET.write_bytes((WORK / 'native.3mf').read_bytes())
    with ZipFile(TARGET) as archive:
        assert archive.testzip() is None
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        assert settings['printer_model'] == 'Bambu Lab A1'
        assert settings['nozzle_diameter'] == ['0.4']
        assert settings['wall_loops'] == '5'
        assert settings['brim_type'] == 'no_brim'
        assert not any(name.endswith('.gcode') for name in archive.namelist())
    slice_dir = WORK / 'slice'
    slice_dir.mkdir(exist_ok=True)
    run(['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(slice_dir),
         '--export-3mf', 'validation-only.3mf', str(TARGET)], 'slice.log')
    result = json.loads((slice_dir / 'result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 2
    report = {
        'project': TARGET.name,
        'printer_assumed': 'Bambu Lab A1 0.4 mm',
        'filament_profile': 'Generic PETG @BBL A1',
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
    (HERE / 'bambu-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
