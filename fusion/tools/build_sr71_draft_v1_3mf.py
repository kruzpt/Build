"""Prepare, reopen and slice the actual SR-71 draft with official Bambu Studio."""
import argparse
import ast
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
from generate_sr71_draft_v1 import ROOT, FOLDER, PREFIX


def package():
    target=ROOT/'downloads'/f'{PREFIX}-A1-PLA-2-pratos.3mf'
    report=json.loads((FOLDER/'bambu-validation.json').read_text())
    assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
    entries={target.name:target,'LEIA-ME.md':FOLDER/'README.md'}
    for p in (ROOT/'downloads').glob(f'{PREFIX}-*.stl'):entries[p.name]=p
    glb=ROOT/'downloads'/f'{PREFIX}-montado.glb';entries[glb.name]=glb
    for p in FOLDER.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            entries['SR71DraftV1/'+str(p.relative_to(FOLDER))]=p
            entries['reproducao/fusion/SR71DraftV1/'+str(p.relative_to(FOLDER))]=p
    for p in (ROOT/'designs').glob(f'{PREFIX}-*.png'):entries['imagens/'+p.name]=p
    helpers=['build_sr71_draft_v1_3mf.py','generate_sr71_draft_v1.py','sr71_reference.py',
             'generate_universo_stand.py','generate_joana_topper.py','build_pintos_pla_3mf.py',
             'build_m7_prototypes_v1_3mf.py','generate_m7_prototypes_v1.py']
    for name in helpers:
        p=ROOT/'fusion/tools'/name
        ast.parse(p.read_text());entries['reproducao/fusion/tools/'+name]=p
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in entries.items()}
    result=ROOT/'downloads'/f'{PREFIX}-pacote.zip'
    with ZipFile(result,'w',ZIP_DEFLATED) as z:
        for n,p in entries.items():z.write(p,n)
        z.writestr('manifesto-sha256.json',json.dumps(hashes,indent=2)+'\n')
    with ZipFile(result) as z:
        assert z.testzip() is None
        for n,h in hashes.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    print('Package verified:',result.name,len(entries)+1,'files',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/sr71-v1-bambu'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    parser.add_argument('--package-only',action='store_true');args=parser.parse_args()
    if args.package_only:
        package();return
    w=args.work_dir;w.mkdir(exist_ok=True)
    extra=[Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu'),args.bambu_bin.parent]
    paths=[str(p) for p in extra if p.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):paths.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH']=':'.join(paths)
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.12mm High Quality @BBL A1')
    process.update({'name':'SR-71 draft V1 A1 PLA 0.12','from':'User',
        'layer_height':'0.12','initial_layer_print_height':'0.16',
        'wall_loops':'3','sparse_infill_density':'12%','sparse_infill_pattern':'gyroid',
        'top_shell_layers':'6','bottom_shell_layers':'5','top_shell_thickness':'0.72',
        'bottom_shell_thickness':'0.6','wall_generator':'arachne',
        'top_surface_pattern':'monotonicline','bottom_surface_pattern':'monotonic',
        'outer_wall_speed':['35'],'inner_wall_speed':['70'],'top_surface_speed':['25'],
        'initial_layer_speed':['20'],'initial_layer_infill_speed':['30'],
        'small_perimeter_speed':['25'],'bridge_speed':['20'],
        'outer_wall_acceleration':['1500'],'top_surface_acceleration':['1000'],
        'enable_support':['0'],'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15',
        'elefant_foot_compensation':'0.12','resolution':'0.008','seam_position':'aligned',
        'enable_prime_tower':'0','curr_bed_type':'Textured PEI Plate'})
    filament=flatten_profile(args.profiles,'filament','Generic PLA @BBL A1')
    filament.update({'name':'SR-71 PLA preto qualidade','from':'User',
        'filament_colour':['#24272C'],'filament_max_volumetric_speed':['6'],
        'nozzle_temperature':['215'],'nozzle_temperature_initial_layer':['220']})
    for name,data in [('machine',machine),('process',process),('filament',filament)]:
        (w/f'{name}.json').write_text(json.dumps(data))
    geometry=json.loads((FOLDER/'assembly.json').read_text())
    def item(part):
        result={'path':str(ROOT/'downloads'/part['file']),'count':1,'filaments':[1]}
        if part['key'].startswith(('cone','tubeira','cavilha','deriva')):
            result['print_params']={'sparse_infill_density':'100%',
                                    'brim_type':'outer_only','brim_width':'2'}
        return result
    plan={'plates':[
        {'plate_name':'01 SR-71 - metade superior - 0.12 mm','need_arrange':True,
         'objects':[item(p) for p in geometry['parts'] if p['key']=='superior']},
        {'plate_name':'02 SR-71 - metade inferior e detalhes - 0.12 mm','need_arrange':True,
         'objects':[item(p) for p in geometry['parts'] if p['key']!='superior']}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'bambu-user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',str(w/'filament.json'),'--load-assemble-list',str(w/'assembly.json'),
        '--orient','0','--arrange','1','--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-PLA-2-pratos.3mf'
    annotate(w/'native.3mf',target,['#24272C'],PREFIX)
    blobs,settings,plates=read_project(target)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert float(cfg['layer_height'])==.12 and float(cfg['initial_layer_print_height'])==.16
    assert len(plates)==2
    native=plate_meshes(blobs,settings)
    remaining=[m for plate in native for oid,color,m in plate]
    assert len(remaining)==len(geometry['parts'])
    for part in geometry['parts']:
        ref=trimesh.load(ROOT/'downloads'/part['file'],force='mesh')
        matches=[m for m in remaining if abs(m.volume-ref.volume)<.20 and
                 np.allclose(np.linalg.eigvalsh(m.moment_inertia),
                             np.linalg.eigvalsh(ref.moment_inertia),rtol=.0002,atol=.2)]
        assert matches,('Missing STL',part['key'])
        found=matches[0];remaining.pop(next(i for i,m in enumerate(remaining) if m is found))
        assert found.is_watertight and found.is_winding_consistent
    for plate in native:
        for oid,color,mesh in plate:
            assert mesh.bounds[0,:2].min()>=0 and mesh.bounds[1,:2].max()<253
            assert abs(mesh.bounds[0,2])<.001
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0',
        '--outputdir',str(w/'slicing'),'--export-3mf','validation-only.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slicing/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==2
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'printer':'Bambu Lab A1 0.4 nozzle','bambu_version':cfg['version'],
            'layer_height_mm':.12,'first_layer_height_mm':.16,'material':'Generic PLA black',
            'native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
            'physical_print_tested':False,'plates':[]}
    with ZipFile(w/'slicing/validation-only.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            assert p['filament_change_times']==0
            assert not p.get('warning_message'),p.get('warning_message')
            heights=[float(v) for v in re.findall(r'; CHANGE_LAYER\n; Z_HEIGHT: [0-9.]+\n; LAYER_HEIGHT: ([0-9.]+)',code)]
            markers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
            assert len(heights)==int(markers[-1][0])
            # An extremely small final tip can leave the slicer's nominal
            # total one above the last nonempty layer. Verify actual layers.
            assert int(markers[-1][1])-len(heights) in (0,1)
            assert abs(heights[0]-.16)<.00001
            assert np.allclose(heights[1:],.12,atol=.00001)
            report['plates'].append({'id':i+1,'objects':len(native[i]),'layers':len(heights),
                'nominal_total_layers_from_gcode':int(markers[-1][1]),
                'estimated_seconds':p['total_predication'],
                'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
                'filament_changes':0,'supports_generated':False,'warnings':[],
                'gcode_layer_heights_mm':[.12,.16],
                'model_layer_height_check':'First layer 0.16 mm; all subsequent model layers 0.12 mm, verified at CHANGE_LAYER markers'})
    report['total_seconds']=sum(p['estimated_seconds'] for p in report['plates'])
    report['total_grams']=sum(p['estimated_grams'] for p in report['plates'])
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    if (FOLDER/'README.md').exists():package()


if __name__=='__main__':
    main()
