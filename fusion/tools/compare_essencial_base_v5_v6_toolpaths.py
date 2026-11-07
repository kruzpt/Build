"""Render a faithful side-by-side comparison of saved native Bambu G-code.

Plots extrusion centre lines from the same corner/scale. Colors encode speed;
this is an engineering plot, not an image predicting the printed finish.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_pintos_pla_3mf import read_project
from build_m7_prototypes_v1_3mf import plate_meshes
from check_anilha_lobito_v5_toolpaths import paths

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'essencial-compacto-v5-v6-comparacao-percursos'
PROJECTS = [
    ROOT/'downloads/essencial-compacto-v5-azeitona-A1-AMS-4-pratos.3mf',
    ROOT/'downloads/essencial-compacto-v6-base-acabamento-A1-AMS-2-pratos.3mf',
]
COLORS = ['#276c9f', '#168e7d', '#d48a24', '#c44842']


def color(speed):
    return COLORS[0 if speed<=20.001 else 1 if speed<=25.001 else 2 if speed<=35.001 else 3]


def clip(a, b, box):
    """Liang–Barsky clipping in XY; keep segments crossing the view boundary."""
    a, b = np.array(a[:2]), np.array(b[:2])
    delta = b-a
    low, high = 0., 1.
    for p, q in zip((-delta[0], delta[0], -delta[1], delta[1]),
                    (a[0]-box[0], box[2]-a[0], a[1]-box[1], box[3]-a[1])):
        if abs(p)<1e-12:
            if q<0:
                return None
        else:
            t = q/p
            if p<0:
                low = max(low, t)
            else:
                high = min(high, t)
            if low>high:
                return None
    return a+delta*low, a+delta*high


def main(a):
    versions = []
    gold_bounds = []
    for project, validation, plate, title in zip(PROJECTS, (a.before_validation, a.after_validation), (3,1), ('V5 — anterior', 'V6 — revisão da base')):
        blobs, settings, _ = read_project(project)
        material = json.loads(blobs['Metadata/project_settings.config'])
        mesh = next(m for ident, slot, m in plate_meshes(blobs, settings)[plate-1] if slot==3)
        gold_bounds.append(mesh.bounds)
        with ZipFile(validation) as z:
            code = z.read(f'Metadata/plate_{plate}.gcode').decode()
        rows = [r for r in paths(code) if r['tool']==3 and r['feature']!='Prime tower' and any(abs(r['layer']-h)<.0001 for h in (9.12,9.6))]
        assert rows
        versions.append({'title':title, 'project':project.name, 'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),
            'gcode_sha256':hashlib.sha256(code.encode()).hexdigest(), 'rows':rows,
            'flow':material['filament_flow_ratio'][2], 'temperature':material['nozzle_temperature'][2]})
    assert np.allclose(gold_bounds[0], gold_bounds[1], atol=1e-7)
    bounds = gold_bounds[0]
    box = [bounds[0,0], bounds[0,1], bounds[0,0]+24., bounds[0,1]+18.]
    factor = 2
    canvas = Image.new('RGB', (1560*factor, 1580*factor), '#f5f7fa')
    d = ImageDraw.Draw(canvas)
    font = lambda size: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size*factor)
    def text(x, y, value, size=24, fill='#17344a'):
        d.text((x*factor,y*factor), value, font=font(size), fill=fill)
    text(40,24,'Base do QR — comparação real V5 / V6',34)
    text(40,78,'Mesmo canto de 24 × 18 mm · mesma escala · camadas de 0,16 mm',24,'#455d70')
    for col, v in enumerate(versions):
        x = 55+col*790
        text(x,130,v['title'],30)
        text(x,176,f"Fluxo {v['flow'].replace('.', ',')} · bico {v['temperature']} °C",23,'#455d70')
    text(40,226,'Camada interna dourada — Z 9,12 mm',26)
    text(40,821,'Última camada dourada — Z 9,60 mm',26)
    panel_reports = []
    scale = 640/24
    for row, height in enumerate((9.12,9.6)):
        for col, v in enumerate(versions):
            left, top = 55+col*790, 276+row*595
            bottom = top+18*scale
            d.rectangle((left*factor,top*factor,(left+640)*factor,bottom*factor), fill='#ffffff', outline='#d4dee5', width=2)
            xy = lambda p: ((left+(p[0]-box[0])*scale)*factor,(bottom-(p[1]-box[1])*scale)*factor)
            speeds = set()
            count = 0
            for r in v['rows']:
                if abs(r['layer']-height)>.0001:
                    continue
                for p, q in zip(r['points'],r['points'][1:]):
                    segment = clip(p,q,box)
                    if segment is None:
                        continue
                    speeds.add(r['speed'])
                    count += 1
                    d.line([xy(segment[0]),xy(segment[1])], fill=color(r['speed']), width=4)
            assert count>0
            caption = ('Interior ≈ 81 mm/s · paredes até 75 mm/s' if col==0 else 'Interior e paredes: 25 mm/s') if row==0 else ('Preenchimento final: 20 mm/s')
            text(left,bottom+16,caption,22)
            panel_reports.append({'version':v['title'], 'layer_mm':height, 'clipped_chords_drawn':count,'visible_speeds_mm_s':sorted(speeds)})
    text(40,1427,'Cores = velocidade de extrusão no G-code',23)
    for x, c, label in zip((40,330,620,930),COLORS,('20 mm/s','25 mm/s','35 mm/s','75–81 mm/s')):
        d.line(((x*factor,1480*factor),((x+45)*factor,1480*factor)),fill=c,width=7*factor)
        text(x+60,1462,label,23)
    text(40,1513,'A base já tinha linhas: a maior mudança está na velocidade das camadas internas.',23)
    text(40,1550,'Traços centrais reais · a largura desenhada e as cores não representam o acabamento físico.',20,'#455d70')
    output = ROOT/'designs'/f'{PREFIX}.png'
    canvas.resize((1560,1580),Image.Resampling.LANCZOS).save(output)
    report = {'image':output.name, 'native_slicer_version':'02.08.02.61', 'rendered_layers_mm':[9.12,9.6],
        'same_xy_bounds_and_scale_verified':True, 'view_box_xy_mm':box, 'view_size_mm':[24.,18.],
        'colors_encode':'Requested G-code extrusion speed; blue 20, teal 25, amber 35, red 75–81 mm/s.',
        'geometry_type':'Clipped G-code extrusion centre lines, including sampled arcs. Drawn width is illustrative, not bead width.',
        'versions':[{k:value for k,value in v.items() if k!='rows'} for v in versions], 'panels':panel_reports,
        'physical_finish_predicted':False}
    (ROOT/'fusion/EssencialCompactoV6Base/toolpath-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--before-validation',type=Path,required=True)
    p.add_argument('--after-validation',type=Path,required=True)
    main(p.parse_args())
