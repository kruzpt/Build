"""Remove Monotonic-line corner gap detours from the user's successful 0-wall test.

Only top_surface_pattern changes. The native Gcode checks establish the new
paths, not that the physical corner protrusion is eliminated.
"""
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image,ImageDraw,ImageFont
from build_m7_orange_test_v2 import archive,slice_project,summarize

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-tijolo-teste-laranja-v4-zero-paredes'
FOLDER=ROOT/'fusion/M7TijoloTesteLaranjaV4'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf'


def corner_image(before,after):
    canvas=Image.new('RGB',(1340,890),'#f5f6f8');draw=ImageDraw.Draw(canvas)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    draw.text((30,20),'Zero paredes — percursos no canto do prato X+ / Y+',font=font(29),fill='#263446')
    draw.text((30,65),'Camada Z=0,60 mm · janela de 3 × 3 mm · Bambu Studio 2.9.1.70',font=font(22),fill='#465468')
    for i,rows in enumerate((before,after)):
        left=30+i*665;plot=Image.new('RGB',(600,600),'white');pd=ImageDraw.Draw(plot)
        xy=lambda p:((p[0]-147.6)*200,600-(p[1]-158.3)*200)
        for r in rows:
            if r['layer']!=.6 or r['feature'] not in ('Top surface','Gap infill'):continue
            pd.line([xy(r['a']),xy(r['b'])],fill='#3266cc' if r['feature']=='Gap infill' else '#e07716',width=5 if r['feature']=='Gap infill' else 3)
        if i==0:
            x,y=xy((149.15,160.517));pd.ellipse((x-18,y-18,x+18,y+18),outline='#3266cc',width=2)
        canvas.paste(plot,(left,165));draw.rectangle((left,165,left+600,765),outline='#bbc4ce')
        draw.text((left,120),'Recebido: Monotonic line' if i==0 else 'V4: Monotonic',font=font(24),fill='#263446')
        draw.text((left,783),'Azul: micropreenchimento adicional' if i==0 else 'Sem percursos adicionais de lacunas',font=font(22),fill='#263446')
    draw.text((30,825),'Laranja: topo · azul: Gap infill · segmentos obtidos do Gcode; a fotografia pode estar rodada.',font=font(19),fill='#465468')
    draw.text((30,855),'O percurso adicional foi removido. A origem e a resolução do defeito físico ainda precisam de confirmação.',font=font(18),fill='#465468')
    canvas.save(ROOT/'designs'/f'{PREFIX}-percursos.png')


def main(args):
    blobs=archive(args.source);cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['filament_flow_ratio'][0]=='0.931' and cfg['top_surface_pattern']=='monotonicline'
    assert cfg['infill_direction']=='45' and cfg['filament_scarf_seam_type'][0]=='none'
    assert b'key="wall_loops" value="0"' in blobs['Metadata/model_settings.config']
    old=dict(cfg);cfg['top_surface_pattern']='monotonic'
    assert [k for k in cfg if cfg[k]!=old[k]]==['top_surface_pattern']
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():
            if name=='Metadata/project_settings.config':data=json.dumps(cfg,indent=2).encode()
            z.writestr(name,data)
    output=archive(TARGET)
    assert all(v==output[k] for k,v in blobs.items() if k!='Metadata/project_settings.config')
    a,ar=slice_project(args.bambu_bin,args.source,args.work_dir/'reference')
    b,br=slice_project(args.bambu_bin,TARGET,args.work_dir/'candidate')
    assert [r for r in ar if r['layer']<.6]==[r for r in br if r['layer']<.6]
    assert not any(r['feature'] in ('Inner wall','Outer wall','Gap infill') for r in br)
    top=[r for r in br if r['layer']==.6]
    assert all(r['feature']=='Top surface' and abs(r['speed_mm_s']-25)<.001 for r in top)
    assert all(r['acceleration_mm_s2']==1000 for r in top)
    assert any(r['feature']=='Gap infill' and r['length']<.1 for r in ar)
    assert abs(sum(x['total_used_g'] for x in a['filaments'])-sum(x['total_used_g'] for x in b['filaments']))<.01
    assert len(b['objects'])==1
    box=b['objects'][0]['bbox'];dims=[box[k] for k in ('width','depth','height')]
    assert all(abs(a-b)<.001 for a,b in zip(dims,[46.4,66.4,.6]))
    FOLDER.mkdir(exist_ok=True)
    report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),bambu_version='02.09.01.70',
        native_slice_exit=0,only_change={'top_surface_pattern':{'before':'monotonicline','after':'monotonic'}},
        object_wall_override_zero_preserved=True,no_wall_paths_verified=True,
        geometry_object_settings_and_seam_paint_byte_identical=True,first_two_layers_paths_identical=True,
        dimensions_mm=dims,orange_flow_ratio=.931,infill_angle_degrees=45,
        candidate_gap_infill_paths=0,candidate_top_speed_mm_s=25,candidate_top_acceleration_mm_s2=1000,
        source_shortest_gap_segment_mm=min(r['length'] for r in ar if r['feature']=='Gap infill'),
        source_tiny_gap_line_width_mm=.104186,
        speed_note='Source F commands are requested feedrates; submillimetre paths cannot reach 250 mm/s.',
        reference=summarize(a,ar),candidate=summarize(b,br),
        top_summary_note='Counts and lengths include connecting extrusion segments, not just long diagonal strokes.',
        caveat='Suspected path contribution, not a proven physical cause. Corner correspondence depends on photo orientation.',
        physical_print_tested=False,physical_fit_tested=False)
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    corner_image(ar,br)
    print(json.dumps({k:report[k] for k in ('sha256','candidate_gap_infill_paths','source_shortest_gap_segment_mm')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-zero-wall-v4'))
    main(p.parse_args())
