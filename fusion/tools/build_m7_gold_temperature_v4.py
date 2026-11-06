"""Matched 205 C counterpart of the approved four-speed 215 C gold test.

Geometry, sample speeds and all other print/material settings are preserved.
Label on the photographed spool: Amazon Basics Silk PLA, 190--220 C nozzle.
"""
import argparse,hashlib,json,os,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
from build_pintos_pla_3mf import read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate
from check_anilha_lobito_v5_toolpaths import paths

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-dourado-temperatura-v4-205C'
FOLDER=ROOT/'fusion/M7DouradoTemperaturaV4'
SOURCE=ROOT/'downloads/m7-dourado-calibracao-velocidade-v3-A1-AMS-1-prato.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-1-prato.3mf'


def main(a):
 FOLDER.mkdir(exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
 original,settings,_=read_project(SOURCE);blobs=dict(original)
 cfg=json.loads(blobs['Metadata/project_settings.config']);before=json.loads(json.dumps(cfg))
 for key in ('nozzle_temperature','nozzle_temperature_initial_layer'):
  assert cfg[key][1]=='215';cfg[key][1]='205'
 blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
 settings.find('plate/metadata[@key="plater_name"]').set('value','01 TESTE 205C - A atual - B35 - C25 - D15')
 blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
 with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
  for n,b in blobs.items():z.writestr(n,b)
 annotate(TARGET,TARGET,cfg['filament_colour'],PREFIX)
 after,model,plates=read_project(TARGET);actual=json.loads(after['Metadata/project_settings.config'])
 assert actual==cfg
 assert all(after[n]==b for n,b in original.items() if n.startswith('3D/'))
 old=ET.fromstring(original['Metadata/model_settings.config'])
 for x,y in zip(old.findall('object'),model.findall('object')):
  assert ET.canonicalize(ET.tostring(x,encoding='unicode'),strip_text=True)==ET.canonicalize(ET.tostring(y,encoding='unicode'),strip_text=True)
 assert len(plates)==1 and len(plates[0]['items'])==4
 common=['--datadir',str(a.work_dir/'user'),'--debug','2']
 run_cli(a.bambu_bin,common+['--info','--outputdir',str(a.work_dir/'reopen'),str(TARGET)],a.work_dir/'reopen.log')
 run_cli(a.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(a.work_dir/'slice'),'--export-3mf','validation.3mf',str(TARGET)],a.work_dir/'slice.log')
 result=json.loads((a.work_dir/'slice/result.json').read_text());assert result['return_code']==0
 p=result['sliced_plates'][0];assert not p.get('warning_message') and p['filament_change_times']==1
 with ZipFile(a.work_dir/'slice/validation.3mf') as z:code=z.read('Metadata/plate_1.gcode').decode()
 assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
 assert 'M109 S205' in code
 rr=paths(code);assert set(r['tool'] for r in rr)=={1,2}
 # Check the last blocking temperature wait before the first gold extrusion
 # on the coupons, excluding purge tower/filament-change moves.
 tool=1;temperature=None;feature='';layer=0.;checked=[]
 for line in code.splitlines():
  m=re.match(r'M620 S([0-3])A',line)
  if m:tool=int(m[1])+1
  m=re.match(r'M109 S(\d+)',line)
  if m:temperature=int(m[1])
  if line.startswith('; FEATURE:'):feature=line.split(':')[1].strip()
  if line.startswith('; Z_HEIGHT:'):layer=float(line.split(':')[1])
  if tool==2 and feature in ('Outer wall','Inner wall') and layer>.6 and re.match(r'^G[123] ',line) and ' E' in line and (' X' in line or ' Y' in line):
   assert temperature==205;checked.append(temperature)
 assert checked
 compared=None
 if a.reference_validation:
  with ZipFile(a.reference_validation) as z:src=paths(z.read('Metadata/plate_1.gcode').decode())
  printable=lambda rows:[r for r in rows if r['feature']!='Prime tower']
  compared=printable(src)==printable(rr);assert compared,'Coupon extrusion paths unexpectedly changed'
 report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),source=SOURCE.name,
  material_confirmed_by_user_label='Amazon Basics Silk PLA Gold, 1.75 mm',label_nozzle_range_c=[190,220],
  only_material_change={'gold_nozzle_temperature_c':[215,205],'gold_nozzle_initial_layer_temperature_c':[215,205]},
  source_geometry_and_assembly_bytes_identical=True,object_settings_identical=True,coupon_extrusion_paths_identical=compared,
  gold_print_temperature_wait_verified_c=205,flow=actual['filament_flow_ratio'][:2],
  speeds_by_sample={'A':'50 outer / 100 configured inner, volumetric limit applies','B':35,'C':25,'D':15},
  physical_identification='1,2,3,4 notches; identical shapes to 215 C group, keep groups separately labelled',
  native_reopen_exit=0,native_slice_exit=0,bambu_version=cfg['version'],warnings=p.get('warning_message'),
  filament_changes=1,estimated_seconds=p['total_predication'],estimated_grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']),
  filaments=p['filaments'],brim=False,supports=False,physical_print_tested=False,temperature_cause_established=False)
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--reference-validation',type=Path);main(p.parse_args())
