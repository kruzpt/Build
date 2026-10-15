"""Reinforced replacement base for the already printed Universo do Saber V4.

An integral front crossbar turns the open fork into a closed cable window.
No backrest, mating slot, foot plane, angle or phone stop is changed.
"""
from pathlib import Path
import hashlib
import json

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_joana_topper import section_groups, save_mesh
import generate_universo_stand_v4 as v4

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/UniversoSaberBaseV5'
PREFIX = 'universo-saber-base-v5-reforcada'
BLUE = v4.BLUE
WHITE = v4.WHITE
WINDOW_X = -9.0
WINDOW_Y = 80.0
WINDOW_WIDTH = 18.0
WINDOW_LENGTH = 20.0
WINDOW_RADIUS = 3.0
FRONT_BAR = v4.L - (WINDOW_Y + WINDOW_LENGTH)


def base():
    face = v4.rounded(-v4.W/2, 0, v4.W, v4.L, 3)
    face -= v4.rect(-v4.W/2-1, v4.B-v4.GAP/2,
                    v4.W/2+1+v4.GAP/2, v4.T+v4.GAP)
    hole = v4.rounded(WINDOW_X, WINDOW_Y, WINDOW_WIDTH,
                      WINDOW_LENGTH, WINDOW_RADIUS)
    face -= hole
    body = face.extrude(v4.T).trim_by_plane((0, v4.COS, v4.SIN),
                                           v4.T*v4.SIN)
    pads = [v4.rounded(x-9, v4.B+25, 18, 6, 1.4) for x in (-26, 26)]
    body = v4.union([body] + [p.extrude(4).translate((0, 0, v4.T))
                              for p in pads])
    return face, body, hole, pads


def plug_checks(body, white, relief):
    """Test plug insertion through the base for explicitly sized cases.

    The envelopes describe the *whole plastic housing*, not just the metal
    connector. They are examples, not a claim that every cable brand fits.
    """
    results = []
    shelf_back = v4.shelf_in_back()
    supported = v4.union([white, relief])
    cases = [(8.0, 10.0, 5.0), (10.0, 12.0, 6.0),
             (14.0, 12.0, 8.0), (17.0, 12.0, 8.0)]
    for phone_thickness, housing_width, housing_depth in cases:
        center_y = v4.B + v4.T + v4.RELIEF + 0.1 + phone_thickness/2
        housing = md.Manifold.cube((housing_width, housing_depth, 12)).translate(
            (-housing_width/2, center_y-housing_depth/2, -12))
        # Move the housing normally through the shelf until it meets the port
        # at z=6. None of this trajectory may intersect the base or backrest.
        for dz in np.linspace(-8, 6, 29):
            moving = housing.translate((0, 0, float(dz)))
            assert (moving ^ body).volume() < 1e-5, (phone_thickness, dz)
            in_back = v4.transform(moving, shelf_back)
            assert (in_back ^ supported).volume() < 1e-5, ('backrest', phone_thickness, dz)
        results.append({'phone_case_thickness_mm': phone_thickness,
                        'housing_width_mm': housing_width,
                        'housing_depth_mm': housing_depth,
                        'housing_length_mm': 12,
                        'port_center_from_backrest_centerline_mm': 0,
                        'insertion_positions_checked': 29,
                        'collision_volume_mm3': 0})
    # Verify that a 16 x 10 mm housing can be threaded through the central
    # region of the closed window, before connecting it to the phone.
    threading = md.Manifold.cube((16, 10, 14)).translate((-8, 85, -8))
    for dz in np.linspace(-8, 14, 23):
        assert (threading.translate((0, 0, float(dz))) ^ body).volume() < 1e-5
    return results


def validate(face, body, hole, white, relief):
    old_face, _, _, old_body, old_pads = v4.bodies()
    mating = md.Manifold.cube((100, 78.151, 25)).translate((-50, 0, -5))
    assert ((body-old_body) ^ mating).volume() < 1e-5
    assert ((old_body-body) ^ mating).volume() < 1e-5
    assert len(body.decompose()) == 1
    assert body.status() == md.Error.NoError
    # A substantial rectangular load path now connects both arms across the
    # front of the window. The old design has no material in this region.
    crossbar = md.Manifold.cube((18, FRONT_BAR, v4.T)).translate((-9, 100, 0))
    assert (crossbar-body).volume() < 1e-5
    assert (crossbar ^ old_body).volume() < 1e-5
    mats = [v4.back_transform(), v4.back_transform(),
            v4.back_transform() @ v4.shelf_in_back()]
    assembled = [v4.transform(s, m) for s, m in zip((white, relief, body), mats)]
    stats = v4.check_geometry((white, relief, body), assembled)
    stats.update({
        'revision': 'Replacement base V5 for V4 plate 1',
        'existing_plate_1_modified': False,
        'mating_zone_difference_mm3': 0,
        'new_front_crossbar_width_mm': FRONT_BAR,
        'new_front_crossbar_thickness_mm': v4.T,
        'crossbar_section_area_mm2': FRONT_BAR*v4.T,
        'previous_local_root_gap_mm': 80-(v4.B+v4.T+v4.GAP/2),
        'local_root_gap_retained_mm': 80-(v4.B+v4.T+v4.GAP/2),
        'reinforcement_method': 'Additional front load path, not a strength claim from infill alone',
        'window_maximum_width_mm': WINDOW_WIDTH,
        'window_maximum_length_mm': WINDOW_LENGTH,
        'window_corner_radius_mm': WINDOW_RADIUS,
        'cable_loading': 'Thread the small connector through the window before connecting the phone',
        'plug_housing_checks': plug_checks(body, white, relief),
        'threading_envelope_mm': [16, 10, 14],
        'threading_positions_checked': 23,
        'physical_cable_fit_tested': False,
        'physical_strength_tested': False,
    })
    return stats, assembled


