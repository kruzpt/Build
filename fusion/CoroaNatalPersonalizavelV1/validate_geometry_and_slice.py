"""Check browser-exported meshes, glue contacts, colors and real Bambu toolpaths."""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, LineString
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'fusion/tools'))
from build_pintos_pla_3mf import read_project, run_cli
from build_m7_prototypes_v1_3mf import plate_meshes
from check_anilha_lobito_v5_toolpaths import paths


def polygon(contours):
    result = Polygon()
    polys = [Polygon([(p['X']/10000, p['Y']/10000) for p in c]) for c in contours]
    for p in sorted(polys, key=lambda p: -p.area):
        assert p.is_valid
        result = result.union(p) if p.exterior.is_ccw else result.difference(p)
    assert result.is_valid
    return result


def inspect_case(key, work, executable):
    source = work / (key + '.3mf')
    model = json.loads((work / (key + '-geometry.json')).read_text())
    meshes = json.loads((work / (key + '-meshes.json')).read_text())
    shapes = [polygon(p['paths']) for p in model['parts']]
    assert shapes[0].geom_type == shapes[6].geom_type == 'Polygon'
    assert abs(shapes[0].bounds[2] - shapes[0].bounds[0] - 100) < .001
    for p in model['pads']:
        patch = polygon(p['footprint'])
        assert patch.intersection(shapes[6]).area >= 18
        assert patch.difference(shapes[0]).area < .0001
    for i in range(1, 6):
        assert shapes[i].difference(shapes[0]).area < .0001, (key, 'unsupported crown detail', i)
    assert shapes[7].difference(shapes[6]).area < .0001
    for i, p in enumerate(model['parts']):
        for j, q in enumerate(model['parts'][:i]):
            if p['piece'] == q['piece'] and min(p['z1'], q['z1']) > max(p['z0'], q['z0']) + .001:
                assert shapes[i].intersection(shapes[j]).area < .0001, (key, 'overlapping volumes', i, j)
    blobs, config, plates = read_project(source)
    native = plate_meshes(blobs, config)
    assert [len(p['items']) for p in plates] == [1, 1]
    assert [len(p) for p in native] == [6, 2]
    cfg = json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['filament_colour'] == [c.upper() for c in model['colors']]
    assert cfg['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert cfg['layer_height'] == '0.12' and cfg['brim_type'] == 'no_brim' and cfg['enable_support'] == '0'
    by_id = {int(i): (color, mesh) for plate in native for i, color, mesh in plate}
    volume = 0
    for i, p in enumerate(meshes):
        m = trimesh.Trimesh(vertices=p['mesh']['vertices'], faces=p['mesh']['triangles'], process=True)
        assert m.is_watertight and m.is_winding_consistent and m.volume > 0, (key, p['name'])
        expected_volume = shapes[i].area * (p['z1']-p['z0'])
        assert abs(m.volume-expected_volume) < .01
        color, actual = by_id[i+1]
        assert color == p['color'] and actual.is_watertight and actual.is_winding_consistent
        assert abs(actual.volume-m.volume) < .05
        assert actual.bounds[0, :2].min() > 0 and actual.bounds[1, :2].max() < 253
        assert np.allclose(actual.vertices - [112,115,0], m.vertices, atol=.0001)
        volume += m.volume
    out = work / ('bambu-' + key)
    out.mkdir(exist_ok=True)
    common = ['--datadir', str(out/'user'), '--debug', '2']
    run_cli(executable, common + ['--info', '--outputdir', str(out/'reopen'), str(source)], out/'reopen.log')
    run_cli(executable, common + ['--slice', '0', '--orient', '0', '--arrange', '0', '--outputdir', str(out/'slice'),
                                 '--export-3mf', 'validation.3mf', str(source)], out/'slice.log')
    result = json.loads((out/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 2
    reviews = []
    with ZipFile(out/'slice/validation.3mf') as z:
        for i, plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message'), (key, plate.get('warning_message'))
            code = z.read(f'Metadata/plate_{i+1}.gcode').decode()
            rows = [r for r in paths(code) if r['feature'] != 'Prime tower']
            assert rows and not any(r['feature'].startswith(('Brim', 'Support')) for r in rows)
            assert {r['tool'] for r in rows} == ({1,2,3,4} if i == 0 else {1,4})
            assert abs(max(r['layer'] for r in rows) - (2.6 if i == 0 else 2.12)) < .001
            assert max(r['speed'] for r in rows if r['feature']=='Top surface') <= 18.001
            assert max(r['speed'] for r in rows if r['feature']=='Outer wall') <= 25.001
            if i == 0:
                # The raised pad must really receive cream extrusion at its final Z.
                for p in model['pads']:
                    center = np.array(p['center'])+[112,115]
                    assert any(r['tool']==1 and abs(r['layer']-2.6)<.001 and any(np.linalg.norm(np.array(v[:2])-center)<2.3 for v in r['points']) for r in rows)
                # Fine veins must survive slicing on their two raised layers.
                assert any(r['tool']==2 and r['layer']>2.24 and r['layer']<=2.48 for r in rows)
            else:
                components = list(shapes[7].geoms) if hasattr(shapes[7], 'geoms') else [shapes[7]]
                traces = [LineString([(p[0]-112,p[1]-115) for p in r['points']]) for r in rows if r['tool']==4 and r['layer']>1.4]
                assert all(any(region.intersects(line) for line in traces) for region in components), (key, 'red detail lost')
                assert plate['filament_change_times'] == 1
            reviews.append({'plate': i+1, 'estimated_seconds': plate['total_predication'],
                            'main_grams': sum(f['main_used_g'] for f in plate['filaments']),
                            'total_grams_including_purge_and_tower': sum(f['total_used_g'] for f in plate['filaments']),
                            'filament_changes': plate['filament_change_times'], 'warning': plate.get('warning_message'),
                            'gcode_sha256': hashlib.sha256(code.encode()).hexdigest()})
            if key == 'clemente-2026':
                draw_paths(rows, i)
    report = {'key': key, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'solid_volume_mm3': volume,
              'all_eight_volumes_watertight': True, 'overlapping_material_volumes': False,
              'text_and_crown_bases_connected': True, 'contact_area_mm2': model['metrics']['contact_total_mm2'],
              'native_reopen_exit': 0, 'native_slice_exit': 0, 'raised_pads_and_leaf_veins_extrusion_verified': True,
              'all_red_text_components_receive_extrusion': True, 'plates': reviews}
    print(json.dumps({'case': key, 'validated': True, 'plates': len(reviews)}), flush=True)
    return report


def draw_paths(rows, plate):
    im = Image.new('RGB', (1040, 1100), '#f7f4ec'); draw = ImageDraw.Draw(im)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    draw.text((30, 24), ('Coroa' if plate==0 else 'Texto')+' · percursos reais do Bambu Studio', font=font(27), fill='#234e3a')
    palette = ['#E6D2A8', '#234E3A', '#719071', '#B51636']
    for r in sorted(rows, key=lambda r: r['layer']):
        pts = [(520+(p[0]-112)*8,600-(p[1]-115)*8) for p in r['points']]
        draw.line(pts, fill=palette[r['tool']-1], width=3)
    draw.text((30, 1048), '0,12 mm · bico 0,4 mm · sem suportes nem brim', font=font(24), fill='#234e3a')
    im.save(ROOT/f'designs/coroa-natal-v1-percursos-{plate+1}.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, default=Path('/tmp/coroa-v1-tests'))
    parser.add_argument('--bambu-bin', type=Path, required=True)
    args = parser.parse_args()
    os.environ['LD_LIBRARY_PATH'] = '/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    browser = json.loads((HERE/'browser-validation.json').read_text())
    keys = [p['key'] for p in browser['cases']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        reports = list(pool.map(lambda key: inspect_case(key, args.work, args.bambu_bin), keys))
    (HERE/'bambu-validation.json').write_text(json.dumps({'bambu_version':'02.09.01.70','printer':'Bambu Lab A1 / AMS Lite / 0.4 mm',
        'filament':'Generic PLA, not spool-calibrated','cases':reports,'physical_print_tested':False,'physical_glue_tested':False}, indent=2)+'\n')


if __name__ == '__main__':
    main()
