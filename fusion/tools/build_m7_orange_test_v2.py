"""Prepare a targeted corner-path test from the user's calibrated 3MF.

Only infill_direction and gap_infill_speed are changed. Native slicing checks
verify the paths, not the physical cause or quality of the printed corners.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'm7-tijolo-teste-laranja-v2-cantos'
FOLDER = ROOT / 'fusion/M7TijoloTesteLaranjaV2'
TARGET = ROOT / 'downloads' / f'{PREFIX}-A1-PLA-1-prato.3mf'


def archive(path):
    with ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def paths(code):
    x = y = height = speed = acceleration = 0.
    feature = 'Custom'
    tool = 1
    rows = []
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):
            height = float(line.split(':')[1])
        if line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
        if line.startswith('M204 S'):
            acceleration = float(line[6:].split()[0])
        switch = re.match(r'^M620 S([0-3])A', line) or re.match(r'^T([0-3])\s*$', line)
        if switch:
            tool = int(switch[1]) + 1
        if not re.match(r'^G[0123] ', line):
            continue
        values = {k: float(v) for k, v in re.findall(
            r'([XYEF])(-?(?:\d+(?:\.\d*)?|\.\d+))', line.split(';')[0])}
        nx, ny = values.get('X', x), values.get('Y', y)
        speed = values.get('F', speed)
        if height > 0 and values.get('E', 0) > 0 and (nx, ny) != (x, y) and feature not in ('Custom', 'Prime tower'):
            rows.append(dict(layer=height, feature=feature, a=[x, y], b=[nx, ny],
                             length=math.hypot(nx-x, ny-y), tool=tool,
                             speed_mm_s=speed/60, acceleration_mm_s2=acceleration))
        x, y = nx, ny
    return rows


def slice_project(binary, source, work):
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(binary.parent)
    with (work / 'slice.log').open('w') as log:
        subprocess.run([str(binary), '--datadir', str(work.parent/'bambu-user'),
                        '--debug', '2', '--slice', '0', '--orient', '0', '--arrange', '0',
                        '--outputdir', str(work), '--export-3mf', 'validation.3mf', str(source)],
                       env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads((work/'result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    plate = result['sliced_plates'][0]
    assert not plate.get('warning_message') and plate['filament_change_times'] == 0
    code = archive(work/'validation.3mf')['Metadata/plate_1.gcode'].decode()
    (work/'plate_1.gcode').write_text(code)
    rows = paths(code)
    assert {round(r['layer'], 3) for r in rows} == {.2, .4, .6}
    assert {r['tool'] for r in rows} == {1}
    assert not any('; FEATURE: '+f in code for f in ('Brim', 'Support', 'Prime tower'))
    return plate, rows


def summarize(plate, rows):
    top = [r for r in rows if abs(r['layer']-.6) < 1e-5 and r['feature'] == 'Top surface']
    gap = [r for r in rows if abs(r['layer']-.6) < 1e-5 and r['feature'] == 'Gap infill']
    return dict(estimated_seconds=plate['total_predication'],
                estimated_grams=sum(f['total_used_g'] for f in plate['filaments']),
                warnings=plate.get('warning_message', ''),
                top_line_count=len(top),
                top_line_length_range_mm=[min(r['length'] for r in top), max(r['length'] for r in top)],
                top_speeds_mm_s=sorted({round(r['speed_mm_s'], 4) for r in top}),
                top_first_line=top[0], top_last_line=top[-1],
                edge_gap_paths=gap)


def comparison_image(before, after, target):
    # Draw actual native extrusion segments, not a simulated printed surface.
    canvas = Image.new('RGB', (1340, 890), '#f5f6f8')
    draw = ImageDraw.Draw(canvas)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    fonts = [ImageFont.truetype(font_path, size) for size in (28, 21, 17)]
    draw.text((35, 22), 'M7 — percursos reais do topo, canto inferior direito', fill='#17212e', font=fonts[0])
    draw.text((35, 65), 'Bambu Studio 2.9.1.70 · camada Z = 0,60 mm · janela de 8 × 8 mm', fill='#465468', font=fonts[1])
    colors = {'Top surface':'#e07716', 'Gap infill':'#3266cc', 'Inner wall':'#818b97', 'Outer wall':'#414b57'}
    for panel, rows in enumerate((before, after)):
        left = 35 + panel*665
        draw.text((left, 115), ('Atual: 45°' if panel == 0 else 'V2: 0° + preenchimento de lacunas a 25 mm/s'), fill='#17212e', font=fonts[1])
        box = (left, 160, left+600, 760)
        plot = Image.new('RGB', (600, 600), 'white')
        pd = ImageDraw.Draw(plot)
        top = [r for r in rows if r['layer'] == .6 and r['feature'] == 'Top surface']
        # Same printer XY in both files; magnify the lower-right corner.
        def xy(p): return ((p[0]-142.0)*75, 600-(p[1]-93.5)*75)
        for r in rows:
            if r['layer'] == .6 and r['feature'] in colors:
                pd.line([xy(r['a']), xy(r['b'])], fill=colors[r['feature']], width=3)
        first = xy(top[0]['a'])
        pd.ellipse((first[0]-7, first[1]-7, first[0]+7, first[1]+7), fill='#bd253b')
        canvas.paste(plot, box[:2])
        draw.rectangle(box, outline='#bbc4ce', width=1)
        caption = ('Primeira linha do topo: 0,48 mm' if panel == 0 else 'Linhas do topo: cerca de 43,94 mm')
        draw.text((left, 775), caption, fill='#17212e', font=fonts[1])
    draw.text((35, 820), 'Laranja: topo · azul: lacunas · cinzento: paredes · ponto vermelho: início do topo', fill='#465468', font=fonts[2])
    draw.text((35, 851), 'A alteração dos percursos está verificada. A qualidade física dos cantos ainda não foi testada.', fill='#465468', font=fonts[2])
    canvas.save(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--bambu-bin', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    assert args.source.resolve() != TARGET.resolve(), 'Preserve the user reference file.'
    blobs = archive(args.source)
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['filament_flow_ratio'][0] == '0.931'
    assert cfg['filament_flow_ratio'][1] == '0.9702'
    assert cfg['infill_wall_overlap'] == '10%'
    assert cfg['filament_scarf_seam_type'][0] == 'none'
    assert cfg['wall_loops'] == '3' and cfg['infill_direction'] == '45'
    changes = {'infill_direction': {'before': cfg['infill_direction'], 'after': '0'},
               'gap_infill_speed': {'before': cfg['gap_infill_speed'], 'after': ['25']}}
    original_cfg = dict(cfg)
    cfg['infill_direction'] = '0'
    cfg['gap_infill_speed'] = ['25']
    for k in cfg.keys() | original_cfg.keys():
        if k not in changes:
            assert cfg[k] == original_cfg[k]
    FOLDER.mkdir(exist_ok=True)
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as z:
        for n, data in blobs.items():
            if n == 'Metadata/project_settings.config':
                data = json.dumps(cfg, indent=2).encode()
            z.writestr(n, data)
    output = archive(TARGET)
    assert set(output) == set(blobs)
    assert all(data == output[n] for n, data in blobs.items() if n != 'Metadata/project_settings.config')
    a, ar = slice_project(args.bambu_bin, args.source, args.work_dir/'reference')
    b, br = slice_project(args.bambu_bin, TARGET, args.work_dir/'candidate')
    assert len(a['objects']) == len(b['objects']) == 1
    bbox = b['objects'][0]['bbox']
    dimensions = [bbox[k] for k in ('width', 'depth', 'height')]
    assert all(abs(v-t) < .001 for v, t in zip(dimensions, (46.4, 66.4, .6)))
    sa, sb = summarize(a, ar), summarize(b, br)
    assert sa['top_line_length_range_mm'][0] < 1
    assert sb['top_line_length_range_mm'][0] > 43
    assert sb['top_line_length_range_mm'][1] - sb['top_line_length_range_mm'][0] < .01
    assert sb['top_speeds_mm_s'] == [25.]
    assert len(sb['edge_gap_paths']) == 2
    assert all(abs(r['speed_mm_s']-25) < .01 for r in sb['edge_gap_paths'])
    assert abs(sa['estimated_grams']-sb['estimated_grams']) < .01
    first_walls = lambda rows: [r for r in rows if r['feature'] in ('Inner wall', 'Outer wall')]
    assert first_walls(ar) == first_walls(br), 'Wall and seam paths must remain unchanged.'
    report = dict(project=TARGET.name, source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                  sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                  bambu_version='02.09.01.70', native_slice_exit=0,
                  physical_print_tested=False, diagnostic_not_guaranteed_fix=True,
                  dimensions_mm=dimensions, layers_mm=[.2, .4, .6], wall_loops=3,
                  geometry_and_seam_paint_preserved_byte_for_byte=True,
                  only_settings_changes=changes,
                  orange_flow_ratio=.931, gold_flow_ratio=.9702, overlap_percent=10,
                  brim=False, supports=False, prime_tower=False,
                  user_confirmed_flow_dynamics_calibration_enabled=True,
                  reference=sa, candidate=sb,
                  caveat='The infill direction also rotates the fill of the preceding layers. '
                         'Longer strokes remove the short corner fan but do not establish the physical cause.')
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    comparison_image(ar, br, ROOT/'designs'/f'{PREFIX}-percursos.png')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
