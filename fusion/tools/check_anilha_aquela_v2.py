"""Inspect exported mesh transforms and actual native extrusion paths."""
import argparse
import hashlib
import json
from zipfile import ZipFile
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from build_pintos_pla_3mf import read_project
from build_m7_prototypes_v1_3mf import plate_meshes
from check_anilha_lobito_v5_toolpaths import paths
from generate_anilha_aquela_v2 import ROOT, FOLDER, PREFIX, COLORS, BROWN, GREEN


def main(work):
    geometry = json.loads((FOLDER/'geometry.json').read_text())
    reviews = []; views = []
    for kind in ['lobo', 'acessorios']:
        report = json.loads((FOLDER/f'bambu-validation-{kind}.json').read_text())
        target = ROOT/'downloads'/report['project']
        assert hashlib.sha256(target.read_bytes()).hexdigest() == report['sha256']
        blobs, cfg, _ = read_project(target)
        native = plate_meshes(blobs, cfg)
        colors = COLORS if kind == 'lobo' else [BROWN, GREEN]
        selected = [p for p in geometry['parts'] if (p['piece'] == 'lobo') == (kind == 'lobo')]
        poses = {}; errors = []
        for p in selected:
            ref = trimesh.load(ROOT/'downloads'/p['file'], force='mesh')
            assert hashlib.sha256((ROOT/'downloads'/p['file']).read_bytes()).hexdigest() == p['sha256']
            col = colors.index(p['color'])+1
            mesh = next(m for plate in native for _, c, m in plate if c == col)
            assert np.array_equal(ref.faces, mesh.faces), p['key']
            fit = np.linalg.lstsq(np.c_[ref.vertices, np.ones(len(ref.vertices))], mesh.vertices, rcond=None)[0]
            error = np.max(np.linalg.norm(np.c_[ref.vertices, np.ones(len(ref.vertices))]@fit-mesh.vertices, axis=1))
            assert error < .003
            assert np.allclose(fit[:3].T@fit[:3], np.eye(3), atol=.00001)
            if p['piece'] in poses:
                assert np.allclose(fit, poses[p['piece']], atol=.003), 'Color volumes moved independently'
            poses[p['piece']] = fit; errors.append(float(error))
        with ZipFile(work/kind/'slice/validation.3mf') as archive:
            for i, plate in enumerate(native):
                code = archive.read(f'Metadata/plate_{i+1}.gcode').decode()
                assert hashlib.sha256(code.encode()).hexdigest() == report['plates'][i]['gcode_sha256']
                rows = [r for r in paths(code) if r['feature'] != 'Prime tower']
                assert rows
                layers = sorted(set(r['layer'] for r in rows))
                assert abs(layers[0]-.2) < 1e-6 and max(np.diff(layers)) < .12001
                assert not any(r['feature'].startswith(('Support', 'Brim')) for r in rows)
                outer = [r['speed'] for r in rows if r['feature'] == 'Outer wall']
                top = [r['speed'] for r in rows if r['feature'] == 'Top surface']
                assert outer and max(outer) <= 25.001
                assert top and max(top) <= 18.001
                expected = {1, 2, 3, 4} if kind == 'lobo' else {i+1}
                assert {r['tool'] for r in rows} == expected
                piece = 'lobo' if kind == 'lobo' else ['anilha', 'folhas'][i]
                pose = np.eye(4); pose[:3] = poses[piece].T
                inverse = np.linalg.inv(pose)
                for row in rows:
                    points = np.array(row['points'])
                    row['points'] = (np.c_[points, np.ones(len(points))]@inverse.T)[:, :3]
                reviews.append({'piece': piece, 'layer_count': len(layers),
                                'tools': sorted(expected), 'top_speed_max_mm_s': max(top),
                                'outer_speed_max_mm_s': max(outer),
                                'native_transform_error_max_mm': max(errors),
                                'supports': False, 'brim': False,
                                'gcode_sha256': hashlib.sha256(code.encode()).hexdigest()})
                views.append((piece, rows, colors))
    sheet = Image.new('RGB', (1700, 1100), '#f4f6f8'); draw = ImageDraw.Draw(sheet)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    draw.text((35, 25), 'Aquelá V2 · percursos reais do Bambu Studio', font=font(34), fill='#23384C')
    panels = {'lobo': (35, 110, 780, 880), 'folhas': (880, 110, 760, 580), 'anilha': (1030, 740, 420, 245)}
    for piece, rows, colors in views:
        x0, y0, width, height = panels[piece]
        pp = np.concatenate([r['points'] for r in rows])[:, :2]
        lo, hi = pp.min(0), pp.max(0)
        scale = min((width-30)/(hi[0]-lo[0]), (height-30)/(hi[1]-lo[1]))
        shift = np.array([x0+width/2, y0+height/2])
        for row in sorted(rows, key=lambda r: r['layer']):
            points = (np.array(row['points'])[:, :2]-(lo+hi)/2)*scale
            points[:, 1] *= -1; points += shift
            draw.line([tuple(p) for p in points], fill=colors[row['tool']-1], width=max(1, round(.40*scale)))
        draw.text((x0, y0+height), piece.capitalize(), font=font(24), fill='#23384C')
    draw.text((35, 1050), 'Vista superior · largura gráfica dos traços: 0,4 mm · não é uma fotografia de impressão', font=font(22), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-percursos.png')
    data = {'multicolor_relative_poses_preserved': True,
            'gcode_parsed_including_arc_moves': True, 'plates': reviews,
            'physical_print_tested': False}
    (FOLDER/'toolpath-review.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--work-dir', type=Path, required=True)
    main(parser.parse_args().work_dir)
