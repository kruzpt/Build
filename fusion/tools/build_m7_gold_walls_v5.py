"""Approved four-sample gold-tree wall-count calibration; original geometry and calibrated profiles.

The gold setting difference between samples is requested wall count. A single plate
contains A/B/C/D (five, three, two and one notches), with orange + gold only.
"""
import argparse,json,hashlib,os,re,uuid
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as md
from PIL import Image,ImageDraw,ImageFont
from build_pintos_pla_3mf import read_project,run_cli,NS
from build_m7_prototypes_v1_3mf import plate_meshes,annotate
from check_anilha_lobito_v5_toolpaths import paths
from generate_m7_prototypes_v1 import rounded
from generate_joana_topper import save_mesh

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-dourado-paredes-v5'
FOLDER=ROOT/'fusion/M7DouradoParedesV5'
SOURCE=ROOT/'downloads/m7-tijolo-teste-dourado-v1-5-paredes-A1-AMS-2-pratos.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-1-prato.3mf'
I='1 0 0 0 1 0 0 0 1 0 0 0'
SAMPLES=[('A',5,48),('B',3,90),('C',2,132),('D',1,174)]


def render_sample_overview(native):
 image=Image.new('RGB',(1640,780),'#f5f6f8');draw=ImageDraw.Draw(image)
 font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 title=ImageFont.truetype(font_path,30);label_font=ImageFont.truetype(font_path,24);small=ImageFont.truetype(font_path,21)
 draw.text((38,25),'Dourado V5 — comparação de paredes',font=title,fill='#183344')
 draw.text((38,78),'Todas: 25 mm/s · 215 °C · fluxo 0,9702 · mesma árvore',font=label_font,fill='#183344')
 scale=10
 for i,(label,walls,position) in enumerate(SAMPLES):
  left=45+i*400;bottom=570
  draw.text((left,155),f'{label} — {walls} '+('parede' if walls==1 else 'paredes'),font=title,fill='#183344')
  parts=[(col,m) for ident,col,m in native if position-.01<=m.bounds[0,0] and m.bounds[1,0]<=position+32.01]
  assert len(parts)==2
  for col,m in sorted(parts,key=lambda p:p[1].bounds[0,2]):
   for tri in m.triangles:
    draw.polygon([(left+(x-position)*scale,bottom-(y-110)*scale) for x,y,z in tri],fill='#e78339' if col==1 else '#dab967')
  draw.text((left,600),f'{walls} '+('recorte na base' if walls==1 else 'recortes na base'),font=label_font,fill='#183344')
 draw.text((38,677),'Neste teste: número de recortes = número de paredes no dourado.',font=label_font,fill='#183344')
 draw.text((38,724),'Projeção da geometria real · acabamento físico por testar · cerca de 35 min / 4,9 g',font=small,fill='#465d6b')
 image.save(ROOT/'designs'/f'{PREFIX}-amostras.png')


def metadata(node,key,value):ET.SubElement(node,'metadata',key=key,value=str(value))
def write(file,blobs):
 with ZipFile(file,'w',ZIP_DEFLATED) as z:
  for name,data in blobs.items():z.writestr(name,data)


def mesh_xml(mesh,ident):
 v=''.join('<vertex x="%.9g" y="%.9g" z="%.9g"/>'%tuple(p) for p in mesh.vertices)
 f=''.join('<triangle v1="%d" v2="%d" v3="%d"/>'%tuple(t) for t in mesh.faces)
 return f'<object id="{ident}" type="model"><mesh><vertices>{v}</vertices><triangles>{f}</triangles></mesh></object>'


