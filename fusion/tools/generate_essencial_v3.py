"""Generate V3 Fusion script, preview and package. Run with QR tool venv."""
import ast
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LINKS = {
    'Instagram': 'https://www.instagram.com/clinicaessencial_setubal/',
    'Google': 'https://share.google/2xgo7t8ZFrO7ukORw',
}

# Raster reference manually redrawn as cubic curves in its original coordinates.
# Not the original vector artwork. No middle bar; two curved stars and a dot.
GEOMETRY = '''
def sample_path(commands, steps=12):
    vertices = []
    for command in commands:
        if command[0] in ('M', 'L'):
            vertices.append((command[1], command[2]))
        elif command[0] == 'C':
            x0, y0 = vertices[-1]
            x1, y1, x2, y2, x3, y3 = command[1:]
            for i in range(1, steps+1):
                t = i/steps
                u = 1-t
                vertices.append((u**3*x0+3*u*u*t*x1+3*u*t*t*x2+t**3*x3,
                                 u**3*y0+3*u*u*t*y1+3*u*t*t*y2+t**3*y3))
    if vertices[-1] == vertices[0]:
        vertices.pop()
    return vertices


def logo_contours():
    e = sample_path([
        ('M',263,200), ('L',804,200), ('L',804,333),
        ('C',792,266,761,223,689,223), ('L',411,223), ('L',411,875),
        ('L',690,875), ('C',766,875,805,841,818,773),
        ('L',818,895), ('L',263,895),
        ('C',302,881,321,853,321,808), ('L',321,648),
        ('C',321,604,343,579,380,569),
        ('C',342,562,321,540,321,502), ('L',321,295),
        ('C',321,252,301,218,263,200)])
    small = sample_path([
        ('M',488,322), ('C',487,355,470,381,435,387),
        ('C',468,391,482,417,486,452),
        ('C',491,416,504,395,537,387),
        ('C',505,382,490,358,488,322)])
    large = sample_path([
        ('M',594,441), ('C',590,511,553,558,487,570),
        ('C',552,582,585,629,594,700),
        ('C',604,632,642,581,707,570),
        ('C',638,557,602,510,594,441)])
    scale = LOGO_RADIUS/540
    return [[(LOGO_X+(x-540)*scale, LOGO_Y+(540-y)*scale)
             for x,y in contour] for contour in (e,small,large)]


def qr_runs(rows):
    for row, values in enumerate(rows):
        start = None
        for col,value in enumerate(values+'0'):
            if value == '1' and start is None:
                start = col
            elif value == '0' and start is not None:
                yield row,start,col
                start = None


def sector_contour(cx,cy,radius,stroke,start,end,segments=32):
    angles = [math.radians(start+(end-start)*i/segments)
              for i in range(segments+1)]
    outer = [(cx+(radius+stroke/2)*math.cos(a),
              cy+(radius+stroke/2)*math.sin(a)) for a in angles]
    inner = [(cx+(radius-stroke/2)*math.cos(a),
              cy+(radius-stroke/2)*math.sin(a)) for a in reversed(angles)]
    return outer+inner


def row_layout():
    return [('Instagram', INSTAGRAM_ROWS, 86.0), ('Google', GOOGLE_ROWS, 21.0)]
'''

LOGO_BLOCK = '''        # Engraved custom serif E, two curved stars and dot.
        # No horizontal middle bar; all contours follow the supplied reference.
        for name, contour in zip(('Serif E', 'Small star', 'Large star'),
                                 logo_contours()):
            tool = polygon(c, name+' engraving', contour,
                           PANEL_THICKNESS-0.6, 0.8)
            combine(c, plate, tool, ops.CutFeatureOperation)
        dot_scale = LOGO_RADIUS/540
        dot = disk(c, 'Logo dot', LOGO_X+(680-540)*dot_scale,
                   LOGO_Y+(540-327)*dot_scale, 18*dot_scale,
                   PANEL_THICKNESS-0.6, 0.8)
        combine(c, plate, dot, ops.CutFeatureOperation)
'''

