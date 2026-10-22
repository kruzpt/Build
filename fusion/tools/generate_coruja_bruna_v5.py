"""Trace the illustrated badge into actual flat, stepped printable relief."""
from pathlib import Path
import json
import hashlib
import cv2
import numpy as np
import manifold3d as md
import trimesh
from PIL import Image, ImageDraw, ImageFont
from generate_coruja_bruna_v1 import BROWN, CREAM, GOLD, BLACK, GREEN, ellipse, rounded
from generate_coruja_bruna_v3 import exact, union
from generate_joana_topper import cross_section, groups, section_groups
from generate_universo_stand import render_meshes

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/CorujaBrunaV5'
PREFIX='anilha-coruja-bruna-v5'
SOURCE=ROOT/'designs'/'anilha-coruja-bruna-v4-ilustracao.png'

def build():
    rgb=np.asarray(Image.open(SOURCE).convert('RGB')).astype(float)
    palette=[BLACK,BROWN,CREAM,GOLD,GREEN,'#FFFFFF']
    pal=np.array([[int(c[i:i+2],16) for i in (1,3,5)] for c in palette])
    labels=np.argmin(((rgb[:,:,None,:]-pal)**2).sum(3),axis=2).astype('uint8')
    fg=(labels!=5).astype('uint8')*255
    contours,_=cv2.findContours(fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    outer=max(contours,key=cv2.contourArea)
    fg[:]=0;cv2.drawContours(fg,[outer],-1,255,-1)
    x,y,w,h=cv2.boundingRect(outer);scale=50/(h-1)
    xmid=x+(w-1)/2;ymax=y+h-1
    def section(mask,minimum=45):
        return cross_section(groups(mask.astype('uint8')*255,scale,xmid,ymax,minimum)).simplify(.008)
    silhouette=section(fg>0,1000)
    # Morphological filtering suppresses artwork grain below nozzle resolution.
    masks=[]
    for i in range(5):
        mask=((labels==i)&(fg>0)).astype('uint8')
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
        masks.append(mask)
    # One connected removable scarf insert; black backing joins its four ends.
    insert_mask=cv2.dilate(masks[4],cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    cv2.ellipse(insert_mask,(651,650),(51,46),0,0,360,1,-1)
    components,_=cv2.findContours(insert_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    largest=max(components,key=cv2.contourArea)
    assert cv2.contourArea(largest)>sum(cv2.contourArea(c) for c in components)*.98
    insert_mask[:]=0;cv2.drawContours(insert_mask,[largest],-1,1,-1)
    insert=section(insert_mask>0,100)
    sections={c:section(masks[i]>0)^silhouette for i,c in enumerate(palette[:5])}
    # Enforce disjoint footprints after contour simplification.
    used=md.CrossSection()
    for c in [GREEN,CREAM,GOLD,BROWN]:
        sections[c]-=used;used+=sections[c]
    # Keep the palette inside a continuous dark frame. Smooth only large
    # color islands so the tiny eye highlights retain their original shapes.
    for c in [BROWN,CREAM,GOLD]:
        pieces=[]
        for island in sections[c].decompose():
            if island.area()>3:
                island=island.offset(-.12,md.JoinType.Round,circular_segments=16).offset(.04,md.JoinType.Round,circular_segments=16)
            # A small inward margin separates colors from the outer silhouette.
            pieces.append(island)
        sections[c]=md.CrossSection.batch_boolean(pieces,md.OpType.Add) ^ silhouette.offset(-.20,md.JoinType.Round,circular_segments=16)
    sections[BLACK]=silhouette-sections[GREEN]-sections[CREAM]-sections[GOLD]-sections[BROWN]
    pocket=insert.offset(.2,md.JoinType.Round,circular_segments=16)
    body={BLACK:silhouette.extrude(2.4)}
    heights={BROWN:3.0,GOLD:3.2,CREAM:3.4,BLACK:3.6}
    # Colored surfaces are opaque four-layer caps on black relief pedestals,
    # rather than full-height colored walls. The raised black border surrounds
    # each patch, including the formerly striped feather edge below the face.
    for c in [BROWN,GOLD,CREAM]:
        pedestal=heights[c]-.4
        body[BLACK]+=sections[c].extrude(pedestal-2.4).translate((0,0,2.4))
        body[c]=sections[c].extrude(.4).translate((0,0,pedestal))
    body[BLACK]+=sections[BLACK].extrude(1.2).translate((0,0,2.4))
    for c in body:
        body[c]-=pocket.extrude(10).translate((0,0,2.0))
    # Separate assembled scarf: green, brown knot, black outline; three colors.
    original={c:section(masks[i]>0)^silhouette for i,c in enumerate(palette[:5])}
    green_sec=original[GREEN]^insert
    # Warm highlights in the illustration's knot map back to brown filament.
    knot_sec=((original[BROWN]+original[GOLD])^insert).simplify(.015)
    black_sec=insert-green_sec-knot_sec
    scarf={BLACK:insert.extrude(.5)+black_sec.extrude(.9).translate((0,0,.5)),
           GREEN:green_sec.extrude(.7).translate((0,0,.5)),
           BROWN:knot_sec.extrude(.8).translate((0,0,.5))}
    return body,scarf,silhouette,sections,heights

def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    body,scarf,sil,sections,heights=build()
    entries=[];assembled=[]
    def add(key,col,solid,pose=None):
        target=ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=exact(solid,target)
        pose=np.eye(4) if pose is None else pose
        entries.append({'key':key,'file':target.name,'color':col,'assembly':pose.tolist(),
                        'dimensions_mm':mesh.extents.tolist(),'volume_mm3':mesh.volume,
                        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'watertight':True})
        assembled.append((solid.transform(pose[:3].tolist()),col))
    for key,c in [('castanho',BROWN),('creme',CREAM),('dourado',GOLD),('preto',BLACK)]:add(key,c,body[c])
    pose=np.eye(4);pose[2,3]=2.15
    for key,c in [('lenco-verde',GREEN),('no-castanho',BROWN),('lenco-preto',BLACK)]:add(key,c,scarf[c],pose)
    ring_sec=(ellipse(0,0,15,11.5)+rounded(-7,-13,14,4,.6))-ellipse(0,0,12.5,9)
    ring=ring_sec.extrude(20)
    ring_pose=np.array([[1,0,0,0],[0,0,1,12],[0,-1,0,-13],[0,0,0,1]],float)
    add('anilha-castanha',BROWN,ring,ring_pose)
    whole=union(body.values())
    assert len([p for p in whole.decompose() if p.volume()>1e-5])==1
    mono=exact(whole,ROOT/'downloads'/f'{PREFIX}-CORUJA-COMPLETA-monocor.stl')
    assert mono.extents[1]<=50.01
    collisions=[]
    for i,(a,c) in enumerate(assembled):
        for j,(b,_) in enumerate(assembled[i+1:],i+1):
            volume=(a^b).volume()
            if volume>.003:collisions.append([entries[i]['key'],entries[j]['key'],volume])
    assert not collisions,collisions
    data={'title':'Coruja BRUNA V5 - emblema ilustrado em camadas',
          'model_type':'traced illustration with planar stepped color relief; not rounded sculpture',
          'front_dimensions_mm':mono.extents.tolist(),'front_height_limit_mm':50,
          'base_thickness_mm':2.4,'top_heights_mm':heights,
          'color_cap_thickness_mm':.4,'outer_black_rim_minimum_mm':.20,
          'large_color_region_inset_mm':.08,
          'scarf_glue_gap_mm':.15,'scarf_lateral_clearance_mm':.2,
          'ring_clear_opening_mm':[25,18],'ring_height_mm':20,'body_connected':True,
          'assembled_color_intersections':collisions,'physical_print_tested':False,'parts':entries}
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    (FOLDER/'contours.json').write_text(json.dumps({c:section_groups(s) for c,s in sections.items()}))
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    upright=[(s.transform(stand[:3].tolist()),c) for s,c in assembled]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet=Image.new('RGB',(1700,1120),'#f4f6f8');d=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:7],(820,900),direction=(0,-1,0),margin=35),(0,110))
    sheet.paste(render_meshes(upright,(820,900),direction=(.65,-1,.32),margin=35),(860,110))
    d.text((35,25),'Coruja BRUNA V5 · emblema ilustrado em camadas',font=font(34),fill=BROWN)
    d.text((35,1040),f'50 × {mono.extents[0]:.1f} mm · relevo total 3,6 mm · vistas do modelo real',font=font(27),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    sheet=Image.new('RGB',(1650,1000),'#f4f6f8');d=ImageDraw.Draw(sheet)
    sheet.paste(render_meshes(upright[:4],(620,760),direction=(.15,-1,.12),margin=30),(0,85))
    sheet.paste(render_meshes([(s,c) for c,s in scarf.items()],(430,460),direction=(.2,.3,1),margin=35),(630,160))
    sheet.paste(render_meshes([(ring,BROWN)],(500,530),direction=(.6,-1,.8),margin=30),(1100,125))
    d.text((35,25),'V5 · peças e medidas · bico 0,2 mm na coruja',font=font(33),fill=BROWN)
    d.text((35,855),f'Coruja: 50 × {mono.extents[0]:.1f} × 3,6 mm',font=font(24),fill=BROWN)
    d.text((650,690),'Lenço: uma peça de 3 cores',font=font(22),fill=GREEN)
    d.text((650,730),'Folga lateral: 0,20 mm',font=font(22),fill=BROWN)
    d.text((1120,735),'Anilha: interior 25 × 18 mm',font=font(22),fill=BROWN)
    d.text((1120,775),'Altura: 20 mm · bico 0,4 mm',font=font(22),fill=BROWN)
    d.text((35,940),'Frente: castanho, creme, dourado e preto. Lenço separado para colar. Sem suportes.',font=font(24),fill=BROWN)
    sheet.save(ROOT/'designs'/f'{PREFIX}-pecas-dimensoes.png')
    scene=trimesh.Scene()
    for e in entries:
        m=trimesh.load(ROOT/'downloads'/e['file'],force='mesh');m.apply_transform(e['assembly'])
        m.visual.face_colors=tuple(int(e['color'][i:i+2],16) for i in (1,3,5))+(255,)
        scene.add_geometry(m,node_name=e['key'])
    scene.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    print(json.dumps({k:v for k,v in data.items() if k!='parts'},indent=2))

if __name__=='__main__':main()
