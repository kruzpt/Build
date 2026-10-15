"""Generate the actual two-piece Universo do Saber stand, geometry and evidence.

Units are mm. Backrest local XY is the print bed; local Z points to the phone.
The blue shelf is perpendicular to it, climbing 20 degrees towards the front.
Its long rear end, not the phone lip, is the second contact with the table.
Requires the project's geometry venv: numpy, manifold3d, trimesh, OpenCV, Pillow.
"""
from pathlib import Path
import json
import math
import sys

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from generate_joana_topper import section_groups, save_mesh, groups

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/UniversoSaberStandV3'
PREFIX='universo-saber-suporte-v3'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
T=6.0
H=200.0
W=80.0
L=110.0
ANGLE=70.0
GAP=0.30
RELIEF=0.8
B=72.0
A=math.radians(ANGLE)
SIN=math.sin(A)
COS=math.cos(A)
C=(B+T)/math.tan(A)-T
WHITE='#FFFFFF'
BLUE='#17385B'


def rect(x,y,w,h):
    return md.CrossSection.square((w,h)).translate((x,y))


def rounded(x,y,w,h,r):
    return rect(x+r,y+r,w-2*r,h-2*r).offset(r,circular_segments=20)


def union(items):
    return md.Manifold.batch_boolean(list(items),md.OpType.Add)


def back_transform():
    return np.array([[1,0,0,0],[0,COS,-SIN,T*SIN],
                     [0,SIN,COS,-T*COS],[0,0,0,1]],float)


def shelf_in_back():
    # Proper rotation (det +1): the shelf's printed left becomes assembled right.
    return np.array([[-1,0,0,0],[0,0,1,C],[0,1,0,-B],[0,0,0,1]],float)


def transform(solid,matrix):
    return solid.transform(np.asarray(matrix)[:3].tolist())


def bodies(gap=GAP):
    white=rounded(-W/2,0,W,H,3)
    white-=rect(-9,-2,18,8)+md.CrossSection.circle(9,40).translate((0,6))
    white-=rect(-W/2-1,C-gap/2,W/2+1+gap/2,T+gap)
    white_solid=white.extrude(T).trim_by_plane((0,SIN,COS),T*COS)

    blue=rounded(-W/2,0,W,L,3)
    blue-=rect(-W/2-1,B-gap/2,W/2+1+gap/2,T+gap)
    # Charging fork: the port lies over the cutout, with two broad side rails.
    blue-=rect(-9,89,18,25)+md.CrossSection.circle(9,40).translate((0,89))
    blue_solid=blue.extrude(T).trim_by_plane((0,COS,SIN),T*SIN)
    pad_regions=[]
    for x in (-26,26):
        pad=rounded(x-9,B+25,18,6,1.4)
        pad_regions.append(pad)
    blue_solid=union([blue_solid]+[p.extrude(4).translate((0,0,T)) for p in pad_regions])
    return white,white_solid,blue,blue_solid,pad_regions


def text_section(text,height,cy):
    scale=30
    f=ImageFont.truetype(FONT,round(height*scale/0.73))
    b=f.getbbox(text)
    im=Image.new('L',(b[2]-b[0]+20,b[3]-b[1]+20))
    ImageDraw.Draw(im).text((10-b[0],10-b[1]),text,font=f,fill=255)
    m=(np.asarray(im)>127).astype('uint8')*255
    cs=md.CrossSection([loop for group in groups(m,1/scale,0,im.height,min_area=6)
                        for loop in group],md.FillRule.EvenOdd).simplify(0.025)
    paths=np.vstack(cs.to_polygons());lo=paths.min(0);hi=paths.max(0)
    factor=min(1,73/(hi[0]-lo[0]))
    cs=cs.scale((factor,factor))
    paths=np.vstack(cs.to_polygons());lo=paths.min(0);hi=paths.max(0)
    return cs.translate((-(lo[0]+hi[0])/2,cy-(lo[1]+hi[1])/2))


def _signed_area(points):
    points=np.asarray(points,float)
    return .5*np.sum(points[:,0]*np.roll(points[:,1],-1)-
                     points[:,1]*np.roll(points[:,0],-1))


