"""Panda Preguiçoso V6 — correção localizada da pega e do bambu.

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


def ellipse_frustum(rx, ry, h, top_scale, center=(0, 0, 0), segments=128):
    return (md.Manifold.cylinder(h, 1, top_scale, circular_segments=segments)
            .scale((rx, ry, 1)).translate(center))


def head_tilt(shape):
    pivot = (0, -5.8, 28.0)
    return shape.translate(tuple(-v for v in pivot)).rotate((0, -11, 0)).translate(pivot)


# Núcleo preto estrutural: manga, corpo, ancas, pernas, pés e orelhas.
feet = [
    egg((-11.2, -12.4, 5.9), (7.7, 7.1, 6.5), rotation=(3, -8, -5)),
    egg((11.2, -12.4, 5.9), (7.7, 7.1, 6.5), rotation=(3, 8, 5)),
]
sleeve_chamfer_height = 1.2
sleeve_main_height = 25 - sleeve_chamfer_height
sleeve_outer = (
    ellipse_tube(15.5, 12, sleeve_main_height, (0, 18, 0)) +
    ellipse_frustum(15.5, 12, sleeve_chamfer_height, 15.0 / 15.5,
                     (0, 18, sleeve_main_height))
)
black = union([
    sleeve_outer,
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
stem = chain(((1.8, -17.8, 2.2), (2.7, -18.15, 8.0), (6.15, -18.5, 17.0),
              (9.8, -18.7, 27.0), (13.15, -18.15, 35.5)),
             (2.58, 2.54, 2.48, 2.42, 2.30), 56)
nodes = union([
    capsule((.8, -18.0, 7.8), (4.0, -18.2, 8.9), 2.68),
    capsule((7.7, -18.95, 23.9), (11.2, -18.85, 25.1), 2.56),
])
green = union([
    stem, nodes,
    leaf((10.4, -17.75, 26.1), (20.6, -17.25, 34.8), 2.65),
    leaf((11.5, -17.15, 29.6), (23.2, -16.65, 37.7), 2.82),
    leaf((12.4, -16.65, 32.6), (21.5, -15.9, 41.2), 2.58),
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
grip_channel = capsule((7.0, -19.2, 20.8), (12.0, -19.0, 29.5), 2.52, 56)
palm = palm_raw - grip_channel
fingers = union([
    chain(((6.0, -20.2, 27.5), (8.3, -21.0, 28.3),
           (10.0, -20.75, 28.25), (11.35, -20.1, 27.75)),
          (1.42, 1.52, 1.38, 1.20), 48),
    chain(((6.2, -20.35, 23.5), (8.5, -21.05, 22.75),
           (10.1, -20.85, 22.85), (11.55, -20.1, 23.35)),
          (1.42, 1.50, 1.36, 1.20), 48),
])
arms = union([left_arm, left_paw, right_arm, palm, fingers])
whole_raw += arms; black += arms; ivory -= arms; green -= arms

# Almofadas positivas com interface traseira plana. Cada cúpula é recortada no
# mesmo plano Y e esse mesmo sólido é subtraído da pata preta. Isto cria uma
# fronteira de material única, sem âncoras curvas a irromper pela superfície.
tan_parts = []
pad_interface_y = -17.75
front_pad_clip = md.Manifold.cube((120, pad_interface_y + 60, 70)).translate((-60, -60, 0))
for x in (-11.2, 11.2):
    large_dome = egg((x, -18.95, 5.35), (3.85, 1.65, 2.9), 64)
    tan_parts.append(large_dome ^ front_pad_clip)
    for dx, dz in ((-2.7, 3.45), (0, 4.15), (2.7, 3.45)):
        small_dome = egg((x + dx, -18.55, 5.35 + dz), (1.12, 1.18, 1.08), 56)
        tan_parts.append(small_dome ^ front_pad_clip)
tan = union(tan_parts)
whole_raw += tan; black -= tan; ivory -= tan; green -= tan

# Base técnica baixa e contínua, totalmente escondida na projeção normal do
# modelo. Une os contactos das patas, corpo, manga traseira e bambu num único
# primeiro estrato preto. As outras cores começam sobre a base, sem ilhas no ar.
base_height = 1.2
base_raw_height = base_height + .2
base_raw_z = -.2
print_base = union([
    ellipse_tube(15.2, 11.3, base_raw_height, (0, 17.8, base_raw_z)),
    ellipse_tube(14.5, 10.5, base_raw_height, (0, 3.0, base_raw_z)),
    ellipse_tube(10.0, 7.0, base_raw_height, (0, -9.0, base_raw_z)),
    ellipse_tube(8.0, 6.8, base_raw_height, (-11.0, -10.0, base_raw_z)),
    ellipse_tube(8.0, 6.8, base_raw_height, (11.0, -10.0, base_raw_z)),
    ellipse_tube(6.0, 5.0, base_raw_height, (1.5, -16.0, base_raw_z)),
])
whole_raw += print_base
black += print_base
ivory -= print_base
green -= print_base
tan -= print_base

# Tubo funcional: furo nominal 25 × 18 mm. Só os 1,2 mm superiores recebem
# chanfro, tanto no exterior como na entrada do furo; a face inferior permanece
# totalmente plana e com a área de contacto original.
bore_nominal = ellipse_tube(12.5, 9, 59, (0, 18, -.5))
bore_top_chamfer = ellipse_frustum(12.5, 9, sleeve_chamfer_height, 1.04,
                                   (0, 18, sleeve_main_height))
bore = bore_nominal + bore_top_chamfer
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
    duplicate_faces = len(tri.faces) - len(np.unique(np.sort(tri.faces, axis=1), axis=0))
    assert tri.is_watertight and tri.is_winding_consistent and tri.volume > 0, (
        name, tri.is_watertight, tri.is_winding_consistent, tri.volume,
        len(tri.faces), len(tri.split(only_watertight=False)))
    assert duplicate_faces == 0, (name, duplicate_faces)
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
        "duplicate_faces": duplicate_faces,
    }

assembly = (whole_raw - bore) ^ plate_clip
data = assembly.to_mesh()
whole = trimesh.Trimesh(data.vert_properties[:, :3], data.tri_verts, process=True)
whole.remove_unreferenced_vertices()
assert whole.is_watertight and whole.is_winding_consistent and len(whole.split()) == 1
whole.export(OUT / "panda-assembly-reference.stl")

# Verifica a primeira camada como uma única região contínua. A passagem oval é
# mantida aberta, mas o anel em seu redor continua ligado ao resto da base.
first_layer_slab = md.Manifold.cube((120, 120, .2)).translate((-60, -60, 0))
first_layer_shape = assembly ^ first_layer_slab
first_layer_data = first_layer_shape.to_mesh()
first_layer_mesh = trimesh.Trimesh(first_layer_data.vert_properties[:, :3],
                                   first_layer_data.tri_verts, process=True)
first_layer_mesh.remove_unreferenced_vertices()
first_layer_components = len(first_layer_mesh.split())
first_layer_area = float(first_layer_mesh.volume / .2)
assert first_layer_components == 1
assert first_layer_area > 900

# Mede as interseções reais: interfaces coincidentes são permitidas, volume não.
intersections = {}
names = list(meshes)
for i, first in enumerate(names):
    for second in names[i + 1:]:
        volume = float((final_shapes[first] ^ final_shapes[second]).volume())
        intersections[f"{first}_{second}"] = round(volume, 6)
        assert volume < .001, (first, second, volume)

tan_components = meshes["tan"].split()
tan_component_volumes = sorted(float(component.volume) for component in tan_components)
assert len(tan_components) == 8
assert tan_component_volumes[0] > 5.0
assert abs(float(meshes["tan"].bounds[1, 1]) - pad_interface_y) < .001

report = {
    "version": "premium_v6_local_grip_fix",
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
    "sleeve_edge_treatment": {
        "top_only": True,
        "chamfer_height_mm": sleeve_chamfer_height,
        "outer_top_radii_mm": [15.0, round(12 * 15.0 / 15.5, 3)],
        "inner_top_opening_mm": [26.0, 18.72],
        "bottom_edge_chamfer_mm": 0,
        "bottom_plane_z_mm": 0,
    },
    "print_base": {
        "plane_z_mm": 0,
        "height_mm": base_height,
        "first_layer_components": first_layer_components,
        "first_layer_contact_area_mm2": round(first_layer_area, 2),
        "designed_for_support_free_lower_zone": True,
        "slicer_support_analysis_performed": False,
    },
    "minimum_designed_leaf_thickness_mm": 3.1,
    "grip_revision": {
        "scope": "right hand, fingers and bamboo only",
        "green_black_overlap_mm3": intersections["black_green"],
        "grip_channel_radius_mm": 2.52,
        "isolated_green_components": max(0, len(meshes["green"].split()) - 1),
    },
    "paw_pad_geometry": {
        "feet": 2,
        "large_positive_pads": 2,
        "small_positive_pads": 6,
        "pads_per_foot": "1 oval + 3 round",
        "construction": "positive dome with single planar colour interface",
        "interface_plane_y_mm": pad_interface_y,
        "separate_colour_body": "tan",
        "component_count": len(tan_components),
        "smallest_component_volume_mm3": round(tan_component_volumes[0], 3),
        "unexpected_micro_components": 0,
        "maximum_rear_extent_y_mm": round(float(meshes["tan"].bounds[1, 1]), 3),
        "black_tan_overlap_mm3": intersections["black_tan"],
    },
    "target_printer": "Snapmaker U1",
    "physical_fit_tested": False,
}
(HERE / "geometry.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
