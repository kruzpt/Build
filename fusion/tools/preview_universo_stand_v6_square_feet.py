"""V6 proposal image only: 7 mm backrest and support-free square foot edges.

The new contacts are uncut edges. Their height is solved before rendering;
there is no need for the previous broad bevel on the printed underside.
No production STL, Fusion definition or 3MF is exported by this preview.
"""
import json
import math

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_joana_topper import section_groups
import generate_universo_stand_v4 as v4


ROOT = v4.ROOT
PREFIX = 'universo-saber-suporte-v6-proposta-sem-suportes'
BLUE, WHITE = v4.BLUE, v4.WHITE
BACK_T = 7.0
SHELF_T = 6.0
GAP = 0.30
H, W = 200.0, 80.0
B = 72.0
L = 111.0
ANGLE = 70.0
A = math.radians(ANGLE)
S, C = math.sin(A), math.cos(A)
# With square edges, the backrest touches at local (y,z)=(0,0), and the
# rear base edge touches at (y,z)=(0,0).  C_cross*S - B*C must equal zero.
CROSSING = B/math.tan(A)
WINDOW_Y = 81.0
PAD_Y = 98.0


def geometry():
    back = v4.rounded(-W/2, 0, W, H, 3)
    back -= v4.rect(-9, -2, 18, 8) + md.CrossSection.circle(9, 40).translate((0, 6))
    # This slot receives the unchanged 6 mm blue base.
    back -= v4.rect(-W/2-1, CROSSING-GAP/2, W/2+1+GAP/2, SHELF_T+GAP)
    white = back.extrude(BACK_T)
    relief = v4.decoration().extrude(.8).translate((0, 0, BACK_T))

    shelf = v4.rounded(-W/2, 0, W, L, 3)
    # This slot receives the new 7 mm white backrest.
    shelf -= v4.rect(-W/2-1, B-GAP/2, W/2+1+GAP/2, BACK_T+GAP)
    shelf -= v4.rounded(-9, WINDOW_Y, 18, 20, 3)
    blue = shelf.extrude(SHELF_T)
    pads = [v4.rounded(x-9, PAD_Y, 18, 6, 1.4) for x in (-26, 26)]
    blue = v4.union([blue] + [p.extrude(4).translate((0, 0, SHELF_T)) for p in pads])

    back_mat = np.array([[1, 0, 0, 0], [0, C, -S, 0],
                         [0, S, C, 0], [0, 0, 0, 1]], float)
    base_in_back = np.array([[-1, 0, 0, 0], [0, 0, 1, CROSSING],
                             [0, 1, 0, -B], [0, 0, 0, 1]], float)
    transforms = (back_mat, back_mat, back_mat@base_in_back)
    solids = (white, relief, blue)
    assembled = [v4.transform(solid, matrix) for solid, matrix in zip(solids, transforms)]
    return back, shelf, solids, assembled, transforms


def verify(solids, assembled, transforms):
    white, relief, blue = solids
    aw, ar, ab = assembled
    assert all(s.status() == md.Error.NoError for s in solids)
    assert len(v4.union([white, relief]).decompose()) == 1
    assert len(blue.decompose()) == 1
    assert (aw^ab).volume() < 1e-5 and (ar^ab).volume() < 1e-5
    contacts = []
    contact_minima = []
    for solid in (aw, ab):
        vertices = v4.vertices(solid)
        z = float(vertices[:, 2].min())
        assert abs(z) < 1e-5
        contact_minima.append(z)
        contacts.extend(vertices[np.abs(vertices[:, 2]) < 1e-5, :2].tolist())
    hull = cv2.convexHull(np.asarray(contacts, np.float32)).reshape(-1, 2)
    assert cv2.contourArea(hull) > 4500
    for dx in np.linspace(0, 82, 42):
        assert (aw ^ ab.translate((-float(dx), 0, 0))).volume() < 1e-5

    phone_gaps = []
    for length, width, thickness in [(145, 65, 8), (165, 80, 14), (180, 90, 17)]:
        phone = md.Manifold.cube((width, length, thickness)).translate(
            (-width/2, CROSSING+SHELF_T, BACK_T+.9))
        assert (v4.transform(phone, transforms[0]) ^ v4.union(assembled)).volume() < 1e-5
        phone_gaps.append(thickness)
    for phone_t, plug_w, plug_t in [(8, 10, 5), (10, 12, 6), (14, 12, 8), (17, 12, 8)]:
        center_y = B+BACK_T+.9+phone_t/2
        plug = md.Manifold.cube((plug_w, plug_t, 12)).translate((-plug_w/2, center_y-plug_t/2, -12))
        for dz in np.linspace(-8, 6, 29):
            moving = plug.translate((0, 0, float(dz)))
            assert (moving^blue).volume() < 1e-5
            # Both pieces are also tested while the housing approaches the port.
            base_to_back = np.linalg.inv(transforms[0])@transforms[2]
            assert (v4.transform(moving, base_to_back)^v4.union([white, relief])).volume() < 1e-5

    return {'preview_only': True, 'angle_deg': ANGLE,
            'backrest_core_mm': BACK_T, 'relief_mm': .8, 'blue_core_mm': SHELF_T,
            'blue_slot_for_backrest_mm': BACK_T+GAP,
            'white_slot_for_base_mm': SHELF_T+GAP,
            'square_edge_contacts_z_mm': contact_minima,
            'side_insertion_positions_checked': 42,
            'phone_thicknesses_checked_mm': phone_gaps,
            'plug_insertions_checked': 4*29,
            'cable_window_mm': [18, 20], 'front_bar_mm': 10,
            'blue_base_length_mm': L,
            'usable_backrest_mm': H-CROSSING-SHELF_T,
            'crossing_back_local_mm': CROSSING,
            'full_project_generated': False, 'slicing_performed': False,
            'compatibility': 'Both pieces are revised; not compatible with old 6 mm backrest set'}


