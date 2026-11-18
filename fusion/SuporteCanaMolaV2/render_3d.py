"""Render 3D simples a partir dos sólidos CAD reais."""
from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_concept import P, fixed_body, moving_arm, DESIGNS


def mesh(shape):
    vertices, triangles = shape.val().tessellate(0.22, 0.18)
    xyz = np.array([[v.x, v.y, v.z] for v in vertices])
    return xyz[np.array(triangles)]


def add(ax, shape, color, edge="#25333b", alpha=1.0):
    poly = Poly3DCollection(mesh(shape), facecolor=color, edgecolor=edge,
                            linewidth=.08, alpha=alpha)
    ax.add_collection3d(poly)


def scene(ax, angle, title):
    fixed = fixed_body()
    moving = moving_arm().rotate((P.pivot_x, P.pivot_y, 0),
                                 (P.pivot_x, P.pivot_y, 1), angle)
    add(ax, moving, "#d9924d", "#75451f")
    add(ax, fixed, "#344b58", "#1d2d35")
    # Mola apenas ilustrativa, colocada entre os apoios reais.
    turns = 7
    y0 = 9.8 if angle == 0 else 13.4
    t = np.linspace(0, turns * 2 * np.pi, 220)
    y = np.linspace(y0, P.fixed_bottom - .2, len(t))
    x = P.spring_x + (P.spring_d / 2 - .5) * np.cos(t)
    z = P.depth / 2 + (P.spring_d / 2 - .5) * np.sin(t)
    ax.plot(x, y, z, color="#d8dde0", linewidth=2.2)
    ax.set_xlim(-4, 75); ax.set_ylim(-7, 42); ax.set_zlim(-4, 27)
    ax.set_box_aspect((79, 49, 31))
    ax.view_init(elev=27, azim=-66)
    ax.set_axis_off()
    ax.set_title(title, fontsize=18, fontweight="bold", color="#203b49", pad=4)


fig = plt.figure(figsize=(15, 7), dpi=170, facecolor="#f4f6f7")
for index, angle, title in ((1, 0, "Fechado"), (2, -P.max_open_deg, "Aberto 32°")):
    ax = fig.add_subplot(1, 2, index, projection="3d", facecolor="#f4f6f7")
    scene(ax, angle, title)
fig.suptitle("Suporte de cana V2.1 — prévia dos sólidos CAD",
             fontsize=22, fontweight="bold", color="#203b49", y=.94)
fig.text(.5, .055,
         "Eixo oculto pelas orelhas exteriores · mola de compressão entre as duas peças",
         ha="center", fontsize=13, color="#496775")
fig.subplots_adjust(left=.01, right=.99, top=.88, bottom=.08, wspace=.02)
fig.savefig(DESIGNS / "suporte-cana-mola-v2-render-3d.png",
            bbox_inches="tight", pad_inches=.2)
