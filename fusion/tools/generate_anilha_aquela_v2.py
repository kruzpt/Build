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
FOLDER = ROOT / 'fusion/AnilhaAquelaV2'
PREFIX = 'anilha-aquela-v2'
SOURCE = ROOT / 'designs/anilha-escuteiros-v2-tres-pecas-dimensoes.png'
BLACK, GRAY, BROWN, WHITE, GREEN = '#202124', '#686C70', '#905532', '#F5F4ED', '#27853C'
COLORS = [BLACK, GRAY, BROWN, WHITE]
BASE = 2.48
CAP_THICKNESS = {BROWN: .48, GRAY: .48, WHITE: .72}


def largest(mask):
    contours, _ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    result = np.zeros(mask.shape, 'uint8')
    cv2.drawContours(result, [contour], -1, 1, -1)
    return result, cv2.boundingRect(contour)


def tracer(box, width, height):
    x, y, w, h = box
    def section(mask, min_area=4):
        contours, hierarchy = cv2.findContours(mask.astype('uint8'), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        loops = []
        if hierarchy is None:
            return md.CrossSection()
        for i, contour in enumerate(contours):
            if cv2.contourArea(contour) < min_area:
                continue
            parent = hierarchy[0, i, 3]
            if parent >= 0 and cv2.contourArea(contours[parent]) < min_area:
                continue
            points = cv2.approxPolyDP(contour, .45, True)[:, 0, :].astype(float)
            if len(points) < 3:
                continue
            # Two Chaikin passes remove pixel stairs, retaining the source shape.
            for _ in range(2):
                nxt = np.roll(points, -1, axis=0)
                points = np.stack((.75*points+.25*nxt, .25*points+.75*nxt), axis=1).reshape((-1, 2))
            points[:, 0] = (points[:, 0]-x-(w-1)/2)*width/(w-1)
            points[:, 1] = (y+h-1-points[:, 1])*height/(h-1)
            loops.append(points)
        return md.CrossSection(loops, md.FillRule.EvenOdd).simplify(.008)
    return section


def cap(section, bottom, top, bevel=.12):
    """Supported colored cap with a small, printable inward edge bevel."""
    body = section.extrude(top-bottom-.12).translate((0, 0, bottom))
    for i in range(3):
        inner = section.offset(-bevel*(i+1)/3, md.JoinType.Round, circular_segments=16)
        body += inner.extrude(.04).translate((0, 0, top-.12+i*.04))
    return body


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
    # The original tiny highlights disappear in 0.4 mm nozzle paths. Enlarge
    # them locally, preserving the pupil positions and the expression.
    highlights = np.zeros_like(fg)
    cv2.circle(highlights, (217, 110), 4, 1, -1)
    cv2.circle(highlights, (284, 104), 4, 1, -1)
    labels[highlights > 0] = 3
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
    to_section = tracer(box, 55, 65)
    silhouette = to_section(fg, 100)
    # All material regions are subsets of the silhouette and mutually disjoint.
    sections = {}; used = md.CrossSection()
    for i, c in ((3, WHITE), (2, BROWN), (1, GRAY)):
        section = to_section(labels == i, 5) ^ silhouette.offset(-.15, circular_segments=16)
        section -= used
        sections[c] = section; used += section
    sections[BLACK] = silhouette-used
    body = {BLACK: silhouette.extrude(BASE)}
    heights = {BROWN: 3.20, GRAY: 3.80, WHITE: 4.40}
    for c in (BROWN, GRAY, WHITE):
        floor = heights[c]-CAP_THICKNESS[c]
        body[BLACK] += sections[c].extrude(floor-BASE).translate((0, 0, BASE))
        body[c] = cap(sections[c], floor, heights[c])
    # Black framing at the appropriate height, including the eyes and smile.
    board_box = md.CrossSection.square((100, 25)).translate((-50, 0))
    letters = sections[WHITE] ^ board_box
    letter_outline = letters.offset(.7, md.JoinType.Round, circular_segments=16) ^ sections[BLACK]
    low_black = (sections[BLACK] ^ board_box)-letter_outline
    high_black = sections[BLACK]-low_black
    body[BLACK] += low_black.extrude(3.08-BASE).translate((0, 0, BASE))
    body[BLACK] += cap(high_black, BASE, 4.16, .09)
    # Nose is visibly forward of the muzzle, as in the approved drawing.
    nose_mask = np.zeros_like(fg)
    cv2.fillPoly(nose_mask, [np.array([(287, 112), (303, 106), (327, 102), (333, 108),
                                     (330, 127), (322, 136), (306, 136), (289, 125)])], 1)
    nose = to_section(nose_mask) ^ sections[BLACK]
    body[BLACK] += cap(nose, 4.04, 4.88, .25)
    body = {c: union(p for p in s.decompose() if p.volume() > 1e-7) for c, s in body.items()}
    whole = union(body.values())
    assert len([p for p in whole.decompose() if p.volume() > 1e-7]) == 1
    assert all((body[a] ^ body[b]).volume() < .001 for i, a in enumerate(body) for b in list(body)[i+1:])
    # The silhouette matches the traced illustration, rather than a substitute.
    return body, silhouette, heights, labels, fg


def foliage(badge_section):
    rgb = np.array(Image.open(SOURCE).convert('RGB').crop((550, 178, 1010, 442)))
    r, g, b = rgb.astype(float).transpose(2, 0, 1)
    fg, box = largest((g > r*1.35) & (g > b*1.15) & (g > 35))
    to_section = tracer(box, 62, 48)
    outline = to_section(fg, 100)
    bright = cv2.medianBlur(((g >= 108) & (fg > 0)).astype('uint8'), 3)
    blades = to_section(bright, 15) ^ outline.offset(-.20, circular_segments=16)
    # Broad flat gluing face behind the badge; raised veins never intersect it.
    exposed = outline-badge_section.offset(.20, md.JoinType.Round, circular_segments=16)
    raised = blades ^ exposed
    body = outline.extrude(2.0)
    # Stepped inward borders give the leaves relief and retain the source veins.
    body += cap(exposed, 2.0, 2.48, .10)
    body += cap(raised, 2.36, 2.96, .18)
    assert len(body.decompose()) == 1
    return body, outline


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    body, silhouette, heights, labels, fg = wolf()
    leaves, leaf_section = foliage(silhouette)
    ring = (rounded(-14.5, -11, 29, 22, 3)-rounded(-12.5, -9, 25, 18, 2.1)).extrude(25)
    parts = []; scene = []
    ring_pose = np.array([[1, 0, 0, 0], [0, 0, 1, 9], [0, -1, 0, -11], [0, 0, 0, 1]], float)
    badge_pose = np.eye(4); badge_pose[2, 3] = 2.0
    def add(key, solid, color, piece, pose):
        target = ROOT/'downloads'/f'{PREFIX}-{key}.stl'
        mesh = exact(solid, target)
        parts.append({'key': key, 'file': target.name, 'color': color, 'piece': piece,
                      'assembly': pose.tolist(), 'dimensions_mm': mesh.extents.tolist(),
                      'volume_mm3': mesh.volume, 'watertight': True,
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        scene.append((solid.transform(pose[:3].tolist()), color))
    add('anilha-castanha', ring, BROWN, 'anilha', ring_pose)
    add('folhas-verdes', leaves, GREEN, 'folhas', np.eye(4))
    for key, c in [('preto', BLACK), ('cinzento', GRAY), ('castanho', BROWN), ('branco', WHITE)]:
        add(f'lobo-{key}', body[c], c, 'lobo', badge_pose)
    front = union(body.values())
    mesh = exact(front, ROOT/'downloads'/f'{PREFIX}-lobo-completo-monocor.stl')
    intersections = []
    for i, (a, _) in enumerate(scene):
        for j, (b, _) in enumerate(scene[i+1:], i+1):
            volume = (a ^ b).volume()
            if volume > .003: intersections.append([parts[i]['key'], parts[j]['key'], volume])
    assert not intersections, intersections
    assert np.allclose(mesh.extents[:2], [55, 65], atol=.2)
    # At every occupied XY position, extruded material rests on solid backing.
    for c in (BROWN, GRAY, WHITE):
        floor = heights[c]-CAP_THICKNESS[c]
        overhang = body[c].slice(floor+.02)-body[BLACK].slice(floor-.02).offset(.01)
        assert overhang.area() < .002, (c, overhang.area())
    data = {'title': 'Aquelá V2 — contornos recuperados da referência aprovada',
            'name': 'Aquelá', 'source': str(SOURCE.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'construction': 'Three separate physical pieces, joined by flat glue faces.',
            'model_type': 'traced contour relief with stepped height and small beveled edges',
            'detail_limit': 'image grain removed; four printable face colors; no photoreal fur/wood texture',
            'front_dimensions_mm': mesh.extents.tolist(), 'front_base_mm': BASE,
            'color_caps_mm': CAP_THICKNESS, 'surface_heights_mm': heights,
            'foliage_max_thickness_mm': 2.96,
            'ring_outer_mm': [29, 22, 25], 'ring_clear_opening_mm': [25, 18],
            'parts_count': 3, 'body_connected': True, 'foliage_connected': True,
            'supported_color_caps': True, 'assembly_intersections': intersections,
            'physical_print_tested': False, 'physical_fit_tested': False,
            'parts': parts}
    (FOLDER/'geometry.json').write_text(json.dumps(data, indent=2)+'\n')
    glb = trimesh.Scene()
    for p in parts:
        m = trimesh.load(ROOT/'downloads'/p['file'], force='mesh')
        m.apply_transform(p['assembly'])
        m.visual.face_colors = [int(p['color'][i:i+2], 16) for i in (1, 3, 5)]+[255]
        glb.add_geometry(m, node_name=p['key'])
    glb.export(ROOT/'downloads'/f'{PREFIX}-montada.glb')
    stand = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    upright = [(s.transform(stand[:3].tolist()), c) for s, c in scene]
    front_scene = [(s.transform(stand[:3].tolist()), c) for c, s in body.items()]
    font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
    sheet = Image.new('RGB', (1800, 1100), '#f4f6f8'); d = ImageDraw.Draw(sheet)
    d.text((40, 25), 'Aquelá V2 · vistas da geometria real', font=font(36), fill='#23384C')
    sheet.paste(render_meshes(upright, (870, 850), direction=(0, -1, 0), margin=35), (10, 100))
    sheet.paste(render_meshes(upright, (870, 850), direction=(.6, -1, .3), margin=35), (910, 100))
    d.text((40, 970), '3 peças: anilha + folhas numa peça + lobo/tabuleta · montagem por colagem', font=font(26), fill='#23384C')
    d.text((40, 1020), 'Frente 55 × 65 × 4,88 mm · folhas 62 × 48 × 2,96 mm · interior da anilha 25 × 18 mm', font=font(25), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    sheet = Image.new('RGB', (1800, 1020), '#f4f6f8'); d = ImageDraw.Draw(sheet)
    d.text((35, 25), 'Aquelá V2 · as três peças separadas', font=font(35), fill='#23384C')
    sheet.paste(render_meshes(front_scene, (700, 810), direction=(0, -1, .08), margin=30), (0, 90))
    sheet.paste(render_meshes([upright[1]], (620, 610), direction=(.15, -1, .15), margin=35), (700, 170))
    sheet.paste(render_meshes([(ring, BROWN)], (470, 590), direction=(.65, -1, .65), margin=35), (1320, 180))
    d.text((40, 925), 'Lobo e tabuleta: 4 cores', font=font(27), fill='#23384C')
    d.text((740, 830), 'Folhas: peça única verde', font=font(26), fill='#23384C')
    d.text((1340, 830), 'Anilha castanha', font=font(26), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-pecas.png')
    # Reference comparison explicitly distinguishes illustration from real CAD.
    sheet = Image.new('RGB', (1450, 950), '#f4f6f8'); d = ImageDraw.Draw(sheet)
    source = Image.open(SOURCE).crop((65, 133, 425, 490)).resize((640, 650))
    sheet.paste(source, (35, 130))
    sheet.paste(render_meshes(front_scene, (700, 720), direction=(0, -1, 0), margin=30), (730, 95))
    d.text((35, 30), 'Referência aprovada', font=font(32), fill='#23384C')
    d.text((765, 30), 'Modelo V2 exportado', font=font(32), fill='#23384C')
    d.text((35, 835), 'Contornos e expressão recuperados · nome corrigido para Aquelá', font=font(27), fill='#23384C')
    d.text((35, 885), 'Textura fina simplificada; relevo em alturas imprimíveis. Imagens à mesma altura visual.', font=font(22), fill='#23384C')
    sheet.save(ROOT/'designs'/f'{PREFIX}-comparacao.png')
    print(json.dumps({k: v for k, v in data.items() if k != 'parts'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