def font(size, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+name, size)


def draw_section(draw, section, origin, scale, colour):
    def pt(p): return (origin[0]+p[0]*scale, origin[1]-p[1]*scale)
    for group in section_groups(section):
        draw.polygon([pt(p) for p in group[0]], fill=colour)
        for hole in group[1:]:
            draw.polygon([pt(p) for p in hole], fill='white')


def side_panel(out, assembled):
    draw = ImageDraw.Draw(out)
    x0, y0, x1, y1 = 960, 190, 1840, 740
    draw.rounded_rectangle((x0, y0, x1, y1), radius=20, fill='white', outline='#d7dee5', width=2)
    draw.text((990, 210), 'Os dois apoios chegam à mesa', font=font(27, True), fill=BLUE)
    draw.text((990, 254), 'Arestas sem o bisel grande · vista lateral', font=font(22), fill='#354552')
    scale, origin = 1.85, (1040, 685)
    for solid, colour in zip(assembled, [WHITE, BLUE, BLUE]):
        section = v4.mesh_of(solid).section(plane_origin=(20, 0, 0), plane_normal=(1, 0, 0))
        if section:
            for path in section.discrete:
                pts = [(origin[0]+y*scale, origin[1]-z*scale) for x, y, z in path]
                draw.polygon(pts, fill=colour, outline='#354552')
    draw.line((1000, 686, 1795, 686), fill='#73818d', width=3)
    for y in (0, B/S):
        x = origin[0]+y*scale
        draw.ellipse((x-9, 677, x+9, 695), outline='#d39b00', width=4)
    draw.text((1380, 355), 'Placa: 7 mm + relevo', font=font(23), fill=BLUE)
    draw.text((1380, 405), 'Base azul: 6 mm', font=font(23), fill=BLUE)
    draw.text((1380, 455), 'Inclinação mantida: 70°', font=font(23), fill=BLUE)
    draw.text((1380, 505), 'Contacto pela aresta', font=font(23), fill='#a87900')
    draw.text((1380, 550), 'Sem corte inferior inclinado', font=font(21), fill='#354552')


def print_panel(out, solids):
    draw = ImageDraw.Draw(out)
    draw.rounded_rectangle((960, 775, 1840, 1410), radius=20, fill='white', outline='#d7dee5', width=2)
    draw.text((990, 795), 'Impressão deitada', font=font(28, True), fill=BLUE)
    draw.text((990, 840), 'Verso plano em contacto com o prato', font=font(23), fill='#354552')
    # A real underside view of the proposed blue piece: full flat back edge.
    picture = v4.render_meshes([(solids[2], BLUE)], (540, 400),
                                direction=(.45, -.8, -.6), margin=38)
    out.paste(picture, (1000, 885))
    draw.text((1500, 955), 'Bisel grande', font=font(22), fill='#354552')
    draw.text((1500, 990), 'removido', font=font(22), fill='#354552')
    draw.text((1000, 1305), 'Ranhura azul: 7,30 mm para placa de 7,00 mm', font=font(23), fill=BLUE)
    draw.text((1000, 1350), 'Janela 18 × 20 mm e travessa frontal mantidas', font=font(22), fill='#354552')


def main():
    back, shelf, solids, assembled, transforms = geometry()
    stats = verify(solids, assembled, transforms)
    out = Image.new('RGB', (1900, 1540), '#f4f6f8')
    draw = ImageDraw.Draw(out)
    draw.text((45, 25), 'Proposta V6 — placa de 7 mm e apoios pela aresta', font=font(41, True), fill=BLUE)
    draw.text((45, 91), 'Geometria proposta para imprimir as duas peças deitadas, sem o bisel que exigia suportes.',
              font=font(25), fill='#354552')
    out.paste(v4.render_meshes(list(zip(assembled, [WHITE, BLUE, BLUE])),
                               (900, 1090), margin=50), (10, 190))
    draw.text((55, 1315), 'Placa: 200 × 80 × 7 mm', font=font(27, True), fill=BLUE)
    draw.text((55, 1360), 'Base: 111 × 80 × 6 mm · folga total: 0,30 mm', font=font(24), fill='#354552')
    side_panel(out, assembled)
    print_panel(out, solids)
    draw.text((45, 1460), 'Apenas prévia: ambas as peças serão revistas. Fatiamento e ficheiros de impressão ficam para a etapa seguinte.',
              font=font(23), fill='#354552')
    path = ROOT/'designs'/f'{PREFIX}.png'
    out.save(path)
    # The report is useful locally but is not a production design definition.
    print(json.dumps(stats, indent=2))
    print(path)


if __name__ == '__main__':
    main()
