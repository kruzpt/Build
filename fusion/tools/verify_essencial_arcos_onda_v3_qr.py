"""Check projected black relief material coverage; not a physical scan."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
import trimesh

from build_pintos_pla_3mf import read_project
from build_m7_prototypes_v1_3mf import plate_meshes
from generate_essencial_arcos_220_onda_v3 import ROOT,FOLDER,PREFIX,URLS,qr_rows


def main():
    source=trimesh.load(ROOT/'downloads'/f'{PREFIX}-qr-texto-preto.stl',force='mesh')
    project=ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf'
    blobs,settings,_=read_project(project)
    meshes=plate_meshes(blobs,settings)
    target=next(mesh for key,color,mesh in meshes[0] if color==4)
    tree=cKDTree(target.vertices);match=None
    for angle in (0,np.pi/2,np.pi,3*np.pi/2):
        rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
        vertices=source.vertices@rot.T
        shift=(target.bounds[0]+target.bounds[1]-vertices.min(0)-vertices.max(0))/2
        if tree.query(vertices+shift)[0].max()<.002:match=(rot,shift);break
    assert match is not None
    rot,shift=match
    with ZipFile('/tmp/essencial-arcos-220-onda-v3/slice/validation.3mf') as z:
        code=z.read('Metadata/plate_1.gcode').decode()
    # Check actual object extrusion material, excluding prime tower/custom moves.
    material_layers={};active=0;zheight=0.;feature='Custom'
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):zheight=float(line.split(':')[1])
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        change=re.match(r'^M620 S([0-3])A',line) or re.match(r'^T([0-3])\s*$',line)
        if change:active=int(change[1])
        if zheight<=0 or feature in ('Custom','Prime tower'):continue
        if not line.startswith(('G1 ','G2 ','G3 ')):continue
        vals={a:float(b) for a,b in re.findall(r'([XYE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
        if vals.get('E',0)>0 and ('X' in vals or 'Y' in vals):material_layers.setdefault(zheight,set()).add(active)
    assert len(material_layers)==25
    assert all(tools=={0} for z,tools in material_layers.items() if z<=3.68001)
    assert all(tools=={2,3} for z,tools in material_layers.items() if z>3.68001)
    color_sequence={'white_only_layers':23,'white_finished_z_mm':3.68,
                    'top_color_layers_mm':[3.84,4.0],
                    'material_slots_by_layer':{str(z):[t+1 for t in sorted(tools)] for z,tools in material_layers.items()}}
    x=y=0.;layer=0.;tool=0;segments=[];width=.42
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):layer=float(line.split(':')[1])
        if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1])
        t=re.match(r'^T([0-3])\s*$',line)
        if t:tool=int(t[1])
        if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
        values={a:float(b) for a,b in re.findall(r'([XYEIJ])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
        nx,ny=values.get('X',x),values.get('Y',y)
        # Black from preceding relief layers remains visible through tiny gaps
        # between top strands; inspect the material projection of the relief.
        if tool==3 and 3.68<layer<=4.0001 and values.get('E',0)>0:
            if line.startswith(('G2 ','G3 ')) and ('I' in values or 'J' in values):
                centre=np.array([x+values.get('I',0),y+values.get('J',0)])
                radius=np.linalg.norm(np.array([x,y])-centre)
                a0=np.arctan2(y-centre[1],x-centre[0])
                a1=np.arctan2(ny-centre[1],nx-centre[0])
                clockwise=line.startswith('G2 ')
                sweep=-((a0-a1)%(2*np.pi)) if clockwise else (a1-a0)%(2*np.pi)
                if abs(sweep)<1e-7:sweep=(-1 if clockwise else 1)*2*np.pi
                count=max(3,int(np.ceil(abs(sweep)*radius/.03)))
                previous=(x,y)
                for angle in np.linspace(a0,a0+sweep,count+1)[1:]:
                    current=tuple(centre+radius*np.array([np.cos(angle),np.sin(angle)]))
                    segments.append((previous,current,width));previous=current
            elif (nx,ny)!=(x,y):segments.append(((x,y),(nx,ny),width))
        x,y=nx,ny
    assert segments
    decoded={}
    for name,x in [('Instagram',-78),('Google',14)]:
        corners=np.array([[x,41,0],[x+64,41,0],[x,105,0],[x+64,105,0]])@rot.T+shift
        lo,hi=corners[:,:2].min(0),corners[:,:2].max(0)
        scale=20;image=Image.new('L',(1280,1280),255);draw=ImageDraw.Draw(image)
        def point(p):return ((p[0]-lo[0])*scale,(hi[1]-p[1])*scale)
        count=0
        for start,end,width in segments:
            mid=(np.array(start)+end)/2
            if np.all(mid>=lo) and np.all(mid<=hi):
                draw.line([point(start),point(end)],fill=0,width=max(1,round(width*scale)))
                radius=width*scale/2
                for px,py in (point(start),point(end)):
                    draw.ellipse((px-radius,py-radius,px+radius,py+radius),fill=0)
                count+=1
        raw_value,_,_=cv2.QRCodeDetector().detectAndDecode(np.asarray(image))
        image.save(Path('/tmp/essencial-arcos-220-onda-v3')/f'qr-{name.lower()}-gcode.png')
        # This is a coverage check using the known module grid, not a claim
        # that a camera can scan the synthetic line drawing. Average the
        # central half of each module to avoid relying on a single pixel.
        raster=np.asarray(image);pitch=1280/45
        sampled=np.full((45,45),255,dtype=np.uint8)
        for row in range(45):
            for col in range(45):
                tile=raster[round((row+.25)*pitch):round((row+.75)*pitch),
                            round((col+.25)*pitch):round((col+.75)*pitch)]
                sampled[row,col]=0 if tile.mean()<128 else 255
        grid=Image.fromarray(sampled).resize((1080,1080),Image.Resampling.NEAREST)
        value,_,_=cv2.QRCodeDetector().detectAndDecode(np.asarray(grid))
        assert value==URLS[name],(name,value,count)
        expected=np.array([[bit=='1' for bit in row] for row in qr_rows()[name]])
        # Rotation of the native arrangement can rotate the module grid.
        mismatches=min(int(np.sum((sampled==0)!=np.rot90(expected,k))) for k in range(4))
        assert mismatches==0,(name,mismatches)
        grid.save(FOLDER/f'qr-{name.lower()}-gcode-modules.png')
        decoded[name]={'url':value,'segments':count,'module_mismatches':mismatches,
                       'raw_line_raster_decoded':bool(raw_value),
                       'known_grid_module_sampling_decoded':True}
    report={'projected_relief_layers_mm':[3.84,4.0],'filament_slot':4,'line_width_source':'G-code LINE_WIDTH comments',
        'gcode_sha256':hashlib.sha256(code.encode()).hexdigest(),'decoded':decoded,
        'interpretation':'Known-grid module coverage from projected black relief paths, including preceding relief layers, tessellated arcs/full circles and round caps; not an optical or physical scan',
        'physical_scan_tested':False,'front_color_sequence':color_sequence}
    (FOLDER/'qr-gcode-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
