"""Generate a genuinely hollow nest egg and validate its native A1 project."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED

import manifold3d as md
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT/'fusion/OvoFalsoMV1'
PREFIX = 'ovo-falso-M-v1'
WHITE = '#F4F0E6'


def mesh_of(solid):
    data = solid.to_mesh()
    return trimesh.Trimesh(np.asarray(data.vert_properties)[:, :3], np.asarray(data.tri_verts), process=True)


def geometry():
    FOLDER.mkdir(parents=True, exist_ok=True)
    # Smooth asymmetric oval; the broad end is down. M is a commercial mass
    # category, so these dimensions are an approximate typical chicken egg.
    theta = np.linspace(0, 2*np.pi, 401)
    radial = np.sin(theta)*(1+.15*np.cos(theta))
    radial *= 21.5/max(abs(radial))
    height = 57.35/2*(1-np.cos(theta))-.35
    profile = md.CrossSection([np.column_stack([radial, height]).tolist()], md.FillRule.EvenOdd)
    profile ^= md.CrossSection.square([100, 57]).translate([-50, 0])
    cavity_profile = profile.offset(-2, circular_segments=128)
    outer = profile.revolve(192)
    cavity = cavity_profile.revolve(192)
    shell = outer-cavity
    mesh = mesh_of(shell)
    assert mesh.is_watertight and mesh.is_winding_consistent
    assert np.allclose(mesh.extents, [43, 43, 57], atol=.01)
    assert abs(mesh.volume-(outer.volume()-cavity.volume())) < .05
    boundaries = mesh.split(only_watertight=True)
    # The two closed surfaces are a positive exterior and a negative cavity.
    assert len(boundaries) == 2
    assert sorted(np.sign(m.volume) for m in boundaries) == [-1, 1]
    assert (shell ^ md.Manifold.sphere(.1).translate([0, 0, 28])).is_empty()
    target = ROOT/'downloads'/f'{PREFIX}-oco.stl'
    mesh.export(target)
    reread = trimesh.load(target, force='mesh')
    assert reread.is_watertight and reread.is_winding_consistent
    assert len(reread.split()) == 2 and abs(reread.volume-mesh.volume) < .01
    contours = profile.to_polygons()
    inside = cavity_profile.to_polygons()
    floor_radius = max(abs(p[0]) for p in contours[0] if abs(p[1]) < .001)
    report = {'dimensions_mm': [43, 43, 57], 'nominal_wall_mm': 2,
              'single_closed_piece': True, 'genuinely_hollow_mesh': True,
              'hollow_cavity_cm3': cavity.volume()/1000,
              'outer_enclosed_cm3': outer.volume()/1000,
              'shell_cm3': mesh.volume/1000,
              'small_flat_base_diameter_mm': floor_radius*2,
              'watertight': True, 'physical_print_tested': False,
              'mesh_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    # Actual meridian sections, not an illustrative AI rendering.
    image = Image.new('RGB', (1150, 850), '#eef1f3')
    draw = ImageDraw.Draw(image)
    def font(n):
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    draw.text((45, 30), 'Ovo falso M · peça única e oca', font=font(32), fill='#17374e')
    scale = 9
    def points(contour, x):
        return [(x+float(r)*scale, 655-float(z)*scale) for r, z in contour]
    for c in contours:
        draw.polygon(points(c, 300), fill=WHITE, outline='#73726b', width=3)
        draw.polygon(points(c, 800), fill=WHITE, outline='#73726b', width=3)
    for c in inside:
        draw.polygon(points(c, 800), fill='#cbd9e0', outline='#73726b', width=2)
    draw.text((230, 695), 'Exterior', font=font(24), fill='#17374e')
    draw.text((690, 695), 'Corte: parede 2 mm', font=font(24), fill='#17374e')
    draw.line((65, 142, 65, 655), fill='#17374e', width=2)
    for y in (142, 655):
        draw.line((55, y, 80, y), fill='#17374e', width=2)
    draw.text((15, 100), '57 mm', font=font(23), fill='#17374e')
    draw.line((107, 675, 493, 675), fill='#17374e', width=2)
    for x in (107, 493):
        draw.line((x, 665, x, 685), fill='#17374e', width=2)
    draw.text((260, 635), '43 mm', font=font(21), fill='#17374e')
    draw.text((45, 760), 'Tamanho aproximado de ovo M de galinha · não tem o peso de um ovo real', font=font(22), fill='#17374e')
    draw.text((45, 795), 'PLA branco · suportes exteriores apenas na base · geometria real', font=font(21), fill='#17374e')
    image.save(ROOT/'designs'/f'{PREFIX}-dimensoes.png')
    return target, mesh, report


def package(target):
    entries = [target, ROOT/'downloads'/f'{PREFIX}-oco.stl', Path(__file__)]
    entries += list(FOLDER.glob('*.json'))+[FOLDER/'README.md']
    entries += list((ROOT/'designs').glob(f'{PREFIX}-*.png'))
    with ZipFile(ROOT/'downloads'/f'{PREFIX}-pacote.zip', 'w', ZIP_DEFLATED) as z:
        for entry in entries:
            z.write(entry, entry.name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bambu-bin', type=Path, default=Path('/workspace/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    p.add_argument('--profiles', type=Path, default=Path('/workspace/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    p.add_argument('--work-dir', type=Path, default=Path('/tmp/ovo-falso-m-v1'))
    p.add_argument('--package-only', action='store_true')
    a = p.parse_args()
    target = ROOT/'downloads'/f'{PREFIX}-A1-PLA-1-prato.3mf'
    if a.package_only:
        package(target)
        return
    source, ref, geom = geometry()
    w = a.work_dir
    w.mkdir(parents=True, exist_ok=True)
    os.environ['LD_LIBRARY_PATH'] = '/workspace/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(a.bambu_bin.parent)
    machine = flatten_profile(a.profiles, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = flatten_profile(a.profiles, 'process', '0.16mm Optimal @BBL A1')
    process.update({'name': 'Ovo falso M oco - A1 PLA 0.16', 'from': 'User',
        'layer_height': '0.16', 'initial_layer_print_height': '0.2',
        'wall_loops': '3', 'wall_generator': 'arachne',
        'sparse_infill_density': '0%', 'top_shell_layers': '6', 'bottom_shell_layers': '6',
        'top_shell_thickness': '0.96', 'bottom_shell_thickness': '0.96',
        'outer_wall_speed': ['35'], 'inner_wall_speed': ['70'],
        'top_surface_speed': ['25'], 'small_perimeter_speed': ['25'],
        'bridge_speed': ['20'], 'outer_wall_acceleration': ['1500'],
        'initial_layer_speed': ['20'], 'initial_layer_infill_speed': ['30'],
        'enable_support': ['1'], 'support_type': 'normal(auto)', 'support_style': 'snug',
        'support_on_build_plate_only': '1', 'support_threshold_angle': '30',
        'support_top_z_distance': '0.2', 'support_object_xy_distance': '0.35',
        'support_interface_top_layers': '2',
        'brim_type': 'outer_only', 'brim_width': '4', 'brim_object_gap': '0.15',
        'elefant_foot_compensation': '0.1', 'resolution': '0.008',
        'enable_prime_tower': '0', 'curr_bed_type': 'Textured PEI Plate'})
    filament = flatten_profile(a.profiles, 'filament', 'Generic PLA @BBL A1')
    filament.update({'name': 'Ovo M PLA branco', 'from': 'User',
        'filament_colour': [WHITE], 'filament_max_volumetric_speed': ['6']})
    for name, data in [('machine', machine), ('process', process), ('filament', filament)]:
        (w/f'{name}.json').write_text(json.dumps(data))
    plan = {'plates': [{'plate_name': '01 Ovo falso M oco - PLA branco', 'need_arrange': True,
        'objects': [{'path': str(source), 'count': 1, 'filaments': [1]}]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common = ['--datadir', str(w/'user'), '--debug', '2']
    run_cli(a.bambu_bin, common+['--load-settings', str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments', str(w/'filament.json'), '--load-assemble-list', str(w/'assembly.json'),
        '--orient', '0', '--arrange', '1', '--outputdir', str(w), '--export-3mf', 'native.3mf'], w/'export.log')
    annotate(w/'native.3mf', target, [WHITE], PREFIX)
    blobs, settings, plates = read_project(target)
    native = plate_meshes(blobs, settings)
    assert len(plates) == 1 and len(native[0]) == 1
    actual = native[0][0][2]
    assert actual.is_watertight and abs(actual.volume-ref.volume) < .1
    assert len(actual.split()) == 2
    assert np.allclose(actual.extents, [43, 43, 57], atol=.02)
    run_cli(a.bambu_bin, common+['--info', '--outputdir', str(w/'reopen'), str(target)], w/'reopen.log')
    run_cli(a.bambu_bin, common+['--slice', '0', '--orient', '0', '--arrange', '0',
        '--outputdir', str(w/'slice'), '--export-3mf', 'validation.3mf', str(target)], w/'slice.log')
    result = json.loads((w/'slice/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    plate = result['sliced_plates'][0]
    assert not plate.get('warning_message') and plate['filament_change_times'] == 0
    with ZipFile(w/'slice/validation.3mf') as z:
        code = z.read('Metadata/plate_1.gcode').decode()
    # The sealed cavity must not receive unreachable supports. Every generated
    # support feature must be confined to the bottom exterior of the egg.
    z_height = 0
    support_heights = []
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):
            z_height = float(line.split(':')[1])
        if line.startswith('; FEATURE: Support'):
            support_heights.append(z_height)
    assert support_heights and max(support_heights) < 10
    assert '; FEATURE: Sparse infill' not in code
    mass = sum(f['total_used_g'] for f in plate['filaments'])
    report = {'project': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'printer': 'Bambu Lab A1 0.4 nozzle', 'bambu_version': '02.08.02.61',
        'native_export_exit': 0, 'native_reopen_exit': 0, 'native_slice_exit': 0,
        'physical_print_tested': False, 'warnings': plate.get('warning_message'),
        'filament_changes': 0, 'support_max_height_mm': max(support_heights),
        'support_only_near_base': True, 'sparse_infill_generated': False,
        'estimated_seconds': plate['total_predication'], 'estimated_total_grams': mass,
        'estimated_main_part_grams': sum(f['main_used_g'] for f in plate['filaments']),
        'estimated_material_eur_at_13_per_kg': round(mass*.013, 3),
        'dimensions_mm': geom['dimensions_mm'], 'nominal_wall_mm': 2}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)
    if (FOLDER/'README.md').exists():
        package(target)


if __name__ == '__main__':
    main()
