"""Inspect the supplied pre-Boolean TOMAS/Gallardo project; no CAD output."""
import argparse
import hashlib
import json
from pathlib import Path

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import read_project

ROOT = Path(__file__).resolve().parents[2]


def solid(mesh):
    result = md.Manifold(md.Mesh64(np.asarray(mesh.vertices, dtype=np.float64),
                                   np.asarray(mesh.faces, dtype=np.uint64)))
    assert result.status() == md.Error.NoError
    return result


def mesh(result):
    data = result.to_mesh64()
    return trimesh.Trimesh(data.vert_properties[:, :3], data.tri_verts, process=True)


def main(source):
    _, config, plates = read_project(source)
    assert len(plates) == 1 and len(plates[0]['items']) == 2
    car, text = [item['mesh'] for item in plates[0]['items']]
    assert car.is_watertight and text.is_watertight
    glyphs = text.split()
    # Overlapping closed glyph shells need a true union before set intersection.
    united = md.Manifold.batch_boolean([solid(g) for g in glyphs], md.OpType.Add)
    result = solid(car) ^ united
    pieces = sorted(result.decompose(), key=lambda p: -p.volume())
    assert len(united.decompose()) == 1 and len(pieces) == 3
    assert pieces[0].volume() / result.volume() > .998
    parts = [mesh(p) for p in pieces]
    # text_info belongs to the second object.
    font_info = config.findall('object')[1].find('part/text_info')
    report = {
        'source_filename': source.name,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_is_before_boolean': True,
        'car_extents_xyz_mm': car.extents.tolist(),
        'text_extents_xyz_mm': text.extents.tolist(),
        'car_bounds_xyz_mm': car.bounds.tolist(),
        'text_bounds_xyz_mm': text.bounds.tolist(),
        'text_settings': dict(font_info.attrib),
        'source_car_connected_components': len(car.split()),
        'source_text_closed_glyph_shells': len(glyphs),
        'text_components_after_true_union': len(united.decompose()),
        'simulation': 'Manifold3D union of glyphs, then intersection with car; not native Bambu Boolean or a sliced print test.',
        'intersection_volume_mm3': result.volume(),
        'intersection_components': [
            {'volume_mm3': p.volume(), 'bounds_xyz_mm': list(p.bounding_box())}
            for p in pieces],
        'main_component_volume_fraction': pieces[0].volume() / result.volume(),
        'final_print_project_created': False,
    }
    folder = ROOT / 'fusion/GallardoTomasReview'
    folder.mkdir(exist_ok=True)
    (folder / 'analysis.json').write_text(json.dumps(report, indent=2) + '\n')

    scale = 2
    im = Image.new('RGB', (1440 * scale, 1130 * scale), '#f5f7fa')
    draw = ImageDraw.Draw(im)
    def font(n):
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n * scale)
    def label(x, y, text, n=21, color='#17344a'):
        draw.text((x * scale, y * scale), text, font=font(n), fill=color)
    label(35, 22, 'Gallardo + TOMAS — análise do ficheiro enviado', 30)
    label(35, 70, 'Projeções das malhas reais · mesma escala · simulação geométrica, sem alterar o projeto', 19)
    label(35, 117, 'ANTES DA INTERSEÇÃO', 23)
    label(745, 117, 'SIMULAÇÃO: UNIR LETRAS → INTERSEÇÃO', 22)
    xmin, xmax = min(car.bounds[0, 0], text.bounds[0, 0]), max(car.bounds[1, 0], text.bounds[1, 0])
    def project(m, left, top, axis, color):
        factor = 4.18
        low = car.bounds[0, axis] if axis == 2 else text.bounds[0, axis]
        high = car.bounds[1, axis] if axis == 2 else text.bounds[1, axis]
        # Rotate the overhead viewing direction 180 degrees so TOMAS is readable.
        def point(v):
            x = v[0] - xmin if axis == 2 else xmax - v[0]
            y = high - v[axis] if axis == 2 else v[axis] - low
            return ((left + x * factor) * scale, (top + y * factor) * scale)
        for tri in m.triangles:
            draw.polygon([point(v) for v in tri], fill=color)
        return point
    label(35, 166, 'Carro visto de lado')
    label(745, 166, 'Vista de lado: detalhes separados a vermelho')
    project(car, 40, 210, 2, '#264653')
    project(parts[0], 750, 210, 2, '#277f91')
    for i, p in enumerate(parts[1:], 1):
        fn = project(p, 750, 210, 2, '#cf4339')
        center = fn(p.centroid)
        radius = 12 * scale
        draw.ellipse((center[0] - radius, center[1] - radius,
                      center[0] + radius, center[1] + radius), outline='#cf4339', width=2 * scale)
        draw.text((center[0] + radius, center[1] - radius), str(i), font=font(18), fill='#b6352b')
    label(35, 425, 'Nome visto de cima — Courier New, sem negrito')
    label(745, 425, 'Vista de cima após o recorte pelo carro')
    project(mesh(united), 40, 475, 1, '#264653')
    project(parts[0], 750, 475, 1, '#277f91')
    for p in parts[1:]:
        project(p, 750, 475, 1, '#cf4339')
    label(35, 668, 'Dimensões atuais: carro 150 × 30 × 37,30 mm; nome 150,40 × 30 × 37,30 mm.', 21)
    label(35, 714, 'A orientação perpendicular e a profundidade já estão corretas neste ficheiro.', 22)
    label(35, 765, 'Resultado da simulação', 24)
    label(35, 810, f'1 corpo principal: {pieces[0].volume():.1f} mm³ ({100 * pieces[0].volume() / result.volume():.2f}% do volume)', 22)
    label(35, 849, f'2 fragmentos soltos: {pieces[1].volume():.2f} e {pieces[2].volume():.2f} mm³', 22, '#b6352b')
    label(35, 903, 'As letras sobrepõem-se: fundi-las primeiro evita usar cascas sobrepostas no Boolean.', 20)
    label(35, 944, 'Mesmo após essa união, o recorte do nome deixa dois detalhes do carro sem ligação.', 20)
    label(35, 1011, 'Próximo passo proposto: ajustar ligações/traço das letras e rever as duas zonas marcadas.', 20)
    label(35, 1054, 'Não é um STL/3MF final, nem uma validação de impressão ou do Boolean nativo do Bambu.', 18, '#526476')
    im.resize((1440, 1130), Image.Resampling.LANCZOS).save(ROOT / 'designs/gallardo-tomas-analise-intersecao.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    main(parser.parse_args().source)
