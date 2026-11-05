"""One outer wall diagnostic from the user's physically successful 0-wall test.

Only the object wall_loops override changes, from 0 to 1. All geometry,
filament/process configuration and seam painting are preserved byte-for-byte.
Native checks establish the paths, not the physical fit or surface quality.
"""
import argparse,hashlib,json,math
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from build_m7_orange_test_v2 import archive,slice_project,summarize

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-tijolo-teste-laranja-v5-uma-parede'
FOLDER=ROOT/'fusion/M7TijoloTesteLaranjaV5'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf'


def preview(rows,bounds):
    out=Image.new('RGB',(1100,1050),'#f5f6f8');d=ImageDraw.Draw(out)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    d.text((35,25),'M7 — V5, uma parede exterior',font=font(34),fill='#263446')
    d.text((35,80),'Percursos da última camada · Bambu Studio 2.9.1.70',font=font(23),fill='#465468')
    xmin,ymin,xmax,ymax=bounds
    scale=10.8;left=75;bottom=890
    xy=lambda p:(left+(p[0]-xmin)*scale,bottom-(p[1]-ymin)*scale)
    for r in rows:
        if r['layer']!=.6:continue
        color={'Outer wall':'#343e4e','Top surface':'#df7b23','Gap infill':'#3266cc'}.get(r['feature'])
        if color:d.line([xy(r['a']),xy(r['b'])],fill=color,width=4 if r['feature']=='Outer wall' else 2)
    outer=[r for r in rows if r['layer']==.6 and r['feature']=='Outer wall']
    x,y=xy(outer[0]['a']);d.ellipse((x-7,y-7,x+7,y+7),fill='#be2640')
    d.line((x,y+10,x,y+45),fill='#be2640',width=2)
    d.text((100,945),'Costura numa zona reta do bordo',font=font(24),fill='#be2640')
    for i,text in enumerate(('1 parede exterior','0 paredes interiores','Monotonic line a 45°','Fluxo laranja 0,931','46,4 × 66,4 × 0,60 mm')):
        d.text((650,240+i*60),text,font=font(25),fill='#263446')
    d.text((650,620),'Cinzento: parede',font=font(23),fill='#343e4e')
    d.text((650,665),'Laranja: superfície',font=font(23),fill='#df7b23')
    d.text((650,710),'Azul: lacuna interior',font=font(23),fill='#3266cc')
    d.text((35,1000),'Percursos do Gcode, não uma simulação do acabamento físico.',font=font(21),fill='#465468')
    out.save(ROOT/'designs'/f'{PREFIX}-percursos.png')


def main(args):
    blobs=archive(args.source)
    cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['filament_flow_ratio'][0]=='0.931'
    assert cfg['top_surface_pattern']=='monotonicline' and cfg['infill_direction']=='45'
    assert cfg['filament_scarf_seam_type'][0]=='none'
    settings=ET.fromstring(blobs['Metadata/model_settings.config'])
    assert len(settings.findall('object'))==1
    override=settings.find('object/metadata[@key="wall_loops"]')
    assert override is not None and override.get('value')=='0'
    old=b'key="wall_loops" value="0"';new=b'key="wall_loops" value="1"'
    model=blobs['Metadata/model_settings.config'];assert model.count(old)==1
    changed=model.replace(old,new,1)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():
            z.writestr(name,changed if name=='Metadata/model_settings.config' else data)
    output=archive(TARGET)
    assert output['Metadata/model_settings.config'].replace(new,old,1)==model
    assert all(output[k]==v for k,v in blobs.items() if k!='Metadata/model_settings.config')
    a,ar=slice_project(args.bambu_bin,args.source,args.work_dir/'reference')
    b,br=slice_project(args.bambu_bin,TARGET,args.work_dir/'candidate')
    assert not any(r['feature'] in ('Inner wall','Outer wall') for r in ar)
    assert not any(r['feature']=='Inner wall' for r in br)
    assert len(b['objects'])==1
    box=b['objects'][0]['bbox'];dims=[box[k] for k in ('width','depth','height')]
    assert all(abs(v-t)<.001 for v,t in zip(dims,[46.4,66.4,.6]))
    bbox=[box['x'],box['y'],box['x']+box['width'],box['y']+box['depth']]
    loops=[]
    for h in (.2,.4,.6):
        wall=[r for r in br if r['layer']==h and r['feature']=='Outer wall']
        assert len(wall)>4
        assert all(r['b']==s['a'] for r,s in zip(wall,wall[1:]))
        seam_start,seam_end=wall[0]['a'],wall[-1]['b']
        gap=math.dist(seam_start,seam_end);assert gap<.1
        assert bbox[0]+10<seam_start[0]<bbox[2]-10
        assert bbox[1]<seam_start[1]<bbox[1]+1
        speed=20 if h==.2 else 50;accel=500 if h==.2 else 1000
        assert all(abs(r['speed_mm_s']-speed)<.001 and r['acceleration_mm_s2']==accel for r in wall)
        loops.append(dict(layer_mm=h,contiguous_outer_loop_count=1,inner_wall_count=0,
            outer_segments=len(wall),seam_start_xy_mm=seam_start,seam_end_xy_mm=seam_end,
            seam_gap_mm=gap,seam_on_straight_edge=True,speed_mm_s=speed,acceleration_mm_s2=accel))
    top=[r for r in br if r['layer']==.6 and r['feature']=='Top surface']
    assert all(r['speed_mm_s']==25 and r['acceleration_mm_s2']==1000 for r in top)
    assert abs(sum(f['total_used_g'] for f in a['filaments'])-sum(f['total_used_g'] for f in b['filaments']))<.02
    report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        source_file=args.source.name,source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        bambu_version='02.09.01.70',native_slice_exit=0,
        only_input_change={'object.wall_loops':{'before':0,'after':1}},
        global_wall_loops_preserved=cfg['wall_loops'],
        configuration_geometry_seam_paint_and_other_archive_entries_byte_identical=True,
        object_settings_identical_except_wall_override=True,dimensions_mm=dims,
        orange_flow_ratio=.931,top_pattern='monotonicline',infill_angle_degrees=45,
        layer_wall_checks=loops,brim=False,supports=False,prime_tower=False,
        reference=summarize(a,ar),candidate=summarize(b,br),
        physical_print_tested=False,physical_fit_tested=False,
        purpose='Assess whether a dedicated outer contour improves the edge and dry fit without two inner walls.',
        limitation='A native slice cannot guarantee removal of the protrusion or a defect-free seam.')
    FOLDER.mkdir(exist_ok=True)
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    preview(br,bbox)
    print(json.dumps({'project':TARGET.name,'seconds':b['total_predication'],
        'grams':sum(f['total_used_g'] for f in b['filaments']),'walls':loops,'sha256':report['sha256']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-one-wall-v5'))
    main(p.parse_args())
