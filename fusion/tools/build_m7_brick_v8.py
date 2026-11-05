"""Full decorated brick using the last tested one-wall orange backing.

Keep V7 geometry; apply one wall only to the orange carrier and transfer the
tested seam painting and measured filament flow ratios. Validate actual Gcode.
"""
import argparse,hashlib,json,os,re,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import numpy as np
from build_pintos_pla_3mf import read_project,run_cli,NS
from build_m7_orange_test_v2 import archive,paths
from build_m7_prototypes_v1_3mf import annotate
import generate_m7_prototypes_v1 as v

ROOT=v.ROOT;PREFIX='m7-tijolo-v8-uma-parede';FOLDER=ROOT/'fusion/M7TijoloV8'
SOURCE=ROOT/'downloads/m7-tijolo-v7-acabamento-A1-AMS-2-pratos.3mf'
TEST=ROOT/'downloads/m7-tijolo-teste-laranja-v5-uma-parede-A1-PLA-1-prato.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-AMS-2-pratos.3mf'


def data(obj):
    vs=np.array([[float(e.get(k)) for k in 'xyz'] for e in obj.findall(f'{{{NS}}}mesh/{{{NS}}}vertices/{{{NS}}}vertex')])
    ts=obj.findall(f'{{{NS}}}mesh/{{{NS}}}triangles/{{{NS}}}triangle')
    ids=np.array([[int(t.get(k)) for k in ('v1','v2','v3')] for t in ts])
    return vs,ids,ts


def main(args):
    w=args.work_dir;w.mkdir(parents=True,exist_ok=True);FOLDER.mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    blobs,settings,_=read_project(SOURCE);original=dict(blobs);test=archive(TEST)
    cfg=json.loads(blobs['Metadata/project_settings.config']);tcfg=json.loads(test['Metadata/project_settings.config'])
    cfg['filament_flow_ratio']=tcfg['filament_flow_ratio']
    cfg['filament_settings_id']=tcfg['filament_settings_id']
    assert cfg['filament_flow_ratio']==['0.931','0.9702','0.98','0.98']
    blobs['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
    plaque=next(o for o in settings.findall('object') if o.find("part/metadata[@key='source_file'][@value='m7-tijolo-v6-folga-placa-laranja.stl']") is not None)
    carrier=next(p for p in plaque.findall('part') if 'placa-laranja' in p.find("metadata[@key='source_file']").get('value'))
    def setting(node,key,val):
        m=node.find(f"metadata[@key='{key}']")
        if m is None:m=ET.SubElement(node,'metadata',key=key)
        m.set('value',str(val))
    setting(plaque,'infill_wall_overlap','10%')
    for part in plaque.findall('part'):setting(part,'wall_loops',1 if part is carrier else 3)
    settings.findall('plate')[1].find("metadata[@key='plater_name']").set('value','02 Placa completa V8 - fundo uma parede e relevos AMS')
    blobs['Metadata/model_settings.config']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    # Transfer paint attributes without rewriting model namespace declarations.
    modelname='3D/Objects/object_2.model';m=ET.fromstring(blobs[modelname]);tm=ET.fromstring(test[modelname])
    obj=m.find(f'{{{NS}}}resources/{{{NS}}}object[@id="{carrier.get("id")}"]')
    tobj=tm.find(f'{{{NS}}}resources/{{{NS}}}object');av,ai,at=data(obj);bv,bi,bt=data(tobj)
    np.testing.assert_allclose(av-av.mean(0),bv-bv.mean(0),atol=.0001);assert np.array_equal(ai,bi)
    pattern=rb'<object\b(?=[^>]*\bid="'+carrier.get('id').encode()+rb'")[^>]*>.*?</object>'
    match=re.search(pattern,blobs[modelname],re.S);assert match
    index=iter(bt)
    def paint(hit):
        tri=next(index);raw=re.sub(rb'\s+paint_seam="[^"]*"',b'',hit.group(0))
        return raw[:-2]+(' paint_seam="'+tri.get('paint_seam')+'"/>').encode() if tri.get('paint_seam') else raw
    piece=re.sub(rb'<triangle\b[^>]*/>',paint,match.group(0))
    blobs[modelname]=blobs[modelname][:match.start()]+piece+blobs[modelname][match.end():]
    verify=ET.fromstring(blobs[modelname])
    for a,b in zip(m.findall(f'{{{NS}}}resources/{{{NS}}}object'),verify.findall(f'{{{NS}}}resources/{{{NS}}}object')):
        va,ia,_=data(a);vb,ib,_=data(b);assert np.array_equal(va,vb) and np.array_equal(ia,ib)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,b in blobs.items():z.writestr(name,b)
    native=annotate(TARGET,TARGET,[v.ORANGE,v.GOLD,v.WHITE,v.CYAN],PREFIX)
    actual,_,plates=read_project(TARGET);assert len(plates)==2
    for name,b in original.items():
        if name.startswith('3D/') and name!=modelname:assert actual[name]==b
    common=['--datadir',str(w/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),'--export-3mf','validation.3mf',str(TARGET)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text());assert result['return_code']==0
    reports=[]
    with ZipFile(w/'slice/validation.3mf') as z:
        for i,p in enumerate(result['sliced_plates']):
            assert not p.get('warning_message'),p.get('warning_message')
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode();rows=paths(code)
            assert '; FEATURE: Support' not in code and '; FEATURE: Brim' not in code
            if i==1:
                layers={h:sorted({r['tool'] for r in rows if r['layer']==h}) for h in sorted({r['layer'] for r in rows})}
                assert len(layers)==8 and all(t==[1] for h,t in layers.items() if h<=.6)
                assert all(t==[2,3,4] for h,t in layers.items() if h>.6)
                orange=[r for r in rows if r['tool']==1]
                assert not any(r['feature']=='Inner wall' for r in orange)
                wall_checks=[]
                for h in (.2,.4,.6):
                    wall=[r for r in orange if r['layer']==h and r['feature']=='Outer wall']
                    assert len(wall)==17 and all(a['b']==b['a'] for a,b in zip(wall,wall[1:]))
                    wall_checks.append({'z':h,'outer_segments':len(wall),'inner_segments':0,'seam_start':wall[0]['a']})
                assert all(r['speed_mm_s']==25 for r in orange if r['feature']=='Top surface')
                relief_features={t:sorted({r['feature'] for r in rows if r['tool']==t}) for t in (2,3,4)}
                assert all('Outer wall' in f and 'Inner wall' in f for f in relief_features.values()),relief_features
                sequence=dict(material_slots_by_layer=layers,orange_wall_checks=wall_checks,relief_features=relief_features)
            reports.append(dict(plate=i+1,estimated_seconds=p['total_predication'],estimated_grams=sum(f['total_used_g'] for f in p['filaments']),filament_changes=p['filament_change_times'],warnings=p.get('warning_message'),filaments=p['filaments']))
    report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        source_project=SOURCE.name,test_source=TEST.name,bambu_version='02.09.01.70',
        native_slice_exit=0,all_vertices_and_triangles_preserved=True,body_geometry_unchanged=True,
        calibrated_flow_ratios=cfg['filament_flow_ratio'],carrier_wall_loops=1,relief_requested_wall_loops=3,
        orange_seam_paint_transferred=True,plaque_overlap_percent=10,plate_mm=[46.4,66.4,.6],
        side_clearance_mm=.3,brim=False,supports=False,sequence=sequence,plates=reports,
        physical_print_tested=False,physical_fit_tested=False,
        future_glued_parts_requirement='Natal 2026 must be one part, or at most two; not implemented in this unified-plaque project.')
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-v8'))
    main(p.parse_args())
