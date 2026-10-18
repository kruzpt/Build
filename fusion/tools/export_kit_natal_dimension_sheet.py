"""Package dimension images as client PDFs: V1 one page, V2 kit and palette.

This creates a presentation document; it does not generate printable geometry
or a 1:1 cutting template. Requires Pillow and reportlab.
"""
import argparse
from pathlib import Path

from PIL import Image
from reportlab import rl_config
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'designs/kit-natal-pintar-v1-dimensoes.png'
TARGET = ROOT / 'downloads/kit-natal-pintar-v1-dimensoes.pdf'


def main(version='v1'):
    rl_config.useA85 = False
    sources = ([SOURCE] if version == 'v1' else [
        ROOT / 'designs/kit-natal-pintar-v2-dimensoes-cavidades.png',
        ROOT / 'designs/kit-natal-paleta-v2-CAD-dimensoes.png'])
    target = (TARGET if version == 'v1' else
              ROOT / 'downloads/kit-natal-pintar-v2-dimensoes-cavidades.pdf')
    page_width, page_height = landscape(A4)
    margin = 8 * mm
    document = canvas.Canvas(str(target), pagesize=(page_width, page_height))
    document.setTitle(f'Kit de Natal para pintar — proposta de dimensões {version.upper()}')
    document.setAuthor('')
    document.setSubject('Uma paleta e seis enfeites; medidas propostas, vistas ilustrativas.')
    for source in sources:
        with Image.open(source) as image:
            image.verify()
        with Image.open(source) as image:
            width_px, height_px = image.size
        scale = min((page_width - 2 * margin) / width_px,
                    (page_height - 2 * margin) / height_px)
        width, height = width_px * scale, height_px * scale
        document.drawImage(str(source), (page_width - width) / 2,
                           (page_height - height) / 2, width, height)
        document.showPage()
    document.save()
    assert target.read_bytes().startswith(b'%PDF-')
    print(f'PDF criado: {target.name} ({target.stat().st_size} bytes)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', choices=['v1', 'v2'], default='v1')
    args = parser.parse_args()
    main(args.version)
