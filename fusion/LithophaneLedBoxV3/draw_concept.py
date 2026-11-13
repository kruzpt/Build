"""Review drawing only: accessible USB socket at rear-lid edge."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "designs/lithoavos-caixa-led-conceito-v3.svg"
W, H = 1800, 1160
NAVY = "#203642"
BLUE = "#337e9b"
RED = "#c33f48"
GOLD = "#d8aa50"
MUTED = "#536b74"
GREEN = "#218565"
PAPER = "#f8f7f3"
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']


def rect(x, y, w, h, fill="none", stroke="none", sw=0, rx=0):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def circle(x, y, r, fill="none", stroke="none", sw=0):
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, color=NAVY, sw=3, dash=""):
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{dashed}/>' )


def path(d, color=NAVY, sw=4, fill="none"):
    svg.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


def text(x, y, value, size=25, color=NAVY, weight="normal", anchor="start"):
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def card(x, y, w, h, title):
    rect(x, y, w, h, "white", "#c8d2d2", 3, 20)
    text(x+26, y+47, title, 29, NAVY, "bold")


rect(0, 0, W, H, PAPER)
text(56, 70, "CAIXA PARA LITOFANIA + LED", 49, NAVY, "bold")
text(58, 113, "Conceito V3 · placa fixa na tampa traseira · tomada USB-C exposta", 26, MUTED)

card(45, 155, 805, 610, "FRENTE · litofania horizontal")
# Front envelope stays symmetrical. The back-lid edge has a local USB notch.
x, y, s = 172, 273, 3
rect(x, y, 178*s, 142*s, NAVY, NAVY, 2, 15)
rect(x+9*s, y+9*s, 160*s, 124*s, "#e3d5b9", GOLD, 2, 4)
rect(x+11*s, y+11*s, 156*s, 120*s, "#f2e8d5")
text(x+89*s, y+68*s, "LITOFANIA", 37, "#746854", "bold", "middle")
text(x+89*s, y+81*s, "160 × 124 × 3 mm", 25, "#746854", anchor="middle")
line(x, y-26, x+178*s, y-26, RED, 3)
line(x, y-36, x, y-15, RED, 3)
line(x+178*s, y-36, x+178*s, y-15, RED, 3)
text(x+89*s, y-40, "≈ 178 mm exterior", 22, RED, "bold", "middle")
text(91, 734, "Tomada USB acessível pelo recorte traseiro.", 21, MUTED)

card(885, 155, 870, 610, "TAMPA TRASEIRA · vista pelo interior")
lx, ly, lw, lh = 1007, 271, 534, 426
rect(lx, ly, lw, lh, "#e8edf0", NAVY, 5, 12)
# Landscape board 156 x 120.1, port on midpoint of the right short edge.
bx, by, bw, bh = lx+33, ly+34, 468, 360
rect(bx, by, bw, bh, "#dae9ed", BLUE, 4, 4)
for xx in range(11):
    for yy in range(6):
        circle(bx+27+xx*41, by+35+yy*56, 4.5, "#ecc45e")
for hx in (bx+9, bx+bw-9):
    for hy in (by+8, by+bh-8):
        circle(hx, hy, 5.5, "white", BLUE, 2)
# The lid edge is notched back to the fixed female connector. The body gets
# matching rear-edge clearance, so the connector is reachable from outside.
rect(bx+bw, by+bh/2-30, 70, 60, "white")
line(bx+bw, by+bh/2-30, lx+lw, by+bh/2-30, RED, 3)
line(bx+bw, by+bh/2+30, lx+lw, by+bh/2+30, RED, 3)
rect(bx+bw-4, by+bh/2-12, 24, 24, "#22272a", RED, 2, 3)
rect(bx+bw+20, by+bh/2-16, 31, 32, "#475159", RED, 2, 5)
line(bx+bw+51, by+bh/2, lx+lw+79, by+bh/2, "#475159", 9)
text(1030, 255, "LED ≈ 156 × 120 mm", 22, BLUE, "bold")
text(1600, 411, "USB-C", 21, RED, "bold")
text(1600, 439, "fixa na placa", 19, RED)
text(1600, 467, "e acessível", 19, RED)
text(1186, 733, "Liga e desliga o cabo por fora.", 22, RED, "bold")

card(45, 800, 1015, 314, "CORTE · frente → costas")
rect(108, 888, 34, 164, NAVY)
rect(142, 900, 29, 140, "#e3d5b9", GOLD, 2)
rect(171, 900, 250, 140, "#fff2c9", GOLD, 2)
rect(421, 900, 16, 140, "#dae9ed", BLUE, 2)
rect(437, 888, 35, 164, "#e8edf0", NAVY, 2)
text(297, 961, "≈ 15 mm", 24, NAVY, "bold", "middle")
text(523, 909, "Litofania → ar → LED → tampa traseira", 22, NAVY, "bold")
text(523, 948, "LED preso na face interna da tampa.", 21, MUTED)
text(523, 986, "Recorte na tampa expõe a tomada da placa.", 21, RED)
text(523, 1024, "Cabo ligado e desligado pelo exterior.", 21, MUTED)
text(523, 1062, "Pequeno alívio no bordo traseiro do corpo.", 20, GREEN)

card(1090, 800, 665, 314, "MONTAGEM PROPOSTA")
text(1119, 887, "1  Corpo frontal com calha da litofania", 20, NAVY, "bold")
text(1119, 921, "2  Aro fino a segurar a litofania", 20, NAVY, "bold")
text(1119, 955, "3  LED alinhado na tampa traseira", 20, NAVY, "bold")
text(1119, 989, "4  Porta USB-C acessível no recorte", 20, NAVY, "bold")
line(1119, 1008, 1716, 1008, "#cad6d3", 2)
text(1119, 1041, "Furos da placa: dispensáveis.", 20, GREEN)
text(1119, 1075, "Medir tomada/ficha e espessura antes do CAD.", 19, RED)

svg.append("</svg>")
OUT.write_text("\n".join(svg), encoding="utf-8")
print(OUT)
