"""Add broom gold, clean letter tops and construct uniform stems/cake stop.

V1/V2 files remain preserved. A single black material includes the thicker
support ledge, avoiding an extra AMS slot or a separate assembly.
"""
import argparse
import json

import manifold3d as md
from PIL import Image,ImageDraw,ImageFont

from generate_joana_topper import ROOT,cross_section,section_groups,models,save_mesh,svg,preview
from refine_joana_topper_v2 import collar

FOLDER=ROOT/'fusion/JoanaTopperV3'
STEM='joana-topper-v3'
STEM_CENTERS=(51.33,122.44)
STEM_WIDTH=8.5
INSERTION_DEPTH=44.0
STOP_X=43.0
STOP_Y=44.0
STOP_WIDTH=88.0
STOP_HEIGHT=6.0


def stop_section():
    return md.CrossSection.square((STOP_WIDTH-2,STOP_HEIGHT-2)).translate(
        (STOP_X+1,STOP_Y+1)).offset(1,md.JoinType.Round,circular_segments=16).simplify(.02)


def stem_section(center):
    left,right=center-STEM_WIDTH/2,center+STEM_WIDTH/2
    return md.CrossSection([[(left,INSERTION_DEPTH),(left,6),(center-.55,0),
        (center+.55,0),(right,6),(right,INSERTION_DEPTH)]],md.FillRule.NonZero)


def refined_data(stop_depth=8):
    data=json.loads((ROOT/'fusion/JoanaTopperV2/contours.json').read_text())
    black,gold,brown,bordo=data['parts']
    base=cross_section(black['groups'])
    # Remove both old traced stems, including the steps at their roots.
    keep=md.CrossSection.square((220,220)).translate((-20,INSERTION_DEPTH))
    base=(base^keep)+stop_section()
    for center in STEM_CENTERS:base+=stem_section(center)
    # The new bar can enclose tiny gaps beneath the old curved bottom edge.
    # Fill those too, so the backing remains continuous and entirely black.
    base=md.CrossSection([g[0] for g in section_groups(base)],md.FillRule.EvenOdd).simplify(.02)
    gold_shape=cross_section(gold['groups'])
    brown_shape=cross_section(brown['groups'])
    # The three internal brown holes are the deliberately drawn bristle grooves.
    brush_gold=md.CrossSection([hole for group in brown['groups'] for hole in group[1:]],md.FillRule.NonZero)
    tip_gold=collar((112.4,72.4),3.4,5)^brown_shape
    gold_shape+=brush_gold+tip_gold
    brown_shape-=tip_gold
    # Close submillimeter tracing cuts at the tops, preserving the Gothic peaks.
    top_zone=md.CrossSection.square((122,24)).translate((25,120))
    digit_zone=md.CrossSection.square((54,9)).translate((60,87))
    zone=top_zone+digit_zone
    polished=gold_shape.offset(.4,md.JoinType.Round,circular_segments=24).offset(
        -.4,md.JoinType.Round,circular_segments=24).simplify(.08)
    gold_shape=(gold_shape-zone)+(polished^zone)
    gold_shape=(gold_shape^base).simplify(.015)
    brown_shape=(brown_shape-gold_shape).simplify(.015)
    bordo_shape=(cross_section(bordo['groups'])-gold_shape).simplify(.015)
    black['groups']=section_groups(base)
    if stop_depth>black['height']:
        black['additions']=[{'name':'Apoio bolo','z':0,'height':stop_depth,
                            'groups':section_groups(stop_section())}]
    gold['groups']=section_groups(gold_shape)
    brown['groups']=section_groups(brown_shape)
    bordo['groups']=section_groups(bordo_shape)
    data.update({'version':'v3','max_z_mm':max(3.2,float(stop_depth)),
                 'refinement':'Gold bristle grooves and handle cap; polished letter tops; identical stems and cake stop',
                 'cake_stop':{'x':STOP_X,'y':STOP_Y,'width_mm':STOP_WIDTH,
                              'height_mm':STOP_HEIGHT,'depth_mm':stop_depth},
                 'stems':{'centers_x_mm':list(STEM_CENTERS),'width_mm':STEM_WIDTH,
                          'insertion_depth_mm':INSERTION_DEPTH,'tip_flat_mm':1.1},
                 'letter_top_polish_radius_mm':.4})
    return data


