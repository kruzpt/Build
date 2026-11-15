"""Create an editable, unsliced A1 project with smooth board chairs.

The first plate is a small proof of the face-down text. The source CAD and
neutral STL exports remain useful if another printer is selected later.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'fusion' / 'tools'))
from build_pintos_pla_3mf import flatten_profile, read_project  # noqa: E402

COLORS = [('#F0E4CF', 'creme'), ('#4F2E1C', 'texto-castanho'),
          ('#AD7147', 'madeira')]


def assembly(style='boards'):
    assert style == 'boards'
    def item(name, filament, count=1, group=False):
        p = {'path': str(HERE / 'stl' / (name + '.stl')),
             'count': count, 'filaments': [filament]}
        if group:
            p['assemble_index'] = [1]
        return p

    return {'plates': [
        {'plate_name': '01 AMOSTRA texto pequeno - imprimir primeiro',
         'need_arrange': True, 'objects': [
             item('text_coupon_cream', 1, group=True),
             item('text_coupon_brown', 2, group=True)]},
        {'plate_name': '02 Base redonda creme 236 mm',
         'need_arrange': True, 'objects': [item('base', 1)]},
        {'plate_name': '03 Arvore bicolor - face do texto no prato',
         'need_arrange': True, 'objects': [
             item('tree_cream', 1, group=True),
             item('tree_brown', 2, group=True)]},
        {'plate_name': '04 Cadeiras V4 tabuas lisas - quatro laterais',
         'need_arrange': True, 'objects': [
             item(f'{style}_side_A', 3, count=2),
             item(f'{style}_side_B', 3, count=2)]},
        {'plate_name': '05 Cadeiras V4 tabuas lisas - travessas',
         'need_arrange': True, 'objects':
             [item('boards_back', 3, count=6),
              item('boards_seat', 3, count=4)] +
             [item(f'{style}_bar', 3, count=2)]},
    ]}


def run(binary, args, log):
    with log.open('w') as f:
        completed = subprocess.run([str(binary), *args], stdout=f,
                                   stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeError(f'Bambu Studio returned {completed.returncode}: {log}')


def build(style, binary, work):
    profiles = binary.parent.parent / 'resources/profiles/BBL'
    work.mkdir(parents=True, exist_ok=True)
    machine = flatten_profile(profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(profiles, 'process', '0.12mm Fine @BBL A1')
    process.update({
        'name': 'Natal memoria V4 tabuas lisas 0.12 A1 PLA', 'from': 'User',
        'curr_bed_type': 'High Temp Plate', 'brim_type': 'no_brim',
        'enable_support': '0', 'enable_prime_tower': '1',
        'wall_generator': 'arachne', 'wall_loops': '3',
        'outer_wall_speed': '25', 'initial_layer_speed': '20',
        'initial_layer_print_height': '0.2',
        'top_shell_layers': '6', 'bottom_shell_layers': '5',
        'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
        'elefant_foot_compensation': '0.15',
    })
    (work/'machine.json').write_text(json.dumps(machine))
    (work/'process.json').write_text(json.dumps(process))
    filaments = []
    for i, (color, label) in enumerate(COLORS, 1):
        obj = flatten_profile(profiles, 'filament', 'Generic PLA @BBL A1')
        obj.update({'name': 'Generic PLA @BBL A1', 'from': 'User',
                    'filament_colour': [color],
                    'filament_max_volumetric_speed': ['8']})
        path = work/f'filament-{i}.json'
        path.write_text(json.dumps(obj))
        filaments.append(str(path))
    (work/'assembly.json').write_text(json.dumps(assembly(style), indent=2))
    common = ['--datadir', str(work/'user'), '--debug', '2']
    run(binary, common + [
        '--load-settings', str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments', ';'.join(filaments),
        '--load-assemble-list', str(work/'assembly.json'),
        '--allow-multicolor-oneplate', '--orient', '0', '--arrange', '1',
        '--outputdir', str(work), '--export-3mf', 'native.3mf'],
        work/'export.log')
    target = ROOT/'downloads'/'natal-memoria-cadeiras-v4-tabuas-lisas-A1-PLA.3mf'
    target.parent.mkdir(exist_ok=True)
    target.write_bytes((work/'native.3mf').read_bytes())
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        assert not any(n.endswith('.gcode') for n in archive.namelist())
    _, _, plates = read_project(target)
    assert len(plates) == 5
    assert [len(p['items']) for p in plates] == [1, 1, 1, 4, 12]
    for plate in plates:
        for item in plate['items']:
            mesh = item['mesh']
            assert mesh.is_watertight and mesh.is_winding_consistent
            assert abs(mesh.bounds[0, 2]) < .002
            assert mesh.bounds[0, :2].min() >= 0
            assert mesh.bounds[1, :2].max() <= 256
    run(binary, common + ['--info', '--outputdir', str(work/'reopen'),
                          str(target)], work/'reopen.log')
    run(binary, common + ['--slice', '0', '--orient', '0', '--arrange', '0',
                          '--outputdir', str(work/'slicing'),
                          '--export-3mf', 'validation-only.3mf', str(target)],
        work/'slice.log')
    report = json.loads((work/'slicing'/'result.json').read_text())
    assert report['return_code'] == 0
    assert len(report['sliced_plates']) == 5
    assert all(not p.get('warning_message') for p in report['sliced_plates'])
    layer_counts = []
    with ZipFile(work/'slicing'/'validation-only.3mf') as sliced:
        for plate_id in range(1,6):
            gcode = sliced.read(f'Metadata/plate_{plate_id}.gcode').decode()
            markers = re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',gcode)
            assert markers and markers[-1][0] == markers[-1][1]
            layer_counts.append(int(markers[-1][1]))
    # Smooth chairs end at the plain base thickness, without extra relief layers.
    assert layer_counts[3] <= 23
    assert layer_counts[4] <= 21
    validation = {
        'printer': 'Bambu Lab A1 0.4 nozzle', 'material': 'PLA',
        'plate': 'Smooth PEI / High Temp Plate', 'layer_mm': .12,
        'physical_fit_tested': False, 'text_coupon_printed': False,
        'actual_gcode_layer_counts': layer_counts,
        'project': str(target), 'plates': [
            {'name': plan['plate_name'],
             'seconds': result['total_predication'],
             'grams': sum(f['total_used_g'] for f in result['filaments']),
             'filament_changes': result['filament_change_times']}
            for plan, result in zip(assembly(style)['plates'], report['sliced_plates'])],
    }
    (HERE/f'validation-{style}.json').write_text(json.dumps(validation, indent=2)+'\n')
    print(f'{style}: {target}; 5 plates sliced without warnings', flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bambu-bin', type=Path, required=True)
    p.add_argument('--work-dir', type=Path)
    args = p.parse_args()
    for style in ('boards',):
        work = (args.work_dir or Path(tempfile.mkdtemp(prefix='natal-memoria-'))) / style
        build(style, args.bambu_bin, work)


if __name__ == '__main__':
    main()
