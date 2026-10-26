"""Three native A1 PETG prototype plates, never a physical print-start job."""
import argparse,json,os,hashlib
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np,trimesh
from build_pintos_pla_3mf import flatten_profile,run_cli,read_project
from build_m7_prototypes_v1_3mf import annotate,plate_meshes
from generate_saca_rolamentos_v1 import ROOT,FOLDER,PREFIX

def package():
 entries=list(FOLDER.glob('*'))+list((ROOT/'downloads').glob(PREFIX+'-*.stl'))+list((ROOT/'downloads').glob(PREFIX+'-*.3mf'))+list((ROOT/'designs').glob(PREFIX+'-*.png'))
 entries+=[Path(__file__),ROOT/'fusion/tools/generate_saca_rolamentos_v1.py']
 with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
  for p in entries:
   if p.is_file():z.write(p,p.name)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--package-only',action='store_true');a=parser.parse_args()
 if a.package_only:package();return
 w=Path('/tmp/saca-rolamentos-v1');w.mkdir(exist_ok=True)
 b=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio');profiles=b.parent.parent/'resources/profiles/BBL'
 os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(b.parent)
 machine=flatten_profile(profiles,'machine','Bambu Lab A1 0.4 nozzle')
 process=flatten_profile(profiles,'process','0.16mm Optimal @BBL A1')
 process.update({'name':'Extrator V1 PETG 8 paredes 100 percent prototipo','from':'User','wall_loops':'8','sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','layer_height':'0.16','initial_layer_print_height':'0.2','top_shell_layers':'6','bottom_shell_layers':'6','top_shell_thickness':'0.96','bottom_shell_thickness':'0.96','wall_generator':'arachne','outer_wall_speed':['25'],'inner_wall_speed':['40'],'top_surface_speed':['25'],'internal_solid_infill_speed':['50'],'initial_layer_speed':['20'],'initial_layer_infill_speed':['20'],'outer_wall_acceleration':['1000'],'top_surface_acceleration':['800'],'enable_prime_tower':'0','enable_support':['1'],'support_type':'normal(auto)','support_style':'snug','support_threshold_angle':'45','support_top_z_distance':'0.2','support_bottom_z_distance':'0.2','support_interface_top_layers':'3','brim_type':'outer_only','brim_width':'5','brim_object_gap':'0.15','elefant_foot_compensation':'0.1','ironing_type':'no ironing','curr_bed_type':'Textured PEI Plate'})
 filament=flatten_profile(profiles,'filament','Generic PETG @BBL A1');filament.update({'name':'PETG prototipo reforcado','from':'User','filament_colour':['#287D96'],'filament_max_volumetric_speed':['6']})
 for name,d in [('machine',machine),('process',process),('filament',filament)]: (w/f'{name}.json').write_text(json.dumps(d))
 parts={p['key']:p for p in json.loads((FOLDER/'geometry.json').read_text())['parts']}
 def item(k):return {'path':str(ROOT/'downloads'/parts[k]['file']),'count':1,'filaments':[1],'print_params':{'enable_support':'1' if k.startswith('gancho') or k in ['eixo','copo'] else '0'}}
 groups=[('01 PRIMEIRO - teste da rosca',['teste-rosca-macho','teste-rosca-porca']),('02 DEPOIS - ganchos eixo e clip',['gancho-5p4','gancho-5p8','gancho-6p2','eixo','clip']),('03 CORPO - apenas apos verificar encaixes',['copo','veio','manipulo-porca','anilha-deslizamento'])]
 plan={'plates':[{'plate_name':name,'need_arrange':True,'objects':[item(k) for k in keys]} for name,keys in groups]}
 (w/'assembly.json').write_text(json.dumps(plan));common=['--datadir',str(w/'user'),'--debug','2']
 run_cli(b,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),'--load-filaments',str(w/'filament.json'),'--load-assemble-list',str(w/'assembly.json'),'--orient','0','--arrange','1','--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
 target=ROOT/'downloads'/f'{PREFIX}-A1-PETG-bico-0.4-3-pratos.3mf';annotate(w/'native.3mf',target,['#287D96'],PREFIX)
 blobs,settings,_=read_project(target);native=plate_meshes(blobs,settings)
 assert len(native)==3 and sum(len(p) for p in native)==11
 for plate,(_,keys) in zip(native,groups):
  remaining=[m for _,_,m in plate]
  for k in keys:
   ref=trimesh.load(ROOT/'downloads'/parts[k]['file'],force='mesh')
   matches=[m for m in remaining if abs(m.volume-ref.volume)<.1 and np.allclose(np.linalg.eigvalsh(m.moment_inertia),np.linalg.eigvalsh(ref.moment_inertia),rtol=.001,atol=.01)]
   assert matches,k
   m=matches[0];remaining.pop(next(i for i,v in enumerate(remaining) if v is m));assert m.is_watertight
   assert m.bounds[0,:2].min()>0 and m.bounds[1,:2].max()<254
 run_cli(b,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
 run_cli(b,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),'--export-3mf','validation.3mf',str(target)],w/'slice.log')
 result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0
 report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bambu_version':'02.08.02.61','native_export_reopen_slice_ok':True,'nozzle_mm':.4,'layer_height_mm':.16,'wall_loops':8,'infill_percent':100,'material':'Generic PETG','physical_print_tested':False,'plates':[]}
 for p in result['sliced_plates']:
  assert not p.get('warning_message'),p.get('warning_message')
  report['plates'].append({'id':p['id'],'estimated_seconds':p['total_predication'],'estimated_total_grams':sum(f['total_used_g'] for f in p['filaments']),'filament_changes':p['filament_change_times'],'warnings':p.get('warning_message')})
 (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
 if (FOLDER/'README.md').exists():package()
if __name__=='__main__':main()
