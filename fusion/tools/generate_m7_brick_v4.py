"""Extract the customer's actual seven from an STL and reuse it without tracing.

Run with --source-stl on first extraction. Later runs use the small, derived
source-seven.json; the customer's complete old plaque is not redistributed.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from shutil import copy2

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

import generate_m7_prototypes_v1 as v1
from generate_joana_topper import cross_section, section_groups, save_mesh
from generate_universo_stand import render_meshes

ROOT = v1.ROOT
FOLDER = ROOT / 'fusion/M7TijoloV4'
PREFIX = 'm7-tijolo-v4'
SOURCE_AXES = [[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0]]


def extract(source):
    mesh = trimesh.load(source, force='mesh')
    assert mesh.is_watertight and mesh.is_winding_consistent
    solid = md.Manifold(md.Mesh(mesh.vertices.astype('float32'), mesh.faces.astype('uint32')))
    upright = solid.transform(SOURCE_AXES)

    def seven_at(depth):
        candidates = []
        for section in upright.slice(depth).decompose():
            points = v1.pts(section)
            lo, hi = points.min(0), points.max(0)
            # Location of the real 7 in this specific supplied plaque. Select
            # the connected profile, including its holes, never a raster trace.
            if 54 < lo[0] < 56 and 2 < lo[1] < 3 and 67 < hi[0] < 69 and 20 < hi[1] < 22:
                candidates.append(section)
        assert len(candidates) == 1, ('Ambiguous source seven', len(candidates))
        return candidates[0]

    raw = seven_at(.5)
    errors = []
    for depth in (.1, .25, .75, .9):
        other = seven_at(depth)
        difference = (raw - other).area() + (other - raw).area()
        errors.append(difference)
        assert difference < .00001, ('Source changes through thickness', depth, difference)
    groups = section_groups(raw)
    cached = cross_section(groups)
    cache_difference = (raw - cached).area() + (cached - raw).area()
    assert cache_difference < .001
    points = v1.pts(raw)
    data = {
        'source_file': source.name,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_mesh_closed': True,
        'source_to_upright_axes': SOURCE_AXES,
        'extraction_plane_original_x_mm': -.5,
        'checked_original_x_planes_mm': [-.1, -.25, -.5, -.75, -.9],
        'through_thickness_max_symmetric_difference_mm2': max(errors),
        'raw_bounds_xy_mm': [points.min(0).tolist(), points.max(0).tolist()],
        'raw_size_xy_mm': np.ptp(points, axis=0).tolist(),
        'raw_area_mm2': raw.area(),
        'holes': len(raw.to_polygons()) - 1,
        'cache_rounding_symmetric_difference_mm2': cache_difference,
        'groups': groups,
    }
    FOLDER.mkdir(exist_ok=True)
    (FOLDER / 'source-seven.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return data


def exact_mesh(solid, path):
    """Serialize the extracted polygon without simplifying its brush outline."""
    raw = solid.to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties[:, :3], faces=raw.tri_verts, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent
    mesh.export(path)
    return trimesh.load(path, force='mesh')


def make(source=None):
    data = extract(source) if source else json.loads((FOLDER / 'source-seven.json').read_text())
    raw = cross_section(data['groups'])
    original = json.loads((ROOT / 'fusion/M7TijoloV3/geometry.json').read_text())
    old = {p['key']: p for p in original['parts']}
    sections = {k: cross_section(p['regions'][0]['groups']) for k, p in old.items() if k != 'tijolo-terracota'}
    old_seven = sections['7-ciano']
    old_points, raw_points = v1.pts(old_seven), v1.pts(raw)
    anchor = old_points.min(0)
    scale = np.ptp(old_points, axis=0)[1] / np.ptp(raw_points, axis=0)[1]
    raw_min = raw_points.min(0)
    seven = raw.translate(-raw_min).scale((scale, scale)).translate(anchor)
    sections['7-ciano'] = seven
    frame, letter_m = sections['estrela-dourada'], sections['m-branco']
    assert ((letter_m + seven).offset(.35, circular_segments=24) ^ frame).area() < 1e-6
    assert (letter_m.offset(.15) ^ seven.offset(.15)).area() < 1e-6

    profile = cross_section(old['tijolo-terracota']['regions'][0]['groups'])
    body = profile.extrude(70)
    regions = [v1.region(profile, 70)]
    for key in list(old)[1:]:
        if key == '7-ciano':
            region = v1.region(seven.offset(.15, circular_segments=24), .25, -.2, 'cut', v1.pose_front())
        else:
            region = deepcopy(old['tijolo-terracota']['regions'][list(old).index(key)])
        cutter = cross_section(region['groups']).extrude(region['height']).translate((0, 0, region['z']))
        body -= v1.transformed(cutter, np.array(region['transform']))
        regions.append(region)

    parts, assembled = [], []
    for key, part in old.items():
        entry = deepcopy(part)
        entry['file'] = f'{PREFIX}-{key}.stl'
        path = ROOT / 'downloads' / entry['file']
        if key == 'tijolo-terracota':
            solid = body
            entry['regions'] = regions
            mesh = save_mesh(solid.simplify(.003), path)
        elif key == '7-ciano':
            solid = seven.extrude(1.2)
            entry['regions'] = [v1.region(seven, 1.2)]
            entry['name'] = '7 ciano original extraído do STL'
            mesh = exact_mesh(solid, path)
        else:
            solid = sections[key].extrude(1.2)
            copy2(ROOT / 'downloads' / part['file'], path)
            mesh = trimesh.load(path, force='mesh')
        assert mesh.is_watertight and mesh.is_winding_consistent
        assert len(mesh.split()) == (9 if key == 'natal-branco' else 1)
        entry.update(bbox_mm=mesh.extents.tolist(), volume_mm3=float(mesh.volume), watertight=True)
        posed = v1.transformed(solid, np.array(entry['assembly']))
        if key != 'tijolo-terracota':
            assert (posed ^ body).volume() < .001
        assembled.append((posed, entry['color']))
        parts.append(entry)
    for i, (solid, _) in enumerate(assembled[1:]):
        for other, _ in assembled[i+2:]:
            assert (solid ^ other).volume() < .001
        for offset in np.linspace(0, 4, 21):
            assert (solid.translate((0, -float(offset), 0)) ^ body).volume() < .001

    # Compare the serialized STL section back to the extracted source polygon.
    result = trimesh.load(ROOT / f'downloads/{PREFIX}-7-ciano.stl', force='mesh')
    roundtrip = md.Manifold(md.Mesh(result.vertices.astype('float32'), result.faces.astype('uint32'))).slice(.6)
    difference = (seven - roundtrip).area() + (roundtrip - seven).area()
    assert difference < .0001, ('Export distorted extracted outline', difference)
    recovered = roundtrip.translate(-anchor).scale((1/scale, 1/scale)).translate(raw_min)
    source_difference = (raw - recovered).area() + (recovered - raw).area()
    assert source_difference < .001
    reusable = ['estrela-dourada', 'arvore-dourada', 'natal-branco', 'm-branco']
    for key in reusable:
        assert (ROOT / f'downloads/{PREFIX}-{key}.stl').read_bytes() == (ROOT / 'downloads' / old[key]['file']).read_bytes()
    report = {
        'version': 4,
        'change': 'Actual seven extracted from the supplied STL, uniformly scaled; seven and matching body pocket only',
        'source_file': data['source_file'], 'source_sha256': data['source_sha256'],
        'source_extraction': {k: v for k, v in data.items() if k != 'groups'},
        'uniform_scale_xy': scale, 'no_anisotropic_scaling': True, 'outline_redrawn_or_smoothed': False,
        'source_origin_xy_mm': raw_min.tolist(), 'target_origin_xy_mm': anchor.tolist(),
        'exported_outline_symmetric_difference_mm2': difference,
        'exported_outline_recovered_to_source_symmetric_difference_mm2': source_difference,
        'body_width_depth_height_mm': [50, 26, 70], 'star_width_mm': 30,
        'seven_bbox_mm': result.extents.tolist(), 'source_holes_preserved_in_stl': data['holes'],
        'pocket_depth_mm': .2, 'pocket_clearance_per_side_mm': .15, 'glue_gap_mm': .05,
        'ornament_thickness_mm': 1.2, 'all_parts_watertight': True,
        'insertion_positions_checked': 105, 'reusable_v2_v3_parts': reusable,
        'requires_new_body_and_seven': True, 'physical_fit_tested': False, 'fusion_runtime_tested': False,
        'parts': [{k: v for k, v in p.items() if k not in ('assembly', 'regions')} for p in parts],
    }
    (FOLDER / 'geometry.json').write_text(json.dumps({'units': 'mm', 'version': 4, 'parts': parts, 'brick': report}, ensure_ascii=False, indent=2) + '\n')
    (FOLDER / 'geometry-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    script = (ROOT / 'fusion/M7TijoloV3/M7TijoloV3.py').read_text().replace('V3', 'V4').replace('7 pincelado', '7 original do STL')
    (FOLDER / 'M7TijoloV4.py').write_text(script)
    illustrate(assembled, frame, letter_m, old_seven, seven, scale)
    print(json.dumps({k: v for k, v in report.items() if k not in ('parts', 'source_extraction')}, ensure_ascii=False, indent=2))


def draw_profile(draw, cs, center, scale, color, background):
    points = v1.pts(cs)
    middle = (points.min(0) + points.max(0)) / 2
    for loop in cs.to_polygons():
        a = np.array(loop)
        signed = np.sum(a[:, 0]*np.roll(a[:, 1], -1) - np.roll(a[:, 0], -1)*a[:, 1]) / 2
        draw.polygon([(center[0]+(x-middle[0])*scale, center[1]-(y-middle[1])*scale) for x, y in a],
                     fill=color if signed > 0 else background)


def illustrate(assembled, frame, letter_m, old_seven, seven, scale):
    font = lambda n: ImageFont.truetype(v1.REGULAR, n)
    background = '#f4f6f8'
    image = Image.new('RGB', (1800, 1080), background)
    draw = ImageDraw.Draw(image)
    draw.text((35, 25), 'M7 — V4 com o 7 original do STL enviado', font=font(37), fill=v1.BLUE)
    raw = cross_section(json.loads((FOLDER / 'source-seven.json').read_text())['groups'])
    raw_scaled = raw.scale((scale, scale))
    for i, (cs, title, note) in enumerate([
        (old_seven, 'V3 anterior', 'Interpretação manual anterior'),
        (raw_scaled, '7 extraído do STL', 'Original mostrado reduzido à altura final'),
        (seven, 'V4 para imprimir', 'Mesmo contorno e proporções do original'),
    ]):
        draw.text((35+i*600, 135), title, font=font(29), fill=v1.BLUE)
        draw_profile(draw, cs, (300+i*600, 570), 88, v1.CYAN, background)
        draw.text((25+i*600, 950), note, font=font(20), fill=v1.BLUE)
    draw.text((35, 1005), f'Escala uniforme do original: {scale*100:.3f}% · 7 final: 5,31 × 7,25 × 1,20 mm · sem redesenhar o contorno.', font=font(25), fill=v1.BLUE)
    image.save(ROOT / f'designs/{PREFIX}-comparacao.png')
    canvas = Image.new('RGB', (1530, 1060), background)
    d = ImageDraw.Draw(canvas)
    canvas.paste(render_meshes(assembled, (840, 850), direction=(.45, -.8, .55)), (0, 120))
    symbols = [(v1.transformed(cs.extrude(1.2), v1.pose_front()), color) for cs, color in [(frame, v1.GOLD), (letter_m, v1.WHITE), (seven, v1.CYAN)]]
    panel = md.Manifold.cube((36, .5, 34)).translate((-18, .2, 38))
    canvas.paste(render_meshes([(panel, v1.ORANGE)] + symbols, (650, 740), direction=(.03, -1, .05)), (860, 160))
    d.text((40, 25), 'M7 — tijolo V4 · 7 original do STL', font=font(34), fill=v1.BLUE)
    d.text((40, 77), 'Estrela de 30 mm · proporções originais do 7 preservadas · restantes enfeites mantidos.', font=font(24), fill=v1.BLUE)
    d.text((40, 1000), 'Substituir corpo e 7 · estrela, m, árvore e inscrição reutilizáveis da V2/V3 · rebaixos 0,20 mm', font=font(23), fill=v1.BLUE)
    canvas.save(ROOT / f'designs/{PREFIX}-CAD.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-stl', type=Path)
    make(parser.parse_args().source_stl)
