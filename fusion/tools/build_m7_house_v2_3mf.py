"""Build the full house and a three-plate project with only replacement parts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile,ZIP_DEFLATED

from build_m7_prototypes_v1_3mf import build,annotate
from build_pintos_pla_3mf import read_project,run_cli
from generate_m7_house_v2 import ROOT,FOLDER,PREFIX
import generate_m7_prototypes_v1 as v


def replacement(args):
    source=ROOT/'downloads'/f'{PREFIX}-A1-AMS-3-pratos.3mf'
    target=ROOT/'downloads'/f'{PREFIX}-substituicao-A1-AMS-3-pratos.3mf'
    blobs,config,_=read_project(source)
    remove=[]
    for obj in config.findall('object'):
        files=[m.get('value','') for m in obj.findall("part/metadata[@key='source_file']")]
        if any('fachada-branca' in p or 'fundo-azul' in p for p in files):
            remove.append(obj.get('id'));config.remove(obj)
    assert len(remove)==2
    for plate in config.findall('plate'):
        for instance in plate.findall('model_instance'):
            key=instance.find("metadata[@key='object_id']").get('value')
            if key in remove:plate.remove(instance)
        assert len(plate.findall('model_instance'))==1
    names=['01 Substituir - m branco original','02 Substituir - base azul com rebaixos','03 Substituir - 7 ciano original']
    for plate,name in zip(config.findall('plate'),names):
        plate.find("metadata[@key='plater_name']").set('value',name)
    model=blobs['3D/3dmodel.model']
    for key in remove:
        pattern=rb'<item\b(?=[^>]*\bobjectid="'+key.encode()+rb'")[^>]*/>'
        model,count=re.subn(pattern,b'',model)
        assert count==1
    blobs['3D/3dmodel.model']=model
    blobs['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    native=annotate(target,target,[v.WHITE,v.BLUE,v.CYAN],PREFIX+'-substituicao')
    assert [len(p) for p in native]==[1,1,1]
    _,_,plates=read_project(target)
    assert len(plates)==3
    w=args.work_dir/'substituicao';w.mkdir(exist_ok=True)
    common=['--datadir',str(w/'user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
        '--export-3mf','validation.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==3
    report={'project':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'native_reopen_exit':0,'native_slice_exit':0,'physical_fit_tested':False,'plates':[]}
    with ZipFile(w/'slice/validation.3mf') as z:
        for i,plate in enumerate(result['sliced_plates']):
            code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
            assert '; FEATURE: Support' not in code
            assert not plate.get('warning_message') and plate['filament_change_times']==0
            report['plates'].append({'name':names[i],'warnings':plate.get('warning_message'),
                'support_toolpaths':False,'filament_changes':0,'estimated_seconds':plate['total_predication'],
                'estimated_grams':sum(f['total_used_g'] for f in plate['filaments'])})
    report['total_estimated_seconds']=sum(p['estimated_seconds'] for p in report['plates'])
    report['total_estimated_grams']=sum(p['estimated_grams'] for p in report['plates'])
    (FOLDER/'bambu-validation-substituicao.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


def package():
    entries=list(FOLDER.iterdir())+list((ROOT/'downloads').glob(f'{PREFIX}-*.stl'))
    entries+=list((ROOT/'downloads').glob(f'{PREFIX}-*.3mf'))
    entries+=list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    entries+=[Path(__file__),ROOT/'fusion/tools/generate_m7_house_v2.py']
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip','w',ZIP_DEFLATED) as z:
        for p in entries:
            name=('M7CasaV2/'+p.name if p.parent==FOLDER else 'scripts/'+p.name if p.parent.name=='tools' else p.name)
            z.write(p,name)
        z.write(FOLDER/'README.md','LEIA-ME.md')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-casa-v2'))
    p.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    p.add_argument('--package-only',action='store_true');args=p.parse_args()
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    if not args.package_only:
        build('casa',args,version='v2',folder=FOLDER)
        replacement(args)
    if (FOLDER/'README.md').exists():package()


if __name__=='__main__':main()
