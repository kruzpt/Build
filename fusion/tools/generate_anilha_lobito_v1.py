"""Parametric wolf woggle with a keyed, glue-on flat-relief face; mm.

This creates actual meshes, not an Autodesk Fusion native document.
Opening reuses Coruja BRUNA; the 30 mm body and flat-relief styling are proposed.
"""
import argparse
import json
from pathlib import Path
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from generate_m7_prototypes_v1 import union, stroke, pose_front, transformed, rounded
from generate_joana_topper import save_mesh
from generate_universo_stand import render_meshes

ROOT=Path(__file__).resolve().parents[2]
PREFIX='anilha-lobito-v1'
FOLDER=ROOT/'fusion/AnilhaLobitoV1'
COLORS=['#72767C','#F5F3ED','#18191C']


def ellipse(x,z,rx,rz):
    return md.CrossSection.circle(1,96).scale((rx,rz)).translate((x,z))


def polygon(points,rounding=.25):
    return md.CrossSection([points],md.FillRule.EvenOdd).offset(rounding,circular_segments=24)


def make(height=30.):
    FOLDER.mkdir(exist_ok=True)
    bore=md.CrossSection.circle(1,100).scale((12.5,9))
    hole=bore.extrude(height+2).translate((0,0,-1))
    entry=md.Manifold.cylinder(1,13.5,12.5,100).scale((1,.72,1))
    exit=md.Manifold.cylinder(1,12.5,13.5,100).scale((1,.72,1)).translate((0,0,height-1))
    body=md.Manifold.cylinder(height,21,18.5,192)-union([hole,entry,exit])
    body-=md.Manifold.cube((60,30,height+2)).translate((-30,-45,-1))
    pocket=rounded(-10,3.5,20,23,1.2)
    cutter=transformed(pocket.extrude(1.85),pose_front(-13.65))
    body-=cutter
    tongue=pocket.offset(-.2,circular_segments=32)
    head=polygon([(-20,0),(20,0),(18.5,30),(-18.5,30)],.65)
    ear_white=md.CrossSection()
    for sign in (-1,1):
        ear=polygon([(9,27),(11.5,34.5),(16,38),(18,37.8),(20,34),(19,25)],.65)
        inner=polygon([(12.3,29.5),(15.8,34.6),(17.2,34.8),(18.1,29.2)],.35)
        if sign<0:ear=ear.mirror((1,0));inner=inner.mirror((1,0))
        head+=ear;ear_white+=inner
    head=head ^ md.CrossSection.square((60,45)).translate((-30,0))
    whites=ellipse(0,8.4,11.2,7.6)+ear_white
    for sign in (-1,1):
        tuft=polygon([(9,4.5),(14,4),(17.5,6),(15.5,6.6),(18.3,9),(15.7,9.3),(18,12.4),(14.2,10.8),(10,11.5)],.2)
        if sign<0:tuft=tuft.mirror((1,0))
        whites+=tuft
    for x in (-8.5,8.5):whites+=ellipse(x,20.3,4.25,5.25)
    blacks=ellipse(-7.2,19.1,2,2.75)+ellipse(7.2,19.1,2,2.75)
    for sign in (-1,1):
        pts=np.array([(5.3,27),(6.7,27.7),(8.6,28),(10.4,27.6),(11.6,26.6)])
        pts[:,0]*=sign;blacks+=stroke(pts,.95)
    blacks+=polygon([(-3.7,14.1),(-3.9,12.8),(-2.5,11.1),(0,10.4),(2.5,11.1),(3.9,12.8),(3.7,14.1),(0,14.6)],.35)
    smile=polygon([(-6.3,8.3),(-4.6,6.9),(-2,6.1),(0,5.9),(2,6.1),(4.6,6.9),(6.3,8.3),(5.1,5.6),(3.3,3.6),(1.6,2.7),(0,2.5),(-1.6,2.7),(-3.3,3.6),(-5.1,5.6)],.2)
    blacks+=smile
    accents=ellipse(-6.8,20.5,.65,.7)+ellipse(6.8,20.5,.65,.7)
    accents+=(ellipse(-.8,3.6,1.5,1)+ellipse(.8,3.6,1.5,1)) ^ smile.offset(-.45)
    assert (whites-head).area()<.001 and (blacks-head).area()<.001
    base=head.extrude(3.6)-(head-tongue).extrude(1.2)
    black=blacks.extrude(1.1).translate((0,0,3.6))
    accents_s=accents.extrude(.5).translate((0,0,4.4))
    raw_white=whites.extrude(.6).translate((0,0,3.6))
    envelope=union([base,raw_white,black,accents_s])
    white=union([raw_white-black,accents_s])
    black-=accents_s
    face=union([s for s in envelope.simplify(.001).decompose() if s.volume()>1e-6])
    assert len(face.decompose())==1
    mount=pose_front(-13.8)
    face_assembled=transformed(face,mount)
    assert (face_assembled ^ body).volume()<.001
    assert (transformed(tongue.extrude(1.2),mount)-cutter).volume()<.001
    assert (body ^ bore.offset(-.01).extrude(height)).volume()<.001
    parts=[]
    for key,solid,col in zip(('corpo','rosto-cinzento','rosto-branco','rosto-preto'),(body,base,white,black),(COLORS[0],*COLORS)):
        mesh=save_mesh(solid,ROOT/'downloads'/f'{PREFIX}-{key}.stl')
        parts.append(dict(key=key,file=f'{PREFIX}-{key}.stl',color=col,dimensions_mm=mesh.extents.tolist(),volume_mm3=solid.volume()))
    save_mesh(face,ROOT/'downloads'/f'{PREFIX}-rosto-completo.stl')
    owl=json.loads((ROOT/'fusion/CorujaBrunaV1/geometry.json').read_text())
    owl_ring=next(p for p in owl['parts'] if p['key']=='anilha-castanha')
    old_bore=md.CrossSection([owl_ring['regions'][0]['groups'][0][1]],md.FillRule.EvenOdd)
    bore_difference=(old_bore-bore).area()+(bore-old_bore).area()
    assert bore_difference<.001
    report=dict(parameters=dict(bore_opening_mm=[25,18],body_height_mm=height,pocket_width_height_depth_mm=[20,23,1.35],tongue_width_height_depth_mm=[19.6,22.6,1.2],clearance_each_side_mm=.2,glue_floor_gap_mm=.15,face_back_thickness_mm=2.4),opening_source='Coruja BRUNA V1-V6: ellipse radii12.5,9; 100 segments',bore_symmetric_difference_from_cached_owl_mm2=bore_difference,proposed_body_height=True,parts=parts,face_mount_matrix=mount.tolist(),closed_meshes=True,face_connected=True,assembly_interference_mm3=(face_assembled ^ body).volume(),bore_open=True,physical_fit_tested=False,physical_print_tested=False,print_note='Body upright. Face relief up on locating tongue; supports under back overhangs only.')
    (FOLDER/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    assembled=[(body,COLORS[0])]+[(transformed(a,mount),c) for a,c in zip((base,white,black),COLORS)]
    image=Image.new('RGB',(1500,950),'#f4f6f8');draw=ImageDraw.Draw(image)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    image.paste(render_meshes(assembled,(800,760),direction=(.1,-1,.35)),(0,130))
    image.paste(render_meshes(assembled,(650,650),direction=(.65,-.8,.85)),(830,170))
    draw.text((35,25),'Anilha de lenço — lobito V1',font=font(35),fill='#263446')
    draw.text((35,78),'Abertura oval 25 × 18 mm, como na coruja · rosto com guia de colagem',font=font(24),fill='#465468')
    draw.text((35,900),'Modelo real. Corpo proposto: 30 mm. Rosto em relevo plano. Encaixe e acabamento por testar.',font=font(22),fill='#465468')
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    detail=Image.new('RGB',(1400,900),'#f4f6f8');d=ImageDraw.Draw(detail)
    detail.paste(render_meshes([(body,COLORS[0])],(680,670),direction=(.05,-1,.3)),(0,125))
    detail.paste(render_meshes([(base,COLORS[0])],(680,670),direction=(.3,-.25,-1)),(710,125))
    d.text((30,25),'Guia de colagem — geometria real',font=font(34),fill='#263446')
    d.text((30,90),'Corpo: rebaixo 20 × 23 × 1,35 mm',font=font(24),fill='#465468')
    d.text((735,90),'Verso: guia 19,6 × 22,6 × 1,20 mm',font=font(24),fill='#465468')
    d.text((30,825),'Folga de 0,20 mm por lado · espaço de 0,15 mm no fundo para cola · verificar a seco',font=font(24),fill='#465468')
    detail.save(ROOT/'designs'/f'{PREFIX}-encaixe.png')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--height',type=float,default=30)
    args=p.parse_args();assert args.height>=30
    make(args.height)
