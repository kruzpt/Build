"""M7 V5: reinforced eight-hole brick and one registered multicolour plaque."""
import hashlib
import json
from pathlib import Path

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

import generate_m7_prototypes_v1 as v
from generate_joana_topper import cross_section, save_mesh
from generate_m7_brick_v4 import exact_mesh
from generate_universo_stand import render_meshes

ROOT=v.ROOT
FOLDER=ROOT/'fusion/M7TijoloV5'
PREFIX='m7-tijolo-v5'
BASE=.6
DEPTH=.7


def main():
    FOLDER.mkdir(exist_ok=True)
    old=json.loads((ROOT/'fusion/M7TijoloV4/geometry.json').read_text())
    old={p['key']:p for p in old['parts']}
    original=cross_section(old['tijolo-terracota']['regions'][0]['groups'])
    polygons=original.to_polygons()
    exterior=md.CrossSection([polygons[0]])
    holes=md.CrossSection([loop for loop in polygons[1:]],md.FillRule.EvenOdd)
    # Preserve the outer grooves and all eight openings, but increase the shell
    # behind both broad faces. Recess leaves a full 3 mm backing wall.
    holes=holes ^ v.rect(-30,3.7,60,22.5-3.7)
    assert len(holes.decompose())==8
    profile=exterior-holes
    pocket=v.rounded(-23.5,1.5,47,67,1.)
    carrier=v.rounded(-23.3,1.7,46.6,66.6,.8)
    assert (carrier-pocket).area()<1e-6
    assert (carrier.offset(.199,circular_segments=32)-pocket).area()<.001
    fp=v.pose_front()
    cutter=v.transformed(pocket.extrude(DEPTH+.1).translate((0,0,-DEPTH)),fp)
    body=profile.extrude(70)-cutter
    body_regions=[v.region(profile,70),v.region(pocket,DEPTH+.1,-DEPTH,'cut',fp)]
    star=v.normalize(cross_section(old['estrela-dourada']['regions'][0]['groups']),width=30).translate((0,39))
    tree=v.normalize(cross_section(old['arvore-dourada']['regions'][0]['groups']),height=27).translate((0,11.5))
    wording=v.text('Natal 2026',38,font=v.SCRIPT,strengthen=.16).translate((0,2.8))
    mdata=json.loads((ROOT/'fusion/M7TijoloV5Conceito/m-original.json').read_text())
    sdata=json.loads((ROOT/'fusion/M7TijoloV4/source-seven.json').read_text())
    raw_m=md.CrossSection(mdata['groups'],md.FillRule.EvenOdd)
    raw_seven=cross_section(sdata['groups'])
    points=v.pts(raw_m+raw_seven);lo,hi=points.min(0),points.max(0)
    factor=13/(hi[0]-lo[0]);origin=np.array([(lo[0]+hi[0])/2,lo[1]])
    def logo(cs): return cs.translate(-origin).scale((factor,factor)).translate((0,48))
    letter_m,seven=logo(raw_m),logo(raw_seven)
    assert ((letter_m+seven).offset(.35,circular_segments=24)^star).area()<1e-6
    assert (letter_m^seven).area()<1e-6
    sections=[star+tree,wording+letter_m,seven]
    for cs in sections: assert (cs-carrier).area()<.001
    for i,a in enumerate(sections):
        for b in sections[i+1:]: assert (a^b).area()<.0001
    assert (star^tree).area()<.001
    assert (wording^(star+tree)).area()<.001
    solids=[body,carrier.extrude(BASE)]+[cs.extrude(1.0).translate((0,0,BASE)) for cs in sections]
    colors=[v.ORANGE,v.ORANGE,v.GOLD,v.WHITE,v.CYAN]
    keys=['corpo-reforcado','placa-laranja','relevo-dourado','relevo-branco','7-ciano']
    names=['Tijolo com moldura e paredes reforçadas','Fundo laranja único da placa',
           'Estrela e árvore douradas unidas à placa','m original e Natal 2026 manuscrito','7 original ciano']
    plaque_pose=fp.copy();plaque_pose[:3,3]+=fp[:3,2]*(-BASE)
    # Carrier front is flush with body Y=0, its back at Y=.6; pocket floor .7.
    assembled=[(body,colors[0])]
    parts=[]
    regions=[body_regions,[v.region(carrier,BASE)]]+[[v.region(cs,1.,BASE)] for cs in sections]
    for i,(solid,col,key,name) in enumerate(zip(solids,colors,keys,names)):
        path=ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=exact_mesh(solid,path)
        pose=v.identity() if i==0 else plaque_pose
        parts.append({'key':key,'name':name,'file':path.name,'color':col,'product':'tijolo',
                      'regions':regions[i],'assembly':pose.tolist(),
                      'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),
                      'watertight':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if i: assembled.append((v.transformed(solid,pose),col))
    union=v.union(solids[1:]);um=union.to_mesh()
    joined=trimesh.Trimesh(um.vert_properties[:,:3],um.tri_verts,process=True)
    assert joined.is_watertight and len(joined.split())==1
    for solid,col in assembled[1:]:assert (solid^body).volume()<.001
    for solid,col in assembled[1:]:
        for distance in np.linspace(0,6,25):assert (solid.translate((0,-float(distance),0))^body).volume()<.001
    # Verify the serialized exact logo still recovers the customer's outlines.
    source_errors={}
    white_mesh=trimesh.load(ROOT/'downloads'/parts[3]['file'],force='mesh')
    white_solid=md.Manifold(md.Mesh(white_mesh.vertices.astype('float32'),white_mesh.faces.astype('uint32')))
    m_slice=white_solid.slice(1.0) ^ v.rect(-15,47,30,18)
    seven_mesh=trimesh.load(ROOT/'downloads'/parts[4]['file'],force='mesh')
    seven_slice=md.Manifold(md.Mesh(seven_mesh.vertices.astype('float32'),seven_mesh.faces.astype('uint32'))).slice(1.)
    for name,raw,section in [('m',raw_m,m_slice),('7',raw_seven,seven_slice)]:
        recovered=section.translate((0,-48)).scale((1/factor,1/factor)).translate(origin)
        err=(raw-recovered).area()+(recovered-raw).area()
        assert err<.002,(name,err)
        source_errors[name]=err
    report={'version':5,'body_width_depth_height_mm':[50,26,70],'through_holes':8,
            'pocket_width_height_depth_mm':[47,67,.7],'carrier_width_height_thickness_mm':[46.6,66.6,.6],
            'lateral_clearance_per_side_mm':.2,'nominal_glue_gap_mm':.1,'frame_width_mm':1.5,
            'front_surface_flush_nominally':True,'front_wall_behind_pocket_mm':3.,
            'rear_wall_mm':3.5,'relief_height_mm':1.,'finished_plaque_thickness_mm':1.6,
            'logo_width_mm':13,'star_width_mm':30,'uniform_logo_scale':factor,'original_m_and_7_relationship_preserved':True,
            'logo_recovered_source_errors_mm2':source_errors,'m_source_sha256':mdata['source_sha256'],
            'seven_source_sha256':sdata['source_sha256'],'script':'Z003 Medium Italic',
            'inscription':'Natal 2026','plaque_connected_as_assembled':True,
            'mesh_watertight':True,'insertion_positions_checked_per_component':25,
            'physical_fit_tested':False,'physical_print_tested':False,'fusion_runtime_tested':False,
            'rib_marks_eliminated_confirmed':False}
    (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','version':5,'parts':parts,'brick':report},ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    # Generic region-based Fusion BRep builder; run inside Fusion, not a claimed F3D export.
    script=(ROOT/'fusion/M7TijoloV3/M7TijoloV3.py').read_text().replace('V3','V5').replace('7 pincelado','placa única')
    script=script.replace('Tijolo: 50 x 26 x 70 mm, rebaixos 0,20 mm.',
                          'Tijolo: 50 x 26 x 70 mm; placa 46,6 x 66,6 x 0,6 mm.')
    script=script.replace('V5 de quatro pratos','V5 de dois pratos')
    (FOLDER/'M7TijoloV5.py').write_text(script)
    sheet(assembled,body,solids,colors)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


def sheet(assembled,body,solids,colors):
    font=lambda n:ImageFont.truetype(v.REGULAR,n)
    image=Image.new('RGB',(1800,1200),'#f4f6f8');d=ImageDraw.Draw(image)
    d.text((35,20),'M7 · Tijolo V5 — placa única e moldura',font=font(38),fill=v.BLUE)
    d.text((35,80),'50 × 26 × 70 mm · 8 furos · m e 7 do STL original · Natal 2026 manuscrito',font=font(25),fill=v.BLUE)
    image.paste(render_meshes(assembled,(830,950),direction=(.45,-.85,.55)),(5,130))
    exploded=[(body,v.ORANGE)]+[(solid.translate((0,-9,0)),col) for solid,col in assembled[1:]]
    image.paste(render_meshes(exploded,(900,780),direction=(.6,-1,.5)),(875,140))
    d=ImageDraw.Draw(image)
    d.text((945,930),'Placa: 46,6 × 66,6 mm · fundo 0,6 mm',font=font(24),fill=v.BLUE)
    d.text((945,976),'Rebaixo 0,7 mm · folga 0,2 mm por lado',font=font(24),fill=v.BLUE)
    d.text((945,1022),'Superfície laranja alinhada com a moldura',font=font(24),fill=v.BLUE)
    d.text((35,1120),'Corpo: paredes reforçadas e perfil de acabamento · Placa: relevo para cima, base apoiada na mesa',font=font(25),fill=v.BLUE)
    d.text((35,1160),'Geometria real · encaixe e acabamento ainda a confirmar numa impressão física',font=font(24),fill=v.BLUE)
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    front=Image.new('RGB',(1000,1150),'#f4f6f8')
    front.paste(render_meshes(assembled,(960,1000),direction=(.015,-1,.01)),(20,80))
    ImageDraw.Draw(front).text((30,20),'M7 V5 · vista frontal do modelo real',font=font(30),fill=v.BLUE)
    front.save(ROOT/'designs'/f'{PREFIX}-frente.png')


if __name__=='__main__':main()
