"""Export, reopen and slice the original-STL seven and its matching V4 brick."""
import argparse
import os
from pathlib import Path

from build_m7_prototypes_v1_3mf import build
from build_m7_brick_v2_3mf import package
from build_m7_brick_v3_3mf import compare_slicing
from generate_m7_brick_v4 import ROOT, FOLDER, PREFIX


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir', type=Path, default=Path('/tmp/m7-tijolo-v4-bambu'))
    parser.add_argument('--bambu-bin', type=Path, default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles', type=Path, default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    parser.add_argument('--package-only', action='store_true')
    args = parser.parse_args()
    paths = [Path('/tmp/bambu-libs/usr/lib/x86_64-linux-gnu'), args.bambu_bin.parent]
    folders = [str(p) for p in paths if p.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):
        folders.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH'] = ':'.join(folders)
    if not args.package_only:
        build('tijolo', args, version='v4', folder=FOLDER)
        compare_slicing(args.work_dir, folder=FOLDER, prefix=PREFIX, label='V4 — original do STL')
    images = [PREFIX+suffix for suffix in ('-CAD.png', '-comparacao.png', '-pratos.png', '-fatiador.png')]
    if (FOLDER / 'README.md').exists() and all((ROOT / 'designs' / name).exists() for name in images):
        package(folder=FOLDER, prefix=PREFIX, image_names=images)


if __name__ == '__main__':
    main()
