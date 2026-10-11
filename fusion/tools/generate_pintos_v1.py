"""Generate the chick prototype STL, engineering preview and ZIP.

Requires the QR tools venv's numpy, Pillow, trimesh and manifold3d.
Usage: python fusion/tools/generate_pintos_v1.py --reference-stl ORIGINAL.stl
The uploaded reference itself is not copied or published.
"""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/GrelhaPintosV1'


def parameters():
    path = FOLDER/'GrelhaPintosV1.py'
    tree = ast.parse(path.read_text())
    pure = [n for n in tree.body if isinstance(n,ast.Assign) or
            (isinstance(n,ast.FunctionDef) and n.name in
             ('layout','foot_contour','validate'))]
    v = {'math': math}
    exec(compile(ast.Module(body=pure,type_ignores=[]),str(path),'exec'),v)
    return v


def cube(x,y,z,w,h,d):
    return md.Manifold.cube((w,h,d)).translate((x,y,z))


def model(v):
    p = v['validate']()
    w,h,t,r = [v[k] for k in ('WIDTH','DEPTH','GRID_THICKNESS','CORNER_RADIUS')]
    outline = md.CrossSection.square((w-2*r,h-2*r)).translate((r,r)).offset(
        r, circular_segments=64)
    body = outline.extrude(t)
    holes = [cube(x,y,-1,v['HOLE'],v['HOLE'],t+2)
             for x in p['xs'] for y in p['ys']]
    body -= md.Manifold.batch_boolean(holes,md.OpType.Add)
    pieces = [body]
    for x in p['rib_x']:
        pieces.append(cube(x-v['WEB']/2,0,t,v['WEB'],h,v['RIB_DEPTH']))
    for y in p['rib_y']:
        pieces.append(cube(0,y-v['WEB']/2,t,w,v['WEB'],v['RIB_DEPTH']))
    for x,y in p['feet']:
        pieces.append(md.CrossSection([v['foot_contour'](x,y)]).extrude(
            v['HEIGHT']-t).translate((0,0,t)))
    result = md.Manifold.batch_boolean(pieces,md.OpType.Add)
    assert result.status() == md.Error.NoError
    assert len(result.decompose()) == 1
    assert len(result.slice(t/2).to_polygons()) == p['nx']*p['ny']+1
    expected_area = w*h - (4-math.pi)*r*r - p['nx']*p['ny']*v['HOLE']**2
    assert abs(result.slice(t/2).area()-expected_area) < 0.1
    return result


def reference_volume(path):
    mesh = trimesh.load(path,force='mesh')
    parts = mesh.split(only_watertight=False)
    # The submitted STL has overlapping shells. Adding its signed volumes
    # would overstate material by roughly 2x: fuse them before comparison.
    assert all(p.is_watertight for p in parts)
    objects = [md.Manifold(md.Mesh(np.asarray(p.vertices,dtype=np.float32),
                                  np.asarray(p.faces,dtype=np.uint32))) for p in parts]
    assert all(p.status() == md.Error.NoError for p in objects)
    union = md.Manifold.batch_boolean(objects,md.OpType.Add)
    assert union.status() == md.Error.NoError
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'extents_mm':mesh.extents.tolist(),'overlapping_shells':len(parts),
            'union_volume_mm3':union.volume()}


