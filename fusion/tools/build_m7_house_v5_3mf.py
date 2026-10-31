"""Prepare a single laminated house with different blue/white finishing rules."""
import argparse,hashlib,json,os,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np
import trimesh
from build_pintos_pla_3mf import flatten_profile,read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate
from generate_m7_house_v5 import ROOT,FOLDER,PREFIX
import generate_m7_prototypes_v1 as v


def inspect(code,window_boxes):
 z=0.;tool=0;feature='Custom';x=y=0.;feed=0.;layers={};finishes={};top_speeds=set()
 for line in code.splitlines():
  if line.startswith('; Z_HEIGHT:'):z=float(line.split(':')[1])
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  ch=re.match(r'^M620 S([0-2])A',line) or re.match(r'^T([0-2])\s*$',line)
  if ch:tool=int(ch[1])
  if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
  vals={a:float(b) for a,b in re.findall(r'([XYEF])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
  nx,ny=vals.get('X',x),vals.get('Y',y);feed=vals.get('F',feed)
  if z>0 and feature not in ('Custom','Prime tower') and vals.get('E',0)>0 and (nx,ny)!=(x,y):
   layers.setdefault(z,set()).add(tool)
   if abs(z-.8)<.0001 or abs(z-6)<.0001:finishes.setdefault(z,set()).add(feature)
   if abs(z-.8)<.0001 and feature=='Top surface':
    midpoint=np.array([(x+nx)/2,(y+ny)/2])
    assert any(np.all(midpoint>=box[0]-.5) and np.all(midpoint<=box[1]+.5) for box in window_boxes),'Blue top outside windows'
   if abs(z-6)<.0001 and feature=='Top surface':top_speeds.add(round(feed/60,4))
  x,y=nx,ny
 assert len(layers)==33
 assert all(t=={1} for z,t in layers.items() if z<=.80001)
 assert all(t=={0} for z,t in layers.items() if .80001<z<=6.00001)
 assert all(t=={1} for z,t in layers.items() if z>6.00001)
 assert 'Top surface' in finishes[.8],finishes
 assert 'Top surface' in finishes[6.]
 assert not {'Internal solid infill','Sparse infill'}&finishes[6.],finishes
 assert top_speeds=={25.}
 return {'material_slots_by_layer':{str(z):[t+1 for t in sorted(ts)] for z,ts in layers.items()},
  'blue_first_layers':4,'blue_last_z_mm':.8,'blue_transition_features':sorted(finishes[.8]),
  'blue_window_surfaces_finished':True,'covered_blue_has_no_top_finishing':True,'white_first_z_mm':1.,'white_last_z_mm':6.,
  'white_final_layer_features':sorted(finishes[6.]),'white_final_layer_has_internal_or_sparse_infill':False,
  'white_final_top_speed_mm_s':sorted(top_speeds),'phrase_first_z_mm':6.2,'phrase_top_mm':6.6,
  'white_fully_finished_before_phrase':True}


def build(args):
 w=args.work_dir;w.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
 machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
 process=flatten_profile(args.profiles,'process','0.20mm Standard @BBL A1')
 process.update({'name':'M7 Casa V5 unida 0.20','from':'User','layer_height':'0.2','initial_layer_print_height':'0.2',
  'wall_loops':'3','sparse_infill_density':'15%','sparse_infill_pattern':'gyroid','top_shell_layers':'5',
  'top_shell_thickness':'1','bottom_shell_layers':'4','top_surface_pattern':'monotonic','wall_generator':'arachne',
  'outer_wall_speed':['60'],'inner_wall_speed':['130'],'top_surface_speed':['35'],
  'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],'enable_support':['0'],
  'brim_type':'no_brim','brim_width':'0','brim_object_gap':'0.15','elefant_foot_compensation':'0.1',
  'interface_shells':'1','flush_into_infill':'0','flush_into_support':'0','enable_prime_tower':'1',
  'prime_tower_width':'30','curr_bed_type':'Textured PEI Plate','detect_thin_wall':'0','ironing_type':'no ironing'})
 for key,cfg in [('machine',machine),('process',process)]: (w/f'{key}.json').write_text(json.dumps(cfg))
 colors=[v.WHITE,v.BLUE,v.CYAN];filaments=[]
 for i,col in enumerate(colors):
  cfg=flatten_profile(args.profiles,'filament','Generic PLA @BBL A1')
  cfg.update({'name':['PLA branco M7','PLA azul M7','PLA ciano M7'][i],'from':'User','filament_colour':[col],
   'filament_max_volumetric_speed':['8']})
  path=w/f'filament-{i+1}.json';path.write_text(json.dumps(cfg));filaments.append(str(path))
 def obj(key,col,assembly=None,params=None):
  d={'path':str(ROOT/'downloads'/f'{PREFIX}-{key}.stl'),'count':1,'filaments':[col]}
  if assembly:d['assemble_index']=[assembly]
  if params:d['print_params']=params
  return d
 blue_params={'top_shell_layers':'0','top_shell_thickness':'0','bottom_shell_layers':'4','bottom_shell_thickness':'0.8',
  'internal_solid_infill_speed':'35'}
 white_params={'top_surface_pattern':'monotonic','top_surface_speed':'25','top_one_wall_type':'not apply',
  'outer_wall_speed':'50','outer_wall_acceleration':'1000','top_surface_acceleration':'1000'}
 plan={'plates':[
  {'plate_name':'01 Casa UNIDA - azul branco frase azul','need_arrange':True,'objects':[
   obj('fundo-azul-fino',2,1,blue_params),
   obj('acabamento-azul-janelas',2,1,{'top_shell_layers':'1','top_shell_thickness':'0.2','bottom_shell_layers':'0','bottom_shell_thickness':'0','top_surface_speed':'25'}),obj('fachada-branca',1,1,white_params),obj('frase-azul',2,1)]},
  {'plate_name':'02 Base azul - encaixes V2','need_arrange':True,'objects':[obj('base-azul',2,params={'wall_loops':'4','sparse_infill_density':'20%'})]},
  {'plate_name':'03 m branco original para colar','need_arrange':True,'objects':[obj('m-branco',1)]},
  {'plate_name':'04 7 ciano original para colar','need_arrange':True,'objects':[obj('7-ciano',3)]}]}
 (w/'assembly.json').write_text(json.dumps(plan))
 common=['--datadir',str(w/'user'),'--debug','2']
 run_cli(args.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
  '--load-filaments',';'.join(filaments),'--load-assemble-list',str(w/'assembly.json'),'--allow-multicolor-oneplate',
  '--orient','0','--arrange','1','--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
 target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf'
 native=annotate(w/'native.3mf',target,colors,PREFIX)
 data=json.loads((FOLDER/'geometry.json').read_text());remaining=[m for plate in native for k,c,m in plate]
 assert len(remaining)==7
 for part in data['parts']:
  source=trimesh.load(ROOT/'downloads'/part['file'],force='mesh')
  matches=[m for m in remaining if abs(m.volume-source.volume)<.15 and np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(source.moment_inertia),rtol=.0003,atol=.1)]
  assert len(matches)==1,part['key']
  actual=matches[0];remaining.pop(next(i for i,m in enumerate(remaining) if m is actual));assert actual.is_watertight
  if part['key']=='acabamento-azul-janelas':
   window_boxes=[m.bounds[:,:2] for m in actual.split()];assert len(window_boxes)==4
 blobs,settings,plates=read_project(target);assert len(plates)==4
 cfg=json.loads(blobs['Metadata/project_settings.config'])
 assert cfg['brim_type']=='no_brim'
 for node in settings.iter('metadata'):
  if node.get('key')=='brim_type':assert node.get('value')=='no_brim'

 for plate in plates:
  assert len(plate['items'])==1
  mesh=plate['items'][0]['mesh'];assert abs(mesh.bounds[0,2])<.001 and mesh.bounds[0,:2].min()>3 and mesh.bounds[1,:2].max()<253
 run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
 run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
  '--export-3mf','validation.3mf',str(target)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==4
 reports=[]
 with ZipFile(w/'slice/validation.3mf') as archive:
  for i,p in enumerate(result['sliced_plates']):
   assert not p.get('warning_message') and p['filament_change_times']==(2 if i==0 else 0)
   code=archive.read(f'Metadata/plate_{i+1}.gcode').decode();assert '; FEATURE: Support' not in code
   assert '; FEATURE: Brim' not in code
   if i==0:sequence=inspect(code,window_boxes)
   reports.append({'plate':i+1,'name':plan['plates'][i]['plate_name'],'estimated_seconds':p['total_predication'],
    'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),'filament_changes':p['filament_change_times'],
    'warnings':p.get('warning_message'),'supports':False,'brim':False,'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
 report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bambu_version':'02.08.02.61',
  'printer':'Bambu Lab A1 0.4 nozzle','brim_enabled':False,'layer_height_mm':.2,'blue_part_overrides':blue_params,
  'white_part_overrides':white_params,'native_reopen_exit':0,'native_slice_exit':0,
  'plates':reports,'house_sequence':sequence,'total_estimated_seconds':sum(p['estimated_seconds'] for p in reports),
  'total_estimated_grams':sum(p['estimated_grams'] for p in reports),'physical_print_tested':False,'physical_fit_tested':False}
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


def package():
 paths=list(FOLDER.iterdir())+list((ROOT/'downloads').glob(f'{PREFIX}-*.stl'))+list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
 paths+=[ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf',Path(__file__),ROOT/'fusion/tools/generate_m7_house_v5.py']
 with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
  for p in paths:
   name='M7CasaV5/'+p.name if p.parent==FOLDER else 'scripts/'+p.name if p.parent.name=='tools' else p.name
   z.write(p,name)
  z.write(FOLDER/'README.md','LEIA-ME.md')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-casa-v5-alinhada'))
 p.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
 p.add_argument('--profiles',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
 p.add_argument('--package-only',action='store_true');args=p.parse_args()
 if not args.package_only:build(args)
 if (FOLDER/'README.md').exists():package()
