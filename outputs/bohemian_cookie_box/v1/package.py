"""Verify the delivery inventory and create a portable OpenSCAD/print ZIP."""
from pathlib import Path
import hashlib,json,re
from zipfile import ZipFile,ZIP_DEFLATED
D=Path(__file__).resolve().parent
ROOT=D.parents[2]

def main():
    geom=json.loads((D/'validation/geometry.json').read_text())
    for part in geom['parts']:
        file=D/part['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==part['sha256']
    for p in (D/'validation').glob('bambu-*.json'):
        v=json.loads(p.read_text());file=D/v['project']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==v['sha256']
        assert all(not plate['warnings'] for plate in v['plates'])
        with ZipFile(file) as z:assert z.testzip() is None
    step=json.loads((D/'validation/step.json').read_text())
    assert step['export_and_reopen_verified'] and all(p['valid'] for p in step['files'])
    files=sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='release-files.json')
    # No stale/empty files, G-code, credential exports or temporary caches.
    assert all(p.stat().st_size>0 for p in files)
    allowed={'.py','.json','.md','.scad','.stl','.step','.png','.3mf','.ttf','.txt'}
    assert all(p.suffix in allowed for p in files)
    package=D.parent/'caixa-maria-bohemian-v1-pacote.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as z:
        for file in files:z.write(file,'caixa-maria-v1/'+str(file.relative_to(D)))
        z.writestr('COMECA-AQUI.txt',
          'Caixa Maria / Bohemian Rhapsody V1\n\n'
          'Ver caixa-maria-v1/README.md. Dimensoes provisorias: interior 70 x 42 mm.\n'
          'Primeiro: caixa-maria-v1-testes-A1-04-PEI-liso.3mf.\n'
          'Principal: caixa-maria-v1-vinil-3cores-A1-04-PEI-liso.3mf.\n'
          'A tampa imprime com a decoracao para baixo, sem relevo, no PEI liso.\n'
          'AMS: 1 preto, 2 roxo, 3 dourado. A alternativa aneis-tonais usa ainda 4 cinzento escuro.\n'
          'O corpo branco e opcional e tem um projeto de uma cor separado.\n'
          'Usar saco/liner fechado e certificado para contacto alimentar. Nunca bolachas diretamente no PLA.\n'
          'Fonte autonoma: cookie_box.scad + parameters.scad; fonte tipografica em fonts/.\n'
          'Scripts Python de validacao/regeneracao requerem o checkout completo de github.com/kruzpt/Build.\n'
          'Sem teste fisico; nenhuma impressao foi iniciada.\n')
    with ZipFile(package) as z:assert z.testzip() is None
    manifest={str(p.relative_to(D)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
    manifest['../'+package.name]={'bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest()}
    (D/'validation/release-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(package,package.stat().st_size,len(files))


if __name__=='__main__':main()