def _chaikin(points,passes=5):
    """Turn the traced outline into a dense, continuous quadratic curve."""
    points=np.asarray(points,float)
    for _ in range(passes):
        following=np.roll(points,-1,axis=0)
        first=.75*points+.25*following
        second=.25*points+.75*following
        points=np.stack((first,second),axis=1).reshape(-1,2)
    return points


def logo_section():
    # Preserve the approved symbol, but remove the perspective and the visibly
    # faceted raster outline.  At 800+ contour vertices its chord spacing is
    # below the useful resolution of a 0.4 mm nozzle.
    source=ROOT/'designs/suporte-universo-saber-conceito-v3-branco-azul.png'
    rgb=np.asarray(Image.open(source).convert('RGB'))
    r,g,b=np.moveaxis(rgb.astype(float),2,0)
    m=((b>r*1.25)&(r<110)).astype('uint8')*255
    mask=np.zeros(m.shape,np.uint8);mask[240:530,240:590]=m[240:530,240:590]
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    cs=md.CrossSection([p for gr in groups(mask,1,0,530,min_area=150) for p in gr],
                       md.FillRule.EvenOdd)
    # Remove the perspective lean of the concept's backrest.
    cs=cs.transform(((1,0.30,0),(0,1,0)))
    points=np.vstack(cs.to_polygons());lo=points.min(0);hi=points.max(0)
    cs=cs.translate(-lo).scale((62/(hi[0]-lo[0]),57/(hi[1]-lo[1])))
    cs=cs.translate((-31,119))

    polygons=[np.asarray(p,float) for p in cs.to_polygons()]
    main=max(polygons,key=lambda p:abs(_signed_area(p)))
    details=[p for p in polygons if p is not main]
    if len(details)!=2:raise RuntimeError('O logotipo deve ter símbolo, cabeça e estrela.')
    # Make the long outside of U an exact vertical segment before smoothing.
    following=np.roll(main,-1,axis=0)
    lengths=np.linalg.norm(following-main,axis=1)
    candidates=np.where((lengths>10)&
        (np.maximum(main[:,0],following[:,0])<main[:,0].min()+2))[0]
    if len(candidates)!=1:raise RuntimeError('Não foi possível localizar a vertical de U.')
    edge=int(candidates[0]);other=(edge+1)%len(main)
    main[[edge,other],0]=main[[edge,other],0].mean()
    main=_chaikin(main,5)

    # The source is a perspective render.  Level the two letter feet, then use
    # the long left side of U as the true vertical datum.  This makes the logo
    # perpendicular to the support instead of preserving the camera lean.
    u=main[main[:,0]<0];s=main[main[:,0]>5]
    ufoot=u[np.argmin(u[:,1])];sfoot=s[np.argmin(s[:,1])]
    baseline_slope=(sfoot[1]-ufoot[1])/(sfoot[0]-ufoot[0])
    main[:,1]-=baseline_slope*main[:,0]
    u=main[main[:,0]<0];s=main[main[:,0]>5]
    ufoot=u[np.argmin(u[:,1])];sfoot=s[np.argmin(s[:,1])]
    correction=(sfoot[1]-ufoot[1])/(sfoot[0]-ufoot[0])
    main[:,1]-=correction*main[:,0]
    baseline_slope+=correction
    xmin=main[:,0].min();ymin=main[:,1].min();ymax=main[:,1].max()
    # Exact tangent quarter-circle between the vertical and horizontal faces.
    # This replaces the V2 point clamp that could leave a visible notch.
    corner_radius=1.3
    lower_join=ymin+15;lower_blend=2.0
    outer=np.where((main[:,0]<xmin+3)&(main[:,1]>lower_join-lower_blend))[0]
    for index in outer:
        y=main[index,1]
        if y<lower_join:
            amount=(y-(lower_join-lower_blend))/lower_blend
            amount=max(0,min(1,amount));amount=amount*amount*(3-2*amount)
            main[index,0]+=(xmin-main[index,0])*amount
        elif y<=ymax-corner_radius:
            main[index,0]=xmin
        else:
            dy=min(corner_radius,max(0,y-(ymax-corner_radius)))
            main[index,0]=xmin+corner_radius-math.sqrt(max(0,corner_radius**2-dy**2))
    top=(main[:,0]>xmin+corner_radius)&(main[:,0]<xmin+11)&(main[:,1]>ymax-2)
    main[top,1]=ymax

    def align(p):
        p=np.asarray(p,float).copy()
        p[:,1]-=baseline_slope*p[:,0]
        return p

    # Replace the traced 16-sided head with a true high-resolution circle.
    details.sort(key=lambda p:(p.max(0)-p.min(0))[0])
    head_source,star_source=details
    head_center=align(np.array([(head_source.min(0)+head_source.max(0))/2]))[0]
    head_radius=float(min(head_source.max(0)-head_source.min(0))/2)
    angles=np.linspace(0,2*math.pi,192,endpoint=False)
    head=np.column_stack((head_center[0]+head_radius*np.cos(angles),
                          head_center[1]+head_radius*np.sin(angles)))

    # The star intentionally keeps straight sides, now with ten exact vertices.
    star_center=align(np.array([(star_source.min(0)+star_source.max(0))/2]))[0]
    star_size=star_source.max(0)-star_source.min(0)
    angles=np.deg2rad(90+np.arange(10)*36)
    radius=np.where(np.arange(10)%2==0,1,.45)
    rx=star_size[0]/(2*math.cos(math.radians(18)))
    ry=star_size[1]/(1+math.sin(math.radians(54)))
    star=np.column_stack((star_center[0]+rx*radius*np.cos(angles),
                          star_center[1]+ry*radius*np.sin(angles)))

    result=md.CrossSection([main,head,star],md.FillRule.EvenOdd)
    points=np.vstack(result.to_polygons());lo=points.min(0);hi=points.max(0)
    result=result.translate(-lo).scale((62/(hi[0]-lo[0]),57/(hi[1]-lo[1])))
    result=result.translate((-31,119))
    # Numerical proof of the two visual alignments requested by the user.
    largest=max(result.to_polygons(),key=lambda p:abs(_signed_area(p)))
    largest=np.asarray(largest)
    left=largest[largest[:,0]<0];right=largest[largest[:,0]>5]
    assert abs(left[:,1].min()-right[:,1].min())<0.03
    xmin=largest[:,0].min();lo_y=largest[:,1].min();hi_y=largest[:,1].max()
    side=largest[(largest[:,0]<xmin+0.1)&(largest[:,1]>lo_y+15)&
                 (largest[:,1]<hi_y-1.5)]
    side_slope=float(np.polyfit(side[:,1],side[:,0],1)[0])
    assert abs(side_slope)<0.0001,side_slope
    assert sum(len(p) for p in result.to_polygons())>2900
    return result


