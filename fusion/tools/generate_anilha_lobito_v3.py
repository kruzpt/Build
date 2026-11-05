"""Rounded barrel wolf woggle with a sculpted, glue-on curved face. Units: mm.

The visible face is a rounded barrel cap, not a flat plaque. A hidden chord
provides a defined locating recess and glue seat. Mesh generation is independent
of Autodesk Fusion; the proposed assembly still needs a physical fit test.
"""
import json,math
from pathlib import Path
import manifold3d as md
import numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image,ImageDraw,ImageFont
from generate_m7_prototypes_v1 import union,rounded,transformed
from generate_coruja_bruna_v1 import path
from generate_joana_topper import save_mesh
from generate_universo_stand import render_meshes

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/AnilhaLobitoV3'
PREFIX='anilha-lobito-v3-costas-lisas'
COLORS=['#777B82','#F5F3ED','#191A1E']
H=30.
RADIUS=PchipInterpolator([0,.5,1.5,3,6,10,15,20,24,27,28.5,29.5,30],
                        [18.3,18.9,19.5,20,20.5,20.9,21,20.9,20.5,20,19.5,18.9,18.3])


def ellipsoid(center,radii,segments=64):
    return md.Manifold.sphere(1,segments).scale(radii).translate(center)


def front_mask(profile):
    # Cross-section local XY=(world X,world Z); extrusion goes towards front -Y.
    return profile.extrude(45).transform([[1,0,0,0],[0,0,-1,0],[0,1,0,0]])


def clean(solid):
    assert solid.status()==md.Error.NoError,solid.status()
    pieces=[p for p in solid.simplify(.001).decompose() if p.volume()>1e-5]
    return union(pieces)


def surface_y(x,z):
    r=float(RADIUS(np.clip(z,0,H)))
    return -math.sqrt(max(.1,r*r-x*x))


def barrel():
    z=np.linspace(0,H,81)
    pts=[(0,0)]+[(float(RADIUS(t)),float(t)) for t in z]+[(0,H)]
    return md.CrossSection([pts],md.FillRule.EvenOdd).revolve(192)


