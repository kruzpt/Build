"""Remove only the user-marked under-sill tab from a supplied Gallardo 3MF.

Keeps the source build transform, print configuration, designer and license.
Requires the user-supplied input; does not download another copy or print.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import NS, read_project, run_cli
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'gallardo-straight-sill-v1'
FOLDER = ROOT/'fusion/GallardoStraightSillV1'
TARGET = ROOT/'downloads'/f'{PREFIX}.3mf'
MESH_PATH = '3D/Objects/object_1.model'


def manifold(mesh):
    result = md.Manifold(md.Mesh64(np.asarray(mesh.vertices, dtype=np.float64), np.asarray(mesh.faces, dtype=np.uint64)))
    assert result.status()==md.Error.NoError
    return result


def as_mesh(solid):
    m = solid.to_mesh64()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3], np.asarray(m.tri_verts), process=True)


def xml_mesh(mesh):
    vertices = ''.join('<vertex x="%.12g" y="%.12g" z="%.12g"/>'%tuple(p) for p in mesh.vertices)
    faces = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>'%tuple(f) for f in mesh.faces)
    return f'<mesh><vertices>{vertices}</vertices><triangles>{faces}</triangles></mesh>'.encode()


def side_view(mesh, image, left, top, scale, color):
    # Local Z points down in this imported drawing; keep the car upright.
    d = ImageDraw.Draw(image)
    for tri in mesh.triangles:
        d.polygon([(left+(x+139.533356)*scale, top+(z+42.1745224)*scale) for x,y,z in tri], fill=color)


def comparison(before, after, anchors):
    factor = 2
    im = Image.new('RGB', (1280*factor,1010*factor), '#f5f7fa')
    d = ImageDraw.Draw(im)
    font = lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n*factor)
    d.text((35*factor,20*factor),'Gallardo — straight sill edit',font=font(30),fill='#17344a')
    d.text((35*factor,68*factor),'Before',font=font(25),fill='#17344a')
    side_view(before, im, 60*factor,115*factor,4*factor,'#283e4b')
    x1,z1=anchors[0];x2,z2=anchors[1]
    d.rectangle(((60+(x1+139.533356)*4-5)*factor,(115+(z1+42.1745224)*4-3)*factor,
                 (60+(x2+139.533356)*4+5)*factor,(115+(42.1745224+42.1745224)*4+5)*factor),outline='#d85442',width=3*factor)
    d.text((35*factor,510*factor),'After — marked tab removed',font=font(25),fill='#17344a')
    side_view(after, im,60*factor,560*factor,4*factor,'#283e4b')
    d.line([((60+(x+139.533356)*4)*factor,(560+(z+42.1745224)*4)*factor) for x,z in anchors],fill='#15937c',width=3*factor)
    d.text((35*factor,895*factor),'Green: the new straight edge. Original outline and thickness retained elsewhere.',font=font(22),fill='#17344a')
    d.text((35*factor,942*factor),'Orthographic projections of the actual meshes · same scale · not a print-quality prediction',font=font(20),fill='#455d70')
    output=im.resize((1280,1010),Image.Resampling.LANCZOS)
    output.save(ROOT/'designs'/f'{PREFIX}-comparison.png')
    return output


def png(image):
    s=io.BytesIO();image.save(s,format='PNG');return s.getvalue()


def main(a):
    FOLDER.mkdir(exist_ok=True)
    a.work_dir.mkdir(parents=True,exist_ok=True)
    with ZipFile(a.input) as z:
        assert z.testzip() is None
        original={n:z.read(n) for n in z.namelist()}
    root=ET.fromstring(original[MESH_PATH])
    obj=root.find(f'{{{NS}}}resources/{{{NS}}}object')
    vertices=np.array([[float(v.get(k)) for k in 'xyz'] for v in obj.findall(f'{{{NS}}}mesh/{{{NS}}}vertices/{{{NS}}}vertex')])
    faces=np.array([[int(f.get(k)) for k in ('v1','v2','v3')] for f in obj.findall(f'{{{NS}}}mesh/{{{NS}}}triangles/{{{NS}}}triangle')])
    before=trimesh.Trimesh(vertices,faces,process=True)
    assert before.is_watertight and before.is_winding_consistent and len(before.split())==1
    assert np.allclose(before.extents,[279.066712,3.20000004,84.3490448],atol=.0001)
    section=before.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
    area=lambda p:abs(np.dot(p[:-1,0],p[1:,2])-np.dot(p[1:,0],p[:-1,2]))/2
    outline=max(section.discrete,key=area)
    tab_vertices=vertices[vertices[:,2]>30]
    xmin,xmax=tab_vertices[:,0].min(),tab_vertices[:,0].max()
    assert 49.9<xmax-xmin<50.1
    anchors=[]
    # Join nearby untouched sill edges, avoiding coincident old tab-root vertices.
    # The extra 0.753 mm at each side lies inside the user's marked sill region.
    for x in (xmin-.753,xmax+.753):
        heights=[]
        for p,q in zip(outline,outline[1:]):
            if abs(q[0]-p[0])<1e-10:
                continue
            t=(x-p[0])/(q[0]-p[0])
            if 0<=t<=1:
                heights.append(p[2]+t*(q[2]-p[2]))
        assert heights
        anchors.append([float(x),float(max(heights))])
    (x1,z1),(x2,z2)=anchors
    slope=(z2-z1)/(x2-x1)
    line=lambda x:z1+slope*(x-x1)
    xleft,xright=x1-.2,x2+.2
    cutter=md.CrossSection([[(xleft,line(xleft)),(xright,line(xright)),(xright,60),(xleft,60)]]).extrude(20).rotate((90,0,0)).translate((0,10,0))
    old=manifold(before)
    edited=old-cutter
    assert edited.status()==md.Error.NoError and not edited.is_empty()
    after=as_mesh(edited)
    assert after.is_watertight and after.is_winding_consistent and len(after.split())==1
    assert np.allclose(before.bounds[:,:2],after.bounds[:,:2],atol=1e-9)
    assert (edited-old).volume()<1e-7
    removed=as_mesh(old-edited)
    assert removed.bounds[0,0]>=xleft-1e-7 and removed.bounds[1,0]<=xright+1e-7
    assert np.min(removed.vertices[:,2]-np.array([line(x) for x in removed.vertices[:,0]]))>-1e-7
    cut_faces=after.vertices[np.abs(after.vertices[:,2]-np.array([line(x) for x in after.vertices[:,0]]))<1e-7]
    assert len(cut_faces)>=4
    assert cut_faces[:,0].max()-cut_faces[:,0].min()>49.9
    blobs=dict(original)
    assert len(re.findall(rb'<mesh>.*?</mesh>',blobs[MESH_PATH],re.S))==1
    blobs[MESH_PATH]=re.sub(rb'<mesh>.*?</mesh>',lambda _:xml_mesh(after),blobs[MESH_PATH],flags=re.S)
    settings=ET.fromstring(blobs['Metadata/model_settings.config'])
    main_obj=settings.find('object')
    main_obj.find("metadata[@key='name']").set('value','Gallardo - straight sill')
    main_obj.find('metadata[@face_count]').set('face_count',str(len(after.faces)))
    part=main_obj.find('part')
    part.find("metadata[@key='name']").set('value','Gallardo - straight sill')
    part.find('mesh_stat').set('face_count',str(len(after.faces)))
    plate=settings.find('plate')
    plate.find("metadata[@key='plater_name']").set('value','Gallardo - straight sill')
    # Clear stale view/picking images; retain the new actual geometry thumbnail.
    for key in ('thumbnail_no_light_file','top_file','pick_file'):
        node=plate.find(f"metadata[@key='{key}']")
        if node is not None:plate.remove(node)
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    model=blobs['3D/3dmodel.model']
    model=re.sub(rb'(<metadata name="Title">).*?(</metadata>)',rb'\g<1>Lamborghini Gallardo silhouette - straight sill\g<2>',model)
    model=re.sub(rb'(<metadata name="Origin">).*?(</metadata>)',rb'\g<1>modified\g<2>',model)
    blobs['3D/3dmodel.model']=model
    for name in ('Metadata/plate_no_light_1.png','Metadata/top_1.png','Metadata/pick_1.png'):
        blobs.pop(name,None)
    # Temporary archive permits use of the existing, production-namespace-aware reader.
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    actual,_,plates=read_project(TARGET)
    placed=plates[0]['items'][0]['mesh']
    assert placed.bounds[0,2]>-.00001 and abs(placed.extents[2]-3.2)<.0001
    assert placed.bounds[0,:2].min()>0 and placed.bounds[1,:2].max()<256
    placed.export(ROOT/'downloads'/f'{PREFIX}.stl')
    thumb=Image.new('RGB',(512,512),'#eef2f5');d=ImageDraw.Draw(thumb)
    for tri in placed.triangles:d.polygon([(22+x*468/256,490-y*468/256) for x,y,z in tri],fill='#263d4b')
    blobs['Metadata/plate_1.png']=png(thumb)
    blobs['Metadata/plate_1_small.png']=png(thumb.resize((128,128),Image.Resampling.LANCZOS))
    for name,size in [('Auxiliaries/.thumbnails/thumbnail_3mf.png',(512,512)),('Auxiliaries/.thumbnails/thumbnail_middle.png',(512,512)),('Auxiliaries/.thumbnails/thumbnail_small.png',(128,128))]:
        blobs[name]=png(thumb.resize(size,Image.Resampling.LANCZOS))
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    actual,_,_=read_project(TARGET)
    assert actual['Metadata/project_settings.config']==original['Metadata/project_settings.config']
    # Root placement and component references are untouched.
    assert re.search(rb'<build\b.*?</build>',actual['3D/3dmodel.model'],re.S)[0]==re.search(rb'<build\b.*?</build>',original['3D/3dmodel.model'],re.S)[0]
    comparison(before,after,anchors)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
    help_result=subprocess.run([str(a.bambu_bin),'--help'],capture_output=True,text=True,check=True)
    version=re.search(r'BambuStudio-([\d.]+)',help_result.stdout+help_result.stderr).group(1)
    run_cli(a.bambu_bin,['--datadir',str(a.work_dir/'user'),'--debug','2','--allow-newer-file','--slice','0','--orient','0','--arrange','0','--outputdir',str(a.work_dir/'slice'),'--export-3mf','validation.3mf',str(TARGET)],a.work_dir/'slice.log')
    result=json.loads((a.work_dir/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==1
    p=result['sliced_plates'][0]
    assert not p.get('warning_message')
    cfg=json.loads(actual['Metadata/project_settings.config'])
    with ZipFile(a.work_dir/'slice/validation.3mf') as z:code=z.read('Metadata/plate_1.gcode').decode()
    rr=paths(code)
    assert set(r['tool'] for r in rr)=={3} and '; FEATURE: Support' not in code
    report={'project':TARGET.name,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        'input_filename':a.input.name,'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
        'operation':'Subtract only the under-sill tab below the straight line joining its two roots.',
        'straight_edge_endpoints_local_xz_mm':anchors,'straight_edge_length_mm':float(np.linalg.norm(np.array(anchors[1])-anchors[0])),
        'before_volume_mm3':float(before.volume),'after_volume_mm3':float(after.volume),'removed_volume_mm3':float(removed.volume),
        'removed_bounds_local_xyz_mm':removed.bounds.tolist(),'added_volume_mm3':float((edited-old).volume()),
        'width_and_thickness_unchanged':True,'width_mm':float(after.extents[0]),'thickness_mm':float(after.extents[1]),
        'single_connected_watertight_solid':True,'straight_cut_face_verified':True,'remaining_changes_confined_to_cut_volume':True,
        'source_build_transform_identical':True,'print_configuration_byte_identical':True,
        'source_designer':'Dava','source_license_metadata':'Standard Digital File License','source_attribution_and_license_retained':True,
        'printer':cfg['printer_settings_id'],'layer_height_mm':cfg['layer_height'],'material_slot_used':3,
        'brim_policy_preserved':cfg['brim_type'],'slicer_version':version,'newer_file_compatibility_enabled':True,
        'source_project_version':cfg['version'],'native_slice_exit':0,'warnings':p.get('warning_message'),
        'estimated_seconds':p['total_predication'],'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
        'physical_print_tested':False,'physical_print_started':False}
    (FOLDER/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--bambu-bin',type=Path,required=True)
    parser.add_argument('--work-dir',type=Path,required=True)
    main(parser.parse_args())