def logo_alignment_metrics():
    logo=logo_section();polygons=logo.to_polygons()
    largest=np.asarray(max(polygons,key=lambda p:abs(_signed_area(p))))
    left=largest[largest[:,0]<0];right=largest[largest[:,0]>5]
    xmin=largest[:,0].min();lo_y=largest[:,1].min();hi_y=largest[:,1].max()
    side=largest[(largest[:,0]<xmin+0.1)&(largest[:,1]>lo_y+15)&
                 (largest[:,1]<hi_y-1.5)]
    slope=float(np.polyfit(side[:,1],side[:,0],1)[0])
    main_steps=np.linalg.norm(np.roll(largest,-1,axis=0)-largest,axis=1)
    return {'total_vertices':sum(len(p) for p in polygons),
        'us_baseline_delta_mm':abs(float(left[:,1].min()-right[:,1].min())),
        'u_vertical_slope_x_per_y':slope,
        'u_vertical_deviation_degrees':abs(float(math.degrees(math.atan(slope)))),
        'us_curve_mean_chord_mm':float(main_steps.mean()),
        'us_curve_p95_chord_mm':float(np.percentile(main_steps,95))}


def stroke_path(points,width=0.9,closed=False):
    """Constant-width printable line with round joins and end caps."""
    points=np.asarray(points,float);pieces=[];radius=width/2
    count=len(points) if closed else len(points)-1
    for index in range(count):
        a=points[index];b=points[(index+1)%len(points)]
        direction=b-a;length=np.linalg.norm(direction)
        if length<1e-6:continue
        normal=np.array((-direction[1],direction[0]))/length*radius
        quad=np.array((a+normal,b+normal,b-normal,a-normal))
        pieces.append(md.CrossSection([quad],md.FillRule.EvenOdd))
    for point in points:
        pieces.append(md.CrossSection.circle(radius,32).translate(point))
    return md.CrossSection.batch_boolean(pieces,md.OpType.Add)


