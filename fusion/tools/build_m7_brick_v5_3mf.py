"""Build, reopen and slice both M7 V5 plates with the official Bambu CLI."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import trimesh

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate
from generate_m7_brick_v5 import ROOT, FOLDER, PREFIX
import generate_m7_prototypes_v1 as v


def build(args):
    work=args.work_dir;work.mkdir(exist_ok=True,parents=True)
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'M7 V5 placa unica A1 0.20','from':'User','layer_height':'0.2',
        'initial_layer_print_height':'0.2','wall_loops':'3','sparse_infill_density':'15%',
        'sparse_infill_pattern':'gyroid','top_shell_layers':'5','bottom_shell_layers':'4',
        'top_shell_thickness':'1','top_surface_pattern':'monotonicline','wall_generator':'arachne',
        'wall_sequence':'outer wall/inner wall','outer_wall_speed':['50'],'inner_wall_speed':['100'],
        'outer_wall_acceleration':['2000'],'top_surface_acceleration':['1000'],
        'top_surface_speed':['25'],'initial_layer_speed':['20'],'initial_layer_infill_speed':['30'],
        'enable_support':['0'],'enable_prime_tower':'1','brim_type':'outer_only','brim_width':'3',
        'brim_object_gap':'0.15','elefant_foot_compensation':'0.1','interface_shells':'1',
        'flush_into_infill':'0','flush_into_support':'0','curr_bed_type':'Textured PEI Plate',
        'detect_thin_wall':'0'})
    process.pop('wall_infill_order',None)
    for name,data in [('machine',machine),('process',process)]:
        (work/f'{name}.json').write_text(json.dumps(data))
    colors=[v.ORANGE,v.GOLD,v.WHITE,v.CYAN];filaments=[]
    for i,col in enumerate(colors):
        silk=i==1
        data=flatten_profile(args.profiles,'filament','Generic PLA Silk @BBL A1' if silk else 'Generic PLA @BBL A1')
        data.update({'name':['SUNLU PLA+ laranja M7','PLA Silk dourado M7','PLA branco M7','PLA ciano M7'][i],
                     'from':'User','filament_colour':[col],'filament_max_volumetric_speed':['5' if silk else '8']})
        if silk:
            data.update({'nozzle_temperature':['215'],'nozzle_temperature_initial_layer':['215'],
                         'nozzle_temperature_range_low':['190'],'nozzle_temperature_range_high':['220']})
        path=work/f'filament-{i+1}.json';path.write_text(json.dumps(data));filaments.append(str(path))
    def obj(key,slot,assembly=None,params=None):
        result={'path':str(ROOT/'downloads'/f'{PREFIX}-{key}.stl'),'count':1,'filaments':[slot]}
        if assembly:result['assemble_index']=[assembly]
        if params:result['print_params']=params
        return result
    body={'wall_generator':'classic','wall_sequence':'outer wall/inner wall','outer_wall_speed':'50',
          'inner_wall_speed':'100','outer_wall_acceleration':'2000'}
    plan={'plates':[
        {'plate_name':'01 Corpo reforcado com moldura','need_arrange':True,
         'objects':[obj('corpo-reforcado',1,params=body)]},
        {'plate_name':'02 Placa unica - fundo laranja e relevos AMS','need_arrange':True,
         'objects':[obj('placa-laranja',1,1),obj('relevo-dourado',2,1),
                    obj('relevo-branco',3,1),obj('7-ciano',4,1)]}]}
    (work/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(work/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),
        '--load-filaments',';'.join(filaments),'--load-assemble-list',str(work/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(work),
        '--export-3mf','native.3mf'],work/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'
    native=annotate(work/'native.3mf',target,colors,PREFIX)
    data=json.loads((FOLDER/'geometry.json').read_text())
    refs=[trimesh.load(ROOT/'downloads'/p['file'],force='mesh') for p in data['parts']]
    remaining=[mesh for plate in native for key,col,mesh in plate]
    assert len(remaining)==len(refs)==5
    for ref in refs:
        matches=[m for m in remaining if abs(m.volume-ref.volume)<.12 and
                 np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.0003,atol=.1)]
        assert len(matches)==1
        actual=matches[0];remaining.pop(next(i for i,m in enumerate(remaining) if m is actual))
        assert actual.is_watertight
    blobs,settings,plates=read_project(target)
    assert len(plates)==2
    assert len(plates[0]['items'])==len(plates[1]['items'])==1
    for plate in plates:
        for item in plate['items']:
            mesh=item['mesh'];assert abs(mesh.bounds[0,2])<.001
            assert mesh.bounds[0,:2].min()>3 and mesh.bounds[1,:2].max()<253
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['wall_sequence']=='outer wall/inner wall'
    assert cfg['wall_generator']=='arachne'
    assert cfg['nozzle_temperature'][1]=='215'
    body_nodes=[o for o in settings.findall('object') if any(
        m.get('key')=='name' and 'corpo-reforcado' in m.get('value','') for m in o.findall('metadata'))]
    assert len(body_nodes)==1
    actual_body={m.get('key'):m.get('value') for m in body_nodes[0].findall('metadata')}
    assert all(actual_body.get(k)==value for k,value in body.items())
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(target)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(work/'slice'),
        '--export-3mf','validation.3mf',str(target)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==2
    reports=[]
    with ZipFile(work/'slice/validation.3mf') as z:
        for i,plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            layers=code.split('; CHANGE_LAYER')[1:]
            assert len(layers)==(350 if i==0 else 8)
            if i==0:assert plate['filament_change_times']==0
            else:
                assert plate['filament_change_times']>0
                for index,chunk in enumerate(layers[:3]):
                    assert abs(float(re.search(r'; Z_HEIGHT: ([\d.]+)',chunk)[1])-.2*(index+1))<.0001
                    assert not re.search(r'^T[123]\s*$',chunk,re.M)
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
        'layer_height_mm':.2,'body_settings':body,'plates':reports,
        'plaque_base_completed_before_relief_color_changes':True,
        'plaque_orange_only_base_layers':3,
        'total_estimated_seconds':sum(p['estimated_seconds'] for p in reports),
        'total_estimated_grams':sum(p['estimated_grams_including_flush_and_tower'] for p in reports),
        'physical_print_tested':False,'physical_fit_tested':False,'rib_marks_eliminated_confirmed':False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


def package():
    entries=list(FOLDER.iterdir())+list((ROOT/'downloads').glob(f'{PREFIX}-*.stl'))
    entries+=[ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf']
    entries+=list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    entries+=[Path(__file__),ROOT/'fusion/tools/generate_m7_brick_v5.py']
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
        for p in entries:
            name=('M7TijoloV5/'+p.name if p.parent==FOLDER else
                  'scripts/'+p.name if p.parent.name=='tools' else p.name)
            z.write(p,name)
        z.write(FOLDER/'README.md','LEIA-ME.md')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-v5'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    parser.add_argument('--package-only',action='store_true')
    args=parser.parse_args()
    if not args.package_only:build(args)
    if (FOLDER/'README.md').exists():package()
