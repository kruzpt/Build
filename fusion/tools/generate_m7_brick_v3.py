"""Brick V3: continuous broad brush 7, with shallow left accents and smooth right."""
from pathlib import Path
from shutil import copy2
from copy import deepcopy
import json

import manifold3d as md
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont

import generate_m7_prototypes_v1 as v1
from generate_joana_topper import cross_section,save_mesh
from generate_universo_stand import render_meshes

ROOT=v1.ROOT
FOLDER=ROOT/'fusion/M7TijoloV3'
PREFIX='m7-tijolo-v3'


def seven_outline():
    """Cubic outline from the marked reference, not alternating rectangular cuts."""
    path=[(7.55,8.32)]
    def line(p):path.append(p)
    def curve(c1,c2,end,n=24):
        start=np.array(path[-1]);c1,c2,end=map(np.array,(c1,c2,end))
        t=np.linspace(0,1,n+1)[1:,None]
        points=(1-t)**3*start+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end
        path.extend(points.tolist())
    curve((7.22,8.35),(7.10,8.58),(7.13,8.92))
    line((7.13,9.95))
    curve((7.13,10.30),(7.30,10.50),(7.66,10.53))
    line((14.77,11.25))
    curve((15.18,11.29),(15.49,11.01),(15.38,10.55))
    curve((15.34,10.16),(15.15,9.76),(14.86,9.61))
    # Broad uninterrupted right-hand edge. One small brush taper near the foot.
    curve((14.55,8.62),(14.35,7.23),(13.89,5.98),45)
    curve((13.60,4.95),(13.08,3.83),(12.76,2.80),40)
    line((12.74,2.24));line((12.36,2.46))
    curve((12.12,1.67),(11.92,.71),(11.53,.25))
    curve((11.14,-.05),(10.02,-.08),(9.39,.23))
    curve((8.97,.43),(8.91,.78),(9.08,1.27))
    # Small projecting brush tips interrupt a continuous, wide left-hand stroke.
    curve((9.28,1.82),(9.43,2.25),(9.58,2.70))
    line((9.20,2.76));curve((8.95,2.79),(8.95,3.15),(9.17,3.30),16)
    curve((9.64,3.44),(9.89,3.75),(10.05,4.08))
    curve((10.22,4.43),(10.43,4.76),(10.59,5.10))
    line((10.20,5.16));curve((9.95,5.19),(9.95,5.55),(10.17,5.70),16)
    curve((10.63,5.84),(10.94,6.18),(11.12,6.53))
    curve((11.28,6.82),(11.45,7.10),(11.57,7.35))
    line((11.18,7.41));curve((10.93,7.44),(10.93,7.80),(11.15,7.95),16)
    curve((11.61,8.09),(11.85,8.45),(12.20,8.81))
    curve((10.74,8.65),(9.15,8.39),(7.55,8.32),35)
    return md.CrossSection([path[:-1]],md.FillRule.EvenOdd).simplify(.002)