def support_preview(data,path):
    """Dimensioned front/side views taken from the actual black CAD solid."""
    im=Image.new('RGB',(1100,900),'#f5f0e7');draw=ImageDraw.Draw(im)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    large=ImageFont.truetype(font,26);small=ImageFont.truetype(font,20)
    draw.text((30,20),'Joana 12 V3 — hastes iguais e apoio sobre o bolo',font=large,fill='#202124')
    draw.text((30,64),'Verde: linha de referência do bolo; a peça é preta.',font=small,fill='#202124')
    scale=8;floor=790
    def paint(section,origin):
        mask=Image.new('L',im.size,0);pen=ImageDraw.Draw(mask)
        for group in section_groups(section):
            for index,loop in enumerate(group):
                pen.polygon([(origin+x*scale,floor-y*scale) for x,y in loop],fill=255 if index==0 else 0)
        im.paste('#202124',mask=mask)
    base=cross_section(data['parts'][0]['groups'])
    front=base^md.CrossSection.square((110,75)).translate((35,0))
    paint(front,-220)
    black=models(data)['preto']
    side=black.rotate((0,90,0)).slice(-STEM_CENTERS[0])
    side^=md.CrossSection.square((20,75)).translate((-1,0))
    paint(side,950)
    cake=floor-INSERTION_DEPTH*scale
    draw.line((25,cake,850,cake),fill='#299d67',width=2)
    draw.line((885,cake,1060,cake),fill='#299d67',width=2)
    draw.text((35,150),'Vista frontal — parte inferior',font=small,fill='#202124')
    draw.text((855,150),'Vista lateral',font=small,fill='#202124')
    draw.line((850,floor,850,cake),fill='#58747b',width=2)
    draw.line((840,floor,860,floor),fill='#58747b',width=2)
    draw.line((840,cake,860,cake),fill='#58747b',width=2)
    draw.text((705,610),'44 mm',font=small,fill='#58747b')
    end=950+data['cake_stop']['depth_mm']*scale
    draw.line((950,360,end,360),fill='#58747b',width=2)
    draw.line((950,352,950,368),fill='#58747b',width=2)
    draw.line((end,352,end,368),fill='#58747b',width=2)
    draw.text((920,325),f'{data["cake_stop"]["depth_mm"]:g} mm',font=small,fill='#58747b')
    draw.text((35,840),'Travessa: 88 × 6 mm · hastes: 8,5 mm de largura · apoio com cantos arredondados',font=small,fill='#202124')
    im.save(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stop-depth',type=float,default=8,choices=[2.4,8])
    args=parser.parse_args();FOLDER.mkdir(exist_ok=True)
    data=refined_data(args.stop_depth)
    assert all(len(g)==1 for g in data['parts'][0]['groups'])
    (FOLDER/'contours.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    solids=models(data)
    for name,solid in solids.items():save_mesh(solid,ROOT/f'downloads/{STEM}-{name}.stl')
    combined=md.Manifold.batch_boolean(list(solids.values()),md.OpType.Add)
    assert len(combined.decompose())==1
    mesh=save_mesh(combined,ROOT/f'downloads/{STEM}-completo.stl')
    svg(data,FOLDER/'joana-topper.svg');preview(data,ROOT/f'designs/{STEM}-CAD.png')
    support_preview(data,ROOT/f'designs/{STEM}-apoio.png')
    stats={'version':'v3','extents_mm':mesh.extents.tolist(),'solid_volume_mm3':combined.volume(),
           'connected_assembled_bodies':1,'black_backing_holes':0,'watertight':bool(mesh.is_watertight),
           'cake_stop':data['cake_stop'],'stems':data['stems'],
           'fusion_runtime_tested':False,'physical_print_tested':False,
           'parts':[{'name':p['name'],'groups':len(p['groups']),
                     'vertices':sum(len(loop) for g in p['groups'] for loop in g),
                     'solid_volume_mm3':solids[p['name']].volume()} for p in data['parts']]}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
