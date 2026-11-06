"""Parametric mesh model, mm: integrated gray wolf, continuous white cheeks.

Not an Autodesk Fusion runtime script. Body upright; eight colored modules
print with a common flat back in each assembly. No print is sent to a machine.
"""
import json,math,re
from pathlib import Path
import cv2
import numpy as np
import manifold3d as md
import trimesh
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import PchipInterpolator
from generate_m7_prototypes_v1 import union,transformed
from generate_universo_stand import render_meshes

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'fusion/AnilhaLobitoV5'
PREFIX='anilha-lobito-v5-bochechas-continuas'
GRAY,WHITE,BLACK='#777B82','#F5F3ED','#191A1E'
H=30.;CLEARANCE=.18;GLUE=.15;SEG=128
RAD=PchipInterpolator([0,.5,1.5,3,6,10,15,20,24,27,28.5,29.5,30],
                     [18.3,18.9,19.5,20,20.5,20.9,21,20.9,20.5,20,19.5,18.9,18.3])

def path(text):
    tokens=re.findall(r'[MLCQZ]|-?\d*\.?\d+',text);p=[];i=0;cur=np.zeros(2)
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd=='Z':break
        n={'M':2,'L':2,'Q':4,'C':6}[cmd]
        q=np.array(list(map(float,tokens[i:i+n]))).reshape(-1,2);i+=n
        if cmd in ('M','L'):cur=q[0];p.append(cur)
        else:
            a=cur.copy()
            for t in np.linspace(0,1,49)[1:]:
                v=(1-t)**3*a+3*(1-t)**2*t*q[0]+3*(1-t)*t*t*q[1]+t**3*q[2] if cmd=='C' else (1-t)**2*a+2*(1-t)*t*q[0]+t*t*q[1]
                p.append(v)
            cur=q[-1]
    return md.CrossSection([[v.tolist() for v in p]],md.FillRule.EvenOdd).simplify(.002)

def ell(c,r):return md.Manifold.sphere(1,SEG).scale(r).translate(c)
def ellipse(x,z,rx,rz):return md.CrossSection.circle(1,256).scale((rx,rz)).translate((x,z))
def clip(y):return md.Manifold.cube((100,80,60)).translate((-50,y-80,-5))
def prism(profile,back_y):return profile.extrude(60).transform([[1,0,0,0],[0,0,-1,back_y],[0,1,0,0]])
def foot(s):return s.transform([[1,0,0,0],[0,0,1,0],[0,-1,0,0]]).project().simplify(.002)
def flat_convex(s,back_y):return md.Manifold.batch_hull([s,s.translate((0,30,0))]) ^ clip(back_y)
def cy(x,z):return -math.sqrt(max(.1,float(RAD(np.clip(z,0,H)))**2-x*x))
def sculpt(profile,back,front):
    # Refine the front surface before warping; a thin extrusion alone would
    # retain large flat triangles and lose the intended rounded surface.
    mesh=profile.extrude(1).refine_to_length(.25)
    def warp(v):
        x,z,t=v[:,0],v[:,1],v[:,2]
        y=back+t*(front(x,z)-back)
        return np.column_stack((x,y,z))
    return mesh.warp_batch(warp)

def rounded_cheeks(profile,back):
    loops=[np.asarray(p,dtype=np.float32) for p in profile.to_polygons()]
    def front(x,z):
        dist=np.array([max(cv2.pointPolygonTest(p,(float(a),float(b)),True) for p in loops) for a,b in zip(x,z)])
        edge=np.clip(dist/.3,0,1)
        roll=.3*(1-np.sqrt(np.maximum(0,1-(1-edge)**2)))
        return -np.sqrt(23**2-x*x)+roll-.18*(1-np.exp(-np.maximum(dist,0)/1.5))
    return sculpt(profile,back,front)

