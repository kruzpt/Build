from PIL import Image, ImageDraw, ImageFont

W, H = 1800, 1200
im = Image.new("RGB", (W, H), "#f6f2eb")
d = ImageDraw.Draw(im)

def font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)

navy = "#18242b"
red = "#b4212c"
gold = "#d69b2d"
grey = "#59666c"
light = "#fffdf8"
green = "#148660"

d.text((65, 45), "CAIXA PARA LITOFANIA + PLACA LED", font=font(58, True), fill=navy)
d.text((68, 112), "Draft V1 · medidas reais do 3MF e da placa anunciada", font=font(29), fill=grey)

# Front view
d.rounded_rectangle((55, 185, 870, 810), radius=28, fill=light, outline="#9da5a7", width=4)
d.text((90, 215), "VISTA FRONTAL", font=font(34, True), fill=navy)
x0, y0 = 175, 315
fw, fh = 640, 496  # 4 px/mm, 160 x 124
d.rounded_rectangle((x0-18, y0-18, x0+fw+18, y0+fh+18), radius=16, fill=navy)
d.rectangle((x0, y0, x0+fw, y0+fh), fill="#e6d8bc", outline=gold, width=5)
d.text((x0+130, y0+205), "LITOFANIA", font=font(48, True), fill="#6e6253")
d.text((x0+155, y0+265), "160 × 124 × 3 mm", font=font(31), fill="#6e6253")
d.line((x0, y0-42, x0+fw, y0-42), fill=red, width=4)
d.line((x0, y0-53, x0, y0-31), fill=red, width=4)
d.line((x0+fw, y0-53, x0+fw, y0-31), fill=red, width=4)
d.text((x0+225, y0-84), "160 mm", font=font(27, True), fill=red)

# Exploded view
d.rounded_rectangle((920, 185, 1745, 810), radius=28, fill=light, outline="#9da5a7", width=4)
d.text((955, 215), "VISTA EXPLODIDA", font=font(34, True), fill=navy)
# layers
layers = [
    (1000, 325, 530, 420, "1  Moldura frontal", navy),
    (1040, 365, 500, 390, "2  Litofania 160 × 124", "#d8c8aa"),
    (1080, 405, 468, 360, "3  Câmara de luz: 15 mm", "#fff1b5"),
    (1120, 445, 456, 330, "4  LED rodado: 156 × 120", "#e9edf0"),
    (1160, 485, 440, 300, "5  Tampa removível", "#3f4a50"),
]
for x,y,w,h,label,color in layers:
    d.rounded_rectangle((x,y,x+w,y+h), radius=12, fill=color, outline=navy, width=3)
    d.text((x+18,y+14), label, font=font(24, True), fill=("white" if color in (navy,"#3f4a50") else navy))
d.text((1375, 742), "USB-C → saída lateral", font=font(27, True), fill=red)
d.line((1540, 730, 1648, 654), fill=red, width=4)

# Side section
d.rounded_rectangle((55, 845, 1085, 1145), radius=28, fill=light, outline="#9da5a7", width=4)
d.text((90, 875), "CORTE LATERAL PROPOSTO", font=font(32, True), fill=navy)
sx, sy = 130, 995
d.rectangle((sx, sy-82, sx+20, sy+82), fill=navy)
d.text((92, 1085), "moldura", font=font(18), fill=grey)
d.rectangle((sx+24, sy-75, sx+34, sy+75), fill="#d8c8aa")
d.text((160, 1085), "litho", font=font(18), fill=grey)
d.rectangle((sx+34, sy-75, sx+205, sy+75), fill="#fff1b5", outline=gold, width=2)
d.text((208, 974), "15 mm", font=font(26, True), fill=navy)
d.text((185, 1010), "difusão da luz", font=font(21), fill=grey)
d.rectangle((sx+205, sy-75, sx+217, sy+75), fill="#dfe5e7", outline=navy, width=2)
d.text((335, 1085), "LED", font=font(18), fill=grey)
d.rectangle((sx+217, sy-82, sx+300, sy+82), fill="#3f4a50")
d.text((444, 1085), "tampa", font=font(18), fill=grey)
d.text((555, 945), "Profundidade exterior", font=font(22, True), fill=navy)
d.text((555, 976), "estimada: 24–27 mm", font=font(22, True), fill=navy)
d.text((555, 1017), "Parede: 2,4 mm", font=font(20), fill=grey)
d.text((555, 1047), "Folga: 0,3–0,4 mm", font=font(20), fill=grey)
d.text((555, 1077), "Interior claro/refletor", font=font(20), fill=grey)

# Print recommendation
d.rounded_rectangle((1120, 845, 1745, 1145), radius=28, fill="#edf7f2", outline=green, width=4)
d.text((1155, 875), "IMPRESSÃO DA LITOFANIA", font=font(31, True), fill=green)
d.text((1155, 930), "✓ Brim 8–10 mm", font=font(27, True), fill=navy)
d.text((1155, 970), "✓ 2 estabilizadores traseiros destacáveis", font=font(25), fill=navy)
d.text((1155, 1008), "✓ contacto mínimo: tabs de 0,25–0,30 mm", font=font(25), fill=navy)
d.text((1155, 1046), "✕ raft não é necessário", font=font(27, True), fill=red)
d.text((1155, 1090), "A peça tem 124 mm de altura e só 3 mm de base.", font=font(22), fill=grey)

im.save("designs/lithoavos-caixa-led-draft-v1.png", quality=95)
