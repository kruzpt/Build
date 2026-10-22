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
FOLDER=ROOT/'fusion/CorujaBrunaV3'
PREFIX='anilha-coruja-bruna-v3'
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
    # Coordinates transcribed from the supplied reference screenshot. Every
    # feature shares this frame; no independent enlargement of the owl head.
    raw_outline=path('M 157 623 C 190 623 231 621 278 606 C 333 546 410 533 479 533 C 510 499 528 491 548 466 C 578 490 590 526 594 581 C 644 610 667 662 661 715 C 660 766 642 802 617 833 C 690 878 734 954 747 1048 C 764 1118 748 1174 733 1212 L 757 1168 C 784 1170 777 1210 771 1245 C 776 1284 753 1313 727 1339 C 646 1408 532 1426 414 1413 C 300 1402 198 1371 160 1317 C 144 1283 131 1243 139 1199 L 140 1150 C 161 1131 183 1143 201 1151 C 156 1110 145 1053 161 995 C 183 927 215 870 255 844 C 230 808 211 772 211 720 C 169 709 153 669 157 623 Z')
    pp=pts(raw_outline);y0,y1=pp[:,1].min(),pp[:,1].max();scale=50/(y1-y0)
    def convert(section):return section.scale((scale,-scale)).translate((-450*scale,y1*scale))
    def sec(s):return convert(path(s))
    def point(x,y):return np.array(((x-450)*scale,(y1-y)*scale))
    def ell(x,y,rx,ry):return ellipse(*point(x,y),rx*scale,ry*scale)
    def line(points,width=.23):return stroke([point(x,y) for x,y in points],width)
    silhouette=convert(raw_outline)
    face=sec('M 443 700 C 417 665 380 660 347 670 C 302 676 279 709 269 752 C 258 796 285 829 320 846 C 349 864 376 863 396 865 C 417 860 434 850 450 841 C 460 817 489 820 523 805 C 578 785 604 748 602 699 C 601 654 576 611 541 598 C 494 600 466 648 443 700 Z')
    edge=pts(face);notches=md.CrossSection()
    for x,y in [(277,739),(267,767),(279,795),(296,819),(319,840),(345,852),
                (372,860),(396,865),(419,855),(447,842),(481,816),(514,805),
                (549,788),(576,765),(594,738),(602,709),(599,681),(589,653),(572,627)]:
        target=point(x,y);q=edge[np.argmin(np.linalg.norm(edge-target,axis=1))]
        center=point(374,750) if x<450 else point(514,691)
        inward=center-q;inward/=np.linalg.norm(inward)
        side=np.array((-inward[1],inward[0]))
        notches+=md.CrossSection([[q-inward*.12+side*.18,q-inward*.12-side*.18,q+inward*.30]],md.FillRule.EvenOdd)
    face-=notches
    banner=sec('M 245 1217 C 348 1255 494 1291 620 1247 L 681 1315 C 528 1394 322 1372 199 1290 Z')
    pages=sec('M 311 1029 Q 363 1038 441 1105 Q 503 1047 579 1029 L 605 1084 Q 504 1106 443 1162 Q 364 1111 281 1082 Z')
    cover=sec('M 287 1061 Q 370 1071 441 1144 Q 519 1077 602 1067 L 586 1149 Q 510 1174 450 1232 Q 367 1195 312 1159 Z')
    scarf=sec('M 319 848 Q 371 863 462 911 Q 523 866 605 811 L 625 841 Q 572 875 488 937 Q 526 978 501 1046 L 465 1029 L 446 1047 L 435 953 Q 392 926 308 877 Z')
    scarf=scarf.offset(-.10).offset(.10,circular_segments=24)
    # Same solid rear, but a narrower tilted head and a substantially wider body.
    body=dome(ell(449,1030,285,250),3.5,4.0,center=point(449,1030),radii=(285*scale,250*scale))
    head=dome(ell(460,700,210,185),3.5,4.5,center=point(460,700),radii=(210*scale,185*scale))
    colors={BROWN:(silhouette.extrude(3.5)+body+head)^silhouette.extrude(18),
            CREAM:md.Manifold(),GOLD:md.Manifold(),BLACK:md.Manifold()}
    colors[BROWN]+=face.extrude(.10).translate((0,0,3.5))
    def paint(color,solid,section,floor):
        clip=section.extrude(20-floor).translate((0,0,floor))
        for c in colors:
            if c!=color:colors[c]-=clip
        colors[color]+=solid
    print('V3: silhueta e proporções da referência',flush=True)
    cheeks=dome(face,3.6,4.3,center=point(374,750),radii=(116*scale,133*scale))
    cheeks+=dome(face,3.6,4.5,center=point(514,691),radii=(97*scale,114*scale))
    # Fine curved feather texture follows the two differently placed facial discs.
    face_lines=md.CrossSection()
    for cx,cy,rx,ry in [(374,750,102,115),(514,691,87,104)]:
        for angle in np.linspace(0,2*math.pi,31,endpoint=False):
            points=[]
            for t in np.linspace(.51,.98,10):
                a=angle+.10*(1-t)
                points.append(point(cx+rx*t*math.cos(a),cy+ry*t*math.sin(a)))
            face_lines+=stroke(points,.22)
    cheeks=engrave(cheeks,face_lines^face.offset(-.18),.24)
    paint(CREAM,cheeks,face,3.6)
    wing_lines=md.CrossSection();wing_area=md.CrossSection()
    # Long swept leaves envelop the book; left and right are not mirrored copies.
    leaves=[(181,1014,272,861,31),(165,1062,250,932,34),(179,1121,232,994,34),
        (208,1166,236,1052,33),(259,1207,258,1093,33),(327,1233,278,1144,29),
        (244,994,292,863,32),(256,1067,279,943,34),(284,1142,269,1019,32),(334,1204,295,1106,30),
        (700,1011,607,862,34),(729,1080,649,937,36),(711,1147,657,1012,36),
        (671,1199,665,1082,34),(607,1241,643,1143,33),(529,1266,595,1194,30),
        (636,1005,575,874,34),(624,1074,600,956,35),(596,1146,621,1039,34),(526,1219,597,1122,32)]
    for i,(tx,ty,rx,ry,w) in enumerate(leaves):
        tip,root=point(tx,ty),point(rx,ry);vec=root-tip;length=np.linalg.norm(vec)
        angle=-math.degrees(math.atan2(vec[0],vec[1]))
        section=petal(*tip,length,w*scale,angle)
        section=(section^silhouette)-face.offset(.1)-banner.offset(.15)
        if section.is_empty():continue
        grooves=stroke([(0,.6),(.06,length*.45),(0,length-.6)],.23)
        for h in (length*.28,length*.48,length*.68):
            grooves+=stroke([(-w*scale*.42,h+.65),(0,h)],.21)
            grooves+=stroke([(w*scale*.42,h+.65),(0,h)],.21)
        grooves=grooves.rotate(angle).translate(tip)
        if i%2==0:
            dark=stroke([(0,.75),(.05,length*.45),(0,length-.75)],.20)
        else:
            dark=stroke([(0,.5),(w*scale*.42,length*.25),(w*scale*.5,length*.54),(0,length-.5)],.20)
        wing_lines+=dark.rotate(angle).translate(tip)
        wing_area+=section
        feather=dome(section,3.2,3.0+.2*(i%3))
        feather=engrave(feather,grooves,.18)
        paint(GOLD,feather,section,3.2)
    print('V3: penas longas sobrepostas',flush=True)
    crests=[sec('M 175 633 C 231 655 310 610 365 636 C 295 635 225 681 188 660 Z'),
            sec('M 425 664 C 435 583 515 542 549 483 C 562 537 500 579 463 622 C 505 596 550 564 567 524 C 581 593 511 606 425 664 Z')]
    for crest in crests:
        crest-=face.offset(.08)
        paint(GOLD,dome(crest,3.2,3.9),crest,3.2)
    # Cover and fan-shaped pages, with the lower spine visible below them.
    paint(BROWN,dome(cover,4.1,2.3),cover,4.1)
    book=dome(pages,5.0,2.3,center=point(353,1076),radii=(95*scale,55*scale))
    book+=dome(pages,5.0,2.3,center=point(535,1074),radii=(95*scale,55*scale))
    page_lines=line([(442,1110),(443,1158)],.30)
    for d in (0,13,26):
        page_lines+=line([(298,1070-d),(344,1080-d),(397,1108-d),(435,1140-d)],.22)
        page_lines+=line([(451,1136-d),(494,1106-d),(548,1076-d),(591,1063-d)],.22)
    book=engrave(book,page_lines^pages.offset(-.1),.28)
    paint(CREAM,book,pages,5.0)
    flame=sec('M 441 1095 C 419 1060 390 1026 408 985 C 422 1004 427 1010 428 1009 C 432 965 449 967 444 928 C 469 949 482 975 478 995 C 503 977 493 1000 500 1028 C 503 1058 475 1080 441 1095 Z')
    flame_s=dome(flame,5.0,2.5)
    flame_s=engrave(flame_s,line([(443,1080),(433,1050),(445,1023),(448,999)],.26),.35)
    paint(GOLD,flame_s,flame,5.0)
    for tip,root in [((185,1260),(167,1170)),((227,1274),(221,1193)),((676,1284),(734,1197)),((647,1310),(691,1244))]:
        a,b=point(*tip),point(*root);v=b-a;length=np.linalg.norm(v)
        leaf=petal(*a,length,1.15,-math.degrees(math.atan2(v[0],v[1])))
        leaf=(leaf^silhouette)-banner.offset(.1)
        if not leaf.is_empty():paint(GOLD,dome(leaf,3.2,1.8),leaf,3.2)
    ribbon=dome(banner,2.8,1.7,center=point(444,1298),radii=(280*scale,107*scale))
    paint(CREAM,ribbon,banner,2.8)
    font='/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf'
    name=text('BRUNA',22.3,font=font)
    pp=pts(name);name=name.scale((1,3.8/(pp[:,1].max()-pp[:,1].min())))
    outline=[np.asarray(v) for v in banner.to_polygons()]
    def ribbon_bounds(x):
        values=[]
        for loop in outline:
            for a,b in zip(loop,np.roll(loop,-1,axis=0)):
                if (a[0]<=x<b[0]) or (b[0]<=x<a[0]):
                    values.append(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
        return min(values),max(values)
    warped=[]
    for loop in name.to_polygons():
        contour=[]
        for x,y in loop:
            x-=.1;low,high=ribbon_bounds(x)
            height=min(3.6,high-low-.84)
            contour.append((x,(low+high-height)/2+y/3.8*height))
        warped.append(contour)
    name=md.CrossSection(warped,md.FillRule.EvenOdd)
    colors[BROWN]+=raised(ribbon,name,.55)
    # The eye line follows the strong reference tilt, roughly 22 degrees.
    eye_data=[(374,750,42,51),(514,691,37,47)]
    for x,y,rx,ry in eye_data:
        cx,cy=point(x,y)
        def eye_shape(frac,dx=0,dy=0):
            return ellipse(0,0,rx*scale*frac,ry*scale*frac).rotate(-12).translate((cx+dx,cy+dy))
        rim=eye_shape(1);iris=eye_shape(.80,.02,-.03);pupil=eye_shape(.57,-.10,.10)
        black_rim=raised(cheeks,rim,.40)-iris.extrude(20)
        gold_eye=raised(cheeks,iris,.85)-pupil.extrude(20)
        black_eye=raised(cheeks,pupil,1.25)
        colors[BLACK]+=black_rim+black_eye;colors[GOLD]+=gold_eye
        glint=ellipse(cx-.18,cy+.78,.34,.34)
        colors[CREAM]+=raised(black_eye,glint,.30)
    beak=sec('M 450 737 Q 468 729 480 750 Q 491 782 489 818 Q 465 801 448 774 Q 442 755 450 737 Z')
    colors[BROWN]+=raised(cheeks,beak,1.3)
    brow=line([(319,715),(342,706),(366,708),(387,717),(407,715)],.52)
    brow+=line([(472,677),(490,663),(514,656),(532,638),(536,626)],.59)
    lid=line([(307,748),(334,745),(359,731),(382,720),(402,716)],.52)
    brow_s=raised(cheeks,brow^face,.80)
    lid_s=raised(cheeks,lid^face,.70)
    for c in colors:colors[c]-=brow_s+lid_s
    colors[BROWN]+=brow_s;colors[BLACK]+=lid_s
    # Black is inlaid only in selected feather veins, not thick cartoon outlines.
    inlay=((colors[GOLD]-colors[GOLD].translate((0,0,-.2)))^wing_lines.extrude(20))
    colors[GOLD]-=inlay;colors[BLACK]+=inlay
    for c in (BROWN,CREAM,GOLD):colors[c]-=colors[BLACK]
    grain=md.CrossSection()
    for x,y in [(367,576),(398,561),(432,564),(401,599),(385,630),
                (357,908),(376,944),(548,967),(543,1007),(390,1007),(400,965),(529,916)]:
        grain+=line([(x-12,y+8),(x,y-9),(x+15,y-17)],.22)
    grain-=face.offset(.25)+wing_area.offset(.25)+banner.offset(.3)+pages.offset(.6)+flame.offset(.3)
    grain-=crests[0].offset(.25)+crests[1].offset(.25)
    colors[BROWN]=engrave(colors[BROWN],grain,.24)
    # Curved green scarf with a brown knot, printed as a two-color assembly.
    pocket=scarf.offset(.2,circular_segments=24)
    cutter=pocket.extrude(16).translate((0,0,4.8))
    for c in colors:colors[c]-=cutter
    green=scarf.extrude(.9)+dome(scarf,.9,.9,center=point(466,920),radii=(200*scale,150*scale))
    knot_mask=ell(475,929,37,21)^scarf.offset(-.08)
    green+=knot_mask.extrude(1.3)
    knot=dome(knot_mask,1.3,1.0)
    green-=knot_mask.extrude(10).translate((0,0,1.3))
    knot=engrave(knot,line([(445,922),(467,913),(490,917),(507,924)],.43)+line([(447,936),(470,926),(491,931),(503,939)],.43),.24)
    green=engrave(green,line([(466,1033),(474,993),(470,953)],.30),.22)
    assert all(s.status()==md.Error.NoError for s in colors.values())
    return colors,green,scarf,silhouette,knot


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    colors,green,scarf,sil,knot=build()
    positive=sorted([s for s in union(colors.values()).decompose() if s.volume()>1e-5],key=lambda s:s.volume(),reverse=True)
    removed_volume=sum(s.volume() for s in positive[1:])
    assert removed_volume<.02,'A detached printable feature requires redesign'
    if len(positive)>1:
        chips=union(positive[1:])
        for c in colors:colors[c]-=chips
        print('Removidas aparas abaixo da resolução:',removed_volume,'mm3',flush=True)
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
    tm=np.eye(4);tm[2,3]=5.0
    add('lenco-verde',GREEN,green,tm)
    add('no-castanho',BROWN,knot,tm)
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
    data={'title':'Coruja BRUNA V3 - relevo curvo para bico 0.2',
        'model_type':'bas-relief with smooth domes and engraved feather shafts',
        'front_dimensions_mm':full.extents.tolist(),'front_height_limit_mm':50,
        'base_thickness_mm':3.5,'scarf_glue_gap_mm':.2,'scarf_lateral_clearance_mm':.2,
        'ring_clear_opening_mm':[25,18],'ring_height_mm':20,
        'ring_glue_pad_mm':[12.8,20],'minimum_engraving_width_mm':.20,
        'removed_subresolution_chips_mm3':removed_volume,
        'body_connected':True,'assembled_color_intersections':collisions,
        'physical_print_tested':False,'parts':entries}
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    # Rotate to upright only for the drawings; the STL keeps a flat rear on Z=0.
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    upright=[(s.transform(stand[:3].tolist()),c) for s,c in assembled]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet=Image.new('RGB',(1700,1150),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:6],(830,950),direction=(.1,-1,.12),margin=30),(0,100))
    sheet.paste(render_meshes(upright,(820,900),direction=(.8,-1,.3),margin=30),(850,120))
    draw.text((40,25),'Coruja BRUNA V3 · relevo curvo · bico 0,2 mm',font=font(34),fill=BROWN)
    draw.text((40,1085),f'Altura 50 mm · espessura da frente até {full.extents[2]:.1f} mm · geometria real',font=font(26),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    detail=render_meshes(upright[:4],(1300,1500),direction=(.35,-1,.25),margin=55)
    detail.save(ROOT/'designs'/f'{PREFIX}-detalhe.png')
    sheet=Image.new('RGB',(1600,1000),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:6],(600,730),direction=(0,-1,0),margin=30),(0,110))
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
