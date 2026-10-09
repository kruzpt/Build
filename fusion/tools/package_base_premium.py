"""Create a dimensioned layout and ZIP for the standalone replacement base.

Run from any directory with Pillow installed. No Fusion required for packaging.
"""
import ast
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]


def main():
    folder = ROOT / 'fusion/EssencialBasePremium'
    script = folder / 'EssencialBasePremium.py'
    ast.parse(script.read_text())
    image = Image.new('RGB', (1200, 1100), 'white')
    draw = ImageDraw.Draw(image)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 22)
    title = ImageFont.truetype(font_path, 32)
    pink = (205, 79, 125)
    def text(x, y, message, large=False):
        draw.text((x, y), message, fill='#303038', font=title if large else font)
    text(60, 20, 'Clínica Essencial — Base Premium', True)
    text(60, 66, 'Esquema nominal em mm — encaixe da placa preservado')

    # Plan at 5.5 px/mm; top edge softening is omitted from this diagram.
    s, x, y = 5.5, 120, 140
    draw.rounded_rectangle((x, y, x+160*s, y+70*s), radius=12*s,
                           fill=pink, outline='#543b48', width=2)
    for xx, yy, w, h, colour in (
            (19.2, 31.75, 121.6, 6.5, '#ddd5d9'),
            (19.7, 32.25, 120.6, 5.5, 'white')):
        draw.rectangle((x+xx*s, y+yy*s, x+(xx+w)*s, y+(yy+h)*s),
                       fill=colour, outline='#543b48', width=2)
    draw.line((x+12*s, y+8*s, x+148*s, y+8*s), fill='#f9d5e2', width=2)
    text(120, 106, 'Vista superior — 160 × 70 mm; cantos R12')
    text(120, 540, 'Ranhura: 120,6 × 5,5 mm | entrada: 121,6 × 6,5 mm')
    text(120, 574, 'Frente: Y=0 (aresta superior desta vista)')

    # Centre section through X=80. Exact socket floor/entry and bevel positions.
    # The outer back-top R2 curve is sampled for the drawing only.
    import math
    profile = [(0,0), (70,0), (70,16)]
    profile += [(68+2*math.cos(t*math.pi/32),
                 16+2*math.sin(t*math.pi/32)) for t in range(1,17)]
    profile += [(38.25,18), (38.25,17), (37.75,17), (37.75,5.2),
                (32.25,5.2), (32.25,17), (31.75,17), (31.75,18),
                (8,18), (0,10)]
    s, x, bottom = 12, 120, 935
    pixels = [(x+yy*s, bottom-zz*s) for yy,zz in profile]
    draw.polygon(pixels, fill=pink)
    draw.line(pixels+[pixels[0]], fill='#543b48', width=2)
    text(120, 637, 'Corte lateral central — 70 × 18 mm')
    text(120, 675, 'Chanfro 8 × 8 mm a 45°; frente com 10 mm de altura')
    text(740, 756, 'Ranhura: 12,8 mm')
    text(740, 791, 'Entrada: 1 mm')
    text(740, 826, 'Fundo sólido: 5,2 mm')
    text(120, 954, 'Fundo plano na mesa; ranhura para cima. Escala 100%.')
    text(120, 993, 'Bordos superiores exteriores R2; placa continua vertical.')
    text(120, 1032, 'Imagem de disposição, não render do kernel Fusion.')
    preview = ROOT / 'designs/essencial-base-premium-medidas.png'
    image.save(preview)
    concept = ROOT / 'designs/essencial-base-chanfrada-conceito.png'
    files = {
        'EssencialBasePremium/EssencialBasePremium.py': script,
        'README.md': folder/'README.md',
        'essencial-base-premium-medidas.png': preview,
        'essencial-base-chanfrada-conceito.png': concept,
    }
    package = ROOT / 'downloads/essencial-base-premium.zip'
    with ZipFile(package, 'w', ZIP_DEFLATED) as archive:
        for name, path in files.items():
            archive.write(path, name)
    with ZipFile(package) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(files)
        for name, path in files.items():
            assert archive.read(name) == path.read_bytes(), name
    print('Packaged standalone base, instructions, dimensioned diagram and concept.')
    print('All four ZIP entries match their source files; script syntax valid.')


if __name__ == '__main__':
    main()
