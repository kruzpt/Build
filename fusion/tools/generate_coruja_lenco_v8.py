"""Standalone all-green scarf with a top-only brown knot; fits the V6 pocket."""
from pathlib import Path
import hashlib
import json
import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

import generate_coruja_bruna_v6 as v6
from generate_coruja_bruna_v3 import exact, union
from generate_m7_prototypes_v1 import pts
from generate_universo_stand import render_meshes

ROOT=v6.ROOT
FOLDER=ROOT/'fusion/CorujaBrunaLencoV8'
PREFIX='anilha-coruja-bruna-lenco-v8'
GREEN,BROWN=v6.GREEN,v6.BROWN

def models():
    _,old,_,_,_=v6.build()
    outline=old[v6.BLACK].slice(.25)
    brown=old[BROWN].slice(.9)
    central=[]
    for island in brown.decompose():
        x0,y0,x1,y1=island.bounds()
        if 0<x0 and x1<4 and 23<y0 and y1<27:
            central.append(island)
    assert len(central)==2
    old_knot=md.CrossSection.batch_boolean(central,md.OpType.Add)
    hull=cv2.convexHull(pts(old_knot).astype(np.float32))[:,0,:]
    knot=md.CrossSection([hull.tolist()]) ^ outline
    # Restore the original inset fabric panels and raised surrounding frame,
    # but print both in green: relief defines the folds instead of a third ink.
    panels=old[GREEN].slice(.8).offset(-.04,md.JoinType.Round,circular_segments=16)
    panels-=knot.offset(.08,md.JoinType.Round,circular_segments=16)
    green=outline.extrude(1.2)-panels.extrude(.6).translate((0,0,.9))
    # Two individually raised knot lobes reproduce the original wrapped shape.
    # A continuous brown floor keeps the valley and outer knot edge brown.
    brown=knot.extrude(.2).translate((0,0,1.2))
    lobes=old_knot.offset(-.025,md.JoinType.Round,circular_segments=16)^knot
    brown+=lobes.extrude(.1).translate((0,0,1.4))
    brown+=lobes.offset(-.04,md.JoinType.Round,circular_segments=16).extrude(.1).translate((0,0,1.5))
    assert (green^brown).volume()<1e-6
    assert len([s for s in (green+brown).decompose() if s.volume()>1e-5])==1
    assert (green.slice(.25)-outline).area()<1e-6
    assert (outline-green.slice(.25)).area()<1e-6
    return green,brown

def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    green,brown=models()
    parts=[]
    for key,color,solid in [('verde',GREEN,green),('no-castanho',BROWN,brown)]:
        target=ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=exact(solid,target)
        parts.append({'key':key,'file':target.name,'color':color,
                      'volume_mm3':mesh.volume,'dimensions_mm':mesh.extents.tolist(),
                      'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    whole=exact(green+brown,ROOT/'downloads'/f'{PREFIX}-completo-monocor.stl')
    data={'title':'Lenço V8 com dobras em relevo e nó castanho',
          'dimensions_mm':whole.extents.tolist(),'green_height_mm':1.2,
          'brown_z_range_mm':[1.2,1.6],'knot_groove_depth_mm':.2,
          'green_recess_depth_mm':.3,'minimum_green_floor_mm':.9,
          'same_insert_outline_as_V6':True,'assembly_bottom_z_on_owl_mm':2.15,
          'compatible_owl':'anilha-coruja-bruna-v6','physical_print_tested':False,
          'parts':parts}
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    sheet=Image.new('RGB',(1450,850),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet.paste(render_meshes([(green,GREEN),(brown,BROWN)],(700,620),direction=(0,-.01,1),margin=45),(0,100))
    sheet.paste(render_meshes([(green,GREEN),(brown,BROWN)],(700,620),direction=(.35,-.7,1),margin=45),(730,100))
    draw.text((30,25),'Lenço V8 · dobras e moldura verdes + nó em relevo',font=font(32),fill=BROWN)
    dims=data['dimensions_mm']
    draw.text((30,760),f'{dims[0]:.2f} × {dims[1]:.2f} mm · base 1,20 mm · nó até 1,60 mm',font=font(25),fill=BROWN)
    draw.text((30,805),'Encaixe V6 · bico 0,2 mm · camadas 0,10 mm · geometria real',font=font(23),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    scene=trimesh.Scene()
    for p in parts:
        mesh=trimesh.load(ROOT/'downloads'/p['file'],force='mesh')
        mesh.visual.face_colors=tuple(int(p['color'][i:i+2],16) for i in (1,3,5))+(255,)
        scene.add_geometry(mesh,node_name=p['key'])
    scene.export(ROOT/'downloads'/f'{PREFIX}-montado.glb')
    print(json.dumps(data,indent=2))

if __name__=='__main__':main()
