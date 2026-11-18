"""Vistas ortográficas dos contornos CAD reais da V3."""
from __future__ import annotations

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import cadquery as cq

from build_cad import P, HERE


def contour(wire):
    groups = []
    for edge in wire.Edges():
        groups.append([(v.x, v.y) for v in edge.sample(max(2, math.ceil(edge.Length() / .2)))[0]])
    path = groups.pop(0)
    while groups:
        last = np.asarray(path[-1])
        for index, edge in enumerate(groups):
            if np.linalg.norm(np.asarray(edge[0]) - last) < .02:
                path.extend(edge[1:]); groups.pop(index); break
            if np.linalg.norm(np.asarray(edge[-1]) - last) < .02:
                path.extend(list(reversed(edge[:-1]))); groups.pop(index); break
        else:
            break
    return path


def draw(ax, solid, z, color, edge):
    wires = sorted(solid.section(z).val().Wires(), key=lambda w: w.Length(), reverse=True)
    for index, wire in enumerate(wires):
        ax.add_patch(Polygon(contour(wire), closed=True,
                             facecolor=color if index == 0 else "#f4f6f7",
                             edgecolor=edge, linewidth=1.6))


fixed = cq.importers.importStep(str(HERE / "corpo_fixo.step"))
moving = cq.importers.importStep(str(HERE / "braco_movel.step"))
upper_tpu = cq.importers.importStep(str(HERE / "tpu_superior.step"))
lower_tpu = cq.importers.importStep(str(HERE / "tpu_inferior.step"))
opened = moving.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), -P.max_open_deg)
opened_tpu = lower_tpu.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), -P.max_open_deg)
fig, axes = plt.subplots(1, 3, figsize=(17, 6.2), dpi=170, facecolor="#f4f6f7")

for ax, movable, liner, title in ((axes[0], moving, lower_tpu, "Fechado"),
                                  (axes[1], opened, opened_tpu, "Aberto 45°")):
    ax.set_facecolor("#f4f6f7")
    draw(ax, movable, P.depth - .8, "#53676f", "#24343b")
    draw(ax, fixed, P.depth - .8, "#2c3a41", "#17252b")
    draw(ax, liner, P.depth - .8, "#168bd2", "#075b91")
    draw(ax, upper_tpu, P.depth - .8, "#168bd2", "#075b91")
    if movable is opened:
        ax.add_patch(Circle((P.rod_x, 20.5), 14, facecolor="#91aab5",
                            edgecolor="#4c6b78", linewidth=1.5, alpha=.55))
    ax.set_title(title, fontsize=19, fontweight="bold", color="#203842")
    ax.set(xlim=(-4, 83), ylim=(-15, 47), aspect="equal"); ax.axis("off")

ax = axes[2]; ax.set_facecolor("#f4f6f7")
draw(ax, moving, P.depth / 2, "#53676f", "#24343b")
draw(ax, fixed, P.depth / 2, "#2c3a41", "#17252b")
draw(ax, lower_tpu, P.depth / 2, "#168bd2", "#075b91")
draw(ax, upper_tpu, P.depth / 2, "#168bd2", "#075b91")
ax.add_patch(Circle((P.pivot_x, P.pivot_y), P.axle_d / 2,
                    facecolor="#d3dadd", edgecolor="#54666e", linewidth=1.2))
ys = np.linspace(P.moving_outer_top - P.spring_seat_depth,
                 P.fixed_bottom + P.spring_seat_depth, 17)
xs = P.spring_x + 1.8 * np.sin(np.linspace(0, 8 * np.pi, len(ys)))
ax.plot(xs, ys, color="#d3dadd", linewidth=2.4)
ax.set_title("Corte central do mecanismo", fontsize=19, fontweight="bold", color="#203842")
ax.set(xlim=(-4, 83), ylim=(-15, 47), aspect="equal"); ax.axis("off")

fig.suptitle("Suporte de cana V3 — contornos reais do CAD",
             fontsize=22, fontweight="bold", color="#203842", y=.97)
fig.text(.5, .045,
         "Eixo invisível na vista exterior · berços opostos · passagem validada Ø28 mm",
         ha="center", fontsize=13, color="#4c6873")
fig.subplots_adjust(left=.01, right=.99, top=.86, bottom=.09, wspace=.03)
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-vistas.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
