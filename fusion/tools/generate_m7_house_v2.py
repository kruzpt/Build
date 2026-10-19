"""Reuse the original STL logo on the house, with deep glue locating pockets."""
from copy import deepcopy
import hashlib
import json
from shutil import copy2

import manifold3d as md
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import trimesh

import generate_m7_prototypes_v1 as v
from generate_joana_topper import cross_section
from generate_m7_brick_v4 import exact_mesh
from generate_universo_stand import render_meshes

ROOT=v.ROOT
FOLDER=ROOT/'fusion/M7CasaV2'
PREFIX='m7-casa-v2'


def rebuild(regions):
    result=None
    for region in regions:
        solid=cross_section(region['groups']).extrude(region['height']).translate((0,0,region['z']))
        solid=v.transformed(solid,np.asarray(region['transform']))
        if region['operation']=='new':result=solid if result is None else result+solid
        elif region['operation']=='join':result+=solid
        else:result-=solid
    return result


def main():
    FOLDER.mkdir(exist_ok=True)
    source=json.loads((ROOT/'fusion/M7PrototiposV1/geometry.json').read_text())
    original=[p for p in source['parts'] if p['product']=='casa']
    old={p['key']:p for p in original}
    mdata=json.loads((ROOT/'fusion/M7TijoloV5Conceito/m-original.json').read_text())
    sdata=json.loads((ROOT/'fusion/M7TijoloV4/source-seven.json').read_text())
    raw_m=md.CrossSection(mdata['groups'],md.FillRule.EvenOdd)
    raw_7=cross_section(sdata['groups'])
    points=v.pts(raw_m+raw_7);lo,hi=points.min(0),points.max(0)
    origin=np.array([(lo[0]+hi[0])/2,lo[1]]);scale=18/(hi[0]-lo[0])
    def logo(cs):return cs.translate(-origin).scale((scale,scale)).translate((0,3.))
    shapes={'m-branco':logo(raw_m),'7-ciano':logo(raw_7)}
    assert (shapes['m-branco']^shapes['7-ciano']).area()<.001
    # The final two V1 operations are old logo cuts; all earlier operations stay.
    base_regions=deepcopy(old['base-azul']['regions'][:-2])
    old_base=rebuild(old['base-azul']['regions'])
    original_stl=trimesh.load(ROOT/'downloads'/old['base-azul']['file'],force='mesh')
    assert abs(old_base.volume()-original_stl.volume)<.15
    base=rebuild(base_regions);fp=v.pose_front()
    pockets={};reservoirs={}
    for key,cs in shapes.items():
        pocket=cs.offset(.2,circular_segments=24)
        assert v.pts(pocket)[:,1].max()<15.4
        assert v.pts(pocket)[:,1].min()>2
        # The wider shallow pocket guides the entire letter. A narrower inner
        # well stores glue while leaving a floor/ledge around its perimeter.
        reservoir=cs.offset(-.35,circular_segments=24)
        assert reservoir.area()>.05
        main_region=v.region(pocket,.9,-.8,'cut',fp)
        well_region=v.region(reservoir,.35,-1.1,'cut',fp)
        for region in (main_region,well_region):
            base-=rebuild([dict(region,operation='new')])
            base_regions.append(region)
        pockets[key]=pocket;reservoirs[key]=reservoir
    assert len(base.decompose())==1
    parts=[];assembled=[];difference={};pose=fp.copy()
    pose[:3,3]+=fp[:3,2]*-.65
    reusable=[]
    for entry in original:
        part=deepcopy(entry);key=part['key'];part['file']=f'{PREFIX}-{key}.stl'
        target=ROOT/'downloads'/part['file']
        if key=='base-azul':
            solid=base;part['regions']=base_regions;mesh=exact_mesh(solid,target)
        elif key in shapes:
            solid=shapes[key].extrude(1.8)
            part['regions']=[v.region(shapes[key],1.8)];part['assembly']=pose.tolist()
            part['name']=('m branco' if key=='m-branco' else '7 ciano')+' original do STL - encaixe profundo'
            mesh=exact_mesh(solid,target)
            roundtrip=md.Manifold(md.Mesh(mesh.vertices.astype('float32'),mesh.faces.astype('uint32'))).slice(.9)
            recovered=roundtrip.translate((0,-3)).scale((1/scale,1/scale)).translate(origin)
            raw=raw_m if key=='m-branco' else raw_7
            error=(raw-recovered).area()+(recovered-raw).area()
            assert error<.002
            difference[key]=error
        else:
            copy2(ROOT/'downloads'/entry['file'],target)
            assert target.read_bytes()==(ROOT/'downloads'/entry['file']).read_bytes()
            mesh=trimesh.load(target,force='mesh');solid=rebuild(entry['regions']);reusable.append(key)
        assert mesh.is_watertight and mesh.is_winding_consistent
        part.update(bbox_mm=mesh.extents.tolist(),volume_mm3=float(mesh.volume),
                    watertight=True,sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        parts.append(part);assembled.append((v.transformed(solid,np.array(part['assembly'])),part['color']))
    for i,(a,_) in enumerate(assembled):
        for b,_ in assembled[i+1:]:assert (a^b).volume()<.001
    for key in shapes:
        moving=v.transformed(shapes[key].extrude(1.8),pose)
        for distance in np.linspace(0,4,41):assert (moving.translate((0,-float(distance),0))^base).volume()<.001
    report={'version':2,'change':'Exact source m and 7; deeper locating pockets with inner glue wells',
        'assembled_height_mm':95,'base_width_depth_mm':[85,85],'logo_width_mm':18,
        'original_logo_relative_positions_preserved':True,'uniform_scale_xy':scale,
        'source_sha256':mdata['source_sha256'],'recovered_source_errors_mm2':difference,
        'pocket_depth_mm':.8,'pocket_lateral_clearance_per_side_mm':.2,
        'letter_thickness_mm':1.8,'letter_insertion_mm':.65,'visible_relief_mm':1.15,
        'nominal_glue_floor_gap_mm':.15,'extra_glue_well_depth_mm':.3,
        'glue_well_total_depth_mm':1.1,'glue_well_inset_from_letter_edge_mm':.35,
        'inner_wells_capacity_mm3':{key:float(cs.area()*.3) for key,cs in reservoirs.items()},
        'reusable_v1_parts':reusable,'new_required_parts':['base-azul','m-branco','7-ciano'],
        'insertion_positions_checked':82,'watertight':True,'physical_fit_tested':False,
        'glue_squeeze_out_prevented_guaranteed':False,'fusion_runtime_tested':False}
    (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','version':2,'parts':parts,'house':report},ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    template=(ROOT/'fusion/M7TijoloV3/M7TijoloV3.py').read_text()
    template=template.replace('M7 - Tijolo Natal 2026 V3 - 7 pincelado','M7 Casa V2 - logotipo original')
    template=template.replace('M7 Tijolo V3 criado num documento novo.','M7 Casa V2 criada num documento novo.')
    template=template.replace('Tijolo: 50 x 26 x 70 mm, rebaixos 0,20 mm.','Casa: altura 95 mm; rebaixos do logotipo de 0,80 mm.')
    template=template.replace('3MF V3 de quatro pratos','3MF Casa V2 de tres pratos')
    (FOLDER/'M7CasaV2.py').write_text(template)
    sample=base ^ md.Manifold.cube((24,4,15)).translate((-12,0,1))
    sample_pose=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,4],[0,0,0,1]],float)
    sample=v.transformed(sample,sample_pose)
    exact_mesh(sample,ROOT/'downloads'/f'{PREFIX}-amostra-logo.stl')
    illustrate(assembled,base,shapes,pose)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


