"""Review native G-code paths, including arc moves; no physical print claim."""
import argparse,json,math,re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
PREFIX='anilha-lobito-v5-bochechas-continuas'

def paths(code):
    x=y=z=0.;layer=0.;speed=0.;feature='Custom';tool=1;relative=True;old_e=0.;rows=[]
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):layer=float(line.split(':')[1])
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        if line.startswith('M83'):relative=True
        if line.startswith('M82'):relative=False
        if line.startswith('G92 E'):old_e=float(line.split('E')[1].split()[0])
        sel=re.match(r'^M620 S(\d+)A',line)
        if sel and int(sel[1])<16:tool=int(sel[1])+1
        cmd=re.match(r'^(G[0123])\s',line)
        if not cmd:continue
        v={k:float(n) for k,n in re.findall(r'([XYZEFIJKR])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
        nx,ny,nz=v.get('X',x),v.get('Y',y),v.get('Z',z);speed=v.get('F',speed)
        ee=v.get('E',0 if relative else old_e);de=ee if relative else ee-old_e
        if not relative:old_e=ee
        if layer>0 and de>0 and math.dist((x,y),(nx,ny))>1e-7 and feature!='Custom':
            pts=[(x,y,z),(nx,ny,nz)]
            if cmd[1] in ('G2','G3'):
                assert 'R' not in v,'Unimplemented radius arc'
                cx,cy=x+v.get('I',0),y+v.get('J',0);radius=math.hypot(x-cx,y-cy)
                a=math.atan2(y-cy,x-cx);b=math.atan2(ny-cy,nx-cx)
                delta=(b-a)%(2*math.pi) if cmd[1]=='G3' else -((a-b)%(2*math.pi))
                count=max(2,int(math.ceil(abs(delta)*radius/.12)))
                pts=[(cx+radius*math.cos(a+delta*t),cy+radius*math.sin(a+delta*t),z+(nz-z)*t) for t in np.linspace(0,1,count+1)]
            rows.append(dict(layer=layer,feature=feature,tool=tool,speed=speed/60,extrusion_mm=de,points=pts))
        x,y,z=nx,ny,nz
    return rows

def main(a):
    with ZipFile(a.validation) as z:all_rows=[paths(z.read(f'Metadata/plate_{i}.gcode').decode()) for i in (1,2,3)]
    assert all(all_rows)
    summary=[]
    for i,rows in enumerate(all_rows):
        layer_values=sorted(set(r['layer'] for r in rows));assert abs(layer_values[0]-.2)<1e-6
        assert max(np.diff(layer_values))<.12001
        outer=[r['speed'] for r in rows if r['feature']=='Outer wall'];assert outer and max(outer)<=30.001
        top=[r['speed'] for r in rows if r['feature']=='Top surface'];assert not top or max(top)<=20.001
        supports=[r for r in rows if r['feature'].startswith('Support')]
        if i!=0:assert not supports
        expected={1} if i==0 else {2,3} if i==1 else {3}
        assert set(r['tool'] for r in rows)<=expected
        byfeature=defaultdict(float)
        for r in rows:byfeature[r['feature']]+=r['extrusion_mm']
        summary.append(dict(plate=i+1,extruding_tools=sorted(set(r['tool'] for r in rows)),first_extrusion_height_mm=layer_values[0],maximum_layer_step_mm=float(max(np.diff(layer_values))),outer_wall_speed_max_mm_s=max(outer),top_surface_speed_max_mm_s=max(top) if top else None,support_extrusion_length_mm=sum(r['extrusion_mm'] for r in supports),extrusion_by_feature_mm=dict(byfeature)))
    # Native body was translated in XY; derive the actual transform, don't
    # assume the slicer's bed placement or rotation.
    import sys,trimesh
    sys.path.insert(0,str(ROOT/'fusion/tools'))
    from build_pintos_pla_3mf import read_project
    from build_m7_prototypes_v1_3mf import plate_meshes
    blobs,config,plates=read_project(ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf')
    native=plate_meshes(blobs,config)
    native_parts={key:(color,mesh) for plate in native for key,color,mesh in plate}
    geo=json.loads((ROOT/'fusion/AnilhaLobitoV5/geometry.json').read_text())
    part_names={int(p.get('id')):p.find("metadata[@key='name']").get('value') for o in config.findall('object') for p in o.findall('part')}
    module_poses={};pose_errors=[]
    for part in geo['parts']:
        matches=[key for key,name in part_names.items() if name.startswith(PREFIX+'-'+part['key']+'_')]
        assert len(matches)==1,(part['key'],'native part identification')
        color,mesh=native_parts[matches[0]]
        ref=trimesh.load(ROOT/'downloads'/part['file'],force='mesh')
        assert np.array_equal(ref.faces,mesh.faces),(part['key'],'native topology changed')
        transform=np.linalg.lstsq(np.c_[ref.vertices,np.ones(len(ref.vertices))],mesh.vertices,rcond=None)[0]
        error=float(np.max(np.linalg.norm(np.c_[ref.vertices,np.ones(len(ref.vertices))]@transform-mesh.vertices,axis=1)))
        assert error<.003,(part['key'],'native transform residual',error)
        assert np.allclose(transform[:3].T@transform[:3],np.eye(3),atol=.00001)
        if part['module'] in module_poses:
            assert np.allclose(transform,module_poses[part['module']],atol=.003),(part['module'],'colors shifted inside assembly')
        module_poses[part['module']]=transform
        pose_errors.append(error)
    actual=native[0][0][2]
    source=trimesh.load(ROOT/'downloads'/f'{PREFIX}-corpo.stl',force='mesh')
    assert np.array_equal(source.faces,actual.faces)
    fit=np.linalg.lstsq(np.c_[source.vertices,np.ones(len(source.vertices))],actual.vertices,rcond=None)[0]
    assert np.max(np.linalg.norm(np.c_[source.vertices,np.ones(len(source.vertices))]@fit-actual.vertices,axis=1))<.002
    matrix=np.eye(4);matrix[:3,:]=fit.T;inverse=np.linalg.inv(matrix)
    support_points=np.array([p for r in all_rows[0] if r['feature'].startswith('Support') for p in r['points']])
    local=np.c_[support_points,np.ones(len(support_points))]@inverse.T
    local=local[(local[:,2]>=0)&(local[:,2]<=30)]
    q=(local[:,0]/12.5)**2+(local[:,1]/9)**2
    assert q.min()>1.02,('Support inside oval opening',q.min())
    report=dict(multicolor_assembly_relative_poses_verified=True,maximum_native_transform_residual_mm=max(pose_errors),arc_moves_sampled_at_maximum_step_mm=.12,body_native_transform=matrix.tolist(),support_enters_nominal_oval_opening=False,minimum_support_ellipse_equation=float(q.min()),plates=summary,physical_quality_verified=False)
    (ROOT/'fusion/AnilhaLobitoV5/toolpath-review.json').write_text(json.dumps(report,indent=2)+'\n')
    draw_preview(all_rows[0]);print(json.dumps(report,indent=2))

def draw_preview(rows):
    im=Image.new('RGB',(1340,1500),'#f4f6f8');d=ImageDraw.Draw(im)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    d.text((35,22),'Lobito V5 · revisão dos percursos do corpo',font=font(32),fill='#233347')
    d.text((35,76),'Traços reais do G-code · apoios a azul · paredes a cinzento escuro',font=font(23),fill='#536276')
    slices=[(.2,'Primeira camada'),(10.04,'Zona do focinho'),(20.,'Zona dos olhos'),(28.04,'Zona das sobrancelhas')]
    for j,(z,title) in enumerate(slices):
        r=[v for v in rows if abs(v['layer']-z)<1e-5];assert r,(z,'missing review layer')
        x0=30+(j%2)*660;y0=130+(j//2)*650
        d.text((x0+20,y0+12),f'{title} · Z {z:.2f} mm',font=font(24),fill='#233347')
        pp=np.array([p for v in r for p in v['points']]);lo=pp[:,:2].min(0);hi=pp[:,:2].max(0)
        scale=min(580/(hi[0]-lo[0]),550/(hi[1]-lo[1]));pad=((620-(hi-lo)*scale)/2)
        def xy(p):return (x0+pad[0]+(p[0]-lo[0])*scale,y0+620-pad[1]-(p[1]-lo[1])*scale)
        for v in r:
            support=v['feature'].startswith('Support')
            c='#2489b6' if support else '#344559' if 'wall' in v['feature'].lower() else '#b2bdc8'
            d.line([xy(p) for p in v['points']],fill=c,width=2 if support or 'wall' in v['feature'].lower() else 1)
    d.text((35,1450),'Apoios fora da passagem oval · detalhes de cor sem suportes · acabamento físico por testar',font=font(21),fill='#536276')
    im.save(ROOT/'designs'/f'{PREFIX}-percursos.png')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--validation',type=Path,required=True);main(p.parse_args())
