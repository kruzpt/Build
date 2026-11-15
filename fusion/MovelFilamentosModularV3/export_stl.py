"""Create only the neutral intermediate meshes required for the 3MF builder."""
from pathlib import Path
import subprocess

here=Path(__file__).resolve().parent
source=here/'conector.scad'
target=here/'stl'
target.mkdir(exist_ok=True)
for part in ('connector','foot'):
    path=target/f'{part}.stl'
    result=subprocess.run(['openscad','-o',str(path),'--export-format','binstl',
                           '-D',f'part="{part}"',str(source)],text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if result.returncode or not path.exists() or path.stat().st_size<100:
        raise RuntimeError(result.stdout[-1500:])
    print(path.name,path.stat().st_size,flush=True)
