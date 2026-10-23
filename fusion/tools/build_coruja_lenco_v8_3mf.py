"""Native A1 0.2 mm project for the scarf only: green first, brown once."""
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
from build_m7_prototypes_v1_3mf import annotate, plate_meshes
from generate_coruja_lenco_v8 import ROOT, FOLDER, PREFIX, GREEN, BROWN

def package():
    entries=list(FOLDER.glob('*'))
    for directory,pattern in [('downloads',f'{PREFIX}-*.stl'),('downloads',f'{PREFIX}-*.3mf'),
                              ('designs',f'{PREFIX}-*.png')]:
        entries+=list((ROOT/directory).glob(pattern))
    entries+=[ROOT/'downloads'/f'{PREFIX}-montado.glb',Path(__file__),
              ROOT/'fusion/tools/generate_coruja_lenco_v8.py']
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
        for p in entries:
            if p.is_file():z.write(p,p.name)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/coruja-lenco-v8'))
    parser.add_argument('--package-only',action='store_true');a=parser.parse_args()
    if a.package_only:package();return
    w=a.work_dir;w.mkdir(parents=True,exist_ok=True)
    bambu=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio')
    profiles=bambu.parent.parent/'resources/profiles/BBL'
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(bambu.parent)
    machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.2 nozzle')
    process=flatten_profile(profiles,'process','0.10mm Standard @BBL A1 0.2 nozzle')
    process.update({'name':'Lenco V8 A1 0.2 verde e no castanho no topo','from':'User',
        'layer_height':'0.1','initial_layer_print_height':'0.1','wall_loops':'3',
        'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag',
        'wall_generator':'arachne','top_shell_layers':'6','bottom_shell_layers':'5',
        'top_shell_thickness':'0.6','bottom_shell_thickness':'0.5',
        'top_surface_pattern':'monotonic','outer_wall_speed':['20'],
        'inner_wall_speed':['35'],'top_surface_speed':['15'],'small_perimeter_speed':['12'],
        'outer_wall_acceleration':['800'],'top_surface_acceleration':['500'],
        'initial_layer_speed':['15'],'initial_layer_infill_speed':['20'],
        'enable_support':['0'],'interface_shells':'1','ironing_type':'no ironing',
        'flush_into_infill':'0','flush_into_objects':'0','flush_into_support':'0',
        'enable_prime_tower':'1','prime_tower_width':'20','prime_tower_extra_rib_length':'0',
        'prime_tower_brim_width':'3','brim_type':'outer_only','brim_width':'2',
        'brim_object_gap':'0.15','elefant_foot_compensation':'0.1','resolution':'0.008',
        'curr_bed_type':'Textured PEI Plate'})
    for name,data in [('machine',machine),('process',process)]:
        (w/f'{name}.json').write_text(json.dumps(data))
    filaments=[]
    for i,color in enumerate([GREEN,BROWN]):
        f=flatten_profile(profiles,'filament','Generic PLA @BBL A1')
        f.update({'name':'Lenco PLA '+color,'from':'User','filament_colour':[color],
                  'filament_max_volumetric_speed':['1.5']})
        path=w/f'filament-{i}.json';path.write_text(json.dumps(f));filaments.append(str(path))
    data=json.loads((FOLDER/'geometry.json').read_text())
    plan={'plates':[{'plate_name':'LENCO V8 - verde e no castanho - bico 0.2',
        'need_arrange':True,'objects':[{'path':str(ROOT/'downloads'/p['file']),
        'count':1,'filaments':[i+1],'assemble_index':[1]} for i,p in enumerate(data['parts'])]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'user'),'--debug','2']
    run_cli(bambu,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',';'.join(filaments),'--load-assemble-list',str(w/'assembly.json'),
        '--allow-multicolor-oneplate','--orient','0','--arrange','1',
        '--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-bico-0.2-2-cores.3mf'
    annotate(w/'native.3mf',target,[GREEN,BROWN],PREFIX)
    blobs,settings,_=read_project(target)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert list(map(float,cfg['nozzle_diameter']))==[.2]
    assert float(cfg['layer_height'])==.1
    native=plate_meshes(blobs,settings)
    assert len(native)==1 and len(native[0])==2
    assert len(settings.findall('object'))==1
    for p in data['parts']:
        ref=trimesh.load(ROOT/'downloads'/p['file'],force='mesh')
        matches=[m for key,col,m in native[0] if abs(m.volume-ref.volume)<.001
                 and np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.001,atol=.001)]
        assert len(matches)==1 and matches[0].is_watertight
    assert abs(max(m.bounds[1,2] for _,_,m in native[0])-data['dimensions_mm'][2])<.001
    run_cli(bambu,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(bambu,common+['--slice','0','--orient','0','--arrange','0',
        '--outputdir',str(w/'slice'),'--export-3mf','validation.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==1
    p=result['sliced_plates'][0]
    assert p['filament_change_times']==1 and len(p['filaments'])==2
    assert not p.get('warning_message')
    with ZipFile(w/'slice/validation.3mf') as z:
        code=z.read('Metadata/plate_1.gcode').decode()
        assert '; FEATURE: Support' not in code
        layers=re.findall(r'; CHANGE_LAYER\n; Z_HEIGHT: ([\d.]+)\n; LAYER_HEIGHT: ([\d.]+)',code)
        assert len(layers)==round(data['dimensions_mm'][2]/.1) and all(abs(float(h)-.1)<1e-6 for _,h in layers)
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'bambu_version':'02.08.02.61','native_export_reopen_slice_ok':True,
        'nozzle_mm':.2,'layer_height_mm':.1,'filament_changes':p['filament_change_times'],
        'colors':2,'supports_generated':False,'warnings':p.get('warning_message'),
        'estimated_seconds':p['total_predication'],
        'estimated_main_grams':sum(f['main_used_g'] for f in p['filaments']),
        'estimated_total_grams':sum(f['total_used_g'] for f in p['filaments']),
        'physical_print_tested':False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    if (FOLDER/'README.md').exists():package()

if __name__=='__main__':main()
