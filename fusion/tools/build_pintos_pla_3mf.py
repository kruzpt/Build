"""Build a native Bambu Studio A1 project, using the standard V3 clip.

The native CLI exports the geometry/settings. This script adds overhead
thumbnails from that exported geometry and validates all plates by slicing.
Requires numpy, Pillow, trimesh, and an installed official Bambu Studio CLI.
Example:
 python fusion/tools/build_pintos_pla_3mf.py --bambu-bin PATH --profiles PATH
Add --layout 2-pratos for one grid plate and one plate of 26 standard clips.
"""
import argparse
from copy import deepcopy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/GrelhaPintosV3PLA'
TARGET=ROOT/'downloads/grelha-pintos-v3-A1-PLA-13-pratos.3mf'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def flatten_profile(profiles,kind,name,chain=()):
    if name in chain: raise ValueError('Preset inheritance cycle: '+name)
    item=json.loads((profiles/kind/(name+'.json')).read_text())
    result=flatten_profile(profiles,kind,item['inherits'],chain+(name,)) if item.get('inherits') else {}
    for included in item.get('include',[]):
        result.update(flatten_profile(profiles,kind,included,chain+(name,)))
    result.update(item)
    result.pop('include',None)
    return result


def assembly_plan(two_plates=False):
    clip=json.loads((FOLDER/'clip-overrides.json').read_text())
    def item(name,params=None):
        return {'path':str(ROOT/'downloads'/name),'count':1,'filaments':[1],
                'print_params':deepcopy(params or {})}
    def plate(name,items):
        return {'plate_name':name,'need_arrange':True,'objects':items}
    if two_plates:
        return {'plates':[
            plate('01 - Placa universal PLA',[
                item('grelha-pintos-v3-placa-universal.stl')]),
            plate('02 - 26 presilhas padrao PLA',[
                item('grelha-pintos-v3-presilha-padrao.stl',clip) for _ in range(26)])]}
    result=[plate('01 - Amostra duas bordas PLA',[
                item('grelha-pintos-v3-amostra-duas-bordas.stl')]),
            plate('02 - Presilha padrao TESTE PLA',[
                item('grelha-pintos-v3-presilha-padrao.stl',clip)])]
    result += [plate(f'{i+3:02d} - Placa universal {i+1} de 10',[
                item('grelha-pintos-v3-placa-universal.stl')]) for i in range(10)]
    result += [plate('13 - 26 presilhas padrao PLA',[
                item('grelha-pintos-v3-presilha-padrao.stl',clip) for _ in range(26)])]
    return {'plates':result}


def matrix(text):
    if not text: return np.eye(4)
    a=np.array([float(x) for x in text.split()])
    if len(a)!=12: raise ValueError('Invalid 3MF transform')
    result=np.eye(4)
    result[:3,:3]=a[:9].reshape(3,3).T
    result[:3,3]=a[9:]
    return result


