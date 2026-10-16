"""Build the approved V6: 7 mm white backrest with bevel, flat blue base.

The approved preview is the geometry source. Outputs are separate print STL,
a reference assembly, unequal-thickness fit samples and a Fusion definition.
"""
from pathlib import Path
import json

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw
import trimesh

from generate_joana_topper import save_mesh, section_groups
from preview_universo_stand_v6_white_bevel import (
    BACK_T, SHELF_T, GAP, H, W, B, L, ANGLE, A, CROSSING, WINDOW_Y, PAD_Y,
    geometry, verify, font,
)
import generate_universo_stand_v4 as v4


ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/UniversoSaberStandV6'
PREFIX = 'universo-saber-suporte-v6'
WHITE, BLUE = v4.WHITE, v4.BLUE
RELIEF = .8


def static_checks(solids, assembled, transforms):
    support = v4.union(assembled)
    contact_points = []
    for part in (assembled[0], assembled[2]):
        points = v4.vertices(part)
        contact_points.extend(points[np.abs(points[:, 2]) < 1e-5, :2].tolist())
    hull = cv2.convexHull(np.array(contact_points, np.float32)).reshape(-1, 2)
    stand_mesh = v4.mesh_of(support)
    stand_center = stand_mesh.center_mass
    cases = []
    for length, width, thick, grams in [(145, 65, 8, 180), (165, 80, 14, 250), (180, 90, 17, 320)]:
        phone = md.Manifold.cube((width, length, thick)).translate(
            (-width/2, CROSSING+SHELF_T, BACK_T+RELIEF+.1))
        placed = v4.transform(phone, transforms[0])
        assert (placed^support).volume() < 1e-5
        center = (transforms[0]@np.array([0, CROSSING+SHELF_T+length/2,
                                         BACK_T+RELIEF+.1+thick/2, 1]))[:3]
        for mass_factor in (.5, 1.0):
            stand_grams = support.volume()*.00124*mass_factor
            combined = (stand_center*stand_grams+center*grams)/(stand_grams+grams)
            margin = float(cv2.pointPolygonTest(hull, tuple(combined[:2]), True))
            assert margin > 15, (length, mass_factor, margin)
            cases.append({'phone_mm': [length, width, thick], 'phone_g': grams,
                          'stand_mass_factor': mass_factor, 'static_margin_mm': margin})

    # A large housing can also be threaded through the window before plugging
    # it in; this differs from the smaller envelope needed directly at a port.
    threading = md.Manifold.cube((16, 10, 14)).translate((-8, WINDOW_Y+5, -8))
    for dz in np.linspace(-8, 14, 23):
        assert (threading.translate((0, 0, float(dz)))^solids[2]).volume() < 1e-5
    crossbar = md.Manifold.cube((18, 10, SHELF_T)).translate((-9, WINDOW_Y+20, 0))
    assert (crossbar-solids[2]).volume() < 1e-5
    return {'static_load_cases': cases,
            'worst_static_margin_mm': min(c['static_margin_mm'] for c in cases),
            'foot_contact_polygon_xy': hull.tolist(),
            'threading_housing_mm': [16, 10, 14], 'threading_positions_checked': 23,
            'physical_fit_tested': False, 'physical_cable_fit_tested': False,
            'physical_strength_tested': False, 'structural_FEA_performed': False,
            'fusion_runtime_tested': False}


def fit_pair(gap):
    """The test reproduces both new material thicknesses and slot widths."""
    white = v4.rounded(-14, 0, 28, 24, 1.5)
    white -= v4.rect(-15, 9-gap/2, 15+gap/2, SHELF_T+gap)
    blue = v4.rounded(-14, 0, 28, 24, 1.5)
    blue -= v4.rect(-15, 9-gap/2, 15+gap/2, BACK_T+gap)
    return [white.extrude(BACK_T), blue.extrude(SHELF_T).translate((0, 32, 0))]


def illustrations(assembled):
    out = Image.new('RGB', (1650, 1150), '#f4f6f8')
    draw = ImageDraw.Draw(out)
    out.paste(v4.render_meshes(list(zip(assembled, [WHITE, BLUE, BLUE])), (960, 950)), (0, 125))
    draw.text((45, 25), 'Universo do Saber — V6 final', font=font(37, True), fill=BLUE)
    draw.text((45, 82), 'Placa branca 7 mm com bisel · Base azul 6 mm sem bisel inferior',
              font=font(24), fill='#354552')
    for y, label in [(245, 'Inclinação: 70°'),
                     (305, 'Placa: 200 × 80 × 7 mm'),
                     (365, 'Base: 111 × 80 × 6 mm'),
                     (425, 'Ranhura azul: 7,30 mm'),
                     (485, 'Ranhura branca: 6,30 mm'),
                     (545, 'Folga total: 0,30 mm'),
                     (605, 'Janela do cabo: 18 × 20 mm'),
                     (665, 'Travessa frontal: 10 × 6 mm'),
                     (765, 'Duas peças físicas / dois pratos'),
                     (825, 'Imprimir o conjunto V6 completo')]:
        draw.text((990, y), label, font=font(25), fill=BLUE)
    draw.text((45, 1093), 'Geometria real dos STL e do 3MF. As duas peças e os encaixes foram atualizados.',
              font=font(23), fill='#354552')
    out.save(ROOT/'designs'/f'{PREFIX}-CAD.png')

    side = Image.new('RGB', (1500, 1000), 'white')
    d = ImageDraw.Draw(side)
    d.text((45, 25), 'V6 — contacto com a mesa e montagem', font=font(34, True), fill=BLUE)
    scale, origin = 3.4, (180, 810)
    for solid, colour in zip(assembled, [WHITE, BLUE, BLUE]):
        cut = v4.mesh_of(solid).section(plane_origin=(20, 0, 0), plane_normal=(1, 0, 0))
        if cut:
            for path in cut.discrete:
                d.polygon([(origin[0]+y*scale, origin[1]-z*scale) for x, y, z in path],
                          fill=colour, outline='#354552')
    d.line((80, 811, 1420, 811), fill='#73818d', width=3)
    for y in (0, (B+BACK_T)/np.sin(A)):
        x = origin[0]+y*scale
        d.ellipse((x-10, 801, x+10, 821), outline='#d39b00', width=4)
    for y, label in [(245, 'Branca: bisel mantido'), (305, 'Azul: apoio pela aresta'),
                     (385, 'Os dois apoios ficam no mesmo plano'),
                     (445, f'Altura útil acima do apoio: {H-CROSSING-SHELF_T:.1f} mm'),
                     (505, 'Base azul com verso plano'),
                     (565, 'A ficha passa pela janela antes de ligar')]:
        d.text((730, y), label, font=font(25), fill=BLUE)
    d.text((45, 900), 'Branca 7 mm + relevo 0,8 mm · Azul 6 mm + batentes 4 mm · Montagem a 70°',
           font=font(24), fill='#354552')
    side.save(ROOT/'designs'/f'{PREFIX}-montagem.png')


