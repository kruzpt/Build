"""Apply body-only wall-quality settings to the preserved M7 V4 project."""
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from build_pintos_pla_3mf import run_cli

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/M7TijoloV4Acabamento'
SOURCE = ROOT / 'downloads/m7-tijolo-v4-A1-AMS-4-pratos.3mf'
TARGET = ROOT / 'downloads/m7-tijolo-v4-acabamento-A1-AMS-4-pratos.3mf'
CHANGES = {'wall_generator':'classic', 'wall_sequence':'outer wall/inner wall',
           'outer_wall_speed':'50', 'inner_wall_speed':'100',
           'outer_wall_acceleration':'2000'}


def main():
    FOLDER.mkdir(exist_ok=True)
    with ZipFile(SOURCE) as z:
        blobs = {name:z.read(name) for name in z.namelist()}
    original = dict(blobs)
    config = ET.fromstring(blobs['Metadata/model_settings.config'])
    objects = [obj for obj in config.findall('object')
               if any(m.get('key')=='name' and 'tijolo-terracota' in m.get('value','')
                      for m in obj.findall('metadata'))]
    assert len(objects)==1
    obj = objects[0]
    for key,value in CHANGES.items():
        node = obj.find(f"metadata[@key='{key}']")
        if node is None: node = ET.SubElement(obj,'metadata',key=key)
        node.set('value',value)
    name = config.find("plate/metadata[@key='plater_name']")
    name.set('value','01 Tijolo - ensaio acabamento Classic exterior primeiro')
    blobs['Metadata/model_settings.config'] = ET.tostring(config,encoding='utf-8',xml_declaration=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items(): z.writestr(name,data)
    assert all(original[k]==v for k,v in blobs.items() if k!='Metadata/model_settings.config')
    binary = Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio')
    work = Path('/tmp/m7-v4-acabamento'); work.mkdir(exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(binary.parent)
    common=['--datadir',str(work/'user'),'--debug','2']
    run_cli(binary, common+['--info','--outputdir',str(work/'reopen'),str(TARGET)],work/'reopen.log')
    run_cli(binary, common+['--slice','1','--orient','0','--arrange','0',
            '--outputdir',str(work/'slice'),'--export-3mf','validation.3mf',str(TARGET)],work/'slice.log')
    result=json.loads((work/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==1
    plate=result['sliced_plates'][0]
    assert not plate.get('warning_message') and plate['filament_change_times']==0
    with ZipFile(work/'slice/validation.3mf') as z:
        code=z.read('Metadata/plate_1.gcode').decode()
        native=ET.fromstring(z.read('Metadata/model_settings.config'))
    assert '; FEATURE: Support' not in code
    actual=next(o for o in native.findall('object') if o.get('id')==obj.get('id'))
    values={m.get('key'):m.get('value') for m in actual.findall('metadata')}
    assert all(values.get(k)==v for k,v in CHANGES.items()),values
    report={'source':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'project':TARGET.name,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
            'changed_body_settings':CHANGES,'all_geometry_and_global_filament_settings_unchanged':True,
            'decoration_object_settings_unchanged':True,'native_reopen_exit':0,'native_slice_exit':0,
            'validated_plate':1,'layer_height_mm':.2,'supports':False,'filament_changes':0,
            'warnings':plate.get('warning_message'), 'estimated_seconds':plate['total_predication'],
            'estimated_grams':sum(f['total_used_g'] for f in plate['filaments']),
            'physical_print_tested':False,'rib_marks_eliminated_confirmed':False}
    (FOLDER/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    with ZipFile(ROOT/'downloads/m7-tijolo-v4-acabamento-pacote.zip','w',ZIP_DEFLATED) as z:
        z.write(TARGET,TARGET.name)
        for p in FOLDER.iterdir(): z.write(p,p.name)
        z.write(Path(__file__),'configure_m7_brick_wall_quality.py')


if __name__=='__main__': main()