def books(cx):
    """Two stacked books as perspective line art, readable at 0.4 mm."""
    lower=np.array([(-8.8,3.2),(5.8,3.2),(9.0,5.0),(7.2,7.1),
                    (-7.7,7.0),(-9.0,5.8)])+np.array((cx,0))
    upper=np.array([(-8.4,8.0),(5.0,8.0),(8.2,9.8),(6.3,11.9),
                    (-7.3,11.8),(-8.7,10.5)])+np.array((cx,0))
    top=np.array([(-7.3,11.8),(-0.2,14.7),(8.2,12.7),(6.3,11.9)])+np.array((cx,0))
    return md.CrossSection.batch_boolean([
        stroke_path(lower,0.9,True),stroke_path(upper,0.9,True),
        stroke_path(top,0.9,True)],md.OpType.Add)


def decoration():
    return md.CrossSection.batch_boolean([
        logo_section(),text_section('Centro de Estudos',5.2,101),
        text_section('Universo do Saber',5.2,91),books(-25),books(25)],md.OpType.Add)


def coupon(gap):
    # Same 6 mm thickness, half-width slots and opposite-handed assembled notch.
    face=rounded(-14,0,28,24,1.5)-rect(-15,9-gap/2,15+gap/2,T+gap)
    return face.extrude(T)


def vertices(solid):
    return np.asarray(solid.to_mesh().vert_properties)[:,:3]


def contacts(solid):
    pts=vertices(solid);z=float(pts[:,2].min())
    pts=pts[np.abs(pts[:,2]-z)<1e-4]
    return z,pts[:,:2].tolist()


def check_geometry(solids,assembled):
    white,relief,blue=solids
    aw,ar,ab=assembled
    assert all(s.status()==md.Error.NoError for s in solids)
    assert len(union([white,relief]).decompose())==1
    assert len(blue.decompose())==1
    assert (aw^ab).volume()<1e-5
    assert (ar^ab).volume()<1e-5
    assert (white^relief).volume()<1e-6
    assert (decoration()-bodies()[0]).area()<1e-5
    # The relief is supported everywhere by the white front face.
    assert (relief.translate((0,0,-0.05))-white).volume()<relief.volume()
    wc,wp=contacts(aw);bc,bp=contacts(ab)
    assert abs(wc)<1e-5 and abs(bc)<1e-5
    contact_points=np.array(wp+bp,np.float32)
    hull=cv2.convexHull(contact_points).reshape(-1,2)
    assert cv2.contourArea(hull)>4500
    # Check the full side-insertion route, not only the final assembly.
    for dx in np.linspace(0,82,42):
        moving=ab.translate((-float(dx),0,0))
        # Slide from world -X towards the final position; withdraw in reverse.
        assert (aw^moving).volume()<1e-5,('insertion',dx,(aw^moving).volume())
    table=md.Manifold.cube((600,600,50)).translate((-300,-300,-50))
    assert all((p^table).volume()<1e-5 for p in assembled)
    # Conservative static load checks over phone sizes; no adhesion or FEA claim.
    tm=back_transform();worst_margin=1e9;results=[]
    support=union(assembled)
    material_density=0.00124
    raw=support.to_mesh();mesh=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts)
    stand_center=mesh.center_mass
    for length,width,thickness,mass in [(145,65,8,180),(165,80,14,250),(180,90,17,320)]:
        p=md.Manifold.cube((width,length,thickness)).translate((-width/2,C+T,T+RELIEF+0.1))
        ap=transform(p,tm)
        assert (ap^support).volume()<0.001
        phone_center=(tm@np.array([0,C+T+length/2,T+RELIEF+0.1+thickness/2,1]))[:3]
        for fill_mass_factor in (0.5,1.0):
            sm=support.volume()*material_density*fill_mass_factor
            center=(sm*stand_center+mass*phone_center)/(sm+mass)
            margin=float(cv2.pointPolygonTest(hull.astype(np.float32),tuple(center[:2]),True))
            assert margin>15,('static stability',margin)
            worst_margin=min(worst_margin,margin)
            top_z=float(vertices(ap)[:,2].max())
            gentle_tip_force=(sm+mass)/1000*9.81*margin/top_z
            results.append({'phone_mm':[length,width,thickness],'phone_g':mass,
                'stand_mass_factor':fill_mass_factor,'static_margin_mm':round(margin,3),
                'ideal_horizontal_tip_force_N':round(gentle_tip_force,3)})
    # Accessible central cable path below the phone at its port, 10 x 8 mm section.
    channel=md.Manifold.cube((10,18,8)).translate((-5,C-12,T+RELIEF+3))
    assert (transform(channel,tm)^ab).volume()<1e-5
    return {'backrest_degrees':ANGLE,'shelf_front_degrees':20,
        'inter_piece_angle_degrees':90,'nominal_gap_total_mm':GAP,
        'slot_width_mm':T+GAP,'crossing_back_local_mm':C,
        'usable_backrest_above_shelf_mm':H-C-T,
        'feet_plane_z_mm':[wc,bc],'foot_contact_polygon_xy':hull.tolist(),
        'static_load_cases':results,'worst_static_margin_mm':worst_margin,
        'collision_volume_mm3':float((aw^ab).volume()),
        'side_insertion_checks':42,'phone_clearance_from_relief_mm':0.1,
        'nominal_phone_case_thickness_limit_mm':25-(T+RELIEF+0.1),
        'physical_fit_tested':False,'physical_stability_tested':False,
        'structural_FEA_performed':False,'fusion_runtime_tested':False}