def make():
    source=json.loads((ROOT/'fusion/M7TijoloV2/geometry.json').read_text())
    old={p['key']:p for p in source['parts']}
    sections={k:cross_section(p['regions'][0]['groups']) for k,p in old.items() if k!='tijolo-terracota'}
    old7=sections['7-ciano']
    bounds=v1.pts(old7);lo,hi=bounds.min(0),bounds.max(0)
    raw=seven_outline();rp=v1.pts(raw);rlo,rhi=rp.min(0),rp.max(0)
    seven=raw.translate(-rlo).scale((hi-lo)/(rhi-rlo)).translate(lo)
    sections['7-ciano']=seven
    frame=sections['estrela-dourada'];m=sections['m-branco']
    assert ((m+seven).offset(.35,circular_segments=16)^frame).area()<1e-6
    assert (m^seven).area()<1e-6
    assert (m.offset(.15)^seven.offset(.15)).area()<1e-6
    profile=cross_section(old['tijolo-terracota']['regions'][0]['groups'])
    body=profile.extrude(70)
    regions=[v1.region(profile,70)];fp=v1.pose_front()
    for key,p in old.items():
        if key=='tijolo-terracota':continue
        cs=sections[key]
        # Preserve every V2 pocket exactly, except for the new 7 contour.
        if key=='7-ciano':r=v1.region(cs.offset(.15,circular_segments=24),.25,-.2,'cut',fp)
        else:
            index=list(old).index(key)
            r=deepcopy(old['tijolo-terracota']['regions'][index])
        cutter=cross_section(r['groups']).extrude(r['height']).translate((0,0,r['z']))
        body-=v1.transformed(cutter,np.array(r['transform']))
        regions.append(r)
    FOLDER.mkdir(exist_ok=True)
    parts=[];assembled=[]
    for key,p in old.items():
        entry=deepcopy(p);entry['file']=f'{PREFIX}-{key}.stl'
        path=ROOT/'downloads'/entry['file']
        if key=='tijolo-terracota':
            solid=body;entry['regions']=regions;mesh=save_mesh(solid.simplify(.003),path)
        elif key=='7-ciano':
            solid=seven.extrude(1.2);entry['regions']=[v1.region(seven,1.2)]
            mesh=save_mesh(solid.simplify(.002),path)
        else:
            solid=sections[key].extrude(1.2)
            copy2(ROOT/'downloads'/p['file'],path);mesh=trimesh.load(path,force='mesh')
        entry.update({'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),
                      'watertight':bool(mesh.is_watertight)})
        assert mesh.is_watertight and mesh.is_winding_consistent
        assert len(mesh.split())==(9 if key=='natal-branco' else 1)
        posed=v1.transformed(solid,np.array(entry['assembly']))
        parts.append(entry);assembled.append((posed,entry['color']))
        if key!='tijolo-terracota':assert (posed^body).volume()<.001
    for i,(s,c) in enumerate(assembled[1:]):
        for t,d in assembled[i+2:]:assert (s^t).volume()<.001
    # Path of each glue-on part through its shallow locating recess.
    for s,c in assembled[1:]:
        for y in np.linspace(0,4,21):assert (s.translate((0,-float(y),0))^body).volume()<.001
    # Reuse V2 mating parts exactly; only body and blue 7 are replaced.
    reusable=['estrela-dourada','arvore-dourada','natal-branco','m-branco']
    for key in reusable:
        assert (ROOT/f'downloads/{PREFIX}-{key}.stl').read_bytes()==(ROOT/'downloads'/old[key]['file']).read_bytes()
    np.testing.assert_allclose(v1.pts(seven).min(0),lo,atol=.001)
    np.testing.assert_allclose(v1.pts(seven).max(0),hi,atol=.001)
    report={'version':3,'change':'Seven and its pocket only; broader continuous stroke with cubic right edge and shallow left brush tips',
        'body_width_depth_height_mm':[50,26,70],'star_width_mm':30,'logo_width_mm':14,
        'seven_bbox_mm':(hi-lo).tolist(),'seven_style':'Curved broad brush stroke, three shallow outward left accents, smooth right edge, rounded foot',
        'broad_stem_nominal_width_mm':2.0,'left_accent_nominal_projection_mm':.3,
        'pocket_depth_mm':.2,'pocket_clearance_per_side_mm':.15,'ornament_thickness_mm':1.2,
        'glue_gap_mm':.05,'all_parts_watertight':True,'insertion_positions_checked':105,
        'reusable_v2_parts':reusable,'requires_new_body_and_seven':True,
        'physical_fit_tested':False,'fusion_runtime_tested':False,
        'parts':[{k:v for k,v in p.items() if k not in ('assembly','regions')} for p in parts]}
    (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','version':3,'parts':parts,'brick':report},ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    script=(ROOT/'fusion/M7TijoloV2/M7TijoloV2.py').read_text().replace('V2','V3')
    (FOLDER/'M7TijoloV3.py').write_text(script)
    illustrate(assembled,frame,m,old7,seven)
    print(json.dumps(report,ensure_ascii=False,indent=2))


def illustrate(assembled,frame,m,old7,new7):
    font=lambda n:ImageFont.truetype(v1.REGULAR,n)
    # A true geometric side-by-side comparison, without styling invented by a render.
    image=Image.new('RGB',(1500,1100),'#f4f6f8');draw=ImageDraw.Draw(image)
    draw.text((40,25),'7 — V2 e V3, na mesma escala',font=font(36),fill=v1.BLUE)
    for i,(cs,title) in enumerate([(old7,'V2 — recortes demasiado fundos'),(new7,'V3 — traço largo e contínuo')]):
        points=v1.pts(cs);low,high=points.min(0),points.max(0);scale=93
        cx=380+i*730;cy=580
        for loop in cs.to_polygons():
            draw.polygon([(cx+(x-(low[0]+high[0])/2)*scale,cy-(y-(low[1]+high[1])/2)*scale) for x,y in loop],fill=v1.CYAN)
        draw.text((45+i*730,135),title,font=font(26),fill=v1.BLUE)
    draw.text((50,990),'V3: bordo direito em Bézier; pequenas saliências à esquerda, sem recortes profundos.',font=font(25),fill=v1.BLUE)
    draw.text((50,1045),'Contornos reais dos ficheiros · estrela, m, árvore e inscrição iguais à V2.',font=font(24),fill=v1.BLUE)
    image.save(ROOT/f'designs/{PREFIX}-comparacao.png')
    canvas=Image.new('RGB',(1530,1060),'#f4f6f8');d=ImageDraw.Draw(canvas)
    canvas.paste(render_meshes(assembled,(840,850),direction=(.45,-.8,.55)),(0,120))
    symbol=[(v1.transformed(cs.extrude(1.2),v1.pose_front()),col) for cs,col in [(frame,v1.GOLD),(m,v1.WHITE),(new7,v1.CYAN)]]
    panel=md.Manifold.cube((36,.5,34)).translate((-18,.2,38))
    canvas.paste(render_meshes([(panel,v1.ORANGE)]+symbol,(650,740),direction=(.03,-1,.05)),(860,160))
    d.text((40,25),'M7 — tijolo V3 · 7 com traço contínuo',font=font(34),fill=v1.BLUE)
    d.text((40,77),'Correção da silhueta; o novo 7 mantém o tamanho e a posição da V2.',font=font(24),fill=v1.BLUE)
    d.text((40,1000),'Substituir o corpo e o 7 · restantes peças reutilizáveis da V2 · profundidade dos rebaixos 0,20 mm',font=font(23),fill=v1.BLUE)
    canvas.save(ROOT/f'designs/{PREFIX}-CAD.png')


if __name__=='__main__':make()
