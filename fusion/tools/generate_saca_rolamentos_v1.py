"""All-polymer experimental bearing puller; generator parameters are in mm."""
from pathlib import Path
import json,math,hashlib
import numpy as np
import manifold3d as md
import trimesh
from PIL import Image,ImageDraw,ImageFont
from generate_coruja_bruna_v1 import path
from generate_m7_prototypes_v1 import rounded
from generate_coruja_bruna_v3 import exact,union
from generate_universo_stand import render_meshes
ROOT=Path(__file__).resolve().parents[2];FOLDER=ROOT/'fusion/SacaRolamentosV1';PREFIX='saca-rolamentos-v1'
P={'wheel_nominal_diameter':63,'bearing_bore':7,'bearing_outer':22,'bearing_width':7,
 'cup_outer':54,'cup_inner':34,'hub_contact_outer_PROVISIONAL':34,'hub_contact_inner_PROVISIONAL':24,
 'cup_height':53,'thread_major':30,'thread_root':27,'thread_pitch':6,'thread_length':80,
 'female_radial_clearance_PROVISIONAL':.35,'female_axial_clearance_PROVISIONAL':.15,
 'thread_engagement':26,'stroke_limit_MANUAL':12,'clevis_pin':8,'hook_thickness':3,
 'hook_envelopes_PROVISIONAL':[5.4,5.8,6.2],'material':'PETG','physical_tested':False}
def cyl(r,h):return md.Manifold.cylinder(h,r,r,96)
def box(a,b,c,x=0,y=0,z=0):return md.Manifold.cube((a,b,c)).translate((x,y,z))
def thread(length,clear=0,axial=0):
 n=128;nz=round(length/.10);theta=np.arange(n)*2*np.pi/n;verts=[]
 for z in np.linspace(0,length,nz+1):
  d=np.abs((z/P['thread_pitch']-theta/(2*np.pi)+.5)%1-.5)*P['thread_pitch']
  # Flat crest, broad root and printable sloped flanks. Custom profile, not ISO.
  r=13.5+clear+1.5*np.clip((2.2+axial-d)/1.35,0,1)
  verts.extend(np.c_[r*np.cos(theta),r*np.sin(theta),np.full(n,z)])
 faces=[]
 for j in range(nz):
  for i in range(n):
   a=j*n+i;b=j*n+(i+1)%n;c=b+n;d=a+n
   faces.extend([(a,b,c),(a,c,d)])
 low=len(verts);verts.append([0,0,0]);high=len(verts);verts.append([0,0,length])
 for i in range(n):
  faces.extend([(low,(i+1)%n,i),(high,nz*n+i,nz*n+(i+1)%n)])
 m=md.Manifold(md.Mesh(np.array(verts,np.float32),np.array(faces,np.uint32)))
 assert m.status()==md.Error.NoError
 return m

def hook(width):
 # Flat profile printed on its side. The head is 8 mm thick, all stems 3 mm.
 sec=path('M -7 -6 Q -10 -2 -8 4 Q -6 10 0 9 Q 8 9 9 2 Q 10 -3 6 -7 Q 3 -10 2 -15 L 1.9 -31 L 3.5 -31 Q 4 -31 4 -32 L 4 -34 Q 4 -35 3 -35 L -1 -35 Q -2 -35 -2 -33 L -2 -15 Q -2 -10 -7 -6 Z')
 # Replace toe outline by a controlled rectangular-rounded heel footprint.
 upper=sec^md.CrossSection.square((40,33)).translate((-20,-31))
 toe=rounded(-1.9,-35,width,4,1.0)
 sec=upper+toe
 solid=sec.extrude(3).translate((0,0,-1.5)).rotate((90,0,0))
 # Extrusion before rotation maps profile XY to world XZ, thickness along Y.
 head=md.Manifold.cylinder(8,9,9,64).rotate((90,0,0)).translate((0,4,0))
 solid+=head
 hole=cyl(4.2,14).rotate((90,0,0)).translate((0,7,0))
 solid-=hole
 return solid

