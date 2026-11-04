"""Continuous orange plaque finish and gentler perimeter acceleration; V6 geometry."""
import argparse,hashlib,json,os,re,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np,trimesh
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw,ImageFont
from build_pintos_pla_3mf import read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate
import generate_m7_prototypes_v1 as v
ROOT=v.ROOT;FOLDER=ROOT/'fusion/M7TijoloAcabamentoV7';PREFIX='m7-tijolo-v7-acabamento'
SOURCE=ROOT/'downloads/m7-tijolo-v6-folga-A1-AMS-2-pratos.3mf'
OVERRIDES={'top_one_wall_type':'not apply','outer_wall_acceleration':'1000'}


def analyse(code,source,target,label):
 tree=cKDTree(target.vertices);match=None
 for angle in (0,np.pi/2,np.pi,3*np.pi/2):
  rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
  points=source.vertices@rot.T;shift=(target.bounds[0]+target.bounds[1]-points.min(0)-points.max(0))/2
  if tree.query(points+shift)[0].max()<.003:match=(rot,shift);break
 assert match is not None
 rot,shift=match;z=0.;tool=0;feature='Custom';x=y=0.;acc=0;feed=0;layers={};counts={};paths=[];outer_acc=set();top_speeds=set()
 for line in code.splitlines():
  if line.startswith('; Z_HEIGHT:'):z=float(line.split(':')[1])
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  change=re.match(r'^M620 S([0-3])A',line) or re.match(r'^T([0-3])\s*$',line)
  if change:tool=int(change[1])
  ac=re.match(r'^M204 S([\d.]+)',line)
  if ac:acc=float(ac[1])
  if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
  vals={a:float(b) for a,b in re.findall(r'([XYEF])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
  nx,ny=vals.get('X',x),vals.get('Y',y);feed=vals.get('F',feed)
  if z>0 and vals.get('E',0)>0 and (nx,ny)!=(x,y) and feature not in ('Custom','Prime tower'):
   layers.setdefault(z,set()).add(tool+1)
   if feature=='Outer wall' and z>.20001:outer_acc.add(acc)
   if abs(z-.6)<.0001 and tool==0:
    p=(np.array([x,y,z])-shift)@rot;q=(np.array([nx,ny,z])-shift)@rot;mid=(p[:2]+q[:2])/2
    if -20.5<mid[0]<20.5 and 4.5<mid[1]<65.5:
     counts[feature]=counts.get(feature,0)+1;paths.append((feature,p[:2],q[:2]))
    if feature=='Top surface':top_speeds.add(round(feed/60,3))
  x,y=nx,ny
 assert len(layers)==8
 assert all(ts=={1} for z,ts in layers.items() if z<=.60001)
 assert all(ts=={2,3,4} for z,ts in layers.items() if z>.60001)
 im=Image.new('RGB',(700,1100),'white');plot=Image.new('RGB',(600,900),'white');d=ImageDraw.Draw(plot)
 for feature,p,q in paths:
  color='#1766a4' if feature=='Top surface' else '#d34836'
  def pt(a):return (20+(a[0]+20.5)*13,870-(a[1]-4.5)*13)
  d.line([pt(p),pt(q)],fill=color,width=2)
 im.paste(plot,(50,100));d=ImageDraw.Draw(im)
 d.text((20,20),label,font=ImageFont.truetype(v.REGULAR,26),fill=v.BLUE)
 d.text((20,1030),'Azul: topo · vermelho: outros percursos',font=ImageFont.truetype(v.REGULAR,21),fill=v.BLUE)
 return {'material_slots_by_layer':{str(z):sorted(t) for z,t in layers.items()},
  'last_orange_z_mm':.6,'first_relief_z_mm':.8,'interior_last_orange_features':counts,
  'outer_wall_acceleration_after_first_layer_mm_s2':sorted(outer_acc),'orange_top_speed_mm_s':sorted(top_speeds)},im


def main(args):
 FOLDER.mkdir(exist_ok=True);w=args.work_dir;w.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
 blobs,settings,_=read_project(SOURCE);original_blobs=dict(blobs)
 cfg=json.loads(blobs['Metadata/project_settings.config'])
 cfg['outer_wall_acceleration']=['1000']
 blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
 objects=[o for o in settings.findall('object') if any('placa-laranja' in (m.get('value') or '') for m in o.findall('part/metadata'))]
 assert len(objects)==1;plaque=objects[0]
 for key,value in OVERRIDES.items():
  node=plaque.find(f"metadata[@key='{key}']")
  if node is None:node=ET.SubElement(plaque,'metadata',key=key)
  node.set('value',value)
 for part in plaque.findall('part'):
  node=part.find("metadata[@key='outer_wall_acceleration']")
  if node is None:node=ET.SubElement(part,'metadata',key='outer_wall_acceleration')
  node.set('value','1000')
 for obj in settings.findall('object'):
  for node in obj.findall("metadata[@key='outer_wall_acceleration']"):node.set('value','1000')
 settings.findall('plate')[1].find("metadata[@key='plater_name']").set('value','02 Placa V7 - laranja continuo e contornos suaves')
 blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
 target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'
 with ZipFile(target,'w',ZIP_DEFLATED) as z:
  for n,b in blobs.items():z.writestr(n,b)
 native=annotate(target,target,[v.ORANGE,v.GOLD,v.WHITE,v.CYAN],PREFIX)
 actual,newsettings,plates=read_project(target);assert len(plates)==2
 for n,b in original_blobs.items():
  if n.startswith('3D/') and n.endswith('.model'):assert actual[n]==b
 newcfg=json.loads(actual['Metadata/project_settings.config']);oldcfg=json.loads(original_blobs['Metadata/project_settings.config'])
 assert newcfg['outer_wall_acceleration']==['1000']
 assert {k:v for k,v in oldcfg.items() if k!='outer_wall_acceleration'}=={k:v for k,v in newcfg.items() if k!='outer_wall_acceleration'}
 oldsettings=ET.fromstring(original_blobs['Metadata/model_settings.config'])
 for a,b in zip(oldsettings.findall('object'),newsettings.findall('object')):
  if a.get('id')!=plaque.get('id'):
   for node in a.findall("metadata[@key='outer_wall_acceleration']"):node.set('value','1000')
   assert ET.tostring(a)==ET.tostring(b)
 source=trimesh.load(ROOT/'downloads/m7-tijolo-v6-folga-placa-laranja.stl',force='mesh')
 native_carrier=next(m for k,c,m in native[1] if c==1)
 common=['--datadir',str(w/'user'),'--debug','2']
 run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
 run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
  '--export-3mf','validation.3mf',str(target)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==2
 reports=[]
 with ZipFile(w/'slice/validation.3mf') as z:
  for i,p in enumerate(result['sliced_plates']):
   assert not p.get('warning_message') and p['filament_change_times']==(0 if i==0 else 11)
   code=z.read(f'Metadata/plate_{i+1}.gcode').decode();assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
   if i==0:
    current_z=0.;current_feature='Custom';current_acc=0.;body_acc=set()
    for line in code.splitlines():
     if line.startswith('; Z_HEIGHT:'):current_z=float(line.split(':')[1])
     if line.startswith('; FEATURE:'):current_feature=line.split(':',1)[1].strip()
     command=re.match(r'^M204 S([\d.]+)',line)
     if command:current_acc=float(command[1])
     extrusion=re.search(r'\bE(-?[\d.]+)',line)
     if current_z>.20001 and current_feature=='Outer wall' and line.startswith(('G1 ','G2 ','G3 ')) and extrusion and float(extrusion[1])>0 and re.search(r'\b[XY]-?[\d.]',line):body_acc.add(current_acc)
    assert body_acc=={1000.},body_acc
   if i==1:
    sequence,after=analyse(code,source,native_carrier,'V7 · última camada laranja')
    assert set(sequence['interior_last_orange_features'])=={'Top surface'},sequence
    assert sequence['outer_wall_acceleration_after_first_layer_mm_s2']==[1000.],sequence
    assert sequence['orange_top_speed_mm_s']==[25.]
   reports.append({'plate':i+1,'estimated_seconds':p['total_predication'],
    'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),'filament_changes':p['filament_change_times'],
    'warnings':p.get('warning_message'),'brim':False,'supports':False,'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
 run_cli(args.bambu_bin,common+['--slice','2','--orient','0','--arrange','0','--outputdir',str(w/'baseline'),str(SOURCE)],w/'baseline.log')
 oldsequence,before=analyse((w/'baseline/plate_2.gcode').read_text(),source,native_carrier,'V6 · contornos dentro do laranja')
 assert oldsequence['interior_last_orange_features'].get('Inner wall',0)>0
 image=Image.new('RGB',(1440,1100),'white');image.paste(before,(0,0));image.paste(after,(740,0));image.save(ROOT/'designs'/f'{PREFIX}-comparacao-percursos.png')
 report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_project':SOURCE.name,
  'geometry_and_assembly_models_byte_identical_to_v6':True,'global_profile_changes':{'outer_wall_acceleration':['1000']},
  'body_geometry_unchanged':True,'body_outer_wall_acceleration_mm_s2':1000,'body_acceleration_verified_in_gcode':True,'plaque_object_overrides':OVERRIDES,'plaque_mm':[46.4,66.4,.6],
  'plaque_part_overrides':{'outer_wall_acceleration':'1000'},'side_clearance_mm':.3,'baseline':oldsequence,'corrected':sequence,
  'bambu_version':'02.08.02.61','native_reopen_exit':0,'native_slice_exit':0,'plates':reports,
  'physical_print_tested':False,'corner_tip_eliminated_confirmed':False,'physical_fit_tested':False}
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


def package():
 paths=list(FOLDER.iterdir())+[ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf',Path(__file__)]+list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
 with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
  for p in paths:z.write(p,p.name)
  z.write(FOLDER/'README.md','LEIA-ME.md')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-v7-acabamento'))
 p.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
 p.add_argument('--package-only',action='store_true');args=p.parse_args()
 if not args.package_only:main(args)
 if (FOLDER/'README.md').exists():package()
