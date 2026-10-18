"""Package the proposed dimension image as a one-page client PDF.

This creates a presentation document; it does not generate printable geometry
or a 1:1 cutting template. Requires Pillow and reportlab.
"""
from pathlib import Path

from PIL import Image
from reportlab import rl_config
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'designs/kit-natal-pintar-v1-dimensoes.png'
TARGET = ROOT / 'downloads/kit-natal-pintar-v1-dimensoes.pdf'


def main():
    rl_config.useA85 = False
    with Image.open(SOURCE) as image:
        image.verify()
    with Image.open(SOURCE) as image:
        width_px, height_px = image.size

    page_width, page_height = landscape(A4)
    margin = 8 * mm
    scale = min((page_width - 2 * margin) / width_px,
                (page_height - 2 * margin) / height_px)
    width, height = width_px * scale, height_px * scale
    document = canvas.Canvas(str(TARGET), pagesize=(page_width, page_height))
    document.setTitle('Kit de Natal para pintar — proposta de dimensões V1')
    document.setAuthor('')
    document.setSubject('Uma paleta e seis enfeites; medidas propostas, vistas ilustrativas.')
    document.drawImage(str(SOURCE), (page_width - width) / 2,
                       (page_height - height) / 2, width, height)
    document.showPage()
    document.save()
    assert TARGET.read_bytes().startswith(b'%PDF-')
    print(f'PDF criado: {TARGET.name} ({TARGET.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
