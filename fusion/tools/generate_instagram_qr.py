"""Generate the Instagram QR artifacts; run from any directory.

Dependencies: requirements-qr.txt. Fusion itself is not needed for generation.
"""
import ast
import json
import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import cv2
import manifold3d as md
import numpy as np
import qrcode
import trimesh

ROOT = Path(__file__).resolve().parents[2]
URL = 'https://www.instagram.com/clinicaessencial_setubal/'
SIZE = 51.2
BASE = 0.6
RELIEF = 0.6
EDGE_INSET = 0.01  # Avoid zero-width contacts between raised QR strips.


def runs(rows):
    for row, values in enumerate(rows):
        start = None
        for col, value in enumerate(values + '0'):
            if value == '1' and start is None:
                start = col
            elif value == '0' and start is not None:
                yield row, start, col
                start = None


def main():
    designs = ROOT / 'designs'
    downloads = ROOT / 'downloads'
    downloads.mkdir(exist_ok=True)
    designs.mkdir(exist_ok=True)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                       box_size=20, border=4)
    qr.add_data(URL)
    qr.make(fit=True)
    rows = [''.join('1' if cell else '0' for cell in row)
            for row in qr.get_matrix()]
    n = len(rows)
    pitch = SIZE/n
    qr.make_image(fill_color='black',back_color='white').save(
        designs/'instagram-qr.png')
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(
        cv2.imread(str(designs/'instagram-qr.png')))
    assert decoded == URL, 'PNG did not decode to the requested URL'

    # Rounded tile corners fit the rounded 52 mm plaque recess.
    radius = 2.0
    boundary = []
    for cx,cy,start in [(SIZE-radius,radius,-90),
                        (SIZE-radius,SIZE-radius,0),
                        (radius,SIZE-radius,90),(radius,radius,180)]:
        for angle in np.linspace(start,start+90,17):
            boundary.append((cx+radius*math.cos(math.radians(angle)),
                             cy+radius*math.sin(math.radians(angle))))
    base = md.Manifold.extrude(md.CrossSection([boundary]),BASE)
    rectangles = []
    for row,start,end in runs(rows):
        x0,x1 = start*pitch,end*pitch
        y0,y1 = (n-row-1)*pitch,(n-row)*pitch
        rectangles.append([(x0+EDGE_INSET,y0+EDGE_INSET),
                           (x1-EDGE_INSET,y0+EDGE_INSET),
                           (x1-EDGE_INSET,y1-EDGE_INSET),
                           (x0+EDGE_INSET,y1-EDGE_INSET)])
    # Union black rectangles in 2D first, preserving holes and touching cells.
    ink = md.Manifold.extrude(md.CrossSection(rectangles),RELIEF+0.02)
    ink = ink.translate((0,0,BASE-0.02))
    solid = base + ink
    output = solid.to_mesh()
    mesh = trimesh.Trimesh(vertices=np.asarray(output.vert_properties)[:,:3],
                           faces=np.asarray(output.tri_verts),process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert mesh.volume > 0 and len(mesh.split()) == 1
    assert np.allclose(mesh.extents,[SIZE,SIZE,BASE+RELIEF],atol=1e-5)
    mesh.export(downloads/'instagram-qr-51mm.stl')
    # Check the exported file too, not only the mesh in memory.
    exported = trimesh.load(downloads/'instagram-qr-51mm.stl',force='mesh')
    assert exported.is_watertight and exported.is_winding_consistent
    assert len(exported.split()) == 1

    # Reconstruct a top view from the actual STL's raised top triangles.
    image_size = n*20
    raster = np.full((image_size,image_size),255,dtype=np.uint8)
    triangles = exported.triangles
    top = triangles[np.all(np.isclose(triangles[:,:,2],BASE+RELIEF),axis=1)]
    for triangle in top:
        xy = triangle[:,:2].copy()
        xy[:,0] *= image_size/SIZE
        xy[:,1] = image_size-xy[:,1]*image_size/SIZE
        cv2.fillConvexPoly(raster,np.rint(xy).astype(np.int32),0)
    for row in range(n):
        for col in range(n):
            assert (raster[row*20+10,col*20+10] == 0) == (rows[row][col]=='1')
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(raster)
    assert decoded == URL, 'STL top projection failed to decode'
    cv2.imwrite(str(designs/'instagram-qr-stl-top.png'),raster)
    (designs/'instagram-qr-matrix.json').write_text(json.dumps({
        'url':URL,'error_correction':'Q','version':qr.version,
        'quiet_zone_modules':4,'tile_width_mm':SIZE,
        'module_width_mm':pitch,'rows':rows},indent=2)+'\n')

    folder = ROOT/'fusion/EssencialV2Instagram'
    folder.mkdir(exist_ok=True)
    source = (ROOT/'fusion/EssencialV2/EssencialV2.py').read_text()
    literal = 'QR_ROWS = [\n' + ''.join('    '+repr(row)+',\n' for row in rows) + ']\n'
    source = source.replace('import adsk.fusion\n',
                            'import adsk.fusion\n\n'+literal)
    old = '''        # Recess for a printed QR label, rather than a fake scannable pattern.
        qr = rounded_rectangle(c,'QR label recess',17,30,52,52,2,
                               PANEL_THICKNESS-0.6,0.8)
        combine(c,plate,qr,ops.CutFeatureOperation)
'''
    new = '''        # Functional Instagram QR, joined into the plate: no third part.
        # Includes a four-module quiet zone. Keep the field white and modules black.
        qr_pitch = 52.0/len(QR_ROWS)
        edge_inset = 0.01  # Avoid degenerate corner contacts between strips.
        for row, values in enumerate(QR_ROWS):
            start = None
            for col, value in enumerate(values+'0'):
                if value == '1' and start is None:
                    start = col
                elif value == '0' and start is not None:
                    sk = sketch(c,'QR row %d run %d' % (row,start),
                                PANEL_THICKNESS-0.02)
                    sk.sketchCurves.sketchLines.addTwoPointRectangle(
                        point(17+start*qr_pitch+edge_inset,
                              30+(len(QR_ROWS)-row-1)*qr_pitch+edge_inset),
                        point(17+col*qr_pitch-edge_inset,
                              30+(len(QR_ROWS)-row)*qr_pitch-edge_inset))
                    c.features.extrudeFeatures.addSimple(sk.profiles.item(0),
                        adsk.core.ValueInput.createByReal(0.062),
                        ops.JoinFeatureOperation)
                    sk.isVisible = False
                    start = None
'''
    assert old in source
    source = source.replace(old,new)
    source = source.replace("label('QR',36,17,30,5)",
                            "label('Instagram',18,17,70,5)")
    source = source.replace('QR and exact logo artwork are still pending.',
                            'QR: Instagram clinicaessencial_setubal. Logo still approximate.')
    source = source.replace('V2 created: TWO parts','Instagram version created: TWO parts')
    ast.parse(source)
    (folder/'EssencialV2Instagram.py').write_text(source)
    with ZipFile(downloads/'essencial-fusion-instagram.zip','w',ZIP_DEFLATED) as z:
        z.write(folder/'EssencialV2Instagram.py',
                'EssencialV2Instagram/EssencialV2Instagram.py')
        z.write(ROOT/'fusion/README-Instagram.md','README.md')
        z.write(downloads/'instagram-qr-51mm.stl','instagram-qr-51mm.stl')
        z.write(designs/'instagram-qr.png','instagram-qr.png')
    with ZipFile(downloads/'essencial-fusion-instagram.zip') as z:
        assert z.testzip() is None
    print(f'QR v{qr.version}, {n}x{n} incl. border; pitch {pitch:.3f} mm.')
    print(f'PNG and STL top-view both decode to {decoded}')
    print(f'STL: watertight, one solid, {SIZE} x {SIZE} x {BASE+RELIEF} mm.')
    print('Fusion syntax checked; Fusion execution and physical scanning pending.')


if __name__ == '__main__':
    main()
