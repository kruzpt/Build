"""Build/reopen/slice A1 3MFs and inspect the real coplanar first-layer paths."""
import argparse,hashlib,json,os,sys,shutil
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from generate import FOLDER,ROOT,P,LID_R,BLACK,PURPLE,GOLD,DARK,WHITE
sys.path.insert(0,str(ROOT/'fusion/tools'))
from build_pintos_pla_3mf import flatten_profile,read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate,plate_meshes
from check_anilha_lobito_v5_toolpaths import paths


def build(args,mode):
    work=args.work_dir/mode;work.mkdir(parents=True,exist_ok=True)
    profiles=args.bambu_bin.parent.parent/'resources/profiles/BBL'
    colors=[BLACK,PURPLE,GOLD,DARK] if mode=='aneis-tonais' else [BLACK,PURPLE,GOLD] if mode=='vinil-3cores' else [WHITE] if mode=='corpo-branco' else [BLACK]
    machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'Caixa Maria vinil A1 PEI liso 0.20','from':'User','layer_height':'0.20','initial_layer_print_height':'0.20',
      'wall_loops':'3','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','top_shell_layers':'5','top_shell_thickness':'1.0',
      'bottom_shell_layers':'5','bottom_shell_thickness':'1.0','wall_generator':'arachne','bottom_surface_pattern':'concentric',
      'top_surface_pattern':'monotonicline','initial_layer_line_width':'0.42','outer_wall_line_width':'0.42',
      'inner_wall_line_width':'0.45','top_surface_line_width':'0.42','initial_layer_speed':['18'],'initial_layer_infill_speed':['20'],
      'outer_wall_speed':['35'],'inner_wall_speed':['65'],'top_surface_speed':['25'],'internal_solid_infill_speed':['50'],
      'small_perimeter_speed':['50%'],'bridge_speed':['20'],'overhang_1_4_speed':['30'],'overhang_2_4_speed':['25'],
      'overhang_3_4_speed':['20'],'overhang_4_4_speed':['15'],'default_acceleration':['1200'],'outer_wall_acceleration':['800'],
      'initial_layer_acceleration':['500'],'top_surface_acceleration':['700'],'enable_support':['0'],'brim_type':'no_brim','brim_width':'0',
      'elefant_foot_compensation':'0.15','enable_prime_tower':'1' if len(colors)>1 else '0','prime_tower_width':'25',
      'prime_tower_brim_width':'0','prime_tower_extra_rib_length':'0','flush_into_infill':'0','flush_into_objects':'0','flush_into_support':'0',
      'interface_shells':'1','reduce_crossing_wall':'1','seam_position':'back','ironing_type':'no ironing','resolution':'0.008',
      'curr_bed_type':'High Temp Plate'})
    settings=[]
    for key,obj in [('machine',machine),('process',process)]:
        f=work/f'{key}.json';f.write_text(json.dumps(obj));settings.append(str(f))
    filament_files=[]
    for i,c in enumerate(colors):
        if c==GOLD:
            obj=json.loads((ROOT/'downloads/amazon-basics-silk-pla-gold-09702-A1-04.json').read_text())
        else:
            obj=flatten_profile(profiles,'filament','Generic PLA @BBL A1')
            obj.update({'name':'Generic PLA '+['Preto','Roxo','Dourado','Cinzento escuro'][i]+' @BBL A1 0.4' if c!=WHITE else 'Generic PLA Branco @BBL A1 0.4','from':'User',
                        'filament_max_volumetric_speed':['8'],'filament_scarf_seam_type':['none']})
        obj.update({'filament_colour':[c],'hot_plate_temp':['55'],'hot_plate_temp_initial_layer':['55']})
        f=work/f'filament-{i+1}.json';f.write_text(json.dumps(obj));filament_files.append(str(f))
    keys=[]
    def item(name,color=1,assembly=False):
        keys.append((name,color))
        d={'path':str(FOLDER/'stl'/f'{name}.stl'),'count':1,'filaments':[color]}
        if assembly:
            d['assemble_index']=[1]
            if color in (2,3):d['print_params']={'bottom_surface_pattern':'monotonic'}
        return d
    if mode in ('vinil-3cores','aneis-tonais'):
        black='tampa-preto-aneis' if mode=='aneis-tonais' else 'tampa-preto'
        lid=[item(black,1,True),item('tampa-roxo',2,True),item('tampa-dourado',3,True)]
        if mode=='aneis-tonais':lid.append(item('tampa-aneis-tonais',4,True))
        plan={'plates':[{'plate_name':'01 Corpo liso preto - medidas provisorias','need_arrange':True,'objects':[item('corpo')]},
                        {'plate_name':'02 Tampa plana - face vinil contra PEI liso','need_arrange':True,'objects':lid}]}
    elif mode=='testes':
        plan={'plates':[{'plate_name':'01 Rosca: macho + femeas 0.25 0.30 0.40 mm','need_arrange':True,
                         'objects':[item(n) for n in ['teste-macho','teste-femea-025','teste-femea-030','teste-femea-040']]},
                        {'plate_name':'02 Amostra preta - acabamento concentrico','need_arrange':True,'objects':[item('amostra-acabamento')]}]}
    else:plan={'plates':[{'plate_name':'Corpo liso branco - opcional','need_arrange':True,'objects':[item('corpo')]}]}
    ap=work/'assembly.json';ap.write_text(json.dumps(plan,indent=2))
    common=['--datadir',str(work/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',';'.join(settings),'--load-filaments',';'.join(filament_files),
       '--load-assemble-list',str(ap),'--allow-multicolor-oneplate','--orient','0','--arrange','1','--outputdir',str(work),'--export-3mf','native.3mf'],work/'export.log')
    target=FOLDER/f'caixa-maria-v1-{mode}-A1-04-PEI-liso.3mf'
    prefix='bohemian-cookie-v1-'+mode
    native=annotate(work/'native.3mf',target,colors,prefix)
    image=ROOT/'designs'/f'{prefix}-pratos.png'
    shutil.move(str(image),FOLDER/'images'/f'{mode}-pratos.png')
    blobs,cfg,plates=read_project(target);pcfg=json.loads(blobs['Metadata/project_settings.config'])
    assert pcfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
    assert pcfg['curr_bed_type']=='High Temp Plate' and pcfg['bottom_surface_pattern']=='concentric'
    assert pcfg['brim_type']=='no_brim' and pcfg['layer_height']=='0.2'
    assert pcfg['filament_colour']==colors
    remaining=[(col,m) for plate in native for _,col,m in plate];fits={}
    for key,col in keys:
        ref=trimesh.load(FOLDER/'stl'/f'{key}.stl',force='mesh')
        matches=[(i,m) for i,(c,m) in enumerate(remaining) if c==col and np.array_equal(m.faces,ref.faces) and len(m.vertices)==len(ref.vertices) and abs(m.volume-ref.volume)<.05]
        assert len(matches)==1,(key,len(matches))
        i,m=matches[0];remaining.pop(i)
        fit=np.linalg.lstsq(np.c_[ref.vertices,np.ones(len(ref.vertices))],m.vertices,rcond=None)[0]
        error=float(np.max(np.linalg.norm(np.c_[ref.vertices,np.ones(len(ref.vertices))]@fit-m.vertices,axis=1)))
        assert error<.003 and np.allclose(fit[:3].T@fit[:3],np.eye(3),atol=.00001)
        assert m.is_watertight and m.bounds[0,:2].min()>0 and m.bounds[1,:2].max()<253 and m.bounds[0,2]>-.002
        if key.startswith('tampa-'):
            if 'lid' in fits:assert np.allclose(fit,fits['lid'],atol=.003)
            fits['lid']=fit
    assert not remaining
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(work/'reopen'),str(target)],work/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(work/'slice'),'--export-3mf','validation.3mf',str(target)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text());assert result['return_code']==0
    reviews=[];first_layer_check=None
    with ZipFile(work/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            rows=[r for r in paths(code) if r['feature']!='Prime tower']
            assert not p.get('warning_message'),p.get('warning_message')
            assert not any(r['feature'].startswith(('Support','Brim')) for r in rows)
            reviews.append({'plate':i+1,'name':plan['plates'][i]['plate_name'],'estimated_seconds':p['total_predication'],
                 'main_grams':sum(f['main_used_g'] for f in p['filaments']),'total_grams':sum(f['total_used_g'] for f in p['filaments']),
                 'filament_changes':p['filament_change_times'],'warnings':p.get('warning_message'),'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
            if i==1 and 'lid' in fits:
                pose=np.eye(4);pose[:3]=fits['lid'].T;inverse=np.linalg.inv(pose)
                first=[r for r in rows if abs(r['layer']-.2)<.0001]
                assert {r['tool'] for r in first}==set(range(1,len(colors)+1))
                for r in first:
                    pp=np.array(r['points']);r['points']=(np.c_[pp,np.ones(len(pp))]@inverse.T)[:,:3]
                gold=[LineString(r['points'][:,:2]) for r in first if r['tool']==3]
                assert gold
                gold_paths=unary_union(gold)
                gm=trimesh.load(FOLDER/'stl/tampa-dourado.stl',force='mesh')
                checks=[]
                for component in gm.split():
                    # Every disconnected letter, figure and central dot prints.
                    lo,hi=component.bounds[:,:2];region=Polygon([(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]).buffer(-.08)
                    length=gold_paths.intersection(region).length
                    assert length>.12,(lo,hi,length)
                    checks.append(length)
                tangent=total=0.
                for r in first:
                    if r['tool']!=1:continue
                    a=r['points'][:-1,:2];b=r['points'][1:,:2];mid=(a+b)/2;delta=b-a
                    radius=np.linalg.norm(mid,axis=1);length=np.linalg.norm(delta,axis=1)
                    use=(radius>P['label_diameter']/2+1)&(radius<LID_R-.5)&(length>1e-6)
                    dot=np.abs(np.sum(mid*delta,axis=1))/np.maximum(radius*length,1e-12)
                    total+=length[use].sum();tangent+=length[use&(dot<.15)].sum()
                assert total>100 and tangent/total>.95,(total,tangent)
                first_layer_check={'all_colors_on_layer_1':True,'gold_connected_components_printed':len(checks),
                     'gold_min_path_length_per_component_mm':min(checks),'black_annulus_tangential_fraction':tangent/total,
                     'black_annulus_path_mm':total,'coplanar_geometry':True,'physical_surface_effect_tested':False}
                draw_first(first,colors,mode)
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bambu_version':'02.09.01.70',
        'printer':'Bambu Lab A1 0.4 nozzle','plate':'Smooth PEI / High Temp Plate','layer_height_mm':.2,'supports':False,'brim':False,
        'native_export_reopen_slice_exit':[0,0,0],'source_meshes_colors_and_poses_verified':True,'first_layer':first_layer_check,
        'plates':reviews,'gold_profile':'Amazon Basics Silk PLA Gold 0.9702 @BBL A1 0.4' if len(colors)>1 else None,
        'physical_print_tested':False,'dimensions_provisional':True}
    (FOLDER/'validation'/f'bambu-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


def draw_first(rows,colors,mode):
    image=Image.new('RGB',(1800,1040),'#f4f3f0');d=ImageDraw.Draw(image)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    d.text((35,20),'Primeira camada real · Bambu Studio · '+mode,font=font(30),fill='#24222A')
    scale=9.5
    for i in range(2):
        for r in rows:
            p=r['points'][:,:2].copy()*scale
            p[:,1]*=(-1 if i==0 else 1);p+=np.array([450+i*900,500])
            d.line([tuple(x) for x in p],fill=colors[r['tool']-1],width=round(.42*scale))
        d.text((40+900*i,930),['Vista no prato · texto espelhado','Vista da face depois de virar'][i],font=font(28),fill='#24222A')
    d.text((35,990),'Percursos extrudidos; largura gráfica 0,42 mm. O brilho e as marcas no PEI exigem teste físico.',font=font(23),fill='#55515E')
    image.save(FOLDER/'images'/f'primeira-camada-{mode}.png')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--bambu-bin',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--mode',choices=['vinil-3cores','aneis-tonais','testes','corpo-branco'],required=True);args=ap.parse_args()
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    build(args,args.mode)