def mesh_of(s):
    r=s.to_mesh()
    return trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts,process=True)


def render_meshes(items,size=(1300,1100),direction=(0.45,-0.8,0.55),margin=65):
    """Orthographic z-buffer render of real model triangles, all parts sharing depth."""
    meshes=[(mesh_of(s),colour) for s,colour in items]
    n=np.array(direction,float);n/=np.linalg.norm(n)
    u=np.cross((0,0,1),n);u/=np.linalg.norm(u)
    v=np.cross(n,u)
    allpts=np.vstack([m.vertices for m,c in meshes]);uv=allpts@np.array([u,v]).T
    lo=uv.min(0);hi=uv.max(0)
    scale=min((size[0]-2*margin)/(hi[0]-lo[0]),(size[1]-2*margin)/(hi[1]-lo[1]))
    origin=np.array([(size[0]-(hi[0]-lo[0])*scale)/2,
                     (size[1]-(hi[1]-lo[1])*scale)/2])
    pix=np.full((size[1],size[0],3),(244,246,248),np.uint8)
    zb=np.full((size[1],size[0]),-np.inf)
    for mesh,colour in meshes:
        uv=mesh.vertices@np.array([u,v]).T
        pp=(uv-lo)*scale+origin;pp[:,1]=size[1]-pp[:,1]
        depths=mesh.vertices@n
        rgb=np.array(tuple(int(colour[i:i+2],16) for i in (1,3,5)))
        for k,face in enumerate(mesh.faces):
            p=pp[face];x0,y0=np.maximum(np.floor(p.min(0)).astype(int),0)
            x1,y1=np.minimum(np.ceil(p.max(0)).astype(int),np.array(size)-1)
            if x1<x0 or y1<y0:continue
            den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
            if abs(den)<1e-8:continue
            xx,yy=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
            a=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den
            b=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den
            c=1-a-b;d=a*depths[face[0]]+b*depths[face[1]]+c*depths[face[2]]
            target=zb[y0:y1+1,x0:x1+1]
            visible=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)&(d>target)
            light=np.array((-.4,-.5,.8));light/=np.linalg.norm(light)
            shade=max(.50,min(1,.75+.25*np.dot(mesh.face_normals[k],light)))
            target[visible]=d[visible]
            pix[y0:y1+1,x0:x1+1][visible]=(rgb*shade).astype(np.uint8)
    return Image.fromarray(pix)


def preview(assembled):
    out=Image.new('RGB',(1700,1250),'#f4f6f8');d=ImageDraw.Draw(out)
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    out.paste(render_meshes(list(zip(assembled,[WHITE,BLUE,BLUE])),(1000,1050)),(10,140))
    phone=md.Manifold.cube((80,165,14)).translate((-40,C+T,T+RELIEF+0.1))
    phone=transform(phone,back_transform())
    out.paste(render_meshes(list(zip(assembled,[WHITE,BLUE,BLUE]))+[(phone,'#3B434C')],(620,740)),(1050,140))
    d.text((45,28),'Universo do Saber — CAD V3',font=font(36),fill='#17385b')
    d.text((45,83),'Costas 200 mm · Duas peças · Branco e azul · Apoio a 70°',font=font(25),fill='#303d49')
    d.text((1070,920),'Geometria real, não imagem gerada.',font=font(22),fill='#303d49')
    d.text((1070,965),'Encaixe: 6,30 mm para peça de 6 mm.',font=font(21),fill='#303d49')
    d.text((1070,1010),'Testar a amostra antes do conjunto.',font=font(21),fill='#303d49')
    d.text((45,1190),'Contactos e colisões verificados geometricamente; protótipo físico ainda necessário.',font=font(22),fill='#303d49')
    out.save(ROOT/f'designs/{PREFIX}-CAD.png')


