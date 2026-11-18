"""Detalhe do encaixe escalonado da mola V3."""
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
lower_shoulder = lower_face + P.spring_seat_h
lower_tip = lower_shoulder + P.spring_pilot_h
upper_face = P.fixed_bottom
upper_shoulder = upper_face - P.spring_seat_h
upper_tip = upper_shoulder - P.spring_pilot_h

ax.add_patch(Rectangle((3, 2), lower_face - 3, 18, facecolor="#566870",
                       edgecolor="#17272e", lw=2))
ax.add_patch(Rectangle((upper_face, 2), 7, 18, facecolor="#34444c",
                       edgecolor="#17272e", lw=2))
ax.add_patch(Rectangle((lower_face, z0-seat_r), P.spring_seat_h, 2*seat_r,
                       facecolor="#73858d", edgecolor="#17272e", lw=1.7))
ax.add_patch(Rectangle((lower_shoulder, z0-pilot_r), P.spring_pilot_h, 2*pilot_r,
                       facecolor="#94a5ac", edgecolor="#17272e", lw=1.7))
ax.add_patch(Rectangle((upper_shoulder, z0-seat_r), P.spring_seat_h, 2*seat_r,
                       facecolor="#73858d", edgecolor="#17272e", lw=1.7))
ax.add_patch(Rectangle((upper_tip, z0-pilot_r), P.spring_pilot_h, 2*pilot_r,
                       facecolor="#94a5ac", edgecolor="#17272e", lw=1.7))

# Mola ilustrada apoiada nos ombros e envolvendo os pilotos.
t = np.linspace(0, 12*np.pi, 420)
x = np.linspace(lower_shoulder, upper_shoulder, len(t))
radius = P.spring_outer_d/2
ax.plot(x, z0 + radius*np.sin(t), color="#17272e", lw=4)
ax.plot(x, z0 + radius*np.sin(t), color="#dce3e6", lw=2.2)

ax.annotate("ombro Ø8,6 × 1,2", xy=(lower_face+.6, z0+seat_r),
            xytext=(5, 22.8), fontsize=11, color="#203842",
            arrowprops=dict(arrowstyle="->", color="#203842", lw=1.5))
ax.annotate("piloto Ø4,2 × 2,2\nENTRA NA MOLA", xy=(lower_shoulder+1.1, z0+pilot_r),
            xytext=(11.5, 18.8), fontsize=11, fontweight="bold", color="#0878b5",
            arrowprops=dict(arrowstyle="->", color="#168bd2", lw=2))
ax.text((lower_shoulder+upper_shoulder)/2, 0.2,
        "A extremidade da mola apoia no ombro; o piloto menor impede deslocação lateral",
        ha="center", fontsize=10.5, color="#516a75")
ax.set_xlim(2, 33); ax.set_ylim(-2, 26); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("ENCAIXE DA MOLA — CORTE PELO EIXO", fontsize=18,
             fontweight="bold", color="#203842", pad=12)
fig.tight_layout()
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-encaixe-mola.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
