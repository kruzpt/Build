"""Convert the approved concept into printable vector relief, not a sculpted mesh.

The reference is analyzed for silhouettes/color regions, with millimeter-scale
filtering of fine details. The resulting contours are shared by Fusion and STL.
Requires OpenCV, numpy, Pillow, trimesh and manifold3d in the generation venv.
"""
import argparse
import json
from pathlib import Path
from shutil import copyfile

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/JoanaTopper'
COLORS=[('preto','#202124',0,2.4),('dourado','#e8b449',2.4,0.8),
        ('castanho','#70452e',2.4,0.8),('bordo','#782c42',2.4,0.4)]


def clean(mask,closing=5,opening=5):
    mask=mask.astype(np.uint8)*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(closing,closing)))
    return cv2.morphologyEx(mask,cv2.MORPH_OPEN,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(opening,opening)))


def groups(mask,scale,x0,ymax,min_area=35):
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    result=[]
    if hierarchy is None: return result
    def points(c):
        simple=cv2.approxPolyDP(c,1.2,True)[:,0,:]
        return [[round((float(x)-x0)*scale,5),round((ymax-float(y))*scale,5)]
                for x,y in simple]
    for i,c in enumerate(contours):
        if hierarchy[0,i,3]!=-1 or cv2.contourArea(c)<min_area: continue
        loops=[points(c)]
        child=hierarchy[0,i,2]
        while child!=-1:
            if cv2.contourArea(contours[child])>=min_area:
                loops.append(points(contours[child]))
            child=hierarchy[0,child,0]
        if all(len(p)>=3 for p in loops): result.append(loops)
    return result


def cross_section(group_list):
    return md.CrossSection([p for group in group_list for p in group],md.FillRule.EvenOdd)


def section_groups(section):
    """Regroup manifold-normalized outer loops/holes for the Fusion sketches."""
    paths=[np.asarray(p) for p in section.to_polygons()]
    def area(p):
        return np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])/2
    outers=[p for p in paths if area(p)>0]
    holes=[p for p in paths if area(p)<0]
    result=[[p.tolist()] for p in outers]
    for hole in holes:
        point=hole[0].astype(np.float32)
        matches=[i for i,p in enumerate(outers)
                 if cv2.pointPolygonTest(p.astype(np.float32),tuple(map(float,point)),False)>0]
        if not matches: raise ValueError('Unassigned vector hole')
        chosen=min(matches,key=lambda i:abs(area(outers[i])))
        result[chosen].append(hole.tolist())
    return [[[list(map(lambda n:round(float(n),5),xy)) for xy in loop]
             for loop in group] for group in result]


def trace(reference,width):
    rgb=np.array(Image.open(reference).convert('RGB'))
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    r,g,b=np.moveaxis(rgb.astype(float),2,0)
    foreground=(rgb.max(axis=2)<175)|((r-b>60)&(g-b>30))
    # Exclude cast shadows on the otherwise light background.
    mask=clean(foreground,7,3)
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    outer=max(contours,key=cv2.contourArea)
    inside=np.zeros(mask.shape,np.uint8);cv2.drawContours(inside,[outer],-1,255,-1)
    mask=cv2.bitwise_and(mask,inside)
    # Replace the shaded stem tips with clean, broad insertion stems.
    mask[945:]=0
    for left,right in [(382,428),(805,851)]:
        middle=(left+right)//2
        cv2.fillPoly(mask,[np.array([(left,945),(right,945),(right,1170),
                       (middle+3,1205),(middle-3,1205),(left,1170)],np.int32)],255)
    bounds=cv2.boundingRect(outer);x0,y0,w,h=bounds
    scale=(width-0.8)/(w-1)
    base=cross_section(groups(mask,scale,x0,y0+h-1,min_area=200)).offset(
        0.4,md.JoinType.Round,circular_segments=12).simplify(0.01)
    # Gold has a yellow hue; burgundy is classified separately from warm browns.
    gold=(hsv[:,:,0]>=10)&(hsv[:,:,0]<=35)&(hsv[:,:,1]>65)&(hsv[:,:,2]>125)
    burgundy=(r>1.4*g)&(r>1.12*b)&(r>65)&((hsv[:,:,0]<12)|(hsv[:,:,0]>165))
    yy,xx=np.indices(mask.shape)
    broom=((xx>790)&(xx<965)&(yy>758)&(yy<805))|(
           (xx>1008)&(xx<1145)&(yy>700)&(yy<798))
    rings=(xx>925)&(xx<1008)&(yy>730)&(yy<803)
    brown=broom&~rings&(hsv[:,:,1]>60)&(hsv[:,:,2]>70)&(hsv[:,:,0]<32)
    gold&=~brown
    burgundy&=~brown&~gold
    gold_section=cross_section(groups(clean(gold&(mask>0),5,5),scale,x0,y0+h-1)) ^ base
    brown_section=cross_section(groups(clean(brown&(mask>0),7,5),scale,x0,y0+h-1)) ^ base
    burgundy_section=cross_section(groups(clean(burgundy&(mask>0),9,7),scale,x0,y0+h-1)) ^ base
    # Polygon simplification can move an edge; enforce non-overlapping materials.
    brown_section-=gold_section
    burgundy_section-=gold_section+brown_section
    sections=[base,gold_section,brown_section,burgundy_section]
    all_points=np.vstack(base.to_polygons())
    lower=all_points.min(axis=0)
    result=[]
    for (name,color,z,height),section in zip(COLORS,sections):
        section=section.translate(-lower)
        result.append({'name':name,'color':color,'z':z,'height':height,
                       'groups':section_groups(section)})
    extent=all_points.max(axis=0)-lower
    return {'name':'Joana','age':12,'width_mm':round(float(extent[0]),3),
            'height_mm':round(float(extent[1]),3),'max_z_mm':3.2,
            'base_thickness_mm':2.4,'nominal_detail_filter_mm':round(5*scale,3),
            'parts':result,'reference':'joana-topper-conceito-v1.png',
            'model_type':'contour-based flat relief; simplified from the concept'}


