"""Build and validate the 220 mm clinic sign on four A1 print plates."""
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

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli, NS
from build_m7_prototypes_v1_3mf import annotate
from generate_essencial_compacto_v5 import ROOT, FOLDER, PREFIX, WHITE, GREEN, GOLD, BLACK
import generate_m7_prototypes_v1 as v


def build(args):
    work=args.work_dir;work.mkdir(exist_ok=True,parents=True)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.16mm Optimal @BBL A1')
    process.update({'name':'Essencial Compacto V5 A1 0.16','from':'User','layer_height':'0.16',
        'initial_layer_print_height':'0.16','wall_loops':'3','sparse_infill_density':'15%',
        'sparse_infill_pattern':'gyroid','top_shell_layers':'5','bottom_shell_layers':'5',
        'top_shell_thickness':'1','top_surface_pattern':'monotonic','wall_generator':'arachne',
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
        data.update({'name':['PLA branco Essencial','PLA verde azeitona Essencial','PLA Silk dourado Essencial','PLA preto Essencial'][i],
                     'from':'User','filament_colour':[col],'filament_max_volumetric_speed':['5' if silk else '8'],
                     'filament_cost':[['13','16','20','16'][i]]})
        path=work/f'filament-{i+1}.json';path.write_text(json.dumps(data));filaments.append(str(path))
    def obj(key,slot,assembly=None,params=None):
        result={'path':str(ROOT/'downloads'/f"{PREFIX}-{key}{'-invertido' if key in ('base-verde','friso-dourado') else ''}.stl"),'count':1,'filaments':[slot]}
        if assembly:result['assemble_index']=[assembly]
        if params:result['print_params']=params
        return result
    base_params={'wall_loops':'3','sparse_infill_density':'15%','wall_generator':'classic','seam_position':'front','outer_wall_speed':'35','outer_wall_acceleration':'1000','top_surface_speed':'20','top_shell_layers':'5','top_shell_thickness':'0.8','bottom_shell_layers':'5','bottom_shell_thickness':'0.8','bridge_speed':'20','brim_type':'no_brim'}
    plan={'plates':[
        {'plate_name':'01 Frente branca - dourado e QR pretos','need_arrange':True,
         'objects':[obj('frente-branca',1,1),obj('letras-raposa-douradas',3,1),obj('qr-texto-preto',4,1)]},
        {'plate_name':'02 Fundo verde nervurado','need_arrange':True,
         'objects':[obj('fundo-nervurado-verde',2)]},
        {'plate_name':'03 Base INVERTIDA - verde depois dourado','need_arrange':True,
         'objects':[obj('base-verde',2,2,base_params),obj('friso-dourado',3,2,base_params)]},
        {'plate_name':'04 AMOSTRA primeiro - canto ranhuras e linguetas','need_arrange':True,
         'objects':[obj('amostra-verde',2,3,base_params),obj('amostra-dourado',3,3,base_params),
                    obj('amostra-linguetas',2,params=base_params)]}]}
    (work/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(work/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments',';'.join(filaments),'--load-assemble-list',str(work/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(work),
        '--export-3mf','native.3mf'],work/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf'
    native=annotate(work/'native.3mf',target,colors,PREFIX)
    data=json.loads((FOLDER/'geometry.json').read_text())
    refs=[trimesh.load(ROOT/'downloads'/p['file'],force='mesh') for p in data['parts']]
    refs += [trimesh.load(ROOT/'downloads'/f'{PREFIX}-{key}.stl',force='mesh') for key in ('amostra-verde','amostra-dourado','amostra-linguetas')]
    remaining=[mesh for plate in native for key,col,mesh in plate]
    assert len(remaining)==len(refs)==9
    for ref in refs:
        matches=[m for m in remaining if abs(m.volume-ref.volume)<.12 and
                 np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.0003,atol=.1)]
        assert len(matches)==1
        actual=matches[0];remaining.pop(next(i for i,m in enumerate(remaining) if m is actual))
        assert actual.is_watertight
    blobs,settings,plates=read_project(target)
    assert len(plates)==4
    assert [len(p['items']) for p in plates]==[1,1,1,2]
    for plate in plates:
        for item in plate['items']:
            mesh=item['mesh'];assert abs(mesh.bounds[0,2])<.001
            assert mesh.bounds[0,:2].min()>3 and mesh.bounds[1,:2].max()<253
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['wall_sequence']=='outer wall/inner wall'
    assert cfg['wall_generator']=='arachne'
    assert len(cfg['filament_colour'])==4
    body_nodes=[o for o in settings.findall('object') if any(
        m.get('key')=='name' and m.get('value') in ('assemble_2','assemble_3') for m in o.findall('metadata'))]
    assert len(body_nodes)==2
    actual_body={m.get('key'):m.get('value') for m in body_nodes[0].findall('metadata')}
    # Assembled input volumes inherit per-part settings from the CLI. Apply
    # the structural settings at the assembled object's level as well.
    for body_node in body_nodes:
        for key,value in base_params.items():
            node=body_node.find(f"metadata[@key='{key}']")
            if node is None:node=ET.SubElement(body_node,'metadata',key=key)
            node.set('value',value)
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    # The 0.16 mm purge tower has a different footprint. Reserve an explicit
    # clear side strip, including brim/ribs, instead of trusting auto-placement.
    model=ET.fromstring(blobs['3D/3dmodel.model'])
    first=model.find(f'{{{NS}}}build/{{{NS}}}item')
    original_transform=first.get('transform')
    transform=[float(n) for n in original_transform.split()]
    transform[9]+=250-plates[0]['items'][0]['mesh'].bounds[1,0]
    old_attribute=('transform="'+original_transform+'"').encode()
    new_attribute=('transform="'+' '.join(str(n) for n in transform)+'"').encode()
    assert blobs['3D/3dmodel.model'].count(old_attribute)==1
    # Preserve the native namespace declarations and requiredextensions="p".
    blobs['3D/3dmodel.model']=blobs['3D/3dmodel.model'].replace(old_attribute,new_attribute,1)
    cfg['wipe_tower_x'][0]='8';cfg['wipe_tower_y'][0]='15'
    blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for archive_path,value in blobs.items():z.writestr(archive_path,value)
    annotate(target,target,colors,PREFIX)
    _,_,placed=read_project(target)
    assert placed[0]['items'][0]['mesh'].bounds[0,0]>54
    assert placed[0]['items'][0]['mesh'].bounds[1,0]<253
    actual_body={m.get('key'):m.get('value') for m in body_nodes[0].findall('metadata')}
    assert all(actual_body.get(k)==value for k,value in base_params.items())
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(target)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(work/'slice'),
        '--export-3mf','validation.3mf',str(target)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==4
    reports=[]
    with ZipFile(work/'slice/validation.3mf') as z:
        for i,plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            layers=code.split('; CHANGE_LAYER')[1:]
            assert len(layers) in ([25],[26,27],[60],[60])[i]
            if i==1:assert plate['filament_change_times']==0
            elif i in (2,3):assert plate['filament_change_times']==1
            else:assert plate['filament_change_times']>0
            if i==0:
                for index,chunk in enumerate(layers[:23]):
                    assert abs(float(re.search(r'; Z_HEIGHT: ([\d.]+)',chunk)[1])-.16*(index+1))<.0001
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
        'layer_height_mm':.16,'base_settings':base_params,'base_print_orientation':'inverted; visible green face against plate','gold_last_six_layers':True,'plates':reports,
        'front_white_core_finished_before_color_changes':True,
        'front_white_only_initial_layers':23,
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
    entries+=[ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf']
    entries+=list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    entries+=[Path(__file__),ROOT/'fusion/tools/generate_essencial_compacto_v5.py',
              ROOT/'fusion/tools/verify_essencial_compacto_v5_qr.py',
              ROOT/'fusion/tools/verify_essencial_compacto_v5_base.py']
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
        for p in entries:
            name=('EssencialCompactoV5/'+p.name if p.parent==FOLDER else
                  'scripts/'+p.name if p.parent.name=='tools' else p.name)
            z.write(p,name)
        z.write(FOLDER/'README.md','LEIA-ME.md')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/essencial-compacto-v5'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    parser.add_argument('--package-only',action='store_true')
    args=parser.parse_args()
    if not args.package_only:build(args)
    if (FOLDER/'README.md').exists():package()
