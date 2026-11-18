"""Vista da face real de parede e dos dois encaixes traseiros V3."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path

from build_cad import HERE, P


fig, ax = plt.subplots(figsize=(10, 5.2), dpi=180, facecolor="#f2f4f5")
ax.set_facecolor("#f2f4f5")

# Projeção ortogonal da face X=0: horizontal = profundidade Z; vertical = Y.
face = FancyBboxPatch((0, P.fixed_bottom), P.depth, P.height - P.fixed_bottom,
                      boxstyle="round,pad=0,rounding_size=2.4",
                      facecolor="#33444c", edgecolor="#1e2a30", linewidth=2.0)
ax.add_patch(face)

for z in (5.5, P.depth - 5.5):
    # Cabeça Ø8,6 e canal para haste 4,6; o canal desce 6 mm.
    ax.add_patch(Circle((z, 35.0), 4.3, facecolor="#d9e0e3",
                        edgecolor="#16252c", linewidth=1.8))
    verts = [(z - 2.3, 35.0), (z - 2.3, 29.0),
             (z + 2.3, 29.0), (z + 2.3, 35.0), (z - 2.3, 35.0)]
    ax.add_patch(PathPatch(Path(verts), facecolor="#d9e0e3",
                           edgecolor="#16252c", linewidth=1.8))
    ax.annotate("", xy=(z, 28.3), xytext=(z, 34.7),
                arrowprops=dict(arrowstyle="-|>", color="#e1a400", lw=2.2))

ax.text(P.depth / 2, 45.3, "FACE TRASEIRA — ENCOSTA À PAREDE",
        ha="center", va="bottom", fontsize=14, fontweight="bold", color="#203842")
ax.text(P.depth / 2, 21.8,
        "Dois parafusos pré-instalados · encaixar as cabeças · deslizar 6 mm para baixo",
        ha="center", va="top", fontsize=10.5, color="#4c6873")
ax.text(P.depth + 3.0, 35.0, "Ø8,6 mm\n(cabeça)", va="center", fontsize=10, color="#203842")
ax.text(P.depth + 3.0, 29.7, "4,6 mm\n(canal)", va="center", fontsize=10, color="#203842")
ax.set_xlim(-2.5, 36); ax.set_ylim(19, 49)
ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(pad=1)
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-fixacao-traseira.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
