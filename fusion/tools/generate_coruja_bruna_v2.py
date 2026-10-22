"""Sculpted, curved owl bas-relief with wrapped feather and page engraving."""
from pathlib import Path
import json
import hashlib
import math

import manifold3d as md
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

import generate_coruja_bruna_v1 as v1
from generate_joana_topper import cross_section
from generate_m7_prototypes_v1 import pts,stroke,text
from generate_universo_stand import render_meshes

ROOT=v1.ROOT
FOLDER=ROOT/'fusion/CorujaBrunaV2'
PREFIX='anilha-coruja-bruna-v2'
BROWN,CREAM,GOLD,BLACK,GREEN=v1.BROWN,v1.CREAM,v1.GOLD,v1.BLACK,v1.GREEN
path,ellipse,petal=v1.path,v1.ellipse,v1.petal


def exact(solid,target):
    for tolerance in (.001,.003,.006):
        raw=solid.simplify(tolerance).to_mesh64()
        vertices=np.asarray(raw.vert_properties)[:,:3];faces=np.asarray(raw.tri_verts)
        original=trimesh.Trimesh(vertices,faces,process=False)
        for inset,varied in ((0,False),(.0002,False),(.0002,True),(.0005,True)):
            # Tangent mesh fans can share coordinates while having distinct
            # topology. A sub-micron inward displacement separates these fans
            # before float32 STL serialization; it does not invent new detail.
            adjusted=vertices-original.vertex_normals*inset
            if varied:
                rng=np.random.default_rng(412)
                factors=rng.uniform(1,2,(len(vertices),1))
                adjusted=vertices-original.vertex_normals*inset*factors
                adjusted+=rng.uniform(-1,1,vertices.shape)*(inset*.05)
            mesh=trimesh.Trimesh(adjusted,faces,process=True)
            if not (mesh.is_watertight and mesh.is_winding_consistent):continue
            mesh.export(target)
            read=trimesh.load(target,force='mesh')
            if read.is_watertight and read.is_winding_consistent:
                print('STL validado:',target.name,'tolerância',tolerance,'inset',inset,flush=True)
                return read
    raise ValueError(f'Malha não estanque após conversão STL: {target.name}')


def union(items):
    return md.Manifold.batch_boolean(list(items),md.OpType.Add)


def dome(section,floor,rise,center=None,radii=None,angle=0):
    p=pts(section);lo,hi=p.min(0),p.max(0)
    center=(lo+hi)/2 if center is None else np.asarray(center)
    radii=(hi-lo)*.52 if radii is None else np.asarray(radii)
    bulb=md.Manifold.sphere(1,48).scale((radii[0],radii[1],rise)).rotate((0,0,angle)).translate((center[0],center[1],floor))
    clip=section.extrude(rise+.2).translate((0,0,floor))
    return (bulb^clip)+section.extrude(.18).translate((0,0,floor))


def engrave(solid,mask,depth):
    skin=solid-solid.translate((0,0,-depth))
    return solid-(skin^mask.extrude(20))


def raised(solid,mask,height):
    return (solid.translate((0,0,height))-solid)^mask.extrude(20)


