"""Prévia 3D dos sólidos CAD V3: fechado, aberto e corte funcional."""
from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import cadquery as cq
from build_cad import P, HERE


def triangles(shape):
    vertices, faces = shape.val().tessellate(.18, .12)
    xyz = np.array([[v.x, v.y, v.z] for v in vertices])
    return xyz[np.asarray(faces)]


def add(ax, shape, color, edge="none", alpha=1.0):
    collection = Poly3DCollection(triangles(shape), facecolor=color,
                                  edgecolor=edge, linewidth=0, alpha=alpha)
    ax.add_collection3d(collection)


def spring(ax, open_angle=0):
    turns = 6.5
    t = np.linspace(0, turns * 2 * np.pi, 260)
    lower = P.moving_outer_top - P.spring_seat_depth
    # Abertura comprime a mola; a posição é ilustrativa mas usa os apoios reais.
    lower += abs(open_angle) / P.max_open_deg * 2.6
    upper = P.fixed_bottom + P.spring_seat_depth
    y = np.linspace(lower, upper, len(t))
    radius = P.spring_outer_d / 2 - .45
    x = P.spring_x + radius * np.cos(t)
    z = P.depth / 2 + radius * np.sin(t)
    ax.plot(x, y, z, color="#d7dde0", linewidth=2.0)


def setup(ax, title, azim=-65):
    ax.set_xlim(-4, 83); ax.set_ylim(-15, 47); ax.set_zlim(-3, 27)
    ax.set_box_aspect((87, 62, 30)); ax.view_init(elev=25, azim=azim)
    ax.set_axis_off(); ax.set_title(title, fontsize=15, fontweight="bold",
                                   color="#203842", pad=-4)


fixed = cq.importers.importStep(str(HERE / "corpo_fixo.step"))
moving = cq.importers.importStep(str(HERE / "braco_movel.step"))
upper_tpu = cq.importers.importStep(str(HERE / "tpu_superior.step"))
lower_tpu = cq.importers.importStep(str(HERE / "tpu_inferior.step"))
fig = plt.figure(figsize=(18, 6.8), dpi=170, facecolor="#f2f4f5")

ax = fig.add_subplot(1, 3, 1, projection="3d", facecolor="#f2f4f5")
add(ax, moving, "#566970"); add(ax, fixed, "#29363d")
add(ax, lower_tpu, "#168bd2"); add(ax, upper_tpu, "#168bd2")
spring(ax); setup(ax, "Fechado · junta alinhada")

ax = fig.add_subplot(1, 3, 2, projection="3d", facecolor="#f2f4f5")
opened = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), -P.max_open_deg)
opened_tpu = lower_tpu.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), -P.max_open_deg)
add(ax, opened, "#566970"); add(ax, fixed, "#29363d")
add(ax, opened_tpu, "#168bd2"); add(ax, upper_tpu, "#168bd2")
spring(ax, -P.max_open_deg)
# Cilindro Ø28 no último ponto validado da trajetória.
rod = cq.Workplane("XY").center(P.rod_x, 20.5).circle(14).extrude(P.depth)
add(ax, rod, "#7894a1", "none", .45)
setup(ax, "Aberto 45° · passagem Ø28 mm")

ax = fig.add_subplot(1, 3, 3, projection="3d", facecolor="#f2f4f5")
# Remove a metade frontal para expor eixo e berços internos reais.
clip = cq.Workplane("XY").box(90, 70, P.depth / 2,
       centered=(False, False, False)).translate((-5, -18, P.depth / 2))
add(ax, moving.cut(clip), "#596970")
add(ax, fixed.cut(clip), "#33444c")
add(ax, lower_tpu.cut(clip), "#168bd2")
add(ax, upper_tpu.cut(clip), "#168bd2")
spring(ax)
setup(ax, "Corte · eixo oculto e berços da mola", azim=-58)

fig.suptitle("Suporte de cana V3 — desenho profissional validado no CAD",
             fontsize=21, fontweight="bold", color="#203842", y=.98)
fig.text(.5, .045,
         "Curvas exteriores contínuas · eixo invisível · patilha integral · mola centrada",
         ha="center", fontsize=13, color="#4c6873")
fig.subplots_adjust(left=.01, right=.99, top=.82, bottom=.09, wspace=.01)
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-CAD.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
