"""Replace hidden black in the Aquelá V3 foliage with green, without changing shape."""
import hashlib
import json
from pathlib import Path

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from generate_anilha_aquela_v2 import ROOT, SOURCE, GREEN, BLACK
from generate_anilha_aquela_v3 import build_leaves, solid_from_mesh, WOLF_PROJECT
from generate_coruja_bruna_v3 import exact, union
from generate_universo_stand import render_meshes

FOLDER=ROOT/'fusion/AnilhaAquelaV4'
PREFIX='anilha-aquela-v4'
EDGE_MARGIN=.45


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    prior=json.loads((ROOT/'fusion/AnilhaAquelaV3/geometry.json').read_text())
    reused=[p for p in prior['parts'] if p['piece']!='folhas']
    source_solids={}
    for p in reused:
        file=ROOT/'downloads'/p['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==p['sha256']
        source_solids[p['key']]=solid_from_mesh(file)
    for file,sha in prior['reused_unchanged_sha256'].items():
        assert hashlib.sha256((ROOT/'downloads'/file).read_bytes()).hexdigest()==sha
    badge=source_solids['lobo-preto'].slice(1.0)
    old,outline,ink,visible=build_leaves(badge)
    hidden=badge.offset(-EDGE_MARGIN,md.JoinType.Round,circular_segments=24)^outline
    transfer=old[BLACK]^hidden.extrude(4)
    bodies={GREEN:old[GREEN]+transfer,BLACK:old[BLACK]-transfer}
    combined=union(bodies.values());original=union(old.values())
    assert (combined-original).volume()+(original-combined).volume()<.00001
    assert (bodies[GREEN]^bodies[BLACK]).volume()<.00001
    assert (bodies[BLACK]^hidden.extrude(4)).volume()<.00001
    assert (hidden-bodies[GREEN].slice(1.99)).area()<.001
    assert (hidden^combined.slice(2.01)).area()<.001
    assert len([p for p in combined.decompose() if p.volume()>1e-7])==1
    assert (bodies[BLACK].slice(1.6)-bodies[GREEN].slice(1.5)).area()<.001
    # Every change lies inside the wolf silhouette; the exposed face is preserved.
    outside=outline-badge
    assert (transfer^outside.extrude(4)).volume()<.00001
    parts=list(reused)
    for key,color in [('folhas-verdes',GREEN),('folhas-nervuras-pretas',BLACK)]:
        file=ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=exact(bodies[color],file)
        parts.append({'key':key,'file':file.name,'color':color,'piece':'folhas','assembly':np.eye(4).tolist(),
                      'dimensions_mm':mesh.extents.tolist(),'volume_mm3':mesh.volume,'watertight':True,
                      'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    # Even the exported black STL stays outside the hidden mask, within mesh tolerance.
    actual_black=solid_from_mesh(ROOT/'downloads'/f'{PREFIX}-folhas-nervuras-pretas.stl')
    assert (actual_black^hidden.offset(-.01).extrude(4)).volume()<.001
    whole=exact(combined,ROOT/'downloads'/f'{PREFIX}-folhas-completas-monocor.stl')
    assert np.allclose(whole.extents,[62,48,2.96],atol=.02)
    scene=[];glb=trimesh.Scene();intersections=[]
    for p in parts:
        solid=bodies[p['color']] if p['piece']=='folhas' else source_solids[p['key']]
        pose=np.array(p['assembly']);scene.append((solid.transform(pose[:3].tolist()),p['color']))
        mesh=trimesh.load(ROOT/'downloads'/p['file'],force='mesh');mesh.apply_transform(pose)
        mesh.visual.face_colors=[int(p['color'][i:i+2],16) for i in (1,3,5)]+[255]
        glb.add_geometry(mesh,node_name=p['key'])
    for i,(a,_) in enumerate(scene):
        for j,(b,_) in enumerate(scene[i+1:],i+1):
            if parts[i]['piece']!='folhas' and parts[j]['piece']!='folhas':continue
            v=(a^b).volume()
            if v>.003:intersections.append([parts[i]['key'],parts[j]['key'],v])
    assert not intersections
    glb.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    report={'title':'Aquelá V4 — zona oculta das folhas só verde',
        'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'reused_unchanged_sha256':prior['reused_unchanged_sha256'],'wolf_project':WOLF_PROJECT,
        'physical_parts_count':3,'foliage_color_volume_count':2,'foliage_dimensions_mm':whole.extents.tolist(),
        'flat_glue_face_z_mm':2.0,'exposed_green_top_mm':2.96,'exposed_black_top_mm':2.72,
        'edge_margin_under_wolf_mm':EDGE_MARGIN,'hidden_region_mm2':hidden.area(),
        'original_black_volume_mm3':old[BLACK].volume(),'new_black_volume_mm3':bodies[BLACK].volume(),
        'black_replaced_with_green_mm3':transfer.volume(),'black_volume_reduction_percent':100*transfer.volume()/old[BLACK].volume(),
        'hidden_region_black_volume_mm3':0,'combined_external_geometry_unchanged':True,'visible_decoration_unchanged':True,
        'connected_leaf_piece':True,'supported_color_caps':True,'assembly_intersections':intersections,
        'parts':parts,'physical_print_tested':False,'physical_fit_tested':False}
    (FOLDER/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    leaf=lambda b:[(s.transform(stand[:3].tolist()),c) for c,s in b.items()]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet=Image.new('RGB',(1600,880),'#f4f6f8');d=ImageDraw.Draw(sheet)
    d.text((35,25),'Aquelá V4 · verde na área coberta pelo lobo',font=font(32),fill='#23384C')
    d.text((35,90),'V3 · preto também na zona escondida',font=font(24),fill='#23384C')
    d.text((825,90),'V4 · mesma peça, centro só verde',font=font(24),fill='#23384C')
    sheet.paste(render_meshes(leaf(old),(780,600),direction=(0,-1,0),margin=35),(0,140))
    sheet.paste(render_meshes(leaf(bodies),(780,600),direction=(0,-1,0),margin=35),(810,140))
    d.text((35,785),'Face de colagem mantida a 2 mm · margem de 0,45 mm sob o contorno do lobo',font=font(25),fill='#23384C')
    d.text((35,830),'Nervuras expostas, lobo, tabuleta e anilha mantidos',font=font(23),fill='#536276')
    sheet.save(ROOT/'designs'/f'{PREFIX}-folhas-comparacao-CAD.png')
    upright=[(s.transform(stand[:3].tolist()),c) for s,c in scene]
    sheet=Image.new('RGB',(1450,1000),'#f4f6f8');d=ImageDraw.Draw(sheet)
    d.text((35,25),'Aquelá V4 · conjunto montado',font=font(32),fill='#23384C')
    sheet.paste(render_meshes(upright,(710,800),direction=(0,-1,0),margin=35),(0,100))
    sheet.paste(render_meshes(upright,(710,800),direction=(.55,-1,.25),margin=35),(740,100))
    d.text((35,935),'Geometria real · mesmo aspeto exterior · três peças para colar',font=font(25),fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-montada-CAD.png')
    print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2),flush=True)


if __name__=='__main__':main()
