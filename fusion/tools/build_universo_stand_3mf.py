"""Export, reopen and slice the actual two-plate A1/AMS stand with official CLI."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile,ZIP_DEFLATED

import numpy as np
from PIL import Image,ImageDraw,ImageFont
import trimesh

from build_pintos_pla_3mf import flatten_profile,read_project,run_cli,matrix,NS,PROD
from generate_universo_stand import ROOT,FOLDER,PREFIX,WHITE,BLUE

TARGET=ROOT/f'downloads/{PREFIX}-A1-AMS-2-pratos.3mf'


def meshes_by_plate(blobs,settings):
    main=ET.fromstring(blobs['3D/3dmodel.model']);cache={}
    builds={int(n.get('objectid')):matrix(n.get('transform'))
        for n in main.findall(f'{{{NS}}}build/{{{NS}}}item')}
    part_colors={}
    for o in settings.findall('object'):
        parent={n.get('key'):n.get('value') for n in o.findall('metadata')}
        for p in o.findall('part'):
            props={n.get('key'):n.get('value') for n in p.findall('metadata')}
            part_colors[int(p.get('id'))]=int(props.get('extruder',parent.get('extruder','1')))
    def walk(path,key,mat):
        if path not in cache:
            r=ET.fromstring(blobs[path]);cache[path]={int(o.get('id')):o for o in r.findall(f'{{{NS}}}resources/{{{NS}}}object')}
        o=cache[path][key];mesh=o.find(f'{{{NS}}}mesh')
        if mesh is not None:
            verts=np.array([[float(v.get(c)) for c in ('x','y','z')] for v in mesh.findall(f'{{{NS}}}vertices/{{{NS}}}vertex')])
            faces=np.array([[int(v.get(c)) for c in ('v1','v2','v3')] for v in mesh.findall(f'{{{NS}}}triangles/{{{NS}}}triangle')])
            m=trimesh.Trimesh(verts,faces,process=True);m.apply_transform(mat)
            return [(key,part_colors.get(key,1),m)]
        result=[]
        for c in o.findall(f'{{{NS}}}components/{{{NS}}}component'):
            other=c.get(f'{{{PROD}}}path',path).lstrip('/')
            result+=walk(other,int(c.get('objectid')),mat@matrix(c.get('transform')))
        return result
    result=[]
    for index,p in enumerate(settings.findall('plate')):
        items=[];origin=np.array([index*256*1.2,0,0])
        for inst in p.findall('model_instance'):
            props={m.get('key'):m.get('value') for m in inst.findall('metadata')}
            key=int(props['object_id'])
            placed=walk('3D/3dmodel.model',key,builds[key])
            for k,c,m in placed:m.apply_translation(-origin)
            items+=placed
        result.append(items)
    return result


def finish(source):
    blobs,settings,plates=read_project(source)
    assert len(plates)==2 and all(len(p['items'])==1 for p in plates)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    cfg['filament_colour']=[WHITE,BLUE]
    cfg['filament_multi_colour']=[WHITE,BLUE]
    blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    native=meshes_by_plate(blobs,settings)
    assert len(native[0])==2 and len(native[1])==1
    assert sorted(c for k,c,m in native[0])==[1,2]
    assert native[1][0][1]==2
    pictures=[]
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    for i,(plate,parts) in enumerate(zip(settings.findall('plate'),native)):
        image=Image.new('RGB',(520,590),'white');d=ImageDraw.Draw(image)
        d.rectangle((28,66,492,530),fill='#eceff2',outline='#939ba3',width=2)
        scale=464/256
        for key,extruder,m in sorted(parts,key=lambda p:p[2].bounds[0,2]):
            colour=[WHITE,BLUE][extruder-1]
            for face in m.triangles:
                d.polygon([(28+x*scale,530-y*scale) for x,y,z in face],fill=colour)
        d.text((24,17),'01 - Costas 200 mm / branco + azul' if i==0 else '02 - Base / apenas azul',font=font,fill=BLUE)
        d.text((24,548),'Geometria real / imprimir deitada',font=font,fill=BLUE)
        for path,size in [(f'Metadata/plate_{i+1}.png',image.size),(f'Metadata/plate_{i+1}_small.png',(128,145))]:
            stream=io.BytesIO();image.resize(size).save(stream,format='PNG');blobs[path]=stream.getvalue()
        item=plate.find("metadata[@key='thumbnail_file']")
        if item is None:item=ET.SubElement(plate,'metadata',key='thumbnail_file')
        item.set('value',f'Metadata/plate_{i+1}.png')
        pictures.append(image)
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    overview=Image.new('RGB',(1040,590),'white')
    for i,im in enumerate(pictures):overview.paste(im,(i*520,0))
    overview.save(ROOT/f'designs/{PREFIX}-pratos.png')
    return native


def package():
    target=ROOT/f'downloads/{PREFIX}-pacote.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for p in sorted(FOLDER.iterdir()):
            if p.is_file():z.write(p,'UniversoSaberStand/'+p.name)
        for p in sorted((ROOT/'downloads').glob(PREFIX+'-*.stl')):z.write(p,p.name)
        z.write(TARGET,TARGET.name)
        for p in sorted((ROOT/'designs').glob(PREFIX+'-*.png')):z.write(p,'imagens/'+p.name)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work-dir',type=Path,default=Path('/tmp/universo-bambu'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    a=parser.parse_args();w=a.work_dir;w.mkdir(exist_ok=True)
    for kind,name in [('machine','Bambu Lab A1 0.4 nozzle'),('process','0.20mm Standard @BBL A1')]:
        cfg=flatten_profile(a.profiles,kind,name)
        if kind=='process':cfg.update({'name':'Universo 200 mm - A1 PLA 0.20','from':'User',
            'wall_loops':'3','sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
            'layer_height':'0.2','initial_layer_print_height':'0.2',
            'top_shell_layers':'5','bottom_shell_layers':'4','top_shell_thickness':'1',
            'top_surface_pattern':'monotonicline','wall_generator':'arachne',
            'outer_wall_speed':['70'],'inner_wall_speed':['150'],
            'top_surface_speed':['40'],'initial_layer_speed':['30'],
            'initial_layer_infill_speed':['50'],'enable_support':['0'],
            'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15',
            'elefant_foot_compensation':'0.1','interface_shells':'1',
            'flush_into_infill':'0','flush_into_support':'0','enable_prime_tower':'1',
            'curr_bed_type':'Textured PEI Plate'})
        (w/(kind+'.json')).write_text(json.dumps(cfg))
    files=[]
    for i,col in enumerate((WHITE,BLUE)):
        p=flatten_profile(a.profiles,'filament','Generic PLA @BBL A1')
        p.update({'name':'Universo PLA '+('branco' if i==0 else 'azul'),'from':'User',
                  'filament_colour':[col],'filament_max_volumetric_speed':['8']})
        path=w/f'filament-{i+1}.json';path.write_text(json.dumps(p));files.append(str(path))
    def obj(name,extruder,assembly=None):
        r={'path':str(ROOT/f'downloads/{PREFIX}-{name}.stl'),'count':1,'filaments':[extruder]}
        if assembly:r['assemble_index']=[assembly]
        if name=='base-azul':r['print_params']={
            'enable_support':'1','support_type':'normal(auto)','support_style':'snug',
            'support_on_build_plate_only':'1','support_threshold_angle':'30',
            'support_top_z_distance':'0.2','support_bottom_z_distance':'0.2'}
        return r
    plan={'plates':[
        {'plate_name':'01 - Costas 200 mm - branco e azul','need_arrange':True,'objects':[
            obj('costas-branco',1,1),obj('relevos-azul',2,1)]},
        {'plate_name':'02 - Base - apenas azul','need_arrange':True,'objects':[obj('base-azul',2)]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'bambu-user'),'--debug','2']
    run_cli(a.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',';'.join(files),'--load-assemble-list',str(w/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(w),
        '--export-3mf','native.3mf'],w/'export.log')
    native=finish(w/'native.3mf')
    blobs,settings,plates=read_project(TARGET)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert cfg['filament_colour']==[WHITE,BLUE]
    expected=[trimesh.load(ROOT/f'downloads/{PREFIX}-{n}.stl',force='mesh')
              for n in ['costas-branco','relevos-azul','base-azul']]
    for plate,refs,items in zip(plates,[expected[:2],expected[2:]],native):
        m=plate['items'][0]['mesh']
        assert m.bounds[0].min()>-0.001 and np.all(m.bounds[1,:2]<253)
        for (_,extruder,actual),ref in zip(items,refs):
            assert actual.is_watertight
            assert abs(actual.volume-ref.volume)<0.1
            np.testing.assert_allclose(sorted(actual.extents),sorted(ref.extents),atol=0.01)
    run_cli(a.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(TARGET)],w/'reopen.log')
    run_cli(a.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slicing'),
        '--export-3mf','validation-only.3mf',str(TARGET)],w/'slice.log')
    result=json.loads((w/'slicing/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==2
    report={'printer':'Bambu Lab A1 0.4 nozzle','native_cli_version':cfg['version'],
        'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'layers_mm':0.2,
        'editable_unsliced_project':True,'native_export_exit':0,'native_reopen_exit':0,
        'native_slice_exit':0,'physical_fit_tested':False,'fusion_runtime_tested':False,
        'supports':'Only blue base: normal snug, build plate only, for the rear foot bevel',
        'plates':[]}
    with ZipFile(w/'slicing/validation-only.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            assert not p.get('warning_message'),p.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            markers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
            assert markers[-1]==(('34','34') if i==0 else ('50','50'))
            assert p['filament_change_times']==(1 if i==0 else 0),p['filament_change_times']
            if i==1:assert '; FEATURE: Support' in code
            report['plates'].append({'id':i+1,'filament_changes':p['filament_change_times'],
                'layers':int(markers[-1][1]),'estimated_seconds':p['total_predication'],
                'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
                'filaments':p['filaments'],'warnings':[]})
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    package();print(json.dumps(report,indent=2))


if __name__=='__main__':main()