def preview(v, mesh, path):
    p = v['layout']()
    im = Image.new('RGB',(1400,1350),'white')
    d = ImageDraw.Draw(im)
    fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=ImageFont.truetype(fontfile,24)
    title=ImageFont.truetype(fontfile,34)
    def text(x,y,label,large=False):
        d.text((x,y),label,fill='#28383c',font=title if large else font)
    text(50,25,'Grelha pintos V1 — protótipo',True)
    text(50,72,'217,3 × 179,8 × 30 mm | redução de 0,2 mm POR PLACA em cada direção')
    text(50,112,'Aberturas 6 × 6 mm preservadas; não certificadas para pintos recém-nascidos.')
    text(50,150,'Nos primeiros dias: cobertura aderente temporária; observar o apoio das patas.')
    # Dimensioned plan drawn from the same coordinates as both CAD generators.
    scale,x,y=3.2,50,235
    d.rounded_rectangle((x,y,x+v['WIDTH']*scale,y+v['DEPTH']*scale),
                       radius=v['CORNER_RADIUS']*scale,fill='#62a79f')
    for xx in p['xs']:
        for yy in p['ys']:
            d.rectangle((x+xx*scale,y+yy*scale,
                         x+(xx+v['HOLE'])*scale,y+(yy+v['HOLE'])*scale),fill='white')
    text(50,190,'Vista superior: barras 1,6 mm; grelha 3,2 mm de espessura')
    text(50,825,'Reforços sob 3 barras em cada direção; 9 pés em cruz, sem cavidades fechadas.')
    # Render actual generated triangles in use orientation (feet downward).
    verts=mesh.vertices.copy()
    verts[:,0]-=v['WIDTH']/2
    verts[:,1]-=v['DEPTH']/2
    verts[:,2]=v['HEIGHT']-verts[:,2]
    normals=mesh.face_normals.copy()
    normals[:,2]*=-1
    triangles=verts[mesh.faces]
    depth=triangles.mean(axis=1)@np.array([1,1,2])
    for i in np.argsort(depth):
        projected=[(1045+(xx-yy)*1.5,540+(xx+yy)*0.68-zz*2.5)
                   for xx,yy,zz in triangles[i]]
        shade=max(0.45,min(1.0,0.7+0.25*normals[i,2]+0.12*normals[i,0]))
        colour=tuple(int(c*shade) for c in (98,167,159))
        d.polygon(projected,fill=colour)
    text(800,680,'Geometria STL em posição de uso')
    # Side view, in printing orientation, to make support-free construction clear.
    x,y,s=50,1220,4
    d.rectangle((x,y-v['GRID_THICKNESS']*s,x+v['WIDTH']*s,y),fill='#62a79f')
    for xx in p['rib_x']:
        d.rectangle((x+(xx-v['WEB']/2)*s,y-(v['GRID_THICKNESS']+v['RIB_DEPTH'])*s,
                     x+(xx+v['WEB']/2)*s,y-v['GRID_THICKNESS']*s),
                    fill='#407b75')
    d.rectangle((x,y-(v['GRID_THICKNESS']+v['RIB_DEPTH'])*s,x+v['WIDTH']*s,
                 y-v['GRID_THICKNESS']*s),fill='#407b75')
    for xx in p['rib_x']:
        d.rectangle((x+(xx-v['FOOT_SPAN']/2)*s,y-v['HEIGHT']*s,
                     x+(xx+v['FOOT_SPAN']/2)*s,y-v['GRID_THICKNESS']*s),fill='#62a79f')
    text(50,990,'Impressão: face de apoio na mesa, pés para cima. Sem suportes.')
    text(50,1030,'Esquema lateral em orientação de impressão (três pés alinhados na vista).')
    text(50,1250,'Primeiro imprimir um módulo; validar encaixe, estabilidade e limpeza antes dos dez.')
    text(50,1290,'Protótipo: altura proposta de 30 mm; redução de 0,2 mm por placa confirmada.')
    im.save(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference-stl',type=Path,required=True)
    args=parser.parse_args()
    v=parameters()
    result=model(v)
    # Boolean joins at coplanar grid/rib/foot faces can leave zero-length
    # edges when exported as STL's float32 coordinates. Simplify within
    # 0.00001 mm before welding, then verify the actual saved topology.
    source=result.simplify(0.00001).to_mesh()
    mesh=trimesh.Trimesh(vertices=source.vert_properties[:,:3],
                         faces=source.tri_verts,process=True)
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000001))
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert len(mesh.split()) == 1
    assert np.allclose(mesh.bounds,[[0,0,0],[v['WIDTH'],v['DEPTH'],v['HEIGHT']]],atol=0.001)
    stl=ROOT/'downloads/grelha-pintos-v1-217.3x179.8x30.stl'
    mesh.export(stl)
    saved=trimesh.load(stl,force='mesh')
    saved.merge_vertices(digits_vertex=5)
    assert saved.is_watertight and len(saved.split()) == 1
    ref=reference_volume(args.reference_stl)
    stats={'reference':ref,'new_extents_mm':[v['WIDTH'],v['DEPTH'],v['HEIGHT']],
           'new_volume_mm3':result.volume(),
           'solid_volume_reduction_percent':100*(1-result.volume()/ref['union_volume_mm3']),
           'hole_mm':v['HOLE'],'holes':v['layout']()['nx']*v['layout']()['ny'],
           'clearance_interpretation':'0.2 mm per module in each axis; user confirmed',
           'layout_modules':[2,5],
           'assembled_envelope_mm':[2*v['WIDTH'],5*v['DEPTH']],
           'prototype_only':True,'physical_load_and_hatchling_footing_tested':False}
    stats_path=FOLDER/'validation.json'
    stats_path.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    picture=ROOT/'designs/grelha-pintos-v1-esquema.png'
    preview(v,mesh,picture)
    files={'GrelhaPintosV1/GrelhaPintosV1.py':FOLDER/'GrelhaPintosV1.py',
           'README.md':FOLDER/'README.md','validation.json':stats_path,
           stl.name:stl,picture.name:picture}
    package=ROOT/'downloads/grelha-pintos-v1.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as z:
        for name,path in files.items(): z.write(path,name)
    with ZipFile(package) as z:
        assert z.testzip() is None
        for name,path in files.items(): assert z.read(name)==path.read_bytes()
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    print('STL saved/reloaded: one closed solid. ZIP entries match source files.')


if __name__=='__main__':
    main()