def main():
    FOLDER.mkdir(exist_ok=True)
    back, shelf, solids, assembled, transforms = geometry()
    stats = verify(solids, assembled, transforms)
    stats.update(static_checks(solids, assembled, transforms))
    stats.update({'preview_only': False, 'full_project_generated': True,
                  'approved_preview': 'universo-saber-suporte-v6-proposta-bisel-branco.png',
                  'white_bevel_slope_to_print_bed_deg': ANGLE,
                  'print_orientation': 'Flat with decorations and phone stops facing upwards',
                  'cable_port_assumptions': 'Centered port; phone lies 0.9 mm ahead of white core',
                  'blue_phone_stop_start_mm': PAD_Y})
    names = ['costas-branco', 'relevos-azul', 'base-azul']
    for name, solid in zip(names, solids):
        mesh = save_mesh(solid, ROOT/'downloads'/f'{PREFIX}-{name}.stl')
        stats.setdefault('parts', []).append({'name': name, 'bbox_mm': mesh.extents.tolist(),
            'volume_mm3': solid.volume(), 'watertight': bool(mesh.is_watertight)})
    full_back = v4.union(solids[:2])
    # Keep the two physical pieces separate in the reference mesh. Boolean
    # union of transformed touching faces creates float32 slivers and is not
    # needed for a visual assembly file.
    back_mesh = save_mesh(full_back, ROOT/'downloads'/f'{PREFIX}-costas-completas.stl')
    back_mesh.apply_transform(transforms[0])
    blue_mesh = trimesh.load(ROOT/'downloads'/f'{PREFIX}-base-azul.stl', force='mesh')
    blue_mesh.apply_transform(transforms[2])
    reference = trimesh.util.concatenate([back_mesh, blue_mesh])
    assert reference.is_watertight and reference.is_winding_consistent
    reference.export(ROOT/'downloads'/f'{PREFIX}-montado-referencia-nao-imprimir.stl')
    samples = []
    for i, gap in enumerate((.2, .3, .4)):
        pair = fit_pair(gap)
        save_mesh(v4.union(pair), ROOT/'downloads'/f'{PREFIX}-amostra-encaixe-{round(gap*100):03d}.stl')
        samples.extend([p.translate((i*34, 0, 0)) for p in pair])
    save_mesh(v4.union(samples), ROOT/'downloads'/f'{PREFIX}-amostras-020-030-040.stl')

    pads = [v4.rounded(x-9, PAD_Y, 18, 6, 1.4) for x in (-26, 26)]
    definition = {'version': 6, 'units': 'mm', 'angle_deg': ANGLE,
        'gap_total_mm': GAP, 'backrest_length_mm': H, 'backrest_width_mm': W,
        'backrest_thickness_mm': BACK_T, 'shelf_thickness_mm': SHELF_T,
        'shelf_length_mm': L, 'shelf_rear_offset_mm': B, 'crossing_mm': CROSSING,
        'relief_height_mm': RELIEF, 'parts': [
            {'name': 'Placa branca 7 mm com bisel', 'color': WHITE, 'z': 0, 'height': BACK_T,
             'groups': section_groups(back),
             'bevel_triangle_yz': [[0, 0], [BACK_T/np.tan(A), 0], [0, BACK_T]],
             'assembly_transform': transforms[0].tolist()},
            {'name': 'Símbolo letras e livros azuis', 'color': BLUE, 'z': BACK_T, 'height': RELIEF,
             'groups': section_groups(v4.decoration()), 'assembly_transform': transforms[1].tolist()},
            {'name': 'Base azul sem bisel inferior', 'color': BLUE, 'z': 0, 'height': SHELF_T,
             'groups': section_groups(shelf),
             'additions': [{'name': f'Batente {i+1}', 'z': SHELF_T, 'height': 4,
                           'groups': section_groups(p)} for i, p in enumerate(pads)],
             'assembly_transform': transforms[2].tolist()}]}
    (FOLDER/'geometry.json').write_text(json.dumps(definition, ensure_ascii=False, separators=(',', ':'))+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats, indent=2)+'\n')
    illustrations(assembled)
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