def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def draw_face(draw, section, origin, scale, colour):
    def pt(p): return (origin[0]+p[0]*scale, origin[1]-p[1]*scale)
    for group in section_groups(section):
        draw.polygon([pt(p) for p in group[0]], fill=colour)
        for hole in group[1:]:
            draw.polygon([pt(p) for p in hole], fill='white')


def comparison(face, hole):
    old_face = v4.bodies()[2]
    out = Image.new('RGB', (1500, 1050), 'white')
    draw = ImageDraw.Draw(out)
    draw.text((45, 25), 'Base reforçada V5 — compatível com o prato 1 da V4',
              font=font(33), fill=BLUE)
    draw.text((45, 78), 'Uma travessa frontal liga os dois braços; a janela deixa passar a ficha e o cabo.',
              font=font(23), fill='#354552')
    scale = 6.2
    for face_section, label, origin in [
            (old_face, 'V4 — abertura em U', (375, 875)),
            (face, 'V5 — janela e travessa', (1125, 875))]:
        draw_face(draw, face_section, origin, scale, BLUE)
        draw.text((origin[0]-230, 135), label, font=font(26), fill=BLUE)
    origin = (1125, 875)
    # Highlight the added, fully solid front bridge in a diagram only.
    bar = v4.rect(-9, 100, 18, FRONT_BAR)
    draw_face(draw, bar, origin, scale, '#399b83')
    draw.text((810, 914), 'Verde: travessa de 10 × 6 mm', font=font(24), fill='#23785f')
    draw.text((45, 972), 'Ranhura 6,30 mm · placa 6,00 mm · base 110 × 80 mm · sem reimprimir as costas',
              font=font(25), fill='#354552')
    out.save(ROOT/'designs'/f'{PREFIX}-comparacao.png')


def assembled_preview(assembled):
    out = Image.new('RGB', (1200, 1090), '#f4f6f8')
    draw = ImageDraw.Draw(out)
    picture = v4.render_meshes(list(zip(assembled, [WHITE, BLUE, BLUE])), (900, 900))
    out.paste(picture, (150, 120))
    draw.text((45, 25), 'V4 com base reforçada V5', font=font(36), fill=BLUE)
    draw.text((45, 81), 'Mesmas costas impressas, mesmo encaixe e inclinação de 70°',
              font=font(24), fill='#354552')
    draw.text((45, 1030), 'A ficha passa pela janela antes de ligar o telemóvel.',
              font=font(25), fill='#354552')
    out.save(ROOT/'designs'/f'{PREFIX}-montagem.png')


def main():
    FOLDER.mkdir(exist_ok=True)
    face, body, hole, pads = base()
    _, white, _, _, _ = v4.bodies()
    relief = v4.decoration().extrude(v4.RELIEF).translate((0, 0, v4.T))
    stats, assembled = validate(face, body, hole, white, relief)
    mesh = save_mesh(body, ROOT/'downloads'/f'{PREFIX}.stl')
    stats['base'] = {'bbox_mm': mesh.extents.tolist(), 'volume_mm3': body.volume(),
                     'watertight': bool(mesh.is_watertight)}
    stats['unchanged_plate_1_stl_hashes'] = {
        n: hashlib.sha256((ROOT/'downloads'/n).read_bytes()).hexdigest()
        for n in ('universo-saber-suporte-v4-costas-branco.stl',
                  'universo-saber-suporte-v4-relevos-azul.stl')}
    definition = {'version': 5, 'units': 'mm', 'angle_deg': v4.ANGLE,
        'gap_total_mm': v4.GAP, 'parts': [{
            'name': 'Base V5 reforçada — compatível V4', 'color': BLUE,
            'z': 0, 'height': v4.T, 'groups': section_groups(face),
            'bevel_triangle_yz': [[0, 0], [v4.T*np.tan(v4.A), 0], [0, v4.T]],
            'additions': [{'name': f'Batente {i+1}', 'z': v4.T, 'height': 4,
                           'groups': section_groups(p)} for i, p in enumerate(pads)],
            'assembly_transform': (v4.back_transform() @ v4.shelf_in_back()).tolist(),
        }]}
    (FOLDER/'geometry.json').write_text(json.dumps(definition, ensure_ascii=False, separators=(',', ':'))+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats, indent=2)+'\n')
    comparison(face, hole)
    assembled_preview(assembled)
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
