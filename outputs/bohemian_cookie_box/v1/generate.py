"""Parametric geometry generator. Same dimensions/profile as cookie_box.scad."""
from pathlib import Path
import json,math,sys,subprocess,hashlib
import numpy as np
import manifold3d as md
import trimesh
from PIL import Image,ImageDraw,ImageFont
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
from generate_coruja_bruna_v3 import exact,union
from generate_anilha_aquela_v3 import solid_from_mesh
from generate_universo_stand import render_meshes
P=json.loads((FOLDER/'parameters.json').read_text())
N=P['segments'];R=P['cookie_diameter']/2+P['cookie_radial_clearance']
ROOT_R=R+P['wall'];BODY_H=P['base']+P['stack_height']+P['top_clearance']
LID_H=P['lid_face']+P['lid_skirt'];LID_R=ROOT_R+P['thread_depth']+P['thread_radial_clearance']+P['lid_wall']
ASSEMBLY_Z=BODY_H+P['lid_face']
THREAD_Z=BODY_H-P['thread_top_margin']-P['thread_base_width']/2-P['turns']*P['pitch']
TEST_BOTTOM=THREAD_Z-P['thread_base_width']/2-.6
BLACK='#111115';PURPLE='#582465';GOLD='#DDB34E';DARK='#242428';WHITE='#EEEDE8'


def cyl(r,h,z=0,r2=None):
    return md.Manifold.cylinder(h,r,r if r2 is None else r2,N).translate((0,0,z))


def thread(clearance=0,axial=0,female=False):
    start=-360 if female else 0
    span=360*P['turns']-start
    n=math.ceil(P['thread_segments_per_turn']*span/360);verts=[];faces=[]
    for i in range(n+1):
        a=math.radians(start+i*span/n)
        f=1 if female else min(1,math.degrees(a)/P['thread_ramp_degrees'],(360*P['turns']-math.degrees(a))/P['thread_ramp_degrees'])
        rr=[ROOT_R+clearance-P['thread_embed'],ROOT_R+clearance+P['thread_depth']*f]*2
        profile=[(rr[0],-P['thread_base_width']/2-axial),
                 (rr[1],-P['thread_crest_width']/2-axial),
                 (rr[1],P['thread_crest_width']/2+axial),
                 (rr[0],P['thread_base_width']/2+axial)]
        verts.extend([[r*math.cos(a),r*math.sin(a),THREAD_Z+a/(2*math.pi)*P['pitch']+z] for r,z in profile])
    faces.extend([[0,1,2],[0,2,3]])
    for i in range(n):
        for j in range(4):
            q=(j+1)%4
            faces.extend([[4*i+j,4*(i+1)+j,4*(i+1)+q],[4*i+j,4*(i+1)+q,4*i+q]])
    faces.extend([[4*n+3,4*n+2,4*n+1],[4*n+3,4*n+1,4*n]])
    m=trimesh.Trimesh(verts,faces,process=True)
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    s=md.Manifold(md.Mesh64(np.asarray(m.vertices,dtype='float64'),np.asarray(m.faces,dtype='uint64')))
    assert s.status()==md.Error.NoError
    return s


def body():
    return (cyl(ROOT_R,BODY_H-.5)+cyl(ROOT_R,.5,BODY_H-.5,ROOT_R-.5)+thread())-cyl(R,BODY_H+.02,P['base'])


def lid(clearance=None):
    c=P['thread_radial_clearance'] if clearance is None else clearance
    cavity=cyl(ROOT_R+c,P['lid_skirt']+.02,P['lid_face'])
    ch=P['entry_chamfer']
    cavity+=cyl(ROOT_R+c,ch+.02,LID_H-ch,ROOT_R+c+ch+.02)
    groove=thread(c,P['thread_axial_clearance'],True).rotate((180,0,0)).translate((0,0,ASSEMBLY_Z))
    cavity+=groove^cyl(LID_R+1,P['lid_skirt']+.02,P['lid_face'])
    return cyl(LID_R,LID_H)-cavity


def decals():
    gold=solid_from_mesh(FOLDER/'stl/tampa-dourado.stl')
    label=cyl(P['label_diameter']/2,P['color_depth'])
    assert (gold-label).volume()<.001
    purple=label-gold
    rings=[]
    for r in np.arange(P['label_diameter']/2+2,LID_R-2+.00001,2.4):
        rings.append(cyl(r+P['ring_width']/2,P['color_depth'])-cyl(r-P['ring_width']/2,P['color_depth']))
    return gold,purple,union(rings)


