"""Native A1/0.4 project for the wolf V5: three plates, quality at 0.12 mm.

Exports an editable 3MF, checks native meshes and slices all plates with the
installed Bambu Studio CLI. Does not send anything to a physical printer.
"""
import argparse,hashlib,json,os,re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np,trimesh
from build_pintos_pla_3mf import flatten_profile,read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/AnilhaLobitoV5'
PREFIX='anilha-lobito-v5-bochechas-continuas'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf'
COLORS=['#777B82','#F5F3ED','#191A1E']


def main(args):
    geo=json.loads((FOLDER/'geometry.json').read_text());parts={p['key']:p for p in geo['parts']}
    work=args.work_dir;work.mkdir(parents=True,exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    profiles=args.bambu_bin.parent.parent/'resources/profiles/BBL'
    machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(profiles,'process','0.12mm Fine @BBL A1')
    process.update({'name':'Lobito V5 arredondado A1 0.12','from':'User',
        'layer_height':'0.12','initial_layer_print_height':'0.2','wall_loops':'3',
        'sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
        'top_shell_layers':'6','top_shell_thickness':'0.72','bottom_shell_layers':'5','bottom_shell_thickness':'0.6',
        'top_surface_pattern':'monotonicline','wall_generator':'arachne',
        'outer_wall_speed':['30'],'inner_wall_speed':['50'],'small_perimeter_speed':['50%'],
        'overhang_1_4_speed':['30'],'overhang_2_4_speed':['25'],'overhang_3_4_speed':['15'],
        'overhang_4_4_speed':['10'],'overhang_totally_speed':['10'],'bridge_speed':['25'],
        'internal_solid_infill_speed':['45'],'top_surface_speed':['20'],
        'default_acceleration':['1000'],'outer_wall_acceleration':['800'],'top_surface_acceleration':['800'],
        'initial_layer_speed':['20'],'initial_layer_infill_speed':['25'],
        'enable_support':['0'],'support_on_build_plate_only':'1','support_type':'tree(auto)',
        'support_threshold_angle':'30','support_top_z_distance':'0.24','support_interface_top_layers':'2',
        'brim_type':'no_brim','brim_width':'0','elefant_foot_compensation':'0.1',
        'enable_prime_tower':'1','prime_tower_width':'30','flush_into_infill':'0','flush_into_support':'0',
        'seam_position':'back','ironing_type':'no ironing','resolution':'0.006',
        'curr_bed_type':'Textured PEI Plate'})
    settings=[]
    for name,cfg in [('machine',machine),('process',process)]:
        file=work/f'{name}.json';file.write_text(json.dumps(cfg));settings.append(str(file))
    filaments=[]
    for i,(color,label) in enumerate(zip(COLORS,['cinzento','branco','preto'])):
        f=flatten_profile(profiles,'filament','Generic PLA @BBL A1')
        f.update({'name':f'PLA {label} Lobito V5','from':'User','filament_colour':[color],
                  'filament_max_volumetric_speed':['8'],'filament_scarf_seam_type':['none']})
        file=work/f'filament-{i+1}.json';file.write_text(json.dumps(f));filaments.append(str(file))
    def obj(key,assembly=None,params=None):
        p=parts[key];o={'path':str(ROOT/'downloads'/p['file']),'count':1,'filaments':[p['slot']]}
        if assembly is not None:o['assemble_index']=[assembly]
        if params:o['print_params']=params
        return o
    bw=[];black=[];assembly=10
    for m in geo['modules']:
        if any(parts[k]['slot']==2 for k in m['parts']):
            assembly+=1
            bw.extend(obj(k,assembly) for k in m['parts'])
        else:black.extend(obj(k) for k in m['parts'])
    plan={'plates':[
        {'plate_name':'01 Corpo cinzento - 0.12 mm','need_arrange':True,
         'objects':[obj('corpo',params={'enable_support':'1'})]},
        {'plate_name':'02 Olhos focinho e orelhas - 0.12','need_arrange':True,'objects':bw},
        {'plate_name':'03 Nariz e sobrancelhas - 0.12','need_arrange':True,'objects':black}]}
    (work/'assembly.json').write_text(json.dumps(plan,indent=2))
    common=['--datadir',str(work/'user'),'--debug','2']
    print('native export',flush=True)
    run_cli(args.bambu_bin,common+['--load-settings',';'.join(settings),'--load-filaments',';'.join(filaments),
        '--load-assemble-list',str(work/'assembly.json'),'--allow-multicolor-oneplate','--orient','0','--arrange','1',
        '--outputdir',str(work),'--export-3mf','native.3mf'],work/'export.log')
    native=annotate(work/'native.3mf',TARGET,COLORS,PREFIX)
    remaining=[(c,m) for plate in native for _,c,m in plate];assert len(remaining)==len(parts)
    for key,p in parts.items():
        ref=trimesh.load(ROOT/'downloads'/p['file'],force='mesh')
        matches=[i for i,(c,m) in enumerate(remaining) if c==p['slot'] and abs(m.volume-ref.volume)<.2 and
                 np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.0005,atol=.2)]
        assert matches,(key,'native geometry mismatch')
        remaining.pop(matches[0])
    blobs,model,plates=read_project(TARGET)
    # Explicit parent filament prevents the slicer starting the two-colour
    # plate with an unused gray filament for the tower's first layer.
    for node in model.findall('object'):
        if node.find("metadata[@key='extruder']") is None:
            ET.SubElement(node,'metadata',key='extruder',value='2')
    blobs['Metadata/model_settings.config']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert cfg['layer_height']=='0.12'
    assert len(plates)==3 and [len(p['items']) for p in plates]==[1,5,3]
    for p in plates:
        for item in p['items']:
            m=item['mesh'];assert abs(m.bounds[0,2])<.002
            assert m.bounds[0,:2].min()>3 and m.bounds[1,:2].max()<253
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(TARGET)],work/'reopen.log')
    print('native slicing all three plates',flush=True)
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(work/'slice'),
        '--export-3mf','validation.3mf',str(TARGET)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text());assert result['return_code']==0
    assert len(result['sliced_plates'])==3
    reports=[]
    with ZipFile(work/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert not p.get('warning_message'),p.get('warning_message')
            assert '; FEATURE: Brim' not in code
            supports='; FEATURE: Support' in code
            if i!=0:assert not supports
            if i!=1:assert p['filament_change_times']==0
            layers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
            reports.append(dict(plate=i+1,name=plan['plates'][i]['plate_name'],objects=len(plates[i]['items']),
                estimated_seconds=p['total_predication'],estimated_grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']),
                filament_changes=p['filament_change_times'],warnings=p.get('warning_message'),
                support_toolpaths=supports,filaments=p['filaments'],layers=int(layers[-1][1]) if layers else None,
                gcode_sha256=hashlib.sha256(code.encode()).hexdigest()))
    report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        printer='Bambu Lab A1 0.4 nozzle',bambu_version=cfg['version'],native_export_exit=0,native_reopen_exit=0,native_slice_exit=0,
        native_components_match_source_STL=True,plate_object_counts=[1,5,3],layer_height_mm=.12,first_layer_height_mm=.2,
        brim=False,ironing=False,body_supports_enabled=True,detail_supports_enabled=False,plates=reports,
        total_seconds=sum(p['estimated_seconds'] for p in reports),
        total_grams=sum(p['estimated_grams_including_flush_and_tower'] for p in reports),
        generic_PLA_profiles_require_matching_actual_filament=True,physical_print_tested=False,physical_fit_tested=False)
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);main(p.parse_args())
