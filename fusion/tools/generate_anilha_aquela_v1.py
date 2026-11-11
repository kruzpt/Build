"""Generate the approved three-piece Aquelá scout woggle in millimetres.

The physical stack is deliberately simple: a brown scarf ring, one green
leaf plate, and one connected multi-colour wolf/name badge.  It is an
original vector interpretation of the approved reference, not a traced copy.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_coruja_bruna_v1 import ellipse, path, petal
from generate_joana_topper import save_mesh
from generate_m7_prototypes_v1 import BOLD, normalize, rounded, stroke, text
from generate_universo_stand import render_meshes

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/AnilhaAquelaV1'
PREFIX = 'anilha-aquela-v1'

BROWN = '#70452E'
GREEN = '#2F8B42'
CHARCOAL = '#4B5055'
CREAM = '#F4D6A1'
COLORS = [BROWN, GREEN, CHARCOAL, CREAM]


def union(items):
    pieces = list(items)
    return md.Manifold.batch_boolean(pieces, md.OpType.Add)


def clean(solid):
    assert solid.status() == md.Error.NoError, solid.status()
    pieces = [piece for piece in solid.simplify(.002).decompose() if piece.volume() > 1e-5]
    return union(pieces)


def bounds(section):
    points = np.vstack(section.to_polygons())
    return points.min(axis=0), points.max(axis=0)


def leaf_plate():
    """One green plate: a hidden central carrier and ten distinct leaves."""
    section = rounded(-12, 8, 24, 24, 3)
    for y, length, width, angle in ((8, 22, 5.5, 68), (15, 24, 5.7, 57),
                                    (23, 22, 5.2, 45), (30, 19, 4.7, 31),
                                    (35, 15, 4.2, 20)):
        section += petal(-4.5, y, length, width, angle)
        section += petal(4.5, y, length, width, -angle)
    section = normalize(section, width=62, height=48)
    # Keep the leaf veins broad enough to survive a 0.4 mm nozzle; they are
    # raised in the same green material and make no new colour change.
    vein = md.CrossSection()
    for sign in (-1, 1):
        for y, angle in ((9, 68), (16, 57), (24, 45), (31, 31), (36, 20)):
            base = np.array((sign * 3.8, y))
            end = base + np.array((sign * 8.0, 6.0 + (y - 9) * .13))
            vein += stroke([base, end], .62)
    vein = vein ^ section.offset(-.55, md.JoinType.Round, circular_segments=20)
    base = section.extrude(3.0)
    raised = vein.extrude(.38).translate((0, 0, 2.94))
    result = clean(union([base, raised]))
    return result, section


def wolf_badge():
    """A three-colour connected badge; charcoal is the structural backing."""
    plaque = rounded(-27.5, 0, 55, 18, 3.0)
    neck = rounded(-13.5, 14, 27, 15, 4)
    head = ellipse(0, 39, 17.2, 17.8)
    ear_left = path('M -14 48 C -19 52 -18 61 -14.5 65 C -10.2 60 -7.8 54 -7.8 48 Z')
    ear_right = path('M 14 48 C 19 52 18 61 14.5 65 C 10.2 60 7.8 54 7.8 48 Z')
    outer = plaque + neck + head + ear_left + ear_right
    outer = outer.offset(-.18, md.JoinType.Round, circular_segments=28).offset(.18, md.JoinType.Round, circular_segments=28)

    gray = (ellipse(0, 39.0, 15.7, 16.1) +
            path('M -13.3 49 C -16 53 -15.5 59 -14.1 61.8 C -11.8 57.7 -10.0 53.1 -8.8 48 Z') +
            path('M 13.3 49 C 16 53 15.5 59 14.1 61.8 C 11.8 57.7 10 53.1 8.8 48 Z'))
    gray = gray ^ outer.offset(-.65, md.JoinType.Round, circular_segments=24)
    board = rounded(-25.8, 1.1, 51.6, 15.8, 2.4)
    board = board ^ plaque.offset(-.75, md.JoinType.Round, circular_segments=24)

    muzzle = ellipse(3.2, 31.6, 10.8, 6.0) + ellipse(-5.4, 31.2, 7.0, 5.4)
    brow = path('M -11.2 43.0 Q -6.6 46.4 -2.0 43.4 L -2.7 41.5 Q -6.6 44.0 -10.7 41.3 Z')
    brow += path('M 1.7 43.4 Q 6.5 46.3 11.0 42.9 L 10.6 41.1 Q 6.5 43.9 2.4 41.6 Z')
    eyes = ellipse(-6.2, 41.0, 3.8, 4.4) + ellipse(6.1, 41.0, 3.8, 4.4)
    inner_ears = path('M -13.4 51.2 C -14.6 54.4 -14.2 57.4 -13.9 58.8 C -11.6 55.7 -10.4 52.8 -10.0 50.3 Z')
    inner_ears += path('M 13.4 51.2 C 14.6 54.4 14.2 57.4 13.9 58.8 C 11.6 55.7 10.4 52.8 10.0 50.3 Z')
    name = text('Aquelá', 43.0, font=BOLD, strengthen=.04).translate((0, 3.4))
    cream = (muzzle + eyes + inner_ears + name) ^ outer.offset(-.72, md.JoinType.Round, circular_segments=24)
    cream -= brow

    nose = path('M 2.3 35.8 C 4.1 37.0 5.5 36.5 6.4 35.3 C 5.8 33.8 4.5 33.0 3.2 33.1 C 2.1 33.6 1.9 34.7 2.3 35.8 Z')
    pupils = ellipse(-5.7, 40.3, 1.45, 2.15) + ellipse(6.6, 40.3, 1.45, 2.15)
    smile = stroke([(-2.4, 28.9), (0.0, 27.7), (2.7, 28.8)], .72)
    charcoal_details = nose + pupils + smile + brow

    # Every cap sits on the charcoal backing.  The physical wolf badge remains
    # one connected object after the AMS colour changes.
    charcoal = outer.extrude(2.4)
    brown = board.extrude(.60).translate((0, 0, 2.4))
    gray_solid = gray.extrude(.60).translate((0, 0, 2.4))
    cream_solid = cream.extrude(.60).translate((0, 0, 3.0))
    charcoal_details_solid = charcoal_details.extrude(.48).translate((0, 0, 3.6))
    charcoal = clean(union([charcoal, charcoal_details_solid]))
    brown, gray_solid, cream_solid = (clean(s) for s in (brown, gray_solid, cream_solid))
    full = clean(union([charcoal, brown, gray_solid, cream_solid]))
    assert len(full.decompose()) == 1
    ext = np.asarray(full.bounding_box())
    assert 54 < ext[3] - ext[0] < 56 and 64 < ext[4] - ext[1] < 66
    return {'carvao': charcoal, 'castanho': brown, 'cinzento': gray_solid, 'creme': cream_solid}, outer


def scarf_ring():
    outer = rounded(-14.5, -11.0, 29.0, 22.0, 3.0)
    inner = rounded(-12.5, -9.0, 25.0, 18.0, 2.1)
    tube = clean((outer - inner).extrude(25.0))
    box = np.asarray(tube.bounding_box())
    assert np.allclose(box[3:] - box[:3], [29.0, 22.0, 25.0], atol=.02)
    return tube


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    leaves, leaf_section = leaf_plate()
    wolf, wolf_section = wolf_badge()
    ring = scarf_ring()
    parts = []

    def save(key, solid, colour, piece):
        target = ROOT / 'downloads' / f'{PREFIX}-{key}.stl'
        mesh = save_mesh(solid, target)
        parts.append({'key': key, 'piece': piece, 'file': target.name, 'color': colour,
                      'dimensions_mm': [float(x) for x in mesh.extents],
                      'volume_mm3': float(mesh.volume),
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                      'watertight': bool(mesh.is_watertight)})

    save('anilha-castanha', ring, BROWN, 'anilha')
    save('folhas-verdes', leaves, GREEN, 'folhas')
    for key, colour in [('carvao', CHARCOAL), ('castanho', BROWN), ('cinzento', CHARCOAL), ('creme', CREAM)]:
        # Gray top volume uses the same charcoal filament as the structural wolf.
        save(f'lobo-{key}', wolf[key], colour, 'lobo')

    data = {
        'title': 'Anilha Aquelá V1 — lobo, folhas e tabuleta',
        'construction': 'Three physical pieces: brown scarf ring, one green leaf plate, one connected AMS wolf/name badge.',
        'name': 'Aquelá',
        'printer_target': 'Bambu Lab A1, 0.4 mm nozzle, AMS',
        'dimensions_mm': {
            'ring_outer_width_depth_height': [29, 22, 25],
            'ring_clear_opening_width_depth': [25, 18],
            'leaf_plate_width_height_thickness': [62, 48, 3.32],
            'wolf_badge_width_height_max_thickness': [55, 65, 4.08],
        },
        'assembly': {
            'order': ['Glue the brown ring centrally to the rear of the leaves.',
                      'Glue the wolf/name badge to the front of the leaf plate.'],
            'joint_type': 'large flat glue faces; dry-fit before applying a small amount of cyanoacrylate or suitable PLA adhesive',
            'physical_fit_tested': False,
        },
        'print_intent': {'brim': False, 'supports': False, 'walls': 3, 'ring_walls': 4,
                         'infill': '15% gyroid; 30% for ring'},
        'parts': parts,
    }
    (FOLDER / 'geometry.json').write_text(json.dumps(data, indent=2) + '\n')

    # Actual-mesh overview: flat pieces are rotated upright only for rendering.
    upright = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    badge_scene = [(solid.transform(upright[:3].tolist()), {'carvao': CHARCOAL, 'castanho': BROWN,
                    'cinzento': CHARCOAL, 'creme': CREAM}[key]) for key, solid in wolf.items()]
    leaf_scene = [(leaves.transform(upright[:3].tolist()), GREEN)]
    font = lambda size: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    image = Image.new('RGB', (1800, 1120), '#f5f4f0')
    draw = ImageDraw.Draw(image)
    draw.text((45, 28), 'Anilha Aquelá V1 — três peças para colar', font=font(40), fill='#26384A')
    draw.text((45, 83), 'Anilha castanha · folhas verdes numa só peça · lobo e nome Aquelá num único emblema AMS', font=font(24), fill='#536574')
    image.paste(render_meshes(badge_scene, (800, 770), direction=(0, -1, .15), margin=38), (0, 150))
    image.paste(render_meshes(leaf_scene, (520, 530), direction=(0, -1, .15), margin=35), (825, 205))
    image.paste(render_meshes([(ring, BROWN)], (400, 530), direction=(.7, -1, .7), margin=35), (1375, 205))
    draw.text((75, 950), 'Lobo + tabuleta: 55 × 65 × 4,08 mm', font=font(25), fill='#26384A')
    draw.text((855, 790), 'Folhas: 62 × 48 × 3,32 mm', font=font(23), fill='#26384A')
    draw.text((1390, 790), 'Anilha: 29 × 22 × 25 mm', font=font(23), fill='#26384A')
    draw.text((45, 1030), 'Passagem útil da anilha: 25 × 18 mm · 0,4 mm · sem brim e sem suportes · montagem por colagem', font=font(24), fill='#536574')
    image.save(ROOT / 'designs' / f'{PREFIX}-CAD.png')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
