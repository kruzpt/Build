"""Refine fine lettering in the V7 stand without changing model geometry."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'downloads/universo-saber-suporte-v7-perfil-premium-A1-AMS-2-pratos.3mf'
TARGET = ROOT / 'downloads/universo-saber-suporte-v8-letras-premium-A1-AMS-2-pratos.3mf'
FOLDER = ROOT / 'fusion/UniversoSaberStandV8Letras'
PREVIEW = ROOT / 'designs/universo-saber-suporte-v8-letras-premium-pratos.png'
BIN = Path('/tmp/bambu-studio-2.9.1/squashfs-root/bin/bambu-studio')
WORK = Path('/tmp/universo-v8-letras-bambu')


def read_zip(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        return {name: z.read(name) for name in z.namelist()}


def modify_profile():
    blobs = read_zip(SOURCE)
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    cfg.update({
        'print_settings_id': 'Universo V8 letras premium A1 0.20',
        'gap_infill_speed': ['25'],
        'internal_solid_infill_speed': ['60'],
        'outer_wall_acceleration': ['1000'],
        'small_perimeter_speed': ['20'],
        'small_perimeter_threshold': ['10'],
    })
    # The V7 white/blue filament settings and ironed white-before-blue sequence
    # are inherited unchanged. Only the fine-geometry process speeds change.
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()

    root = etree.fromstring(blobs['Metadata/model_settings.config'])
    objects = root.findall('object')
    assert len(objects) == 2
    assembled = next(o for o in objects if len(o.findall('part')) == 2)
    base = next(o for o in objects if len(o.findall('part')) == 1)
    blue = next(p for p in assembled.findall('part') if
                any(m.get('key') == 'extruder' and m.get('value') == '2'
                    for m in p.findall('metadata')))
    etree.SubElement(blue, 'metadata', key='top_one_wall_type', value='not apply')
    for i, plate in enumerate(root.findall('plate'), 1):
        meta = plate.find("metadata[@key='plater_name']")
        assert meta is not None
        meta.set('value', '01 - V8 Branco completo e letras azuis' if i == 1
                 else '02 - V8 Base azul acabamento premium')
    blobs['Metadata/model_settings.config'] = etree.tostring(
        root, encoding='utf-8', xml_declaration=True)

    pictures = []
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    for i, title in enumerate(('01 - V8 Branco completo e letras azuis',
                               '02 - V8 Base azul acabamento premium'), 1):
        image = Image.open(io.BytesIO(blobs[f'Metadata/plate_{i}.png'])).convert('RGB')
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, 58), fill='white')
        draw.text((20, 16), title, font=font, fill='#17385B')
        stream = io.BytesIO()
        image.save(stream, format='PNG')
        blobs[f'Metadata/plate_{i}.png'] = stream.getvalue()
        stream = io.BytesIO()
        image.resize((128, 145)).save(stream, format='PNG')
        blobs[f'Metadata/plate_{i}_small.png'] = stream.getvalue()
        pictures.append(image)
    overview = Image.new('RGB', (pictures[0].width * 2, pictures[0].height), 'white')
    for i, picture in enumerate(pictures):
        overview.paste(picture, (i * picture.width, 0))
    overview.save(PREVIEW)

    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as z:
        for name, blob in blobs.items():
            z.writestr(name, blob)
    check = read_zip(TARGET)
    assert all(check[name] == blob for name, blob in blobs.items())
    assert {name: hashlib.sha256(blob).hexdigest()
            for name, blob in check.items() if name.startswith('3D/')} == {
            name: hashlib.sha256(blob).hexdigest()
            for name, blob in read_zip(ROOT / 'downloads/universo-saber-suporte-v6-A1-AMS-2-pratos.3mf').items() if name.startswith('3D/')}
    return cfg


def run_cli(args, log):
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(BIN.parent)
    with log.open('w') as f:
        p = subprocess.run([str(BIN), '--datadir', str(WORK/'user'), '--debug', '2', *args],
                           cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError(f'Bambu Studio exit {p.returncode}: {log}')


def layer_sections(code):
    starts = [(int(m.group(1)), m.start()) for m in re.finditer(
        r'; layer num/total_layer_count: (\d+)/\d+', code)]
    return {n: code[start:end] for (n, start), (_, end) in
            zip(starts, starts[1:] + [(0, len(code))])}


def validate(cfg):
    WORK.mkdir(parents=True, exist_ok=True)
    run_cli(['--info', '--outputdir', str(WORK/'reopen'), str(TARGET)], WORK/'reopen.log')
    sliced = WORK/'sliced'
    sliced.mkdir(exist_ok=True)
    run_cli(['--slice', '0', '--orient', '0', '--arrange', '0',
             '--outputdir', str(sliced), '--export-3mf', 'validation-only.3mf',
             str(TARGET)], WORK/'slice.log')
    result = json.loads((sliced/'result.json').read_text())
    assert result['return_code'] == 0
    assert len(result['sliced_plates']) == 2
    assert all(not p.get('warning_message') for p in result['sliced_plates'])
    with ZipFile(sliced/'validation-only.3mf') as z:
        white_code = z.read('Metadata/plate_1.gcode').decode()
        base_code = z.read('Metadata/plate_2.gcode').decode()
    white_layers = layer_sections(white_code)
    base_layers = layer_sections(base_code)
    assert len(white_layers) == 39 and len(base_layers) == 50
    last_white = white_layers[35]
    assert '; FEATURE: Top surface' in last_white
    assert '; FEATURE: Sparse infill' not in last_white
    assert '; FEATURE: Ironing' in last_white
    features = re.findall(r'(?m)^; FEATURE: (.+)$', last_white)
    assert features[-1] == 'Ironing', features[-5:]
    assert 'T1\n' in white_layers[36]
    assert white_code.index('; FEATURE: Ironing', white_code.index(
        '; layer num/total_layer_count: 35/39')) < white_code.index('T1\n')
    assert all('; FEATURE: Ironing' not in white_layers[n] for n in range(36, 40))
    assert '; FEATURE: Gap infill' in white_layers[39]
    assert '; FEATURE: Top surface' in white_layers[39]
    assert '; FEATURE: Outer wall' in white_layers[39]
    gap = re.search(r'; FEATURE: Gap infill\n.*?G1 F(\d+)', white_layers[39], re.S)
    assert gap and int(gap.group(1)) == 1500, gap.group(0) if gap else 'no gap fill'
    assert sum('; FEATURE: Ironing' in section for section in base_layers.values()) >= 1
    assert result['sliced_plates'][0]['filament_change_times'] == 1
    assert result['sliced_plates'][1]['filament_change_times'] == 0
    for code in (white_code, base_code):
        assert '; FEATURE: Support' not in code
    report = {
        'project': TARGET.name,
        'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        'geometry_identical_to_v6': True,
        'machine': 'Bambu Lab A1 0.4 nozzle',
        'layer_mm': 0.2,
        'white_nozzle_c_provisional': 205,
        'white_flow_ratio': 0.98,
        'blue_profile': 'Generic PLA from V6, not separately calibrated',
        'white_top_complete_before_blue': True,
        'white_top_layer': 35,
        'blue_first_layer': 36,
        'white_ironing_before_color_change': True,
        'blue_relief_ironing': False,
        'blue_base_ironing': True,
        'letter_gap_fill_mm_s': 25,
        'short_perimeter_mm_s': 20,
        'outer_wall_acceleration_mm_s2': 1000,
        'letter_top_one_wall': False,
        'brim': False,
        'physical_finish_tested': False,
        'plates': [{
            'name': '01 - Placa branca e relevo azul' if i == 0 else '02 - Base azul',
            'layers': 39 if i == 0 else 50,
            'filament_changes': p['filament_change_times'],
            'estimated_minutes': round(p['total_predication']/60, 1),
            'estimated_g': round(sum(f['total_used_g'] for f in p['filaments']), 2),
            'warnings': p['warning_message'],
        } for i, p in enumerate(result['sliced_plates'])],
    }
    FOLDER.mkdir(exist_ok=True)
    (FOLDER/'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    config = modify_profile()
    validate(config)