def main(a):
 FOLDER.mkdir(exist_ok=True);w=a.work_dir;w.mkdir(parents=True,exist_ok=True)
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
 source_blobs,source_settings,_=read_project(SOURCE)
 cfg=json.loads(source_blobs['Metadata/project_settings.config']);original_cfg=json.loads(json.dumps(cfg))
 assert cfg['filament_flow_ratio'][:2]==['0.931','0.9702'] and cfg['nozzle_temperature'][1]=='215'
 gold=next(m for key,col,m in plate_meshes(source_blobs,source_settings)[1] if col==2)
 components=gold.split(only_watertight=False);assert len(components)==2
 tree=min(components,key=lambda m:m.bounds[0,1]);tree.apply_translation([3.1-tree.bounds[0,0],3.5-tree.bounds[0,1],.6-tree.bounds[0,2]])
 assert np.allclose(tree.extents,[25.8037968,27,1],atol=.0001)
 assert tree.is_watertight and tree.is_winding_consistent
 meshes=[];manifest=[];model_objects=[];config=ET.Element('config')
 for j,(label,walls,position) in enumerate(SAMPLES):
  base=rounded(0,0,32,34,1.2).extrude(.6)
  for x in [16-2*(walls-1)+4*k for k in range(walls)]:base-=md.Manifold.cylinder(1,.8,.8,48).translate((x,0,-.2))
  base_file=ROOT/'downloads'/f'{PREFIX}-{label}-base-laranja.stl';base_mesh=save_mesh(base,base_file)
  tree_file=ROOT/'downloads'/f'{PREFIX}-{label}-arvore-dourada.stl';tree.export(tree_file)
  check=trimesh.load(tree_file,force='mesh');assert check.is_watertight
  pair=[base_mesh,tree.copy()];meshes.extend(pair)
  oid=3+j*3;parent=ET.SubElement(config,'object',id=str(oid));metadata(parent,'name',f'Amostra {label} - '+f'{walls} paredes - {walls} marcas - 25 mm-s');metadata(parent,'extruder',1);metadata(parent,'top_one_wall_type','not apply');metadata(parent,'outer_wall_acceleration',1000);metadata(parent,'infill_wall_overlap','10%')
  for k,(mesh,slot,file) in enumerate(zip(pair,(1,2),(base_file,tree_file))):
   pid=1+j*3+k;model_objects.append(mesh_xml(mesh,pid));part=ET.SubElement(parent,'part',id=str(pid),subtype='normal_part',uuid=str(uuid.uuid4()))
   for key,value in {'name':file.stem,'source_file':file.name,'extruder':slot,'outer_wall_acceleration':1000,'wall_loops':1 if slot==1 else walls}.items():metadata(part,key,value)
   if slot==2:
    for kk,vv in {'outer_wall_speed':25,'inner_wall_speed':25,'internal_solid_infill_speed':25,'gap_infill_speed':25,'top_surface_speed':25,'top_surface_pattern':'concentric'}.items():metadata(part,kk,vv)
   ET.SubElement(part,'mesh_stat',face_count=str(len(mesh.faces)),edges_fixed='0',degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
   manifest.append(dict(sample=label,part='base' if slot==1 else 'tree',file=file.name,volume_mm3=float(mesh.volume),dimensions_mm=mesh.extents.tolist(),watertight=bool(mesh.is_watertight),slot=slot))
  model_objects.append(f'<object id="{oid}" type="model"><components><component objectid="{oid-2}" transform="{I}"/><component objectid="{oid-1}" transform="{I}"/></components></object>')
 plate=ET.SubElement(config,'plate')
 for key,value in {'plater_id':1,'plater_name':'01 Paredes A5 B3 C2 D1 - todos 25 mm-s 215C','locked':'false','filament_map_mode':'Auto For Flush'}.items():metadata(plate,key,value)
 for j,oid in enumerate((3,6,9,12)):
  inst=ET.SubElement(plate,'model_instance')
  for key,value in {'object_id':oid,'instance_id':0,'identify_id':1001+j}.items():metadata(inst,key,value)
 build=''.join(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {x} 110 0" printable="1"/>' for oid,x in [(3,48),(6,90),(9,132),(12,174)])
 model=f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="{NS}" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"><metadata name="Application">BambuStudio-02.08.02.61</metadata><metadata name="BambuStudio:3mfVersion">1</metadata><resources>{''.join(model_objects)}</resources><build>{build}</build></model>'''
 cfg['wipe_tower_x']=['15'];cfg['wipe_tower_y']=['170']
 blobs={'[Content_Types].xml':source_blobs['[Content_Types].xml'],'_rels/.rels':b'''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>''','3D/3dmodel.model':model.encode(),'Metadata/project_settings.config':json.dumps(cfg,indent=2).encode(),'Metadata/model_settings.config':ET.tostring(config,encoding='utf-8',xml_declaration=True),'Metadata/filament_sequence.json':b'{"plate_1":{"nozzle_sequence":[],"optimal_assignment":[],"sequence":[]}}'}
 write(w/'input.3mf',blobs)
 print('native export',flush=True)
 run_cli(a.bambu_bin,['--datadir',str(w/'user'),'--debug','2','--orient','0','--arrange','0','--outputdir',str(w),'--export-3mf','native.3mf',str(w/'input.3mf')],w/'export.log')
 annotate(w/'native.3mf',TARGET,cfg['filament_colour'],PREFIX)
 actual,native_settings,plates=read_project(TARGET);native_cfg=json.loads(actual['Metadata/project_settings.config'])
 # Export may normalize presentation/profile metadata; verify all source
 # material and process values which control this test explicitly.
 keys=['filament_flow_ratio','nozzle_temperature','nozzle_temperature_initial_layer','filament_retraction_length','filament_max_volumetric_speed','fan_min_speed','fan_max_speed','layer_height','initial_layer_print_height','inner_wall_speed','outer_wall_speed','retraction_length','retract_restart_extra','seam_gap','wall_generator','gap_infill_speed','top_surface_speed','internal_solid_infill_speed','enable_support','brim_type','default_acceleration']
 for key in keys:assert native_cfg.get(key)==original_cfg.get(key),(key,native_cfg.get(key),original_cfg.get(key))
 assert len(plates)==1 and len(plates[0]['items'])==4
 native=plate_meshes(actual,native_settings)[0];assert len(native)==8
 render_sample_overview(native)
 for i in range(4):
  box=plates[0]['items'][i]['mesh'].bounds
  assert box[0,:2].min()>3 and box[1,:2].max()<253 and abs(box[0,2])<.001
 for ref in (tree,):
  matches=[m for k,col,m in native if col==2];assert len(matches)==4
  assert all(abs(m.volume-ref.volume)<.001 and np.allclose(m.extents,ref.extents,atol=.001) for m in matches)
 print('native slice',flush=True)
 run_cli(a.bambu_bin,['--datadir',str(w/'user'),'--debug','2','--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),'--export-3mf','validation.3mf',str(TARGET)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0
 p=result['sliced_plates'][0];assert not p.get('warning_message')
 with ZipFile(w/'slice/validation.3mf') as z:code=z.read('Metadata/plate_1.gcode').decode()
 assert '; FEATURE: Brim' not in code and '; FEATURE: Support' not in code
 rr=paths(code);assert set(r['tool'] for r in rr)=={1,2}
 assert {round(r['layer'],2) for r in rr}=={.2,.4,.6,.8,1,1.2,1.4,1.6}
 model_rows=[r for r in rr if r['feature']!='Prime tower']
 assert all(r['tool']==1 for r in model_rows if r['layer']<=.6) and all(r['tool']==2 for r in model_rows if r['layer']>.6)
 assert p['filament_change_times']==1
 gold_nodes=[];node_reports=[]
 for obj in native_settings.findall('object'):
  parts=obj.findall('part');parent_props={m.get('key'):m.get('value') for m in obj.findall('metadata') if m.get('key')}
  g=next(n for n in parts if n.find("metadata[@key='extruder'][@value='2']") is not None)
  vals={m.get('key'):m.get('value') for m in g.findall('metadata') if m.get('key')}
  label=next(lab for lab,sp,pos in SAMPLES if '-'+lab+'-' in vals['name']);gold_nodes.append((label,vals))
  mesh=next(m for ident,col,m in native if ident==int(g.get('id')))
  rows=[r for r in rr if r['tool']==2 and all(mesh.bounds[0,k]-.01<=np.mean(np.array(r['points'])[:,k])<=mesh.bounds[1,k]+.01 for k in (0,1))]
  features=set(r['feature'] for r in rows);assert 'Outer wall' in features
  speeds={f:sorted(set(r['speed'] for r in rows if r['feature']==f)) for f in features}
  expected=next(n for lab,n,pos in SAMPLES if lab==label)
  assert all(abs(v-25)<.001 for vv in speeds.values() for v in vv)
  if expected==1:assert 'Inner wall' not in features
  assert vals['wall_loops']==str(expected)
  node_reports.append(dict(sample=label,notches=expected,requested_walls=expected,native_gold_bounds_mm=mesh.bounds.tolist(),actual_requested_speeds_mm_s={f:{'min':min(v),'max':max(v)} for f,v in speeds.items()}))
 aa=next(v for lab,v in gold_nodes if lab=='A')
 ignored={'name','source_file','source_object_id','source_volume_id','source_offset_x','source_offset_y','source_offset_z','matrix'}
 av={k:v for k,v in aa.items() if k not in ignored}
 for label,bb in gold_nodes:
  bv={k:v for k,v in bb.items() if k not in ignored}
  assert {k:v for k,v in bv.items() if k!='wall_loops'}=={k:v for k,v in av.items() if k!='wall_loops'},(label,'Unexpected part setting difference')
 report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),source_project=SOURCE.name,bambu_version=native_cfg['version'],printer=native_cfg['printer_settings_id'],approved_coupon_geometry_reused=True,one_wall_requested_by_user=True,base_mm=[32,34,.6],relief_height_mm=1,tree_original_scale_preserved=True,only_gold_setting_difference={lab:{'wall_loops':n} for lab,n,pos in SAMPLES},common_gold_speed_mm_s=25,common_gold_top_pattern='concentric',flow=native_cfg['filament_flow_ratio'][:2],temperature_c=native_cfg['nozzle_temperature'][:2],gold_retraction_mm=native_cfg['filament_retraction_length'][1],layer_height_mm=.2,brim=False,supports=False,native_slice_exit=0,filament_changes=1,estimated_seconds=p['total_predication'],estimated_grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']),filaments=p['filaments'],warnings=p.get('warning_message'),samples=node_reports,physical_print_tested=False,physical_cause_established=False)
 (FOLDER/'geometry.json').write_text(json.dumps(dict(parts=manifest,source_tree_volume_mm3=float(tree.volume),geometry_note='Original tree translated only; not scaled or thickened'),indent=2)+'\n')
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);main(p.parse_args())
