"""Vista da face larga e das duas posições de parafuso V3."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

from build_cad import HERE, P


fig, ax = plt.subplots(figsize=(10, 5.2), dpi=180, facecolor="#f2f4f5")
ax.set_facecolor("#f2f4f5")

# Projeção ortogonal da face larga Z=22: horizontal = X; vertical = Y.
face = FancyBboxPatch((0, P.fixed_bottom), P.width_closed, P.height - P.fixed_bottom,
                      boxstyle="round,pad=0,rounding_size=2.4",
                      facecolor="#33444c", edgecolor="#1e2a30", linewidth=2.0)
ax.add_patch(face)

for x in (16.0, 60.0):
    ax.add_patch(Circle((x, 35.0), 4.2, facecolor="#d9e0e3",
                        edgecolor="#16252c", linewidth=1.8))
    ax.add_patch(Circle((x, 35.0), 2.15, facecolor="#7f929b",
                        edgecolor="#16252c", linewidth=1.2))

ax.text(P.width_closed / 2, 45.3, "FACE LARGA EXTERIOR — PARAFUSOS M4",
        ha="center", va="bottom", fontsize=14, fontweight="bold", color="#203842")
ax.text(P.width_closed / 2, 21.8,
        "Eixos perpendiculares à parede · face larga oposta Z=0 encostada à parede",
        ha="center", va="top", fontsize=10.5, color="#4c6873")
ax.text(P.width_closed + 3.0, 35.0, "Ø4,3 mm\nEscareado Ø8,4 mm",
        va="center", fontsize=10, color="#203842")
ax.set_xlim(-3, 88); ax.set_ylim(19, 49)
ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(pad=1)
out = HERE.parents[1] / "designs/suporte-cana-mola-v3-fixacao-traseira.png"
fig.savefig(out, bbox_inches="tight", pad_inches=.2)
print(out)