def side_diagram(assembled,stats):
    out=Image.new('RGB',(1500,950),'white');d=ImageDraw.Draw(out)
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    # Draw x=+20 mm sections, away from cable openings, book cutouts and half slot.
    def pt(y,z):return (180+y*3.5,780-z*3.5)
    for solid,col in zip(assembled,[WHITE,BLUE,BLUE]):
        mesh=mesh_of(solid)
        seg=mesh.section(plane_origin=(20,0,0),plane_normal=(1,0,0))
        if seg:
            for path in seg.discrete:
                p=[pt(y,z) for x,y,z in path]
                if len(p)>2:d.polygon(p,fill=col,outline='#333333')
    d.line((50,780,1400,780),fill='#666666',width=3)
    d.text((50,25),'Montagem real — vista lateral',font=font(34),fill=BLUE)
    d.text((50,78),'Apoio do telefone a 70° da mesa; peça azul sobe 20° à frente.',font=font(24),fill='#303d49')
    d.text((860,280),'Costas: 200 × 80 × 6 mm',font=font(25),fill=BLUE)
    d.text((860,330),f'Útil acima do apoio: {H-C-T:.1f} mm',font=font(25),fill=BLUE)
    d.text((860,380),'Base: 110 × 80 × 6 mm',font=font(25),fill=BLUE)
    d.text((860,430),'Batentes integrados: +4 mm',font=font(25),fill=BLUE)
    d.text((50,835),'Os dois pés têm faces de contacto no mesmo plano (Z = 0).',font=font(24),fill='#303d49')
    d.text((50,880),'Equilíbrio estático calculado; aderência e resistência ao toque por testar.',font=font(24),fill='#303d49')
    out.save(ROOT/f'designs/{PREFIX}-montagem.png')


def logo_diagram():
    """Front view of the actual relief contour with its alignment datums."""
    logo=logo_section();polygons=[np.asarray(p) for p in logo.to_polygons()]
    points=np.vstack(polygons);lo=points.min(0);hi=points.max(0)
    out=Image.new('RGB',(1100,900),'white');d=ImageDraw.Draw(out)
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    scale=10;origin=np.array((235,735),float)
    def image_point(p):return tuple((origin+np.array((p[0]-lo[0],-(p[1]-lo[1])))*scale).tolist())
    for polygon in polygons:d.polygon([image_point(p) for p in polygon],fill=BLUE)
    baseline_y=origin[1]
    vertical_x=origin[0]
    d.line((vertical_x-45,baseline_y,vertical_x+690,baseline_y),fill='#20a36a',width=3)
    d.line((vertical_x,baseline_y+40,vertical_x,baseline_y-610),fill='#20a36a',width=3)
    d.text((48,30),'Logótipo vetorial V3 — curva corrigida',font=font(34),fill=BLUE)
    d.text((48,80),'Vista frontal do contorno realmente usado no STL/3MF',font=font(23),fill='#303d49')
    d.text((48,805),'Base U/S: diferença < 0,01 mm  ·  Lateral de U: vertical',font=font(23),fill='#303d49')
    d.text((48,842),'3018 vértices; curvas com passo médio próximo de 0,12 mm.',font=font(21),fill='#303d49')
    out.save(ROOT/f'designs/{PREFIX}-logo-alinhado.png')


