"""Local V6 eye-tip correction; reuse V5 lettering, backing, foliage and ring."""
import copy
import hashlib
import json
import cv2
import manifold3d as md
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
import generate_anilha_aquela_v5 as v5
from generate_anilha_aquela_v5 import ROOT,SOURCE,COLORS,BLACK,GRAY,BROWN,WHITE,GREEN,SCALE_X,SCALE_Y
from generate_anilha_aquela_v2 import largest,tracer,cap
from generate_anilha_aquela_v3 import solid_from_mesh
from generate_coruja_bruna_v3 import exact,union
from generate_universo_stand import render_meshes
FOLDER=ROOT/'fusion/AnilhaAquelaV6';PREFIX='anilha-aquela-v6'


def wolf():
    old,badge,masks=v5.wolf()
    rgb=np.array(Image.open(SOURCE).convert('RGB').crop((65,133,425,490)))
    r,g,b=rgb.astype(float).transpose(2,0,1);gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    fg=(gray<130)&~((b>r*1.3)&(b>g*1.05));fg[:2]=0;fg[:,:4]=0;fg[:,-4:]=0
    fg,box=largest(fg);trace=tracer(box,55*SCALE_X,65*SCALE_Y)
    raw=np.zeros_like(fg)
    cv2.fillPoly(raw,[np.array([(270,80),(281,79),(287,88),(291,93),(298,99),(304,106),
                               (300,112),(289,116),(281,115),(276,103),(271,89)])],1)
    mask=trace(raw)^badge.offset(-.38)
    mask-=masks['right_eye_white'].offset(.38,md.JoinType.Round,circular_segments=24)
    mask-=masks['right_pupil'].offset(.38,md.JoinType.Round,circular_segments=24)
    mask-=old[BLACK].slice(4.30).offset(.12,md.JoinType.Round,circular_segments=24)
    region=mask^old[BLACK].slice(3.90)
    assert region.area()>3
    cut=region.extrude(3).translate((0,0,3.32))
    body=dict(old)
    body[BLACK]-=cut
    body[GRAY]+=cap(region,3.32,3.80,.08)
    whole=union(body.values())
    assert all(s.status()==md.Error.NoError for s in body.values())
    assert len([s for s in whole.decompose() if s.volume()>1e-7])==1
    assert all((body[a]^body[b]).volume()<.001 for i,a in enumerate(body) for b in list(body)[i+1:])
    assert (body[BLACK]^region.extrude(3).translate((0,0,3.33))).volume()<.001
    assert (region-body[BLACK].slice(3.30)).area()<.001
    assert (body[WHITE]-old[WHITE]).volume()+(old[WHITE]-body[WHITE]).volume()<.001
    assert (body[BROWN]-old[BROWN]).volume()+(old[BROWN]-body[BROWN]).volume()<.001
    # The nose and all geometry outside the local tip keep their exact solids.
    for c in (GRAY,BLACK):
        difference=(body[c]-old[c])+(old[c]-body[c])
        assert (difference-cut).volume()<.001
    masks['gray_eye_tip']=region
    return body,old,badge,masks


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    body,old,badge,masks=wolf()
    data=copy.deepcopy(json.loads((v5.FOLDER/'geometry.json').read_text()))
    parts=data['parts'];reused={};scene=[];glb=trimesh.Scene()
    for p in parts:
        if p['key'] in ('lobo-preto','lobo-cinzento'):
            path=ROOT/'downloads'/f"{PREFIX}-{p['key']}.stl"
            mesh=exact(body[p['color']],path)
            p.update(file=path.name,dimensions_mm=mesh.extents.tolist(),volume_mm3=mesh.volume,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            solid=body[p['color']]
        else:
            path=ROOT/'downloads'/p['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
            reused[path.name]=p['sha256'];mesh=trimesh.load(path,force='mesh')
            solid=body[p['color']] if p['piece']=='lobo' else solid_from_mesh(path)
        pose=np.array(p['assembly']);scene.append((solid.transform(pose[:3].tolist()),p['color']))
        mesh=mesh.copy();mesh.apply_transform(pose)
        mesh.visual.face_colors=[int(p['color'][i:i+2],16) for i in (1,3,5)]+[255]
        glb.add_geometry(mesh,node_name=p['key'])
    project=ROOT/'downloads/anilha-aquela-v5-ACESSORIOS-A1-04-AMS-2-pratos.3mf'
    reused[project.name]=hashlib.sha256(project.read_bytes()).hexdigest()
    glb.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    front=exact(union(body.values()),ROOT/'downloads'/f'{PREFIX}-lobo-completo-monocor.stl')
    assert np.allclose(front.extents,data['front_dimensions_mm'],atol=.003)
    masks_json={k:[np.asarray(p).tolist() for p in s.to_polygons()] for k,s in masks.items()}
    old_masks=json.loads((v5.FOLDER/'validation-regions.json').read_text())
    masks_json['hidden_leaf']=old_masks['hidden_leaf']
    (FOLDER/'validation-regions.json').write_text(json.dumps(masks_json,indent=2)+'\n')
    data.update(title='Aquelá V6 — ponta exterior do olho cinzenta',
                wolf_project=PREFIX+'-LOBO-A1-04-AMS-4-cores.3mf',
                accessory_project=project.name,reused_unchanged_sha256=reused,
                local_eye_gray_area_mm2=masks['gray_eye_tip'].area(),
                gray_tip_bottom_mm=3.32,gray_tip_top_mm=3.80,
                pupil_white_letters_nose_and_accessories_unchanged=True,
                front_dimensions_mm=front.extents.tolist(),physical_print_tested=False)
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    (FOLDER/'bambu-validation-acessorios.json').write_bytes((v5.FOLDER/'bambu-validation-acessorios.json').read_bytes())
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0]],float)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    clip=md.CrossSection.square((24,20)).translate((-3,32)).extrude(6)
    sheet=Image.new('RGB',(1400,800),'#f4f6f8');d=ImageDraw.Draw(sheet)
    for i,b in enumerate((old,body)):
        items=[((s^clip).transform(stand.tolist()),c) for c,s in b.items() if (s^clip).volume()>1e-5]
        sheet.paste(render_meshes(items,(690,670),direction=(0,-1,0),margin=25),(700*i,70))
        d.text((700*i+30,20),['V5 · ponta preta','V6 · ponta cinzenta'][i],font=font(28),fill='#23384C')
    d.text((30,750),'Geometria real · pupila e branco mantidos · contorno fino junto ao olho',font=font(24),fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-olho-comparacao-CAD.png')
    upright=[(s.transform(stand.tolist()),c) for s,c in scene]
    sheet=Image.new('RGB',(1500,1040),'#f4f6f8');d=ImageDraw.Draw(sheet)
    d.text((35,25),'Aquelá V6 · ponta do olho em cinzento',font=font(34),fill='#23384C')
    for i,direction in enumerate(((0,-1,0),(.55,-1,.25))):
        sheet.paste(render_meshes(upright,(730,840),direction=direction,margin=35),(i*760,90))
    d.text((35,950),'Conjunto 52 × 55 mm · letras sem contorno preto · folhas e anilha da V5',font=font(26),fill='#23384C')
    d.text((35,990),'Prévia dos sólidos exportados · impressão física por testar',font=font(24),fill='#536276')
    sheet.save(ROOT/'designs'/f'{PREFIX}-montada-CAD.png')
    print(json.dumps({'front_dimensions_mm':front.extents.tolist(),'gray_tip_mm2':masks['gray_eye_tip'].area(),
                      'reused_files':sorted(reused)},indent=2),flush=True)


if __name__=='__main__':main()