def make():
    FOLDER.mkdir(exist_ok=True)
    shell=barrel()
    bore=md.CrossSection.circle(1,100).scale((12.5,9))
    hole=bore.extrude(H+12).translate((0,0,-1))
    entry=md.Manifold.cylinder(.8,13.3,12.5,100).scale((1,.72,1))
    exit=md.Manifold.cylinder(.8,12.5,13.3,100).scale((1,.72,1)).translate((0,0,H-.8))
    ring=shell-union([hole,entry,exit])
    # The split is hidden behind the rounded front cap. The cap's curved
    # exterior is the original barrel surface and restores its round outline.
    front_half=md.Manifold.cube((60,30,44)).translate((-30,-44,0)) # ends at Y=-14
    body=ring-front_half
    cap_half=md.Manifold.cube((60,30,44)).translate((-30,-44.15,0))
    cap=ring ^ cap_half
    key_profile=rounded(-10,4,20,22,1.4)
    # Actual body front is Y=-14. Recess floor Y=-12.65. Cap back Y=-14.15.
    recess=key_profile.extrude(1.85).transform([[1,0,0,0],[0,0,-1,-12.65],[0,1,0,0]])
    body-=recess
    key=key_profile.offset(-.2,circular_segments=32).extrude(1.35).transform(
        [[1,0,0,0],[0,0,-1,-12.8],[0,1,0,0]])
    # Subtract a slightly expanded body from sculpt details outside the cap.
    # This prevents the cheek tips/ear feet binding on the curved side surface.
    keep_clear=body.scale((1.005,1.005,1))
    ears=[];inner_ears=[]
    for sign in (-1,1):
        ear=md.Manifold.batch_hull([
            ellipsoid((sign*12.6,-14.8,28.5),(3.8,2.15,3.1)),
            ellipsoid((sign*16.1,-14.45,35.5),(1.45,1.5,1.7)),
            ellipsoid((sign*16.5,-14.25,37.0),(.55,.85,.65)),
            ellipsoid((sign*17.5,-14.5,30.8),(1.4,1.7,2.2))])
        ear=ear-keep_clear
        inner=md.Manifold.batch_hull([
            ellipsoid((sign*13.0,-16.6,30.0),(1.75,.85,1.0)),
            ellipsoid((sign*15.9,-16.0,34.7),(.6,.7,.85)),
            ellipsoid((sign*16.3,-16.4,30.6),(.65,.8,.85))])-keep_clear
        ears.append(ear);inner_ears.append(inner)
    grey_base=union([cap,key,*ears])
    muzzle=ellipsoid((0,-20.45,8.1),(11.5,3.6,7.4))
    eye_bases=[];pupils=[];glints=[]
    for sign in (-1,1):
        x=sign*7.6
        eye=ellipsoid((x,-18.75,20.1),(4.8,2.55,5.2))
        pupil=ellipsoid((sign*6.55,-21.0,18.85),(2.0,1.2,2.75))
        glint=ellipsoid((sign*6.15,-21.9,20.4),(.62,.52,.68))
        eye_bases.append(eye);pupils.append(pupil);glints.append(glint)
    cheeks=[]
    cheek_skin=shell.scale((1.04,1.04,1))-shell.scale((.995,.995,1))
    for sign in (-1,1):
        # Continuous curved white cheek beneath the three lobes. The lobes
        # leave only small notches at the outer edge, rather than whisker rods.
        backing_profile=md.CrossSection.circle(1,96).scale((4.5,4.8)).translate((sign*12.5,10.1))
        cheeks.append((cheek_skin ^ front_mask(backing_profile))-keep_clear)
        for ax,az,mx,mz,bx,bz,r in [(8.8,12.0,13.1,12.9,17.8,15.2,1.85),
                                   (9.8,9.3,13.7,10.1,18.3,11.7,1.85),
                                   (9.3,6.7,12.9,7.1,16.8,8.1,1.65)]:
            a=(sign*ax,surface_y(ax,az)-.65,az)
            middle=(sign*mx,surface_y(mx,mz)-.35,mz)
            b=(sign*bx,surface_y(bx,bz)-.25,bz)
            tuft=md.Manifold.batch_hull([ellipsoid(a,(2.4,1.3,r)),
                                         ellipsoid(middle,(2.6,.95,r)),
                                         ellipsoid(b,(.65,.65,.6))])
            lobe_profile=md.CrossSection.batch_hull([
                md.CrossSection.circle(1,64).scale((2.4,r)).translate((sign*ax,az)),
                md.CrossSection.circle(1,64).scale((2.6,r)).translate((sign*mx,mz)),
                md.CrossSection.circle(1,64).scale((.65,.6)).translate((sign*bx,bz))])
            cheeks.append((cheek_skin ^ front_mask(lobe_profile))-keep_clear)
            cheeks.append(tuft-keep_clear)
    white_base=union([muzzle,*eye_bases,*cheeks,*inner_ears])-keep_clear
    eyebrows=[]
    for sign in (-1,1):
        ts=np.linspace(0,1,13)
        pts=[]
        for t in ts:
            x=5.3+6.1*t;z=26.9+1.15*math.sin(math.pi*t)
            pts.append((sign*x,surface_y(x,z)-.2,z))
        spheres=[ellipsoid(p,(.62,.75,.62),40) for p in pts]
        eyebrows+= [md.Manifold.batch_hull([a,b]) for a,b in zip(spheres,spheres[1:])]
    nose=md.Manifold.batch_hull([
        ellipsoid((-2.1,-23.65,13.7),(1.65,1.45,1.35)),
        ellipsoid((2.1,-23.65,13.7),(1.65,1.45,1.35)),
        ellipsoid((0,-23.75,11.85),(1.6,1.3,1.1))])
    smile=path('M -6.4 9.0 C -3.5 7.3 3.5 7.3 6.4 9.0 C 5.4 5.9 3.0 2.2 0 2.15 C -3.0 2.2 -5.4 5.9 -6.4 9.0 Z')
    mouth=ellipsoid((0,-20.45,8.1),(11.55,3.65,7.45)) ^ front_mask(smile)
    tongue_profile=path('M -2.8 4.2 C -2.5 5.3 -1.0 5.7 0 4.8 C 1.0 5.7 2.5 5.3 2.8 4.2 C 2.0 2.8 1.0 2.3 0 2.3 C -1.0 2.3 -2.0 2.8 -2.8 4.2 Z')
    tongue=ellipsoid((0,-20.45,8.1),(11.6,3.70,7.5)) ^ front_mask(tongue_profile)
    black_base=union([nose,*pupils,*eyebrows,mouth])-keep_clear
    white_accents=union([*glints,tongue])
    # Material partition: white glints/tongue > black > white > grey.
    grey=clean(grey_base-white_base-black_base-white_accents)
    white=clean(union([white_base-black_base,white_accents]))
    black=clean(black_base-white_accents)
    face=clean(union([grey_base,white_base,black_base,white_accents]))
    assert len(face.decompose())==1,[(s.volume(),s.bounding_box()) for s in face.decompose()]
    assert (face ^ body).volume()<.001,('interference',(face ^ body).volume())
    assert (key-recess).volume()<.001
    assert (union([body,face]) ^ bore.offset(-.01).extrude(42)).volume()<.001
    # Retain the front relief and reconstruct the hidden carrier with a flat
    # rear plane. Body guides enter two small sockets in this printed base.
    plane=-11.
    clip=md.Manifold.cube((60,40,45)).translate((-30,plane-40,-1))
    # Rebuild only the hidden support volume from the unchanged barrel and
    # convex ear forms. Front surfaces remain the approved sculpt.
    flat_base=union([shell ^ clip,*[md.Manifold.batch_hull([e,e.translate((0,5,0))]) ^ clip for e in ears]])
    white=clean(white ^ clip);black=clean(black ^ clip)
    grey=clean((flat_base-white)-black)
    face=clean(union([flat_base,white,black]))
    body=ring-md.Manifold.cube((60,30,44)).translate((-30,-40.85,0))
    pin_centres=[(-5.,8.),(6.,21.)]
    for x,z in pin_centres:
        pin=md.Manifold.cylinder(1.05,1.2,circular_segments=48).transform([[1,0,0,x],[0,0,-1,-10.8],[0,1,0,z]])
        body=union([body,pin])
        socket=md.Manifold.cylinder(1.05,1.4,circular_segments=48).transform([[1,0,0,x],[0,0,-1,-10.95],[0,1,0,z]])
        grey-=socket
        face-=socket
    grey=clean(grey)
    face=clean(face)
    assert len(face.decompose())==1
    assert (face ^ body).volume()<.001
    assert (union([body,face]) ^ bore.offset(-.01).extrude(42)).volume()<.001
    print_pose=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,plane],[0,0,0,1]],float)
    face_print=[transformed(a,print_pose) for a in (grey,white,black)]
    contact_areas=[a.slice(.1).area() for a in face_print]
    assert contact_areas[0]>300
    parts=[]
    for name,s,color in zip(('corpo','rosto-cinzento','rosto-branco','rosto-preto'),(body,*face_print),(COLORS[0],*COLORS)):
        m=save_mesh(s,ROOT/'downloads'/f'{PREFIX}-{name}.stl')
        parts.append(dict(key=name,file=f'{PREFIX}-{name}.stl',color=color,
                          dimensions_mm=m.extents.tolist(),volume_mm3=s.volume(),watertight=bool(m.is_watertight)))
    owl=json.loads((ROOT/'fusion/CorujaBrunaV1/geometry.json').read_text())
    old_ring=next(p for p in owl['parts'] if p['key']=='anilha-castanha')
    old_bore=md.CrossSection([old_ring['regions'][0]['groups'][0][1]],md.FillRule.EvenOdd)
    bore_diff=(old_bore-bore).area()+(bore-old_bore).area();assert bore_diff<.001
    data=dict(parameters=dict(bore_opening_mm=[25,18],body_height_mm=H,maximum_body_diameter_mm=42,
        body_end_diameter_mm=36.6,hidden_seat_plane_y_mm=-10.85,cap_back_plane_y_mm=-11,
        socket_diameter_depth_mm=[2.8,1.0],pin_diameter_length_mm=[2.4,1.0],pin_centres_xz_mm=pin_centres,
        lateral_clearance_each_side_mm=.2,seat_glue_gap_mm=.15,key_floor_glue_gap_mm=.15),
        parts=parts,body_supports_required=False,face_supports_required=False,
        face_print_tilt_degrees=0,first_contact_cross_section_z_0_1_mm2=contact_areas,
        face_world_to_print_matrix=print_pose.tolist(),face_print_to_world_matrix=np.linalg.inv(print_pose).tolist(),
        face_print_lowest_z_mm=min(s.bounding_box()[2] for s in face_print),
        bore_source='Coruja BRUNA: exact same ellipse radii12.5,9;100 segments',bore_symmetric_difference_mm2=bore_diff,
        face_components_connected=True,assembly_interference_mm3=(face ^ body).volume(),
        bore_open_verified=True,physical_print_tested=False,physical_fit_tested=False,
        reference='Rounded body/contact sheet and original colour wolf photo supplied by user',
        modelling_note='Curved barrel cap plus ellipsoidal sculpt details; hidden chord seat and guide, not a flat visible badge.')
    (FOLDER/'geometry.json').write_text(json.dumps(data,indent=2)+'\n')
    scene=[(body,COLORS[0]),(grey,COLORS[0]),(white,COLORS[1]),(black,COLORS[2])]
    preview(scene,body,grey,data)
    print(json.dumps(data,indent=2))