def read_project(path):
    """Resolve native external component meshes and build transformations."""
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        blobs={n:archive.read(n) for n in archive.namelist()}
    roots={}
    def objects(model_path):
        if model_path not in roots:
            root=ET.fromstring(blobs[model_path])
            assert root.get('unit','millimeter')=='millimeter'
            roots[model_path]={int(o.get('id')):o for o in root.findall(f'{{{NS}}}resources/{{{NS}}}object')}
        return roots[model_path]
    def geometry(model_path,object_id,stack=()):
        key=(model_path,object_id)
        if key in stack: raise ValueError('Component cycle')
        obj=objects(model_path)[object_id]
        mesh=obj.find(f'{{{NS}}}mesh')
        if mesh is not None:
            verts=np.array([[float(v.get(c)) for c in ('x','y','z')]
                            for v in mesh.findall(f'{{{NS}}}vertices/{{{NS}}}vertex')])
            faces=np.array([[int(t.get(c)) for c in ('v1','v2','v3')]
                            for t in mesh.findall(f'{{{NS}}}triangles/{{{NS}}}triangle')])
            return trimesh.Trimesh(vertices=verts,faces=faces,process=True)
        pieces=[]
        for part in obj.findall(f'{{{NS}}}components/{{{NS}}}component'):
            other=part.get(f'{{{PROD}}}path',model_path).lstrip('/')
            item=geometry(other,int(part.get('objectid')),stack+(key,))
            item.apply_transform(matrix(part.get('transform')))
            pieces.append(item)
        if not pieces: raise ValueError('Empty 3MF object')
        return trimesh.util.concatenate(pieces)
    root=ET.fromstring(blobs['3D/3dmodel.model'])
    model_config=ET.fromstring(blobs['Metadata/model_settings.config'])
    build={int(i.get('objectid')):matrix(i.get('transform'))
           for i in root.findall(f'{{{NS}}}build/{{{NS}}}item')}
    object_configs={int(o.get('id')):{m.get('key'):m.get('value') for m in o.findall('metadata')
                                    if m.get('key')} for o in model_config.findall('object')}
    plates=[]
    count=len(model_config.findall('plate'))
    cols=math.ceil(math.sqrt(count))
    for i,plate in enumerate(model_config.findall('plate')):
        props={m.get('key'):m.get('value') for m in plate.findall('metadata')}
        assert int(props['plater_id'])==i+1
        origin=np.array([(i%cols)*256*1.2,-(i//cols)*256*1.2,0])
        items=[]
        for inst in plate.findall('model_instance'):
            settings={m.get('key'):m.get('value') for m in inst.findall('metadata')}
            object_id=int(settings['object_id'])
            assert int(settings['instance_id'])==0
            mesh=geometry('3D/3dmodel.model',object_id)
            mesh.apply_transform(build[object_id])
            mesh.apply_translation(-origin)
            items.append({'id':object_id,'mesh':mesh,'settings':object_configs[object_id]})
        plates.append({'properties':props,'items':items})
    return blobs,model_config,plates


def thumbnails(source,target,preview_path):
    """Attach truthful overhead diagrams of the exported plate placement."""
    blobs,config,plates=read_project(source)
    thumbs=[]
    for index,plate in enumerate(plates):
        im=Image.new('RGB',(400,440),'white')
        draw=ImageDraw.Draw(im)
        scale=350/256
        draw.rectangle((25,45,375,395),fill='#eef0f1',outline='#849498',width=2)
        for item in plate['items']:
            for tri in item['mesh'].triangles:
                points=[(25+v[0]*scale,395-v[1]*scale) for v in tri]
                draw.polygon(points,fill='#62a79f')
        font=ImageFont.truetype(FONT,17)
        draw.text((15,10),plate['properties']['plater_name'],font=font,fill='#28383c')
        draw.text((20,410),f"A1 · PLA · {len(plate['items'])} objeto(s)",font=font,fill='#28383c')
        stream=io.BytesIO(); im.save(stream,format='PNG')
        path=f'Metadata/plate_{index+1}.png'
        blobs[path]=stream.getvalue()
        small=im.resize((128,140),Image.Resampling.LANCZOS)
        stream=io.BytesIO(); small.save(stream,format='PNG')
        blobs[f'Metadata/plate_{index+1}_small.png']=stream.getvalue()
        node=config.findall('plate')[index]
        existing=node.find("metadata[@key='thumbnail_file']")
        if existing is not None: node.remove(existing)
        ET.SubElement(node,'metadata',key='thumbnail_file',value=path)
        thumbs.append(im)
    blobs['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as archive:
        for name,data in blobs.items(): archive.writestr(name,data)
    two_plates=len(plates)==2
    overview=Image.new('RGB',(850,580) if two_plates else (1400,1760),'white')
    d=ImageDraw.Draw(overview)
    d.text((35,15),f'Grelha V3 — projeto A1 / PLA / {len(plates)} pratos',
           font=ImageFont.truetype(FONT,32),fill='#28383c')
    subtitle=('01: uma placa universal · 02: 26 presilhas padrão' if two_plates else
              '01–02: testar encaixe · 03–12: dez placas · 13: 26 presilhas padrão')
    d.text((35,65),subtitle,
           font=ImageFont.truetype(FONT,23),fill='#28383c')
    for i,thumb in enumerate(thumbs):
        if two_plates:
            overview.paste(thumb,(20+i*410,115))
        else:
            overview.paste(thumb.resize((330,363),Image.Resampling.LANCZOS),
                           (20+(i%4)*345,115+(i//4)*390))
    overview.save(preview_path)


def validate_project(path,two_plates=False):
    blobs,config,plates=read_project(path)
    assert len(plates)==(2 if two_plates else 13)
    assert [len(p['items']) for p in plates]==([1,26] if two_plates else [1]*12+[26])
    global_settings=json.loads(blobs['Metadata/project_settings.config'])
    assert global_settings['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert global_settings['filament_type']==['PLA']
    for key,value in {'layer_height':'0.2','wall_loops':'3','sparse_infill_density':'20%',
                      'sparse_infill_pattern':'gyroid','wall_generator':'arachne'}.items():
        assert global_settings[key]==value,(key,global_settings[key])
    volumes=[]
    for i,plate in enumerate(plates):
        boxes=[]
        for item in plate['items']:
            mesh=item['mesh']
            assert mesh.is_watertight and mesh.is_winding_consistent
            assert abs(mesh.bounds[0,2])<0.001
            assert np.all(mesh.bounds[0,:2]>=-0.001)
            assert np.all(mesh.bounds[1,:2]<=256.001)
            assert mesh.bounds[1,2]<256
            # Keep both objects and the outer brim clear of the A1 wrap zone.
            brim=0 if item['settings'].get('brim_type')=='no_brim' else 3
            low=mesh.bounds[0,:2]-brim
            high=mesh.bounds[1,:2]+brim
            assert np.all(low>=0) and np.all(high<=256)
            assert high[0]<226 or high[1]<224
            boxes.append(mesh.bounds[:,:2])
            if (i==0 if two_plates else 2<=i<=11):
                np.testing.assert_allclose(sorted(mesh.extents[:2]),[179.8,217.3],atol=0.0001)
                assert abs(mesh.extents[2]-30)<0.0001
                assert 'placa-universal' in item['settings']['name']
            if (i==1 if two_plates else i==1 or i==12):
                for key,val in {'layer_height':'0.16','wall_loops':'4',
                                'sparse_infill_density':'100%',
                                'sparse_infill_pattern':'alignedrectilinear',
                                'outer_wall_speed':'25','brim_type':'no_brim'}.items():
                    assert item['settings'].get(key)==val
                assert 'presilha-padrao' in item['settings']['name']
                assert abs(mesh.extents[2]-6.4)<0.0001
            volumes.append(mesh.volume)
        # Bounding boxes of rotated clips may touch, but must not overlap in XY.
        for a in range(len(boxes)):
            for b in range(a):
                overlap=np.minimum(boxes[a][1],boxes[b][1])-np.maximum(boxes[a][0],boxes[b][0])
                assert np.any(overlap<=0.001),'Overlapping objects on plate '+str(i+1)
        assert plate['properties']['thumbnail_file'] in blobs
    assert len(volumes)==(27 if two_plates else 38)
    # Native root thumbnail references must also have real targets.
    rels=ET.fromstring(blobs['_rels/.rels'])
    for rel in rels:
        assert rel.get('Target').lstrip('/') in blobs
    assert not any(n.endswith('.gcode') for n in blobs) # Editable, unsliced delivery.
    return plates


def run_cli(binary,args,log):
    with log.open('w') as output:
        result=subprocess.run([str(binary)]+args,stdout=output,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Bambu CLI failed ({result.returncode}); see {log}')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bambu-bin',type=Path,required=True)
    parser.add_argument('--profiles',type=Path,required=True)
    parser.add_argument('--work-dir',type=Path)
    parser.add_argument('--layout',choices=['13-pratos','2-pratos'],default='13-pratos')
    args=parser.parse_args()
    two_plates=args.layout=='2-pratos'
    target=(ROOT/'downloads/grelha-pintos-v3-A1-PLA-2-pratos.3mf') if two_plates else TARGET
    preview=ROOT/'designs'/('grelha-pintos-v3-PLA-2-pratos.png' if two_plates else
                          'grelha-pintos-v3-PLA-pratos.png')
    expected_layers=[150,40] if two_plates else [74,40]+[150]*10+[40]
    work=args.work_dir or Path(tempfile.mkdtemp(prefix='pintos-pla-3mf-'))
    work.mkdir(parents=True,exist_ok=True)
    for kind,name in [('machine','Bambu Lab A1 0.4 nozzle'),
                      ('process','0.20mm Standard @BBL A1'),
                      ('filament','Generic PLA @BBL A1')]:
        preset=flatten_profile(args.profiles,kind,name)
        changes=FOLDER/(kind+'-overrides.json')
        if changes.exists(): preset.update(json.loads(changes.read_text()))
        (work/(kind+'.json')).write_text(json.dumps(preset,indent=2)+'\n')
    (work/'assembly.json').write_text(json.dumps(assembly_plan(two_plates),indent=2)+'\n')
    common=['--datadir',str(work/'bambu-user'),'--debug','2']
    run_cli(args.bambu_bin,common+[
        '--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments',str(work/'filament.json'),
        '--load-assemble-list',str(work/'assembly.json'),'--orient','0','--arrange','1',
        '--outputdir',str(work),'--export-3mf','native-project.3mf'],work/'export.log')
    thumbnails(work/'native-project.3mf',target,preview)
    plates=validate_project(target,two_plates)
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(target)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0',
        '--outputdir',str(work/'slicing'),'--export-3mf','validation-only.3mf',str(target)],work/'slice.log')
    report=json.loads((work/'slicing/result.json').read_text())
    assert report['return_code']==0
    assert len(report['sliced_plates'])==len(plates)
    assert all(not p.get('warning_message') for p in report['sliced_plates'])
    # Each plate needs actual slicing/G-code evidence, not merely CLI exit 0.
    with ZipFile(work/'slicing/validation-only.3mf') as z:
        codes=[n for n in z.namelist() if n.endswith('.gcode')]
        assert len(codes)==len(plates)
        assert all(z.getinfo(n).file_size>10000 for n in codes)
        layer_counts=[]
        for index in range(1,len(plates)+1):
            text=z.read(f'Metadata/plate_{index}.gcode').decode()
            markers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',text)
            assert markers and markers[-1][0]==markers[-1][1]
            layer_counts.append(int(markers[-1][1]))
        assert layer_counts==expected_layers
    with ZipFile(target) as z:
        native_version=json.loads(z.read('Metadata/project_settings.config'))['version']
    result={
        'native_cli_version':native_version,
        'project_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'printer':'Bambu Lab A1 0.4 nozzle','material':'Generic PLA @BBL A1',
        'bed':'Textured PEI Plate','project_plates':len(plates),
        'project_objects':sum(len(p['items']) for p in plates),
        'native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
        'sliced_plates':len(plates),'slice_warnings':[],
        'actual_gcode_layer_counts':layer_counts,
        'delivery_is_editable_unsliced_project':True,
        'source_geometry':'V3 unchanged, standard clip only',
        'thumbnails':'overhead diagrams from the native exported geometry',
        'physical_PLA_clip_retention_tested':False,
        'plates':[{ 'id':i+1,'name':plates[i]['properties']['plater_name'],
                    'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
                    'estimated_seconds':p['total_predication'],
                    'objects':len(plates[i]['items'])}
                  for i,p in enumerate(report['sliced_plates'])]}
    validation_name='validation-2-pratos.json' if two_plates else 'validation.json'
    (FOLDER/validation_name).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f"Native 3MF: {len(plates)} plates, {result['project_objects']} objects.")
    print('PLA: export, reopen, bounds and ALL plate slicing passed.')
    print('Editable delivery contains settings/geometry/previews; no cached G-code.')


if __name__=='__main__': main()
