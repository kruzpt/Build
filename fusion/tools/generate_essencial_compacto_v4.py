"""Create the asymmetric clinic sign at 220 mm assembled height, without NFC."""
import ast
import hashlib
import json
from pathlib import Path

import cv2
import manifold3d as md
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh

import generate_m7_prototypes_v1 as v
from generate_joana_topper import cross_section, groups, save_mesh
from generate_universo_stand import render_meshes

ROOT=v.ROOT
FOLDER=ROOT/'fusion/EssencialCompactoV4'
PREFIX='essencial-compacto-v4-azeitona'
WHITE,GREEN,GOLD,BLACK='#FFFDF7','#737648','#DDB34E','#202124'
URLS={'Instagram':'https://www.instagram.com/clinicaessencial_setubal/',
      'Google':'https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg'}
PLATE_SCALE=190.4/208
BASE_HEIGHT=9.6
SERIF='/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf'


def wave(x):
    """Smooth central dip: local shoulder rises 0..10 mm towards the sides."""
    return 10*(1-np.exp(-(np.asarray(x,dtype=float)/40)**2))


def path(start,commands):
    points=[start]
    for command in commands:
        if len(command)==2:points.append(command)
        else:
            p0=np.array(points[-1]);p1,p2,p3=np.array(command).reshape(3,2)
            for t in np.linspace(0,1,41)[1:]:points.append(((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3).tolist())
    return md.CrossSection([points],md.FillRule.EvenOdd)


def qr_rows():
    tree=ast.parse((ROOT/'fusion/EssencialA1Reviews/EssencialA1Reviews.py').read_text())
    result={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ('INSTAGRAM_ROWS','GOOGLE_ROWS'):
                    result['Instagram' if target.id=='INSTAGRAM_ROWS' else 'Google']=ast.literal_eval(node.value)
    assert set(result)==set(URLS)
    return result


def qr_section(rows,x,y):
    pitch=64/len(rows);rectangles=[]
    for row,line in enumerate(rows):
        col=0
        while col<len(line):
            if line[col]=='0':col+=1;continue
            end=col+1
            while end<len(line) and line[end]=='1':end+=1
            # 0.02 mm separation prevents corner-only contacts in the black STL;
            # all islands remain attached to the solid white backing after printing.
            rectangles.append(v.rect(x+col*pitch+.01,y+(len(rows)-row-1)*pitch+.01,(end-col)*pitch-.02,pitch-.02))
            col=end
    return md.CrossSection.batch_boolean(rectangles,md.OpType.Add)


def trace_fox(source):
    cache=FOLDER/'fox-reference.json'
    if source.exists():
        image=cv2.imread(str(source));crop=image[220:475,780:955]
        hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
        mask=((hsv[:,:,1]>65)&(hsv[:,:,2]<222)).astype('uint8')*255
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        cs=cross_section(groups(mask,1,0,crop.shape[0],min_area=60))
        cs=v.normalize(cs,height=40).offset(.10,circular_segments=16).simplify(.03)
        cache.write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'method':'Colour segmentation of reference fox, not original vector logo',
            'groups':v.region(cs,1)['groups']},indent=2)+'\n')
    else:cs=cross_section(json.loads(cache.read_text())['groups'])
    return cs


