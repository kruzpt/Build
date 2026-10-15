"""Create review images for the proposed Universo do Saber V4 adjustments.

This script intentionally creates PNG previews only.  It does not export STL,
3MF or Fusion geometry, so the proposal can be approved before rebuilding the
complete stand.
"""
from pathlib import Path

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_joana_topper import section_groups
from generate_universo_stand_v3 import (
    BLUE,
    ROOT,
    _signed_area,
    logo_section,
    stroke_path,
)


PREFIX = "universo-saber-suporte-v4-proposta"
TEXT = "#303d49"
GREEN = "#20a36a"
PALE = "#f3f5f7"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def cubic_bezier(p0, p1, p2, p3, count=160):
    t = np.linspace(0, 1, count)[:, None]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def proposed_logo():
    """Replace only the lower-left U transition with one tangent Bezier."""
    current = logo_section()
    polygons = [np.asarray(p, float) for p in current.to_polygons()]
    main_index = max(range(len(polygons)),
                     key=lambda i: abs(_signed_area(polygons[i])))
    main = polygons[main_index]
    xmin, ymin = main.min(axis=0)

    # The existing curve is retained up to 6 mm above the baseline.  From
    # there a single cubic joins it to the exact vertical 18 mm above the
    # baseline.  Both handles follow their neighbouring tangents.
    lower_target = ymin + 6.0
    upper_target = ymin + 18.0
    outer = np.where(main[:, 0] < xmin + 8.0)[0]
    lower = int(outer[np.argmin(abs(main[outer, 1] - lower_target))])
    upper = int(outer[np.argmin(abs(main[outer, 1] - upper_target))])
    if upper >= lower:
        raise RuntimeError("Unexpected U contour ordering")

    p0 = main[lower].copy()
    tangent = main[lower - 1] - p0
    tangent /= np.linalg.norm(tangent)
    p1 = p0 + tangent * 4.0
    p3 = np.array((xmin, upper_target))
    p2 = p3 + np.array((0.0, -4.5))
    curve = cubic_bezier(p0, p1, p2, p3)

    # Polygon order runs from the vertical down towards the bowl here.
    revised = np.vstack((main[:upper], curve[::-1], main[lower + 1:]))
    polygons[main_index] = revised
    result = md.CrossSection(polygons, md.FillRule.EvenOdd)
    if result.area() <= 0:
        raise RuntimeError("Invalid proposed logo")
    return result


def proposed_books(cx=0):
    """Two simple closed books with a thick spine and white page block."""

    def rounded_box(x, y, width, height, radius):
        core = md.CrossSection.square((width - 2 * radius,
                                       height - 2 * radius))
        return core.translate((x + radius, y + radius)).offset(
            radius, circular_segments=24)

    def one_book(center_x, y, width):
        height = 4.7
        left = center_x - width / 2
        outer = rounded_box(left, y, width, height, 0.75)
        # A wider blue band on the left is the spine.  The thinner bands above,
        # below and on the right are the two covers around the white pages.
        pages = rounded_box(left + 2.7, y + 1.05,
                            width - 3.75, height - 2.1, 0.4)
        book = outer - pages
        page_detail = stroke_path([
            (center_x + 0.8, y + height / 2),
            (center_x + width / 2 - 1.55, y + height / 2),
        ], 0.8, False)
        book = md.CrossSection.batch_boolean([book, page_detail], md.OpType.Add)
        return book.transform(((1.0, 0.11, -0.11 * (y + height / 2)),
                               (0.0, 1.0, 0.0)))

    return md.CrossSection.batch_boolean([
        one_book(cx - 0.55, 1.0, 18.5),
        one_book(cx + 0.55, 6.4, 17.3),
    ], md.OpType.Add)


def draw_section(draw, section, origin, scale, fill=BLUE):
    groups = section_groups(section)

    def point(p):
        return (origin[0] + p[0] * scale, origin[1] - p[1] * scale)

    for group in groups:
        draw.polygon([point(p) for p in group[0]], fill=fill)
        for hole in group[1:]:
            draw.polygon([point(p) for p in hole], fill="white")


