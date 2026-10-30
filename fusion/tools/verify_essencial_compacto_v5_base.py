"""Check actual inverted base/sample toolpaths; no physical finish/fit claims."""
import hashlib,json,re
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree
import trimesh
from build_pintos_pla_3mf import read_project
from build_m7_prototypes_v1_3mf import plate_meshes
from generate_essencial_compacto_v5 import ROOT,FOLDER,PREFIX,GREEN,GOLD


def main():
    project=ROOT/'downloads'/f'{PREFIX}-A1-AMS-4-pratos.3mf'
    blobs,settings,_=read_project(project);parts=plate_meshes(blobs,settings)
    source=trimesh.load(ROOT/'downloads'/f'{PREFIX}-base-verde-invertido.stl',force='mesh')
    target=next(m for k,c,m in parts[2] if c==2)
    shift=(target.bounds[0]+target.bounds[1]-source.bounds[0]-source.bounds[1])/2
    assert cKDTree(target.vertices).query(source.vertices+shift)[0].max()<.003
    # With no XY rotation, inverted Y puts the assembled rear at the printer front.
    objects=[]
    for obj in settings.findall('object'):
        props={m.get('key'):m.get('value') for m in obj.findall('metadata')}
        if props.get('name') in ('assemble_2','assemble_3'):
            assert props['seam_position']=='front'
            assert props['bottom_shell_layers']=='5' and props['wall_loops']=='3'
            objects.append(props)
    assert len(objects)==2
    report={'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),
        'base_xy_rotation_degrees':0,'printer_front_maps_to_assembled_rear':True,
        'seam_setting_is_position_preference_not_finish_guarantee':True,'plates':[],
        'physical_print_tested':False,'physical_fit_tested':False}
    canvas=Image.new('RGB',(1600,850),'#f4f6f8');draw=ImageDraw.Draw(canvas)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    with ZipFile('/tmp/essencial-compacto-v5/slice/validation.3mf') as archive:
        for index in (3,4):
            code=archive.read(f'Metadata/plate_{index}.gcode').decode()
            z=0.;tool=0;feature='Custom';x=y=0.;feed=0.;layers={};bridge=[];paths=[]
            for line in code.splitlines():
                if line.startswith('; Z_HEIGHT:'):z=float(line.split(':')[1])
                if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
                change=re.match(r'^M620 S([0-3])A',line) or re.match(r'^T([0-3])\s*$',line)
                if change:tool=int(change[1])
                if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
                vals={a:float(b) for a,b in re.findall(r'([XYEFIJ])(-?(?:\d+(?:\.\d*)?|\.\d+))',line.split(';')[0])}
                feed=vals.get('F',feed);nx,ny=vals.get('X',x),vals.get('Y',y)
                if z>0 and feature not in ('Custom','Prime tower') and vals.get('E',0)>0 and (nx,ny)!=(x,y):
                    layers.setdefault(z,set()).add(tool)
                    if feature=='Bridge':bridge.append({'z':z,'speed':feed/60})
                    if index==3 and abs(z-.16)<.0001:paths.append(((x,y),(nx,ny)))
                x,y=nx,ny
            assert len(layers)==60
            assert all(t=={1} for z,t in layers.items() if z<=8.64001)
            assert all(t=={2} for z,t in layers.items() if z>8.64001)
            assert len([z for z in layers if z>8.64001])==6
            assert any(abs(b['z']-6.56)<.0001 for b in bridge)
            assert max(b['speed'] for b in bridge)<=20.001
            report['plates'].append({'plate':index,'gcode_sha256':hashlib.sha256(code.encode()).hexdigest(),
                'green_only_layers':54,'gold_only_layers':6,'first_gold_z_mm':8.8,
                'gold_height_mm':.96,'slot_ceiling_first_bridge_z_mm':6.56,'slot_bridge_span_mm':3.6,
                'bridge_layer_z_mm':sorted(set(b['z'] for b in bridge)),
                'max_bridge_speed_mm_s':max(b['speed'] for b in bridge),
                'material_slots_by_layer':{str(z):[t+1 for t in sorted(ts)] for z,ts in layers.items()}})
            if index==3:
                # Plot only the real model's first-layer paths, excluding the tower.
                lo,hi=target.bounds[0,:2],target.bounds[1,:2]
                def point(p):return (70+(p[0]-lo[0])*7,150+(hi[1]-p[1])*7)
                for a,b in paths:draw.line([point(a),point(b)],fill=GREEN,width=2)
    draw.text((35,25),'Base V5 · percursos reais da primeira camada verde',font=font(32),fill='#203c54')
    draw.text((35,700),'Esta face fica contra o prato e será o topo visível depois de virar a base.',font=font(26),fill='#203c54')
    draw.text((35,755),'Ranhuras abertas no prato · pequenas pontes internas a Z=6,56 mm · dourado só no fim.',font=font(24),fill='#203c54')
    canvas.save(ROOT/'designs'/f'{PREFIX}-primeira-camada.png')
    (FOLDER/'base-print-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'plates':[{k:v for k,v in p.items() if k!='material_slots_by_layer'} for p in report['plates']]},indent=2))

if __name__=='__main__':main()