def main():
    FOLDER.mkdir(exist_ok=True)
    front=path((-96,16),[(-96,177),(-96,200,-85,208,-68,208),
        (-42,208,-20,194,15,188),(48,182,78,178,89,159),
        (96,148,96,130,96,110),(96,16),(96,5,90,0,80,0),
        (-80,0),(-90,0,-96,5,-96,16)])
    rear=path((-88,0),[(-88,165),(-88,190,-60,192,-30,198),
        (-6,204,14,208,36,208),(72,208,104,194,104,167),
        (104,0),(-88,0)])
    # Organic footprint follows the client's top-view outline; height is flat.
    footprint=path((-100,31),[(-100,13,-88,0,-72,0),
        (-46,0,-32,17,-11,18),(12,20,22,1,44,1),
        (75,-2,100,12,100,33),(100,56,91,70,77,70),
        (64,70,58,64,46,66),(0,76,-34,71,-70,66),
        (-90,64,-100,53,-100,31)])
    a,b,c,d=footprint.bounds()
    footprint=footprint.translate((-a,-b)).scale((200/(c-a),70/(d-b))).translate((-100,0))
    # Straight hidden tongues join the contoured shoulders above the wave.
    tongue_white=v.rounded(-70,-6.2/PLATE_SCALE,140,25,.3)
    tongue_green=v.rounded(-80,-6.2/PLATE_SCALE,160,25,.3)
    white_profile=front+tongue_white;green_profile=rear+tongue_green
    white=white_profile.extrude(3.2)
    white_regions=[v.region(white_profile,3.2)]
    cards=[]
    for x in (-84,8):
        card=v.rounded(x,19,76,91,3.)
        assert (card-front).area()<.001
        white+=card.extrude(.48).translate((0,0,3.2))
        white_regions.append(v.region(card,.48,3.2,'join'))
        cards.append(card)
    green=green_profile.extrude(3.2)
    green_regions=[v.region(green_profile,3.2)]
    ribs=md.CrossSection()
    for x in np.arange(-87,105,3.2):ribs+=v.rect(float(x),0,1.25,210)
    ribs=ribs^rear
    green+=ribs.extrude(1.).translate((0,0,3.2))
    green_regions.append(v.region(ribs,1.,3.2,'join'))
    slots=[v.rounded(-70*PLATE_SCALE-.3,32.4-1.8,140*PLATE_SCALE+.6,3.6,.3),
           v.rounded(-80*PLATE_SCALE-.3,37.6-1.8,160*PLATE_SCALE+.6,3.6,.3)]
    base=footprint.extrude(8.64).translate((0,0,.96))
    base_regions=[v.region(footprint,8.64,.96)]
    for slot in slots:
        assert (slot-footprint).area()<.001
        base-=slot.extrude(10).translate((0,0,3.2))
        base_regions.append(v.region(slot,10,3.2,'cut'))
    trim=footprint.extrude(.96)
    gold=v.text('Clínica',106,font=SERIF,strengthen=.14).translate((-25,164))
    gold+=v.text('Essencial',136,font=SERIF,strengthen=.14).translate((-20,133))
    # Reuse the V1 derived trace; do not reinterpret the identity in this revision.
    fox_data=json.loads((ROOT/'fusion/EssencialArcos220/fox-reference.json').read_text())
    fox=cross_section(fox_data['groups'])
    clean=[];removed=[]
    for component in fox.decompose():
        x0,y0,x1,y1=component.bounds()
        if x1<-9 and x1-x0<4 and y1<16:
            removed.append(component)
        else:clean.append(component)
    assert len(removed)==1 and 26<removed[0].area()<28
    fox=md.CrossSection.batch_boolean(clean,md.OpType.Add)
    fox_data['groups']=v.region(fox,1)['groups']
    fox_data['cleanup']='Removed detached serif fragment to left of fox; two fox components retained'
    (FOLDER/'fox-reference.json').write_text(json.dumps(fox_data,indent=2)+'\n')
    fox=fox.translate((70,132))
    gold+=fox
    gold+=v.rounded(-83,113,166,.6,.29)
    assert (gold-front).area()<.001,('Gold outside panel',(gold-front).area())
    wording=v.text('N Á D I A   P A L O N G O',121,font=v.REGULAR,strengthen=.07).translate((0,119))
    assert (wording-front).area()<.001
    qrdata=qr_rows();qr_sections={};caption=md.CrossSection()
    for name,x in [('Instagram',-78),('Google',14)]:
        qr_sections[name]=qr_section(qrdata[name],x,41)
    # Recognisable monochrome service icons, kept outside all QR quiet zones.
    insta=v.rounded(-76,23,9,9,2)-v.rounded(-74.9,24.1,6.8,6.8,1.2)
    insta+=md.CrossSection.circle(2.2,32).translate((-71.5,27.5))-md.CrossSection.circle(1.2,32).translate((-71.5,27.5))
    insta+=md.CrossSection.circle(.65,24).translate((-69,30))
    caption+=insta
    caption+=v.text('Instagram',41,strengthen=.02).translate((-40,24.2))
    caption+=v.text('G',8,strengthen=.03).translate((27,29))
    caption+=v.text('Google',30,strengthen=.02).translate((51,29.5))
    caption+=v.text('Deixe a sua opinião',61,strengthen=.025).translate((46,21.9))
    card_union=cards[0]+cards[1]
    assert (caption-card_union).area()<.001
    qr_all=qr_sections['Instagram']+qr_sections['Google']
    # White pedestals carry the upper lettering to the same height as QR cards.
    # Therefore ALL white is complete before either top color begins.
    pedestals=gold+wording
    white+=pedestals.extrude(.48).translate((0,0,3.2))
    white_regions.append(v.region(pedestals,.48,3.2,'join'))
    black=(wording+caption+qr_all).extrude(.32).translate((0,0,3.68))
    gold_solid=gold.extrude(.32).translate((0,0,3.68))
    assert (gold_solid^black).volume()<.001
    fp=v.pose_front(34);fp[2,3]=BASE_HEIGHT
    bp=v.pose_front(39.2);bp[2,3]=BASE_HEIGHT
    solids=[s.scale((PLATE_SCALE,PLATE_SCALE,1)) for s in [white,gold_solid,black,green]]+[base,trim]
    keys=['frente-branca','letras-raposa-douradas','qr-texto-preto','fundo-nervurado-verde','base-verde','friso-dourado']
    colors=[WHITE,GOLD,BLACK,GREEN,GREEN,GOLD]
    poses=[fp,fp,fp,bp,v.identity(),v.identity()]
    regions=[white_regions,[v.region(gold,.32,3.68)],
             [v.region(wording+caption+qr_all,.32,3.68)],green_regions,
             base_regions,[v.region(footprint,.96)]]
    for rs in regions[:4]:
        for r in rs:
            r['groups']=[[[[x*PLATE_SCALE,y*PLATE_SCALE] for x,y in loop] for loop in group] for group in r['groups']]
    parts=[];assembled=[]
    for solid,key,col,pose,rs in zip(solids,keys,colors,poses,regions):
        pathfile=ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=save_mesh(solid,pathfile)
        parts.append({'key':key,'name':key.replace('-',' '),'product':'expositor',
            'color':col,'file':pathfile.name,'regions':rs,'assembly':pose.tolist(),
            'bbox_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),
            'sha256':hashlib.sha256(pathfile.read_bytes()).hexdigest(),'watertight':True})
        assembled.append((v.transformed(solid,pose),col))
    for i,(a,_) in enumerate(assembled):
        for b,_ in assembled[i+1:]:assert (a^b).volume()<.001
    insertion=[]
    for index in (0,1,2,3):
        for dz in np.linspace(0,30,31):
            collision=(assembled[index][0].translate((0,0,float(dz)))^v.union([base,trim])).volume()
            assert collision<.001
            insertion.append(collision)
    combined=v.union([s for s,c in assembled]);raw=combined.to_mesh()
    mesh=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
    np.testing.assert_allclose(mesh.bounds,[[-100,0,0],[100,70,200]],atol=.01)
    # Static projected centre of gravity inside actual contact outline, not a push test.
    mass=[];centres=[]
    for s,c in assembled:
        raw=s.to_mesh();m=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
        mass.append(m.volume*(.55 if c==GREEN and s is not assembled[3][0] else 1))
        centres.append(m.center_mass)
    cg=np.average(centres,axis=0,weights=mass)
    loop=np.asarray(footprint.to_polygons()[0],dtype=np.float32)
    margin=cv2.pointPolygonTest(loop,tuple(map(float,cg[:2])),True)
    assert margin>12
    # Rasterise exported black STL sections, not the original matrices, to verify QR fidelity.
    actual=trimesh.load(ROOT/'downloads'/f'{PREFIX}-qr-texto-preto.stl',force='mesh')
    actual_solid=md.Manifold(md.Mesh(actual.vertices.astype('float32'),actual.faces.astype('uint32')))
    decoded={};minimum_pitch=64*PLATE_SCALE/45
    for name,x in [('Instagram',-78),('Google',14)]:
        x=x*PLATE_SCALE
        region=actual_solid.slice(3.84)^v.rect(x,41*PLATE_SCALE,64*PLATE_SCALE,64*PLATE_SCALE)
        image=Image.new('L',(1280,1280),255);draw=ImageDraw.Draw(image)
        for polygon in region.to_polygons():
            p=np.asarray(polygon)
            area=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])/2
            draw.polygon([((xx-x)*20/PLATE_SCALE,(105*PLATE_SCALE-yy)*20/PLATE_SCALE) for xx,yy in polygon],fill=0 if area>0 else 255)
        value,_,_=cv2.QRCodeDetector().detectAndDecode(np.asarray(image))
        assert value==URLS[name],(name,value)
        image.save(FOLDER/f'qr-{name.lower()}-stl.png')
        decoded[name]=value
    report={'overall_width_depth_height_mm':[200,70,200],'base_height_range_mm':[9.6,9.6],
        'wave_height_amplitude_mm':0,'wave_shoulder_clearance_mm':0,
        'wave_profile':'none: flat top, organic XY footprint',
        'slot_width_mm':3.6,'tongue_thickness_mm':3.2,'clearance_per_side_mm':.2,
        'slot_depth_range_mm':[6.4,6.4],'tongue_tip_floor_z_mm':3.4,'slot_floor_mm':3.2,'bottom_clearance_mm':.2,
        'front_thickness_mm':3.2,'rear_core_thickness_mm':3.2,'rib_relief_mm':1,
        'rib_pitch_mm':3.2,'rib_width_mm':1.25,'rib_free_insertion_tongue':True,
        'qr_field_mm':64*PLATE_SCALE,'plate_xy_scale':PLATE_SCALE,'requires_new_front_and_rear':True,'qr_modules_with_quiet_zone':45,'qr_pitch_mm':minimum_pitch,
        'qr_relief_mm':.32,'card_relief_mm':.48,'all_front_color_start_mm':3.68,'all_front_color_top_mm':4.0,'removed_serif_area_mm2':removed[0].area(),'qr_stl_decoded':decoded,'insertion_checks':len(insertion),
        'max_collision_mm3':max(insertion),'static_cg_mm':cg.tolist(),'static_margin_mm':margin,
        'logo_original_vector_available':False,'fox_traced_from_reference':True,
        'typeface':'Nimbus Roman; interpretation of reference, not an exact original vector',
        'nfc':False,'whatsapp':False,'physical_fit_tested':False,'physical_qr_scan_tested':False,
        'structural_load_or_push_tested':False,'fusion_runtime_tested':False}
    (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','parts':parts,'validation':report},ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    template=(ROOT/'fusion/M7TijoloV3/M7TijoloV3.py').read_text()
    template=template.replace('M7 - Tijolo Natal 2026 V3 - 7 pincelado','Clinica Essencial Compacto V4 200 mm')
    template=template.replace('M7 Tijolo V3 criado num documento novo.','Expositor Essencial 220 criado num documento novo.')
    template=template.replace('Tijolo: 50 x 26 x 70 mm, rebaixos 0,20 mm.','Conjunto: 200 x 70 x 200 mm; dois encaixes independentes.')
    template=template.replace('Use o projeto 3MF V3 de quatro pratos para imprimir.','Use o projeto 3MF Essencial Compacto V4 para imprimir.')
    template=template.replace('Falha ao criar M7:','Falha ao criar Clínica Essencial:')
    (FOLDER/'EssencialCompactoV4.py').write_text(template)
    sample= v.rounded(-23,0,46,20,3).extrude(9.6)
    for y in (8.,13.2):
        sample-=v.rounded(-10.3,y-1.8,20.6,3.6,.3).extrude(9).translate((0,0,3.2))
    for x in (-13.,13.):
        grip=v.rounded(x-11.5,33.8,23,14,1)
        tab=v.rounded(x-10,28,20,6.2,.3)
        sample+=(grip+tab).extrude(3.2)
    sample_path=ROOT/'downloads'/f'{PREFIX}-amostra-encaixes.stl'
    sm=save_mesh(sample,sample_path)
    assert len(sm.split())==3
    sheet(assembled)
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)


