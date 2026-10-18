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
FOLDER=ROOT/'fusion/EssencialArcos220'
PREFIX='essencial-arcos-220-v1'
WHITE,GREEN,GOLD,BLACK='#FFFDF7','#78866B','#DDB34E','#202124'
URLS={'Instagram':'https://www.instagram.com/clinicaessencial_setubal/',
      'Google':'https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg'}
SERIF='/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf'


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
    footprint=path((-110,27),[(-110,10,-100,0,-80,0),
        (-48,0,-34,7,0,7),(34,7,48,0,80,0),(100,0,110,10,110,27),
        (110,53),(110,70,100,80,80,80),(-80,80),(-100,80,-110,70,-110,53),(-110,27)])
    tongue_white=v.rounded(-70,-7.8,140,8.2,.3)
    tongue_green=v.rounded(-80,-7.8,160,8.2,.3)
    white_profile=front+tongue_white;green_profile=rear+tongue_green
    white=white_profile.extrude(3.2)
    white_regions=[v.region(white_profile,3.2)]
    cards=[]
    for x in (-84,8):
        card=v.rounded(x,19,76,91,3.)
        assert (card-front).area()<.001
        white+=card.extrude(1).translate((0,0,3.2))
        white_regions.append(v.region(card,1,3.2,'join'))
        cards.append(card)
    green=green_profile.extrude(3.2)
    green_regions=[v.region(green_profile,3.2)]
    ribs=md.CrossSection()
    for x in np.arange(-87,105,3.2):ribs+=v.rect(float(x),0,1.25,210)
    ribs=ribs^rear
    green+=ribs.extrude(1.).translate((0,0,3.2))
    green_regions.append(v.region(ribs,1.,3.2,'join'))
    # Base slots are blind: floor Z=4, shoulders Z=12, 0.2 mm bottom gap.
    slots=[v.rounded(-70.3,32.4-1.8,140.6,3.6,.3),
           v.rounded(-80.3,37.6-1.8,160.6,3.6,.3)]
    base=footprint.extrude(10.8).translate((0,0,1.2))
    base_regions=[v.region(footprint,10.8,1.2)]
    for slot in slots:
        assert (slot-footprint).area()<.001
        base-=slot.extrude(8.1).translate((0,0,4))
        base_regions.append(v.region(slot,8.1,4,'cut'))
    trim=footprint.extrude(1.2)
    gold=v.text('Clínica',106,font=SERIF,strengthen=.14).translate((-25,164))
    gold+=v.text('Essencial',136,font=SERIF,strengthen=.14).translate((-20,133))
    fox=trace_fox(Path('/tmp/codex-remote-attachments/01a116d6-a0e2-751f-b4ce-c385f66bd04b/9e8d828a-9d8e-4cac-bad4-2185d4eb0d47/1-1000077363.jpg'))
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
    black=wording.extrude(.6).translate((0,0,3.2))
    black+=(caption+qr_all).extrude(.6).translate((0,0,4.2))
    gold_solid=gold.extrude(.6).translate((0,0,3.2))
    assert (gold_solid^black).volume()<.001
    fp=v.pose_front(34);fp[2,3]=12
    bp=v.pose_front(39.2);bp[2,3]=12
    solids=[white,gold_solid,black,green,base,trim]
    keys=['frente-branca','letras-raposa-douradas','qr-texto-preto','fundo-nervurado-verde','base-verde','friso-dourado']
    colors=[WHITE,GOLD,BLACK,GREEN,GREEN,GOLD]
    poses=[fp,fp,fp,bp,v.identity(),v.identity()]
    regions=[white_regions,[v.region(gold,.6,3.2)],
             [v.region(wording,.6,3.2),v.region(caption+qr_all,.6,4.2)],green_regions,
             base_regions,[v.region(footprint,1.2)]]
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
    np.testing.assert_allclose(mesh.bounds,[[-110,0,0],[110,80,220]],atol=.01)
    # Static projected centre of gravity inside actual contact outline, not a push test.
    mass=[];centres=[]
    for s,c in assembled:
        raw=s.to_mesh();m=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
        mass.append(m.volume*(.55 if c==GREEN and s is not assembled[3][0] else 1))
        centres.append(m.center_mass)
    cg=np.average(centres,axis=0,weights=mass)
    loop=np.asarray(footprint.to_polygons()[0],dtype=np.float32)
    margin=cv2.pointPolygonTest(loop,tuple(map(float,cg[:2])),True)
    assert margin>20
    # Rasterise exported black STL sections, not the original matrices, to verify QR fidelity.
    actual=trimesh.load(ROOT/'downloads'/f'{PREFIX}-qr-texto-preto.stl',force='mesh')
    actual_solid=md.Manifold(md.Mesh(actual.vertices.astype('float32'),actual.faces.astype('uint32')))
    decoded={};minimum_pitch=64/45
    for name,x in [('Instagram',-78),('Google',14)]:
        region=actual_solid.slice(4.5)^v.rect(x,41,64,64)
        image=Image.new('L',(1280,1280),255);draw=ImageDraw.Draw(image)
        for polygon in region.to_polygons():
            p=np.asarray(polygon)
            area=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])/2
            draw.polygon([((xx-x)*20,(105-yy)*20) for xx,yy in polygon],fill=0 if area>0 else 255)
        value,_,_=cv2.QRCodeDetector().detectAndDecode(np.asarray(image))
        assert value==URLS[name],(name,value)
        image.save(FOLDER/f'qr-{name.lower()}-stl.png')
        decoded[name]=value
    report={'overall_width_depth_height_mm':[220,80,220],'base_height_mm':12,
        'slot_width_mm':3.6,'tongue_thickness_mm':3.2,'clearance_per_side_mm':.2,
        'slot_depth_mm':8,'tongue_insertion_mm':7.8,'slot_floor_mm':4,'bottom_clearance_mm':.2,
        'front_thickness_mm':3.2,'rear_core_thickness_mm':3.2,'rib_relief_mm':1,
        'rib_pitch_mm':3.2,'rib_width_mm':1.25,'rib_free_insertion_tongue':True,
        'qr_field_mm':64,'qr_modules_with_quiet_zone':45,'qr_pitch_mm':minimum_pitch,
        'qr_relief_mm':.6,'qr_stl_decoded':decoded,'insertion_checks':len(insertion),
        'max_collision_mm3':max(insertion),'static_cg_mm':cg.tolist(),'static_margin_mm':margin,
        'logo_original_vector_available':False,'fox_traced_from_reference':True,
        'typeface':'Nimbus Roman; interpretation of reference, not an exact original vector',
        'nfc':False,'whatsapp':False,'physical_fit_tested':False,'physical_qr_scan_tested':False,
        'structural_load_or_push_tested':False,'fusion_runtime_tested':False}
    (FOLDER/'geometry.json').write_text(json.dumps({'units':'mm','parts':parts,'validation':report},ensure_ascii=False,indent=2)+'\n')
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    template=(ROOT/'fusion/M7TijoloV3/M7TijoloV3.py').read_text()
    template=template.replace('M7 - Tijolo Natal 2026 V3 - 7 pincelado','Clinica Essencial Arcos 220 mm')
    template=template.replace('M7 Tijolo V3 criado num documento novo.','Expositor Essencial 220 criado num documento novo.')
    template=template.replace('Tijolo: 50 x 26 x 70 mm, rebaixos 0,20 mm.','Conjunto: 220 x 80 x 220 mm; dois encaixes independentes.')
    template=template.replace('Use o projeto 3MF V3 de quatro pratos para imprimir.','Use o projeto 3MF Essencial Arcos 220 para imprimir.')
    (FOLDER/'EssencialArcos220.py').write_text(template)
    sample= v.rounded(-23,0,46,20,3).extrude(12)
    for y in (8.,13.2):
        sample-=v.rounded(-10.3,y-1.8,20.6,3.6,.3).extrude(8.1).translate((0,0,4))
    for x in (-13.,13.):
        grip=v.rounded(x-11.5,35.8,23,14,1)
        tab=v.rounded(x-10,28,20,8.2,.3)
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
    draw.text((35,25),'Clínica Essencial · projeto 220 mm',font=font(38),fill=v.BLUE)
    draw.text((35,82),'220 × 80 × 220 mm · Instagram + avaliações Google · sem NFC',font=font(27),fill=v.BLUE)
    draw.text((920,1020),'QR reais: campos de 64 × 64 mm',font=font(25),fill=v.BLUE)
    draw.text((920,1065),'Dois encaixes · folga de 0,2 mm por lado',font=font(25),fill=v.BLUE)
    draw.text((35,1130),'Geometria real · placas deitadas na impressão · nervuras fora das línguas de encaixe',font=font(25),fill=v.BLUE)
    draw.text((35,1170),'Encaixes, leitura física e estabilidade ao toque a confirmar no protótipo.',font=font(24),fill=v.BLUE)
    image.save(ROOT/'designs'/f'{PREFIX}-CAD.png')


if __name__=='__main__':main()
