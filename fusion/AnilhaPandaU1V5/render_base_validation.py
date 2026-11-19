"""Prancha dedicada à validação visual da base de impressão do Panda V5."""
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
    ("BASE - FRENTE BAIXA", (0, -1, .04)),
    ("BASE - TRASEIRA BAIXA", (0, 1, .04)),
    ("PLANO INFERIOR Z=0", (.001, 0, -1)),
)
font = ImageFont.load_default(size=22)
canvas = Image.new("RGB", (1800, 760), "#F4F6F7")
draw = ImageDraw.Draw(canvas)
for index, (title, direction) in enumerate(views):
    panel = render_meshes(items, size=(600, 650), direction=direction, margin=55)
    x = index * 600
    canvas.paste(panel, (x, 82))
    draw.text((x + 300, 52), title, fill="#203842", font=font, anchor="ma")
draw.text((900, 18), "PANDA V5 - VALIDACAO DA BASE DE IMPRESSAO",
          fill="#203842", font=font, anchor="ma")
out = HERE.parents[1] / "designs/anilha-panda-u1-CAD-v5-validacao-base.png"
canvas.save(out)
print(out)
