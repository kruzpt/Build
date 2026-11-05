"""Build and slice the grey body and keyed three-colour glue-on wolf face."""
import json, os, hashlib, argparse,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from build_pintos_pla_3mf import flatten_profile,run_cli,read_project
from build_m7_prototypes_v1_3mf import annotate
from generate_anilha_lobito_v1 import ROOT,PREFIX,FOLDER,COLORS


def main(args):
    w=args.work_dir;w.mkdir(parents=True,exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    profiles=args.bambu_bin.parent.parent/'resources/profiles/BBL'
    machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'Anilha Lobito V1 A1 0.16','from':'User','layer_height':'0.16','initial_layer_print_height':'0.2',
        'wall_loops':'3','sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
        'top_shell_layers':'5','bottom_shell_layers':'5','top_surface_pattern':'monotonicline',
        'wall_generator':'arachne','outer_wall_speed':['35'],'inner_wall_speed':['60'],
        'internal_solid_infill_speed':['50'],'top_surface_speed':['25'],
        'default_acceleration':['1000'],'outer_wall_acceleration':['1000'],'top_surface_acceleration':['1000'],
        'initial_layer_speed':['20'],'initial_layer_infill_speed':['30'],
        'enable_support':['1'],'support_on_build_plate_only':'1','support_threshold_angle':'45',
        'support_top_z_distance':'0.2','brim_type':'no_brim','brim_width':'0',
        'enable_prime_tower':'1','prime_tower_width':'35','flush_into_infill':'0',
        'flush_into_support':'0','curr_bed_type':'Textured PEI Plate'})
    paths=[]
    for name,obj in [('machine',machine),('process',process)]:
        path=w/f'{name}.json';path.write_text(json.dumps(obj));paths.append(str(path))
    filaments=[]
    for i,color in enumerate(COLORS):
        f=flatten_profile(profiles,'filament','Generic PLA @BBL A1')
        f.update({'name':['PLA cinzento Lobito','PLA branco Lobito','PLA preto Lobito'][i],
                  'from':'User','filament_colour':[color],'filament_max_volumetric_speed':['8'],
                  'filament_scarf_seam_type':['none']})
        path=w/f'filament-{i+1}.json';path.write_text(json.dumps(f));filaments.append(str(path))
    def obj(key,slot,assembly=None):
        d={'path':str(ROOT/'downloads'/f'{PREFIX}-{key}.stl'),'count':1,'filaments':[slot]}
        if assembly is not None:d['assemble_index']=[assembly]
        return d
    plan={'plates':[
      {'plate_name':'01 Corpo cinzento - abertura oval 25 x 18','need_arrange':True,'objects':[obj('corpo',1)]},
      {'plate_name':'02 Rosto AMS com guia para colar','need_arrange':True,
       'objects':[obj(key,i+1,1) for i,key in enumerate(('rosto-cinzento','rosto-branco','rosto-preto'))]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',';'.join(paths),'--load-filaments',';'.join(filaments),
        '--load-assemble-list',str(w/'assembly.json'),'--allow-multicolor-oneplate','--orient','0','--arrange','1',
        '--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'
    annotate(w/'native.3mf',target,COLORS,PREFIX)
    blobs,settings,plates=read_project(target)
    for node in settings.findall('object'):
        body=any('corpo' in m.get('value','') for m in node.findall('part/metadata') if m.get('key')=='name')
        element=ET.SubElement(node,'metadata',key='enable_support',value='0' if body else '1')
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    assert len(plates)==2 and all(len(p['items'])==1 for p in plates)
    for p in plates:
        mesh=p['items'][0]['mesh'];assert abs(mesh.bounds[0,2])<.001
        assert mesh.bounds[0,:2].min()>3 and mesh.bounds[1,:2].max()<253
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
        '--export-3mf','validation.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0
    reports=[]
    with ZipFile(w/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            assert not p.get('warning_message'),p.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Brim' not in code
            if i==0:assert '; FEATURE: Support' not in code
            else:assert '; FEATURE: Support' in code
            reports.append({'plate':i+1,'estimated_seconds':p['total_predication'],
                'estimated_grams_including_flush_and_tower':sum(f['total_used_g'] for f in p['filaments']),
                'filament_changes':p['filament_change_times'],'warnings':p.get('warning_message'),
                'filaments':p['filaments']})
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'native_slice_exit':0,'printer':'Bambu Lab A1 0.4 nozzle','bambu_version':'02.09.01.70',
        'layer_height_mm':.16,'brim':False,'supports':'Only face back overhangs on plate2','plates':reports,
        'generic_PLA_profiles_require_matching_actual_filament':True,
        'opening_reused_from_owl_mm':[25,18],'body_height_proposed_mm':30,
        'physical_print_tested':False,'physical_fit_tested':False}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True)
    main(p.parse_args())