def main():
    (FOLDER/'parameters.scad').write_text('// Valores provisorios; unidades mm.\n'+'\n'.join(k+' = '+json.dumps(v)+';' for k,v in P.items())+'\n')
    subprocess.run(['openscad','-o',str(FOLDER/'stl/tampa-dourado.stl'),'-D','part="lid_gold"',str(FOLDER/'cookie_box.scad')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    b=body();l=lid();gold,purple,rings=decals()
    black=l-gold-purple;black_rings=black-rings
    items={'corpo':(b,BLACK),'tampa-preto':(black,BLACK),'tampa-roxo':(purple,PURPLE),'tampa-dourado':(gold,GOLD),
           'tampa-preto-aneis':(black_rings,BLACK),'tampa-aneis-tonais':(rings,DARK),'tampa-completa-monocor':(l,BLACK),
           'amostra-acabamento':(cyl(22.5,1.2),BLACK)}
    male=(b^cyl(LID_R+2,BODY_H-TEST_BOTTOM+.02,TEST_BOTTOM)).translate((0,0,-TEST_BOTTOM))
    items['teste-macho']=(male,BLACK)
    for c,marks in [(.25,1),(.30,2),(.40,3)]:
        female=(lid(c)-cyl(LID_R+1,P['lid_face']+.02,-.02)).translate((0,0,-P['lid_face']))
        for i in range(marks):
            mark=cyl(.45,.7,P['lid_skirt']-.6).translate((LID_R-.15,0,0)).rotate((0,0,i*12))
            female-=mark
        items[f'teste-femea-{int(c*100):03}']=(female,BLACK)
    report=[]
    for name,(s,color) in items.items():
        assert s.status()==md.Error.NoError,(name,s.status())
        mesh=exact(s,FOLDER/'stl'/f'{name}.stl')
        if name in ('corpo','tampa-completa-monocor','teste-macho') or name.startswith('teste-femea'):
            assert len([p for p in s.decompose() if p.volume()>1e-6])==1,name
        report.append({'name':name,'file':'stl/'+name+'.stl','color':color,'dimensions_mm':mesh.extents.tolist(),
                       'volume_mm3':mesh.volume,'watertight':True,'sha256':hashlib.sha256((FOLDER/'stl'/f'{name}.stl').read_bytes()).hexdigest()})
    for combo in [[black,purple,gold],[black_rings,purple,gold,rings]]:
        for i,a in enumerate(combo):
            for c in combo[i+1:]:assert (a^c).volume()<.001
        combined=union(combo)
        assert (combined-l).volume()+(l-combined).volume()<.001
        assert len([p for p in combined.decompose() if p.volume()>1e-6])==1
        assert abs(combined.bounding_box()[2])<.001
    collisions=[]
    for c in (.25,.30,.40):
        female=lid(c)
        for angle in [0,30,60,90,180,270,360,450,540,720]:
            placed=female.rotate((180,0,0)).rotate((0,0,angle)).translate((0,0,ASSEMBLY_Z+P['pitch']*angle/360))
            v=(b^placed).volume();collisions.append({'radial_clearance_mm':c,'unscrew_degrees':angle,'collision_mm3':v})
            assert v<.02,(c,angle,v)
    # Verify available cylindrical capacity, including the full 42 mm height.
    usable=cyl(R-.001,P['stack_height']+P['top_clearance']-.002,P['base']+.001)
    assert (b^usable).volume()<.001
    closed=l.rotate((180,0,0)).translate((0,0,ASSEMBLY_Z))
    assert (closed^usable).volume()<.001
    report_data={'parameters_provisional':True,'existing_source_found':False,'parameters':P,
        'inner_diameter_mm':2*R,'usable_height_mm':P['stack_height']+P['top_clearance'],
        'smooth_body_diameter_mm':2*ROOT_R,'thread_major_diameter_mm':2*(ROOT_R+P['thread_depth']),
        'lid_diameter_mm':2*LID_R,'closed_height_mm':ASSEMBLY_Z,'lid_print_height_mm':LID_H,
        'nominal_radial_cookie_liner_allowance_mm':P['cookie_radial_clearance'],
        'axial_stop':'lid inner roof contacts body rim at Z=body_h; zero intended volume overlap',
        'face_flat_z_mm':0,'color_depth_mm':P['color_depth'],'same_origin_color_parts':True,
        'thread_flank_angle_from_vertical_degrees':math.degrees(math.atan(P['thread_depth']/((P['thread_base_width']-P['thread_crest_width'])/2))),
        'interference_checks':collisions,'parts':report,'physical_fit_tested':False,'food_barrier_required':True}
    (FOLDER/'validation/geometry.json').write_text(json.dumps(report_data,indent=2)+'\n')
    # Color volumes are identical to the STL exports. Closed and open positions.
    top=[(x.rotate((180,0,0)).translate((0,0,ASSEMBLY_Z)),c) for x,c in [(black,BLACK),(purple,PURPLE),(gold,GOLD)]]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    image=Image.new('RGB',(1600,1100),'#f4f3f0');d=ImageDraw.Draw(image)
    d.text((35,25),'Bohemian Rhapsody · caixa para seis bolachas Maria',font=font(32),fill='#24222A')
    image.paste(render_meshes([(b,WHITE)]+top,(780,850),direction=(.6,-1,.9),margin=45),(0,100))
    image.paste(render_meshes([(b,BLACK)]+[(x.translate((0,0,18)),c) for x,c in top],(780,850),direction=(.6,-1,1),margin=45),(810,100))
    d.text((35,980),'Interior provisório: Ø70 × 42 mm · tampa Ø80,2 mm · rosca 1,25 voltas',font=font(25),fill='#24222A')
    d.text((35,1030),'Corpo liso · barreira alimentar removível obrigatória · impressão física por testar',font=font(23),fill='#55515E')
    image.save(FOLDER/'images/conjunto-CAD.png')
    view=[]
    for x,c in [(black,BLACK),(purple,PURPLE),(gold,GOLD)]:view.append((x.rotate((180,0,0)).translate((0,0,LID_H)),c))
    face=render_meshes([(x.rotate((90,0,0)),c) for x,c in view],(1000,1000),direction=(0,-1,0),margin=40)
    sheet=Image.new('RGB',(1080,1180),'#f4f3f0');sheet.paste(face,(40,70));d=ImageDraw.Draw(sheet)
    d.text((35,20),'Face plana · vista depois de retirar do prato',font=font(28),fill='#24222A')
    d.text((35,1090),'Preto + roxo + dourado · sem relevo decorativo',font=font(25),fill='#24222A')
    d.text((35,1130),'As marcas do preto dependem dos percursos e do acabamento do PEI.',font=font(21),fill='#55515E')
    sheet.save(FOLDER/'images/face-vinil-CAD.png')
    print(json.dumps({k:v for k,v in report_data.items() if k not in ('parts','parameters','interference_checks')},indent=2),flush=True)


if __name__=='__main__':main()
