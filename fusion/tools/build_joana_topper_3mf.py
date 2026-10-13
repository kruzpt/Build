"""Export, reopen and slice the four-part Joana topper with official Bambu CLI."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import flatten_profile,read_project,run_cli,matrix,NS,PROD
from generate_joana_topper import FOLDER,ROOT

TARGET=ROOT/'downloads/joana-topper-v1-A1-AMS-4-cores.3mf'
STEM='joana-topper-v1'
FUSION_DIRECTORY='JoanaTopper'


def configure(version):
    global FOLDER,TARGET,STEM,FUSION_DIRECTORY
    STEM='joana-topper-'+version
    FUSION_DIRECTORY='JoanaTopper' if version=='v1' else 'JoanaTopperV2'
    FOLDER=ROOT/'fusion'/FUSION_DIRECTORY
    TARGET=ROOT/'downloads'/f'{STEM}-A1-AMS-4-cores.3mf'


def package():
    with ZipFile(ROOT/f'downloads/{STEM}-pacote.zip','w',ZIP_DEFLATED) as z:
        for path in sorted(FOLDER.iterdir()):
            if path.is_file():z.write(path,FUSION_DIRECTORY+'/'+path.name)
        for path in sorted((ROOT/'downloads').glob(STEM+'-*.stl')):
            z.write(path,path.name)
        z.write(TARGET,TARGET.name)
        for name in ['joana-topper-conceito-v1.png',STEM+'-CAD.png',STEM+'-prato.png']:
            z.write(ROOT/'designs'/name,'imagens/'+name)


def native_parts(blobs):
    """Resolve transformed meshes of the native multipart object for its thumbnail."""
    model=ET.fromstring(blobs['3D/3dmodel.model'])
    build=model.find(f'{{{NS}}}build/{{{NS}}}item')
    cache={}
    def walk(path,objid,transform):
        if path not in cache:
            root=ET.fromstring(blobs[path])
            cache[path]={int(o.get('id')):o for o in root.findall(f'{{{NS}}}resources/{{{NS}}}object')}
        obj=cache[path][objid]
        mesh=obj.find(f'{{{NS}}}mesh')
        if mesh is not None:
            vertices=np.array([[float(v.get(c)) for c in ('x','y','z')]
                               for v in mesh.findall(f'{{{NS}}}vertices/{{{NS}}}vertex')])
            faces=np.array([[int(t.get(c)) for c in ('v1','v2','v3')]
                            for t in mesh.findall(f'{{{NS}}}triangles/{{{NS}}}triangle')])
            result=trimesh.Trimesh(vertices=vertices,faces=faces,process=True)
            result.apply_transform(transform)
            return [(objid,result)]
        result=[]
        for c in obj.findall(f'{{{NS}}}components/{{{NS}}}component'):
            next_path=c.get(f'{{{PROD}}}path',path).lstrip('/')
            result+=walk(next_path,int(c.get('objectid')),transform@matrix(c.get('transform')))
        return result
    return walk('3D/3dmodel.model',int(build.get('objectid')),matrix(build.get('transform')))


def finish_project(source):
    blobs,settings,plates=read_project(source)
    assert len(plates)==1 and len(plates[0]['items'])==1
    data=json.loads((FOLDER/'contours.json').read_text())
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    cfg['filament_colour']=[p['color'].upper() for p in data['parts']]
    blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    parts=settings.find('object').findall('part')
    assert len(parts)==4
    by_id={}
    for part,definition in zip(parts,data['parts']):
        props={m.get('key'):m.get('value') for m in part.findall('metadata')}
        expected_id=data['parts'].index(definition)+1
        assert int(props['extruder'])==expected_id,(props,expected_id)
        name=part.find("metadata[@key='name']")
        if name is not None:name.set('value',definition['name'])
        by_id[int(part.get('id'))]=definition['color']
    obj=settings.find('object')
    name=obj.find("metadata[@key='name']")
    if name is not None:name.set('value','Joana 12 - topper magico')
    # Render the actual native parts at their exported bed coordinates.
    im=Image.new('RGB',(450,510),'white');draw=ImageDraw.Draw(im)
    scale=400/256
    draw.rectangle((25,55,425,455),fill='#f3f0e9',outline='#8e9699',width=2)
    meshes=native_parts(blobs)
    assert set(k for k,m in meshes)==set(by_id),(set(k for k,m in meshes),set(by_id))
    for key,mesh in sorted(meshes,key=lambda pair:pair[1].bounds[0,2]):
        for triangle in mesh.triangles:
            draw.polygon([(25+x*scale,455-y*scale) for x,y,z in triangle],fill=by_id[key])
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    draw.text((20,14),'Joana 12 · A1 · AMS · quatro cores',font=font,fill='#282828')
    draw.text((20,475),'Contornos reais do projeto nativo',font=font,fill='#282828')
    for path,size in [('Metadata/plate_1.png',im.size),('Metadata/plate_1_small.png',(128,145))]:
        stream=io.BytesIO();im.resize(size,Image.Resampling.LANCZOS).save(stream,format='PNG')
        blobs[path]=stream.getvalue()
    plate=settings.find('plate')
    thumbnail=plate.find("metadata[@key='thumbnail_file']")
    if thumbnail is None:thumbnail=ET.SubElement(plate,'metadata',key='thumbnail_file')
    thumbnail.set('value','Metadata/plate_1.png')
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,value in blobs.items():z.writestr(name,value)
    im.save(ROOT/'designs'/f'{STEM}-prato.png')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bambu-bin',type=Path,required=True)
    parser.add_argument('--profiles',type=Path,required=True)
    parser.add_argument('--work-dir',type=Path)
    parser.add_argument('--version',choices=['v1','v2'],default='v1')
    args=parser.parse_args();configure(args.version)
    work=args.work_dir or Path('/tmp/'+STEM+'-bambu');work.mkdir(exist_ok=True)
    data=json.loads((FOLDER/'contours.json').read_text())
    for kind,name in [('machine','Bambu Lab A1 0.4 nozzle'),('process','0.20mm Standard @BBL A1')]:
        profile=flatten_profile(args.profiles,kind,name)
        if kind=='process':profile.update({
            'name':'Joana topper - A1 0.20 PLA AMS','from':'User',
            'wall_loops':'3','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid',
            'top_shell_layers':'5','bottom_shell_layers':'5','wall_generator':'arachne',
            'outer_wall_speed':['80'],'top_surface_speed':['40'],
            'enable_support':['0'],'brim_type':'no_brim',
            'initial_layer_speed':['30'],'elefant_foot_compensation':'0.1'})
        (work/(kind+'.json')).write_text(json.dumps(profile))
    filament_files=[];objects=[]
    for index,part in enumerate(data['parts']):
        preset=flatten_profile(args.profiles,'filament','Generic PLA @BBL A1')
        preset.update({'name':'Joana PLA '+part['name'],'from':'User',
                       'filament_colour':[part['color'].upper()]})
        path=work/f'filament-{index+1}.json';path.write_text(json.dumps(preset));filament_files.append(str(path))
        objects.append({'path':str(ROOT/f'downloads/{STEM}-{part["name"]}.stl'),
                        'count':1,'filaments':[index+1],'assemble_index':[1]})
    assembly={'plates':[{'plate_name':'Joana 12 - 4 cores AMS','need_arrange':True,'objects':objects}]}
    (work/'assembly.json').write_text(json.dumps(assembly))
    common=['--datadir',str(work/'bambu-user'),'--debug','2']
    run_cli(args.bambu_bin,common+[
        '--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments',';'.join(filament_files),'--load-assemble-list',str(work/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1',
        '--outputdir',str(work),'--export-3mf','native-project.3mf'],work/'export.log')
    finish_project(work/'native-project.3mf')
    blobs,config,plates=read_project(TARGET)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    mesh=plates[0]['items'][0]['mesh']
    assert np.all(mesh.bounds[0]>=-1e-3) and np.all(mesh.bounds[1,:2]<=256)
    # Arrangement can rotate in XY. Compare volumes and relative mass centers
    # instead of comparing axis-aligned bounds after rotation.
    placed=native_parts(blobs)
    reference=[trimesh.load(ROOT/f'downloads/{STEM}-{part["name"]}.stl',force='mesh')
               for part in data['parts']]
    for (_,actual),expected in zip(placed,reference):
        assert actual.is_watertight and actual.is_winding_consistent
        assert abs(actual.volume-expected.volume)<0.05
    actual_centers=np.array([m.center_mass for _,m in placed])
    source_centers=np.array([m.center_mass for m in reference])
    actual_distances=np.linalg.norm(actual_centers[:,None,:]-actual_centers[None,:,:],axis=2)
    source_distances=np.linalg.norm(source_centers[:,None,:]-source_centers[None,:,:],axis=2)
    np.testing.assert_allclose(actual_distances,source_distances,atol=0.001)
    assert abs(mesh.extents[2]-3.2)<0.001
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert cfg['filament_type']==['PLA']*4
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(TARGET)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0',
        '--outputdir',str(work/'slicing'),'--export-3mf','validation-only.3mf',str(TARGET)],work/'slice.log')
    report=json.loads((work/'slicing/result.json').read_text())
    assert report['return_code']==0 and len(report['sliced_plates'])==1
    p=report['sliced_plates'][0]
    assert not p.get('warning_message'),p.get('warning_message')
    assert len(p['filaments'])==4,p['filaments']
    with ZipFile(work/'slicing/validation-only.3mf') as z:
        code=z.read('Metadata/plate_1.gcode').decode()
        markers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
        assert markers[-1]==('16','16'),markers[-1]
        assert all(f'T{i}\n' in code or f'T{i} ' in code for i in range(4))
    stats={'native_cli_version':cfg['version'],'project_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
           'printer':'Bambu Lab A1 0.4 nozzle','filament_slots':cfg['filament_colour'],
           'plates':1,'assembled_objects':1,'color_parts':4,'layers':16,
           'native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
           'warnings':[],'extents_mm':mesh.extents.tolist(),'estimated_seconds':p['total_predication'],
           'estimated_filament_changes':p['filament_change_times'],
           'filaments':p['filaments'],'editable_unsliced_delivery':True,
           'fusion_runtime_tested':False,'physical_print_tested':False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
    package()
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
