"""Detalhe do alojamento anular rebaixado da mola V3."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from build_cad import P, HERE


fig, ax = plt.subplots(figsize=(10, 5.5), dpi=180, facecolor="#f3f5f6")
ax.set_facecolor("#f3f5f6")

# Corte pelo eixo da mola: Y horizontal, Z vertical.
z0 = P.depth / 2
seat_r = P.spring_seat_d / 2
pilot_r = P.spring_pilot_d / 2
lower_face = P.moving_outer_top
upper_face = P.fixed_bottom
depth = P.spring_seat_depth
lower_floor = lower_face - depth
upper_floor = upper_face + depth

ax.add_patch(Rectangle((3, 2), lower_face - 3, 18, facecolor="#566870",
                       edgecolor="#17272e", lw=2))
ax.add_patch(Rectangle((upper_face, 2), 7, 18, facecolor="#34444c",
                       edgecolor="#17272e", lw=2))
# Retira visualmente apenas o anel: a ilha Ø4,2 permanece até à face original.
bg = "#f3f5f6"
for z in (z0-seat_r, z0+pilot_r):
    height = seat_r-pilot_r
    ax.add_patch(Rectangle((lower_floor, z), depth, height,
                           facecolor=bg, edgecolor="#17272e", lw=1.5))
    ax.add_patch(Rectangle((upper_face, z), depth, height,
                           facecolor=bg, edgecolor="#17272e", lw=1.5))

# Mola ilustrada com as extremidades inseridas nos dois rebaixos.
t = np.linspace(0, 12*np.pi, 420)
x = np.linspace(lower_floor, upper_floor, len(t))
radius = P.spring_outer_d/2
ax.plot(x, z0 + radius*np.sin(t), color="#17272e", lw=4)
ax.plot(x, z0 + radius*np.sin(t), color="#dce3e6", lw=2.2)

ax.annotate("rebaixo anular Ø8,6/Ø4,2 × 1,2", xy=(lower_floor+.5, z0+seat_r-.4),
            xytext=(5, 22.8), fontsize=11, color="#203842",
            arrowprops=dict(arrowstyle="->", color="#203842", lw=1.5))
ax.annotate("ilha central Ø4,2\nAO NÍVEL DA FACE", xy=(lower_face, z0),
            xytext=(11.5, 18.8), fontsize=11, fontweight="bold", color="#0878b5",
            arrowprops=dict(arrowstyle="->", color="#168bd2", lw=2))
ax.text((lower_face+upper_face)/2, 0.2,
        "A mola entra no anel rebaixado; a ilha central não fica saliente",
        ha="center", fontsize=10.5, color="#516a75")
ax.set_xlim(2, 33); ax.set_ylim(-2, 26); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("ENCAIXE DA MOLA — CORTE PELO EIXO", fontsize=18,
             fontweight="bold", color="#203842", pad=12)
fig.tight_layout()
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-encaixe-mola.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
