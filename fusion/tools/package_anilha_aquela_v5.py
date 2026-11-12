"""Package the matching V5 front/foliage, unchanged ring and validation reports."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/AnilhaAquelaV5';PREFIX='anilha-aquela-v5'


def main():
    data=json.loads((FOLDER/'geometry.json').read_text())
    json.loads((FOLDER/'toolpath-review.json').read_text())
    files=set()
    for kind in ['lobo','acessorios']:
        report=json.loads((FOLDER/f'bambu-validation-{kind}.json').read_text())
        p=ROOT/'downloads'/report['project']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==report['sha256']
        files.add(p)
    for p in data['parts']:
        file=ROOT/'downloads'/p['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==p['sha256']
        files.add(file)
    for name,digest in data['reused_unchanged_sha256'].items():
        assert hashlib.sha256((ROOT/'downloads'/name).read_bytes()).hexdigest()==digest
    files.update(ROOT/'downloads'/f'{PREFIX}-{s}' for s in ['lobo-completo-monocor.stl','folhas-completas-monocor.stl','montada.glb'])
    images=sorted((ROOT/'designs').glob(PREFIX+'-*.png'))
    scripts=sorted((ROOT/'fusion/tools').glob('*anilha_aquela_v5*.py'))
    package=ROOT/'downloads'/f'{PREFIX}-pacote.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as z:
        for p in sorted(files):z.write(p,p.name)
        for p in images:z.write(p,'imagens/'+p.name)
        for p in scripts:z.write(p,'scripts/'+p.name)
        for p in sorted(FOLDER.glob('*.json')):
            if p.name!='release-files.json':z.write(p,'verificacao/'+p.name)
        def link(m):
            t=m.group(1)
            return m.group(0) if t.startswith('http') else '](https://github.com/kruzpt/Build/blob/main/'+str((FOLDER/t).resolve().relative_to(ROOT))+')'
        z.writestr('README.md',re.sub(r'\]\(([^)]+)\)',link,(FOLDER/'README.md').read_text()))
        z.writestr('LEIA-ME.txt',
            'Aquelá V5 — conjunto 52 x 55 mm\n\n'
            'Abrir os 3MF como PROJETO no Bambu Studio.\n'
            'LOBO: 1 preto, 2 cinzento, 3 castanho, 4 branco.\n'
            'ACESSORIOS: 1 castanho, 2 verde, 3 preto.\n'
            'Prato 1 dos acessórios: anilha. Prato 2: folhas.\n'
            'Usar as folhas V5 com a frente V5. A anilha V2 mantém-se igual e pode ser reutilizada.\n'
            'Não imprimir os STL de cor separadamente; são partes de uma montagem multicolor.\n'
            'Nome sem contorno nem apoio preto; branco de 1,44 mm.\n'
            'Conjunto visível 52 x 55 mm; passagem do lenço 25 x 18 mm mantida.\n'
            'Colar lobo e folhas com centros e bases alinhados. Anilha centrada no verso, bordo inferior a 7,8 mm da base.\n'
            'A1, bico 0,4 mm, PLA, camada 0,12 mm; sem suportes nem brim.\n'
            'Verificado digitalmente, ainda sem teste físico.\n'
            'Os scripts requerem o checkout completo de github.com/kruzpt/Build e as suas dependências.\n')
    with ZipFile(package) as z:assert z.testzip() is None
    files.add(package)
    files.update(images);files.update(scripts)
    manifest={str(p.relative_to(ROOT)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(files)}
    (FOLDER/'release-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(package.name,package.stat().st_size)


if __name__=='__main__':main()
