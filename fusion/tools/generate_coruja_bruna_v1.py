"""Printable owl interpretation: measured vector relief, not a sculpted replica."""
from pathlib import Path
import json
import re
import math
import hashlib

import manifold3d as md
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

from generate_m7_prototypes_v1 import rounded, stroke, text, pts, region
from generate_joana_topper import section_groups
from generate_universo_stand import render_meshes

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/CorujaBrunaV1'
PREFIX = 'anilha-coruja-bruna-v1'
BROWN, CREAM, GOLD, BLACK, GREEN = '#67402B', '#F5E5BB', '#DCA23E', '#191716', '#285D39'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'


def path(s):
    tokens = re.findall(r'[MLCQZ]|-?\d*\.?\d+', s)
    p = []
    i = 0
    cur = np.zeros(2)
    while i < len(tokens):
        cmd = tokens[i];i += 1
        if cmd == 'Z':break
        count = {'M':2, 'L':2, 'Q':4, 'C':6}[cmd]
        q = np.array(list(map(float, tokens[i:i+count]))).reshape(-1, 2);i += count
        if cmd in ('M', 'L'):
            cur = q[0];p.append(cur)
        else:
            a = cur.copy()
            for t in np.linspace(0, 1, 28)[1:]:
                if cmd == 'C':
                    v = (1-t)**3*a+3*(1-t)**2*t*q[0]+3*(1-t)*t*t*q[1]+t**3*q[2]
                else:v = (1-t)**2*a+2*(1-t)*t*q[0]+t*t*q[1]
                p.append(v)
            cur = q[-1]
    return md.CrossSection([[v.tolist() for v in p]], md.FillRule.EvenOdd).simplify(.006)


def ellipse(x, y, rx, ry):
    return md.CrossSection.circle(1, 100).scale((rx, ry)).translate((x, y))


def petal(x, y, length, width, angle):
    shape = path(f'M 0 0 C {-width} {length*.32} {-width*.6} {length*.86} 0 {length} C {width*.6} {length*.86} {width} {length*.32} 0 0 Z')
    return shape.rotate(angle).translate((x, y))


def union(solids):
    return md.Manifold.batch_boolean(list(solids), md.OpType.Add)


def exact(solid, target):
    data = solid.simplify(.0001).to_mesh()
    m = trimesh.Trimesh(np.asarray(data.vert_properties)[:, :3], np.asarray(data.tri_verts), process=True)
    assert m.is_watertight and m.is_winding_consistent
    m.export(target)
    again = trimesh.load(target, force='mesh')
    assert again.is_watertight and again.is_winding_consistent
    return again