def illustrate(assembled,base,shapes,pose):
    image=Image.new('RGB',(1650,1100),'#f4f6f8');font=lambda n:ImageFont.truetype(v.REGULAR,n)
    image.paste(render_meshes(assembled,(830,920),direction=(.45,-.8,.4)),(0,110))
    exploded=[(base,v.BLUE)]+[(v.transformed(cs.extrude(1.8),pose).translate((0,-8,0)),
                              v.WHITE if key=='m-branco' else v.CYAN) for key,cs in shapes.items()]
    image.paste(render_meshes(exploded,(800,650),direction=(.18,-1,.15)),(850,210))
    d=ImageDraw.Draw(image)
    d.text((35,20),'M7 · Casinha V2 · m e 7 originais',font=font(35),fill=v.BLUE)
    d.text((35,73),'Mesmo desenho e dimensões · base 85 × 85 mm · altura 95 mm',font=font(26),fill=v.BLUE)
    for y,line in [(880,'Rebaixo: 0,80 mm · inserção: 0,65 mm'),
                   (925,'Folga lateral: 0,20 mm por lado'),
                   (970,'Fundo para cola + reservatório interior')]:
        d.text((850,y),line,font=font(24),fill=v.BLUE)
    d.text((35,1050),'Reutilizar fachada, frase e fundo da V1 · substituir base, m e 7 · testar sem cola primeiro',font=font(24),fill=v.BLUE)
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')


if __name__=='__main__':main()
