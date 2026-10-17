"""M7 brick V2: hand-drawn brush-like 7, enlarged star/logo and matching pockets."""
from pathlib import Path
import json
import math
from copy import deepcopy
from shutil import copy2

import manifold3d as md
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import trimesh

import generate_m7_prototypes_v1 as v1
from generate_joana_topper import cross_section,save_mesh
from generate_universo_stand import render_meshes,mesh_of

ROOT=v1.ROOT
FOLDER=ROOT/'fusion/M7TijoloV2'
PREFIX='m7-tijolo-v2'


def brush_logo(width=14):
    # Keep the rounded m from V1; replace the plain diagonal 7 with brush edges.
    m=v1.logo(21.75)[0]
    # Recover m's original origin before centering the complete, new logo.
    p=v1.pts(m);m=m.translate((-6.3-p[:,0].min(),-p[:,1].min()))
    seven=md.CrossSection([[
        (7.30,8.35),(7.13,8.65),(7.13,9.90),(7.26,10.30),(7.62,10.52),
        (14.75,11.25),(15.13,11.18),(15.38,10.87),(15.38,10.35),
        (15.13,9.77),(14.57,9.42),
        (14.15,8.10),(14.30,7.72),(13.65,6.03),(13.81,5.62),
        (13.18,3.94),(13.34,3.53),(12.32,.80),
        (12.02,.32),(11.58,.08),(10.88,.02),(10.08,.16),(9.73,.48),(9.75,.90),
        (10.35,2.63),(11.06,2.77),(10.58,3.32),
        (11.25,5.12),(11.97,5.26),(11.48,5.82),
        (12.15,7.63),(12.84,7.77),(12.36,8.33),
        (12.19,8.81),(7.71,8.27)
    ]],md.FillRule.EvenOdd)
    # Slightly round stroke terminals without erasing the intentional notches.
    seven=seven.offset(-.07,circular_segments=32).offset(.07,circular_segments=32)
    points=v1.pts(m+seven);lo,hi=points.min(0),points.max(0)
    scale=width/(hi[0]-lo[0]);origin=((lo[0]+hi[0])/2,lo[1])
    return [cs.translate(-np.array(origin)).scale((scale,scale)).simplify(.003) for cs in (m,seven)]


def star(width=30):
    # A slightly wider central opening gives the larger mark comfortable clearance.
    points=[]
    for i in range(10):
        a=math.pi/2+i*math.pi/5;r=11 if i%2==0 else 6.3
        points.append((r*math.cos(a),r*math.sin(a)))
    outer=md.CrossSection([points])
    return v1.normalize(outer-outer.offset(-.95,circular_segments=20),width=width)


def fit_logo(frame,m,seven):
    candidates=[]
    clear=(m+seven).offset(.35,circular_segments=16)
    for y in np.arange(49.5,53.51,.1):
        for x in np.arange(-1.0,1.01,.1):
            if (clear.translate((float(x),float(y)))^frame).area()<1e-6:
                score=(x-.15)**2+(y-50.5)**2
                candidates.append((score,float(x),float(y)))
    if not candidates:raise RuntimeError('Enlarged logo does not clear the star')
    _,x,y=min(candidates)
    return m.translate((x,y)),seven.translate((x,y)),[x,y]