def front():
    silhouette = ellipse(0, 21.5, 14.7, 16.5)
    silhouette += path('M -12 32 C -17 36 -13 40 -16.8 44.2 C -12 42.5 -9 46.8 -1 46.5 C 3 46.6 6 49.4 10.5 50 C 11.7 48 13.3 47.8 13.7 44 C 17.5 39 14 30 9 28 C 1 24 -8 26 -12 32 Z')
    silhouette += path('M -16 12 C -18 12 -17.8 9 -17 7 C -20 4 -14 0 0 0 C 14 0 20 4 17 7 C 18 10 18 12 16 12 L 0 7 Z')
    assert abs(pts(silhouette)[:,1].max()-50) < .01
    face = path('M -.3 42 C -5 45.4 -10.4 42.5 -11.5 37.4 C -13 32.7 -7.5 29.6 -2.8 29.8 L .5 28.9 C 3.2 30.5 10.3 30.9 11.2 37.3 C 12.2 42 8.5 45.2 4.6 44.1 C 2.1 43.7 .8 42.4 -.3 42 Z')
    # Subtle face-edge feather notches, broad enough for a 0.4 mm nozzle.
    notches = md.CrossSection()
    for x,y,a in [(-11.1,37,-20),(-10.5,34.6,0),(-8.8,32,15),(-5.5,30.1,30),(8.9,33,160),(10.5,35.3,170),(10.8,38,190)]:
        notches += path('M 0 0 L .7 -.8 L 1.2 .2 Z').rotate(a).translate((x,y))
    face -= notches
    banner = path('M -16 7 Q -14 8.3 -12.8 10 Q 0 7.2 12.8 10 Q 14 8.3 16 7 Q 14.5 4.6 13.3 3.1 Q 0 -.1 -13.3 3.1 Q -14.5 4.6 -16 7 Z')
    pages = path('M -9.8 18.5 Q -5 18.9 0 15.1 Q 5 18.9 9.8 18.5 L 10.8 15.8 Q 5 15.4 0 11.9 Q -5 15.4 -10.8 15.8 Z')
    cream_sections = face+banner+pages
    scarf = path('M -9.3 29 Q -7 27.5 2.8 25 Q 7 27.9 10.4 29.6 L 10.4 27.7 Q 7.1 26 4.5 24.3 Q 6 22.6 5.8 19.6 L 4.2 20.4 L 3.4 19.4 L 2.9 23.4 Q 1.6 22.5 .6 23.8 Q -6 25.2 -9.5 27.4 Z')
    scarf = scarf.offset(-.12).offset(.12, circular_segments=24)
    pocket = scarf.offset(.20, circular_segments=24)
    # All green is one glueable piece. The pocket has lateral and bottom glue clearance.
    base = silhouette.extrude(2.4)-pocket.extrude(.4).translate((0,0,2.0))
    brown_regions = [region(silhouette,2.4), region(pocket,.4,2.0,'cut')]
    brown_items = [base]
    gold_items = []
    gold_regions = []
    gold_footprints = md.CrossSection()
    def golden(section, z=2.4, height=.64):
        nonlocal gold_footprints
        section = (section ^ silhouette)-pocket
        if z < 3:section -= cream_sections.offset(.20)
        if section.is_empty():return
        if z < 3:gold_footprints += section
        gold_items.append(section.extrude(height).translate((0,0,z)))
        gold_regions.append(region(section,height,z))
    # Eight separate broad feather outlines per wing, staggered for clear layering.
    for mirror in (-1,1):
        for x,y,l,w,a in [(10.7,23.5,6.1,1.5,22),(12,20.1,6.8,1.65,18),
                           (13,16.2,7,1.6,10),(13.5,12.2,6.7,1.55,-2),
                           (10.2,10.4,7.3,1.7,-22),(7,10,6.1,1.6,-38),
                           (9,17,7,1.65,-10),(8.7,21.1,5.6,1.5,5)]:
            shape = petal(x,y,l,w,a)
            if mirror == -1:shape = shape.mirror((1,0))
            # A small gap exposes the brown supporting outline between feathers.
            shape -= gold_footprints.offset(.35)
            golden(shape)
    golden(path('M -15.3 43.4 Q -10.5 42.4 -5.1 44.3 Q -9.4 43.9 -14.4 44.6 Z'))
    golden(path('M 1.4 44.1 Q 2.8 46.5 9.9 49.1 Q 8.8 46.3 3 43 Z'))
    golden(petal(-14.3,6.1,5.2,1.1,31))
    golden(petal(14.3,6.1,5.2,1.1,-31))
    flame = path('M .1 17.4 C -4 20 -2.1 21.8 -.5 23.4 Q -.2 22.1 .1 21.6 Q 1.7 24 1.8 25 C 5 21.5 2.9 19 .1 17.4 Z')
    flame -= stroke([(-.1,18.6),(.8,20.2),(.5,21.2)], .6)
    golden(flame)
    # Beak sits on the cream mask instead of occupying the same volume.
    golden(path('M -.1 36.4 Q 1.4 37 2.7 35.9 L 1.8 32.5 Q .8 33.1 -.1 36.4 Z'),3.2,.48)
    cream_items = [cream_sections.extrude(.8).translate((0,0,2.4))]
    cream_regions = [region(cream_sections,.8,2.4)]
    black_items = []
    black_regions = []
    for x,y in [(-5.0,37.1),(5.1,38.6)]:
        rim = ellipse(x,y,2.85,3.05)
        iris = ellipse(x+.1,y-.1,2.27,2.45)
        pupil = ellipse(x+.2,y+.1,1.33,1.72)
        glint = ellipse(x-.23,y+.9,.43,.43)
        assert (rim-face).area() < .001
        for sec,z,h,items,regions in [(rim,3.2,.32,black_items,black_regions),
                                    (iris,3.52,.32,gold_items,gold_regions),
                                    (pupil,3.84,.32,black_items,black_regions),
                                    (glint,4.16,.32,cream_items,cream_regions)]:
            items.append(sec.extrude(h).translate((0,0,z)));regions.append(region(sec,h,z))
    brows = stroke([(-8.1,39.1),(-6.9,40),(-5.7,40.3),(-4.1,40),(-2.5,40.6)],.85)
    brows += stroke([(2.2,40.7),(3.9,41.7),(5.8,42),(7.1,43.1)],.9)
    brows ^= face
    black_items.append(brows.extrude(.48).translate((0,0,3.2)));black_regions.append(region(brows,.48,3.2))
    face_texture=md.CrossSection()
    for a,b in [((-10.2,36),(-8.9,34.9)),((-9.7,34.4),(-8.1,33.4)),
                ((-7.9,32.9),(-6.3,31.8)),((-5.6,31.8),(-4.4,30.7)),
                ((-3.5,31.4),(-2.6,30.3)),((3.9,31.7),(4.8,32.8)),
                ((6,32.5),(7,33.8)),((8,34.1),(9.2,35.2)),
                ((8.9,37),(10.1,38)),((-8.6,41),(-7.4,42)),
                ((3.2,42.9),(4.7,43.4))]:
        face_texture+=stroke([a,b],.5)
    eyes=ellipse(-5,37.1,3.3,3.5)+ellipse(5.1,38.6,3.3,3.5)
    face_texture=(face_texture^face.offset(-.35))-eyes-brows.offset(.3)
    face_texture-=ellipse(1,35,2.5,3)
    cream_items.append(face_texture.extrude(.16).translate((0,0,3.2)))
    cream_regions.append(region(face_texture,.16,3.2))
    name = text('BRUNA',25,font=SERIF)
    pp = pts(name);name = name.scale((1,3.8/(pp[:,1].max()-pp[:,1].min()))).translate((0,3.4))
    assert (name-banner).area() < .001
    brown_items.append(name.extrude(.48).translate((0,0,3.2)));brown_regions.append(region(name,.48,3.2))
    page_lines = md.CrossSection()
    for s in (-1,1):
        for dy in (0,.9):
            page_lines += stroke([(s*.8,13.5+dy),(s*3.3,15+dy),(s*6,16.1+dy),(s*8.8,16.7+dy)],.46)
    page_lines ^= pages
    brown_items.append(page_lines.extrude(.16).translate((0,0,3.2)));brown_regions.append(region(page_lines,.16,3.2))
    # Same-material ridges imply wood/feather texture without introducing a fifth AMS color.
    texture = md.CrossSection()
    for x,y in [(-4,21),(-6,23),(-3,25),(0,26),(-3.5,44),(0,44.5),(2,46)]:
        texture += stroke([(x-.8,y-.8),(x,y+.3),(x+1.1,y+.8)],.55)
    texture = texture ^ silhouette
    texture -= cream_sections.offset(.35)+gold_footprints.offset(.25)+pocket
    brown_items.append(texture.extrude(.32).translate((0,0,2.4)));brown_regions.append(region(texture,.32,2.4))
    return [(k,c,union(items),regions) for k,c,items,regions in [
        ('castanho',BROWN,brown_items,brown_regions),('creme',CREAM,cream_items,cream_regions),
        ('dourado',GOLD,gold_items,gold_regions),('preto',BLACK,black_items,black_regions)]], scarf, silhouette


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    parts, scarf, silhouette = front()
    entries=[];solids=[]
    def add(key,color,solid,regions,assembly=None):
        filename=f'{PREFIX}-{key}.stl'
        mesh=exact(solid,ROOT/'downloads'/filename)
        matrix=np.eye(4) if assembly is None else assembly
        entries.append({'key':key,'name':key,'product':'Coruja BRUNA','file':filename,'color':color,'regions':regions,
            'assembly':matrix.tolist(),'dimensions_mm':mesh.extents.tolist(),
            'volume_mm3':mesh.volume,'watertight':True,
            'sha256':hashlib.sha256((ROOT/'downloads'/filename).read_bytes()).hexdigest()})
        solids.append((solid.transform(matrix[:3].tolist()),color))
    for key,color,solid,regions in parts:add(key,color,solid,regions)
    green = scarf.extrude(1.2)
    matrix=np.eye(4);matrix[2,3]=2.15
    add('lenco-verde',GREEN,green,[region(scarf,1.2)],matrix)
    outer=ellipse(0,0,15,11.5)
    inner=ellipse(0,0,12.5,9)
    mount=rounded(-7,-13,14,4,.6)
    ring_section=(outer+mount)-inner
    ring=ring_section.extrude(20)
    ring_matrix=np.array([[1,0,0,0],[0,0,1,12],[0,-1,0,-13],[0,0,0,1]],float)
    add('anilha-castanha',BROWN,ring,[region(ring_section,20)],ring_matrix)
    # Distinct material volumes must only touch; no same-space color assignments.
    collisions=[]
    for i,(a,c) in enumerate(solids):
        for j,(b,_) in enumerate(solids[i+1:],i+1):
            vol=(a^b).volume()
            if vol>.002:collisions.append([entries[i]['key'],entries[j]['key'],vol])
    assert not collisions,collisions
    all_points=np.vstack([np.asarray(s.to_mesh().vert_properties)[:,:3] for s,c in solids])
    low,high=all_points.min(0),all_points.max(0)
    assert high[1]-low[1]<=50.01
    data={'title':'Anilha Coruja BRUNA V1','model_type':'interpretação em relevo vetorial da referência; não escultura 3D',
        'max_front_height_mm':50,'base_thickness_mm':2.4,'max_front_thickness_mm':4.48,
        'nominal_min_detail_mm':.46,'nominal_min_visible_eye_glint_mm':.86,
        'scarf_lateral_clearance_mm':.2,'scarf_insertion_mm':.25,'scarf_glue_floor_gap_mm':.15,
        'ring_clear_opening_mm':[25,18],'ring_height_mm':20,'ring_min_radial_wall_mm':2.5,
        'ring_glue_pad_mm':[12.8,20],'assembled_dimensions_mm':(high-low).tolist(),
        'physical_print_tested':False,'color_collisions':collisions,'parts':entries}
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    # Optional editable Fusion reconstruction, preserving shared contours and poses.
    template=(ROOT/'fusion/M7CasaV2/M7CasaV2.py').read_text()
    template=template.replace('M7 brick V3','Coruja BRUNA V1').replace('M7 Casa V2','Coruja BRUNA V1').replace('M7CasaV2','CorujaBrunaV1')
    template=template.replace("part['name']","part.get('name',part['key'])")
    template=template.replace(' - logotipo original',' - relevo 50 mm')
    template=template.replace('M7 - criar protótipos','Coruja - criar relevo')
    template=template.replace('Casa: altura 95 mm; rebaixos do logotipo de 0,80 mm.','Coruja: altura total 50 mm; lenco e anilha para colar.')
    template=template.replace('Use o projeto 3MF Casa V2 de tres pratos para imprimir.','Use os dois projetos 3MF incluidos para imprimir.')
    (FOLDER/'CorujaBrunaV1.py').write_text(template)
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    standing=[(s.transform(stand[:3].tolist()),c) for s,c in solids]
    front_only=standing[:5]
    image=Image.new('RGB',(1600,1120),'#f4f6f8');draw=ImageDraw.Draw(image)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    image.paste(render_meshes(front_only,(820,900),direction=(0,-1,0),margin=35),(0,100))
    image.paste(render_meshes(standing,(730,800),direction=(.75,-1,.4),margin=35),(850,140))
    draw.text((40,25),'Coruja BRUNA · anilha para lenço · CAD V1',font=font(34),fill=BROWN)
    draw.text((840,990),'Frente: 50 mm · abertura: 25 × 18 mm',font=font(23),fill=BROWN)
    draw.text((40,1050),'Geometria imprimível real · 4 cores na frente + lenço verde separado · protótipo por testar',font=font(24),fill=BROWN)
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    # A dimensional assembly sheet includes the rear glue face and the small insert.
    image=Image.new('RGB',(1600,1000),'#f4f6f8');draw=ImageDraw.Draw(image)
    image.paste(render_meshes(front_only,(600,740),direction=(0,-1,0),margin=30),(0,100))
    image.paste(render_meshes([(green.transform(stand[:3].tolist()),GREEN)],(440,430),direction=(0,-1,0),margin=30),(590,170))
    image.paste(render_meshes([(ring,BROWN)],(480,550),direction=(.6,-1,.8),margin=35),(1090,140))
    draw.text((40,25),'Peças e dimensões · Coruja BRUNA',font=font(34),fill=BROWN)
    draw.text((45,855),'Coruja: altura total 50 mm',font=font(24),fill=BROWN)
    draw.text((45,895),f'Largura {high[0]-low[0]:.1f} mm · relevo até 4,48 mm',font=font(21),fill=BROWN)
    ex=pts(scarf);extent=ex.max(0)-ex.min(0)
    draw.text((610,640),f'Lenço: {extent[0]:.1f} × {extent[1]:.1f} × 1,2 mm',font=font(22),fill=GREEN)
    draw.text((610,680),'Entra 0,25 mm; folga lateral 0,20 mm',font=font(20),fill=BROWN)
    draw.text((1100,730),'Anilha: 30 × 24,5 × 20 mm',font=font(22),fill=BROWN)
    draw.text((1100,770),'Abertura útil: 25 × 18 mm',font=font(22),fill=BROWN)
    draw.text((1100,810),'Apoio plano para colar atrás',font=font(22),fill=BROWN)
    draw.text((40,955),'A frente inclui a faixa BRUNA nos 50 mm. Lenço e anilha são colados; não há peças móveis.',font=font(22),fill=BROWN)
    image.save(ROOT/'designs'/f'{PREFIX}-pecas-dimensoes.png')
    scene=trimesh.Scene()
    for entry,(solid,color) in zip(entries,solids):
        mesh=trimesh.Trimesh(np.asarray(solid.to_mesh().vert_properties)[:,:3],np.asarray(solid.to_mesh().tri_verts),process=True)
        mesh.visual.face_colors=tuple(int(color[i:i+2],16) for i in (1,3,5))+(255,)
        scene.add_geometry(mesh,node_name=entry['key'])
    scene.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    print(json.dumps({k:v for k,v in data.items() if k!='parts'},indent=2),flush=True)


if __name__=='__main__':main()
