"""Isolate the unchanged M7 facade and validate a conservative surface trial."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from build_pintos_pla_3mf import read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from generate_m7_prototypes_v1 import ROOT, WHITE, BLUE, CYAN

PREFIX = 'm7-casa-v3-fachada'
FOLDER = ROOT / 'fusion/M7CasaFachadaV3'
WHITE_SETTINGS = {
    'top_surface_pattern': 'monotonic',
    'top_surface_speed': '25',
    'top_one_wall_type': 'not apply',
}


def project(target, trial):
    source = ROOT / 'downloads/m7-casa-v2-A1-AMS-3-pratos.3mf'
    blobs, config, _ = read_project(source)
    keep = None
    for obj in config.findall('object'):
        if any('fachada-branca' in m.get('value', '') for m in obj.findall("part/metadata[@key='source_file']")):
            keep = obj
        else:
            config.remove(obj)
    assert keep is not None and len(keep.findall('part')) == 2
    key = keep.get('id')
    for p in config.findall('plate')[1:]:
        config.remove(p)
    plate = config.find('plate')
    for instance in plate.findall('model_instance'):
        if instance.find("metadata[@key='object_id']").get('value') != key:
            plate.remove(instance)
    plate.find("metadata[@key='plater_name']").set('value', '01 Fachada branca e frase - acabamento V3')
    def build_item(m):
        return m.group(0) if re.search(rb'\bobjectid="' + key.encode() + rb'"', m.group(0)) else b''
    # Keep namespace declarations and all component coordinates byte for byte.
    blobs['3D/3dmodel.model'] = re.sub(rb'<item\b[^>]*/>', build_item, blobs['3D/3dmodel.model'])
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    if trial:
        cfg.update({'interface_shells': '1', 'flush_into_infill': '0', 'flush_into_objects': '0',
                    'flush_into_support': '0', 'enable_prime_tower': '1',
                    'print_settings_id': 'M7 fachada V3 - branco completo antes do azul'})
        ET.SubElement(keep, 'metadata', key='reduce_crossing_wall', value='1')
        white = next(p for p in keep.findall('part') if 'fachada-branca' in p.find("metadata[@key='source_file']").get('value'))
        for k, v in WHITE_SETTINGS.items():
            ET.SubElement(white, 'metadata', key=k, value=v)
    blobs['Metadata/project_settings.config'] = json.dumps(cfg, indent=2).encode()
    blobs['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    # Remove obsolete previews from other plates, which are no longer printable.
    for name in list(blobs):
        if re.match(r'Metadata/plate_[23](?:_|\.)', name):
            del blobs[name]
    with ZipFile(target, 'w', ZIP_DEFLATED) as z:
        for name, data in blobs.items():
            z.writestr(name, data)
    return source


def inspect_gcode(code):
    """Record actual part extrusion, excluding startup, flushing and prime tower."""
    z = None
    feature = None
    printing = False
    tool = None
    e = 0.0
    relative = False
    feed = None
    top_feeds = []
    final_retractions = 0
    moves = []
    for line_no, line in enumerate(code.splitlines(), 1):
        if line.startswith('; Z_HEIGHT:'):
            z = float(line.split(':', 1)[1])
        if line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
        if line.startswith('; OBJECT_ID:'):
            printing = True
        if line.startswith(('; CHANGE_LAYER', '; WIPE_TOWER_START')) or (line.startswith('; FEATURE:') and feature in ('Custom', 'Prime tower')):
            printing = False
        select = re.match(r'M620 S(\d+)A', line)
        if select:
            tool = int(select.group(1))
        if re.fullmatch(r'T[01]', line.strip()):
            tool = int(line.strip()[1:])
        if line.startswith('M83'):
            relative = True
        if line.startswith('M82'):
            relative = False
        if line.startswith('G92 E'):
            e = float(line.split('E')[1].split()[0])
        if line.startswith(('G0 ', 'G1 ', 'G2 ', 'G3 ')):
            fv = re.search(r'\bF([\d.]+)', line.split(';')[0])
            if fv:
                feed = float(fv.group(1)) / 60
            ev = re.search(r'\bE(-?[\d.]+)', line.split(';')[0])
            if ev:
                new_e = float(ev.group(1))
                delta = new_e if relative else new_e - e
                if delta > 1e-6 and printing and z is not None and re.search(r'\b[XYIJ]-?[\d.]', line):
                    moves.append((line_no, tool, z, feature))
                    if tool == 0 and abs(z-4) < .001 and feature == 'Top surface':
                        top_feeds.append(feed)
                if delta < -.1 and tool == 0 and z is not None and abs(z-4) < .001:
                    final_retractions += 1
                e = new_e
    assert moves, 'No classified object extrusion'
    white = [m for m in moves if m[1] == 0]
    blue = [m for m in moves if m[1] == 1]
    assert white and blue
    assert abs(max(m[2] for m in white) - 4.0) < 0.001
    assert abs(min(m[2] for m in blue) - 4.2) < 0.001
    assert max(m[0] for m in white) < min(m[0] for m in blue)
    features = sorted(set(m[3] for m in white if abs(m[2] - 4) < .001))
    assert 'Top surface' in features
    assert 'Internal solid infill' not in features and 'Sparse infill' not in features
    return {'last_white_object_z_mm': 4.0, 'first_blue_object_z_mm': 4.2,
            'all_white_before_any_blue': True, 'white_final_layer_features': features,
            'white_final_layer_has_internal_or_sparse_infill': False,
            'white_final_top_speed_mm_s': sorted(set(top_feeds)),
            'white_final_layer_retractions': final_retractions,
            'white_final_layer_extrusion_moves': sum(abs(m[2]-4)<.001 for m in white)}


def validate(args, path, label):
    w = args.work_dir / label
    w.mkdir(parents=True, exist_ok=True)
    common = ['--datadir', str(w/'user'), '--debug', '2']
    run_cli(args.bambu_bin, common+['--info', '--outputdir', str(w/'info'), str(path)], w/'info.log')
    run_cli(args.bambu_bin, common+['--slice', '0', '--orient', '0', '--arrange', '0',
        '--outputdir', str(w/'slice'), '--export-3mf', 'validation.3mf', str(path)], w/'slice.log')
    result = json.loads((w/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    p = result['sliced_plates'][0]
    assert not p.get('warning_message') and p['filament_change_times'] == 1
    with ZipFile(w/'slice/validation.3mf') as archive:
        code = archive.read('Metadata/plate_1.gcode').decode()
    assert '\nM83' in code
    assert '; FEATURE: Support' not in code
    return {'native_reopen_exit': 0, 'native_slice_exit': 0,
            'estimated_seconds': p['total_predication'],
            'estimated_grams': sum(f['total_used_g'] for f in p['filaments']),
            'filament_changes': p['filament_change_times'], 'supports': False,
            'warnings': p.get('warning_message'), **inspect_gcode(code)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bambu-bin', type=Path, default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--work-dir', type=Path, default=Path('/tmp/m7-casa-fachada-v3'))
    a = p.parse_args()
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:' + str(a.bambu_bin.parent)
    a.work_dir.mkdir(parents=True, exist_ok=True)
    FOLDER.mkdir(parents=True, exist_ok=True)
    baseline = a.work_dir/'fachada-v2-isolada.3mf'
    target = ROOT/'downloads'/f'{PREFIX}-A1-AMS-1-prato.3mf'
    source = project(baseline, False)
    project(target, True)
    meshes = annotate(target, target, [WHITE, BLUE, CYAN], PREFIX)
    assert len(meshes) == 1 and len(meshes[0]) == 2
    orig_blobs, orig_config, _ = read_project(source)
    original = plate_meshes(orig_blobs, orig_config)[0][:2]
    for (key, col, mesh), (okey, ocol, omesh) in zip(meshes[0], original):
        assert key == okey and col == ocol
        assert (mesh.vertices == omesh.vertices).all() and (mesh.faces == omesh.faces).all()
    report = {'project': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'geometry_identical_to_v2': True, 'physical_print_tested': False,
              'white_part_overrides': WHITE_SETTINGS, 'ironing': False,
              'baseline': validate(a, baseline, 'baseline'),
              'trial': validate(a, target, 'trial')}
    assert report['baseline']['white_final_top_speed_mm_s'] == [35]
    assert report['trial']['white_final_top_speed_mm_s'] == [25]
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    entries = [target, ROOT/'designs'/f'{PREFIX}-pratos.png',
               FOLDER/'README.md', FOLDER/'bambu-validation.json', Path(__file__)]
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip', 'w', ZIP_DEFLATED) as archive:
        for entry in entries:
            archive.write(entry, entry.name)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