ROW_BLOCK = '''        # Each row: social symbol -> functional QR -> contactless symbol.
        # Icons and QR share the plate body. Exactly two internal tag cavities.
        def relief_polygon(name, contour):
            body = polygon(c, name, contour, PANEL_THICKNESS-0.02, 0.62)
            combine(c, plate, body, ops.JoinFeatureOperation)

        for platform, rows, bottom in row_layout():
            center_y = bottom+QR_SIZE/2
            cx = ICON_X
            if platform == 'Instagram':
                outline = rounded_rectangle(c,'Instagram outline',cx-12,
                    center_y-12,24,24,6,PANEL_THICKNESS-0.02,0.62)
                inner = rounded_rectangle(c,'Instagram outline hollow',cx-10.4,
                    center_y-10.4,20.8,20.8,4.4,PANEL_THICKNESS-0.1,0.8)
                combine(c,outline,inner,ops.CutFeatureOperation)
                combine(c,plate,outline,ops.JoinFeatureOperation)
                ring = disk(c,'Instagram lens',cx,center_y,7.0,
                            PANEL_THICKNESS-0.02,0.62)
                inner = disk(c,'Instagram lens hollow',cx,center_y,5.4,
                             PANEL_THICKNESS-0.1,0.8)
                combine(c,ring,inner,ops.CutFeatureOperation)
                combine(c,plate,ring,ops.JoinFeatureOperation)
                dot = disk(c,'Instagram camera dot',cx+6.7,center_y+6.7,1.45,
                           PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,dot,ops.JoinFeatureOperation)
            else:
                relief_polygon('Google G curved outline',
                    sector_contour(cx,center_y,10.5,2.8,45,315))
                bar = rectangle(c,'Google G horizontal stroke',cx+0.4,
                    center_y-1.4,11.4,2.8,PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,bar,ops.JoinFeatureOperation)
                bar = rectangle(c,'Google G right stroke',cx+9,
                    center_y-7.5,2.8,7.5,PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,bar,ops.JoinFeatureOperation)

            pitch = QR_SIZE/len(rows)
            for row,start,end in qr_runs(rows):
                sk = sketch(c,platform+' QR row %d run %d' % (row,start),
                            PANEL_THICKNESS-0.02)
                sk.sketchCurves.sketchLines.addTwoPointRectangle(
                    point(QR_X+start*pitch+0.01,
                          bottom+(len(rows)-row-1)*pitch+0.01),
                    point(QR_X+end*pitch-0.01,
                          bottom+(len(rows)-row)*pitch-0.01))
                c.features.extrudeFeatures.addSimple(sk.profiles.item(0),
                    adsk.core.ValueInput.createByReal(0.062),
                    ops.JoinFeatureOperation)
                sk.isVisible = False

            # Three contactless arcs, 1.4 mm strokes, over the concealed tag.
            for radius in (3.7,7.0,10.3):
                relief_polygon(platform+' contactless wave %.1f' % radius,
                    sector_contour(NFC_X-5,center_y,radius,1.4,-55,55))

            # A fully enclosed void. At the pause the upper wall isn't printed yet.
            pocket = disk(c,platform+' concealed NFC cavity',NFC_X,center_y,
                          NFC_CAVITY_DIAMETER/2,NFC_CAVITY_FLOOR_Z,
                          NFC_CAVITY_HEIGHT)
            combine(c,plate,pocket,ops.CutFeatureOperation)

'''


