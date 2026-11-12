"""Aquelá: trace the approved wolf/foliage, then build supported relief.

The approved illustration is the contour source, not an output preview.
All CAD previews below are rendered from the same solids exported to STL.
"""
from pathlib import Path
import hashlib
import json
import cv2
import manifold3d as md
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

from generate_coruja_bruna_v3 import exact, union
from generate_m7_prototypes_v1 import rounded
from generate_universo_stand import render_meshes

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/AnilhaAquelaV5'
PREFIX = 'anilha-aquela-v5'
SOURCE = ROOT / 'designs/anilha-escuteiros-v2-tres-pecas-dimensoes.png'
BLACK, GRAY, BROWN, WHITE, GREEN = '#202124', '#686C70', '#905532', '#F5F4ED', '#27853C'
COLORS = [BLACK, GRAY, BROWN, WHITE]
BASE = 2.48
CAP_THICKNESS = {BROWN: .48, GRAY: .48, WHITE: .72}


from generate_anilha_aquela_v2 import largest, tracer, cap
from generate_anilha_aquela_v3 import solid_from_mesh

SCALE_X = 52/62
SCALE_Y = 55/65
EDGE_MARGIN = .45
LETTER_WHITE_MM = 1.44
LETTER_FLOOR = 4.40-LETTER_WHITE_MM
WOLF_PROJECT = PREFIX+"-LOBO-A1-04-AMS-4-cores.3mf"

