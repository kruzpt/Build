"""M7 approved gift prototypes. Millimetres; actual printable geometry.

Run with the project's geometry Python (numpy, Pillow, cv2, trimesh, manifold3d).
The original brick is only read. All decoration is new, separate and glueable.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from generate_joana_topper import groups, section_groups, save_mesh
from generate_universo_stand import render_meshes, mesh_of

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/M7PrototiposV1'
WHITE, BLUE, CYAN, ORANGE, GOLD = '#FFFDF7', '#17385B', '#009FCA', '#C85D2E', '#DDB34E'
SCRIPT = '/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ANGLE = math.radians(70)
C, S = math.cos(ANGLE), math.sin(ANGLE)
PARTS = []


def union(items):
    return md.Manifold.batch_boolean(list(items), md.OpType.Add)


def rect(x, y, w, h):
    return md.CrossSection.square((w, h)).translate((x, y))


def rounded(x, y, w, h, r):
    return rect(x+r, y+r, w-2*r, h-2*r).offset(r, circular_segments=32)


def pts(section):
    return np.vstack(section.to_polygons())


def normalize(section, width=None, height=None):
    p = pts(section); low, high = p.min(0), p.max(0)
    section = section.translate(-low)
    factors = np.ones(2)
    if width is not None: factors[0] = width/(high[0]-low[0])
    if height is not None: factors[1] = height/(high[1]-low[1])
    if width is not None and height is None: factors[1] = factors[0]
    if height is not None and width is None: factors[0] = factors[1]
    section = section.scale(factors)
    p = pts(section)
    return section.translate((-(p[:,0].min()+p[:,0].max())/2, -p[:,1].min()))


def text(text, width, font=BOLD, strengthen=0):
    f = ImageFont.truetype(font, 420)
    b = f.getbbox(text)
    image = Image.new('L', (b[2]-b[0]+32, b[3]-b[1]+32))
    ImageDraw.Draw(image).text((16-b[0],16-b[1]), text, font=f, fill=255)
    section = md.CrossSection([loop for g in groups(np.asarray(image), 1, 0, image.height,
                           min_area=5) for loop in g], md.FillRule.EvenOdd)
    section = normalize(section, width=width)
    if strengthen: section = section.offset(strengthen, circular_segments=20)
    return normalize(section, width=width).simplify(.008)


def stroke(points, width):
    pieces = [md.CrossSection.circle(width/2, 40).translate(p) for p in points]
    for a, b in zip(points[:-1], points[1:]):
        a, b = np.array(a), np.array(b)
        d = b-a; n = np.array((-d[1],d[0]))/np.linalg.norm(d)*width/2
        pieces.append(md.CrossSection([[a+n,b+n,b-n,a-n]],md.FillRule.EvenOdd))
    return md.CrossSection.batch_boolean(pieces, md.OpType.Add)


def logo(width):
    # Rounded lowercase m and stylized cyan 7, interpreted from supplied image.
    arches = []
    for cx in (-2.7, 2.7):
        a = np.linspace(math.pi, 0, 60)
        arches.append(stroke(np.column_stack((cx+2.7*np.cos(a),5.4+2.7*np.sin(a))),1.8))
    m = arches[0]+arches[1]
    for x in (-5.4,0,5.4): m += rounded(x-.9,0,1.8,5.6,.45)
    seven = md.CrossSection([[(7.4,8.9),(14.7,8.9),(14.25,7.5),
                             (11.65,0),(9.25,0),(11.9,6.9),(7.15,6.9)]],md.FillRule.EvenOdd)
    allp=pts(m+seven); lo,hi=allp.min(0),allp.max(0)
    fac=width/(hi[0]-lo[0]); origin=np.array(((lo[0]+hi[0])/2,lo[1]))
    return [(part.translate(-origin).scale((fac,fac))) for part in (m,seven)]


def identity(): return np.eye(4)


def pose_house():
    return np.array([[1,0,0,0],[0,C,-S,35],[0,S,C,2],[0,0,0,1]],float)


def pose_front(y=0):
    # Local XY is width/height; +Z projects forwards towards the viewer.
    return np.array([[1,0,0,0],[0,0,-1,y],[0,1,0,0],[0,0,0,1]],float)


def transformed(solid, matrix): return solid.transform(matrix[:3].tolist())


def region(section, height, z=0, operation='new', matrix=None):
    return {'groups':section_groups(section), 'height':height, 'z':z,
            'operation':operation, 'transform':(identity() if matrix is None else matrix).tolist()}


def add(key, name, solid, color, assembly=None, regions=None, product=None):
    path=ROOT/'downloads'/f'm7-{product}-v1-{key}.stl'
    mesh=save_mesh(solid.simplify(.005),path)
    entry={'key':key,'name':name,'file':path.name,'color':color,'product':product,
           'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(solid.volume()),
           'watertight':bool(mesh.is_watertight),'assembly':(identity() if assembly is None else assembly).tolist(),
           'regions':regions or []}
    PARTS.append(entry)
    return entry, solid


def house():
    matrix=pose_house()
    # H is solved for 95 mm assembled vertical height, including 4 mm facade.
    h=(95-2-4*C)/S
    outline=md.CrossSection([[(-34,0),(34,0),(34,63),(37.5,63),
                             (37.5,65),(0,h),(-37.5,65),(-37.5,63),(-34,63)]])
    outline=outline.offset(-.7, circular_segments=32).offset(.7, circular_segments=32)
    outline=normalize(outline,width=75,height=h)
    windows=md.CrossSection()
    for x in (-11.5,1):
        for y in (47,59.5): windows += rounded(x,y,10.5,10.5,.7)
    front=outline-windows
    white=front.extrude(4)
    script1=text('O que fazemos',57,font=SCRIPT,strengthen=.16).translate((0,30))
    script2=text('mostra quem somos',60,font=SCRIPT,strengthen=.16).translate((0,16))
    wording=script1+script2
    assert (wording-front).area()<.001
    blue_relief=wording.extrude(.6).translate((0,0,4))
    background=outline.offset(-.8, circular_segments=24)
    backing=background.extrude(2)
    backing_pose=matrix.copy();backing_pose[:3,3]+=matrix[:3,2]*-2

    floor=rounded(-42.5,0,85,85,3)
    floor_s=floor.extrude(6)
    lip=rounded(-40.5,0,81,10,2)
    base=union([floor_s,lip.extrude(9.6).translate((0,0,6))])
    base_regions=[region(floor,6),region(lip,9.6,6,'join')]
    # Cross-section in world YZ, extruded across X; both faces slope inward up.
    rear_w=-2.15
    top_v=58
    top_y=35+C*top_v-S*rear_w; top_z=2+S*top_v+C*rear_w
    low_v=(6-2-C*rear_w)/S; low_y=35+C*low_v-S*rear_w
    side=md.CrossSection([[(low_y,6),(80,6),(top_y,top_z)]])
    for x in (-30.5,26.5):
        tm=np.array([[0,0,1,x],[1,0,0,0],[0,1,0,0],[0,0,0,1]],float)
        base=union([base,transformed(side.extrude(4),tm)])
        base_regions.append(region(side,4,operation='join',matrix=tm))
    # Inclined 6.30 mm blind slot; nominal total clearance 0.30 mm.
    # World YZ cutter retains a 2 mm blind floor; shared with Fusion.
    zlo,zhi=2,26
    def y_for(z,w):return 35+(z-2-C*w)*C/S-S*w
    cross=md.CrossSection([[(y_for(zlo,4.15),zlo),(y_for(zhi,4.15),zhi),
                           (y_for(zhi,-2.15),zhi),(y_for(zlo,-2.15),zlo)]],md.FillRule.EvenOdd)
    cutter_pose=np.array([[0,0,1,-34.25],[1,0,0,0],[0,1,0,0],[0,0,0,1]],float)
    slot_exact=transformed(cross.extrude(68.5),cutter_pose)
    base-=slot_exact
    if base.status()!=md.Error.NoError:
        raise RuntimeError(('base slot',base.status(),side.area(),cross.area(),slot_exact.status()))
    base_regions.append(region(cross,68.5,operation='cut',matrix=cutter_pose))

    lm,l7=logo(20)
    # Front lip has a broad, upright face. Recesses are 0.20 mm deep.
    lm=lm.translate((0,6.5));l7=l7.translate((0,6.5))
    fp=pose_front()
    for cs in (lm,l7):
        pocket=cs.offset(.15,circular_segments=20)
        base-=transformed(pocket.extrude(.25).translate((0,0,-.2)),fp)
        if base.status()!=md.Error.NoError:raise RuntimeError(('base logo pocket',base.status(),pocket.area()))
        base_regions.append(region(pocket,.25,-.2,'cut',fp))
    assembled=[]
    entries=[]
    e,s=add('fachada-branca','Fachada branca',white,WHITE,matrix,
            [region(front,4)],'casa');entries.append(e);assembled.append((transformed(s,matrix),WHITE))
    e,s=add('frase-azul','Frase manuscrita azul',blue_relief,BLUE,matrix,
            [region(wording,.6,4)],'casa');entries.append(e);assembled.append((transformed(s,matrix),BLUE))
    e,s=add('fundo-azul','Fundo azul da janela',backing,BLUE,backing_pose,
            [region(background,2)],'casa');entries.append(e);assembled.append((transformed(s,backing_pose),BLUE))
    e,s=add('base-azul','Base azul e dois apoios',base,BLUE,regions=base_regions,product='casa')
    entries.append(e);assembled.append((s,BLUE))
    logo_pose=fp.copy();logo_pose[:3,3]+=fp[:3,2]*-.15
    for key,cs,col in [('m-branco',lm,WHITE),('7-ciano',l7,CYAN)]:
        e,s=add(key,key,cs.extrude(1.2),col,logo_pose,[region(cs,1.2)],'casa')
        entries.append(e);assembled.append((transformed(s,logo_pose),col))

    core_assembled=[assembled[i][0] for i in (0,2)]
    collisions=[]
    for moving in core_assembled:
        for dv in np.linspace(0,105,43):
            delta=matrix[:3,1]*float(dv)
            collision=(moving.translate(delta)^base).volume()
            assert collision<.001,('house insertion',dv,collision)
            collisions.append(collision)
    assert (assembled[0][0]^assembled[2][0]).volume()<.001
    assert len(base.decompose())==1
    assert abs(mesh_of(assembled[0][0]).bounds[1,2]-95)<.01
    assert len(background.to_polygons())==1
    floor_hull=np.array([[-39.5,3],[39.5,3],[39.5,82],[-39.5,82]],np.float32)
    # Static projected CG check with illustrative phone masses, not strength/adhesion.
    static=[]
    core=union([v for v,c in assembled]);cm=mesh_of(core).center_mass
    for length,width,thick,grams in [(145,65,8,180),(165,80,14,250),(180,90,17,320)]:
        w=4.8;v=(6-2-C*w)/S
        phone=md.Manifold.cube((width,length,thick)).translate((-width/2,v,w))
        phone=transformed(phone,matrix)
        assert (phone^core).volume()<.001
        pc=mesh_of(phone).center_mass
        mass=core.volume()*.00124*.55
        cg=(pc*grams+cm*mass)/(grams+mass)
        margin=float(cv2.pointPolygonTest(floor_hull,tuple(map(float,cg[:2])),True))
        assert margin>10
        static.append({'phone_mm':[length,width,thick],'phone_g':grams,'static_margin_mm':margin})
    return assembled,{'facade_width_mm':75,'facade_length_mm':h,'facade_thickness_mm':4,
        'assembled_height_mm':95,'base_width_depth_mm':[85,85],'backing_thickness_mm':2,
        'slot_normal_width_mm':6.3,'slot_clearance_total_mm':.3,'angle_to_table_deg':70,
        'insertion_positions_checked':len(collisions),'max_insertion_collision_mm3':max(collisions),
        'static_load_cases':static,'window_panes':4,'text':'O que fazemos / mostra quem somos',
        'script_font':'Z003 Medium Italic (URW Base35)','physical_fit_tested':False,
        'cable_charging_tested':False,'structural_FEA_performed':False}


def star_section():
    vertices=[]
    for i in range(10):
        a=math.pi/2+i*math.pi/5;r=11 if i%2==0 else 5.3
        vertices.append((r*math.cos(a),r*math.sin(a)))
    star=md.CrossSection([vertices])
    return normalize(star-star.offset(-1.2,circular_segments=16),width=24)


def brick(source):
    original=trimesh.load(source,force='mesh')
    original.apply_transform(np.array([[0,1,0,-25],[-1,0,0,0],[0,0,1,0],[0,0,0,1]],float))
    imported=md.Manifold(md.Mesh(original.vertices.astype(np.float32),original.faces.astype(np.uint32)))
    assert imported.status()==md.Error.NoError
    profile=imported.slice(35).simplify(.002)
    body=profile.extrude(70)
    difference=(body-imported).volume()+(imported-body).volume()
    assert difference<.25, difference
    fp=pose_front()
    star=star_section().translate((0,44))
    # One continuous rounded zigzag, including the pointed top (no loose tip).
    zigzag=[(-14.2,10.6),(13.8,17.3),(-11.5,18.1),(11,24.2),(-8.3,25),
            (7.7,30.2),(-5.2,31.1),(4.3,36),(-2.4,37),(0,40)]
    tree=stroke(zigzag,2.2)
    inscription=text('Natal 2026',34,strengthen=.04).translate((0,3.0))
    lm,l7=logo(10.0)
    lm=lm.translate((.7,52.9));l7=l7.translate((.7,52.9))
    assert ((lm+l7).offset(.25,circular_segments=16)^star).area()<.001,'Logo must clear star border'
    pieces=[('estrela-dourada',star,GOLD),('arvore-dourada',tree,GOLD),
            ('natal-branco',inscription,WHITE),('m-branco',lm,WHITE),('7-ciano',l7,CYAN)]
    regions=[region(profile,70)]
    # Letter pockets as well as ornament pockets: no whole-face carrier plate.
    for key,cs,col in pieces:
        pocket=cs.offset(.15,circular_segments=20)
        assert (pts(pocket)[:,0].min()>-23 and pts(pocket)[:,0].max()<23)
        cutter=transformed(pocket.extrude(.25).translate((0,0,-.2)),fp)
        body-=cutter
        regions.append(region(pocket,.25,-.2,'cut',fp))
    assert len(body.decompose())==1
    assembled=[]
    e,s=add('tijolo-terracota','Tijolo original com rebaixos',body,ORANGE,
            regions=regions,product='tijolo');assembled.append((s,ORANGE))
    ornament_pose=fp.copy();ornament_pose[:3,3]+=fp[:3,2]*-.15
    for key,cs,col in pieces:
        e,s=add(key,key,cs.extrude(1.2),col,ornament_pose,[region(cs,1.2)],'tijolo')
        part=transformed(s,ornament_pose)
        assert (body^part).volume()<.001,(key,(body^part).volume())
        assembled.append((part,col))
    assert len(star.to_polygons())==2
    assert len(tree.to_polygons())==1
    return assembled,{'original_file':'Tijolos.stl','original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'body_width_depth_height_mm':[50,26,70],'original_volume_mm3':float(imported.volume()),
        'profile_reconstruction_symmetric_difference_mm3':difference,'through_holes':8,
        'pocket_depth_mm':.2,'pocket_lateral_clearance_per_side_mm':.15,
        'ornament_thickness_mm':1.2,'nominal_glue_gap_mm':.05,
        'star_width_mm':24,'tree_stroke_mm':2.2,'star_border_approx_mm':1.35,
        'inscription_width_mm':34,'physical_glue_fit_tested':False}


def illustrations(ha,ba):
    font=lambda s:ImageFont.truetype(REGULAR,s)
    out=Image.new('RGB',(1700,1120),'#f4f6f8');d=ImageDraw.Draw(out)
    out.paste(render_meshes(ha,(950,930),direction=(.50,-.8,.52)),(0,130))
    out.paste(render_meshes(ba,(650,850),direction=(.48,-.8,.58)),(990,190))
    d.text((45,25),'M7 — primeiro protótipo de cada oferta',font=font(36),fill=BLUE)
    d.text((45,78),'Geometria real dos ficheiros de impressão · A1 / bico 0,4 mm',font=font(24),fill=BLUE)
    d.text((70,1020),'Casa: 95 mm de altura · base 85 × 85 mm · 70°',font=font(22),fill=BLUE)
    d.text((1000,1020),'Tijolo: 50 × 26 × 70 mm',font=font(22),fill=BLUE)
    d.text((45,1070),'Peças para colar por cor; encaixe real, estabilidade ao toque e colagem a testar no protótipo.',font=font(21),fill=BLUE)
    out.save(ROOT/'designs/m7-prototipos-v1-CAD.png')
    detail=Image.new('RGB',(1500,1050),'#f4f6f8');d=ImageDraw.Draw(detail)
    detail.paste(render_meshes(ha,(720,850),direction=(.04,-1,.05)),(10,120))
    detail.paste(render_meshes(ba,(720,850),direction=(.04,-1,.05)),(770,120))
    d.text((40,25),'M7 — detalhes reais: manuscrito e peças para colar',font=font(31),fill=BLUE)
    d.text((40,985),'A decoração dourada é impressa deitada; o tijolo imprime com os furos na vertical.',font=font(23),fill=BLUE)
    detail.save(ROOT/'designs/m7-prototipos-v1-detalhes.png')
    rear=Image.new('RGB',(1500,1000),'#f4f6f8');d=ImageDraw.Draw(rear)
    rear.paste(render_meshes(ha,(750,850),direction=(.55,.8,.5)),(0,95))
    rear.paste(render_meshes(ha,(650,850),direction=(1,.02,.05)),(820,95))
    d.text((40,25),'Casinha — traseira e perfil reais',font=font(34),fill=BLUE)
    d.text((40,950),'Fachada 4 mm + fundo 2 mm · ranhura 6,30 mm · dois apoios integrados na base',font=font(24),fill=BLUE)
    rear.save(ROOT/'designs/m7-casa-v1-CAD-tras-lado.png')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--brick-source',type=Path,default=Path('/workspace/attachments/185461ba-a2a6-4bec-a37f-f59c35c56997/Tijolos.stl'))
    args=parser.parse_args();FOLDER.mkdir(exist_ok=True)
    ha,hreport=house();ba,breport=brick(args.brick_source)
    data={'units':'mm','version':1,'parts':PARTS,'house':hreport,'brick':breport}
    (FOLDER/'geometry.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps({'house':hreport,'brick':breport,
        'parts':[{k:v for k,v in p.items() if k not in ('regions','assembly')} for p in PARTS],
        'fusion_runtime_tested':False,'physical_prototypes_printed':False},ensure_ascii=False,indent=2)+'\n')
    illustrations(ha,ba)
    print(json.dumps({'house':hreport,'brick':breport,'part_count':len(PARTS)},ensure_ascii=False,indent=2))


if __name__=='__main__': main()
