"""Build and validate the 220 mm clinic sign on three A1 print plates."""
import argparse
import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import trimesh

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate
from generate_essencial_arcos_220 import ROOT, FOLDER, PREFIX, WHITE, GREEN, GOLD, BLACK
import generate_m7_prototypes_v1 as v


def build(args):
    work=args.work_dir;work.mkdir(exist_ok=True,parents=True)
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'Essencial Arcos 220 A1 0.20','from':'User','layer_height':'0.2',
        'initial_layer_print_height':'0.2','wall_loops':'3','sparse_infill_density':'15%',
        'sparse_infill_pattern':'gyroid','top_shell_layers':'5','bottom_shell_layers':'5',
        'top_shell_thickness':'1','top_surface_pattern':'monotonicline','wall_generator':'arachne',
        'wall_sequence':'outer wall/inner wall','outer_wall_speed':['50'],'inner_wall_speed':['100'],
        'outer_wall_acceleration':['2000'],'top_surface_acceleration':['1000'],
        'top_surface_speed':['25'],'initial_layer_speed':['20'],'initial_layer_infill_speed':['30'],
        'enable_support':['0'],'enable_prime_tower':'1','brim_type':'outer_only','brim_width':'3',
        'brim_object_gap':'0.15','elefant_foot_compensation':'0.1','interface_shells':'1',
        'prime_tower_width':'30',
        'flush_into_infill':'0','flush_into_support':'0','curr_bed_type':'Textured PEI Plate',
        'detect_thin_wall':'0'})
    process.pop('wall_infill_order',None)
    for name,data in [('machine',machine),('process',process)]:
        (work/f'{name}.json').write_text(json.dumps(data))
    colors=[WHITE,GREEN,GOLD,BLACK];filaments=[]
    for i,col in enumerate(colors):
        silk=i==2
        data=flatten_profile(args.profiles,'filament','Generic PLA Silk @BBL A1' if silk else 'Generic PLA @BBL A1')
        data.update({'name':['PLA branco Essencial','PLA verde salvia Essencial','PLA Silk dourado Essencial','PLA preto Essencial'][i],
                     'from':'User','filament_colour':[col],'filament_max_volumetric_speed':['5' if silk else '8'],
                     'filament_cost':[['13','16','20','16'][i]]})
        if silk:
            data.update({'nozzle_temperature':['215'],'nozzle_temperature_initial_layer':['215'],
                         'nozzle_temperature_range_low':['190'],'nozzle_temperature_range_high':['220']})
        path=work/f'filament-{i+1}.json';path.write_text(json.dumps(data));filaments.append(str(path))
    def obj(key,slot,assembly=None,params=None):
        result={'path':str(ROOT/'downloads'/f'{PREFIX}-{key}.stl'),'count':1,'filaments':[slot]}
        if assembly:result['assemble_index']=[assembly]
        if params:result['print_params']=params
        return result
    base_params={'wall_loops':'4','sparse_infill_density':'25%','wall_generator':'classic'}
    plan={'plates':[
        {'plate_name':'01 Frente branca - dourado e QR pretos','need_arrange':True,
         'objects':[obj('frente-branca',1,1),obj('letras-raposa-douradas',3,1),obj('qr-texto-preto',4,1)]},
        {'plate_name':'02 Fundo verde nervurado','need_arrange':True,
         'objects':[obj('fundo-nervurado-verde',2)]},
        {'plate_name':'03 Base verde e friso dourado','need_arrange':True,
         'objects':[obj('base-verde',2,2,base_params),obj('friso-dourado',3,2,base_params)]}]}
    (work/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(work/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments',';'.join(filaments),'--load-assemble-list',str(work/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(work),
        '--export-3mf','native.3mf'],work/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf'
    native=annotate(work/'native.3mf',target,colors,PREFIX)
    data=json.loads((FOLDER/'geometry.json').read_text())
    refs=[trimesh.load(ROOT/'downloads'/p['file'],force='mesh') for p in data['parts']]
    remaining=[mesh for plate in native for key,col,mesh in plate]
    assert len(remaining)==len(refs)==6
    for ref in refs:
        matches=[m for m in remaining if abs(m.volume-ref.volume)<.12 and
                 np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.0003,atol=.1)]
        assert len(matches)==1
        actual=matches[0];remaining.pop(next(i for i,m in enumerate(remaining) if m is actual))
        assert actual.is_watertight
    blobs,settings,plates=read_project(target)
    assert len(plates)==3
    assert all(len(p['items'])==1 for p in plates)
    for plate in plates:
        for item in plate['items']:
            mesh=item['mesh'];assert abs(mesh.bounds[0,2])<.001
            assert mesh.bounds[0,:2].min()>3 and mesh.bounds[1,:2].max()<253
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['wall_sequence']=='outer wall/inner wall'
    assert cfg['wall_generator']=='arachne'
    assert cfg['nozzle_temperature'][2]=='215'
    body_nodes=[o for o in settings.findall('object') if any(
        m.get('key')=='name' and m.get('value')=='assemble_2' for m in o.findall('metadata'))]
    assert len(body_nodes)==1
    actual_body={m.get('key'):m.get('value') for m in body_nodes[0].findall('metadata')}
    # Assembled input volumes inherit per-part settings from the CLI. Apply
    # the structural settings at the assembled object's level as well.
    for key,value in base_params.items():
        node=body_nodes[0].find(f"metadata[@key='{key}']")
        if node is None:node=ET.SubElement(body_nodes[0],'metadata',key=key)
        node.set('value',value)
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,value in blobs.items():z.writestr(name,value)
    actual_body={m.get('key'):m.get('value') for m in body_nodes[0].findall('metadata')}
    assert all(actual_body.get(k)==value for k,value in base_params.items())
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(target)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(work/'slice'),
        '--export-3mf','validation.3mf',str(target)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==3
    reports=[]
    with ZipFile(work/'slice/validation.3mf') as z:
        for i,plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            layers=code.split('; CHANGE_LAYER')[1:]
            assert len(layers)==[24,21,60][i]
            if i==1:assert plate['filament_change_times']==0
            else:assert plate['filament_change_times']>0
            if i==0:
                for index,chunk in enumerate(layers[:16]):
                    assert abs(float(re.search(r'; Z_HEIGHT: ([\d.]+)',chunk)[1])-.2*(index+1))<.0001
                    assert not re.search(r'^T[23]\s*$',chunk,re.M)
            reports.append({'plate':i+1,'name':plan['plates'][i]['plate_name'],
                'estimated_seconds':plate['total_predication'],
                'estimated_grams_including_flush_and_tower':sum(f['total_used_g'] for f in plate['filaments']),
                'filament_changes':plate['filament_change_times'],'filaments':plate['filaments'],
                'warnings':plate.get('warning_message'),'supports':False,
                'layers':len(layers),
                'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'printer':'Bambu Lab A1 0.4 nozzle','bambu_version':'02.08.02.61',
        'native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
        'layer_height_mm':.2,'base_settings':base_params,'plates':reports,
        'front_white_core_finished_before_color_changes':True,
        'front_white_only_initial_layers':16,
        'total_estimated_seconds':sum(p['estimated_seconds'] for p in reports),
        'total_estimated_grams':sum(p['estimated_grams_including_flush_and_tower'] for p in reports),
        'physical_print_tested':False,'physical_fit_tested':False,'physical_qr_scan_tested':False}
    report['material_cost_eur_at_assumed_spool_prices']=sum(
        f['total_used_g']*[13,16,20,16][f['id']-1]/1000
        for plate in reports for f in plate['filaments'])
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


def package():
    entries=list(FOLDER.iterdir())+list((ROOT/'downloads').glob(f'{PREFIX}-*.stl'))
    entries+=[ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf']
    entries+=list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    entries+=[Path(__file__),ROOT/'fusion/tools/generate_essencial_arcos_220.py',
              ROOT/'fusion/tools/verify_essencial_arcos_qr_gcode.py']
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
        for p in entries:
            name=('EssencialArcos220/'+p.name if p.parent==FOLDER else
                  'scripts/'+p.name if p.parent.name=='tools' else p.name)
            z.write(p,name)
        z.write(FOLDER/'README.md','LEIA-ME.md')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/essencial-arcos-220'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    parser.add_argument('--package-only',action='store_true')
    args=parser.parse_args()
    if not args.package_only:build(args)
    if (FOLDER/'README.md').exists():package()
