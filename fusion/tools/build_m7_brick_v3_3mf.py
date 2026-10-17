"""Export, slice and package the V3 brick; native checks shared with V1/V2."""
import argparse
import os
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree
import trimesh

from build_m7_prototypes_v1_3mf import build
from build_m7_prototypes_v1_3mf import read_project,plate_meshes
from build_m7_brick_v2_3mf import package
from generate_m7_brick_v3 import ROOT,FOLDER,PREFIX


def compare_slicing(work):
    project=ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf'
    blobs,settings,_=read_project(project)
    native=plate_meshes(blobs,settings)[3][0][2]
    source=trimesh.load(ROOT/'downloads'/f'{PREFIX}-7-ciano.stl',force='mesh')
    target_points=np.unique(source.vertices[:,:2],axis=0)
    native_points=np.unique(native.vertices[:,:2],axis=0)
    tree=cKDTree(target_points)
    nc,sc=native.center_mass[:2],source.center_mass[:2]
    def rotation(deg):
        a=np.radians(deg);return np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    def score(deg):
        distances=tree.query((native_points-nc)@rotation(deg).T+sc)[0]
        return float((distances**2).mean())
    coarse=min(range(360),key=score)
    angle=min(np.linspace(coarse-1,coarse+1,401),key=score)
    transform=rotation(angle)
    max_error=float(tree.query((native_points-nc)@transform.T+sc)[0].max())
    assert max_error<.01,('Mesh alignment',max_error)
    code=(work/'tijolo/slicing/plate_4.gcode').read_text()
    lo,hi=native.bounds[:,:2];x=y=0;layer=0;feature='';width=.42;segments=[]
    for line in code.splitlines():
        marker=re.match(r'; layer num/total_layer_count: (\d+)/(\d+)',line)
        if marker:layer=int(marker[1]);last=int(marker[2])
        if line.startswith('; FEATURE: '):feature=line.split(': ',1)[1]
        if line.startswith('; LINE_WIDTH: '):width=float(line.split(': ',1)[1])
        if not re.match(r'^G[01] ',line):continue
        values={k:float(v) for k,v in re.findall(r'([XYE])([-+]?\d*\.?\d+)',line)}
        nx,ny=values.get('X',x),values.get('Y',y)
        if layer==6 and values.get('E',0)>0 and ('X' in values or 'Y' in values):
            if lo[0]-.5<nx<hi[0]+.5 and lo[1]-.5<ny<hi[1]+.5:
                a=(np.array([x,y])-nc)@transform.T+sc;b=(np.array([nx,ny])-nc)@transform.T+sc
                if np.linalg.norm(a-b)>1e-6:segments.append((a,b,width,feature))
        x,y=nx,ny
    assert len(segments)>30 and any('Outer wall' in f for a,b,w,f in segments)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    image=Image.new('RGB',(1500,1080),'#f4f6f8');d=ImageDraw.Draw(image)
    d.text((40,25),'7 V3 — comparação com o fatiamento real',font=font(34),fill='#17385B')
    d.text((60,135),'Modelo STL',font=font(28),fill='#17385B')
    d.text((790,135),'Última camada · Bambu Studio',font=font(28),fill='#17385B')
    low,high=source.bounds[:,:2];scale=93
    def pixel(p,index):
        return (375+index*730+(p[0]-(low[0]+high[0])/2)*scale,
                580-(p[1]-(low[1]+high[1])/2)*scale)
    for i in range(2):
        for triangle in source.triangles:
            d.polygon([pixel(p[:2],i) for p in triangle],fill='#009FCA' if i==0 else '#dfe8eb')
    for a,b,w,feature in segments:
        pa,pb=pixel(a,1),pixel(b,1);size=max(1,round(w*scale));r=size/2
        d.line((pa,pb),fill='#009FCA',width=size)
        for px,py in (pa,pb):d.ellipse((px-r,py-r,px+r,py+r),fill='#009FCA')
    d.text((40,995),'Mesma orientação e escala · à direita: percursos com a largura de extrusão indicada no G-code.',font=font(24),fill='#17385B')
    d.text((40,1040),'O arredondamento das pequenas saliências depende do bico de 0,4 mm; a impressão física é o teste final.',font=font(23),fill='#17385B')
    image.save(ROOT/f'designs/{PREFIX}-fatiador.png')
    report=json.loads((FOLDER/'geometry-validation.json').read_text())
    report['slicer_comparison']={'last_layer':6,'extrusion_segments':len(segments),
        'native_to_source_alignment_max_error_mm':max_error,'view':'Source silhouette vs final-layer G1 sweeps at G-code widths',
        'same_orientation_and_scale':True,'physical_result_not_tested':True}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Compared final-layer extrusion paths:',len(segments),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-v3-bambu'))
    p.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    p.add_argument('--package-only',action='store_true');a=p.parse_args()
    extra=[Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu'),a.bambu_bin.parent]
    folders=[str(v) for v in extra if v.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):folders.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH']=':'.join(folders)
    if not a.package_only:
        build('tijolo',a,version='v3',folder=FOLDER)
        compare_slicing(a.work_dir)
    images=[PREFIX+suffix for suffix in ('-CAD.png','-comparacao.png','-pratos.png','-fatiador.png')]
    if (FOLDER/'README.md').exists() and all((ROOT/'designs'/n).exists() for n in images):
        package(folder=FOLDER,prefix=PREFIX,image_names=images)


if __name__=='__main__':main()
