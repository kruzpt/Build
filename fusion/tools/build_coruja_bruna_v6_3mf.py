"""Two A1 projects: four-color owl front, then three-color scarf and brown ring."""
import argparse
import ast
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
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from generate_coruja_bruna_v6 import ROOT, FOLDER, PREFIX, BROWN, CREAM, GOLD, BLACK, GREEN, WHITE


def build(a, accessory):
    kind='acessorios' if accessory else 'frente'
    colors=[BROWN,GREEN,BLACK] if accessory else [BROWN,WHITE,GOLD,BLACK]
    w=a.work_dir/kind;w.mkdir(parents=True,exist_ok=True)
    machine=flatten_profile(a.profiles,'machine','Bambu Lab A1 '+('0.4' if accessory else '0.2')+' nozzle')
    process=flatten_profile(a.profiles,'process','0.16mm Optimal @BBL A1' if accessory else '0.10mm Standard @BBL A1 0.2 nozzle')
    process.update({'name':'Coruja BRUNA '+kind+' A1 PLA 0.16','from':'User',
        'layer_height':'0.16','initial_layer_print_height':'0.16','wall_loops':'3',
        'sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','wall_generator':'arachne',
        'top_shell_layers':'6','bottom_shell_layers':'5','top_shell_thickness':'0.96',
        'bottom_shell_thickness':'0.8','top_surface_pattern':'monotonic',
        'outer_wall_speed':['35'],'inner_wall_speed':['70'],'top_surface_speed':['25'],
        'small_perimeter_speed':['20'],'bridge_speed':['20'],
        'outer_wall_acceleration':['1500'],'top_surface_acceleration':['1000'],
        'initial_layer_speed':['20'],'initial_layer_infill_speed':['30'],
        'enable_support':['0'],'interface_shells':'1','reduce_crossing_wall':'1',
        'flush_into_infill':'0','flush_into_objects':'0','flush_into_support':'0',
        'enable_prime_tower':'1','prime_tower_width':'25',
        'prime_tower_extra_rib_length':'0','prime_tower_brim_width':'3',
        'brim_type':'outer_only','brim_width':'2','brim_object_gap':'0.15',
        'elefant_foot_compensation':'0.1','resolution':'0.008',
        'curr_bed_type':'Textured PEI Plate'})
    if not accessory:
        process.update({'name':'Coruja BRUNA V6 A1 bico 0.2 - emblema em camadas',
            'layer_height':'0.1','initial_layer_print_height':'0.1','top_shell_thickness':'0.6',
            'bottom_shell_thickness':'0.5','outer_wall_speed':['20'],'inner_wall_speed':['35'],
            'top_surface_speed':['15'],'small_perimeter_speed':['12'],'bridge_speed':['15'],
            'outer_wall_acceleration':['800'],'top_surface_acceleration':['500'],
            'initial_layer_speed':['15'],'initial_layer_infill_speed':['20']})
    (w/'machine.json').write_text(json.dumps(machine));(w/'process.json').write_text(json.dumps(process))
    filaments=[]
    for i,color in enumerate(colors):
        data=flatten_profile(a.profiles,'filament','Generic PLA @BBL A1')
        data.update({'name':'Coruja PLA '+color,'from':'User','filament_colour':[color],
                     'filament_max_volumetric_speed':['6' if accessory else '1.5']})
        f=w/f'filament-{i+1}.json';f.write_text(json.dumps(data));filaments.append(str(f))
    data=json.loads((FOLDER/'geometry.json').read_text())
    parts={p['key']:p for p in data['parts']}
    def item(key,col,assembly=None,overrides=None):
        o={'path':str(ROOT/'downloads'/parts[key]['file']),'count':1,'filaments':[col]}
        if assembly:o['assemble_index']=[assembly]
        if overrides:o['print_params']=overrides
        return o
    if accessory:
        plan={'plates':[
            {'plate_name':'01 Anilha castanha - abertura 25 x 18 mm','need_arrange':True,
             'objects':[item('anilha-castanha',1,overrides={'wall_loops':'4','sparse_infill_density':'30%'})]},
            {'plate_name':'02 Lenco verde e no castanho - imprimir juntos','need_arrange':True,
             'objects':[item('lenco-verde',2,1,overrides={'sparse_infill_density':'100%'}),item('no-castanho',1,1),item('lenco-preto',3,1)]}]}
        name=f'{PREFIX}-ACESSORIOS-A1-bico-0.4-2-pratos.3mf'
    else:
        plan={'plates':[{'plate_name':'01 CORUJA COMPLETA - bico 0.2 - 50 mm','need_arrange':True,
            'objects':[item(key,i+1,1) for i,key in enumerate(['castanho','creme','dourado','preto'])]}]}
        name=f'{PREFIX}-CORUJA-A1-bico-0.2-4-cores.3mf'
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'user'),'--debug','2']
    run_cli(a.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',';'.join(filaments),'--load-assemble-list',str(w/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(w),
        '--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/'downloads'/name
    annotate(w/'native.3mf',target,colors,PREFIX+'-'+kind)
    blobs,settings,plates=read_project(target)
    if not accessory:
        assert len(settings.findall('object'))==1
        settings.find("object/metadata[@key='name']").set('value','CORUJA BRUNA V6 - COMPLETA - 50 mm')
        blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
        with ZipFile(target,'w',ZIP_DEFLATED) as z:
            for archive_path,value in blobs.items():z.writestr(archive_path,value)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert np.allclose(list(map(float,cfg['nozzle_diameter'])),[.4 if accessory else .2])
    assert abs(float(cfg['layer_height'])-(.16 if accessory else .1))<1e-7
    native=plate_meshes(blobs,settings)
    assert len(native)==(2 if accessory else 1)
    refs=[parts[k] for k in (['anilha-castanha','lenco-verde','no-castanho','lenco-preto'] if accessory else ['castanho','creme','dourado','preto'])]
    remaining=[m for plate in native for key,col,m in plate]
    assert len(remaining)==len(refs)
    for r in refs:
        ref=trimesh.load(ROOT/'downloads'/r['file'],force='mesh')
        matches=[m for m in remaining if abs(m.volume-ref.volume)<.05
             and np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.0002,atol=.1)]
        assert matches,r['key']
        m=matches[0];remaining.pop(next(i for i,other in enumerate(remaining) if other is m))
        assert m.is_watertight and m.is_winding_consistent
    for plate in native:
        assert len(set(col for key,col,m in plate))<=4
        for key,col,m in plate:
            assert m.bounds[0,:2].min()>0 and m.bounds[1,:2].max()<253
    if not accessory:
        assert abs(max(m.bounds[1,2] for key,col,m in native[0])-data['front_dimensions_mm'][2])<.02
        assert abs(min(m.bounds[0,2] for key,col,m in native[0]))<.001
    run_cli(a.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(a.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
        '--export-3mf','validation.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==len(native)
    report={'project':name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'bambu_version':'02.08.02.61','native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
        'physical_print_tested':False,'nozzle_mm':.4 if accessory else .2,'layer_height_mm':.16 if accessory else .1,'first_layer_height_mm':.16 if accessory else .1,'plates':[]}
    with ZipFile(w/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code and not p.get('warning_message')
            if accessory:
                assert p['filament_change_times']==0 if i==0 else p['filament_change_times']>0
            else:
                assert p['filament_change_times']>0 and len(p['filaments'])==4
                assert '; FEATURE: Outer wall' in code
                layers=re.findall(r'; CHANGE_LAYER\n; Z_HEIGHT: ([\d.]+)\n; LAYER_HEIGHT: ([\d.]+)',code)
                assert layers and all(abs(float(h)-.1)<1e-6 for _,h in layers)
                assert float(layers[-1][0])>=data['front_dimensions_mm'][2]-.11
            report['plates'].append({'id':i+1,'colors':len(p['filaments']),
                'filament_changes':p['filament_change_times'],'supports_generated':False,
                'warnings':p.get('warning_message'),'estimated_seconds':p['total_predication'],
                'estimated_main_grams':sum(f['main_used_g'] for f in p['filaments']),
                'estimated_grams':sum(f['total_used_g'] for f in p['filaments'])})
    report['estimated_total_seconds']=sum(p['estimated_seconds'] for p in report['plates'])
    report['estimated_total_grams']=sum(p['estimated_grams'] for p in report['plates'])
    (FOLDER/f'bambu-validation-{kind}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


def package():
    entries=list(FOLDER.glob('*'))
    entries+=list((ROOT/'downloads').glob(f'{PREFIX}-*.stl'))
    entries+=list((ROOT/'downloads').glob(f'{PREFIX}-*.3mf'))
    entries+=[ROOT/'downloads'/f'{PREFIX}-montada.glb']
    entries+=list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    entries+=[ROOT/'designs/anilha-coruja-bruna-v4-ilustracao.png']
    entries+=[ROOT/'fusion/tools/generate_coruja_bruna_v6.py',Path(__file__)]
    out=ROOT/'downloads'/f'{PREFIX}-pacote.zip'
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for p in entries:
            if p.is_file():z.write(p,p.name)
    with ZipFile(out) as z:assert z.testzip() is None


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/coruja-bruna-v6'))
    p.add_argument('--package-only',action='store_true');a=p.parse_args()
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
    if not a.package_only:
        build(a,False)
        build(a,True)
    if (FOLDER/'README.md').exists():package()


if __name__=='__main__':main()
