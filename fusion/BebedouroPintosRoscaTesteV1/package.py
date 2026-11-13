"""Validate and package the provisional PET bottle-thread fit coupons."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
import trimesh

D=Path(__file__).resolve().parent
ROOT=D.parents[1]
TARGET=ROOT/'downloads/bebedouro-pintos-rosca-ensaio-v1.zip'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    report=json.loads((D/'validation.json').read_text())
    project=D/report['project']
    assert sha(project)==report['sha256']
    assert report['no_slicer_warnings'] and not report['brim'] and not report['supports']
    with ZipFile(project) as z:assert z.testzip() is None
    meshes=[]
    for label in 'ABCD':
        p=D/'stl'/f'anel-{label}.stl'
        m=trimesh.load(p,force='mesh')
        assert m.is_watertight and len(m.split())==1
        assert abs(m.extents[0]-42)<.02 and abs(m.extents[2]-12)<.02
        meshes.append({'ring':label,'file':p.relative_to(D).as_posix(),
            'sha256':sha(p),'volume_mm3':m.volume,'watertight':True})
    (D/'geometry.json').write_text(json.dumps({'physical_fit_tested':False,'parts':meshes},indent=2)+'\n')
    files=sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    assert all(p.stat().st_size>0 for p in files)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
        for p in files:z.write(p,'ensaio-rosca-garrafa-v1/'+p.relative_to(D).as_posix())
        z.writestr('COMECA-AQUI.txt',
            'OBSOLETO - NAO IMPRIMIR. Medidas corrigidas: rosca exterior 29.25 mm, base a 7.20 mm.\n'
            'Usar o ensaio de rosca V2 em fusion/BebedouroPintosRoscaTesteV2.\n'
            'Ensaio da rosca da garrafa do bebedouro V1 (historico).\n'
            'Ler ensaio-rosca-garrafa-v1/README.md.\n'
            'O antigo prato 1 B desta V1 usa medidas erradas. Nao imprimir.\n'
            'Nao forcar o anel na garrafa; parar se encravar.\n'
            'Sao hipoteses de rosca, sem teste fisico. Nao sao o copo final.\n')
    with ZipFile(TARGET) as z:assert z.testzip() is None
    print(TARGET,TARGET.stat().st_size,len(files))

if __name__=='__main__':main()
