"""Render a middle-depth section through the actual CadQuery solids."""
from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import numpy as np

from build_cad import P, fixed_arm, moving_arm, HERE


def points(wire):
    edges = []
    for edge in wire.Edges():
        n = max(2, math.ceil(edge.Length() / .3))
        edges.append([(v.x, v.y) for v in edge.sample(n)[0]])
    path = edges.pop(0)
    while edges:
        last = np.array(path[-1])
        found = False
        for i, edge in enumerate(edges):
            if np.linalg.norm(np.array(edge[0]) - last) < .01:
                path.extend(edge[1:]); edges.pop(i); found = True; break
            if np.linalg.norm(np.array(edge[-1]) - last) < .01:
                path.extend(list(reversed(edge[:-1]))); edges.pop(i); found = True; break
        if not found:
            raise RuntimeError('Disconnected cross-section contour')
    return path


def section(ax, part, color, edge_color):
    wires = sorted(part.section(P.depth / 2).val().Wires(), key=lambda w: w.Length(), reverse=True)
    for i, wire in enumerate(wires):
        ax.add_patch(Polygon(points(wire), closed=True,
                             facecolor=color if i == 0 else '#f6f9fb',
                             edgecolor=edge_color, linewidth=1.5))


def scene(ax, angle):
    fixed = fixed_arm()
    jaw = moving_arm().rotate((P.pivot_x, P.pivot_y, 0),
                              (P.pivot_x, P.pivot_y, 1), angle)
    section(ax, fixed, '#2d4350', '#20333e')
    section(ax, jaw, '#e7a258', '#a9622f')
    # The yellow segment identifies the integral contact ramp in the concept.
    ramp = np.array([(64, 19.6), (67, 21.4), (68.8, 23.2), (69.7, 23.2)])
    if angle:
        a = math.radians(angle)
        delta = ramp - np.array([P.pivot_x, P.pivot_y])
        ramp = np.array([P.pivot_x, P.pivot_y]) + delta @ np.array([
            [math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
    ax.plot(ramp[:, 0], ramp[:, 1], color='#f0cf3e', linewidth=4,
            solid_capstyle='round')
    ax.add_patch(Circle((P.pivot_x, P.pivot_y), 1.7,
                        facecolor='#1681db', edgecolor='#075799', linewidth=1.5))
    if angle == 0:
        rod_x, rod_y = P.rod_center_x, P.rod_center_y
    else:
        rod_x, rod_y = 54, 11.5
    ax.add_patch(Circle((rod_x, rod_y), P.rod_max_d / 2,
                        facecolor='#bdcbd3', edgecolor='#667e8d', linewidth=2, alpha=.75))
    upper_y = P.upper_bottom + P.spring_pocket_depth
    rad = math.radians(angle)
    lower_y = P.pivot_y + math.sin(rad) * (P.spring_x - P.pivot_x) + math.cos(rad) * (
        P.jaw_left_top - P.spring_pocket_depth - P.pivot_y)
    ys = np.linspace(lower_y, upper_y, 15)
    xs = np.full_like(ys, P.spring_x)
    xs[1:-1:2] -= 1.5
    xs[2:-1:2] += 1.5
    ax.plot(xs, ys, color='#e4403d', linewidth=2.5)
    ax.set_xlim(-4, 76)
    ax.set_ylim(-6, 45)
    ax.set_aspect('equal')
    ax.axis('off')


fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), dpi=150, facecolor='#f6f9fb')
for ax, angle, title in zip(axes, (0, -32), ('Fechado', 'Aberto 32° · cana a entrar')):
    ax.set_facecolor('#f6f9fb')
    scene(ax, angle)
    ax.set_title(title, fontsize=18, color='#1b3b4a', fontweight='bold', pad=10)
fig.suptitle('Suporte de cana V1 · secção do CAD real ao meio da profundidade',
             fontsize=18, color='#1b3b4a')
fig.text(.5, .04, 'Veio em azul · mola esquemática em vermelho · recorte de entrada na ponta direita',
         ha='center', fontsize=12, color='#496775')
fig.subplots_adjust(top=.87, bottom=.1, wspace=.1)
fig.savefig(HERE.parents[1] / 'designs/suporte-cana-mola-v1-CAD.png',
            bbox_inches='tight', pad_inches=.25)