def models(data):
    result={}
    for p in data['parts']:
        regions=[p]+p.get('additions',[])
        pieces=[cross_section(r['groups']).extrude(r['height']).translate((0,0,r['z']))
                for r in regions]
        result[p['name']]=md.Manifold.batch_boolean(pieces,md.OpType.Add)
    return result


def save_mesh(solid,path):
    assert solid.status()==md.Error.NoError
    # Remove sub-micron Boolean slivers before STL float32 serialization.
    raw=solid.simplify(0.001).to_mesh()
    mesh=trimesh.Trimesh(vertices=raw.vert_properties[:,:3],faces=raw.tri_verts,process=True)
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
    mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent
    mesh.export(path)
    return mesh


def svg(data,path):
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{data["width_mm"]}mm" '
         f'height="{data["height_mm"]}mm" viewBox="0 0 {data["width_mm"]} {data["height_mm"]}">',
         '<title>Joana 12 — contornos reais do topper</title>']
    for p in data['parts']:
        for group in p['groups']:
            d=' '.join('M '+' L '.join(f'{x:.4f},{data["height_mm"]-y:.4f}' for x,y in loop)+' Z'
                       for loop in group)
            out.append(f'<path d="{d}" fill="{p["color"]}" fill-rule="evenodd"/>')
    out.append('</svg>');path.write_text('\n'.join(out)+'\n')


def preview(data,path):
    im=Image.new('RGB',(1000,1260),'#f5f0e7');draw=ImageDraw.Draw(im)
    scale=min(900/data['width_mm'],1060/data['height_mm'])
    ox=(1000-data['width_mm']*scale)/2;oy=110
    def point(p):return (ox+p[0]*scale,oy+(data['height_mm']-p[1])*scale)
    for part in data['parts']:
        # Render holes transparently to the existing lower material.
        layer=Image.new('L',im.size,0);pen=ImageDraw.Draw(layer)
        for group in part['groups']:
            for i,loop in enumerate(group):pen.polygon([point(p) for p in loop],fill=255 if i==0 else 0)
        im.paste(part['color'],mask=layer)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
    version=data.get('version','v1').upper()
    draw.text((40,25),f'Joana · 12 anos — modelo CAD {version}',font=font,fill='#282828')
    draw.text((40,64),f'{data["width_mm"]:.0f} × {data["height_mm"]:.0f} mm · 4 cores · bico 0,4 mm',font=font,fill='#282828')
    draw.text((40,1200),'Vista dos contornos reais; volumes e texturas do conceito simplificados.',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19),fill='#282828')
    im.save(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--width',type=float,default=180)
    args=parser.parse_args();FOLDER.mkdir(exist_ok=True)
    if args.reference:
        data=trace(args.reference,args.width)
        (FOLDER/'contours.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
        copyfile(args.reference,ROOT/'designs/joana-topper-conceito-v1.png')
    else:data=json.loads((FOLDER/'contours.json').read_text())
    solids=models(data)
    for name,solid in solids.items():save_mesh(solid,ROOT/f'downloads/joana-topper-v1-{name}.stl')
    combined=md.Manifold.batch_boolean(list(solids.values()),md.OpType.Add)
    assert len(combined.decompose())==1,'The assembled topper must be a connected object'
    total=save_mesh(combined,ROOT/'downloads/joana-topper-v1-completo.stl')
    svg(data,FOLDER/'joana-topper.svg');preview(data,ROOT/'designs/joana-topper-v1-CAD.png')
    stats={'extents_mm':total.extents.tolist(),'solid_volume_mm3':combined.volume(),
           'connected_assembled_bodies':len(combined.decompose()),
           'watertight':bool(total.is_watertight),'fusion_runtime_tested':False,
           'source':'approved generated concept, traced and filtered for flat relief',
           'parts':[{'name':p['name'],'groups':len(p['groups']),
                     'vertices':sum(len(loop) for g in p['groups'] for loop in g),
                     'solid_volume_mm3':solids[p['name']].volume()} for p in data['parts']]}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
