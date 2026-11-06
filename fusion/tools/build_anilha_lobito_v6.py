"""Quality revision of wolf V5: 0.08 mm colored modules, concentric fine tops.

Keep every mesh, assembly and flat glue back. Body remains at its verified
0.12 mm settings. Native slicing verifies actual paths, not physical quality.
"""
import argparse,hashlib,json,os,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
from build_pintos_pla_3mf import read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate,plate_meshes
from check_anilha_lobito_v5_toolpaths import paths

ROOT=Path(__file__).resolve().parents[2]
SOURCE_PREFIX='anilha-lobito-v5-bochechas-continuas'
PREFIX='anilha-lobito-v6-rosto-alta-qualidade'
SOURCE=ROOT/'downloads'/f'{SOURCE_PREFIX}-A1-AMS-3-pratos.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf'
FOLDER=ROOT/'fusion/AnilhaLobitoV6'
DETAIL_SETTINGS={
 'layer_height':'0.08','top_surface_pattern':'concentric',
 'top_surface_line_width':'0.36','top_shell_thickness':'1.0','top_shell_layers':'13',
 'outer_wall_speed':'20','inner_wall_speed':'30','internal_solid_infill_speed':'30',
 'top_surface_speed':'15','gap_infill_speed':'15',
 'overhang_1_4_speed':'20','overhang_2_4_speed':'20','overhang_3_4_speed':'15',
 'overhang_4_4_speed':'10','overhang_totally_speed':'10','bridge_speed':'20',
 'outer_wall_acceleration':'500','top_surface_acceleration':'500',
 'default_acceleration':'800'}


def archive(file):
 with ZipFile(file) as z:
  assert z.testzip() is None
  return {n:z.read(n) for n in z.namelist()}


def setmeta(node,key,value):
 item=node.find(f"metadata[@key='{key}']")
 if item is None:item=ET.SubElement(node,'metadata',key=key)
 item.set('value',str(value))


def slice_project(binary,source,work,plate='0'):
 work.mkdir(parents=True,exist_ok=True)
 run_cli(binary,['--datadir',str(work/'user'),'--debug','2','--slice',plate,'--orient','0','--arrange','0',
  '--outputdir',str(work/'slice'),'--export-3mf','validation.3mf',str(source)],work/'slice.log')
 result=json.loads((work/'slice/result.json').read_text());assert result['return_code']==0
 return result,archive(work/'slice/validation.3mf')


def top_width_review(sliced):
 result=[]
 for i in (2,3):
  feature='';width=None;values=[]
  for line in sliced[f'Metadata/plate_{i}.gcode'].decode().splitlines():
   if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
   if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1])
   if feature=='Top surface' and re.match(r'^G[123] ',line) and ' E' in line and (' X' in line or ' Y' in line):values.append(width)
  result.append(dict(plate=i,actual_top_nominal_widths_mm=sorted(set(values))))
 return result