def books_diagram():
    """Magnified front view of the exact two-book line art."""
    icon=books(0);grouped=section_groups(icon)
    points=np.vstack(icon.to_polygons());lo=points.min(0);hi=points.max(0)
    out=Image.new('RGB',(1000,700),'white');d=ImageDraw.Draw(out)
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    scale=30;origin=np.array((220,570),float)
    def image_point(p):return tuple((origin+np.array((p[0]-lo[0],-(p[1]-lo[1])))*scale).tolist())
    for group in grouped:
        d.polygon([image_point(p) for p in group[0]],fill=BLUE)
        for hole in group[1:]:d.polygon([image_point(p) for p in hole],fill='white')
    d.text((45,28),'Dois livros em perspetiva — contorno real',font=font(34),fill=BLUE)
    d.text((45,78),'Traço azul de 0,9 mm, preparado para bico de 0,4 mm',font=font(23),fill='#303d49')
    d.text((45,635),'A superfície branca da placa forma o interior das páginas.',font=font(22),fill='#303d49')
    out.save(ROOT/f'designs/{PREFIX}-livros.png')


def main():
    FOLDER.mkdir(exist_ok=True)
    white_plan,white,blue_plan,blue,pads=bodies()
    deco=decoration();relief=deco.extrude(RELIEF).translate((0,0,T))
    flat=[white,relief,blue]
    mats=[back_transform(),back_transform(),back_transform()@shelf_in_back()]
    assembled=[transform(s,m) for s,m in zip(flat,mats)]
    stats=check_geometry(flat,assembled)
    stats['logo_alignment']=logo_alignment_metrics()
    names=['costas-branco','relevos-azul','base-azul']
    for name,solid in zip(names,flat):
        mesh=save_mesh(solid,ROOT/f'downloads/{PREFIX}-{name}.stl')
        stats.setdefault('parts',[]).append({'name':name,'bbox_mm':mesh.extents.tolist(),
            'volume_mm3':solid.volume(),'watertight':bool(mesh.is_watertight)})
    complete=save_mesh(union(flat[:2]),ROOT/f'downloads/{PREFIX}-costas-completas.stl')
    complete.apply_transform(mats[0])
    blue_reference=trimesh.load(ROOT/f'downloads/{PREFIX}-base-azul.stl',force='mesh')
    blue_reference.apply_transform(mats[2])
    reference=trimesh.util.concatenate([complete,blue_reference])
    assert reference.is_watertight and reference.is_winding_consistent
    reference.export(ROOT/f'downloads/{PREFIX}-montado-referencia-nao-imprimir.stl')
    samples=[]
    for i,gap in enumerate((0.2,0.3,0.4)):
        # Export each tolerance as a clearly named two-piece test.  Keep the
        # combined plate as a convenient option, ordered 0.20/0.30/0.40 left
        # to right.
        pair=[coupon(gap),coupon(gap).translate((0,32,0))]
        save_mesh(union(pair),ROOT/f'downloads/{PREFIX}-amostra-encaixe-{round(gap*100):03d}.stl')
        samples.extend([p.translate((i*34,0,0)) for p in pair])
    sample=union(samples)
    save_mesh(sample,ROOT/f'downloads/{PREFIX}-amostras-020-030-040.stl')
    definitions={'version':3,'units':'mm','angle_deg':ANGLE,'gap_total_mm':GAP,
        'backrest_length_mm':H,'backrest_width_mm':W,'backrest_thickness_mm':T,
        'shelf_length_mm':L,'shelf_rear_offset_mm':B,'crossing_mm':C,
        'relief_height_mm':RELIEF,
        'parts':[
            {'name':'Costas brancas','color':WHITE,'z':0,'height':T,
             'groups':section_groups(white_plan),'bevel_triangle_yz':[[0,0],[T/math.tan(A),0],[0,T]],
             'assembly_transform':mats[0].tolist()},
            {'name':'Símbolo, letras e livros azuis','color':BLUE,'z':T,'height':RELIEF,
             'groups':section_groups(deco),'assembly_transform':mats[1].tolist()},
            {'name':'Base azul','color':BLUE,'z':0,'height':T,
             'groups':section_groups(blue_plan),'bevel_triangle_yz':[[0,0],[T*math.tan(A),0],[0,T]],
             'additions':[{'name':'Batente '+str(i+1),'z':T,'height':4,
                           'groups':section_groups(p)} for i,p in enumerate(pads)],
             'assembly_transform':mats[2].tolist()}]}
    (FOLDER/'geometry.json').write_text(json.dumps(definitions,ensure_ascii=False,separators=(',',':'))+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
    preview(assembled);side_diagram(assembled,stats);logo_diagram();books_diagram()
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
