"""Export universal underside sockets, PETG clips and a two-edge fit sample.

Reuses the validated V2 grid generator; preserves all earlier deliverables.
Run with the existing STL-generation venv. No uploaded file is republished.
"""
import ast
import json
import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from generate_pintos_v2 import model as grid_model

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/GrelhaPintosV3'
STEM = 'grelha-pintos-v3'


def parameters():
    path = FOLDER/'GrelhaPintosV3.py'
    tree = ast.parse(path.read_text())
    names = {'layout','foot_contour','validate','socket_sites','socket_polygon',
             'clip_contour','clip_print_contour'}
    pure = [n for n in tree.body if isinstance(n,ast.Assign) or
            (isinstance(n,ast.FunctionDef) and n.name in names)]
    v = {'math':math}
    exec(compile(ast.Module(body=pure,type_ignores=[]),str(path),'exec'),v)
    v['validate']()
    return v


def prism(polygon,z,height):
    return md.CrossSection([polygon],md.FillRule.NonZero).extrude(height).translate((0,0,z))


def sockets(body,v,sites):
    bosses = [prism(v['socket_polygon'](s,0,v['BOSS_DEPTH'],v['BOSS_LENGTH']),
                    v['GRID_THICKNESS'],v['BOSS_END_Z']-v['GRID_THICKNESS'])
              for s in sites]
    body = md.Manifold.batch_boolean([body]+bosses,md.OpType.Add)
    cutters = []
    for site in sites:
        cutters += [prism(v['socket_polygon'](site,v['SOCKET_NEAR'],
                            v['SOCKET_HEAD_FAR'],v['SOCKET_WIDTH']),
                           v['SOCKET_HEAD_Z'],v['SOCKET_SHOULDER_Z']-v['SOCKET_HEAD_Z']),
                    prism(v['socket_polygon'](site,v['SOCKET_NEAR'],
                            v['SOCKET_THROAT_FAR'],v['SOCKET_WIDTH']),
                           v['SOCKET_SHOULDER_Z'],
                           v['BOSS_END_Z']-v['SOCKET_SHOULDER_Z']+1),
                    prism(v['socket_polygon'](site,v['SOCKET_THROAT_FAR'],
                            v['BOSS_DEPTH']+1,v['SOCKET_WIDTH']),
                           v['RELEASE_WINDOW_Z'],v['RELEASE_WINDOW_HEIGHT'])]
    return body-md.Manifold.batch_boolean(cutters,md.OpType.Add)


def plate_model(v):
    return sockets(grid_model(v),v,v['socket_sites']())


def coupon_model(v):
    body = md.Manifold.cube((v['COUPON_WIDTH'],v['COUPON_LENGTH'],v['GRID_THICKNESS']))
    return sockets(body,v,[(0,v['COUPON_LENGTH']/2,1,0,0,1)])


def clip_model(v,reach=None):
    return prism(v['clip_print_contour'](reach),0,v['CLIP_WIDTH'])


def assembled_clip(v,reach=None,deflection=0):
    # Input profile is across-seam X versus plate Z; extrusion is tangential Y.
    source = prism(v['clip_contour'](reach,deflection),0,v['CLIP_WIDTH'])
    return source.transform(np.array([[1,0,0,0],
                                     [0,0,1,-v['CLIP_WIDTH']/2],
                                     [0,1,0,0]],dtype=float))


def export(model,path,components=1):
    assert model.status() == md.Error.NoError
    assert len(model.decompose()) == components
    raw = model.simplify(0.00001).to_mesh()
    mesh = trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000001))
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert len(mesh.split()) == components
    mesh.export(path)
    saved = trimesh.load(path,force='mesh')
    assert saved.is_watertight and saved.is_winding_consistent
    assert len(saved.split()) == components
    assert abs(saved.volume-model.volume()) < 0.3
    return saved


def assembly_checks(v,coupon,reach=None):
    # Align the two sample edges, in plate printing coordinates, at X=0.
    right = coupon.translate((0,-v['COUPON_LENGTH']/2,0))
    left = right.rotate((0,0,180))
    boards = right+left
    reach = v['CLIP_HOOK_REACH'] if reach is None else reach
    clip = assembled_clip(v,reach)
    assert (clip ^ right).volume() < 0.00001
    assert (clip ^ left).volume() < 0.00001
    # A rigid clip cannot leave in Z without catching the retaining shoulder.
    assert (clip.translate((0,0,1)) ^ boards).volume() > 0.1
    # Enclosed mouths also stop lateral separation and tangential slipping.
    assert (clip ^ right.translate((0.8,0,0))).volume() > 0.1
    assert (clip.translate((0,1,0)) ^ boards).volume() > 0.1
    # A flat release probe can reach the arm through the inner-side window,
    # without crossing the holder. At the contact position it touches the arm.
    probe = md.Manifold.cube((3,4,2)).translate((2.7,-2,10.5))
    assert (probe ^ right).volume() < 0.00001
    assert (probe ^ clip).volume() < 0.00001
    probe = probe.translate((-0.2,0,0))
    assert (probe ^ right).volume() < 0.00001
    assert (probe ^ clip).volume() > 0.01
    # Idealised deflection clears the entire insertion route (standard: 0.45 mm).
    # This is geometry only; it does not predict PETG force, strain or lifetime.
    compressed = assembled_clip(v,reach,deflection=reach-v['SOCKET_THROAT_FAR']+0.05)
    for dz in np.linspace(0,10,41):
        assert (compressed.translate((0,0,dz)) ^ boards).volume() < 0.00001
    return right,left,clip


