"""Export, reopen, slice and inspect native Bambu A1 projects for M7 prototypes."""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli, matrix, NS, PROD
from generate_m7_prototypes_v1 import ROOT, FOLDER, WHITE, BLUE, CYAN, ORANGE, GOLD


def plate_meshes(blobs, settings):
    root=ET.fromstring(blobs['3D/3dmodel.model']);cache={};colors={}
    build={int(v.get('objectid')):matrix(v.get('transform')) for v in root.findall(f'{{{NS}}}build/{{{NS}}}item')}
    for o in settings.findall('object'):
        props={v.get('key'):v.get('value') for v in o.findall('metadata')}
        colors[int(o.get('id'))]=int(props.get('extruder','1'))
        for p in o.findall('part'):
            meta={v.get('key'):v.get('value') for v in p.findall('metadata')}
            colors[int(p.get('id'))]=int(meta.get('extruder',props.get('extruder','1')))
    def walk(path, key, tm):
        if path not in cache:
            model=ET.fromstring(blobs[path]);cache[path]={int(v.get('id')):v for v in model.findall(f'{{{NS}}}resources/{{{NS}}}object')}
        node=cache[path][key];mesh=node.find(f'{{{NS}}}mesh')
        if mesh is not None:
            vs=np.array([[float(v.get(c)) for c in ('x','y','z')] for v in mesh.findall(f'{{{NS}}}vertices/{{{NS}}}vertex')])
            fs=np.array([[int(v.get(c)) for c in ('v1','v2','v3')] for v in mesh.findall(f'{{{NS}}}triangles/{{{NS}}}triangle')])
            m=trimesh.Trimesh(vs,fs,process=True);m.apply_transform(tm)
            return [(key,colors.get(key,1),m)]
        result=[]
        for c in node.findall(f'{{{NS}}}components/{{{NS}}}component'):
            result+=walk(c.get(f'{{{PROD}}}path',path).lstrip('/'),int(c.get('objectid')),tm@matrix(c.get('transform')))
        return result
    plates=settings.findall('plate');cols=math.ceil(math.sqrt(len(plates)));result=[]
    for i,p in enumerate(plates):
        parts=[];origin=np.array([(i%cols)*307.2,-(i//cols)*307.2,0])
        for instance in p.findall('model_instance'):
            props={v.get('key'):v.get('value') for v in instance.findall('metadata')}
            key=int(props['object_id'])
            for oid,color,m in walk('3D/3dmodel.model',key,build[key]):
                m.apply_translation(-origin);parts.append((oid,color,m))
        result.append(parts)
    return result


def annotate(source,target,colours,prefix):
    blobs,settings,plates=read_project(source)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    cfg.update({'filament_colour':colours,'filament_multi_colour':colours})
    blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    native=plate_meshes(blobs,settings);thumbs=[]
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    for i,(p,parts) in enumerate(zip(settings.findall('plate'),native)):
        image=Image.new('RGB',(500,565),'white');d=ImageDraw.Draw(image)
        d.rectangle((25,65,475,515),fill='#e9edf0',outline='#9ca9b2',width=2)
        scale=450/256
        for key,col,m in sorted(parts,key=lambda v:v[2].bounds[0,2]):
            for tri in m.triangles:
                d.polygon([(25+x*scale,515-y*scale) for x,y,z in tri],fill=colours[col-1])
        title=plates[i]['properties']['plater_name']
        d.text((15,15),title,font=font,fill=BLUE)
        d.text((15,532),'Um protótipo · geometria real · A1 / 0,4 mm',font=font,fill=BLUE)
        for path,size in [(f'Metadata/plate_{i+1}.png',image.size),(f'Metadata/plate_{i+1}_small.png',(128,145))]:
            stream=io.BytesIO();image.resize(size).save(stream,format='PNG');blobs[path]=stream.getvalue()
        node=p.find("metadata[@key='thumbnail_file']")
        if node is None:node=ET.SubElement(p,'metadata',key='thumbnail_file')
        node.set('value',f'Metadata/plate_{i+1}.png');thumbs.append(image)
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for path,value in blobs.items():z.writestr(path,value)
    out=Image.new('RGB',(500*len(thumbs),565),'white')
    for i,im in enumerate(thumbs):out.paste(im,(i*500,0))
    out.save(ROOT/f'designs/{prefix}-pratos.png')
    return native


def build(product,args):
    w=args.work_dir/product;w.mkdir(parents=True,exist_ok=True)
    prefix=f'm7-{product}-v1';cols=[WHITE,BLUE,CYAN] if product=='casa' else [ORANGE,GOLD,WHITE,CYAN]
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'M7 prototipo A1 PLA 0.20','from':'User','layer_height':'0.2',
        'initial_layer_print_height':'0.2','wall_loops':'3','sparse_infill_density':'15%',
        'sparse_infill_pattern':'gyroid','top_shell_layers':'5','bottom_shell_layers':'4',
        'top_shell_thickness':'1','top_surface_pattern':'monotonicline','wall_generator':'arachne',
        'outer_wall_speed':['60'],'inner_wall_speed':['130'],'top_surface_speed':['35'],
        'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],'enable_support':['0'],
        'brim_type':'no_brim','elefant_foot_compensation':'0.1','interface_shells':'1',
        'flush_into_infill':'0','flush_into_support':'0','enable_prime_tower':'1',
        'curr_bed_type':'Textured PEI Plate','detect_thin_wall':'0'})
    (w/'machine.json').write_text(json.dumps(machine));(w/'process.json').write_text(json.dumps(process))
    fila=[]
    for i,col in enumerate(cols):
        gold=col==GOLD
        preset=flatten_profile(args.profiles,'filament','Generic PLA Silk @BBL A1' if gold else 'Generic PLA @BBL A1')
        preset.update({'name':'M7 '+('Silk dourado' if gold else 'PLA '+col),'from':'User',
            'filament_colour':[col],'filament_max_volumetric_speed':['5' if gold else '8']})
        if gold:preset.update({'nozzle_temperature':['215'],'nozzle_temperature_initial_layer':['215'],
                              'nozzle_temperature_range_low':['190'],'nozzle_temperature_range_high':['220']})
        path=w/f'filament-{i+1}.json';path.write_text(json.dumps(preset));fila.append(str(path))
    def obj(key,col,assembly=None,params=None):
        result={'path':str(ROOT/f'downloads/{prefix}-{key}.stl'),'count':1,'filaments':[col]}
        if assembly:result['assemble_index']=[assembly]
        if params:result['print_params']=params
        return result
    body_params={'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15'}
    if product=='casa':
        plan={'plates':[
            {'plate_name':'01 Casa - fachada e m branco','need_arrange':True,'objects':[
                obj('fachada-branca',1,1,body_params),obj('frase-azul',2,1),obj('m-branco',1)]},
            {'plate_name':'02 Casa - base e fundo azul','need_arrange':True,'objects':[
                obj('base-azul',2,params={**body_params,'wall_loops':'4','sparse_infill_density':'20%'}),
                obj('fundo-azul',2,params=body_params)]},
            {'plate_name':'03 Casa - 7 ciano para colar','need_arrange':True,'objects':[obj('7-ciano',3)]}]}
    else:
        gold_params={'outer_wall_speed':'35','top_surface_speed':'25','sparse_infill_density':'100%'}
        plan={'plates':[
            {'plate_name':'01 Tijolo - corpo terracota','need_arrange':True,'objects':[obj('tijolo-terracota',1,params=body_params)]},
            {'plate_name':'02 Tijolo - arvore e estrela','need_arrange':True,'objects':[
                obj('arvore-dourada',2,params=gold_params),obj('estrela-dourada',2,params=gold_params)]},
            {'plate_name':'03 Tijolo - m e Natal 2026','need_arrange':True,'objects':[
                obj('m-branco',3),obj('natal-branco',3)]},
            {'plate_name':'04 Tijolo - 7 ciano','need_arrange':True,'objects':[obj('7-ciano',4)]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'bambu-user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',';'.join(fila),'--load-assemble-list',str(w/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(w),
        '--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/f'downloads/{prefix}-A1-AMS-{len(plan["plates"])}-pratos.3mf'
    native=annotate(w/'native.3mf',target,cols,prefix)
    blobs,settings,plates=read_project(target)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert len(plates)==len(plan['plates'])
    # Match every exported native component to a source STL by actual volume/extents.
    source_entries=[p for p in json.loads((FOLDER/'geometry.json').read_text())['parts'] if p['product']==product]
    refs=[trimesh.load(ROOT/'downloads'/p['file'],force='mesh') for p in source_entries]
    actual=[m for plate in native for key,c,m in plate]
    assert len(actual)==len(refs)
    remaining=actual[:]
    for r in refs:
        # Arrange may rotate XY (notably the star); use rotation-invariant inertia.
        matches=[m for m in remaining if abs(m.volume-r.volume)<.12
                 and abs(m.extents[2]-r.extents[2])<.015
                 and np.allclose(np.linalg.eigvalsh(m.moment_inertia),
                                 np.linalg.eigvalsh(r.moment_inertia),rtol=.0002,atol=.1)]
        assert matches,('Missing source component',r.extents,r.volume)
        m=matches[0];remaining.pop(next(i for i,a in enumerate(remaining) if a is m))
        assert m.is_watertight and m.is_winding_consistent
    for p in plates:
        for item in p['items']:
            m=item['mesh'];assert m.bounds[0,:2].min()>=0 and m.bounds[1,:2].max()<253
            assert abs(m.bounds[0,2])<.001
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slicing'),
            '--export-3mf','validation-only.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slicing/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==len(plates)
    report={'product':product,'printer':'Bambu Lab A1 0.4 nozzle','version':cfg['version'],
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'layer_height_mm':.2,
        'project':target.name,'editable_unsliced_project':True,'native_export_exit':0,
        'native_reopen_exit':0,'native_slice_exit':0,'physical_print_tested':False,'plates':[]}
    with ZipFile(w/'slicing/validation-only.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            changes=p['filament_change_times'];assert changes==(1 if product=='casa' and i==0 else 0)
            markers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
            report['plates'].append({'id':i+1,'name':plan['plates'][i]['plate_name'],
                'filament_changes':changes,'layers':int(markers[-1][1]),
                'estimated_seconds':p['total_predication'],
                'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
                'filaments':p['filaments'],'warnings':p.get('warning_message',[]),'support_toolpaths':False})
    report['total_grams']=sum(p['estimated_grams'] for p in report['plates'])
    report['total_seconds']=sum(p['estimated_seconds'] for p in report['plates'])
    (FOLDER/f'bambu-validation-{product}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    return report


def package():
    reports=[json.loads((FOLDER/f'bambu-validation-{p}.json').read_text()) for p in ('casa','tijolo')]
    entries={}
    for r in reports:
        path=ROOT/'downloads'/r['project']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
        assert all(not p['warnings'] and not p['support_toolpaths'] for p in r['plates'])
        entries[path.name]=path
    for path in sorted((ROOT/'downloads').glob('m7-*-v1-*.stl')):entries[path.name]=path
    assert sum(name.endswith('.stl') for name in entries)==12
    report=json.loads((FOLDER/'geometry-validation.json').read_text())
    report.update({'bambu_slicing_verified':True,'supports_generated':False,
                   'stl_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in entries.values() if p.suffix=='.stl'}})
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for path in sorted(FOLDER.iterdir()):
        if path.is_file():entries['M7PrototiposV1/'+path.name]=path
    entries['LEIA-ME.md']=FOLDER/'README.md'
    for name in ('m7-prototipos-v1-CAD.png','m7-prototipos-v1-detalhes.png',
                 'm7-casa-v1-CAD-tras-lado.png','m7-casa-v1-pratos.png','m7-tijolo-v1-pratos.png'):
        entries['imagens/'+name]=ROOT/'designs'/name
    manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in entries.items()}
    target=ROOT/'downloads/m7-prototipos-v1-pacote.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,path in entries.items():z.write(path,name)
        z.writestr('manifesto-sha256.json',json.dumps(manifest,indent=2)+'\n')
    with ZipFile(target) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in manifest.items())
        assert not any('__pycache__' in name or name.startswith('/') or '..' in Path(name).parts for name in z.namelist())
    print('Package verified:',target.name,len(entries)+1,'entries',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--product',choices=['casa','tijolo','both'],default='both')
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-v1-bambu'))
    p.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    a=p.parse_args()
    # Optional existing AppImage extraction dependencies in this managed machine.
    extra=[Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu'),a.bambu_bin.parent]
    folders=[str(v) for v in extra if v.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):folders.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH']=':'.join(folders)
    for product in (['casa','tijolo'] if a.product=='both' else [a.product]):build(product,a)
    if all((FOLDER/f'bambu-validation-{p}.json').exists() for p in ('casa','tijolo')):package()


if __name__=='__main__':main()