def preview(scene,body,grey,data):
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    image=Image.new('RGB',(1600,1100),'#f4f6f8');d=ImageDraw.Draw(image)
    image.paste(render_meshes(scene,(850,820),direction=(0,-1,.15),margin=55),(0,140))
    image.paste(render_meshes(scene,(730,800),direction=(.6,-1,.65),margin=45),(855,150))
    d.text((35,25),'Anilha de lenço — lobito V3 — costas lisas',font=font(34),fill='#263446')
    d.text((35,78),'Abertura oval 25 × 18 mm · corpo abaulado · rosto curvo e volumes suaves',font=font(23),fill='#465468')
    d.text((35,1010),'Geometria real: corpo e rosto separados para colar, com guia e espaço para cola.',font=font(23),fill='#465468')
    d.text((35,1050),'Conceito aprovado · corpo 30 mm · impressão e ajuste físico ainda por validar.',font=font(21),fill='#465468')
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    # Separate actual geometry views for the hidden guide/recess.
    detail=Image.new('RGB',(1400,950),'#f4f6f8');d=ImageDraw.Draw(detail)
    detail.paste(render_meshes([(body,COLORS[0])],(680,710),direction=(.1,-1,.4)),(0,140))
    detail.paste(render_meshes([(grey,COLORS[0])],(680,710),direction=(.3,1,.4)),(710,140))
    d.text((30,25),'Encaixe oculto — verso do rosto e rebaixo',font=font(32),fill='#263446')
    d.text((30,90),'Corpo: apoio plano e dois pinos',font=font(24),fill='#465468')
    d.text((730,90),'Verso: plano com dois pequenos alojamentos',font=font(24),fill='#465468')
    d.text((30,895),'Costas planas · dois pinos de orientação · 0,15 mm para cola',font=font(22),fill='#465468')
    detail.save(ROOT/'designs'/f'{PREFIX}-encaixe.png')


if __name__=='__main__':make()