def draw_mesh(image,mesh,origin,scale,colour,flip_z=None):
    verts=mesh.vertices.copy()
    centre=(verts.max(axis=0)+verts.min(axis=0))/2
    verts[:,:2]-=centre[:2]
    normals=mesh.face_normals.copy()
    if flip_z is not None:
        verts[:,2]=flip_z-verts[:,2]
        normals[:,2]*=-1
    ox,oy=origin
    projected=np.column_stack((ox+(verts[:,0]-verts[:,1])*scale,
                               oy+(verts[:,0]+verts[:,1])*scale*0.43-verts[:,2]*scale))
    depth=verts@np.array([1,1,0.86])
    pixels=np.asarray(image).copy()
    zbuffer=np.full(pixels.shape[:2],-np.inf)
    # Orthographic z-buffer, so underside faces cannot paint over the top.
    for i,face in enumerate(mesh.faces):
        p=projected[face]
        x0,y0=np.maximum(np.floor(p.min(axis=0)).astype(int),[0,0])
        x1,y1=np.minimum(np.ceil(p.max(axis=0)).astype(int),
                         [pixels.shape[1]-1,pixels.shape[0]-1])
        if x1<x0 or y1<y0: continue
        denom=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
        if abs(denom)<1e-8: continue
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
        a=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/denom
        b=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/denom
        c=1-a-b
        z=a*depth[face[0]]+b*depth[face[1]]+c*depth[face[2]]
        target=zbuffer[y0:y1+1,x0:x1+1]
        visible=(a>=-1e-8)&(b>=-1e-8)&(c>=-1e-8)&(z>target)
        shade=max(0.4,min(1,0.7+0.25*normals[i,2]+0.1*normals[i,0]))
        target[visible]=z[visible]
        pixels[y0:y1+1,x0:x1+1][visible]=tuple(int(c*shade) for c in colour)
    image.paste(Image.fromarray(pixels))


def preview(v,plate_mesh,coupon_mesh,clip_mesh,path):
    image=Image.new('RGB',(1500,1650),'white')
    d=ImageDraw.Draw(image)
    fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=ImageFont.truetype(fontfile,25)
    title=ImageFont.truetype(fontfile,35)
    def text(x,y,value,large=False):
        d.text((x,y),value,fill='#28383c',font=title if large else font)
    text(50,25,'Grelha pintos V3 — placa universal + presilhas',True)
    text(50,75,'217,3 × 179,8 × 30 mm | aberturas 8 × 8 mm | redução 0,2 mm por placa')
    text(50,115,'8 encaixes fêmea inferiores: 2 por lado. Nos lados exteriores ficam vazios.')
    # Actual plate mesh viewed from underside (its printing orientation).
    draw_mesh(image,plate_mesh,(750,480),2.6,(98,167,159))
    text(50,720,'Vista inferior do STL: os alojamentos ficam dentro do contorno da placa.')
    text(50,760,'Uma única placa para cantos, bordas e interior; 26 presilhas para 2 × 5 placas.')
    # Same real sample geometry, assembled, shown in use orientation.
    right,left,clip=assembly_checks(v,coupon_model(v))
    combined=right+left+clip
    raw=combined.to_mesh()
    sample=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=False)
    draw_mesh(image,sample,(380,1110),7.0,(98,167,159),flip_z=v['HEIGHT'])
    # Mark the seam on the coplanar sample top face.
    d.line([(492,851.84),(268,948.16)],fill='#477d76',width=2)
    text(50,1120,'Amostra montada: duas bordas + uma presilha')
    # Section at the centre of a connector, with the seam vertical in the drawing.
    ox,oy,s=1000,1160,18
    def poly(vertices,colour):
        pts=[(ox+x*s,oy-z*s) for x,z in vertices]
        d.polygon(pts,fill=colour)
        d.line(pts+[pts[0]],fill='#294844',width=2)
    for sign in (-1,1):
        poly([(sign*0,3.2),(sign*4.2,3.2),(sign*4.2,14.8),(sign*0,14.8)],'#62a79f')
        poly([(sign*0.8,5.6),(sign*3.4,5.6),(sign*3.4,7.8),
              (sign*2.8,7.8),(sign*2.8,14.8),(sign*0.8,14.8)],'white')
        poly([(sign*2.8,9.4),(sign*4.2,9.4),
              (sign*4.2,13.8),(sign*2.8,13.8)],'white')
    poly(v['clip_contour'](), '#e9a452')
    text(780,1120,'Corte dos encaixes (pés para cima)')
    text(780,1160,'Laranja: presilha; verde: bordas reforçadas')
    text(50,1250,'Presilha impressa deitada de lado em PETG: braços de 1,2 mm, rampa a 45°.')
    draw_mesh(image,clip_mesh,(200,1460),8.0,(233,164,82))
    text(390,1320,'Amostra: 2 bordas + presilhas suave / padrão / firme')
    text(390,1370,'Diferença de 0,1 mm no gancho; escolher a que prende e solta bem.')
    text(390,1420,'Inserir por baixo. Janelas interiores permitem pressionar e soltar os braços.')
    text(390,1470,'A retenção física depende do filamento e da impressão; testar a amostra.')
    text(50,1570,'Geometria STL verificada. Sem validação física de elasticidade, carga ou apoio das patas.')
    image.save(path)


