"""Add printable black veins/contours to the approved Aquelá leaf backing.

Wolf meshes and its 3MF are reused byte-for-byte from V2. Only the leaf piece
changes. Black and green are two color volumes of one physical glued backing.
"""
from pathlib import Path
import hashlib
import json
import cv2
import manifold3d as md
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

from generate_anilha_aquela_v2 import ROOT, SOURCE, BLACK, GREEN, largest, tracer, cap
from generate_coruja_bruna_v3 import exact, union
from generate_universo_stand import render_meshes

FOLDER = ROOT/'fusion/AnilhaAquelaV3'
PREFIX = 'anilha-aquela-v3'
WOLF_PROJECT = 'anilha-aquela-v2-LOBO-A1-04-AMS-4-cores.3mf'


def solid_from_mesh(path):
    mesh = trimesh.load(path, force='mesh')
    solid = md.Manifold(md.Mesh64(np.ascontiguousarray(mesh.vertices, dtype='float64'),
                                 np.ascontiguousarray(mesh.faces, dtype='uint64')))
    assert solid.status() == md.Error.NoError
    return solid


def build_leaves(badge):
    rgb = np.array(Image.open(SOURCE).convert('RGB').crop((550, 178, 1010, 442)))
    r, g, b = rgb.astype(float).transpose(2, 0, 1)
    fg, box = largest((g > r*1.35) & (g > b*1.15) & (g > 35))
    trace = tracer(box, 62, 48)
    outline = trace(fg, 100)
    dark = cv2.medianBlur(((g < 108) & (fg > 0)).astype('uint8'), 3)
    veins = trace(dark, 6).offset(.12, md.JoinType.Round, circular_segments=16)
    # A continuous printable outline, plus the source's separate leaves/stems.
    rim = outline-outline.offset(-.48, md.JoinType.Round, circular_segments=16)
    ink = (veins+rim) ^ outline
    green_face = outline-ink
    # Under the wolf both colors terminate at Z=2, preserving the flat glue face.
    # The exposed leaves are raised; black lies 0.24 mm below the green face.
    exposed = outline-badge.offset(.20, md.JoinType.Round, circular_segments=16)
    green = outline.extrude(1.52)+green_face.extrude(.48).translate((0, 0, 1.52))
    green += cap(green_face ^ exposed, 2.0, 2.96, .08)
    black = ink.extrude(.48).translate((0, 0, 1.52))
    black += (ink ^ exposed).extrude(.72).translate((0, 0, 2.0))
    bodies = {GREEN: green, BLACK: black}
    combined = union(bodies.values())
    assert len([p for p in combined.decompose() if p.volume() > 1e-7]) == 1
    assert (green ^ black).volume() < .001
    assert (black.slice(1.6)-green.slice(1.5)).area() < .001
    visible_ink = ink ^ exposed
    assert visible_ink.area() > 50
    return bodies, outline, ink, visible_ink


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    prior = json.loads((ROOT/'fusion/AnilhaAquelaV2/geometry.json').read_text())
    reused = [p for p in prior['parts'] if p['piece'] != 'folhas']
    source_hashes = {}
    source_solids = {}
    for p in reused:
        target = ROOT/'downloads'/p['file']
        assert hashlib.sha256(target.read_bytes()).hexdigest() == p['sha256']
        source_hashes[p['file']] = p['sha256']
        source_solids[p['key']] = solid_from_mesh(target)
    source_hashes[WOLF_PROJECT] = hashlib.sha256((ROOT/'downloads'/WOLF_PROJECT).read_bytes()).hexdigest()
    badge = source_solids['lobo-preto'].slice(1.0)
    bodies, outline, ink, visible = build_leaves(badge)
    parts = list(reused)
    for key, color in [('folhas-verdes', GREEN), ('folhas-nervuras-pretas', BLACK)]:
        target = ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh = exact(bodies[color], target)
        parts.append({'key': key, 'file': target.name, 'color': color, 'piece': 'folhas',
                      'assembly': np.eye(4).tolist(), 'dimensions_mm': mesh.extents.tolist(),
                      'volume_mm3': mesh.volume, 'watertight': True,
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    whole = union(bodies.values())
    combined = exact(whole, ROOT/'downloads'/f'{PREFIX}-folhas-completas-monocor.stl')
    assert np.allclose(combined.extents, [62, 48, 2.96], atol=.02)
    scene = []; glb = trimesh.Scene()
    for p in parts:
        solid = bodies[p['color']] if p['piece'] == 'folhas' else source_solids[p['key']]
        pose = np.array(p['assembly'])
        scene.append((solid.transform(pose[:3].tolist()), p['color']))
        mesh = trimesh.load(ROOT/'downloads'/p['file'], force='mesh')
        mesh.apply_transform(pose)
        mesh.visual.face_colors = [int(p['color'][i:i+2], 16) for i in (1, 3, 5)]+[255]
        glb.add_geometry(mesh, node_name=p['key'])
    intersections = []
    for i, (a, _) in enumerate(scene):
        for j, (b, _) in enumerate(scene[i+1:], i+1):
            # Previously validated wolf colors are unchanged; review new leaf interfaces.
            if parts[i]['piece'] != 'folhas' and parts[j]['piece'] != 'folhas': continue
            volume = (a ^ b).volume()
            if volume > .003: intersections.append([parts[i]['key'], parts[j]['key'], volume])
    assert not intersections, intersections
    glb.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    report = {'title': 'Aquelá V3 — folhas com nervuras e contornos pretos',
              'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'reused_unchanged_sha256': source_hashes, 'wolf_project': WOLF_PROJECT,
              'physical_parts_count': 3, 'foliage_color_volume_count': 2,
              'foliage_dimensions_mm': combined.extents.tolist(),
              'flat_glue_face_z_mm': 2.0, 'exposed_green_top_mm': 2.96,
              'exposed_black_top_mm': 2.72, 'rim_width_mm': .48,
              'traced_vein_expansion_mm': .12, 'black_contact_start_z_mm': 1.52,
              'black_area_mm2': ink.area(), 'black_area_visible_when_assembled_mm2': visible.area(),
              'connected_leaf_piece': True, 'supported_color_caps': True,
              'assembly_intersections': intersections, 'parts': parts,
              'physical_print_tested': False, 'physical_fit_tested': False}
    (FOLDER/'geometry.json').write_text(json.dumps(report, indent=2)+'\n')
    stand = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    leaf_scene = [(s.transform(stand[:3].tolist()), c) for c, s in bodies.items()]
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    sheet = Image.new('RGB', (1550, 850), '#f4f6f8'); d = ImageDraw.Draw(sheet)
    d.text((35, 25), 'Aquelá V3 · folhas com nervuras e contornos pretos', font=font(32), fill='#23384C')
    sheet.paste(render_meshes(leaf_scene, (780, 640), direction=(0, -1, 0), margin=35), (0, 95))
    sheet.paste(render_meshes(leaf_scene, (760, 640), direction=(.35, -1, .3), margin=35), (790, 95))
    d.text((35, 765), '62 × 48 × 2,96 mm · verde + preto · uma peça · centro plano para colar o lobo', font=font(25), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-folhas-CAD.png')
    upright = [(s.transform(stand[:3].tolist()), c) for s, c in scene]
    sheet = Image.new('RGB', (1450, 1000), '#f4f6f8'); d = ImageDraw.Draw(sheet)
    d.text((35, 25), 'Aquelá V3 · conjunto com as novas folhas', font=font(32), fill='#23384C')
    sheet.paste(render_meshes(upright, (710, 800), direction=(0, -1, 0), margin=35), (0, 100))
    sheet.paste(render_meshes(upright, (710, 800), direction=(.55, -1, .25), margin=35), (740, 100))
    d.text((35, 935), 'Geometria real · lobo e anilha aprovados mantidos · três peças para colar', font=font(25), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-montada-CAD.png')
    print(json.dumps({k: v for k, v in report.items() if k != 'parts'}, indent=2), flush=True)


if __name__ == '__main__': main()
