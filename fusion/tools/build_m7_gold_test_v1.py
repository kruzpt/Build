"""Controlled gold diagnostic: only gold wall count 3 -> 5 in M7 V8.

Same geometry, flow, temperatures, speeds, retraction, orange backing and AMS
sequence. The native G-code comparison tests removal of tiny top/gap fills;
it cannot certify the physical finish.
"""
import argparse,hashlib,json,os,sys,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image,ImageDraw,ImageFont
from build_pintos_pla_3mf import read_project,run_cli
from build_m7_prototypes_v1_3mf import annotate
from build_m7_orange_test_v2 import paths

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-tijolo-teste-dourado-v1-5-paredes'
FOLDER=ROOT/'fusion/M7TijoloTesteDouradoV1'
SOURCE=ROOT/'downloads/m7-tijolo-v8-uma-parede-A1-AMS-2-pratos.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'


def archive(p):
    with ZipFile(p) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}


def slice_plate(binary,source,work):
    work.mkdir(parents=True,exist_ok=True)
    run_cli(binary,['--datadir',str(work/'user'),'--debug','2','--slice','2','--orient','0','--arrange','0',
        '--outputdir',str(work/'slice'),'--export-3mf','validation.3mf',str(source)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text());assert result['return_code']==0
    p=result['sliced_plates'][0];assert p['id']==2 and not p.get('warning_message')
    b=archive(work/'slice/validation.3mf');code=b[next(n for n in b if n.endswith('.gcode'))].decode()
    assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
    return p,paths(code),hashlib.sha256(code.encode()).hexdigest()


def preview(before,after):
    im=Image.new('RGB',(1400,1220),'#f4f6f8');d=ImageDraw.Draw(im)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    d.text((35,25),'Dourado · comparação dos percursos de topo',font=font(32),fill='#253549')
    d.text((35,80),'Mesma geometria e fluxo 0,9702 · alteração apenas no número de paredes do dourado',font=font(22),fill='#526377')
    top=lambda rows:[r for r in rows if r['tool']==2 and r['layer']==1.6]
    for j,(title,rows) in enumerate([('V8 · 3 paredes',top(before)),('Teste V1 · 5 paredes',top(after))]):
        left=65+j*700;bottom=1020;scale=14.5
        lo=[min(min(r['a'][k],r['b'][k]) for r in rows) for k in (0,1)]
        xy=lambda p:(left+(p[0]-lo[0])*scale,bottom-(p[1]-lo[1])*scale)
        d.text((left,145),title,font=font(27),fill='#253549')
        for r in sorted(rows,key=lambda r:r['feature'] in ('Top surface','Gap infill')):
            c={'Outer wall':'#ac8b36','Inner wall':'#ac8b36','Top surface':'#d54a43','Gap infill':'#963e9e'}.get(r['feature'],'#7a8999')
            d.line([xy(r['a']),xy(r['b'])],fill=c,width=5 if r['feature'] in ('Top surface','Gap infill') else 3)
        d.text((left,1060),'26 traços de topo + 19 de lacunas' if j==0 else 'Preenchido com contornos',font=font(23),fill='#253549')
    d.text((35,1120),'Vermelho: topo curto · roxo: lacunas · dourado: paredes',font=font(23),fill='#526377')
    d.text((35,1165),'G-code fatiado no Bambu Studio 02.08.02.61 · efeito no acabamento físico ainda por testar',font=font(20),fill='#526377')
    im.save(ROOT/'designs'/f'{PREFIX}-comparacao.png')


def main(a):
    FOLDER.mkdir(exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
    b=archive(SOURCE);original=dict(b);cfg=json.loads(b['Metadata/project_settings.config'])
    assert cfg['filament_flow_ratio']==['0.931','0.9702','0.98','0.98']
    settings=ET.fromstring(b['Metadata/model_settings.config'])
    gold=next(p for o in settings.findall('object') for p in o.findall('part') if p.find("metadata[@key='source_file'][@value='m7-tijolo-v6-folga-relevo-dourado.stl']") is not None)
    wall=gold.find("metadata[@key='wall_loops']");assert wall.get('value')=='3';wall.set('value','5')
    settings.findall('plate')[1].find("metadata[@key='plater_name']").set('value','02 TESTE dourado V1 - cinco paredes so no dourado')
    b['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for n,data in b.items():z.writestr(n,data)
    annotate(TARGET,TARGET,cfg['filament_colour'],PREFIX)
    actual,after_settings,_=read_project(TARGET)
    assert json.loads(actual['Metadata/project_settings.config'])==cfg
    assert all(actual[n]==data for n,data in original.items() if n.startswith('3D/'))
    # Exactly one object/part metadata value changes; plate caption and native
    # thumbnails are presentation only. No other part or process override.
    before_obj=ET.fromstring(original['Metadata/model_settings.config']).findall('object')
    for x,y in zip(before_obj,after_settings.findall('object')):
        expected=ET.fromstring(ET.tostring(x))
        match=next((p for p in expected.findall('part') if p.get('id')==gold.get('id')),None)
        if match is not None:match.find("metadata[@key='wall_loops']").set('value','5')
        assert ET.canonicalize(ET.tostring(expected,encoding="unicode"),strip_text=True)==ET.canonicalize(ET.tostring(y,encoding="unicode"),strip_text=True)
    ref,br,bhash=slice_plate(a.bambu_bin,SOURCE,a.work_dir/'reference')
    test,tr,thash=slice_plate(a.bambu_bin,TARGET,a.work_dir/'candidate')
    nongold=lambda r:[p for p in r if p['tool']!=2]
    assert nongold(br)==nongold(tr),'Non-gold extrusion paths changed'
    assert ref['filament_change_times']==test['filament_change_times']==11
    assert all(r['feature'] in ('Outer wall','Inner wall') for r in tr if r['tool']==2),'Unexpected gold infill remains'
    for h in (.2,.4,.6):
        assert {r['tool'] for r in tr if r['layer']==h}=={1}
    report=[]
    for label,p,rows,h in [('V8 reference',ref,br,bhash),('V1 test',test,tr,thash)]:
        rr=[r for r in rows if r['tool']==2 and r['layer']==1.6]
        report.append(dict(name=label,seconds=p['total_predication'],grams_including_flush_and_tower=sum(f['total_used_g'] for f in p['filaments']),gold_main_grams=next(f['main_used_g'] for f in p['filaments'] if f['id']==2),top_gold_features={f:sum(r['feature']==f for r in rr) for f in sorted(set(r['feature'] for r in rr))},warnings=p.get('warning_message'),gcode_sha256=h))
    data=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),source=SOURCE.name,bambu_version='02.08.02.61',geometry_byte_identical=True,process_and_filament_config_identical=True,non_gold_extrusion_paths_identical=True,only_print_setting_change={'gold_part.wall_loops':{'before':3,'after':5}},flow=cfg['filament_flow_ratio'],temperature=cfg['nozzle_temperature'],all_gold_layers_walls_only=True,filament_changes=11,brim=False,supports=False,comparison=report,physical_print_tested=False,physical_finish_verified=False)
    (FOLDER/'bambu-validation.json').write_text(json.dumps(data,indent=2)+'\n');preview(br,tr);print(json.dumps(data,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);main(p.parse_args())
