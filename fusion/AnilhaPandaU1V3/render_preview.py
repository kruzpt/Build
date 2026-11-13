"""Render the actual printable colour solids from two sides."""
from pathlib import Path
import sys
import numpy as np
import trimesh
import manifold3d as md
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'fusion/tools'))
from generate_universo_stand import render_meshes

items = []
for name, col in [('black', '#2B2B2B'), ('ivory', '#F2E9DA'),
                  ('green', '#79B515'), ('tan', '#DAA76E')]:
    tri = trimesh.load(HERE / 'stl' / f'panda-{name}.stl', force='mesh')
    mesh = md.Mesh(np.asarray(tri.vertices, dtype=np.float32),
                   np.asarray(tri.faces, dtype=np.uint32))
    items.append((md.Manifold(mesh), col))

front = render_meshes(items, size=(900, 950), direction=(0, -.94, .34), margin=80)
back = render_meshes(items, size=(900, 950), direction=(.65, .65, .4), margin=80)
out = Image.new('RGB', (1800, 1020), 'white')
out.paste(front, (0, 70))
out.paste(back, (900, 70))
d = ImageDraw.Draw(out)
d.text((350, 20), 'FRENTE', fill='#172B30')
d.text((1250, 20), 'COSTAS E TUBO', fill='#172B30')
out.save(HERE.parents[1] / 'designs/anilha-panda-u1-CAD-v3.png')
