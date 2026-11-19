"""Panda Preguiçoso V5 premium — quatro volumes de cor fechados.

Unidades mm. X lateral, Y frente/trás, Z altura. O furo do lenço usa o eixo Z.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import manifold3d as md
import trimesh

HERE = Path(__file__).resolve().parent
OUT = HERE / "stl"
OUT.mkdir(parents=True, exist_ok=True)


def egg(center, radii, segments=64, rotation=(0, 0, 0)):
    shape = md.Manifold.sphere(1, segments).scale(radii)
    if any(rotation):
        shape = shape.rotate(rotation)
    return shape.translate(center)


def union(items):
    result = items[0]
    for item in items[1:]:
        result += item
    return result


def chain(points, radii, segments=48):
    """Curva orgânica C0 contínua por invólucros convexos sobrepostos."""
    nodes = [egg(p, (r, r, r), segments) for p, r in zip(points, radii)]
    return union([(a + b).hull() for a, b in zip(nodes, nodes[1:])])


def capsule(a, b, radius, segments=48):
    return chain((a, b), (radius, radius), segments)


def leaf(root, tip, width=2.8, thickness=1.55):
    mid = tuple((a + b) / 2 for a, b in zip(root, tip))
    return union([
        egg(root, (1.35, thickness, 1.35), 48),
        egg(mid, (width, thickness, width * .82), 48),
        egg(tip, (.42, .55, .62), 32),
    ]).hull()


def ellipse_tube(rx, ry, h, center=(0, 0, 0), segments=128):
    return md.Manifold.cylinder(h, 1, circular_segments=segments).scale((rx, ry, 1)).translate(center)


def head_tilt(shape):
    pivot = (0, -5.8, 28.0)
    return shape.translate(tuple(-v for v in pivot)).rotate((0, -11, 0)).translate(pivot)


# Núcleo preto estrutural: manga, corpo, ancas, pernas, pés e orelhas.
feet = [
    egg((-11.2, -12.4, 5.9), (7.7, 7.1, 6.5), rotation=(3, -8, -5)),
    egg((11.2, -12.4, 5.9), (7.7, 7.1, 6.5), rotation=(3, 8, 5)),
]
black = union([
    ellipse_tube(15.5, 12, 25, (0, 18, 0)),
    egg((0, -2.0, 13.0), (15.7, 11.6, 14.5)),
    egg((0, 4.5, 13.0), (13.8, 9.0, 11.5)),
    egg((-11.8, -6.5, 12.5), (8.2, 8.6, 10.8), rotation=(0, -9, -5)),
    egg((11.8, -6.5, 12.5), (8.2, 8.6, 10.8), rotation=(0, 9, 5)),
    *feet,
    head_tilt(egg((-14.7, -5.5, 48.8), (6.2, 5.7, 7.5), 64, (0, 0, -8))),
    head_tilt(egg((14.7, -5.5, 46.5), (6.2, 5.7, 7.5), 64, (0, 0, 8))),
])

# Cabeça e barriga creme com formas menos esféricas e transições mais amplas.
ivory = union([
    head_tilt(egg((0, -5.6, 37.0), (19.5, 14.3, 15.3), 80, (2, 0, 0))),
    egg((0, -11.0, 13.0), (9.4, 5.8, 12.8), 64),
])
whole_raw = black + ivory
black -= ivory

# Manchas, nariz e sorriso subtil integrados na curvatura da face.
marks = head_tilt(union([
    egg((-7.8, -16.9, 40.0), (6.0, 3.0, 6.5), 64, (2, 0, -7)),
    egg((7.8, -16.9, 40.0), (6.0, 3.0, 6.5), 64, (2, 0, 7)),
    egg((0, -18.8, 33.8), (2.2, 2.0, 1.5), 56),
    chain(((-4.1, -18.1, 31.0), (-2.0, -18.0, 30.1), (0, -18.0, 29.8),
           (2.0, -18.0, 30.1), (4.1, -18.1, 31.0)),
          (.62, .62, .62, .62, .62), 40),
]))
whole_raw += marks; ivory -= marks; black += marks

# Olhos semicerrados assimétricos, sobrancelhas pesadas e pupilas orientadas.
whites = head_tilt(union([
    egg((-7.8, -19.0, 37.5), (3.25, 1.25, 1.85), 56, (0, 0, -3)),
    egg((7.8, -19.0, 37.6), (3.15, 1.25, 1.75), 56, (0, 0, 3)),
]))
whole_raw += whites; black -= whites; ivory += whites
pupils = head_tilt(union([
    egg((-7.0, -19.75, 37.25), (1.0, .8, 1.15), 48),
    egg((7.2, -19.75, 37.3), (1.0, .8, 1.15), 48),
    capsule((-11.6, -19.42, 39.05), (-4.0, -19.42, 39.3), .76),
    capsule((4.0, -19.42, 39.3), (11.6, -19.42, 39.0), .76),
]))
whole_raw += pupils; ivory -= pupils; black += pupils

# Bambu contínuo com nós e folhas espessas ligadas ao caule.
stem = chain(((1.8, -17.8, 2.2), (2.8, -18.1, 8.0), (6.2, -18.5, 17.0),
              (9.8, -18.7, 27.0), (12.9, -18.3, 35.5)),
             (2.55, 2.55, 2.48, 2.42, 2.35), 56)
nodes = union([
    capsule((.7, -18.0, 7.7), (4.2, -18.2, 9.0), 2.85),
    capsule((7.5, -19.0, 23.8), (11.4, -18.9, 25.2), 2.72),
])
green = union([
    stem, nodes,
    leaf((10.3, -17.7, 26.0), (21.0, -17.4, 34.5), 2.7),
    leaf((11.3, -17.2, 29.5), (23.0, -16.9, 38.0), 2.8),
    leaf((12.2, -16.7, 32.5), (21.8, -16.2, 41.0), 2.65),
])
whole_raw += green; black -= green; ivory -= green

# Braço esquerdo: curva ombro–cotovelo–pulso–pata, com inserção profunda no corpo.
left_arm = chain(((-12.8, -7.0, 18.0), (-16.2, -10.5, 22.0),
                  (-17.0, -14.0, 26.0), (-15.2, -16.6, 29.0)),
                 (5.0, 4.7, 4.25, 3.9), 56)
left_paw = egg((-13.9, -18.0, 30.5), (4.8, 3.7, 5.0), 64, (5, -8, -10))

# Braço direito e palma vazada: o bambu continua visível no interior da pega.
right_arm = chain(((12.8, -7.0, 17.5), (15.5, -11.0, 20.5),
                   (14.2, -14.5, 23.0), (11.8, -17.0, 24.5)),
                  (5.0, 4.7, 4.2, 3.8), 56)
palm_raw = egg((9.4, -19.0, 25.2), (5.1, 3.5, 4.5), 64, (0, 8, -8))
grip_channel = capsule((7.0, -19.2, 20.8), (12.0, -19.0, 29.5), 2.72, 56)
palm = palm_raw - grip_channel
fingers = union([
    chain(((6.0, -20.2, 27.5), (8.5, -21.0, 28.2), (11.3, -20.2, 27.8)),
          (1.35, 1.35, 1.3), 44),
    chain(((6.2, -20.4, 23.5), (8.8, -21.1, 22.8), (11.6, -20.2, 23.3)),
          (1.35, 1.35, 1.3), 44),
])
arms = union([left_arm, left_paw, right_arm, palm, fingers])
whole_raw += arms; black += arms; ivory -= arms; green -= arms

# Almofadas positivas: cada uma tem uma âncora dentro da pata e uma cúpula
# saliente no exterior. A âncora impede que o slicer as trate como uma simples
# superfície encostada; a cúpula mantém o aspeto fofo da referência.
tan_parts = []
for x in (-11.2, 11.2):
    large_anchor = egg((x, -17.55, 5.35), (3.25, 1.05, 2.35), 56)
    large_dome = egg((x, -19.05, 5.35), (3.85, 1.55, 2.9), 64)
    tan_parts.append(large_anchor + large_dome)
    for dx, dz in ((-2.7, 3.45), (0, 4.15), (2.7, 3.45)):
        small_anchor = egg((x + dx, -17.15, 5.35 + dz), (.82, .72, .78), 48)
        small_dome = egg((x + dx, -18.65, 5.35 + dz), (1.12, 1.10, 1.08), 56)
        tan_parts.append(small_anchor + small_dome)
tan = union(tan_parts)
whole_raw += tan; black -= tan; ivory -= tan; green -= tan

# Tubo funcional preservado: passagem oval 25 × 18 mm, 25 mm de altura útil.
bore = ellipse_tube(12.5, 9, 59, (0, 18, -.5))
plate_clip = md.Manifold.cube((120, 120, 70)).translate((-60, -60, 0))
raw_parts = (("black", black), ("ivory", ivory), ("green", green), ("tan", tan))
parts = {}
meshes = {}
final_shapes = {}
for name, shape in raw_parts:
    shape = (shape - bore) ^ plate_clip
    assert shape.volume() > 0, name
    data = shape.to_mesh()
    tri = trimesh.Trimesh(data.vert_properties[:, :3], data.tri_verts, process=True)
    tri.remove_unreferenced_vertices()
    assert tri.is_watertight and tri.is_winding_consistent and tri.volume > 0, name
    tri.export(OUT / f"panda-{name}.stl")
    final_shapes[name] = shape
    meshes[name] = tri
    parts[name] = {
        "volume_mm3": round(float(tri.volume), 2),
        "bounds_mm": np.round(tri.bounds, 2).tolist(),
        "components": len(tri.split()),
        "faces": len(tri.faces),
        "watertight": True,
        "winding_consistent": True,
    }

assembly = (whole_raw - bore) ^ plate_clip
data = assembly.to_mesh()
whole = trimesh.Trimesh(data.vert_properties[:, :3], data.tri_verts, process=True)
whole.remove_unreferenced_vertices()
assert whole.is_watertight and whole.is_winding_consistent and len(whole.split()) == 1
whole.export(OUT / "panda-assembly-reference.stl")

# Mede as interseções reais: interfaces coincidentes são permitidas, volume não.
intersections = {}
names = list(meshes)
for i, first in enumerate(names):
    for second in names[i + 1:]:
        volume = float((final_shapes[first] ^ final_shapes[second]).volume())
        intersections[f"{first}_{second}"] = round(volume, 6)
        assert volume < .001, (first, second, volume)

report = {
    "version": "premium_v5",
    "unit": "mm",
    "one_printed_piece": True,
    "colour_volumes": parts,
    "total_bounds_mm": np.round(whole.bounds, 2).tolist(),
    "total_volume_mm3": round(float(whole.volume), 2),
    "whole_watertight": True,
    "whole_winding_consistent": True,
    "whole_components": 1,
    "controlled_colour_intersection_mm3": intersections,
    "scarf_bore_mm": [25, 18],
    "bore_axis": "Z",
    "sleeve_height_mm": 25,
    "minimum_designed_leaf_thickness_mm": 3.1,
    "paw_pad_geometry": {
        "feet": 2,
        "large_positive_pads": 2,
        "small_positive_pads": 6,
        "pads_per_foot": "1 oval + 3 round",
        "construction": "embedded anchor plus proud exterior dome",
        "separate_colour_body": "tan",
    },
    "target_printer": "Snapmaker U1",
    "physical_fit_tested": False,
}
(HERE / "geometry.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
