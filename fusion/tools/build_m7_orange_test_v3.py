"""One-setting seam gap diagnostic, preserving the improved V2 corner paths."""
import argparse,hashlib,json,math
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from build_m7_orange_test_v2 import archive,slice_project,summarize

ROOT=Path(__file__).resolve().parents[2]
PREFIX='m7-tijolo-teste-laranja-v3-costura'
FOLDER=ROOT/'fusion/M7TijoloTesteLaranjaV3'
SOURCE=ROOT/'downloads/m7-tijolo-teste-laranja-v2-cantos-A1-PLA-1-prato.3mf'
TARGET=ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf'


def main(args):
    blobs=archive(SOURCE);cfg=json.loads(blobs['Metadata/project_settings.config'])
    assert cfg['seam_gap']=='15%' and cfg['filament_scarf_seam_type'][0]=='none'
    cfg['seam_gap']='20%'
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():
            if name=='Metadata/project_settings.config':data=json.dumps(cfg,indent=2).encode()
            z.writestr(name,data)
    after=archive(TARGET);old=json.loads(blobs['Metadata/project_settings.config'])
    assert [k for k in cfg if cfg[k]!=old[k]]==['seam_gap']
    assert all(after[k]==v for k,v in blobs.items() if k!='Metadata/project_settings.config')
    a,ar=slice_project(args.bambu_bin,SOURCE,args.work_dir/'reference')
    b,br=slice_project(args.bambu_bin,TARGET,args.work_dir/'candidate')
    assert [r for r in ar if r['feature']=='Top surface']==[r for r in br if r['feature']=='Top surface']
    def seam(rows):
        wall=[r for r in rows if r['layer']==.6 and r['feature']=='Outer wall']
        return dict(start=wall[0]['a'],end=wall[-1]['b'],
                    actual_xy_gap_mm=math.dist(wall[0]['a'],wall[-1]['b']))
    first,last=seam(ar),seam(br)
    assert first['start']==last['start']
    assert abs(first['actual_xy_gap_mm']-.06)<.003
    assert abs(last['actual_xy_gap_mm']-.08)<.003
    report=dict(project=TARGET.name,sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        source=SOURCE.name,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        bambu_version='02.09.01.70',native_slice_exit=0,
        only_setting_changed={'seam_gap':{'before':'15%','after':'20%'}},
        scarf_none_preserved=True,scarf_slope_gap_unchanged=True,
        geometry_and_seam_paint_preserved_byte_for_byte=True,top_paths_unchanged=True,
        reference_outer_seam=first,candidate_outer_seam=last,
        reference=summarize(a,ar),candidate=summarize(b,br),physical_print_tested=False,
        limitation='A larger gap may reduce the seam protrusion or create a small opening; physical result unverified.')
    FOLDER.mkdir(exist_ok=True)
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('reference_outer_seam','candidate_outer_seam','sha256')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bambu-bin',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-orange-test-v3'))
    main(p.parse_args())