def build():
    old,scarf,silhouette=v1.front()
    shapes=cross_section(old[1][3][0]['groups']).decompose()
    face=next(s for s in shapes if pts(s)[:,1].min()>25)
    banner=next(s for s in shapes if pts(s)[:,1].max()<11)
    pages=next(s for s in shapes if pts(s)[:,1].min()>10 and pts(s)[:,1].max()<20)
    face=face.offset(.4,circular_segments=32).offset(-.4,circular_segments=32)
    # A flat, strong rear plate, with actual curved volumes above it.
    body=dome(ellipse(0,21,14.5,16),3.5,3.0,center=(0,21),radii=(14.5,16))
    head=dome(ellipse(0,37,15.2,11.8),3.5,3.5,center=(0,37),radii=(15.2,11.8))
    colors={BROWN:silhouette.extrude(3.5)+(body+head)^silhouette.extrude(16),
            CREAM:md.Manifold(),GOLD:md.Manifold(),BLACK:md.Manifold()}
    # Supports below a painted feature are filled with brown, never air.
    def paint(color,solid,section,floor):
        clip=section.extrude(20-floor).translate((0,0,floor))
        for c in colors:
            if c!=color:colors[c]-=clip
        colors[color]+=solid
    print('Base volumétrica criada',flush=True)
    # Soft feathered facial discs rather than the flat cream plaque of V1.
    cheeks=dome(face,3.6,3.8,center=(-4.8,37.1),radii=(8.1,9.0))
    cheeks+=dome(face,3.6,4.0,center=(5.1,38.2),radii=(7.8,8.5))
    feather_lines=md.CrossSection()
    for cx,cy,rx,ry in [(-5,37.1,6.7,7.7),(5.1,38.6,6.4,7.2)]:
        for a in np.linspace(0,2*math.pi,27,endpoint=False):
            length=.55+.10*math.sin(a*5)
            line=[]
            for t in np.linspace(length,.98,10):
                aa=a+.12*(1-t)
                line.append((cx+rx*t*math.cos(aa),cy+ry*t*math.sin(aa)))
            feather_lines+=stroke(line,.24)
    feather_lines^=face.offset(-.22)
    cheeks=engrave(cheeks,feather_lines,.23)
    paint(CREAM,cheeks,face,3.6)
    print('Discos faciais gravados',flush=True)
    # Overlapping domed feathers, each with engraved shaft and side barbs.
    for mirror in (-1,1):
        for i,(x,y,length,width,angle) in enumerate([
            (10.3,23.9,6.5,1.9,28),(11.9,21.2,7.3,2.05,24),
            (13,18.2,7.2,2,14),(13.7,14.7,7.3,1.9,4),
            (13.6,11.6,7.2,1.9,-12),(10.8,10.2,7.5,2,-28),
            (7.6,10.1,6.9,1.9,-41),(8.9,16.2,7,1.8,-12),
            (8.8,20.6,6,1.8,8)]):
            section=petal(x,y,length,width,angle)
            lines=stroke([(0,.9),(.08,length*.45),(0,length-.9)],.24)
            for h in (2,3.2,4.4):
                if h<length-.8:
                    lines+=stroke([(-width*.48,h+.9),(0,h)],.22)
                    lines+=stroke([(width*.48,h+.9),(0,h)],.22)
            lines=lines.rotate(angle).translate((x,y))
            if mirror<0:section=section.mirror((1,0));lines=lines.mirror((1,0))
            section=(section^silhouette)-face.offset(.15)-banner.offset(.3)
            if section.is_empty():continue
            floor=3.2+.1*(i%3)
            feather=dome(section,floor,2.4+.2*(i%2))
            feather=engrave(feather,lines,.23)
            paint(GOLD,feather,section,floor)
    print('Penas curvas criadas',flush=True)
    crest=[path('M -15.3 43.4 Q -10.5 42.4 -5.1 44.3 Q -9.4 43.9 -14.4 44.6 Z'),
           path('M 1.4 44.1 Q 2.8 46.5 9.9 49.1 Q 8.8 46.3 3 43 Z')]
    for sec in crest:
        sec-=face
        paint(GOLD,dome(sec,3.2,2.0),sec,3.2)
    # A real raised open book, convex pages, and a depressed centre fold.
    cover=pages.offset(.65,circular_segments=24)
    paint(BROWN,dome(cover,4.7,1.8),cover,4.7)
    book=dome(pages,5.0,2.0,center=(-5.3,16),radii=(6.0,3.0))
    book+=dome(pages,5.0,2.0,center=(5.3,16),radii=(6.0,3.0))
    book_lines=stroke([(0,12),(0,15.2)],.32)
    for s in (-1,1):
        for dy in (0,.75,1.5):
            book_lines+=stroke([(s*.8,13.5+dy),(s*3.3,15+dy),(s*6,16.1+dy),(s*8.8,16.7+dy)],.23)
    book=engrave(book,book_lines^pages.offset(-.12),.27)
    paint(CREAM,book,pages,5.0)
    flame=path('M .1 17.4 C -4 20 -2.1 21.8 -.5 23.4 Q -.2 22.1 .1 21.6 Q 1.7 24 1.8 25 C 5 21.5 2.9 19 .1 17.4 Z')
    flame_s=dome(flame,5.0,2.2)
    flame_s=engrave(flame_s,stroke([(-.3,18.6),(.7,20.2),(.5,22)],.3),.4)
    paint(GOLD,flame_s,flame,5.0)
    # Rounded ribbon. The inscription follows its curved surface.
    ribbon=dome(banner,2.8,1.65,center=(0,5.7),radii=(19,6.5))
    paint(CREAM,ribbon,banner,2.8)
    name=text('BRUNA',25,font=v1.SERIF)
    p=pts(name);name=name.scale((1,3.8/(p[:,1].max()-p[:,1].min()))).translate((0,3.4))
    colors[BROWN]+=raised(ribbon,name,.55)
    # Eye rims, irises and pupils are raised curved caps on the face.
    for x,y in [(-5,37.1),(5.1,38.6)]:
        rim=ellipse(x,y,2.9,3.1)
        iris=ellipse(x+.08,y-.08,2.4,2.65)
        pupil=ellipse(x+.18,y+.05,1.42,1.9)
        eye_black=raised(cheeks,rim,.45)
        eye_gold=raised(cheeks,iris,.82)
        eye_pupil=raised(cheeks,pupil,1.3)
        eye_black-=iris.extrude(20)
        eye_gold-=pupil.extrude(20)
        colors[BLACK]+=eye_black+eye_pupil
        colors[GOLD]+=eye_gold
        glint=ellipse(x-.27,y+.85,.38,.38)
        colors[CREAM]+=raised(eye_pupil,glint,.32)
    beak=path('M -.1 36.4 Q 1.4 37 2.7 35.9 L 1.8 32.5 Q .8 33.1 -.1 36.4 Z')
    beak_s=raised(cheeks,beak,1.3)
    colors[GOLD]+=beak_s
    # Brown eyebrows are organically rounded and follow the face curvature.
    brows=stroke([(-8.1,39.1),(-6.9,40),(-5.7,40.3),(-4.1,40),(-2.5,40.6)],.85)
    brows+=stroke([(2.2,40.7),(3.9,41.7),(5.8,42),(7.1,43.1)],.9)
    brows^=face
    brow_s=raised(cheeks,brows,.85)
    for c in colors:colors[c]-=brow_s
    colors[BROWN]+=brow_s
    # Fine same-material grain in the crown and exposed breast.
    grain=md.CrossSection()
    for x,y in [(-4,21),(-6,23),(-3,25),(0,26),(-3.5,44),(0,44.5),(2,46),
                (-2,22),(-5,19),(4,22),(5,25),(-6,45),(1,29),(-8,28)]:
        grain+=stroke([(x-.8,y-.8),(x,y+.3),(x+1.1,y+.8)],.25)
    grain-=face.offset(.3)+banner.offset(.3)+pages.offset(.8)+flame.offset(.3)
    grain-=crest[0].offset(.3)+crest[1].offset(.3)
    colors[BROWN]=engrave(colors[BROWN],grain,.24)
    # Flat-backed separate scarf; the visible face and knot are now rounded too.
    pocket=scarf.offset(.2,circular_segments=24)
    cutter=pocket.extrude(16).translate((0,0,4.4))
    for c in colors:colors[c]-=cutter
    green=scarf.extrude(.65)+dome(scarf,.65,.8,center=(0,26),radii=(11,5))
    knot=ellipse(2.9,24.3,1.5,1.2)^scarf
    green+=dome(knot,.65,1.35)
    green=engrave(green,stroke([(3.7,20.4),(4,22),(3.5,23.4)],.28),.2)
    for c,solid in colors.items():
        assert solid.status()==md.Error.NoError
    return colors,green,scarf,silhouette


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    colors,green,scarf,sil=build()
    entries=[];assembled=[]
    def add(key,color,solid,pose=None):
        name=f'{PREFIX}-{key}.stl';target=ROOT/'downloads'/name
        mesh=exact(solid,target)
        if pose is None:pose=np.eye(4)
        entries.append({'key':key,'file':name,'color':color,'assembly':pose.tolist(),
            'dimensions_mm':mesh.extents.tolist(),'volume_mm3':mesh.volume,
            'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'watertight':True})
        assembled.append((solid.transform(pose[:3].tolist()),color))
    for key,color in [('castanho',BROWN),('creme',CREAM),('dourado',GOLD),('preto',BLACK)]:
        add(key,color,colors[color])
    tm=np.eye(4);tm[2,3]=4.6
    add('lenco-verde',GREEN,green,tm)
    ring_sec=(ellipse(0,0,15,11.5)+v1.rounded(-7,-13,14,4,.6))-ellipse(0,0,12.5,9)
    ring=ring_sec.extrude(20)
    ring_tm=np.array([[1,0,0,0],[0,0,1,12],[0,-1,0,-13],[0,0,0,1]],float)
    add('anilha-castanha',BROWN,ring,ring_tm)
    collisions=[]
    for i,(a,c) in enumerate(assembled):
        for j,(b,_) in enumerate(assembled[i+1:],i+1):
            vol=(a^b).volume()
            if vol>.003:collisions.append([entries[i]['key'],entries[j]['key'],vol])
    assert not collisions,collisions
    whole=union(colors.values())
    components=whole.decompose()
    positive=[s for s in components if s.volume()>1e-5]
    assert len(positive)==1,'Floating feature in owl'
    # The standalone monochrome copy fills tiny enclosed Boolean cavities;
    # these are not floating decorative features or visible surface detail.
    whole=positive[0]
    full=exact(whole,ROOT/'downloads'/f'{PREFIX}-CORUJA-COMPLETA-monocor.stl')
    assert full.extents[1]<=50.01
    data={'title':'Coruja BRUNA V2 - relevo curvo para bico 0.2',
        'model_type':'bas-relief with smooth domes and engraved feather shafts',
        'front_dimensions_mm':full.extents.tolist(),'front_height_limit_mm':50,
        'base_thickness_mm':3.5,'scarf_glue_gap_mm':.2,'scarf_lateral_clearance_mm':.2,
        'ring_clear_opening_mm':[25,18],'ring_height_mm':20,
        'ring_glue_pad_mm':[12.8,20],'minimum_engraving_width_mm':.22,
        'body_connected':True,'assembled_color_intersections':collisions,
        'physical_print_tested':False,'parts':entries}
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    # Rotate to upright only for the drawings; the STL keeps a flat rear on Z=0.
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    upright=[(s.transform(stand[:3].tolist()),c) for s,c in assembled]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet=Image.new('RGB',(1700,1150),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:5],(830,950),direction=(.1,-1,.12),margin=30),(0,100))
    sheet.paste(render_meshes(upright,(820,900),direction=(.8,-1,.3),margin=30),(850,120))
    draw.text((40,25),'Coruja BRUNA V2 · relevo curvo · bico 0,2 mm',font=font(34),fill=BROWN)
    draw.text((40,1085),f'Altura 50 mm · espessura da frente até {full.extents[2]:.1f} mm · geometria real',font=font(26),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    detail=render_meshes(upright[:4],(1300,1500),direction=(.35,-1,.25),margin=55)
    detail.save(ROOT/'designs'/f'{PREFIX}-detalhe.png')
    sheet=Image.new('RGB',(1600,1000),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:5],(600,730),direction=(0,-1,0),margin=30),(0,110))
    sheet.paste(render_meshes([(green.transform(stand[:3].tolist()),GREEN)],(440,430),direction=(.2,-1,.3),margin=30),(600,170))
    sheet.paste(render_meshes([(ring,BROWN)],(470,530),direction=(.6,-1,.8),margin=30),(1110,150))
    draw.text((40,25),'Peças V2 · anilha com coruja esculpida',font=font(34),fill=BROWN)
    draw.text((40,870),f'Coruja: 50 × {full.extents[0]:.1f} mm',font=font(24),fill=BROWN)
    draw.text((40,910),f'Relevo total até {full.extents[2]:.1f} mm',font=font(23),fill=BROWN)
    draw.text((620,650),'Lenço verde arredondado',font=font(22),fill=GREEN)
    draw.text((620,690),'Uma peça para colar; verso plano',font=font(20),fill=BROWN)
    draw.text((1120,750),'Abertura: 25 × 18 mm',font=font(23),fill=BROWN)
    draw.text((1120,790),'Altura: 20 mm · bico 0,4 mm',font=font(21),fill=BROWN)
    draw.text((40,960),'A faixa BRUNA está incluída nos 50 mm. Frente: quatro cores. Lenço verde separado.',font=font(23),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-pecas-dimensoes.png')
    scene=trimesh.Scene()
    for e,(solid,col) in zip(entries,assembled):
        m=exact(solid,ROOT/'downloads'/f'{PREFIX}-temp.stl')
        m.visual.face_colors=tuple(int(col[i:i+2],16) for i in (1,3,5))+(255,)
        scene.add_geometry(m,node_name=e['key'])
    scene.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    (ROOT/'downloads'/f'{PREFIX}-temp.stl').unlink()
    print(json.dumps({k:v for k,v in data.items() if k!='parts'},indent=2),flush=True)


if __name__=='__main__':main()
