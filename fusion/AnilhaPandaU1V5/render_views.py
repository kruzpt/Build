"""Seis vistas da geometria imprimível real do Panda V5."""
from pathlib import Path
import sys
import numpy as np
import trimesh
import manifold3d as md
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "fusion/tools"))
from generate_universo_stand import render_meshes

COLORS = (("black", "#252525"), ("ivory", "#F2E9DA"),
          ("green", "#73AE18"), ("tan", "#D8A36B"))
items = []
for name, color in COLORS:
    tri = trimesh.load(HERE / "stl" / f"panda-{name}.stl", force="mesh")
    mesh = md.Mesh(np.asarray(tri.vertices, dtype=np.float32),
                   np.asarray(tri.faces, dtype=np.uint32))
    items.append((md.Manifold(mesh), color))

views = (
    ("FRENTE", (0, -1, .18)),
    ("LATERAL ESQUERDA", (-1, -.08, .18)),
    ("LATERAL DIREITA", (1, -.08, .18)),
    ("TRASEIRA", (0, 1, .18)),
    ("PERSPETIVA FRONTAL 45°", (.68, -.68, .28)),
    ("PERSPETIVA TRASEIRA 45°", (-.68, .68, .28)),
)
font = ImageFont.load_default(size=22)
canvas = Image.new("RGB", (1800, 1980), "#F4F6F7")
draw = ImageDraw.Draw(canvas)
for index, (title, direction) in enumerate(views):
    panel = render_meshes(items, size=(600, 860), direction=direction, margin=58)
    x = (index % 3) * 600; y = (index // 3) * 920 + 95
    canvas.paste(panel, (x, y + 35))
    draw.text((x + 300, y), title, fill="#203842", font=font, anchor="ma")
draw.text((900, 28), "PANDA PREGUICOSO V5 - INSPECAO 360 GRAUS",
          fill="#203842", font=font, anchor="ma")
out = HERE.parents[1] / "designs/anilha-panda-u1-CAD-v5-seis-vistas.png"
canvas.save(out)
print(out)
