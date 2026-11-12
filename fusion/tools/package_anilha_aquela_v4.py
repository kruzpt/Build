"""Package V4 leaves with byte-identical approved V2 wolf and ring files."""
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/AnilhaAquelaV4'
PREFIX='anilha-aquela-v4'


def main():
    data=json.loads((FOLDER/'geometry.json').read_text())
    report=json.loads((FOLDER/'bambu-validation.json').read_text())
    target=ROOT/'downloads'/report['project']
    assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
    for name,sha in data['reused_unchanged_sha256'].items():
        assert hashlib.sha256((ROOT/'downloads'/name).read_bytes()).hexdigest()==sha
    files={target,ROOT/'downloads'/data['wolf_project']}
    files.update(ROOT/'downloads'/p['file'] for p in data['parts'])
    files.update(ROOT/'downloads'/f'{PREFIX}-{suffix}' for suffix in ['folhas-completas-monocor.stl','montada.glb'])
    images=list((ROOT/'designs').glob(PREFIX+'-*.png'))
    package=ROOT/'downloads'/f'{PREFIX}-pacote.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as archive:
        for path in sorted(files):archive.write(path,path.name)
        for path in images:archive.write(path,'imagens/'+path.name)
        for path in sorted(FOLDER.glob('*.json')):
            if path.name!='release-files.json':archive.write(path,'verificacao/'+path.name)
        def absolute_link(match):
            link=match.group(1)
            if link.startswith('http'):return match.group(0)
            local=(FOLDER/link).resolve().relative_to(ROOT)
            return '](https://github.com/kruzpt/Build/blob/main/'+str(local)+')'
        archive.writestr('README.md',re.sub(r'\]\(([^)]+)\)',absolute_link,(FOLDER/'README.md').read_text()))
        archive.writestr('LEIA-ME.txt',
            'Aquelá V4 — zona oculta das folhas só verde\n\n'
            'Abrir anilha-aquela-v4-ACESSORIOS-A1-04-AMS-2-pratos.3mf como PROJETO.\n'
            'Se já tens o lobo e a anilha, imprimir apenas o prato 02: folhas V4.\n'
            'Prato 01: anilha castanha, sem alterações.\n'
            'Filamentos: 1 castanho, 2 verde, 3 preto.\n'
            'As folhas são uma peça; não imprimir nem colar as nervuras à parte.\n'
            'O projeto do lobo incluído é o V2 aprovado, sem qualquer alteração.\n'
            'Colar com os centros e as bases do lobo e das folhas alinhados.\n'
            'A1, bico 0,4 mm, Generic PLA, camada 0,12 mm, sem suportes nem brim.\n'
            'Validação digital concluída; impressão e colagem físicas por testar.\n')
    with ZipFile(package) as archive:assert archive.testzip() is None
    files.add(package)
    manifest={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(files)}
    (FOLDER/'release-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(package.name,package.stat().st_size)


if __name__=='__main__':main()
