"""Produce the review drawing for the lithophane light box. No print geometry."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'designs/lithoavos-caixa-led-conceito-v2.svg'
W, H = 1800, 1200
navy = '#19313b'
blue = '#287d98'
red = '#c13a45'
amber = '#e5b65a'
paper = '#faf8f3'
ink = '#26383f'
muted = '#587078'
green = '#197f62'
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']


def rect(x, y, w, h, fill='none', stroke='none', sw=0, rx=0):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, color=ink, sw=3, dash=''):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{dash_attr}/>')


def text(x, y, value, size=25, color=ink, weight='normal', anchor='start'):
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def card(x, y, w, h, title):
    rect(x, y, w, h, '#ffffff', '#c8d3d2', 3, 24)
    text(x+30, y+52, title, 31, navy, 'bold')


def arrow(x1, y1, x2, y2, color=red):
    line(x1, y1, x2, y2, color, 3)
    if x1 == x2:
        sign = 1 if y2 > y1 else -1
        line(x2, y2, x2-7, y2-sign*12, color, 3)
        line(x2, y2, x2+7, y2-sign*12, color, 3)
    else:
        sign = 1 if x2 > x1 else -1
        line(x2, y2, x2-sign*12, y2-7, color, 3)
        line(x2, y2, x2-sign*12, y2+7, color, 3)


rect(0, 0, W, H, paper)
text(55, 72, 'CAIXA PARA LITOFANIA + PLACA LED', 53, navy, 'bold')
text(58, 119, 'Conceito V2  ·  litofania medida no 3MF  ·  encaixes propostos para validar', 27, muted)

card(50, 160, 830, 620, 'FRENTE · IMAGEM NA HORIZONTAL')
# Outer 178 x 142, panel 160 x 124, aperture 156 x 120 (constant scale 3.35).
ox, oy, scale = 198, 284, 3.0
ow, oh = 178*scale, 142*scale
px, py = ox+9*scale, oy+9*scale
pw, ph = 160*scale, 124*scale
vx, vy = ox+11*scale, oy+11*scale
vw, vh = 156*scale, 120*scale
rect(ox, oy, ow, oh, navy, navy, 2, 16)
rect(px, py, pw, ph, '#e5d8bf', '#c68d31', 2, 2)
rect(vx, vy, vw, vh, '#f3e9d5', 'none', 0)
text(ox+ow/2, oy+oh/2-9, 'LITOFANIA', 42, '#75664e', 'bold', 'middle')
text(ox+ow/2, oy+oh/2+37, '160 × 124 × 3 mm', 29, '#75664e', 'normal', 'middle')
line(ox, oy-30, ox+ow, oy-30, red, 3)
line(ox, oy-41, ox, oy-19, red, 3)
line(ox+ow, oy-41, ox+ow, oy-19, red, 3)
text(ox+ow/2, oy-43, '178 mm exterior proposto', 22, red, 'bold', 'middle')
text(145, 758, 'Moldura cobre 2 mm da margem da litofania em cada lado.', 22, muted)

card(920, 160, 830, 620, 'COSTAS · PLACA REAL RODADA 90°')
bx, by, bw, bh = 1055, 285, 470, 380
rect(bx-24, by-24, bw+48, bh+48, '#e8edf0', navy, 6, 14)
rect(bx, by, bw, bh, '#f7f9f9', '#98a9b0', 2, 5)
# The LED board is 156 x 120 in landscape, centred inside the 160 x 124 window.
rx, ry, rw, rh = bx+7, by+9, 456, 362
rect(rx, ry, rw, rh, '#dce9ef', blue, 4, 3)
for hx in (rx+10, rx+rw-10):
    for hy in (ry+10, ry+rh-10):
        svg.append(f'<circle cx="{hx}" cy="{hy}" r="6" fill="white" stroke="{blue}" stroke-width="3"/>')
for x in range(12):
    for y in range(6):
        svg.append(f'<circle cx="{rx+31+x*36}" cy="{ry+35+y*56}" r="5" fill="#f2c95f"/>')
rect(bx+bw+22, by+bh/2-32, 34, 64, '#fff2ee', red, 3, 4)
arrow(bx+bw+40, by+bh/2, 1680, by+bh/2, red)
text(1608, by+bh/2-19, 'USB-C', 22, red, 'bold')
text(1025, 725, 'PCB ≈ 156 × 120,1 mm · comprimento por confirmar', 22, muted)
text(1025, 758, 'Furos: 150,24 × 114,73 mm entre centros', 21, red)

card(50, 810, 1040, 330, 'CORTE LATERAL · PROFUNDIDADE PROPOSTA')
# Diagram reads left (visible/front) to right (rear).
cy = 995
rect(120, 903, 44, 188, navy, navy, 1)
rect(164, 913, 34, 168, '#e5d8bf', '#c68d31', 2)
rect(198, 913, 300, 168, '#fff2cc', '#d9a73f', 2)
rect(498, 913, 19, 168, '#dce9ef', blue, 2)
rect(517, 903, 60, 188, '#e8edf0', navy, 2)
text(285, 960, '15 mm de luz', 25, navy, 'bold')
text(624, 943, 'Exterior: ≈ 27 mm', 25, navy, 'bold')
text(624, 983, 'Corpo com fundo + moldura removível', 22, ink)
text(624, 1018, 'Parede: ≈ 3 mm · folga litho: 0,4 mm', 22, ink)
text(624, 1053, 'Interior claro para espalhar a luz', 22, ink)
text(624, 1088, 'Posição do PCB depende da espessura real', 20, red)
text(624, 1119, 'Da frente: moldura · litho · ar · LED · fundo', 18, muted)

card(1120, 810, 630, 330, 'MONTAGEM E IMPRESSÃO')
text(1150, 895, '1  Corpo com fundo e apoios do LED', 21, navy, 'bold')
text(1150, 929, '2  LED preso por 4 grampos de borda', 21, navy, 'bold')
text(1150, 963, '3  Litofania colocada na calha frontal', 21, navy, 'bold')
text(1150, 997, '4  Moldura presa por 4 parafusos M3', 21, navy, 'bold')
line(1150, 1016, 1710, 1016, '#ced9d7', 2)
text(1150, 1050, '2 peças grandes + 4 grampos pequenos.', 20, green)
text(1150, 1082, 'Sem cola; LED acessível para manutenção.', 20, green)
text(1150, 1113, 'Confirmar espessura e abertura da USB-C.', 19, red)

svg.append('</svg>')
OUT.write_text('\n'.join(svg))
print(OUT)
