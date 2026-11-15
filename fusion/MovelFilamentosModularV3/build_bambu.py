"""Build and validate a four-plate Bambu A1 PETG project for the connector."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'fusion/tools'))
from build_pintos_pla_3mf import flatten_profile,read_project

BBL=Path('/tmp/bambu-studio-2.9.1/squashfs-root/resources/profiles/BBL')
BIN=Path('/tmp/bambu-studio-2.9.1/squashfs-root/bin/bambu-studio')
WORK=Path('/tmp/movel-filamentos-v3-bambu')
TARGET=ROOT/'downloads/movel-filamentos-conector-v3-A1-PETG-4-pratos.3mf'

def run(args,log):
    env=os.environ.copy()
    env['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(BIN.parent)
    with (WORK/log).open('w') as f:
        proc=subprocess.run([str(BIN),'--datadir',str(WORK/'user'),'--debug','2',*args],
                            cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
    if proc.returncode:
        raise RuntimeError(f'Bambu Studio failed {proc.returncode}: {WORK/log}')

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    machine=flatten_profile(BBL,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(BBL,'process','0.20mm Strength @BBL A1')
    filament=flatten_profile(BBL,'filament','Generic PETG @BBL A1')
    process.update({
        'name':'Movel filamentos V3 PETG 0.20 A1', 'from':'User',
        'layer_height':'0.2','initial_layer_print_height':'0.2',
        'wall_loops':'5','top_shell_layers':'6','bottom_shell_layers':'6',
        'sparse_infill_density':'35%','sparse_infill_pattern':'gyroid',
        'enable_support':'0','brim_type':'no_brim','brim_width':'0',
        'curr_bed_type':'Textured PEI Plate',
        'outer_wall_speed':'40','initial_layer_speed':'20',
    })
    filament.update({'name':'Generic PETG @BBL A1','from':'User',
                     'filament_colour':['#2E7453']})
    for name,data in [('machine',machine),('process',process),('filament',filament)]:
        (WORK/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    def item(name,count=1):
        return {'path':str(HERE/'stl'/f'{name}.stl'),'count':count,'filaments':[1]}
    plan={'plates':[
        {'plate_name':'01 TESTE - 1 conector','need_arrange':True,
         'objects':[item('connector')]},
        {'plate_name':'02 TESTE - 1 pe','need_arrange':True,
         'objects':[item('foot')]},
        {'plate_name':'03 RESTANTES - 3 conectores','need_arrange':True,
         'objects':[item('connector',3)]},
        {'plate_name':'04 RESTANTES - 3 pes','need_arrange':True,
         'objects':[item('foot',3)]},
    ]}
    (WORK/'assembly.json').write_text(json.dumps(plan,indent=2)+'\n')
    run(['--load-settings',str(WORK/'machine.json')+';'+str(WORK/'process.json'),
         '--load-filaments',str(WORK/'filament.json'),
         '--load-assemble-list',str(WORK/'assembly.json'),
         '--orient','0','--arrange','1','--outputdir',str(WORK),
         '--export-3mf','native.3mf'],'export.log')
    TARGET.write_bytes((WORK/'native.3mf').read_bytes())
    with ZipFile(TARGET) as z:
        assert z.testzip() is None
        assert not any(n.endswith('.gcode') for n in z.namelist())
        cfg=json.loads(z.read('Metadata/project_settings.config'))
        assert cfg['printer_model']=='Bambu Lab A1'
        assert cfg['nozzle_diameter']==['0.4']
        assert cfg['enable_support']=='0'
        assert cfg['wall_loops']=='5'
    _,_,plates=read_project(TARGET)
    assert len(plates)==4
    assert [len(p['items']) for p in plates]==[1,1,3,3]
    for plate in plates:
        for obj in plate['items']:
            mesh=obj['mesh']
            assert mesh.is_watertight and mesh.is_winding_consistent
            assert abs(mesh.bounds[0,2])<.002
            assert mesh.bounds[0,:2].min()>=0
            assert mesh.bounds[1,:2].max()<=256
    slice_dir=WORK/'slice'
    slice_dir.mkdir(exist_ok=True)
    run(['--slice','0','--orient','0','--arrange','0',
         '--outputdir',str(slice_dir),'--export-3mf','sliced.3mf',str(TARGET)],'slice.log')
    report=json.loads((slice_dir/'result.json').read_text())
    assert report['return_code']==0
    assert len(report['sliced_plates'])==4
    assert all(not p['warning_message'] for p in report['sliced_plates'])
    validation={
        'project':TARGET.name,'printer':'Bambu Lab A1 0.4',
        'filament':'Generic PETG @BBL A1', 'hole_d_mm':22.7,
        'supports':False,'physical_fit_tested':False,'load_tested':False,
        'plates':[{'name':plan['plates'][i]['plate_name'],
                   'estimated_seconds':p['total_predication'],
                   'estimated_g':sum(x['total_used_g'] for x in p['filaments']),
                   'warnings':p['warning_message']}
                  for i,p in enumerate(report['sliced_plates'])],
    }
    (HERE/'bambu-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2),flush=True)

if __name__=='__main__':main()
