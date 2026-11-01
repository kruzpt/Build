"""Fix the object-level one-wall policy; preserve all M7 V6 geometry."""
import argparse,hashlib,json,os,re,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree
from build_pintos_pla_3mf import read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate,plate_meshes
from build_m7_house_v6_3mf import inspect
import generate_m7_prototypes_v1 as v

ROOT=v.ROOT;FOLDER=ROOT/'fusion/M7CasaAcabamentoV7';PREFIX='m7-casa-v7-branco-continuo'
SOURCE=ROOT/'downloads/m7-casa-v6-azul-2mm-A1-AMS-4-pratos.3mf'


def wall_check(code,source_mesh,target_mesh,word_bounds,label):
 tree=cKDTree(target_mesh.vertices);match=None
 for angle in (0,np.pi/2,np.pi,3*np.pi/2):
  rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
  points=source_mesh.vertices@rot.T
  shift=(target_mesh.bounds[0]+target_mesh.bounds[1]-points.min(0)-points.max(0))/2
  if tree.query(points+shift)[0].max()<.003:match=(rot,shift);break
 assert match is not None
 rot,shift=match;z=0.;tool=0;feature='Custom';x=y=0.;segments=[];counts={}
 for line in code.splitlines():
  if line.startswith('; Z_HEIGHT:'):z=float(line.split(':')[1])
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  change=re.match(r'^M620 S([0-2])A',line) or re.match(r'^T([0-2])\s*$',line)
  if change:tool=int(change[1])
  if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
  vals={a:float(b) for a,b in re.findall(r'([XYE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
  nx,ny=vals.get('X',x),vals.get('Y',y)
  if abs(z-6)<.0001 and tool==0 and vals.get('E',0)>0 and (nx,ny)!=(x,y) and feature not in ('Custom','Prime tower'):
   p=(np.array([x,y,z])-shift)@rot;q=(np.array([nx,ny,z])-shift)@rot;mid=(p[:2]+q[:2])/2
   if np.all(mid>=word_bounds[0]-.5) and np.all(mid<=word_bounds[1]+.5):
    counts[feature]=counts.get(feature,0)+1;segments.append((feature,p[:2],q[:2]))
  x,y=nx,ny
 assert segments
 im=Image.new('RGB',(1080,600),'white');plot=Image.new('RGB',(950,410),'white');d=ImageDraw.Draw(plot)
 for feature,p,q in segments:
  color='#1465a4' if feature=='Top surface' else '#d64d38'
  def point(t):return (20+(t[0]-word_bounds[0,0])*15,390-(t[1]-word_bounds[0,1])*15)
  d.line([point(p),point(q)],fill=color,width=2)
 im.paste(plot,(50,110));d=ImageDraw.Draw(im)
 d.text((25,20),label,font=ImageFont.truetype(v.REGULAR,27),fill=v.BLUE)
 d.text((25,550),'Azul: percursos de topo · vermelho: perímetros internos',font=ImageFont.truetype(v.REGULAR,21),fill=v.BLUE)
 return counts,im


def main(args):
 FOLDER.mkdir(exist_ok=True);w=args.work_dir;w.mkdir(exist_ok=True,parents=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
 blobs,settings,plates=read_project(SOURCE)
 orig_blobs=dict(blobs);cfg=json.loads(blobs['Metadata/project_settings.config'])
 houses=[o for o in settings.findall('object') if any('fachada-branca' in (m.get('value') or '') for m in o.findall('part/metadata'))]
 assert len(houses)==1;house=houses[0]
 old=house.find("metadata[@key='top_one_wall_type']")
 if old is None:old=ET.SubElement(house,'metadata',key='top_one_wall_type')
 old.set('value','not apply')
 settings.findall('plate')[0].find("metadata[@key='plater_name']").set('value','01 Casa V7 - branco continuo antes da frase')
 blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
 target=ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf'
 with ZipFile(target,'w',ZIP_DEFLATED) as z:
  for n,data in blobs.items():z.writestr(n,data)
 native=annotate(target,target,[v.WHITE,v.BLUE,v.CYAN],PREFIX)
 actual_blobs,new_settings,_=read_project(target)
 for n in orig_blobs:
  if n.startswith('3D/') and n.endswith('.model'):assert orig_blobs[n]==actual_blobs[n]
 assert actual_blobs['Metadata/project_settings.config']==orig_blobs['Metadata/project_settings.config']
 assert len(native)==4
 # All object settings except the intended house override remain identical.
 original=ET.fromstring(orig_blobs['Metadata/model_settings.config'])
 for old_obj,new_obj in zip(original.findall('object'),new_settings.findall('object')):
  if old_obj.get('id')!=house.get('id'):assert ET.tostring(old_obj)==ET.tostring(new_obj)
 common=['--datadir',str(w/'user'),'--debug','2']
 run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
 run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
  '--export-3mf','validation.3mf',str(target)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==4
 reports=[]
 white=trimesh.load(ROOT/'downloads/m7-casa-v6-azul-2mm-fachada-branca.stl',force='mesh')
 wording=trimesh.load(ROOT/'downloads/m7-casa-v6-azul-2mm-frase-azul.stl',force='mesh')
 target_white=next(m for k,c,m in native[0] if c==1)
 window_part=next(m for k,c,m in native[0] if c==2 and abs(m.extents[2]-.2)<.001)
 window_boxes=[m.bounds[:,:2] for m in window_part.split()]
 with ZipFile(w/'slice/validation.3mf') as z:
  for i,p in enumerate(result['sliced_plates']):
   assert not p.get('warning_message') and p['filament_change_times']==(2 if i==0 else 0)
   code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
   assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
   if i==0:
    sequence=inspect(code,window_boxes)
    counts,after=wall_check(code,white,target_white,wording.bounds[:,:2],'V7 · última camada branca · zona da frase')
    assert counts.get('Inner wall',0)==0 and counts.get('Outer wall',0)==0
    assert counts.get('Top surface',0)>0
    assert not set(counts)-{'Top surface'}
   reports.append({'plate':i+1,'estimated_seconds':p['total_predication'],
    'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),'filament_changes':p['filament_change_times'],
    'warnings':p.get('warning_message'),'supports':False,'brim':False,
    'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
 # Re-slice baseline with the same engine, rather than relying on an old report.
 run_cli(args.bambu_bin,common+['--slice','1','--orient','0','--arrange','0','--outputdir',str(w/'baseline'),str(SOURCE)],w/'baseline.log')
 baseline_code=(w/'baseline/plate_1.gcode').read_text()
 old_counts,before=wall_check(baseline_code,white,target_white,wording.bounds[:,:2],'V6 · perímetros nas zonas das letras')
 assert old_counts.get('Inner wall',0)>0
 comparison=Image.new('RGB',(1080,1280),'white');comparison.paste(before,(0,0));comparison.paste(after,(0,640))
 comparison.save(ROOT/'designs'/f'{PREFIX}-comparacao-percursos.png')
 report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
  'source_project':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  'geometry_and_assembly_models_byte_identical_to_v6':True,'global_settings_byte_identical_to_v6':True,
  'other_objects_settings_unchanged':True,'house_object_override':{'top_one_wall_type':'not apply'},
  'white_letter_area_bounds_mm':wording.bounds[:,:2].tolist(),
  'baseline_v6_final_white_letter_area_features':old_counts,'v7_final_white_letter_area_features':counts,
  'last_white_layer_has_no_letter_perimeters':True,'house_sequence':sequence,
  'bambu_version':'02.08.02.61','native_reopen_exit':0,'native_slice_exit':0,'plates':reports,
  'total_estimated_seconds':sum(p['estimated_seconds'] for p in reports),
  'total_estimated_grams':sum(p['estimated_grams'] for p in reports),
  'physical_print_tested':False,'physical_fit_tested':False}
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))


def package():
 paths=list(FOLDER.iterdir())+[ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf',Path(__file__)]+list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
 with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
  for p in paths:z.write(p,p.name)
  z.write(FOLDER/'README.md','LEIA-ME.md')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-casa-v7-branco-continuo'))
 p.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
 p.add_argument('--package-only',action='store_true');args=p.parse_args()
 if not args.package_only:main(args)
 if (FOLDER/'README.md').exists():package()
