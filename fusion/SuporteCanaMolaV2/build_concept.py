"""Protótipo paramétrico V2 do suporte de cana, em milímetros.

Valida a cinemática pedida: mola de compressão entre os braços, veio à direita
da mola e recorte de varrimento para o braço móvel não tocar no corpo fixo.
Ainda não define a mola comercial nem constitui um projeto final de impressão.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import numpy as np


HERE = Path(__file__).resolve().parent
DESIGNS = HERE.parents[1] / "designs"


@dataclass(frozen=True)
class Parameters:
    width: float = 70.0
    height: float = 37.0
    depth: float = 20.0
    fixed_bottom: float = 23.0
    rod_x: float = 43.0
    rod_y: float = 18.5
    rod_d: float = 28.0  # margem para a maioria das canas; confirmar fisicamente
    rod_clearance: float = 0.7
    pivot_x: float = 21.0
    pivot_y: float = 18.7
    pivot_hole_d: float = 4.2
    moving_boss_r: float = 3.8
    fixed_ear_r: float = 5.4
    fixed_ear_t: float = 4.4
    axial_clearance: float = 0.4
    spring_x: float = 9.0
    spring_d: float = 7.0
    spring_seat_depth: float = 1.8
    spring_gap_closed: float = 12.0
    max_open_deg: float = 32.0
    sweep_clearance: float = 0.5


P = Parameters()


def zcyl(x, y, r, z0, length):
    return cq.Workplane("XY").center(x, y).circle(r).extrude(length).translate((0, 0, z0))


def ycyl(x, z, r, y0, length):
    return cq.Solid.makeCylinder(r, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def moving_arm(p=P):
    # Perfil contínuo. O pequeno ressalto redondo junto ao veio é o “calcanhar”
    # que gira dentro do recorte circular, em vez de duas faces baterem.
    outline = [
        (0, 0), (p.width - 2.0, 0), (p.width - 2.0, 12.5),
        (72.0, 19.0), (71.5, 21.8), (69.3, 23.2),
        (66.8, 22.2), (63.0, 18.8), (58.0, 16.0),
        (55.0, 18.2), (34.0, 18.2), (30.0, 14.2),
        (26.0, 11.3), (14.0, 11.3), (10.0, 9.5), (0, 9.5),
    ]
    arm = cq.Workplane("XY").polyline(outline).close().extrude(p.depth)
    rod_r = p.rod_d / 2 + p.rod_clearance
    arm = arm.cut(zcyl(p.rod_x, p.rod_y, rod_r, -1, p.depth + 2))

    z0 = p.fixed_ear_t + p.axial_clearance
    zlen = p.depth - 2 * z0
    boss = zcyl(p.pivot_x, p.pivot_y, p.moving_boss_r, z0, zlen)
    # Ponte suave entre o braço e o boss; a face superior fica abaixo do corpo.
    bridge = cq.Workplane("XY").polyline([
        (13.0, 9.0), (25.5, 9.0), (24.7, 14.5),
        (23.8, 18.7), (18.2, 18.7), (15.8, 13.0),
    ]).close().extrude(zlen).translate((0, 0, z0))
    arm = arm.union(bridge).union(boss)
    # Eixo integrado e escondido: os munhões entram em alojamentos cegos nas
    # faces interiores das orelhas fixas. Do exterior não existe furo visível.
    axle_z0 = p.fixed_ear_t - 1.5
    axle_z1 = p.depth - p.fixed_ear_t + 1.5
    arm = arm.union(zcyl(p.pivot_x, p.pivot_y, p.pivot_hole_d / 2,
                          axle_z0, axle_z1 - axle_z0))
    arm = arm.cut(ycyl(p.spring_x, p.depth / 2, p.spring_d / 2,
                        9.5 - p.spring_seat_depth, p.spring_seat_depth + 1.0))
    return arm.clean()


def fixed_body(p=P):
    base = cq.Workplane("XY").box(
        p.width, p.height - p.fixed_bottom, p.depth,
        centered=(False, False, False)).translate((0, p.fixed_bottom, 0))
    rod_r = p.rod_d / 2 + p.rod_clearance
    base = base.cut(zcyl(p.rod_x, p.rod_y, rod_r, -1, p.depth + 2))

    # Recorte baseado no volume realmente varrido pelo braço. As pequenas
    # translações dão 0,5 mm de folga radial de impressão.
    moving = moving_arm(p)
    sweep = None
    for angle in np.linspace(0, -p.max_open_deg, 17):
        pose = moving.rotate((p.pivot_x, p.pivot_y, 0), (p.pivot_x, p.pivot_y, 1), float(angle))
        for dx, dy in ((0, 0), (p.sweep_clearance, 0), (-p.sweep_clearance, 0),
                       (0, p.sweep_clearance), (0, -p.sweep_clearance)):
            shifted = pose.translate((dx, dy, 0))
            sweep = shifted if sweep is None else sweep.union(shifted)
    base = base.cut(sweep)

    # Orelhas exteriores fixas; o boss móvel roda entre elas.
    for z0 in (0, p.depth - p.fixed_ear_t):
        base = base.union(zcyl(p.pivot_x, p.pivot_y, p.fixed_ear_r, z0, p.fixed_ear_t))
    # Alojamentos cegos, abertos apenas do lado interior. Fica uma pele exterior
    # contínua que esconde completamente o eixo.
    socket_r = p.pivot_hole_d / 2 + 0.25
    base = base.cut(zcyl(p.pivot_x, p.pivot_y, socket_r,
                          p.fixed_ear_t - 1.7, 1.9))
    base = base.cut(zcyl(p.pivot_x, p.pivot_y, socket_r,
                          p.depth - p.fixed_ear_t - 0.2, 1.9))
    base = base.cut(ycyl(p.spring_x, p.depth / 2, p.spring_d / 2,
                         p.fixed_bottom - 0.5, p.spring_seat_depth + 1.0))
    return base.clean()


def section_points(wire):
    edges = []
    for edge in wire.Edges():
        edges.append([(v.x, v.y) for v in edge.sample(max(2, math.ceil(edge.Length() / .35)))[0]])
    path = edges.pop(0)
    while edges:
        last = np.array(path[-1])
        for i, edge in enumerate(edges):
            if np.linalg.norm(np.array(edge[0]) - last) < .02:
                path.extend(edge[1:]); edges.pop(i); break
            if np.linalg.norm(np.array(edge[-1]) - last) < .02:
                path.extend(list(reversed(edge[:-1]))); edges.pop(i); break
        else:
            break
    return path


def draw_section(ax, solid, color, edge, z=None):
    z = P.depth / 2 if z is None else z
    wires = sorted(solid.section(z).val().Wires(), key=lambda w: w.Length(), reverse=True)
    for i, wire in enumerate(wires):
        ax.add_patch(Polygon(section_points(wire), closed=True,
                             facecolor=color if i == 0 else "#f7f8f9",
                             edgecolor=edge, linewidth=1.7))


def render(fixed, moving):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.8), dpi=150, facecolor="#f7f8f9")
    top_skin_z = P.depth - 1.0
    for ax, angle, title in zip(axes[:2], (0, -P.max_open_deg), ("Fechado · eixo oculto", "Aberto 32° · eixo oculto")):
        pose = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), angle)
        draw_section(ax, pose, "#d79655", "#955526", top_skin_z)
        draw_section(ax, fixed, "#344b58", "#20333e", top_skin_z)
        # Mola esquemática no eixo correto entre as duas faces de apoio.
        lower = 9.5 if angle == 0 else 14.0
        ys = np.linspace(lower, P.fixed_bottom, 17)
        xs = P.spring_x + 1.6 * np.sin(np.linspace(0, 8 * np.pi, 17))
        ax.plot(xs, ys, color="#d9463e", linewidth=2.7)
        ax.set(xlim=(-3, 76), ylim=(-7, 42), aspect="equal")
        ax.axis("off"); ax.set_title(title, fontsize=18, fontweight="bold", color="#203b49")

    ax = axes[2]
    for angle, alpha in ((0, .95), (-10, .65), (-20, .4), (-32, .2)):
        pose = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), angle)
        wires = sorted(pose.section(top_skin_z).val().Wires(), key=lambda w: w.Length(), reverse=True)
        if wires:
            ax.add_patch(Polygon(section_points(wires[0]), closed=True,
                                 facecolor="#e4a25f", edgecolor="#955526", alpha=alpha))
    draw_section(ax, fixed, "#344b58", "#20333e", top_skin_z)
    ax.add_patch(Circle((P.pivot_x, P.pivot_y), P.pivot_hole_d / 2,
                        facecolor="none", edgecolor="#1689d4", linewidth=1.8,
                        linestyle="--"))
    ax.annotate("eixo interno\n(não atravessa a face)", xy=(P.pivot_x, P.pivot_y), xytext=(32, 33),
                arrowprops=dict(arrowstyle="->", color="#1689d4"), fontsize=11, color="#1689d4")
    ax.annotate("contorno curvo de sobreposição\n0,5 mm de folga", xy=(15, 24), xytext=(31, 38),
                arrowprops=dict(arrowstyle="->", color="#a2342e"), fontsize=12, color="#a2342e")
    ax.set(xlim=(-3, 76), ylim=(-7, 42), aspect="equal")
    ax.axis("off"); ax.set_title("Sobreposição e varrimento", fontsize=18, fontweight="bold", color="#203b49")
    fig.suptitle("Suporte de cana V2.1 — eixo escondido entre as duas peças",
                 fontsize=20, fontweight="bold", color="#203b49")
    fig.text(.5, .025, "A orelha escura cobre o eixo · a peça móvel entra entre as faces fixas",
             ha="center", fontsize=12, color="#496775")
    fig.subplots_adjust(top=.84, bottom=.1, wspace=.04)
    out = DESIGNS / "suporte-cana-mola-v2-varrimento.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=.25)
    return out


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "stl").mkdir(exist_ok=True)
    fixed, moving = fixed_body(), moving_arm()
    for name, part in (("corpo_fixo", fixed), ("braco_movel", moving)):
        assert part.val().isValid() and len(part.val().Solids()) == 1, name
        cq.exporters.export(part, str(HERE / "stl" / f"{name}.stl"), tolerance=.05)
        cq.exporters.export(part, str(HERE / f"{name}.step"))

    # Cupões curtos para validar primeiro o encaixe oculto e a mola, poupando
    # material antes de imprimir o conjunto completo.
    coupon_box = cq.Workplane("XY").box(31, 44, P.depth,
                 centered=(False, False, False)).translate((-2, -3, 0))
    for name, part in (("cupao_corpo_fixo", fixed.intersect(coupon_box)),
                       ("cupao_braco_movel", moving.intersect(coupon_box))):
        assert part.val().isValid() and len(part.val().Solids()) == 1, name
        cq.exporters.export(part, str(HERE / "stl" / f"{name}.stl"), tolerance=.05)

    assembly = cq.Assembly(name="SuporteCanaMolaV2")
    assembly.add(fixed, name="corpo_fixo", color=cq.Color("#344b58"))
    assembly.add(moving, name="braco_movel", color=cq.Color("#d79655"))
    assembly.save(str(HERE / "suporte-cana-mola-v2-conjunto.step"))

    collisions = {}
    for angle in np.linspace(0, -P.max_open_deg, 33):
        pose = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), float(angle))
        volume = fixed.intersect(pose).val().Volume()
        collisions[f"{angle:.1f}"] = round(volume, 5)
        assert volume < .01, (angle, volume)
    report = {
        "parameters_mm": asdict(P),
        "intersection_volume_mm3_by_angle": collisions,
        "maximum_intersection_mm3": max(collisions.values()),
        "physical_fit_tested": False,
        "hidden_snap_axle_tested": False,
        "status": "prototype_for_visual_and_motion_approval",
    }
    (HERE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    preview = render(fixed, moving)
    print(json.dumps({"preview": str(preview), **report}, indent=2))


if __name__ == "__main__":
    main()