def bounds(s):return np.array(s.bounding_box()).reshape(2,3)
def pose(back_y):return np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,back_y],[0,0,0,1]],float)
def save(s,name):
    assert s.status()==md.Error.NoError,(name,s.status())
    m=s.simplify(.001).to_mesh()
    mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces(height=1e-7));mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent,(name,'mesh topology')
    file=ROOT/'downloads'/f'{PREFIX}-{name}.stl';mesh.export(file)
    check=trimesh.load(file,force='mesh')
    assert check.is_watertight and check.is_winding_consistent,name
    return dict(key=name,file=file.name,volume_mm3=float(check.volume),dimensions_mm=check.extents.tolist(),triangles=len(check.faces),watertight=True)

def make():
    OUT.mkdir(exist_ok=True)
    zz=np.linspace(0,H,161)
    shell=md.CrossSection([[(0,0)]+[(float(RAD(z)),float(z)) for z in zz]+[(0,H)]]).revolve(256)
    bore=md.CrossSection.circle(1,100).scale((12.5,9))
    hole=bore.extrude(45).translate((0,0,-1))
    entry=md.Manifold.cylinder(.8,13.3,12.5,128).scale((1,.72,1))
    exit=md.Manifold.cylinder(.8,12.5,13.3,128).scale((1,.72,1)).translate((0,0,H-.8))
    ring=shell-union([hole,entry,exit]);ears=[];modules=[]
    for sign,label in [(-1,'esquerda'),(1,'direita')]:
        ear=md.Manifold.batch_hull([ell((sign*12.6,-14.8,28.5),(3.8,2.15,3.1)),ell((sign*16.1,-14.45,35.5),(1.45,1.5,1.7)),ell((sign*16.5,-14.25,37),(.55,.85,.65)),ell((sign*17.5,-14.5,30.8),(1.4,1.7,2.2))])
        ears.append(ear)
        inset=md.Manifold.batch_hull([ell((sign*13,-16.6,30),(1.75,.85,1)),ell((sign*15.9,-16,34.7),(.6,.7,.85)),ell((sign*16.3,-16.4,30.6),(.65,.8,.85))])
        back=-14.9;inset=flat_convex(inset,back)
        modules.append(dict(key='orelha-'+label,back=back,parts=[('branco',inset)],profile=foot(inset),receiver='corpo'))
    body=union([ring,*ears]);print('base integrated',flush=True)
    # A single smooth cheek patch on each side. Tufts only define the outer
    # contour: no separate ribs, rods, grooves or gray gaps inside the cheeks.
    right=path('M 7.8 4.0 C 10.6 3.5 13.3 4.4 15.8 5.4 C 17.0 6.0 17.8 6.8 17.4 7.3 C 17.0 7.7 16.5 7.8 16.2 8.0 C 18.4 8.8 19.0 10.1 18.7 10.6 C 18.5 11.0 17.7 10.8 17.1 10.7 C 18.6 12.1 19.4 14.8 18.5 15.6 C 18.1 15.9 17.6 14.7 16.5 14.1 C 13.5 12.3 10.6 13.2 8.1 11.8 C 6.6 9.0 6.8 6.4 7.8 4.0 Z')
    right=right.offset(-.25,circular_segments=64).offset(.25,circular_segments=64)
    cheeks=right+right.mirror((1,0));back=-11.2
    cheek_volume=rounded_cheeks(cheeks,back)
    muzzle_original=ell((0,-20.45,8.1),(11.5,3.6,7.4))
    muzzle=union([flat_convex(muzzle_original,back),cheek_volume])
    smile=path('M -6.4 9.0 C -3.5 7.3 3.5 7.3 6.4 9.0 C 5.4 5.9 3.0 2.2 0 2.15 C -3.0 2.2 -5.4 5.9 -6.4 9.0 Z')
    tongue_profile=path('M -2.8 4.2 C -2.5 5.3 -1.0 5.7 0 4.8 C 1.0 5.7 2.5 5.3 2.8 4.2 C 2.0 2.8 1.0 2.3 0 2.3 C -1.0 2.3 -2.0 2.8 -2.8 4.2 Z')
    mouth=(muzzle_original.translate((0,-.05,0))-muzzle_original.translate((0,.75,0))) ^ prism(smile,0)
    tongue=(muzzle_original.translate((0,-.10,0))-muzzle_original.translate((0,.80,0))) ^ prism(tongue_profile,0)
    mouth-=prism(tongue_profile,0)
    muzzle_white=union([muzzle,tongue])-mouth
    # Nose is separate, with a matching flat-bottom seat in the white muzzle.
    nose=md.Manifold.batch_hull([ell((-2.1,-23.65,13.7),(1.65,1.45,1.35)),ell((2.1,-23.65,13.7),(1.65,1.45,1.35)),ell((0,-23.75,11.85),(1.6,1.3,1.1))])
    nose_back=-22.25;nose=flat_convex(nose,nose_back)
    nose_profile=foot(nose);nose_seat=prism(nose_profile.offset(CLEARANCE,circular_segments=64),nose_back+GLUE)
    muzzle_white-=nose_seat;mouth-=nose_seat
    modules.append(dict(key='focinho-bochechas',back=back,parts=[('branco',muzzle_white),('preto',mouth)],profile=foot(muzzle),receiver='corpo'))
    modules.append(dict(key='nariz',back=nose_back,parts=[('preto',nose)],profile=nose_profile,receiver='focinho-bochechas'))
    print('continuous cheeks and muzzle',flush=True)
    for sign,label in [(-1,'esquerdo'),(1,'direito')]:
        prof=ellipse(sign*7.6,20.1,4.8,5.2);back=-15.8
        def eye_front(x,z):
            radius=RAD(np.clip(z,0,H))
            dome=np.sqrt(np.maximum(0,1-((x-sign*7.6)/4.8)**2-((z-20.1)/5.2)**2))
            return -np.sqrt(np.maximum(.1,radius*radius-x*x))-.25-1.45*dome
        eye=sculpt(prof,back,eye_front)
        pupil=ell((sign*6.55,-21.0,18.85),(2,1.2,2.75)) ^ clip(-20.1)
        glint=ell((sign*6.15,-21.9,20.4),(.62,.52,.68))
        white=union([eye,glint])-pupil;white=union([white,glint]);black=pupil-glint
        modules.append(dict(key='olho-'+label,back=back,parts=[('branco',white),('preto',black)],profile=prof,receiver='corpo'))
        centers=[(sign*(5.3+6.1*t),26.9+1.15*math.sin(math.pi*t)) for t in np.linspace(0,1,41)]
        disks=[ellipse(x,z,.62,.62) for x,z in centers]
        brow_profile=md.CrossSection.batch_boolean([md.CrossSection.batch_hull([a,b]) for a,b in zip(disks,disks[1:])],md.OpType.Add).simplify(.002)
        back=-14.5
        cp=np.array(centers)
        def brow_front(x,z):
            rr=RAD(np.clip(z,0,H))
            dist=np.min((x[:,None]-cp[:,0])**2+(z[:,None]-cp[:,1])**2,axis=1)
            return -np.sqrt(np.maximum(.1,rr*rr-x*x))-.12-.6*np.sqrt(np.maximum(0,1-dist/.62**2))
        brow=sculpt(brow_profile,back,brow_front)
        modules.append(dict(key='sobrancelha-'+label,back=back,parts=[('preto',brow)],profile=foot(brow),receiver='corpo'))
    # Recesses with lateral clearance and a bottom glue gap. No gray carrier is
    # separated. Each colored module has a flat printed back, not guide pins.
    for m in modules:
        if m['receiver']=='corpo':body-=prism(m['profile'].offset(CLEARANCE,circular_segments=64),m['back']+GLUE)
    assert body.status()==md.Error.NoError
    body_components=[s for s in body.decompose() if s.volume()>.01]
    assert len(body_components)==1,[(p.volume(),p.bounding_box()) for p in body_components]
    body=body_components[0]
    assert (body ^ bore.offset(-.01).extrude(43)).volume()<.005
    print('body pockets cut',flush=True)
    parts=[save(body,'corpo')];parts[0].update(color=GRAY,slot=1,module='corpo')
    modreport=[];world=[(body,GRAY)];interference=[]
    world_modules={}
    for m in modules:
        env=union([s for _,s in m['parts']]);world_modules[m['key']]=env
        cs=[s for s in env.decompose() if s.volume()>.01]
        assert len(cs)==1,(m['key'],'module disconnected',[(p.volume(),p.bounding_box()) for p in cs])
        assert abs(bounds(env)[1,1]-m['back'])<.003,(m['key'],'back not planar')
        intersect=(env ^ body).volume();assert intersect<.005,(m['key'],intersect)
        interference.append(intersect)
        pf=pose(m['back']);print_parts=[]
        for color,s in m['parts']:
            if s.is_empty():continue
            printed=transformed(s,pf);key=m['key']+'-'+color
            p=save(printed,key);p.update(color=WHITE if color=='branco' else BLACK,slot=2 if color=='branco' else 3,module=m['key'])
            parts.append(p);print_parts.append(key);world.append((s,p['color']))
        area=transformed(env,pf).slice(.05).area();assert area>.3,(m['key'],'contact area')
        modreport.append(dict(key=m['key'],parts=print_parts,back_plane_y_mm=m['back'],print_to_world=np.linalg.inv(pf).tolist(),receiver=m['receiver'],flat_back=True,contact_area_z_0_05_mm2=area,one_connected_assembled_module=True))
        print('saved',m['key'],flush=True)
    pairs=[]
    for i,a in enumerate(modules):
        for b in modules[i+1:]:
            v=(world_modules[a['key']] ^ world_modules[b['key']]).volume()
            assert v<.005,('module interference',a['key'],b['key'],v)
            if v>1e-6:pairs.append([a['key'],b['key'],v])
    data=dict(parameters=dict(bore_opening_mm=[25,18],body_height_mm=H,max_body_width_mm=42,overall_height_mm=float(bounds(body)[1,2]),lateral_clearance_each_side_mm=CLEARANCE,bottom_glue_gap_mm=GLUE,sphere_segments=SEG,barrel_segments=256,outline_tolerance_mm=.002,mesh_simplification_mm=.001,sculpt_refinement_mm=.25),parts=parts,modules=modreport,glued_modules=8,body_connected=True,opening_clear=True,body_module_interference_mm3=max(interference),module_pair_interference=pairs,physical_fit_tested=False,physical_print_tested=False,modelling_route='Parametric manifold3d mesh script; not an executed Fusion document',concept='Approved direction: continuous cheeks, whole gray body, white/black flat-backed glue modules',quality_intent=dict(layer_height_mm=.12,outer_wall_speed_mm_s=30,top_surface_speed_mm_s=20,ironing=False))
    (OUT/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    preview(world,body)
    print('geometry verified and previews saved',flush=True)


def preview(world,body):
    f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    im=Image.new('RGB',(1600,1100),'#f4f6f8');d=ImageDraw.Draw(im)
    d.text((35,25),'Lobito V5 · bochechas contínuas',font=f(36),fill='#233347')
    d.text((35,82),'Corpo cinzento inteiro · 8 elementos para colar · costas planas',font=f(24),fill='#536276')
    im.paste(render_meshes(world,(810,820),direction=(0,-1,.3),margin=45),(0,145))
    im.paste(render_meshes(world,(770,820),direction=(.65,-1,.6),margin=45),(820,145))
    d.text((35,1000),'Abertura oval 25 × 18 mm · corpo 30 mm · camadas propostas de 0,12 mm',font=f(23),fill='#536276')
    d.text((35,1045),'Prévia da geometria real · ajuste e acabamento físico ainda por testar',font=f(22),fill='#536276')
    im.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    im2=Image.new('RGB',(1300,1000),'#f4f6f8');d=ImageDraw.Draw(im2)
    d.text((35,25),'Corpo inteiro e alojamentos de colagem',font=f(32),fill='#233347')
    im2.paste(render_meshes([(body,GRAY)],(1230,800),direction=(.35,-1,.45),margin=50),(35,100))
    d.text((35,935),'Folga lateral 0,18 mm por lado · fundo 0,15 mm para cola · sem pinos',font=f(23),fill='#536276')
    im2.save(ROOT/'designs'/f'{PREFIX}-encaixe.png')

if __name__=='__main__':make()