def main(a):
 FOLDER.mkdir(exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
 original,config,source_plates=read_project(SOURCE);b=dict(original)
 cfg=json.loads(b['Metadata/project_settings.config']);before_cfg=dict(cfg)
 assert cfg['printer_settings_id']=='Bambu Lab A1 0.4 nozzle'
 # Thinner layers require a longer tower at each purge: place plate 2's tower
 # well inside the bed. Object geometry/placement and the other plates stay put.
 cfg['wipe_tower_y']=list(cfg['wipe_tower_y']);old_tower_y=cfg['wipe_tower_y'][1];cfg['wipe_tower_y'][1]='170'
 b['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
 detail_ids={p['id'] for plate in source_plates[1:] for p in plate['items']}
 old_body=next(o for o in config.findall('object') if int(o.get('id'))==source_plates[0]['items'][0]['id'])
 old_body=ET.canonicalize(ET.tostring(old_body,encoding='unicode'),strip_text=True)
 for node in config.findall('object'):
  if int(node.get('id')) in detail_ids:
   for key,value in DETAIL_SETTINGS.items():setmeta(node,key,value)
 config.findall('plate')[1].find("metadata[@key='plater_name']").set('value','02 Rosto e orelhas HQ - 0.08 mm')
 config.findall('plate')[2].find("metadata[@key='plater_name']").set('value','03 Nariz e sobrancelhas HQ - 0.08')
 b['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
 with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
  for name,data in b.items():z.writestr(name,data)
 annotate(TARGET,TARGET,cfg['filament_colour'],PREFIX)
 actual,settings,plates=read_project(TARGET)
 assert [len(p['items']) for p in plates]==[1,5,3]
 assert all(actual[n]==data for n,data in original.items() if n.startswith('3D/'))
 after_cfg=json.loads(actual['Metadata/project_settings.config']);expected=dict(before_cfg);expected['wipe_tower_y']=cfg['wipe_tower_y'];assert after_cfg==expected
 body=next(o for o in settings.findall('object') if int(o.get('id'))==source_plates[0]['items'][0]['id'])
 assert ET.canonicalize(ET.tostring(body,encoding='unicode'),strip_text=True)==old_body
 for n in settings.findall('object'):
  if int(n.get('id')) in detail_ids:
   for k,v in DETAIL_SETTINGS.items():assert n.find(f"metadata[@key='{k}']").get('value')==v
 for plate in plates:
  for item in plate['items']:
   assert abs(item['mesh'].bounds[0,2])<.002
   assert item['mesh'].bounds[0,:2].min()>3 and item['mesh'].bounds[1,:2].max()<253
 print('native reopen and slice',flush=True)
 run_cli(a.bambu_bin,['--datadir',str(a.work_dir/'reopen-user'),'--debug','2','--info','--outputdir',str(a.work_dir/'reopen'),str(TARGET)],a.work_dir/'reopen.log')
 result,sliced=slice_project(a.bambu_bin,TARGET,a.work_dir/'candidate')
 assert len(result['sliced_plates'])==3
 # A fresh baseline of the face provides matching-version estimates and paths.
 ref_result,ref_sliced=slice_project(a.bambu_bin,SOURCE,a.work_dir/'reference','2')
 reports=[];all_rows=[]
 for i,p in enumerate(result['sliced_plates']):
  assert not p.get('warning_message'),p.get('warning_message')
  code=sliced[f'Metadata/plate_{i+1}.gcode'].decode();rr=paths(code);all_rows.append(rr)
  heights=sorted(set(r['layer'] for r in rr));height=.12 if i==0 else .08
  assert abs(heights[0]-.2)<1e-6 and max(np.diff(heights))<=height+.00001
  assert '; FEATURE: Brim' not in code
  if i:assert '; FEATURE: Support' not in code
  tools=sorted(set(r['tool'] for r in rr));assert set(tools)<=({1} if i==0 else {2,3} if i==1 else {3})
  ow=[r['speed'] for r in rr if r['feature']=='Outer wall'];top=[r['speed'] for r in rr if r['feature']=='Top surface'];gaps=[r['speed'] for r in rr if r['feature']=='Gap infill']
  assert max(ow)<= (30 if i==0 else 20)+.001
  if top:assert max(top)<=(20 if i==0 else 15)+.001
  if i and gaps:assert max(gaps)<=15.001
  layers=re.findall(r'; layer num/total_layer_count: (\d+)/(\d+)',code)
  reports.append(dict(plate=i+1,name=plates[i]['properties']['plater_name'],layer_height_mm=height,
   first_extrusion_height_mm=heights[0],actual_maximum_layer_step_mm=float(max(np.diff(heights))),
   outer_wall_max_speed_mm_s=max(ow),top_surface_max_speed_mm_s=max(top) if top else None,
   gap_infill_max_speed_mm_s=max(gaps) if gaps else None,
   layers=int(layers[-1][1]),estimated_seconds=p['total_predication'],
   estimated_grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']),
   filament_changes=p['filament_change_times'],filaments=p['filaments'],warnings=p.get('warning_message'),
   supports='; FEATURE: Support' in code,gcode_sha256=hashlib.sha256(code.encode()).hexdigest()))
 # Source body params/geometry are identical; compare actual extrusion paths
 # when a prior verified native baseline is supplied.
 body_surface_paths_equal=None;body_extrusion_delta=None
 if a.reference_validation:
  source_codes=archive(a.reference_validation)
  source_body_rows=paths(source_codes['Metadata/plate_1.gcode'].decode())
  surface_features={'Outer wall','Inner wall','Top surface','Bottom surface','Bridge'}
  body_surface_paths_equal=[r for r in source_body_rows if r['feature'] in surface_features]==[r for r in all_rows[0] if r['feature'] in surface_features]
  assert body_surface_paths_equal,'Unexpected body surface path change'
  body_extrusion_delta=sum(r['extrusion_mm'] for r in all_rows[0])-sum(r['extrusion_mm'] for r in source_body_rows)
  # Native floating-shell fill can vary by numerical slivers between runs.
  # Cosmetic paths must match exactly; allow <0.01% total fill variation.
  assert abs(body_extrusion_delta)/sum(r['extrusion_mm'] for r in source_body_rows)<.0001,'Unexpected body fill change'
 baseline=ref_result['sliced_plates'][0]
 source_rows=paths(ref_sliced['Metadata/plate_2.gcode'].decode())
 data=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),source=SOURCE.name,
  bambu_version=cfg['version'],printer=cfg['printer_settings_id'],native_reopen_exit=0,native_slice_exit=0,
  all_geometry_and_assembly_bytes_identical=True,flat_backs_and_fit_geometry_preserved=True,
  body_settings_preserved=True,body_surface_extrusion_paths_identical=body_surface_paths_equal,body_total_extrusion_delta_vs_source_mm=body_extrusion_delta,
  detail_object_overrides=DETAIL_SETTINGS,
  purge_tower_plate_2_y_mm={'before':old_tower_y,'after':170},
  first_layer_height_mm=.2,global_body_layer_height_mm=.12,detail_layer_height_mm=.08,
  brim=False,ironing=False,plates=reports,
  total_estimated_seconds=sum(p['estimated_seconds'] for p in reports),
  total_estimated_grams=sum(p['estimated_grams_including_flush_and_tower'] for p in reports),
  face_reference=dict(seconds=baseline['total_predication'],grams=sum(f['total_used_g'] for f in baseline['filaments']),filament_changes=baseline['filament_change_times']),
  physical_print_tested=False,physical_finish_verified=False)
 data['top_width_review']=top_width_review(sliced)
 (FOLDER/'bambu-validation.json').write_text(json.dumps(data,indent=2)+'\n')
 preview(source_rows,all_rows[1],original)
 print(json.dumps(data,indent=2),flush=True)


def preview(before,after,blobs):
 # Map native XY positions back to the muzzle's unchanged printable axes.
 settings=ET.fromstring(blobs['Metadata/model_settings.config']);native=plate_meshes(blobs,settings)
 names={int(p.get('id')):p.find("metadata[@key='name']").get('value') for o in settings.findall('object') for p in o.findall('part')}
 key=next(k for k,n in names.items() if n.startswith(SOURCE_PREFIX+'-focinho-bochechas-branco_'))
 mesh=next(m for pl in native for k,c,m in pl if k==key)
 src=trimesh.load(ROOT/'downloads'/f'{SOURCE_PREFIX}-focinho-bochechas-branco.stl',force='mesh')
 tf=np.linalg.lstsq(np.c_[src.vertices,np.ones(len(src.vertices))],mesh.vertices,rcond=None)[0]
 matrix=np.eye(4);matrix[:3]=tf.T;inverse=np.linalg.inv(matrix)
 font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
 im=Image.new('RGB',(1520,1000),'#f4f6f8');d=ImageDraw.Draw(im)
 d.text((35,25),'Lobito V6 · camadas superiores do focinho',font=font(34),fill='#253549')
 d.text((35,80),'Mesma geometria · costas planas · contornos das camadas vistos de frente',font=font(23),fill='#526377')
 for j,(title,rows) in enumerate([('V5 · 0,12 mm',before),('V6 · 0,08 mm · topo concêntrico',after)]):
  x0=35+j*755;d.text((x0,150),title,font=font(25),fill='#253549')
  for r in rows:
   if r['feature'] not in ('Outer wall','Top surface') or r['tool'] not in (2,3) or r['layer']<9:continue
   pp=np.array(r['points']);mid=pp.mean(0)
   if not (np.all(mid[:2]>=mesh.bounds[0,:2]-.01) and np.all(mid[:2]<=mesh.bounds[1,:2]+.01)):continue
   local=np.c_[pp,np.ones(len(pp))]@inverse.T
   xy=[(x0+350+p[0]*30,820-p[1]*30) for p in local]
   c='#1c2430' if r['tool']==3 else '#5e758c' if j==0 else '#316d8e'
   if r['feature']=='Top surface':c='#b88c36'
   d.line(xy,fill=c,width=1)
 d.text((35,910),'Dourado: pequenos preenchimentos de topo · cinzento/azul: contornos exteriores',font=font(22),fill='#526377')
 d.text((35,952),'Percursos reais do G-code; a imagem não valida o acabamento físico da impressão.',font=font(21),fill='#526377')
 im.save(ROOT/'designs'/f'{PREFIX}-comparacao.png')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--reference-validation',type=Path);main(p.parse_args())