def sheet(assembled):
    image=Image.new('RGB',(1700,1200),'#f4f6f8');draw=ImageDraw.Draw(image)
    font=lambda n:ImageFont.truetype(v.REGULAR,n)
    image.paste(render_meshes(assembled,(880,980),direction=(.45,-1,.30)),(0,130))
    exploded=[]
    for i,(s,c) in enumerate(assembled):
        exploded.append((s.translate((0,(-18 if i<3 else 12 if i==3 else 0),35 if i<4 else 0)),c))
    image.paste(render_meshes(exploded,(790,820),direction=(.65,-1,.5)),(900,160))
    draw=ImageDraw.Draw(image)
    draw.text((35,25),'Clínica Essencial · compacto V4 · topo plano',font=font(38),fill=v.BLUE)
    draw.text((35,82),'200 × 70 × 200 mm · Instagram + avaliações Google · sem NFC',font=font(27),fill=v.BLUE)
    draw.text((920,1020),'QR reais: campos de 58,6 × 58,6 mm',font=font(25),fill=v.BLUE)
    draw.text((920,1065),'Base plana: 9,6 mm de altura',font=font(25),fill=v.BLUE)
    draw.text((35,1130),'Geometria real · contorno orgânico visto de cima · branco antes das cores',font=font(25),fill=v.BLUE)
    draw.text((35,1170),'Encaixes, leitura física e estabilidade ao toque a confirmar no protótipo.',font=font(24),fill=v.BLUE)
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    top=Image.new('RGB',(1450,720),'#f4f6f8');pen=ImageDraw.Draw(top)
    # Orthographic section of the real top surface; dark areas are slot floors.
    for polygon in assembled[4][0].slice(9.5).to_polygons():
        a=np.asarray(polygon)
        signed=np.sum(a[:,0]*np.roll(a[:,1],-1)-np.roll(a[:,0],-1)*a[:,1])/2
        pen.polygon([(125+(x+100)*6,150+(70-y)*6) for x,y in polygon],fill=GREEN if signed>0 else '#263125')
    pen.text((125,585),'Frente',font=font(22),fill=v.BLUE)
    pen.text((30,20),'Base V4 · vista de cima · contorno orgânico',font=font(32),fill=v.BLUE)
    pen.text((30,640),'200 × 70 mm · topo plano a 9,6 mm · sem onda em altura',font=font(27),fill=v.BLUE)
    top.save(ROOT/'designs'/f'{PREFIX}-base-vista-superior.png')
    for label,color in [('azeitona',GREEN)]:
        items=[(s,color if c==GREEN else c) for s,c in assembled]
        im=Image.new('RGB',(1350,1500),'#f4f6f8')
        im.paste(render_meshes(items,(1180,1240),direction=(.25,-1,.22)),(90,85))
        d=ImageDraw.Draw(im)
        d.text((40,25),f'Clínica Essencial · compacto · {label}',font=font(34),fill=v.BLUE)
        d.line((70,170,70,1320),fill=v.BLUE,width=2)
        for y in (170,1320):d.line((58,y,82,y),fill=v.BLUE,width=2)
        d.text((15,140),'200 mm de altura',font=font(23),fill=v.BLUE)
        d.line((160,1370,1190,1370),fill=v.BLUE,width=2)
        for x in (160,1190):d.line((x,1358,x,1382),fill=v.BLUE,width=2)
        d.text((675,1390),'Largura: 200 mm · profundidade: 70 mm',font=font(25),fill=v.BLUE,anchor='mt')
        d.text((45,1450),'Geometria real · branco completo antes dos relevos de cor',font=font(23),fill=v.BLUE)
        im.save(ROOT/'designs'/f'{PREFIX}-{label}-dimensoes.png')


if __name__=='__main__':main()
