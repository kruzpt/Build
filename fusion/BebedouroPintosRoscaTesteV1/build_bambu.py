"""Create and slice the provisional bottle-thread coupon plate on Bambu A1."""
from pathlib import Path
from zipfile import ZipFile
import argparse, hashlib, json, os, sys
import trimesh

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[1]
sys.path.insert(0,str(ROOT/'fusion/tools'))
from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate
from check_anilha_lobito_v5_toolpaths import paths

COL='#258B95'
TARGET=FOLDER/'ensaio-rosca-garrafa-v1-A1-04-PLA.3mf'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,required=True)
    a=p.parse_args();a.work_dir.mkdir(parents=True,exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
    profiles=a.bambu_bin.parent.parent/'resources/profiles/BBL'
    machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(profiles,'process','0.16mm Optimal @BBL A1')
    process.update({'name':'Ensaio rosca garrafa A1 0.16','from':'User',
        'wall_loops':'3','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid',
        'enable_support':['0'],'brim_type':'no_brim','brim_width':'0',
        'elefant_foot_compensation':'0.15','curr_bed_type':'High Temp Plate',
        'initial_layer_speed':['20'],'initial_layer_infill_speed':['25'],
        'outer_wall_speed':['30'],'inner_wall_speed':['50']})
    filament=flatten_profile(profiles,'filament','Generic PLA @BBL A1')
    filament.update({'name':'Generic PLA @BBL A1','filament_colour':[COL],
                     'hot_plate_temp':['55'],'hot_plate_temp_initial_layer':['55']})
    for name,obj in [('machine',machine),('process',process),('filament',filament)]:
        (a.work_dir/f'{name}.json').write_text(json.dumps(obj))
    parts={}
    for name in 'ABCD':
        f=FOLDER/'stl'/f'anel-{name}.stl'
        m=trimesh.load(f,force='mesh')
        assert m.is_watertight and len(m.split())==1 and abs(m.extents[2]-12)<.01
        parts[name]={'path':str(f),'count':1,'filaments':[1]}
    # One ring per plate: the user can print B first without wasting the others.
    plan={'plates':[{'plate_name':f'Teste rosca - anel {name}',
                     'need_arrange':True,'objects':[parts[name]]}
                    for name in 'BACD']}
    assembly=a.work_dir/'assembly.json';assembly.write_text(json.dumps(plan,indent=2))
    common=['--datadir',str(a.work_dir/'user'),'--debug','2']
    run_cli(a.bambu_bin,common+[
      '--load-settings',str(a.work_dir/'machine.json')+';'+str(a.work_dir/'process.json'),
      '--load-filaments',str(a.work_dir/'filament.json'),
      '--load-assemble-list',str(assembly),'--orient','0','--arrange','1',
      '--outputdir',str(a.work_dir),'--export-3mf','native.3mf'],a.work_dir/'export.log')
    native=annotate(a.work_dir/'native.3mf',TARGET,[COL],'bebedouro-rosca-teste-v1')
    blobs,cfg,plates=read_project(TARGET)
    pcfg=json.loads(blobs['Metadata/project_settings.config'])
    assert pcfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert pcfg['brim_type']=='no_brim' and pcfg['curr_bed_type']=='High Temp Plate'
    assert len(plates)==4 and len(native)==4 and all(len(p)==1 for p in native)
    run_cli(a.bambu_bin,common+['--info','--outputdir',str(a.work_dir/'reopen'),str(TARGET)],a.work_dir/'reopen.log')
    run_cli(a.bambu_bin,common+['--slice','0','--orient','0','--arrange','0',
        '--outputdir',str(a.work_dir/'slice'),'--export-3mf','validation.3mf',str(TARGET)],a.work_dir/'slice.log')
    result=json.loads((a.work_dir/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==4
    reviews=[]
    with ZipFile(a.work_dir/'slice/validation.3mf') as z:
        for i,plate in enumerate(result['sliced_plates']):
            assert not plate.get('warning_message'),plate.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            rows=paths(code)
            assert not any(r['feature'].startswith(('Support','Brim')) for r in rows)
            reviews.append({'plate':i+1,'ring':'BACD'[i],
                'estimated_seconds':plate['total_predication'],
                'total_grams':sum(x['total_used_g'] for x in plate['filaments']),
                'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
    assert all(m.is_watertight for plate in native for _,_,m in plate)
    report={'project':TARGET.name,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
      'printer':'Bambu Lab A1 0.4 nozzle','profile':'0.16mm Optimal @BBL A1',
      'filament':'Generic PLA @BBL A1','plate':'Smooth PEI / High Temp Plate',
      'objects':['anel-A','anel-B','anel-C','anel-D'],
      'plates':reviews,'print_first':'plate 1, ring B',
      'no_slicer_warnings':True,'supports':False,'brim':False,
      'physical_fit_tested':False,'thread_profile_provisional':True}
    (FOLDER/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
