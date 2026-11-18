"""Suporte de cana V3 — CAD profissional baseado no conceito aprovado.

Unidades em mm. O eixo Z é a profundidade; a cana é paralela a Z.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np


HERE = Path(__file__).resolve().parent
OUT = HERE / "stl"


@dataclass(frozen=True)
class Parameters:
    width_closed: float = 68.0
    tab_tip_x: float = 78.0
    height: float = 42.0
    depth: float = 22.0
    fixed_bottom: float = 25.0
    rod_x: float = 46.0
    rod_y: float = 21.5
    rod_max_d: float = 28.0
    rod_clearance: float = 0.8
    tpu_thickness: float = 1.2
    tpu_side_clearance: float = 0.5
    tpu_entry_recess: float = 3.0
    pivot_x: float = 21.5
    pivot_y: float = 20.0
    axle_d: float = 4.0
    moving_boss_r: float = 5.0
    cheek_r: float = 9.0
    cheek_t: float = 5.0
    axial_clearance: float = 0.45
    socket_clearance: float = 0.25
    spring_x: float = 14.5
    spring_outer_d: float = 7.0
    spring_seat_d: float = 8.6
    spring_pilot_d: float = 4.2
    spring_seat_h: float = 1.2
    spring_pilot_h: float = 2.2
    spring_gap_closed: float = 9.6
    moving_outer_top: float = 10.5
    max_open_deg: float = 45.0
    radial_motion_clearance: float = 0.55


P = Parameters()


def zcyl(x, y, r, z0, length):
    return cq.Workplane("XY").center(x, y).circle(r).extrude(length).translate((0, 0, z0))


def ycyl(x, z, r, y0, length):
    return cq.Solid.makeCylinder(r, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def zcone(x, y, r0, r1, z0, length):
    return cq.Solid.makeCone(r0, r1, length, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def rounded_box_xy(x, y, width, height, depth, radius):
    body = cq.Workplane("XY").box(width, height, depth, centered=(False, False, False)).translate((x, y, 0))
    return body.edges("|Z").fillet(radius)


def moving_arm(p=P):
    # Corpo baixo arredondado; a parede de contacto nasce de um arco verdadeiro.
    base = rounded_box_xy(0, 0, p.width_closed, p.moving_outer_top, p.depth, 2.2)
    structural_r = p.rod_max_d / 2 + p.rod_clearance + p.tpu_thickness
    outer_r = structural_r + 3.2
    cradle = zcyl(p.rod_x, p.rod_y, outer_r, 0, p.depth)
    cradle = cradle.intersect(
        cq.Workplane("XY").box(44, 25, p.depth + 2, centered=(False, False, False)).translate((25, 0, -1))
    )
    arm = base.union(cradle)

    # Patilha integral: a união começa na linha de fecho e só depois cresce.
    tab = (cq.Workplane("XY").polyline([
           (58.0, 6.0), (66.0, 6.0), (69.0, 9.0), (71.0, 14.0),
           (73.0, 19.0), (75.5, 22.5), (78.0, 24.0), (79.0, 25.2),
           (78.5, 26.8), (77.0, 28.0), (75.0, 27.6), (72.0, 26.5),
           (68.0, 25.6), (64.0, 25.0), (61.0, 23.0), (59.0, 17.0),
           (58.0, 11.0),
           ]).close().extrude(p.depth))
    try:
        tab = tab.edges("|Z").fillet(1.25)
    except Exception:
        pass
    arm = arm.union(tab)

    arm = arm.cut(zcyl(p.rod_x, p.rod_y, structural_r, -1, p.depth + 2))

    # Língua central e eixo integrado; as faces exteriores permanecem limpas.
    z0 = p.cheek_t + p.axial_clearance
    zlen = p.depth - 2 * z0
    boss = zcyl(p.pivot_x, p.pivot_y, p.moving_boss_r, z0, zlen)
    bridge = (cq.Workplane("XY").polyline([
              (12.0, 7.5), (25.5, 7.5), (27.0, 11.0),
              (26.0, 16.0), (25.0, 19.2), (18.0, 19.2),
              (16.0, 16.0), (15.0, 11.0), (12.0, 9.5),
              ]).close().extrude(zlen).translate((0, 0, z0)))
    try:
        bridge = bridge.edges("|Z").fillet(1.2)
    except Exception:
        pass
    arm = arm.union(bridge).union(boss)
    axle_z0 = p.cheek_t - 1.5
    axle_z1 = p.depth - p.cheek_t + 1.5
    arm = arm.union(zcyl(p.pivot_x, p.pivot_y, p.axle_d / 2,
                          axle_z0 + 1.0, axle_z1 - axle_z0 - 2.0))
    arm = arm.union(zcone(p.pivot_x, p.pivot_y, 1.2, p.axle_d / 2, axle_z0, 1.0))
    arm = arm.union(zcone(p.pivot_x, p.pivot_y, p.axle_d / 2, 1.2, axle_z1 - 1.0, 1.0))

    # Berço inferior: disco de apoio + piloto central para o interior da mola.
    seat_y = p.moving_outer_top
    arm = arm.union(ycyl(p.spring_x, p.depth / 2, p.spring_seat_d / 2,
                         seat_y, p.spring_seat_h))
    arm = arm.union(ycyl(p.spring_x, p.depth / 2, p.spring_pilot_d / 2,
                         seat_y + p.spring_seat_h, p.spring_pilot_h))

    # Acabamento das arestas exteriores sem atacar os encaixes funcionais.
    try:
        arm = arm.edges("|Z and (>X or <X)").fillet(0.7)
    except Exception:
        pass
    return arm.clean()


def fixed_body(p=P):
    # Casco superior de cantos contínuos, terminado na linha de fecho à direita.
    body = rounded_box_xy(0, p.fixed_bottom, p.width_closed, p.height - p.fixed_bottom,
                          p.depth, 2.5)
    structural_r = p.rod_max_d / 2 + p.rod_clearance + p.tpu_thickness
    body = body.cut(zcyl(p.rod_x, p.rod_y, structural_r, -1, p.depth + 2))

    # Faces exteriores largas: formam uma continuidade orgânica em redor do
    # eixo e escondem o mecanismo por completo.
    for z0 in (0, p.depth - p.cheek_t):
        cheek = zcyl(p.pivot_x, p.pivot_y, p.cheek_r, z0, p.cheek_t)
        neck = (cq.Workplane("XY").polyline([
                    (5.0, p.fixed_bottom), (31.0, p.fixed_bottom),
                    (29.0, 20.5), (26.0, 14.0), (22.5, 11.2),
                    (18.5, 11.2), (14.0, 14.0), (11.0, 19.5),
                    (9.0, 23.0),
                ]).close().extrude(p.cheek_t).translate((0, 0, z0)))
        try:
            neck = neck.edges("|Z").fillet(1.8)
        except Exception:
            pass
        body = body.union(cheek).union(neck)

    # Cavidades cegas para os munhões; pele exterior de 3,3 mm.
    socket_r = p.axle_d / 2 + p.socket_clearance
    body = body.cut(zcyl(p.pivot_x, p.pivot_y, socket_r, p.cheek_t - 1.7, 1.9))
    body = body.cut(zcyl(p.pivot_x, p.pivot_y, socket_r,
                         p.depth - p.cheek_t - 0.2, 1.9))

    # Berço superior oposto, centrado no mesmo eixo da mola e separado do veio.
    upper_face_y = p.fixed_bottom
    body = body.union(ycyl(p.spring_x, p.depth / 2, p.spring_seat_d / 2,
                           upper_face_y - p.spring_seat_h, p.spring_seat_h))
    body = body.union(ycyl(p.spring_x, p.depth / 2, p.spring_pilot_d / 2,
                           upper_face_y - p.spring_seat_h - p.spring_pilot_h,
                           p.spring_pilot_h))

    # Recorte de varrimento real em toda a profundidade. Produz uma junta
    # contínua de 0,55 mm e garante que o braço nunca toca nas faces exteriores.
    moving = moving_arm(p)
    for angle in np.linspace(0, -p.max_open_deg, 121):
        pose = moving.rotate((p.pivot_x, p.pivot_y, 0), (p.pivot_x, p.pivot_y, 1), float(angle))
        for dx, dy in ((0, 0), (p.radial_motion_clearance, 0), (-p.radial_motion_clearance, 0),
                       (0, p.radial_motion_clearance), (0, -p.radial_motion_clearance)):
            shifted = pose.translate((dx, dy, 0))
            if shifted.val() and shifted.val().Volume() > 0.001:
                body = body.cut(shifted)
    body = body.clean()
    solids = body.val().Solids()
    if len(solids) > 1:
        body = cq.Workplane(obj=max(solids, key=lambda solid: solid.Volume()))
    return body.clean()


def tpu_liners(p=P):
    inner_r = p.rod_max_d / 2 + p.rod_clearance
    outer_r = inner_r + p.tpu_thickness
    z0 = p.tpu_side_clearance
    depth = p.depth - 2 * p.tpu_side_clearance
    annulus = zcyl(p.rod_x, p.rod_y, outer_r, z0, depth).cut(
        zcyl(p.rod_x, p.rod_y, inner_r, z0 - .2, depth + .4))
    clip_width = 2 * outer_r + 2 - p.tpu_entry_recess
    upper_clip = cq.Workplane("XY").box(clip_width, outer_r + 2, depth + 2,
                 centered=(False, False, False)).translate((p.rod_x - outer_r - 1, p.rod_y, z0 - 1))
    lower_clip = cq.Workplane("XY").box(clip_width, outer_r + 2, depth + 2,
                 centered=(False, False, False)).translate((p.rod_x - outer_r - 1, p.rod_y - outer_r - 1, z0 - 1))
    return annulus.intersect(upper_clip).clean(), annulus.intersect(lower_clip).clean()


def passage_report(fixed, moving, upper_liner, lower_liner, p=P):
    """Procura uma trajetória contínua para o maior cilindro especificado."""
    opened = moving.rotate((p.pivot_x, p.pivot_y, 0), (p.pivot_x, p.pivot_y, 1), -p.max_open_deg)
    opened_lower_liner = lower_liner.rotate(
        (p.pivot_x, p.pivot_y, 0), (p.pivot_x, p.pivot_y, 1), -p.max_open_deg)
    diameter = p.rod_max_d
    radius = diameter / 2
    xs = [float(v) for v in np.linspace(82, p.rod_x, 19)]
    ys = [float(v) for v in np.linspace(4, 34, 61)]
    clear = []
    for x in xs:
        valid = []
        for y in ys:
            probe = zcyl(x, y, radius, -1, p.depth + 2)
            collision = (fixed.intersect(probe).val().Volume()
                         + opened.intersect(probe).val().Volume()
                         + upper_liner.intersect(probe).val().Volume()
                         + opened_lower_liner.intersect(probe).val().Volume())
            if collision < .01:
                valid.append(y)
        clear.append(valid)

    # Programação dinâmica: entre amostras de 2 mm em X, o centro pode variar
    # até 2,5 mm em Y, representando o movimento guiado pela rampa.
    parents = [{y: None for y in clear[0]}]
    for valid in clear[1:]:
        previous = parents[-1]
        current = {}
        for y in valid:
            candidates = [py for py in previous if abs(py - y) <= 2.5]
            if candidates:
                current[y] = min(candidates, key=lambda py: abs(py - y))
        parents.append(current)
    target_candidates = list(parents[-1])
    path = []
    if target_candidates:
        y = min(target_candidates, key=lambda value: abs(value - p.rod_y))
        for index in range(len(xs) - 1, -1, -1):
            path.append([round(xs[index], 2), round(y, 2)])
            parent = parents[index][y]
            if parent is not None:
                y = parent
        path.reverse()
    return {
        "tested_diameter_mm": diameter,
        "continuous_path_found": bool(path),
        "path_xy_mm": path,
        "x_samples": len(xs),
        "y_resolution_mm": 0.5,
        "smaller_diameters_covered_by_envelope_mm": [8, 16, 22],
    }


def spring_report(p=P):
    lower = (p.spring_x, p.moving_outer_top + p.spring_seat_h)
    upper = (p.spring_x, p.fixed_bottom - p.spring_seat_h)
    theta = math.radians(-p.max_open_deg)
    dx, dy = lower[0] - p.pivot_x, lower[1] - p.pivot_y
    opened_lower = (p.pivot_x + dx * math.cos(theta) - dy * math.sin(theta),
                    p.pivot_y + dx * math.sin(theta) + dy * math.cos(theta))
    closed_distance = math.dist(lower, upper)
    open_distance = math.dist(opened_lower, upper)
    return {
        "seat_distance_closed_mm": round(closed_distance, 3),
        "seat_distance_open_45deg_mm": round(open_distance, 3),
        "working_compression_mm": round(closed_distance - open_distance, 3),
        "proposed_free_length_mm": 12.0,
        "required_solid_length_max_mm": 5.5,
        "physical_force_test_required": True,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fixed, moving = fixed_body(), moving_arm()
    upper_liner, lower_liner = tpu_liners()
    for name, part in (("corpo_fixo", fixed), ("braco_movel", moving)):
        assert part.val().isValid() and len(part.val().Solids()) == 1, name
        cq.exporters.export(part, str(OUT / f"{name}.stl"), tolerance=.04, angularTolerance=.1)
        cq.exporters.export(part, str(HERE / f"{name}.step"))
    for name, liner in (("tpu_superior", upper_liner), ("tpu_inferior", lower_liner)):
        assert liner.val().isValid() and len(liner.val().Solids()) == 1, name
        cq.exporters.export(liner, str(OUT / f"{name}.stl"), tolerance=.035, angularTolerance=.08)
        cq.exporters.export(liner, str(HERE / f"{name}.step"))

    coupon_box = cq.Workplane("XY").box(34, 38, P.depth + 2,
                 centered=(False, False, False)).translate((-1, 6, -1))
    for name, part in (("cupao_corpo_fixo", fixed.intersect(coupon_box)),
                       ("cupao_braco_movel", moving.intersect(coupon_box))):
        solids = part.val().Solids()
        if len(solids) > 1:
            part = cq.Workplane(obj=max(solids, key=lambda solid: solid.Volume()))
        assert part.val().isValid() and len(part.val().Solids()) == 1, name
        cq.exporters.export(part, str(OUT / f"{name}.stl"), tolerance=.04, angularTolerance=.1)

    assembly = cq.Assembly(name="SuporteCanaMolaV3")
    assembly.add(fixed, name="corpo_fixo", color=cq.Color("#303b42"))
    assembly.add(moving, name="braco_movel", color=cq.Color("#46545c"))
    assembly.add(upper_liner, name="tpu_superior", color=cq.Color("#168bd2"))
    assembly.add(lower_liner, name="tpu_inferior", color=cq.Color("#168bd2"))
    assembly.save(str(HERE / "suporte-cana-mola-v3-conjunto.step"))

    collisions = {}
    for angle in np.linspace(0, -P.max_open_deg, 81):
        pose = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), float(angle))
        volume = fixed.intersect(pose).val().Volume()
        collisions[f"{angle:.1f}"] = round(volume, 5)
        assert volume < .02, (angle, volume)

    passage = passage_report(fixed, moving, upper_liner, lower_liner)
    assert passage["continuous_path_found"], passage
    spring = spring_report()
    report = {
        "parameters_mm": asdict(P),
        "maximum_part_intersection_mm3": max(collisions.values()),
        "intersection_by_angle_mm3": collisions,
        "cylindrical_passage_test": passage,
        "spring_kinematics": spring,
        "hidden_axis": True,
        "opposed_spring_seats": True,
        "wall_mount": {"type": "none", "screw_holes": 0},
        "physical_fit_tested": False,
        "status": "cad_v3_visual_and_kinematic_validation",
    }
    (HERE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