def main():
    matrices = {}
    for name, url in LINKS.items():
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                           box_size=24,border=4)
        qr.add_data(url)
        qr.make(fit=True)
        matrices[name] = [''.join('1' if cell else '0' for cell in row)
                          for row in qr.get_matrix()]
        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(
            np.array(qr.make_image().convert('L')))
        assert decoded == url

    source = (ROOT/'fusion/EssencialV2/EssencialV2.py').read_text()
    matrices_code = '\n'.join(name.upper()+'_ROWS = [\n'+
        ''.join('    '+repr(row)+',\n' for row in rows)+']\n'
        for name,rows in matrices.items())
    source = source.replace('import adsk.fusion\n',
        'import adsk.fusion\n\n'+matrices_code)
    source = source.replace('NFC_TAG_DIAMETER = 26.0\nNFC_FRONT_WALL = 1.2',
        '''NFC_TAG_DIAMETER = 25.0
NFC_CAVITY_DIAMETER = 25.8
NFC_CAVITY_FLOOR_Z = 3.0
NFC_CAVITY_HEIGHT = 0.8
NFC_PAUSE_Z = NFC_CAVITY_FLOOR_Z+NFC_CAVITY_HEIGHT
QR_SIZE = 52.0
QR_X = 49.0
ICON_X = 27.0
NFC_X = 121.0''')
    source = source.replace('def run(context):',GEOMETRY+'\n\ndef run(context):')
    source = source.replace('''        if not 0 < NFC_FRONT_WALL < PANEL_THICKNESS:
            raise ValueError('Invalid NFC front wall.')''',
        '''        if NFC_CAVITY_DIAMETER <= NFC_TAG_DIAMETER:
            raise ValueError('Tag cavity requires clearance.')
        if NFC_CAVITY_FLOOR_Z <= 0 or NFC_CAVITY_HEIGHT <= 0:
            raise ValueError('NFC cavity requires a solid floor and space.')
        if PANEL_THICKNESS-NFC_PAUSE_Z < 1.0:
            raise ValueError('Keep at least 1 mm of plastic above the tag.')''')
    start = source.index('        # Engraved approximate logo')
    end = source.index('        # Curved lateral processes',start)
    source = source[:start]+LOGO_BLOCK+'\n'+source[end:]
    start = source.index('        # Recess for a printed QR label')
    end = source.index('        def label(',start)
    source = source[:start]+ROW_BLOCK+source[end:]
    source = source.replace("        label('QR',36,17,30,5)\n",'')
    source = source.replace("        label('NFC',98,27,30,5)\n",'')
    source = source.replace('Clínica Essencial v2','Clínica Essencial v3')
    source = source.replace("ui.messageBox('V2 created: TWO parts", 
                            "ui.messageBox('V3 created: TWO parts")
    source = source.replace('NFC rear pocket may need bridging/support in the slicer.',
        'Two 25.8 mm concealed NFC pockets: pause AFTER z=3.8 mm, BEFORE roof.')
    source = source.replace('QR and exact logo artwork are still pending.',
        'Instagram + Google QR. Logo manually redrawn from image, not exact vector.')
    source = source.replace("ui.messageBox('V2 creation failed:",
                            "ui.messageBox('V3 creation failed:")
    ast.parse(source)
    folder = ROOT/'fusion/EssencialV3'
    folder.mkdir(exist_ok=True)
    (folder/'EssencialV3.py').write_text(source)

    # Get the same pure geometry used by Fusion for the schematic preview.
    tree = ast.parse(source)
    pure_names = {'sample_path','logo_contours','sector_contour','row_layout',
                  'vertebra_layout'}
    nodes = [node for node in tree.body if isinstance(node,ast.Assign)
             or (isinstance(node,ast.FunctionDef) and node.name in pure_names)]
    import math
    values = {'math':math}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'v3 geometry','exec'),values)
    scale = 4
    image = Image.new('RGB',(1720,1240),'#ede9e5')
    draw = ImageDraw.Draw(image)
    pink = '#CE5181'
    def xy(x,y):
        return (round(90+x*scale), round(1130-y*scale))
    def box(x0,y0,x1,y1):
        return (*xy(x0,y1),*xy(x1,y0))
    draw.rounded_rectangle(box(0,0,180,220),radius=24,fill='#ffffff')
    draw.rounded_rectangle(box(30,-12,150,2),radius=4,fill='#ffffff')
    draw.ellipse(box(-10,182,66,258),fill=pink)
    for contour in values['logo_contours']():
        draw.polygon([xy(x,y) for x,y in contour],fill='white')
    ds = 38/540
    dx,dy=28+(680-540)*ds,220+(540-327)*ds
    draw.ellipse(box(dx-18*ds,dy-18*ds,dx+18*ds,dy+18*ds),fill='white')
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
        title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',42)
    except OSError:
        font = ImageFont.load_default()
        title = font
    draw.text(xy(18,177),'CLÍNICA',font=title,fill=pink)
    draw.text(xy(18,159),'ESSENCIAL',font=title,fill=pink)
    # Rounded bodies in their actual positions; processes are schematic curves.
    for region,number,x,y,w,h in values['vertebra_layout']():
        draw.rounded_rectangle(box(x-w/2,y-h/2,x+w/2,y+h/2),
            radius=round(min(1.8,h*.27)*scale),fill=pink)
        factor=1 if region=='C' else (1.15 if region=='T' else 1.35)
        process=values['sample_path']([
            ('M',0,1),('C',3,1,6,0,8,-1),
            ('C',9,-1,9,-3,8,-3),('C',4,-3,2,-1,0,-1)])
        draw.polygon([xy(x+w*.2+dx*factor,y+dy*factor)
                      for dx,dy in process],fill=pink)
    draw.polygon([xy(x,y) for x,y in [(141,43),(153,43),(157,38),
        (157,33),(151,28),(150,22),(146,21),(141,29),(138,36)]],fill=pink)
    for platform,rows,bottom in values['row_layout']():
        cy=bottom+26
        if platform=='Instagram':
            draw.rounded_rectangle(box(15,cy-12,39,cy+12),radius=24,
                outline=pink,width=6)
            draw.ellipse(box(20,cy-7,34,cy+7),outline=pink,width=6)
            draw.ellipse(box(32.25,cy+5.25,35.15,cy+8.15),fill=pink)
        else:
            contour=values['sector_contour'](27,cy,10.5,2.8,45,315)
            draw.polygon([xy(x,y) for x,y in contour],fill=pink)
            draw.rectangle(box(27.4,cy-1.4,38.8,cy+1.4),fill=pink)
            draw.rectangle(box(36,cy-7.5,38.8,cy),fill=pink)
        for r,row in enumerate(rows):
            for col,on in enumerate(row):
                if on=='1':
                    p=52/len(rows)
                    draw.rectangle(box(49+col*p,bottom+(len(rows)-r-1)*p,
                        49+(col+1)*p,bottom+(len(rows)-r)*p),fill='black')
        for radius in (3.7,7,10.3):
            contour=values['sector_contour'](116,cy,radius,1.4,-55,55)
            draw.polygon([xy(x,y) for x,y in contour],fill=pink)
    draw.rounded_rectangle(box(213,0,373,70),radius=28,fill=pink)
    draw.rectangle(box(232.7,31.75,353.3,38.25),fill='#442331')
    draw.rectangle(box(233.2,32.25,352.8,37.75),fill='#231118')
    draw.text((970,350),'Base separada • encaixe 5,5 mm',font=font,fill='#292929')
    draw.text((970,405),'Etiquetas internas: Ø25 mm',font=font,fill='#292929')
    draw.text((970,460),'Pausa após Z = 3,8 mm',font=font,fill='#292929')
    draw.text((970,580),'Esquema frontal, não render CAD.',font=font,fill='#555555')
    draw.text((970,630),'Coluna estilizada da V2;',font=font,fill='#555555')
    draw.text((970,680),'curvas simplificadas no esquema.',font=font,fill='#555555')
    preview = ROOT/'designs/essencial-v3-esquema.png'
    image.save(preview)
    # Verify both QR fields in the published schematic too.
    gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY)
    for name,rows,bottom in values['row_layout']():
        x0,y0=xy(49,bottom+52)
        x1,y1=xy(101,bottom)
        crop=gray[y0:y1,x0:x1]
        decoded,_,_=cv2.QRCodeDetector().detectAndDecode(crop)
        assert decoded==LINKS[name], name+' preview did not decode'
    with ZipFile(ROOT/'downloads/essencial-fusion-v3.zip','w',ZIP_DEFLATED) as z:
        z.write(folder/'EssencialV3.py','EssencialV3/EssencialV3.py')
        z.write(folder/'README.md','README.md')
        z.write(preview,'essencial-v3-esquema.png')
    print('V3 script generated; both QR codes decode in PNG preview; ZIP saved.')


if __name__=='__main__':
    main()
