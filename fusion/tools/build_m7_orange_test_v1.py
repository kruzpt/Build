"""Isolate the orange carrier from the actual V7 project without tuning it."""
import argparse,hashlib,json,os,re,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np
from build_pintos_pla_3mf import read_project,run_cli,NS
from build_m7_prototypes_v1_3mf import annotate
import generate_m7_prototypes_v1 as v
ROOT=v.ROOT;FOLDER=ROOT/'fusion/M7TijoloTesteLaranjaV1';PREFIX='m7-tijolo-teste-laranja-v1'
SOURCE=ROOT/'downloads/m7-tijolo-v7-acabamento-A1-AMS-2-pratos.3mf'


def main(args):
 FOLDER.mkdir(exist_ok=True);w=args.work_dir;w.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
 blobs,settings,plates=read_project(SOURCE);source_blobs=dict(blobs)
 objects=[o for o in settings.findall('object') if any('placa-laranja' in (m.get('value') or '') for m in o.findall('part/metadata'))]
 assert len(objects)==1;obj=objects[0];oid=obj.get('id')
 parts=[p for p in obj.findall('part') if any('placa-laranja' in (m.get('value') or '') for m in p.findall('metadata'))]
 assert len(parts)==1;carrier=parts[0];pid=carrier.get('id')
 for other in settings.findall('object'):
  if other is not obj:settings.remove(other)
 for part in obj.findall('part'):
  if part is not carrier:obj.remove(part)
 face_count=carrier.find('mesh_stat').get('face_count')
 for m in obj.findall('metadata'):
  if m.get('key')=='name':m.set('value','Teste - fundo laranja apenas')
  if m.get('face_count') is not None:m.set('face_count',face_count)
 old_plates=settings.findall('plate');keep=old_plates[1]
 for other in old_plates:
  if other is not keep:settings.remove(other)
 keep.find("metadata[@key='plater_id']").set('value','1')
 keep.find("metadata[@key='plater_name']").set('value','01 TESTE - fundo laranja 46.4 x 66.4 x 0.6')
 keep.find("metadata[@key='thumbnail_file']").set('value','Metadata/plate_1.png')
 model=blobs['3D/3dmodel.model']
 expression=rb'<object\b(?=[^>]*\bid="'+oid.encode()+rb'")[^>]*>.*?</object>'
 match=re.search(expression,model,re.S);assert match
 assembly=match.group(0)
 def component(m):return m.group(0) if re.search(rb'\bobjectid="'+pid.encode()+rb'"',m.group(0)) else b''
 assembly=re.sub(rb'<component\b[^>]*/>',component,assembly)
 model=model[:match.start()]+assembly+model[match.end():]
 def builditem(m):
  raw=m.group(0)
  if not re.search(rb'\bobjectid="'+oid.encode()+rb'"',raw):return b''
  a=re.search(rb'transform="([^"]+)"',raw);numbers=[float(x) for x in a[1].split()]
  numbers[9]-=307.2
  return raw.replace(a.group(0),('transform="'+' '.join(str(x) for x in numbers)+'"').encode())
 model=re.sub(rb'<item\b[^>]*/>',builditem,model)
 blobs['3D/3dmodel.model']=model
 cfg=json.loads(blobs['Metadata/project_settings.config']);cfg['enable_prime_tower']='0'
 blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
 blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
 for name in list(blobs):
  if re.match(r'Metadata/plate_2(?:_|\.)',name):del blobs[name]
 target=ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf'
 with ZipFile(target,'w',ZIP_DEFLATED) as z:
  for n,b in blobs.items():z.writestr(n,b)
 native=annotate(target,target,[v.ORANGE,v.GOLD,v.WHITE,v.CYAN],PREFIX)
 assert len(native)==1 and len(native[0])==1 and native[0][0][1]==1
 mesh=native[0][0][2];np.testing.assert_allclose(mesh.extents,[46.4,66.4,.6],atol=.0001)
 assert mesh.is_watertight and abs(mesh.bounds[0,2])<.001
 b,s,_=read_project(target)
 assert b['3D/Objects/object_2.model']==source_blobs['3D/Objects/object_2.model']
 assert ET.tostring(s.find('object/part'))==ET.tostring(carrier)
 common=['--datadir',str(w/'user'),'--debug','2']
 run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
 run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
  '--export-3mf','validation.3mf',str(target)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==1
 plate=result['sliced_plates'][0];assert not plate.get('warning_message') and plate['filament_change_times']==0
 with ZipFile(w/'slice/validation.3mf') as z:code=z.read('Metadata/plate_1.gcode').decode()
 assert '; FEATURE: Prime tower' not in code and '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
 zheight=0.;tool=0;feature='Custom';x=y=0.;layers={};last_features=set()
 for line in code.splitlines():
  if line.startswith('; Z_HEIGHT:'):zheight=float(line.split(':')[1])
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  ch=re.match(r'^M620 S([0-3])A',line) or re.match(r'^T([0-3])\s*$',line)
  if ch:tool=int(ch[1])
  if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
  values={k:float(t) for k,t in re.findall(r'([XYE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
  nx,ny=values.get('X',x),values.get('Y',y)
  if zheight>0 and values.get('E',0)>0 and (nx,ny)!=(x,y) and feature not in ('Custom','Prime tower'):
   layers.setdefault(zheight,set()).add(tool+1)
   if abs(zheight-.6)<.0001:last_features.add(feature)
  x,y=nx,ny
 assert layers=={.2:{1},.4:{1},.6:{1}}
 report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_project':SOURCE.name,
  'test_purpose':'Check the orange carrier before any coloured relief printing',
  'printable_objects':1,'printable_parts':1,'dimensions_mm':mesh.extents.tolist(),
  'carrier_mesh_and_part_settings_unchanged':True,'orientation_and_printer_xy_preserved':True,
  'tower_disabled':True,'supports':False,'brim':False,'filament_changes':0,'layers':3,
  'material_slots_by_layer':{str(k):sorted(v) for k,v in layers.items()},'last_layer_features':sorted(last_features),
  'estimated_seconds':plate['total_predication'],'estimated_grams':sum(f['total_used_g'] for f in plate['filaments']),
  'filaments':plate['filaments'],'warnings':plate.get('warning_message'),'native_reopen_exit':0,'native_slice_exit':0,
  'bambu_version':'02.08.02.61','gcode_sha256':hashlib.sha256(code.encode()).hexdigest(),'physical_print_tested':False}
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


def package():
 paths=list(FOLDER.iterdir())+[ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf',Path(__file__)]+list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
 with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
  for p in paths:z.write(p,p.name)
  z.write(FOLDER/'README.md','LEIA-ME.md')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-teste-laranja-v1'))
 p.add_argument('--bambu-bin',type=Path,default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
 p.add_argument('--package-only',action='store_true');args=p.parse_args()
 if not args.package_only:main(args)
 if (FOLDER/'README.md').exists():package()
