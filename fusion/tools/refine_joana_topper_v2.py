"""Replace the raster-traced broom with explicit printable CAD curves.

V1 is preserved. V2 closes all four holes in the black backing and creates
a coherent brown broom with gold collars and >= 1 mm black bristle grooves.
"""
import json
import math

import manifold3d as md
import numpy as np

from generate_joana_topper import ROOT,cross_section,section_groups,models,save_mesh,svg,preview

FOLDER=ROOT/'fusion/JoanaTopperV2'
STEM='joana-topper-v2'


def cubic(a,b,c,d,steps=24):
    a,b,c,d=map(np.array,(a,b,c,d))
    return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
            for t in np.linspace(0,1,steps+1)]


def stroke(points,width):
    pieces=[]
    for a,b in zip(points,points[1:]):
        a=np.array(a);b=np.array(b)
        delta=b-a;normal=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)*width/2
        pieces.append(md.CrossSection([[a+normal,b+normal,b-normal,a-normal]],md.FillRule.NonZero))
    pieces += [md.CrossSection.circle(width/2,16).translate(point) for point in points]
    return md.CrossSection.batch_boolean(pieces,md.OpType.Add).simplify(.02)


def collar(center,width,length):
    angle=math.radians(10)
    tangent=np.array([math.cos(angle),math.sin(angle)])
    normal=np.array([-math.sin(angle),math.cos(angle)])
    center=np.array(center)
    return md.CrossSection([[center+tangent*x+normal*y for x,y in [
        (-width/2,-length/2),(width/2,-length/2),(width/2,length/2),(-width/2,length/2)]]],md.FillRule.NonZero)


def broom_sections():
    handle=stroke(cubic((111.8,72.3),(122.5,72.5),(137.0,76.7),(151.0,78.2)),2.2)
    head=np.vstack([
        cubic((148.0,78.4),(154.0,83.5),(163.5,84.8),(173.0,85.5)),
        cubic((173.0,85.5),(170.2,82.5),(170.1,81.6),(173.0,80.2))[1:],
        cubic((173.0,80.2),(174.0,76.0),(168.4,70.9),(162.6,70.8))[1:],
        cubic((162.6,70.8),(156.2,70.7),(151.6,74.2),(148.0,76.4))[1:]])
    head=md.CrossSection([head],md.FillRule.NonZero)
    # Grooves stop inside the perimeter so the bristle bundle stays connected.
    grooves=[stroke(cubic(*p),1.0) for p in [
        ((154.4,80.5),(159.5,82.2),(163.5,82.3),(168.0,83.1)),
        ((154.0,78.4),(159.5,79.5),(165.4,79.6),(169.6,79.6)),
        ((154.0,76.3),(159.4,75.8),(163.7,75.3),(167.4,74.6))]]
    bristles=head-md.CrossSection.batch_boolean(grooves,md.OpType.Add)
    whole=handle+bristles
    bands=(collar((145.5,77.1),1.5,5.5)+collar((149.0,77.9),1.5,7.5))^whole
    return (whole-bands).simplify(.01),bands.simplify(.01),whole


def refined_data():
    data=json.loads((ROOT/'fusion/JoanaTopper/contours.json').read_text())
    black,gold,brown,bordo=data['parts']
    backing=md.CrossSection([g[0] for g in black['groups']],md.FillRule.EvenOdd)
    # Only the three old broom gold groups lie fully within this rectangle.
    # The number 2 ends before x=110.7; the lower star ends below y=68.4.
    old_broom=md.CrossSection.square((64,17)).translate((111,69))
    brown_shape,gold_bands,broom=broom_sections()
    backing+=broom.offset(.8,md.JoinType.Round,circular_segments=16)
    # Keep a continuous black backing, without interior white/background holes.
    backing=md.CrossSection([g[0] for g in section_groups(backing)],md.FillRule.EvenOdd).simplify(.01)
    gold_shape=(cross_section(gold['groups'])-old_broom)+gold_bands
    bordo_shape=cross_section(bordo['groups'])
    black['groups']=section_groups(backing)
    gold['groups']=section_groups(gold_shape)
    brown['groups']=section_groups(brown_shape)
    bordo['groups']=section_groups(bordo_shape)
    data['version']='v2'
    data['refinement']='Vector broom, 2.2 mm handle, 1 mm bristle grooves, 1.5 mm gold collars; closed black backing'
    return data


def main():
    FOLDER.mkdir(exist_ok=True)
    data=refined_data()
    (FOLDER/'contours.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    for name in ['JoanaTopper.py','JoanaTopper.manifest']:
        target=name.replace('JoanaTopper','JoanaTopperV2')
        text=(ROOT/'fusion/JoanaTopper'/name).read_text()
        if name.endswith('.py'):text=text.replace('Joana 12 — four-color','Joana 12 V2 — four-color')
        else:text=text.replace('"version": "1.0.0"','"version": "2.0.0"')
        (FOLDER/target).write_text(text)
    solids=models(data)
    for name,solid in solids.items():save_mesh(solid,ROOT/f'downloads/{STEM}-{name}.stl')
    combined=md.Manifold.batch_boolean(list(solids.values()),md.OpType.Add)
    assert len(combined.decompose())==1
    mesh=save_mesh(combined,ROOT/f'downloads/{STEM}-completo.stl')
    svg(data,FOLDER/'joana-topper.svg');preview(data,ROOT/f'designs/{STEM}-CAD.png')
    assert all(len(g)==1 for g in data['parts'][0]['groups'])
    stats={'version':'v2','extents_mm':mesh.extents.tolist(),'solid_volume_mm3':combined.volume(),
           'connected_assembled_bodies':1,'black_backing_holes':0,'watertight':bool(mesh.is_watertight),
           'fusion_runtime_tested':False,'physical_print_tested':False,
           'broom_handle_width_mm':2.2,'bristle_groove_width_mm':1.0,'gold_collar_width_mm':1.5,
           'parts':[{'name':p['name'],'groups':len(p['groups']),
                     'vertices':sum(len(loop) for g in p['groups'] for loop in g),
                     'solid_volume_mm3':solids[p['name']].volume()} for p in data['parts']]}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