def main():
 FOLDER.mkdir(exist_ok=True,parents=True)
 # Broad bottom reaction flange, with a smaller contact shoe touching the hub.
 cup=(cyl(17,4)-cyl(12,4))+(cyl(27,6)-cyl(12,6)).translate((0,0,4))
 cup+=(cyl(27,35)-cyl(17,35)).translate((0,0,10))
 guide=(cyl(15.5,10)^box(60,60,10,-40,-30,0)) # replace by a D-shaped guide below
 guide=cyl(15.5,10)-box(30,40,12,13.0,-20,-1)
 cup+=cyl(27,8).translate((0,0,45))-guide.translate((0,0,44))
 # Two inspection windows, preserving four wide load paths and roof/floor.
 for y in [-30,12]:cup-=box(16,18,30,-8,y,13)
 male=thread(80)-box(20,40,82,12.5,-20,-1)
 clevis=cyl(13.5,22).translate((0,0,-22))-box(32,8.7,19,-16,-4.35,-22)
 pinhole=cyl(4.2,40).rotate((90,0,0)).translate((0,20,-12))
 male+=clevis-pinhole
 male-=box(20,40,104,12.5,-20,-23)
 female=thread(30,.35,.15).translate((0,0,-2))
 nut=cyl(32,26)-female
 for i in range(12):
  ang=2*np.pi*i/12
  nut-=cyl(3.0,28).translate((33*math.cos(ang),33*math.sin(ang),-1))
 axle=cyl(4,34)+cyl(6,3).translate((0,0,-3))
 # Groove for a printed split retaining clip.
 axle-=(cyl(4.1,1.8)-cyl(3.3,1.8)).translate((0,0,30))
 clip=(cyl(6,1.6)-cyl(3.4,1.6))-box(3,12,3,-1.5,0,-.5)
 washer=cyl(27,1)-cyl(15.6,1)
 # Calibration coupon uses the exact male/female profile before full-size work.
 couponmale=(thread(14)-box(20,40,16,12.5,-20,-1))+cyl(19,3).translate((0,0,-3))
 couponnut=cyl(22,12)-thread(16,.35,.15).translate((0,0,-2))
 solids={'copo':cup,'veio':male,'manipulo-porca':nut,'eixo':axle,'clip':clip,'anilha-deslizamento':washer,
         'teste-rosca-macho':couponmale,'teste-rosca-porca':couponnut}
 for width in P['hook_envelopes_PROVISIONAL']:solids['gancho-'+str(width).replace('.','p')]=hook(width)
 entries=[]
 for name,solid in solids.items():
  target=ROOT/'downloads'/f'{PREFIX}-{name}.stl';m=exact(solid,target)
  # Hook/pin layers run along the loaded axis; rotate the broad profile to bed.
  if name.startswith('gancho'):mat=trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0])
  elif name=='eixo':mat=trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0])
  else:mat=np.eye(4)
  m.apply_transform(mat);m.apply_translation(-m.bounds[0]);m.export(target)
  read=trimesh.load(target,force='mesh');assert read.is_watertight
  entries.append({'key':name,'file':target.name,'dimensions_mm':read.extents.tolist(),'volume_mm3':read.volume,'watertight':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 # Validate rotational thread registration and the D guide at three positions.
 collisions=[]
 for turns in [0,.25,.5,1]:
  overlap=(male.rotate((0,0,turns*360)).translate((0,0,turns*6))^nut.translate((0,0,20))).volume()
  collisions.append(overlap)
 assert max(collisions)<.02,collisions
 # Assembled frame: nut above cup, male thread begins at 35mm, pin at23mm.
 scene=[(cup,'#303E49'),(washer.translate((0,0,53)),'#697C87'),(nut.rotate((0,0,240)).translate((0,0,54)),'#1767A0'),
        (male.translate((0,0,36)),'#287DB6'),(solids['gancho-5p8'].translate((0,0,24)),'#E98525')]
 axle_pose=axle.rotate((90,0,0)).translate((0,15,24))
 clip_pose=clip.rotate((90,0,0)).translate((0,-15.1,24))
 scene.extend([(axle_pose,'#8BA2AF'),(clip_pose,'#8BA2AF')])
 collisions_assembled=[]
 for i,(a,_) in enumerate(scene):
  for j,(b,_) in enumerate(scene[i+1:],i+1):
   vol=(a^b).volume()
   if vol>.01:collisions_assembled.append([i,j,vol])
 assert not collisions_assembled,collisions_assembled
 motion_checks=[]
 for travel in [0,3,6,12]:
  moving=[male.translate((0,0,36+travel)),solids['gancho-5p8'].translate((0,0,24+travel)),axle_pose.translate((0,0,travel)),clip_pose.translate((0,0,travel))]
  clearance_volumes=[(s^cup).volume() for s in moving]
  nut_at=nut.rotate((0,0,240-360*travel/6)).translate((0,0,54))
  clearance_volumes.append((moving[0]^nut_at).volume())
  assert max(clearance_volumes)<.01,(travel,clearance_volumes)
  motion_checks.append({'travel_mm':travel,'collision_volumes_mm3':clearance_volumes})
 # Cutaway slices are only drawing geometry; exported parts remain complete.
 clipview=box(100,60,180,-50,-60,-35)
 cut=[(s-clipview,c) if i in [0,1,2] else (s,c) for i,(s,c) in enumerate(scene)]
 sheet=Image.new('RGB',(1800,1100),'#F4F6F8');d=ImageDraw.Draw(sheet)
 f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
 sheet.paste(render_meshes(scene,(850,920),direction=(.9,-1,.5),margin=40),(0,90))
 sheet.paste(render_meshes(cut,(850,920),direction=(.3,-1,.3),margin=40),(900,90))
 d.text((30,20),'Saca-rolamentos V1 · protótipo de estudo · geometria exportada',font=f(32),fill='#233847')
 d.text((30,1035),'Rosca Ø30 / passo 6 · copo Ø54 · apoio Ø34/24 por confirmar · sem carga certificada',font=f(25),fill='#233847')
 sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
 report={'parameters':P,'parts':entries,'thread_collision_volumes_mm3':collisions,'assembled_collisions':collisions_assembled,'motion_clearance_checks':motion_checks,
  'fit_status':'provisional: wheel hub, spacer access and hook engagement unmeasured',
  'assembly':'cup z0; washer z53; nut z54; male thread bottom z36; pin center z24; hook pivot z24',
  'max_stroke_mm':12,'physical_print_tested':False,'certified_load':None}
 (FOLDER/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
 (FOLDER/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
 print(json.dumps({'parts':len(entries),'thread_collision_volumes_mm3':collisions},indent=2),flush=True)
if __name__=='__main__':main()
