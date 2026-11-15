"""Export the smooth board chair and unchanged base/tree as binary STL."""
from pathlib import Path
import os
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'memorial.scad'
TARGET = HERE / 'stl'
TARGET.mkdir(exist_ok=True)
PARTS = ['base', 'tree_cream', 'tree_brown', 'text_coupon_cream',
         'text_coupon_brown', 'joint_coupon', 'side_A', 'side_B',
         'back', 'seat', 'bar']
env = dict(os.environ, XDG_CACHE_HOME='/tmp/natal-font-cache')
Path(env['XDG_CACHE_HOME']).mkdir(exist_ok=True)
for part in PARTS:
    name = ('boards_' if part in ('side_A', 'side_B', 'back', 'seat', 'bar') else '') + part
    target = TARGET / f'{name}.stl'
    cmd = ['openscad', '-o', str(target), '--export-format', 'binstl',
           '-D', f'part="{part}"', '-D', 'style="boards"', str(SOURCE)]
    result = subprocess.run(cmd, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode or not target.exists() or target.stat().st_size < 100:
        raise RuntimeError(f'{target}: {result.stdout[-1500:]}')
    print(f'{target.name}: {target.stat().st_size} bytes', flush=True)