def draw_polyline(draw, points, origin, scale, fill, width):
    pts = [(origin[0] + p[0] * scale, origin[1] - p[1] * scale)
           for p in points]
    draw.line(pts, fill=fill, width=width, joint="curve")


def logo_preview():
    old = logo_section()
    new = proposed_logo()
    out = Image.new("RGB", (1500, 940), "white")
    draw = ImageDraw.Draw(out)
    draw.text((45, 28), "Proposta V4 — suavização local do U", font=font(38, True), fill=BLUE)
    draw.text((45, 82), "Só muda a transição marcada; alinhamento, tamanho e restantes formas ficam iguais.",
              font=font(24), fill=TEXT)

    # Full proposed logo.
    pts = np.vstack(new.to_polygons())
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    scale = 9.0
    origin = (100 - lo[0] * scale, 750 + lo[1] * scale)
    draw_section(draw, new, origin, scale)
    draw.text((80, 825), "CONTORNO PROPOSTO", font=font(24, True), fill=BLUE)

    # Enlarged old/new overlay of the edited path.
    old_main = np.asarray(max(old.to_polygons(), key=lambda p: abs(_signed_area(p))))
    new_main = np.asarray(max(new.to_polygons(), key=lambda p: abs(_signed_area(p))))
    xmin, ymin = old_main.min(axis=0)
    old_crop = old_main[(old_main[:, 0] < xmin + 9) &
                        (old_main[:, 1] < ymin + 25)]
    new_crop = new_main[(new_main[:, 0] < xmin + 9) &
                        (new_main[:, 1] < ymin + 25)]
    inset = (980, 800)
    inset_scale = 23
    draw.rounded_rectangle((900, 170, 1445, 835), radius=24,
                           fill=PALE, outline="#d4d9de", width=3)
    draw.text((940, 205), "DETALHE AMPLIADO", font=font(26, True), fill=BLUE)
    draw.text((940, 250), "V3 a cinzento", font=font(21), fill="#7f8993")
    draw.text((940, 283), "nova Bézier a azul", font=font(21), fill=BLUE)
    local_origin = (980 - xmin * inset_scale, 745 + ymin * inset_scale)
    draw_polyline(draw, old_crop, local_origin, inset_scale, "#a7adb3", 8)
    draw_polyline(draw, new_crop, local_origin, inset_scale, BLUE, 9)
    draw.ellipse((923, 440, 1400, 770), outline=GREEN, width=5)
    draw.text((915, 852), "Curva contínua e tangente",
              font=font(22), fill=GREEN)
    draw.text((915, 884), "entre a base e a vertical.",
              font=font(22), fill=GREEN)
    path = ROOT / "designs" / f"{PREFIX}-logo.png"
    out.save(path)
    return path


def books_preview():
    books = proposed_books()
    out = Image.new("RGB", (1200, 820), "white")
    draw = ImageDraw.Draw(out)
    draw.text((45, 28), "Proposta V4 — dois livros fechados", font=font(38, True), fill=BLUE)
    draw.text((45, 82), "Sem plano triangular: capas paralelas, lombada e páginas brancas.",
              font=font(24), fill=TEXT)
    pts = np.vstack(books.to_polygons())
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    scale = 35
    origin = (600 - (lo[0] + hi[0]) * scale / 2,
              610 + lo[1] * scale)
    draw_section(draw, books, origin, scale)
    draw.text((45, 690), "Traço mínimo: 0,9 mm · preparado para bico de 0,4 mm",
              font=font(23), fill=TEXT)
    draw.text((45, 735), "O branco da placa forma o bloco de páginas.",
              font=font(23), fill=TEXT)
    path = ROOT / "designs" / f"{PREFIX}-livros.png"
    out.save(path)
    return path


def main():
    logo = logo_preview()
    books = books_preview()
    print(logo)
    print(books)
    print("Preview only: no STL, 3MF or Fusion project generated.")


if __name__ == "__main__":
    main()