def wolf():
    rgb = np.array(Image.open(SOURCE).convert('RGB').crop((65, 133, 425, 490)))
    r, g, b = rgb.astype(float).transpose(2, 0, 1)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    fg = (gray < 130) & ~((b > r*1.3) & (b > g*1.05))
    fg[:2] = 0; fg[:, :4] = 0; fg[:, -4:] = 0
    fg, box = largest(fg)
    labels = np.zeros(fg.shape, 'uint8')
    labels[(gray > 57) & (fg > 0)] = 1
    labels[(r > g+15) & (r > b*1.35) & (gray > 52) & (fg > 0)] = 2
    labels[(gray > 170) & (fg > 0)] = 3
    for i in (1, 2, 3):
        mask = cv2.medianBlur((labels == i).astype('uint8'), 3)
        labels[labels == i] = 0
        labels[mask > 0] = i
    # Remove both added and original pupil glints. The old added right glint
    # was outside the pupil. Rebuild the small eye with a continuous white area.
    cv2.ellipse(labels, (217, 111), (5, 6), -20, 0, 360, 0, -1)
    eye_mask = np.zeros_like(fg)
    eye_points = np.array([(257,78),(262,75),(268,78),(274,85),
                          (280,97),(284,110),(280,114),(272,115),
                          (266,112),(261,106),(258,98),(255,87)])
    cv2.fillPoly(eye_mask, [eye_points], 1)
    eye_border = cv2.dilate(eye_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    labels[eye_border>0] = 0
    labels[eye_mask>0] = 3
    pupil_mask = np.zeros_like(fg)
    cv2.ellipse(pupil_mask, (276,104), (5,10), -22, 0, 360, 1, -1)
    labels[(pupil_mask>0)&(eye_mask>0)] = 0
    eye_roi=np.zeros_like(fg);eye_roi[65:117,250:291]=1
    labels[(eye_roi>0)&(eye_mask==0)&(labels==3)]=0
    # Gray tongue: no extra fifth filament for tiny warm shaded patches.
    labels[160:204][labels[160:204] == 2] = 1
    # Reuse the actual lettering. Remove the original accent above A and draw
    # an acute accent above the last a: Aquelá, not Áquela/Àquela.
    accent = np.zeros(fg.shape, 'uint8')
    accent[218:239, 72:102] = (labels[218:239, 72:102] == 3)
    _, components, stats, _ = cv2.connectedComponentsWithStats(accent)
    idx = 1 + np.argmax(stats[1:, 4])
    accent = (components == idx).astype('uint8')
    halo = cv2.dilate(accent, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
    halo[240:] = 0
    labels[halo > 0] = 2
    new_accent = np.zeros_like(accent)
    # A clear acute slope, with the same chunky lettering/rounded corners.
    cv2.fillPoly(new_accent, [np.array([(300, 253), (315, 239), (324, 245), (308, 258)])], 1)
    new_accent = cv2.medianBlur(new_accent, 3)
    new_halo = cv2.dilate(new_accent, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    labels[new_halo > 0] = 0
    labels[new_accent > 0] = 3
    # Remove shading artifacts from the wood without losing the irregular board.
    # The original letter outlines are rebuilt around the traced white letters.
    wood = (labels == 2).astype('uint8'); wood[:208] = 0
    wood = cv2.morphologyEx(wood, cv2.MORPH_CLOSE, np.ones((5, 5), 'uint8'))
    wood, _ = largest(wood)
    word = (labels == 3).astype('uint8'); word[:218] = 0
    word_outline = cv2.dilate(word, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    labels[wood > 0] = 2
    labels[(word_outline > 0) & (wood > 0)] = 0
    labels[word > 0] = 3
    # Reintroduce only broad wood creases visible in the source; exclude letters.
    grain = np.zeros_like(fg)
    for line in [((34, 224), (47, 222), (60, 224)),
                 ((25, 246), (43, 248), (53, 248)),
                 ((140, 248), (178, 251), (217, 248)),
                 ((297, 237), (316, 239), (337, 244)),
                 ((24, 282), (36, 283), (43, 284)),
                 ((31, 327), (47, 330), (78, 332)),
                 ((175, 342), (211, 344), (252, 343)),
                 ((307, 331), (325, 328), (338, 324))]:
        cv2.polylines(grain, [np.array(line)], False, 1, 2, cv2.LINE_8)
    letters_clearance = cv2.dilate(word_outline, np.ones((5, 5), 'uint8'))
    labels[(grain > 0) & (labels == 2) & (letters_clearance == 0)] = 0
    labels[fg == 0] = 0
    # Trace the original board edge, not the fat text shadows. Everything
    # below the word is part of the board, including the old stray gray lines.
    board_mask = cv2.dilate(wood, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    board_mask[240:] = fg[240:]
    board_mask &= fg
    board_mask,_ = largest(board_mask)
    to_section = tracer(box, 55*SCALE_X, 65*SCALE_Y)
    silhouette = to_section(fg,100)
    board = to_section(board_mask,100)^silhouette
    face = silhouette-board
    sections={};used=md.CrossSection()
    for i,c in ((3,WHITE),(2,BROWN),(1,GRAY)):
        region=to_section(labels==i,5)^silhouette.offset(-.12,circular_segments=16)
        region-=used
        sections[c]=region;used+=region
    eye=to_section(eye_mask)^sections[WHITE]
    main_eye=max(eye.decompose(),key=lambda s:s.area())
    eye_specks=eye-main_eye
    sections[WHITE]-=eye_specks
    used-=eye_specks
    sections[BLACK]=silhouette-used
    # The pelt touches the top of the board in the source drawing. Do not
    # mistake sub-millimetre slivers at that boundary for detached lettering.
    letters=md.CrossSection()
    for part in (sections[WHITE]^board).decompose():
        bounds=part.bounds()
        if part.area()>2 and bounds[3]-bounds[1]>1:
            letters+=part
    assert len(letters.decompose())==7  # A q u e l a and the acute accent
    # The plaque has no gray and NO black letter outlines or backing. Brown
    # is the structural substrate, white is 1.44 mm deep at each letter.
    rim=(board-board.offset(-.42,md.JoinType.Round,circular_segments=16))-letters.offset(.35)
    grain_section=to_section(grain,1).offset(.12,md.JoinType.Round,circular_segments=16)
    grain_section=(grain_section^board.offset(-.65))-letters.offset(.65)
    ink=rim+grain_section
    body={c:md.Manifold() for c in COLORS}
    body[BROWN]=silhouette.extrude(BASE)
    body[BROWN]+=(board-letters-ink).extrude(3.20-BASE).translate((0,0,BASE))
    body[BROWN]+=letters.extrude(LETTER_FLOOR-BASE).translate((0,0,BASE))
    body[WHITE]=cap(letters,LETTER_FLOOR,4.40,.06)
    body[BLACK]=cap(ink,BASE,3.20,.04)
    heights={BROWN:3.20,GRAY:3.80,WHITE:4.40}
    for c in (BROWN,GRAY,WHITE):
        section=sections[c]^face
        if section.area()<1e-7:
            continue
        floor=heights[c]-CAP_THICKNESS[c]
        body[BLACK]+=section.extrude(floor-BASE).translate((0,0,BASE))
        body[c]+=cap(section,floor,heights[c])
    body[BLACK]+=cap(sections[BLACK]^face,BASE,4.16,.09)
    nose_mask=np.zeros_like(fg)
    cv2.fillPoly(nose_mask,[np.array([(287,112),(303,106),(327,102),(333,108),
                                    (330,127),(322,136),(306,136),(289,125)])],1)
    nose=to_section(nose_mask)^sections[BLACK]^face
    body[BLACK]+=cap(nose,4.04,4.88,.25)
    assert all(s.status()==md.Error.NoError for s in body.values())
    body={c:union(p for p in s.decompose() if p.volume()>1e-7) for c,s in body.items()}
    whole=union(body.values())
    assert len([p for p in whole.decompose() if p.volume()>1e-7])==1
    assert all((body[a]^body[b]).volume()<.001 for i,a in enumerate(body) for b in list(body)[i+1:])
    assert (body[GRAY]^board.extrude(6)).volume()<.001
    assert (body[BLACK]^letters.extrude(6)).volume()<.001
    assert (letters-body[BROWN].slice(LETTER_FLOOR-.02)).area()<.001
    assert (body[WHITE].slice(LETTER_FLOOR+.02)^letters).area()>.99*letters.area()
    eye=to_section(eye_mask)^sections[WHITE]
    assert len([p for p in eye.decompose() if p.area()>.001])==1
    return body,silhouette,{'board':board,'letters':letters,'right_eye_white':main_eye,
                             'right_pupil':to_section(pupil_mask)^to_section(eye_mask)}


def foliage(badge):
    rgb=np.array(Image.open(SOURCE).convert('RGB').crop((550,178,1010,442)))
    r,g,b=rgb.astype(float).transpose(2,0,1)
    fg,box=largest((g>r*1.35)&(g>b*1.15)&(g>35))
    trace=tracer(box,62*SCALE_X,48*SCALE_Y)
    outline=trace(fg,100)
    dark=cv2.medianBlur(((g<108)&(fg>0)).astype('uint8'),3)
    veins=trace(dark,6).offset(.12,md.JoinType.Round,circular_segments=16)
    rim=outline-outline.offset(-.48,md.JoinType.Round,circular_segments=16)
    hidden=badge.offset(-EDGE_MARGIN,md.JoinType.Round,circular_segments=24)^outline
    ink=((veins+rim)^outline)-hidden
    green_face=outline-ink
    exposed=outline-badge.offset(.20,md.JoinType.Round,circular_segments=16)
    green=outline.extrude(1.52)+green_face.extrude(.48).translate((0,0,1.52))
    green+=cap(green_face^exposed,2.0,2.96,.08)
    black=ink.extrude(.48).translate((0,0,1.52))
    black+=(ink^exposed).extrude(.72).translate((0,0,2.0))
    bodies={GREEN:green,BLACK:black}
    whole=union(bodies.values())
    assert len([p for p in whole.decompose() if p.volume()>1e-7])==1
    assert (green^black).volume()<.001
    assert (black^hidden.extrude(4)).volume()<.001
    assert (black.slice(1.6)-green.slice(1.5)).area()<.001
    assert (hidden-green.slice(1.99)).area()<.001
    assert (hidden^whole.slice(2.01)).area()<.001
    return bodies,outline,hidden


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    body,badge,masks=wolf()
    leaves,outline,hidden=foliage(badge)
    ring_file=ROOT/'downloads/anilha-aquela-v2-anilha-castanha.stl'
    ring=solid_from_mesh(ring_file)
    ring_pose=np.array([[1,0,0,0],[0,0,1,7.8],[0,-1,0,-11],[0,0,0,1]],float)
    badge_pose=np.eye(4);badge_pose[2,3]=2.0
    parts=[];scene=[]
    def add(key,solid,color,piece,pose,reused=None):
        path=reused or ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh=trimesh.load(path,force='mesh') if reused else exact(solid,path)
        parts.append({'key':key,'file':path.name,'color':color,'piece':piece,
                      'assembly':pose.tolist(),'dimensions_mm':mesh.extents.tolist(),
                      'volume_mm3':mesh.volume,'watertight':bool(mesh.is_watertight),
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        scene.append((solid.transform(pose[:3].tolist()),color))
    add('anilha-castanha',ring,BROWN,'anilha',ring_pose,ring_file)
    for key,c in [('folhas-verdes',GREEN),('folhas-nervuras-pretas',BLACK)]:
        add(key,leaves[c],c,'folhas',np.eye(4))
    for key,c in [('preto',BLACK),('cinzento',GRAY),('castanho',BROWN),('branco',WHITE)]:
        add('lobo-'+key,body[c],c,'lobo',badge_pose)
    front=exact(union(body.values()),ROOT/'downloads'/f'{PREFIX}-lobo-completo-monocor.stl')
    leaf=exact(union(leaves.values()),ROOT/'downloads'/f'{PREFIX}-folhas-completas-monocor.stl')
    assert np.allclose(front.extents,[55*SCALE_X,55,4.88],atol=.02)
    assert np.allclose(leaf.extents,[52,48*SCALE_Y,2.96],atol=.02)
    intersections=[]
    for i,(a,_) in enumerate(scene):
        for j,(b,_) in enumerate(scene[i+1:],i+1):
            v=(a^b).volume()
            if v>.003:intersections.append([parts[i]['key'],parts[j]['key'],v])
    assert not intersections,intersections
    # Contact has area, rather than a coincident point/edge. The ring's rear
    # flat wall contacts the leaf at Z=0; the front sits on the Z=2 glue face.
    ring_contact=scene[0][0].slice(-.01)^outline
    wolf_contact=badge^union(leaves.values()).slice(1.99)
    assert ring_contact.area()>400 and wolf_contact.area()>900
    assert (badge^union(leaves.values()).slice(2.01)).area()<.001
    glb=trimesh.Scene()
    for p in parts:
        m=trimesh.load(ROOT/'downloads'/p['file'],force='mesh')
        m.apply_transform(p['assembly'])
        m.visual.face_colors=[int(p['color'][i:i+2],16) for i in (1,3,5)]+[255]
        glb.add_geometry(m,node_name=p['key'])
    glb.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    # Export region contours for independent toolpath checks, not just renders.
    regions={k:[np.asarray(poly).tolist() for poly in v.to_polygons()] for k,v in masks.items()}
    regions['hidden_leaf']=[np.asarray(poly).tolist() for poly in hidden.to_polygons()]
    (FOLDER/'validation-regions.json').write_text(json.dumps(regions,indent=2)+'\n')
    report={'title':'Aquelá V5 — menor, letras sem contorno e olho simplificado',
            'source':str(SOURCE.relative_to(ROOT)),
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'reused_unchanged_sha256':{ring_file.name:hashlib.sha256(ring_file.read_bytes()).hexdigest()},
            'wolf_project':WOLF_PROJECT,'physical_parts_count':3,
            'visible_dimensions_mm':[52,55],
            'dimension_interpretation':'10 mm less in each dimension of the visible assembly (62x65 to 52x55)',
            'front_dimensions_mm':front.extents.tolist(),'foliage_dimensions_mm':leaf.extents.tolist(),
            'xy_scale':[SCALE_X,SCALE_Y],'z_scale':1,'ring_outer_mm':[29,22,25],
            'ring_clear_opening_mm':[25,18],'ring_bottom_y_mm':7.8,
            'flat_glue_face_z_mm':2.0,'ring_glue_contact_area_mm2':ring_contact.area(),
            'wolf_glue_contact_area_mm2':wolf_contact.area(),
            'letter_white_thickness_mm':LETTER_WHITE_MM,'letter_white_start_z_mm':LETTER_FLOOR,
            'letter_black_outline':False,'letter_black_backing_volume_mm3':(body[BLACK]^masks['letters'].extrude(6)).volume(),
            'gray_on_plaque_volume_mm3':(body[GRAY]^masks['board'].extrude(6)).volume(),
            'pupil_highlights':False,'right_eye_white_connected':True,
            'hidden_leaf_black_volume_mm3':(leaves[BLACK]^hidden.extrude(4)).volume(),
            'edge_margin_under_wolf_mm':EDGE_MARGIN,'assembly_intersections':intersections,
            'parts':parts,'physical_print_tested':False,'physical_fit_tested':False}
    (FOLDER/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    stand=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    upright=[(s.transform(stand[:3].tolist()),c) for s,c in scene]
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    sheet=Image.new('RGB',(1600,1100),'#f4f6f8');d=ImageDraw.Draw(sheet)
    d.text((35,25),'Aquelá V5 · geometria real para impressão',font=font(34),fill='#23384C')
    sheet.paste(render_meshes(upright,(780,850),direction=(0,-1,0),margin=35),(0,100))
    sheet.paste(render_meshes(upright,(780,850),direction=(.55,-1,.25),margin=35),(810,100))
    d.text((35,965),'Conjunto 52 × 55 mm · passagem do lenço 25 × 18 mm mantida',font=font(27),fill='#23384C')
    d.text((35,1010),'Letras sem contorno nem base preta · branco 1,44 mm · olho sem brilhos',font=font(26),fill='#23384C')
    d.text((35,1050),'3 peças para colar · folhas ajustadas · impressão e encaixe físicos por testar',font=font(24),fill='#536276')
    sheet.save(ROOT/'designs'/f'{PREFIX}-montada-CAD.png')
    print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2),flush=True)


if __name__=='__main__':main()
