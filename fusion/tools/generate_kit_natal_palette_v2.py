"""Create the 140 x 200 mm palette with four integrated, rounded paint wells.

The wells are designed for direct paint use, about 5 mL with headroom.
Commercial pot dimensions are not standardized or physically fit-tested.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from zipfile import ZipFile

import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

from generate_joana_topper import save_mesh
from generate_m7_prototypes_v1 import text, SCRIPT
from generate_universo_stand import render_meshes

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/KitNatalPaletaV2'
PREFIX = 'kit-natal-paleta-v2'
BROWN = '#986B43'
CENTERS = [(46., 161.), (94., 161.), (46., 119.), (94., 119.)]
BASE, DEPTH, RADIUS, WALL, FILLET = 3., 6., 18., 2.4, 2.


def ellipse(rx, ry, x, y):
    return md.CrossSection.circle(1., 256).scale((rx, ry)).translate((x, y))


def well_void():
    # A radial section, revolved about Z. The lower corner has a 2 mm fillet.
    points = [(0., 0.), (RADIUS-FILLET, 0.)]
    points += [(RADIUS-FILLET + FILLET*math.sin(a), FILLET*(1-math.cos(a)))
               for a in np.linspace(0, math.pi/2, 41)[1:]]
    points += [(RADIUS, DEPTH+.1), (0., DEPTH+.1)]
    return md.CrossSection([points]).revolve(160)


def dimensions(draw, bounds, label, font):
    (x0, y0), (x1, y1) = bounds
    draw.line((x0, y0, x1, y1), fill='#17385B', width=2)
    if abs(y1-y0) < 1:
        for x in [x0, x1]: draw.line((x, y0-8, x, y0+8), fill='#17385B', width=2)
        draw.text(((x0+x1)/2, y0+10), label, font=font, fill='#17385B', anchor='mt')
    else:
        for y in [y0, y1]: draw.line((x0-8, y, x0+8, y), fill='#17385B', width=2)
        draw.text((x0-12, (y0+y1)/2), label, font=font, fill='#17385B', anchor='rm')


def sheet(solid, outline, report):
    im = Image.new('RGB', (1700, 1200), '#F4F6F8')
    d = ImageDraw.Draw(im)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    bold = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', n)
    d.text((45, 25), 'Paleta de Natal · 4 reservatórios integrados', font=bold(34), fill='#17385B')
    d.text((45, 78), '14 × 20 cm · tinta diretamente nas cavidades · geometria do modelo 3D', font=font(24), fill='#30414F')
    im.paste(render_meshes([(solid, BROWN)], size=(800, 900),
                          direction=(.32, -.65, 1.2), margin=45), (20, 125))
    d = ImageDraw.Draw(im)
    scale, xorigin, yorigin = 2.65, 1020., 710.
    def pt(x, y): return (xorigin + x*scale, yorigin-y*scale)
    # Actual planar silhouette and exact well circles.
    for i, loop in enumerate(outline.to_polygons()):
        d.polygon([pt(x,y) for x,y in loop], fill=BROWN if i == 0 else '#F4F6F8')
    for x,y in CENTERS:
        px,py = pt(x,y)
        for radius, color in [(RADIUS+WALL, '#69472E'), (RADIUS, '#E0CBB7'), (RADIUS-FILLET, '#B68B67')]:
            r = radius*scale; d.ellipse((px-r,py-r,px+r,py+r), fill=color)
    dimensions(d, (pt(0,-10),pt(140,-10)), '140 mm', font(23))
    dimensions(d, (pt(-12,0),pt(-12,200)), '200 mm', font(23))
    d.text((1015, 120), 'Vista de cima', font=bold(25), fill='#17385B')
    d.text((875, 815), 'Secção de uma cavidade', font=bold(26), fill='#17385B')
    # Section at a well diameter, with no vertical scale exaggeration.
    u, x, y = 10., 1140., 1030.
    def sp(r,z): return (x+r*u, y-z*u)
    d.rectangle((sp(-RADIUS-WALL, BASE+DEPTH)[0],sp(0,BASE+DEPTH)[1],
                 sp(RADIUS+WALL,0)[0],sp(0,0)[1]), fill=BROWN)
    cavity = [sp(-RADIUS,BASE+DEPTH), sp(RADIUS,BASE+DEPTH), sp(RADIUS,BASE+FILLET)]
    cavity += [sp(RADIUS-FILLET+FILLET*math.sin(a),BASE+FILLET*(1-math.cos(a)))
               for a in np.linspace(math.pi/2,0,30)]
    cavity += [sp(-RADIUS+FILLET,BASE)]
    cavity += [sp(-RADIUS+FILLET-FILLET*math.sin(a),BASE+FILLET*(1-math.cos(a)))
               for a in np.linspace(0,math.pi/2,30)]
    d.polygon(cavity, fill='#F4F6F8')
    dimensions(d,(sp(-RADIUS,11.5),sp(RADIUS,11.5)), 'Ø 36 mm', font(22))
    d.text((1380, 930), '6 mm de profundidade', font=font(21), fill='#17385B')
    d.text((1380, 969), '3 mm de fundo', font=font(21), fill='#17385B')
    d.text((875, 1080), f"Capacidade: {report['well_capacity_to_rim_ml']:.2f} ml até ao bordo; cerca de 5 ml úteis.",font=font(23),fill='#17385B')
    d.text((45, 1150), 'Base de 3 mm · altura máxima de 9 mm nos rebordos · os seis enfeites mantêm as medidas anteriores.',font=font(23),fill='#30414F')
    im.save(ROOT/'designs'/f'{PREFIX}-CAD-dimensoes.png')


def make():
    FOLDER.mkdir(parents=True, exist_ok=True)
    outline = ellipse(70,100,70,100) - ellipse(14,22,107,65)
    outline -= md.CrossSection.circle(20,160).translate((95,4))
    assert len(outline.decompose()) == 1
    body = outline.extrude(BASE)
    void = well_void()
    envelope = md.Manifold.cube((80,80,DEPTH)).translate((-40,-40,0))
    capacity = (void ^ envelope).volume()/1000
    useful = (void ^ md.Manifold.cube((80,80,5.)).translate((-40,-40,0))).volume()/1000
    for x,y in CENTERS:
        footprint = md.CrossSection.circle(RADIUS+WALL,160).translate((x,y))
        assert (footprint-outline).area() < .0001
        outside = md.Manifold.cylinder(DEPTH, RADIUS+WALL, RADIUS+WALL,160).translate((x,y,BASE))
        body += outside
        body -= void.translate((x,y,BASE))
    wording = text('Feliz',46,font=SCRIPT,strengthen=.1).translate((45,54))
    wording += text('Natal',52,font=SCRIPT,strengthen=.1).translate((45,29))
    assert (wording-outline).area()<.001
    body -= wording.extrude(.45).translate((0,0,2.6))
    assert body.status()==md.Error.NoError
    assert len(body.decompose())==1
    stl = ROOT/'downloads'/f'{PREFIX}-4-cavidades.stl'
    mesh = save_mesh(body,stl)
    assert len(mesh.split())==1
    np.testing.assert_allclose(mesh.bounds,[[0,0,0],[140,200,9]],atol=.001)
    reloaded=trimesh.load(stl,force='mesh')
    assert reloaded.is_watertight and reloaded.is_winding_consistent
    # The floor is closed under all four wells. The thumb hole remains open.
    for x,y in CENTERS:
        floor=md.Manifold.cylinder(BASE,16,16,96).translate((x,y,0))
        assert (floor-body).volume()<.001
        probe=md.Manifold.cylinder(DEPTH-.02,15,15,96).translate((x,y,BASE+.01))
        assert (probe^body).volume()<.001
    report={'version':2,'outer_dimensions_mm':[140,200,9],'base_thickness_mm':BASE,
            'reservoir_count':4,'reservoir_centers_xy_mm':CENTERS,'well_mouth_diameter_mm':36,
            'well_depth_mm':DEPTH,'minimum_wall_mm':WALL,'bottom_fillet_radius_mm':FILLET,
            'well_capacity_to_rim_ml':capacity,'well_capacity_at_5mm_fill_ml':useful,
            'nominal_working_volume_ml':5,'well_bottom_flat_diameter_mm':32,
            'thumb_hole_dimensions_mm':[28,44],'source':'Original geometric design',
            'intended_use':'Integrated direct-paint wells; not a guaranteed universal commercial-pot socket',
            'commercial_pot_fit_tested':False,'physical_print_tested':False,'liquid_tightness_tested':False,
            'mesh_watertight':True,'components':1,'volume_mm3':float(mesh.volume),
            'estimated_fully_solid_pla_grams_at_1_24_g_cm3':float(mesh.volume*.00124),
            'file':stl.name,'sha256':hashlib.sha256(stl.read_bytes()).hexdigest()}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    sheet(body,outline,report)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


def build(args):
    from build_pintos_pla_3mf import flatten_profile,read_project,run_cli
    from build_m7_prototypes_v1_3mf import annotate
    w=args.work_dir;w.mkdir(parents=True,exist_ok=True)
    os.environ['LD_LIBRARY_PATH']='/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:'+str(args.bambu_bin.parent)
    machine=flatten_profile(args.profiles,'machine','Bambu Lab A1 0.4 nozzle')
    process=flatten_profile(args.profiles,'process','0.20mm Standard @BBL A1')
    process.update({'name':'Paleta Natal V2 A1 PLA 0.20','from':'User','layer_height':'0.2',
        'initial_layer_print_height':'0.2','wall_loops':'3','sparse_infill_density':'100%',
        'sparse_infill_pattern':'zig-zag','top_shell_layers':'5','bottom_shell_layers':'5',
        'wall_generator':'classic','wall_sequence':'outer wall/inner wall',
        'top_surface_pattern':'monotonicline','outer_wall_speed':['50'],'inner_wall_speed':['100'],
        'top_surface_speed':['25'],'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],
        'outer_wall_acceleration':['2000'],'top_surface_acceleration':['1000'],
        'enable_support':['0'],'enable_prime_tower':'0','brim_type':'outer_only','brim_width':'3',
        'brim_object_gap':'0.15','elefant_foot_compensation':'0.12','curr_bed_type':'Textured PEI Plate'})
    process.pop('wall_infill_order',None)
    filament=flatten_profile(args.profiles,'filament','Generic PLA @BBL A1')
    filament.update({'name':'PLA castanho paleta','from':'User','filament_colour':[BROWN],
                     'filament_max_volumetric_speed':['8'],'filament_cost':['16']})
    for name,config in [('machine',machine),('process',process),('filament',filament)]:
        (w/f'{name}.json').write_text(json.dumps(config))
    plan={'plates':[{'plate_name':'Paleta - quatro cavidades integradas','need_arrange':True,
                    'objects':[{'path':str(ROOT/'downloads'/f'{PREFIX}-4-cavidades.stl'),
                                'count':1,'filaments':[1]}]}]}
    (w/'assembly.json').write_text(json.dumps(plan))
    common=['--datadir',str(w/'bambu-user'),'--debug','2']
    run_cli(args.bambu_bin,common+['--load-settings',str(w/'machine.json')+';'+str(w/'process.json'),
        '--load-filaments',str(w/'filament.json'),'--load-assemble-list',str(w/'assembly.json'),
        '--orient','0','--arrange','1','--outputdir',str(w),'--export-3mf','native.3mf'],w/'export.log')
    target=ROOT/'downloads'/f'{PREFIX}-A1-PLA.3mf'
    annotate(w/'native.3mf',target,[BROWN],PREFIX)
    blobs,settings,plates=read_project(target)
    assert len(plates)==1 and len(plates[0]['items'])==1
    actual=plates[0]['items'][0]['mesh']
    source=trimesh.load(ROOT/'downloads'/f'{PREFIX}-4-cavidades.stl',force='mesh')
    assert abs(actual.volume-source.volume)<.1
    np.testing.assert_allclose(np.linalg.eigvalsh(actual.moment_inertia),
                               np.linalg.eigvalsh(source.moment_inertia),rtol=.0001)
    assert abs(actual.bounds[0,2])<.001
    assert actual.bounds[0,:2].min()>3 and actual.bounds[1,:2].max()<253
    run_cli(args.bambu_bin,common+['--info','--outputdir',str(w/'reopen'),str(target)],w/'reopen.log')
    run_cli(args.bambu_bin,common+['--slice','0','--orient','0','--arrange','0','--outputdir',str(w/'slice'),
        '--export-3mf','validation.3mf',str(target)],w/'slice.log')
    result=json.loads((w/'slice/result.json').read_text())
    assert result['return_code']==0 and len(result['sliced_plates'])==1
    p=result['sliced_plates'][0]
    assert not p.get('warning_message')
    assert p['filament_change_times']==0
    with ZipFile(w/'slice/validation.3mf') as z:
        code=z.read('Metadata/plate_1.gcode').decode()
    assert '; FEATURE: Support' not in code
    report={'project':target.name,'bambu_version':'02.08.02.61','printer':'Bambu Lab A1 0.4 nozzle',
            'layer_height_mm':.2,'infill_percent':100,'support_toolpaths':False,'filament_changes':0,
            'warnings':p.get('warning_message'),'native_export_exit':0,'native_reopen_exit':0,'native_slice_exit':0,
            'estimated_seconds':p['total_predication'],'estimated_grams':sum(f['total_used_g'] for f in p['filaments']),
            'material_cost_eur_at_16_per_kg':sum(f['total_used_g'] for f in p['filaments'])*.016,
            'physical_print_tested':False,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (FOLDER/'bambu-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--build-3mf',action='store_true')
    parser.add_argument('--work-dir',type=Path,default=Path('/tmp/kit-natal-palette-v2'))
    parser.add_argument('--bambu-bin',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/bin/bambu-studio'))
    parser.add_argument('--profiles',type=Path,default=Path('/tmp/bambu-studio-app/squashfs-root/resources/profiles/BBL'))
    args=parser.parse_args()
    make()
    if args.build_3mf:build(args)
