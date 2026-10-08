"""Enlarge both QR fields to 64 mm, retaining the optimized V3 builder."""
import ast
import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]


def main():
    source=(ROOT/'fusion/EssencialV3Fast/EssencialV3Fast.py').read_text()
    replacements={
        'PANEL_WIDTH = 180.0':'PANEL_WIDTH = 200.0',
        'QR_SIZE = 52.0':'QR_SIZE = 64.0',
        'NFC_X = 121.0':'NFC_X = 133.0',
        'SPINE_RELIEF = 2.4':'SPINE_RELIEF = 2.4\nSPINE_X_OFFSET = 20.0',
        'x = 145.0 + 5.0 * math.sin':'x = SPINE_X_OFFSET + 145.0 + 5.0 * math.sin',
        "return [('Instagram', INSTAGRAM_ROWS, 86.0), ('Google', GOOGLE_ROWS, 21.0)]":
        "return [('Instagram', INSTAGRAM_ROWS, 81.0), ('Google', GOOGLE_ROWS, 4.0)]",
        "label('CLINICA',18,163,116,9)":"label('CLINICA',18,168,116,9)",
        "label('ESSENCIAL',18,145,116,11)":"label('ESSENCIAL',18,152,116,11)",
        "tail = process('Coccyx',145,22,1.0)":
        "tail = process('Coccyx',145+SPINE_X_OFFSET,22,1.0)",
        "sacrum = polygon(c,'Sacrum',[(141,43),(153,43),(157,38),\n"
        "            (157,33),(151,28),(150,22),(146,21),(141,29),(138,36)],":
        "sacrum = polygon(c,'Sacrum',[(x+SPINE_X_OFFSET,y) for x,y in\n"
        "            [(141,43),(153,43),(157,38),(157,33),(151,28),(150,22),\n"
        "             (146,21),(141,29),(138,36)]],",
    }
    for old,new in replacements.items():
        assert source.count(old)==1, 'Unexpected source: '+old
        source=source.replace(old,new)
    source=source.replace('V3 Fast','V4').replace('Clínica Essencial v3',
                                               'Clínica Essencial v4')
    source=source.replace("'Plate + logo + spine: one body. Base: one body.\\n'",
        "'Plate + logo + spine: one body. Base: one body.\\n'\n"
        "            'Plate: 200 x 220 mm; both QR fields: 64 x 64 mm.\\n'")
    ast.parse(source)
    folder=ROOT/'fusion/EssencialV4'
    folder.mkdir(exist_ok=True)
    (folder/'EssencialV4.py').write_text(source)
    nodes=ast.parse(source).body
    pure={'sample_path','logo_contours','sector_contour','row_layout',
          'qr_runs','vertebra_layout'}
    nodes=[n for n in nodes if isinstance(n,ast.Assign)
           or (isinstance(n,ast.FunctionDef) and n.name in pure)]
    v={'math':math}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'v4 geometry','exec'),v)

    scale=4
    image=Image.new('RGB',(1840,1240),'#ede9e5')
    draw=ImageDraw.Draw(image)
    pink='#CE5181'
    def xy(x,y):
        return (round(90+x*scale),round(1130-y*scale))
    def box(x0,y0,x1,y1):
        return (*xy(x0,y1),*xy(x1,y0))
    draw.rounded_rectangle(box(0,0,v['PANEL_WIDTH'],v['PANEL_HEIGHT']),
                           radius=24,fill='white')
    tx=(v['PANEL_WIDTH']-v['TONGUE_WIDTH'])/2
    draw.rounded_rectangle(box(tx,-12,tx+120,2),radius=4,fill='white')
    draw.ellipse(box(-10,182,66,258),fill=pink)
    for contour in v['logo_contours']():
        draw.polygon([xy(x,y) for x,y in contour],fill='white')
    ds=38/540
    dx,dy=28+(680-540)*ds,220+(540-327)*ds
    draw.ellipse(box(dx-18*ds,dy-18*ds,dx+18*ds,dy+18*ds),fill='white')
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',42)
    draw.text(xy(18,180),'CLÍNICA',font=title,fill=pink)
    draw.text(xy(18,166),'ESSENCIAL',font=title,fill=pink)
    for region,number,x,y,w,h in v['vertebra_layout']():
        draw.rounded_rectangle(box(x-w/2,y-h/2,x+w/2,y+h/2),
            radius=round(min(1.8,h*.27)*scale),fill=pink)
        factor=1 if region=='C' else (1.15 if region=='T' else 1.35)
        process=v['sample_path']([('M',0,1),('C',3,1,6,0,8,-1),
            ('C',9,-1,9,-3,8,-3),('C',4,-3,2,-1,0,-1)])
        draw.polygon([xy(x+w*.2+dx*factor,y+dy*factor) for dx,dy in process],fill=pink)
    draw.polygon([xy(x+v['SPINE_X_OFFSET'],y) for x,y in [(141,43),(153,43),
        (157,38),(157,33),(151,28),(150,22),(146,21),(141,29),(138,36)]],fill=pink)
    for name,rows,bottom in v['row_layout']():
        cy=bottom+v['QR_SIZE']/2
        cx=v['ICON_X']
        if name=='Instagram':
            draw.rounded_rectangle(box(cx-12,cy-12,cx+12,cy+12),radius=24,
                                   outline=pink,width=6)
            draw.ellipse(box(cx-7,cy-7,cx+7,cy+7),outline=pink,width=6)
            draw.ellipse(box(cx+5.25,cy+5.25,cx+8.15,cy+8.15),fill=pink)
        else:
            draw.polygon([xy(x,y) for x,y in v['sector_contour'](cx,cy,10.5,2.8,45,315)],fill=pink)
            draw.rectangle(box(cx+.4,cy-1.4,cx+11.8,cy+1.4),fill=pink)
            draw.rectangle(box(cx+9,cy-7.5,cx+11.8,cy),fill=pink)
        pitch=v['QR_SIZE']/len(rows)
        for row,start,end in v['qr_runs'](rows):
            draw.rectangle(box(v['QR_X']+start*pitch,
                bottom+(len(rows)-row-1)*pitch,v['QR_X']+end*pitch,
                bottom+(len(rows)-row)*pitch),fill='black')
        for radius in (3.7,7,10.3):
            draw.polygon([xy(x,y) for x,y in v['sector_contour'](
                v['NFC_X']-5,cy,radius,1.4,-55,55)],fill=pink)
    bx=v['PANEL_WIDTH']+30
    draw.rounded_rectangle(box(bx,0,bx+160,70),radius=28,fill=pink)
    draw.rectangle(box(bx+19.7,31.75,bx+140.3,38.25),fill='#442331')
    draw.rectangle(box(bx+20.2,32.25,bx+139.8,37.75),fill='#231118')
    for y,text in [(350,'V4 • QR de 64 × 64 mm'),
                   (405,'Placa: 200 × 220 mm'),
                   (460,'Base e encaixe preservados'),
                   (580,'Pausa NFC após Z = 3,8 mm'),
                   (630,'Esquema frontal, não render CAD.'),
                   (680,'Curvas da coluna simplificadas.')]:
        draw.text((1060,y),text,font=font,fill='#292929')
    preview=ROOT/'designs/essencial-v4-qr64-esquema.png'
    image.save(preview)
    expected={
        'Instagram':'https://www.instagram.com/clinicaessencial_setubal/',
        'Google':'https://share.google/2xgo7t8ZFrO7ukORw'}
    gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY)
    for name,rows,bottom in v['row_layout']():
        x0,y0=xy(v['QR_X'],bottom+v['QR_SIZE'])
        x1,y1=xy(v['QR_X']+v['QR_SIZE'],bottom)
        decoded,_,_=cv2.QRCodeDetector().detectAndDecode(gray[y0:y1,x0:x1])
        assert decoded==expected[name],name+' QR preview failed'
        print(name,'module pitch:',v['QR_SIZE']/len(rows),'mm; decoded URL OK.')
    with ZipFile(ROOT/'downloads/essencial-fusion-v4-qr64.zip','w',ZIP_DEFLATED) as z:
        z.write(folder/'EssencialV4.py','EssencialV4/EssencialV4.py')
        z.write(folder/'README.md','README.md')
        z.write(preview,'essencial-v4-qr64-esquema.png')
    print('V4 generated: 200 x 220 mm plate, 64 mm QR, unchanged base/socket/pause.')


if __name__=='__main__':
    main()
