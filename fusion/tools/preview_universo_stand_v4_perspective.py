"""Second V4 review: perspective books and a legible U comparison.

Only saves previews. No production STL, Fusion or Bambu project is generated.
"""
import json

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw

from generate_universo_stand_v3 import BLUE, ROOT, _signed_area, logo_section, stroke_path
from preview_universo_stand_v4_adjustments import cubic_bezier, draw_section, font, proposed_logo


PREFIX = 'universo-saber-suporte-v4-proposta2'
TEXT = '#354552'


def book(cx, cy):
    """Orthographic projection of a book with three visible rectangular faces.

    The cover is a genuine parallelogram: opposite edges have equal vectors.
    Page thickness is projected vertically and the spine is smoothly rounded.
    """
    a = np.array((-9.0 + cx, 5.0 + cy))
    along = np.array((12.2, 0.5))
    depth = np.array((4.2, 2.4))
    down = np.array((0.0, -3.3))
    b, d = a + along, a + depth
    c = b + depth
    aa, bb, cc = a + down, b + down, c + down
    spine = cubic_bezier(aa, aa + (-0.9, 0.45), a + (-0.9, -0.45), a, 45)
    outer = np.vstack(([a, d, c, cc, bb, aa], spine[1:-1]))
    silhouette = md.CrossSection([outer], md.FillRule.EvenOdd)
    strokes = md.CrossSection.batch_boolean([
        stroke_path(outer, 0.9, True),
        stroke_path([a, b, c], 0.9),
        stroke_path([b, bb], 0.9),
    ], md.OpType.Add)
    # Full opacity when compositing prevents lower book cover edges showing
    # through the white pages of the book stacked above it.
    return strokes, silhouette.offset(0.45, circular_segments=24)


def perspective_books():
    bottom, _ = book(-0.45, 0.0)
    upper, opaque = book(0.45, 4.0)
    return md.CrossSection.batch_boolean([bottom - opaque, upper], md.OpType.Add)


def draw_fitted(draw, section, bounds, fill=BLUE):
    points = np.vstack(section.to_polygons())
    lo, hi = points.min(axis=0), points.max(axis=0)
    x0, y0, x1, y1 = bounds
    scale = min((x1 - x0)/(hi[0]-lo[0]), (y1-y0)/(hi[1]-lo[1]))
    origin = ((x0+x1)/2-(lo[0]+hi[0])*scale/2,
              (y0+y1)/2+(lo[1]+hi[1])*scale/2)
    draw_section(draw, section, origin, scale, fill)


def books_image():
    icon = perspective_books()
    out = Image.new('RGB', (1120, 880), 'white')
    draw = ImageDraw.Draw(out)
    draw.text((45, 30), 'Dois livros em perspetiva', font=font(37, True), fill=BLUE)
    draw.text((45, 88), 'Nova proposta — capas retangulares e lombadas arredondadas',
              font=font(23), fill=TEXT)
    draw_fitted(draw, icon, (200, 180, 920, 700))
    draw.text((45, 765), 'Azul sobre branco · contornos de 0,9 mm · bico de 0,4 mm',
              font=font(23), fill=TEXT)
    draw.text((45, 810), 'Prévia do contorno proposto para o relevo.', font=font(23), fill=TEXT)
    out.save(ROOT/'designs'/f'{PREFIX}-livros.png')
    return icon, out


def transition(section):
    return section ^ md.CrossSection.square((11.0, 22.0)).translate((-32.0, 122.0))


def logo_image():
    old, new = logo_section(), proposed_logo()
    out = Image.new('RGB', (1500, 920), 'white')
    draw = ImageDraw.Draw(out)
    draw.text((45, 25), 'U — detalhe antes e depois', font=font(37, True), fill=BLUE)
    draw.text((45, 84), 'Correção apenas na passagem da lateral vertical para a curva inferior.',
              font=font(24), fill=TEXT)
    draw_fitted(draw, new, (55, 185, 650, 770))
    draw.text((95, 820), 'Símbolo completo com a curva proposta', font=font(22), fill=TEXT)

    # Draw the same geometric window at the same scale in two independent
    # panels. Labels never overlap the geometry, unlike the previous preview.
    for index, (section, label) in enumerate(((old, 'ANTES'), (new, 'PROPOSTA'))):
        left = 740 + index*365
        draw.rounded_rectangle((left, 190, left+320, 770), radius=18,
                               outline='#d6dce2', width=2, fill='white')
        draw.text((left+38, 218), label, font=font(26, True), fill=BLUE)
        cropped = transition(section)
        # Fixed coordinates ensure an honest before/after comparison.
        draw_section(draw, cropped, (left+50+31*20, 697+122*20), 20)
        draw.ellipse((left+39, 350, left+289, 610), outline='#e7b928', width=4)
    draw.text((747, 823), 'Mesmo tamanho e alinhamento; transição tangente.', font=font(22), fill=TEXT)
    out.save(ROOT/'designs'/f'{PREFIX}-U.png')
    return out


def main():
    icon, books = books_image()
    logo = logo_image()
    # This combined image is convenient to display or download in the chat.
    out = Image.new('RGB', (1500, 1799), 'white')
    resized = books.resize((1120, 880), Image.Resampling.LANCZOS)
    out.paste(resized, (190, 0))
    out.paste(logo, (0, 879))
    out.save(ROOT/'designs'/f'{PREFIX}-comparacao.jpg', quality=95, subsampling=0)
    points = np.vstack(icon.to_polygons())
    print(json.dumps({'preview_only': True, 'icon_bounds_mm': [points.min(0).tolist(), points.max(0).tolist()],
        'line_width_mm': 0.9, 'outputs': [f'{PREFIX}-livros.png', f'{PREFIX}-U.png', f'{PREFIX}-comparacao.jpg']}, indent=2))


if __name__ == '__main__':
    main()
