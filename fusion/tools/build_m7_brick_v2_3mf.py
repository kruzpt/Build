"""Native Bambu A1 export/reopen/slicing and package for the revised brick only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

from build_m7_prototypes_v1_3mf import build
from generate_m7_brick_v2 import ROOT,FOLDER,PREFIX


def package():
    report=json.loads((FOLDER/'bambu-validation-tijolo.json').read_text())
    project=ROOT/'downloads'/report['project']
    assert hashlib.sha256(project.read_bytes()).hexdigest()==report['sha256']
    assert all(not p['warnings'] and not p['support_toolpaths'] for p in report['plates'])
    entries={project.name:project,'LEIA-ME.md':FOLDER/'README.md'}
    for p in sorted((ROOT/'downloads').glob(PREFIX+'-*.stl')):entries[p.name]=p
    assert sum(n.endswith('.stl') for n in entries)==6
    for p in sorted(FOLDER.iterdir()):
        if p.is_file():entries['M7TijoloV2/'+p.name]=p
    for name in [PREFIX+'-CAD.png',PREFIX+'-logo.png',PREFIX+'-pratos.png',PREFIX+'-7-percurso.png']:
        entries['imagens/'+name]=ROOT/'designs'/name
    manifest={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in entries.items()}
    target=ROOT/'downloads'/f'{PREFIX}-pacote.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for n,p in entries.items():z.write(p,n)
        z.writestr('manifesto-sha256.json',json.dumps(manifest,indent=2)+'\n')
    with ZipFile(target) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==digest for n,digest in manifest.items())
    print('Verified package',target.name)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--work-dir',type=Path,default=Path('/tmp/m7-tijolo-v2-bambu'))
    p.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    p.add_argument('--package-only',action='store_true');a=p.parse_args()
    extra=[Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu'),a.bambu_bin.parent]
    folders=[str(v) for v in extra if v.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):folders.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH']=':'.join(folders)
    if not a.package_only:build('tijolo',a,version='v2',folder=FOLDER)
    if (FOLDER/'README.md').exists():package()


if __name__=='__main__':main()