def main():
    v=parameters()
    plate=plate_model(v)
    coupon=coupon_model(v)
    assembly_checks(v,coupon)
    files={}
    def save(label,solid,components=1):
        name=STEM+'-'+label+'.stl'
        path=ROOT/'downloads'/name
        mesh=export(solid,path,components)
        files[name]=path
        return mesh
    plate_mesh=save('placa-universal',plate)
    np.testing.assert_allclose(plate_mesh.bounds,[[0,0,0],[v['WIDTH'],v['DEPTH'],v['HEIGHT']]],atol=0.0001)
    two_coupons=coupon+coupon.translate((v['COUPON_WIDTH']+6,0,0))
    coupon_mesh=save('amostra-duas-bordas',two_coupons,components=2)
    standard=None
    for label,reach in [('presilha-suave',3.1),('presilha-padrao',3.2),('presilha-firme',3.3)]:
        assembly_checks(v,coupon,reach)
        mesh=save(label,clip_model(v,reach))
        if label=='presilha-padrao': standard=mesh
    ref=json.loads((ROOT/'fusion/GrelhaPintosV2/validation.json').read_text())
    stats={
        'reference':ref['reference'],'new_extents_mm':[v['WIDTH'],v['DEPTH'],v['HEIGHT']],
        'plate_volume_mm3':plate.volume(),'v2_plate_volume_mm3':ref['new_volume_mm3'],
        'socket_reinforcement_added_mm3':plate.volume()-ref['new_volume_mm3'],
        'solid_volume_reduction_percent':100*(1-plate.volume()/ref['reference']['union_volume_mm3']),
        'standard_clip_volume_mm3':clip_model(v).volume(),
        'complete_2_by_5_solid_volume_mm3':10*plate.volume()+26*clip_model(v).volume(),
        'complete_2_by_5_reduction_percent':100*(1-(10*plate.volume()+26*clip_model(v).volume())/
                                              (10*ref['reference']['union_volume_mm3'])),
        'sockets_per_plate':8,'clips_for_2_by_5':26,'hole_mm':8,
        'assembled_envelope_mm':[2*v['WIDTH'],5*v['DEPTH']],
        'seated_clip_interference_mm3':0,'idealised_required_finger_deflection_mm':0.45,
        'socket_side_clearance_mm':(v['SOCKET_WIDTH']-v['CLIP_WIDTH'])/2,
        'hook_retention_overlap_mm':v['CLIP_HOOK_REACH']-v['SOCKET_THROAT_FAR'],
        'release_access_windows':8,
        'physical_retention_force_and_fatigue_tested':False,'prototype_only':True}
    stats_path=FOLDER/'validation.json'
    stats_path.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    picture=ROOT/'designs/grelha-pintos-v3-encaixes.png'
    preview(v,plate_mesh,coupon_mesh,standard,picture)
    files.update({'GrelhaPintosV3/GrelhaPintosV3.py':FOLDER/'GrelhaPintosV3.py',
                  'README.md':FOLDER/'README.md','validation.json':stats_path,
                  picture.name:picture})
    package=ROOT/'downloads/grelha-pintos-v3-encaixes.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as z:
        for name,path in files.items(): z.write(path,name)
    with ZipFile(package) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(files)
        for name,path in files.items(): assert z.read(name)==path.read_bytes()
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    print('Five STL files closed and reloaded; fit geometry and ZIP verified.')


if __name__=='__main__':
    main()
