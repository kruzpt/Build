"""Generate the four closed colour volumes of the integrated panda scarf slide.

Coordinates in mm: X = left/right, Y = front/back, Z = build height.
The bore runs through Z. This is the printable CAD model, not the concept image.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import manifold3d as md
import trimesh

HERE = Path(__file__).resolve().parent
OUT = HERE / 'stl'
OUT.mkdir(parents=True, exist_ok=True)


def egg(center, radii, segments=40):
    return md.Manifold.sphere(1, segments).scale(radii).translate(center)


def capsule(a, b, radius):
    """A rounded detail following a short straight line."""
    return (egg(a, (radius,)*3, 16) + egg(b, (radius,)*3, 16)).hull()


def leaf(a, b):
    """A thin leaf with a broad middle and a tapered upward tip."""
    mid = tuple((x+y)/2 for x, y in zip(a, b))
    return union([
        egg(a, (1.4, 1.2, 1.4), 24),
        egg(mid, (2.5, 1.5, 2.1), 24),
        egg(b, (.45, .55, .65), 16),
    ]).hull()


def ellipse_tube(rx, ry, h, center=(0, 0, 0), segments=96):
    return md.Manifold.cylinder(h, 1, circular_segments=segments).scale((rx, ry, 1)).translate(center)


def union(items):
    result = items[0]
    for item in items[1:]:
        result += item
    return result


def head_tilt(shape):
    """Lean the complete face toward the paw on the left of the image."""
    pivot = (0, -5.8, 28.0)
    return shape.translate(tuple(-v for v in pivot)).rotate((0, -11, 0)).translate(pivot)


foot_left = egg((-11.2, -12.7, 5.8), (7.4, 7.0, 6.3))
foot_right = egg((11.2, -12.7, 5.8), (7.4, 7.0, 6.3))
black = union([
    # The flat-bottomed rear sleeve is continuous from the build plate.
    ellipse_tube(15.5, 12, 25, (0, 18, 0)),
    egg((0, -3.0, 12), (15, 11, 14)),       # torso
    egg((0, 3.0, 12), (13, 8, 11)),       # broad tube-to-torso rib
    foot_left,
    foot_right,
    egg((-15.5, -10.0, 17.5), (5.1, 6.3, 8.5)), # arms join the feet
    egg((15.5, -10.0, 17.5), (5.1, 6.3, 8.5)),
    head_tilt(egg((-14.6, -5.8, 49.0), (6.0, 5.5, 7.3))), # ears follow head
    head_tilt(egg((14.6, -5.8, 46.6), (6.0, 5.5, 7.3))),
])

ivory = union([
    head_tilt(egg((0, -5.8, 37.0), (19.4, 14.2, 15.2))), # head
    egg((0, -11.0, 12.0), (9.0, 5.6, 12.3)),  # belly
])
whole_raw = black + ivory
black -= ivory

# Apply dark face markings to the cream head. The brows stay inside the patches.
eye_marks = head_tilt(union([
    egg((-7.7, -17.0, 40.0), (5.9, 3.0, 6.4)),
    egg((7.7, -17.0, 40.0), (5.9, 3.0, 6.4)),
    egg((0, -18.8, 33.8), (2.2, 2.0, 1.5)), # nose
    capsule((-3.6, -18.3, 30.5), (-1.5, -17.5, 29.6), .76),
    capsule((-1.5, -17.5, 29.6), (0, -18.0, 31.0), .76),
    capsule((0, -18.0, 31.0), (1.5, -17.5, 29.6), .76),
    capsule((1.5, -17.5, 29.6), (3.6, -18.3, 30.5), .76),
]))
whole_raw += eye_marks
ivory -= eye_marks
black += eye_marks

# Heavy sleepy eyelids, with eyes wide enough for a 0.4 mm nozzle.
eye_whites = head_tilt(union([
    egg((-7.7, -19.0, 37.5), (3.1, 1.25, 1.6)),
    egg((7.7, -19.0, 37.5), (3.1, 1.25, 1.6)),
]))
whole_raw += eye_whites
black -= eye_whites
ivory += eye_whites
pupils = head_tilt(union([
    egg((-7.0, -19.8, 37.2), (1.0, .8, 1.2)),
    egg((8.4, -19.8, 37.2), (1.0, .8, 1.2)),
    capsule((-11.5, -19.45, 39.0), (-4.0, -19.45, 39.3), .75),
    capsule((4.0, -19.45, 39.3), (11.5, -19.45, 39.0), .75),
]))
whole_raw += pupils
ivory -= pupils
black += pupils

# Bamboo runs diagonally across the belly. Short capsules intersect the torso
# and paws; the leaves grow out of a common stem and touch the head or arm.
green = union([
    capsule((2.5, -14.5, 2.5), (1.8, -17.7, 6.0), 2.5),
    capsule((1.8, -17.7, 6.0), (12.8, -18.5, 34.5), 2.5),
    capsule((.9, -18.0, 7.8), (3.2, -18.2, 8.8), 2.9),
    capsule((7.8, -19.0, 24.0), (11.4, -19.0, 25.2), 2.7),
    leaf((10.0, -17.8, 25.5), (21.0, -17.8, 34.5)),
    leaf((11.0, -17.3, 29.0), (23.0, -17.3, 38.0)),
    leaf((12.0, -16.8, 32.0), (22.0, -16.8, 41.0)),
])
whole_raw += green
black -= green
ivory -= green

# Pose from the reference: left paw rests against the cheek; right forearm
# wraps in front of the bamboo. Add after the ivory/green cuts so both paws
# remain clearly visible in the foreground and stay joined to the torso.
posed_arms = union([
    capsule((-15.4, -10.0, 20.0), (-14.3, -16.4, 28.6), 3.8),
    egg((-14.1, -18.5, 30.0), (4.8, 4.0, 5.0)),
    capsule((15.3, -10.0, 19.0), (11.8, -18.0, 24.3), 4.0),
    egg((9.2, -20.7, 25.3), (5.0, 4.0, 4.4)),
])
whole_raw += posed_arms
black += posed_arms
ivory -= posed_arms
green -= posed_arms

# Pads are shallow front-facing colour regions, not glued-on parts.
tan_parts = []
for x in (-11.2, 11.2):
    tan_parts.append(egg((x, -18.6, 5.3), (3.7, 1.7, 2.8)))
    for dx, dz in ((-2.7, 3.4), (0, 4.0), (2.7, 3.4)):
        tan_parts.append(egg((x+dx, -17.8, 5.3+dz), (1.05, 1.2, 1.0)))
tan = union(tan_parts)
whole_raw += tan
black -= tan
ivory -= tan
green -= tan

# The scarf opening is cut through every colour. An oval 25 x 18 mm is kept
# straight to the build plate; the core also removes any torso intrusion.
bore = ellipse_tube(12.5, 9, 59, (0, 18, -.5))
plate_clip = md.Manifold.cube((120, 120, 70)).translate((-60, -60, 0))
parts = {}
for name, shape in [('black', black), ('ivory', ivory), ('green', green), ('tan', tan)]:
    shape = (shape - bore) ^ plate_clip
    assert shape.volume() > 0, name
    mesh = shape.to_mesh()
    tri = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=True)
    assert tri.is_watertight and tri.volume > 0, name
    tri.export(OUT / f'panda-{name}.stl')
    parts[name] = {'volume_mm3': round(float(tri.volume), 2),
                   'bounds_mm': np.round(tri.bounds, 2).tolist(),
                   'components': len(tri.split()), 'faces': len(tri.faces)}

assembly = (whole_raw - bore) ^ plate_clip
whole = assembly.to_mesh()
whole_tri = trimesh.Trimesh(whole.vert_properties[:, :3], whole.tri_verts, process=True)
assert whole_tri.is_watertight and len(whole_tri.split()) == 1
whole_tri.export(OUT / 'panda-assembly-reference.stl')
report = {'unit': 'mm', 'one_printed_piece': True, 'colour_volumes': parts,
          'total_bounds_mm': np.round(whole_tri.bounds, 2).tolist(),
          'total_volume_mm3': round(float(whole_tri.volume), 2),
          'whole_watertight': True, 'whole_components': 1,
          'scarf_bore_mm': [25, 18], 'bore_axis': 'Z',
          'sleeve_height_mm': 25, 'physical_fit_tested': False}
(HERE / 'geometry.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
