"""Render an engineering schematic from the A1 script's actual parameters."""
import ast
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def render_a1_preview(source, preview_path, google_url, google_caption):
    tree=ast.parse(source)
    pure={'sample_path','logo_contours','sector_contour','row_layout',
          'qr_runs','vertebra_layout'}
    nodes=[n for n in tree.body if isinstance(n,ast.Assign)
           or (isinstance(n,ast.FunctionDef) and n.name in pure)]
    v={'math':math}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'a1 geometry','exec'),v)
    # Include every protrusion in the bed-envelope calculation.
    minx=min(0,v['LOGO_X']-v['LOGO_RADIUS'])
    maxx=max(v['PANEL_WIDTH'],v['LOGO_X']+v['LOGO_RADIUS'])
    miny=-v['TONGUE_DEPTH']
    maxy=max(v['PANEL_HEIGHT'],v['LOGO_Y']+v['LOGO_RADIUS'])
    assert maxx-minx==208 and maxy-miny==242
    assert maxx-minx+2*5<=256 and maxy-miny+2*5<=256

    scale=4
    image=Image.new('RGB',(1840,1190),'#ede9e5')
    draw=ImageDraw.Draw(image)
    pink='#CE5181'
    def xy(x,y):
        return (round(90+x*scale),round(1080-y*scale))
    def box(x0,y0,x1,y1):
        return (*xy(x0,y1),*xy(x1,y0))
    draw.rounded_rectangle(box(0,0,v['PANEL_WIDTH'],v['PANEL_HEIGHT']),
                           radius=24,fill='white')
    tx=(v['PANEL_WIDTH']-v['TONGUE_WIDTH'])/2
    draw.rounded_rectangle(box(tx,-v['TONGUE_DEPTH'],tx+v['TONGUE_WIDTH'],2),
                           radius=4,fill='white')
    lx,ly,r=v['LOGO_X'],v['LOGO_Y'],v['LOGO_RADIUS']
    draw.ellipse(box(lx-r,ly-r,lx+r,ly+r),fill=pink)
    for contour in v['logo_contours']():
        draw.polygon([xy(x,y) for x,y in contour],fill='white')
    ds=r/540
    dx,dy=lx+(680-540)*ds,ly+(540-327)*ds
    draw.ellipse(box(dx-18*ds,dy-18*ds,dx+18*ds,dy+18*ds),fill='white')
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='label':
            text,x,y,width,height=[ast.literal_eval(a) for a in node.args]
            font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(height*scale))
            draw.text(xy(x,y+height+3),text,font=font,fill=pink)
    for region,number,x,y,w,h in v['vertebra_layout']():
        draw.rounded_rectangle(box(x-w/2,y-h/2,x+w/2,y+h/2),
            radius=round(min(1.8,h*.27)*scale),fill=pink)
        factor=1 if region=='C' else (1.15 if region=='T' else 1.35)
        process=v['sample_path']([('M',0,1),('C',3,1,6,0,8,-1),
            ('C',9,-1,9,-3,8,-3),('C',4,-3,2,-1,0,-1)])
        draw.polygon([xy(x+w*.2+dx*factor,y+dy*factor) for dx,dy in process],fill=pink)
    draw.polygon([xy(x+v['SPINE_X_OFFSET'],y+v['SPINE_Y_OFFSET']) for x,y in
        [(141,43),(153,43),(157,38),(157,33),(151,28),(150,22),(146,21),(141,29),(138,36)]],fill=pink)
    for name,rows,bottom in v['row_layout']():
        cy=bottom+v['QR_SIZE']/2
        cx=v['ICON_X']
        if name=='Instagram':
            draw.rounded_rectangle(box(cx-12,cy-12,cx+12,cy+12),radius=24,outline=pink,width=6)
            draw.ellipse(box(cx-7,cy-7,cx+7,cy+7),outline=pink,width=6)
            draw.ellipse(box(cx+5.25,cy+5.25,cx+8.15,cy+8.15),fill=pink)
        else:
            draw.polygon([xy(x,y) for x,y in v['sector_contour'](cx,cy,10.5,2.8,45,315)],fill=pink)
            draw.rectangle(box(cx+.4,cy-1.4,cx+11.8,cy+1.4),fill=pink)
            draw.rectangle(box(cx+9,cy-7.5,cx+11.8,cy),fill=pink)
        pitch=v['QR_SIZE']/len(rows)
        for row,start,end in v['qr_runs'](rows):
            draw.rectangle(box(v['QR_X']+start*pitch,bottom+(len(rows)-row-1)*pitch,
                v['QR_X']+end*pitch,bottom+(len(rows)-row)*pitch),fill='black')
        for radius in (3.7,7,10.3):
            draw.polygon([xy(x,y) for x,y in v['sector_contour'](v['NFC_X']-5,cy,radius,1.4,-55,55)],fill=pink)
    bx=v['PANEL_WIDTH']+30
    draw.rounded_rectangle(box(bx,0,bx+160,70),radius=28,fill=pink)
    draw.rectangle(box(bx+19.7,31.75,bx+140.3,38.25),fill='#442331')
    draw.rectangle(box(bx+20.2,32.25,bx+139.8,37.75),fill='#231118')
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
    for y,text in [(230,'Bambu A1 • peça total 208 × 242 mm'),
                   (285,'QR mantidos: 64 × 64 mm'),(340,'Brim de 5 mm: 218 × 252 mm'),
                   (450,google_caption),
                   (505,'Endereço confirmado no telemóvel'),
                   (610,'Pausa NFC após Z = 3,8 mm'),
                   (665,'Esquema frontal, não render CAD.')]:
        draw.text((990,y),text,font=font,fill='#292929')
    preview=Path(preview_path)
    image.save(preview)
    gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY)
    expected={'Instagram':'https://www.instagram.com/clinicaessencial_setubal/',
              'Google':google_url}
    for name,rows,bottom in v['row_layout']():
        x0,y0=xy(v['QR_X'],bottom+v['QR_SIZE'])
        x1,y1=xy(v['QR_X']+v['QR_SIZE'],bottom)
        decoded,_,_=cv2.QRCodeDetector().detectAndDecode(gray[y0:y1,x0:x1])
        assert decoded==expected[name]
    return v