def make():
    data=json.loads((ROOT/'fusion/M7PrototiposV1/geometry.json').read_text())
    old={p['key']:p for p in data['parts'] if p['product']=='tijolo'}
    profile=cross_section(old['tijolo-terracota']['regions'][0]['groups'])
    body=profile.extrude(70)
    tree=cross_section(old['arvore-dourada']['regions'][0]['groups'])
    date=cross_section(old['natal-branco']['regions'][0]['groups'])
    frame=star().translate((0,40))
    m,seven=brush_logo()
    m,seven,offset=fit_logo(frame,m,seven)
    assert ((frame+tree)^date).area()<1e-6
    assert (frame^tree).area()<1e-6
    # Offsets also stay apart, avoiding merged positioning recesses.
    assert (frame.offset(.15)^((m+seven).offset(.15))).area()<1e-6
    pieces=[('estrela-dourada',frame,v1.GOLD),('arvore-dourada',tree,v1.GOLD),
            ('natal-branco',date,v1.WHITE),('m-branco',m,v1.WHITE),('7-ciano',seven,v1.CYAN)]
    regions=[v1.region(profile,70)]
    fp=v1.pose_front();assembly=fp.copy();assembly[:3,3]+=fp[:3,2]*-.15
    for key,cs,col in pieces:
        pocket=cs.offset(.15,circular_segments=24)
        points=v1.pts(pocket)
        assert points[:,0].min()>-23 and points[:,0].max()<23
        assert points[:,1].min()>1 and points[:,1].max()<69.5
        body-=v1.transformed(pocket.extrude(.25).translate((0,0,-.2)),fp)
        regions.append(v1.region(pocket,.25,-.2,'cut',fp))
    parts=[];assembled=[]
    def add(key,solid,color,pose,regions):
        path=ROOT/f'downloads/{PREFIX}-{key}.stl'
        if key in ('arvore-dourada','natal-branco'):
            copy2(ROOT/'downloads'/old[key]['file'],path)
            mesh=trimesh.load(path,force='mesh')
        else:mesh=save_mesh(solid.simplify(.003),path)
        assert len(mesh.split())==(9 if key=='natal-branco' else 1)
        parts.append({'key':key,'name':key,'file':path.name,'color':color,'product':'tijolo',
            'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(solid.volume()),
            'watertight':True,'assembly':pose.tolist(),'regions':regions})
        assembled.append((v1.transformed(solid,pose),color))
    add('tijolo-terracota',body,v1.ORANGE,v1.identity(),regions)
    for key,cs,col in pieces:
        solid=cs.extrude(1.2)
        actual=v1.transformed(solid,assembly)
        assert (actual^body).volume()<.001
        add(key,solid,col,assembly,[v1.region(cs,1.2)])
    for i,(a,c) in enumerate(assembled[1:]):
        for b,d in assembled[i+2:]:assert (a^b).volume()<.001
    # Positive clearance of the actual ornaments at every depth while inserting.
    insertions=0
    for solid,col in assembled[1:]:
        for distance in np.linspace(0,4,21):
            assert (solid.translate((0,-float(distance),0))^body).volume()<.001
            insertions+=1
    old_tree=trimesh.load(ROOT/'downloads'/old['arvore-dourada']['file'],force='mesh')
    old_date=trimesh.load(ROOT/'downloads'/old['natal-branco']['file'],force='mesh')
    for key,ref in [('arvore-dourada',old_tree),('natal-branco',old_date)]:
        current=trimesh.load(ROOT/f'downloads/{PREFIX}-{key}.stl',force='mesh')
        assert abs(current.volume-ref.volume)<.05
        np.testing.assert_allclose(current.extents,ref.extents,atol=.01)
    report={'version':2,'body_width_depth_height_mm':[50,26,70],
            'star_width_mm':30,'star_width_v1_mm':24,'logo_width_mm':14,'logo_width_v1_mm':10,
            'logo_position_mm':offset,'seven_style':'Manual brush silhouette: rising rounded bar, three broad left-edge notches, irregular right edge, rounded foot',
            'seven_bbox_mm':(v1.pts(seven).max(0)-v1.pts(seven).min(0)).tolist(),
            'm_bbox_mm':(v1.pts(m).max(0)-v1.pts(m).min(0)).tolist(),
            'minimum_logo_to_star_clearance_mm':.35,'pocket_depth_mm':.2,
            'pocket_lateral_clearance_per_side_mm':.15,'ornament_thickness_mm':1.2,
            'glue_gap_mm':.05,'insertion_positions_checked':insertions,
            'all_parts_watertight':True,'tree_and_date_reusable_from_v1':True,
            'body_star_and_logo_v1_compatible':False,'physical_fit_tested':False,
            'fusion_runtime_tested':False,'parts':[{k:v for k,v in p.items() if k not in ('regions','assembly')} for p in parts]}
    definition={'units':'mm','version':2,'parts':parts,'brick':report}
    FOLDER.mkdir(exist_ok=True)
    (FOLDER/'geometry.json').write_text(json.dumps(definition,ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    # Self-contained Fusion script, reusing the tested syntax of the V1 importer.
    script=(ROOT/'fusion/M7PrototiposV1/M7PrototiposV1.py').read_text()
    script=script.replace('M7 prototype BRep bodies','M7 brick V2 BRep bodies')
    script=script.replace('M7 - Casinha e Tijolo - protótipos V1','M7 - Tijolo Natal 2026 V2 - 7 pincelado')
    script=script.replace("            if part['product']=='tijolo':tm[0][3]+=140\n",'')
    script=script.replace("'M7 V1 criado num documento novo.\\n'","'M7 Tijolo V2 criado num documento novo.\\n'")
    script=script.replace("            'Casa: 95 mm, base 85 x 85 mm, ranhura 6,30 mm.\\n'\n",'')
    script=script.replace("'Use os projetos 3MF fornecidos para imprimir um de cada.\\n'","'Use o projeto 3MF V2 de quatro pratos para imprimir.\\n'")
    (FOLDER/'M7TijoloV2.py').write_text(script)
    illustrate(assembled,frame,m,seven)
    print(json.dumps(report,ensure_ascii=False,indent=2))


def illustrate(assembled,frame,m,seven):
    font=lambda n:ImageFont.truetype(v1.REGULAR,n)
    im=Image.new('RGB',(1550,1070),'#f4f6f8');d=ImageDraw.Draw(im)
    im.paste(render_meshes(assembled,(840,850),direction=(.45,-.8,.55)),(0,130))
    d.text((45,24),'M7 — tijolo V2 · 7 com traço pincelado',font=font(34),fill=v1.BLUE)
    d.text((45,77),'Contorno real dos STL / 3MF · estrela 30 mm · logótipo 14 mm',font=font(24),fill=v1.BLUE)
    # Isolated real symbol, oriented frontwards, at large scale for inspection.
    symbol=[(cs.extrude(1.2),col) for cs,col in [(frame,v1.GOLD),(m,v1.WHITE),(seven,v1.CYAN)]]
    posed=[(v1.transformed(s,v1.pose_front()),col) for s,col in symbol]
    # Terracotta backing is only a preview background, not an additional part.
    panel=md.Manifold.cube((36,.5,34)).translate((-18,.2,38))
    im.paste(render_meshes([(panel,v1.ORANGE)]+posed,(650,730),direction=(.08,-1,.10)),(870,150))
    d.text((900,920),'Topo inclinado e arredondado',font=font(23),fill=v1.BLUE)
    d.text((900,958),'Três recortes no traço descendente',font=font(23),fill=v1.BLUE)
    d.text((45,1020),'Rebaixos atualizados · profundidade 0,20 mm · peça ciano única, espessura 1,20 mm',font=font(23),fill=v1.BLUE)
    im.save(ROOT/f'designs/{PREFIX}-CAD.png')
    close=Image.new('RGB',(1200,900),'#f4f6f8');d=ImageDraw.Draw(close)
    close.paste(render_meshes([(panel,v1.ORANGE)]+posed,(1080,720),direction=(.0,-1,.015)),(60,100))
    d.text((40,20),'M7 V2 — pormenor do contorno imprimível',font=font(31),fill=v1.BLUE)
    d.text((40,840),'Geometria real: a imagem não acrescenta detalhes que não existam no modelo.',font=font(22),fill=v1.BLUE)
    close.save(ROOT/f'designs/{PREFIX}-logo.png')


if __name__=='__main__':make()
