"""Make the M7 blue backing and white facade a single laminated printed house."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
from shutil import copy2
import manifold3d as md
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
import generate_m7_prototypes_v1 as v
from generate_joana_topper import cross_section
from generate_m7_house_v2 import rebuild
from generate_m7_brick_v4 import exact_mesh
from generate_universo_stand import render_meshes

ROOT=v.ROOT;FOLDER=ROOT/'fusion/M7CasaV4';PREFIX='m7-casa-v4-unida'
BLUE_THICKNESS=.8;HOUSE_THICKNESS=6.;WHITE_THICKNESS=5.2

def main():
 FOLDER.mkdir(exist_ok=True)
 data=json.loads((ROOT/'fusion/M7CasaV2/geometry.json').read_text());old={p['key']:p for p in data['parts']}
 front=cross_section(old['fachada-branca']['regions'][0]['groups'])
 background=cross_section(old['fundo-azul']['regions'][0]['groups'])
 # Recover the four original window holes; keep all external/mating geometry.
 polygons=front.to_polygons();holes=[]
 for polygon in polygons:
  a=np.asarray(polygon);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-np.roll(a[:,0],-1)*a[:,1])/2
  if area<0:holes.append(md.CrossSection([polygon],md.FillRule.EvenOdd))
 assert len(holes)==4
 windows=md.CrossSection.batch_boolean(holes,md.OpType.Add)
 white_back=background-windows
 blue=background.extrude(BLUE_THICKNESS)
 window_faces=background^windows
 window_caps=window_faces.extrude(.2).translate((0,0,.6))
 blue-=window_caps
 white=white_back.extrude(2-BLUE_THICKNESS).translate((0,0,BLUE_THICKNESS))+front.extrude(4).translate((0,0,2))
 wording=cross_section(old['frase-azul']['regions'][0]['groups'])
 phrase=wording.extrude(.6).translate((0,0,HOUSE_THICKNESS))
 pose=np.asarray(old['fachada-branca']['assembly']);pose[:3,3]-=2*pose[:3,2]
 regions={
  'fundo-azul-fino':[v.region(background,BLUE_THICKNESS),v.region(window_faces,.2,.6,'cut')],
  'acabamento-azul-janelas':[v.region(window_faces,.2,.6)],
  'fachada-branca':[v.region(white_back,2-BLUE_THICKNESS,BLUE_THICKNESS),v.region(front,4,2,'join')],
  'frase-azul':[v.region(wording,.6,HOUSE_THICKNESS)]}
 parts=[];assembled=[]
 for key,solid,color in [('fundo-azul-fino',blue,v.BLUE),('acabamento-azul-janelas',window_caps,v.BLUE),('fachada-branca',white,v.WHITE),('frase-azul',phrase,v.BLUE)]:
  p=ROOT/'downloads'/f'{PREFIX}-{key}.stl';mesh=exact_mesh(solid,p)
  assert mesh.is_watertight and mesh.is_winding_consistent
  parts.append({'key':key,'name':key.replace('-',' '),'file':p.name,'product':'casa','color':color,'regions':regions[key],
   'assembly':pose.tolist(),'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),
   'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'watertight':True})
  assembled.append((v.transformed(solid,pose),color))
 for key in ['base-azul','m-branco','7-ciano']:
  entry=deepcopy(old[key]);p=ROOT/'downloads'/f'{PREFIX}-{key}.stl';copy2(ROOT/'downloads'/entry['file'],p)
  entry.update(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest());parts.append(entry)
  assembled.append((v.transformed(rebuild(entry['regions']),np.asarray(entry['assembly'])),entry['color']))
 for i,(a,c) in enumerate(assembled):
  for b,_ in assembled[i+1:]:assert (a^b).volume()<.001
 base=rebuild(old['base-azul']['regions']);house=v.transformed(blue+window_caps+white+phrase,pose)
 assert len([s for s in house.decompose() if s.volume()>1e-6])==1
 for distance in np.linspace(0,105,43):
  assert (house.translate(np.asarray(old['fachada-branca']['assembly'])[:3,1]*distance)^base).volume()<.001
 old_union=rebuild(old['fachada-branca']['regions'])+rebuild(old['fundo-azul']['regions']).translate((0,0,-2))
 canonical=(blue+window_caps+white).translate((0,0,-2))
 expected_removed=(background^windows).area()*(2-BLUE_THICKNESS)
 assert abs((old_union-canonical).volume()-expected_removed)<.02
 assert (canonical-old_union).volume()<.001
 wm=exact_mesh(white,ROOT/'downloads'/f'{PREFIX}-fachada-branca.stl')
 hm=house.bounding_box();assert abs(hm[5]-95)<.02
 report={'version':4,'blue_thickness_mm':BLUE_THICKNESS,'white_frame_max_thickness_mm':WHITE_THICKNESS,
  'overall_house_thickness_mm':6,'phrase_relief_mm':.6,'assembled_height_mm':95,'base_width_depth_mm':[85,85],
  'single_connected_printed_house':True,'parts_to_glue_house_backing':False,
  'base_and_logo_stls_identical_to_v2':True,'original_mating_envelope_preserved':True,
  'window_back_blue_z_mm':BLUE_THICKNESS,'window_recess_from_white_face_mm':5.2,
  'blue_window_surface_finish_only':True,'blue_window_cap_layer_mm':[.6,.8],
  'blue_white_transition_mm':.8,'white_phrase_transition_mm':6.,'phrase_top_mm':6.6,
  'insertion_positions_checked':43,'max_collision_mm3':0,'physical_fit_tested':False,'physical_print_tested':False,
  'fusion_runtime_tested':False}
 (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','version':4,'parts':parts,'house':report},ensure_ascii=False,indent=2)+'\n')
 (FOLDER/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 template=(ROOT/'fusion/M7CasaV2/M7CasaV2.py').read_text().replace('Casa V2','Casa V4 unida').replace('Casa V4 unida de tres pratos','Casa V4 unida de quatro pratos')
 (FOLDER/'M7CasaV4.py').write_text(template)
 im=Image.new('RGB',(1500,1100),'#f4f6f8');im.paste(render_meshes(assembled,(900,920),direction=(.4,-1,.35)),(0,110))
 im.paste(render_meshes([(blue,v.BLUE),(window_caps,v.BLUE),(white,v.WHITE),(phrase,v.BLUE)],(570,650),direction=(.3,-1,.6)),(920,230))
 d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype(v.REGULAR,n)
 for xy,text,size in [((35,25),'M7 · Casa V4 · azul e branco numa só peça',34),((35,80),'Altura 95 mm · base e logótipo V2 preservados',26),
  ((930,140),'Sequência de impressão',26),((930,870),'Azul 0,8 → branco até 6,0 mm',23),((930,920),'Branco acabado → frase azul 0,6 mm',23),
  ((35,1030),'Geometria real · montagem e leitura visual a confirmar na impressão',24)]:d.text(xy,text,font=font(size),fill=v.BLUE)
 im.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
