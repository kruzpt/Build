"""Clínica Essencial v4 — two printable parts. All dimensions in mm.

Run in Autodesk Fusion: Utilities > Scripts and Add-Ins > Scripts.
Creates a NEW document, with the parts separated in their own components.
"""
import math
import traceback
import adsk.core
import adsk.fusion

INSTAGRAM_ROWS = [
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
    '000011111110100111111001000111100011111110000',
    '000010000010111001100111011000100010000010000',
    '000010111010011011010110010010101010111010000',
    '000010111010011100111000010011011010111010000',
    '000010111010011011000101110100000010111010000',
    '000010000010001000101111010000001010000010000',
    '000011111110101010101010101010101011111110000',
    '000000000000000111101001001010111000000000000',
    '000001000011100110000010001010000100000110000',
    '000000110000110011000100111101000001111000000',
    '000011110110001000000011011001100011010110000',
    '000000100100101111001011100100111010010000000',
    '000010111010111100101111110010001011000000000',
    '000011101100110110110000011110111101001100000',
    '000001111110011101011101101001011011010110000',
    '000001010100100100000110111100011000111100000',
    '000001110010010000111101111011110111101010000',
    '000001011001101110110101010001010001010000000',
    '000000000011101001010101111010010010011010000',
    '000001101000011111100000101100001111010100000',
    '000010000111101110000100101111100111111010000',
    '000000111100010000111000011101111101100100000',
    '000010101111010011100100111001110100000110000',
    '000001100000101000100000000011010011010110000',
    '000001011010110000011001100011001111010010000',
    '000011100100110100110101010110000001010000000',
    '000010111110111011010110001001111010100110000',
    '000010110000001011101110100000010100111110000',
    '000010111010011110000010101101101111111000000',
    '000000000000101111011110001101111000110100000',
    '000011111110110111100100111100001010111010000',
    '000010000010001010000000001100111000110000000',
    '000010111010010001110101010001111111101100000',
    '000010111010010101001100000010110010001100000',
    '000010111010011000101011000001010101000010000',
    '000010000010100011110101101010101011110010000',
    '000011111110011101010000100110001011110010000',
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
    '000000000000000000000000000000000000000000000',
]

GOOGLE_ROWS = [
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
    '00001111111001110100000011101011111110000',
    '00001000001000011000011011001010000010000',
    '00001011101001111001001001110010111010000',
    '00001011101011000001001111101010111010000',
    '00001011101000101111011110010010111010000',
    '00001000001011110100010011101010000010000',
    '00001111111010101010101010101011111110000',
    '00000000000010010001100000011000000000000',
    '00000110001001001011000110001011010000000',
    '00001110010110110100001100011010010110000',
    '00000111001111100000011100011110011110000',
    '00000100100110100011101010110011110110000',
    '00000001111111011010111111111010000000000',
    '00000111010110000011111010001001010110000',
    '00001011111000001110010010010001000010000',
    '00001001100111101000001110110111010000000',
    '00001010111001001010101010000011000100000',
    '00000111100000100101100111011110010010000',
    '00001000001110111011101110010001011010000',
    '00001111000011000111101011000110110110000',
    '00000000101000111001111001011111100010000',
    '00000011000100111111001001011111010010000',
    '00001110001111000000001100010111011010000',
    '00000010010000111011001000101110100010000',
    '00001101111010011001010110011111100010000',
    '00000000000010100001011110001000100010000',
    '00001111111001100011001101101010111010000',
    '00001000001001111100101110111000110000000',
    '00001011101001100000111111111111100100000',
    '00001011101001011010111011100101101010000',
    '00001011101010010110110010010101111110000',
    '00001000001010001001000110111101110000000',
    '00001111111000111101000010001001101010000',
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
    '00000000000000000000000000000000000000000',
]

PANEL_WIDTH = 200.0
PANEL_HEIGHT = 220.0
PANEL_THICKNESS = 5.0
LOGO_RADIUS = 38.0
LOGO_X = 28.0
LOGO_Y = PANEL_HEIGHT
TONGUE_WIDTH = 120.0
TONGUE_DEPTH = 12.0
FIT_CLEARANCE_PER_SIDE = 0.25
END_CLEARANCE_PER_SIDE = 0.30
BOTTOM_CLEARANCE = 0.8
ENTRY_EXTRA_PER_SIDE = 0.5
ENTRY_DEPTH = 1.0
BASE_WIDTH = 160.0
BASE_DEPTH = 70.0
BASE_HEIGHT = 18.0
SPINE_RELIEF = 2.4
SPINE_X_OFFSET = 20.0
DISC_GAP = 1.0
NFC_TAG_DIAMETER = 25.0
NFC_CAVITY_DIAMETER = 25.8
NFC_CAVITY_FLOOR_Z = 3.0
NFC_CAVITY_HEIGHT = 0.8
NFC_PAUSE_Z = NFC_CAVITY_FLOOR_Z+NFC_CAVITY_HEIGHT
QR_SIZE = 64.0
QR_X = 49.0
ICON_X = 27.0
NFC_X = 133.0
EMBOSS_TEXT = True


def vertebra_layout():
    """Bottom to top: 5 lumbar, 12 thoracic, 7 cervical vertebrae."""
    result = []
    bottom = 44.0
    groups = [('L', 5, 7.7, 11.0), ('T', 12, 5.3, 8.5),
              ('C', 7, 4.4, 6.4)]
    for region, count, height, width in groups:
        for index in range(count):
            taper = 1.0 - 0.12 * index / max(1, count - 1)
            y = bottom + height / 2
            x = SPINE_X_OFFSET + 145.0 + 5.0 * math.sin((y - 44.0) / 154.0 * 2 * math.pi)
            result.append((region, count-index, x, y, width*taper, height))
            bottom += height + DISC_GAP
    return result



def sample_path(commands, steps=12):
    vertices = []
    for command in commands:
        if command[0] in ('M', 'L'):
            vertices.append((command[1], command[2]))
        elif command[0] == 'C':
            x0, y0 = vertices[-1]
            x1, y1, x2, y2, x3, y3 = command[1:]
            for i in range(1, steps+1):
                t = i/steps
                u = 1-t
                vertices.append((u**3*x0+3*u*u*t*x1+3*u*t*t*x2+t**3*x3,
                                 u**3*y0+3*u*u*t*y1+3*u*t*t*y2+t**3*y3))
    if vertices[-1] == vertices[0]:
        vertices.pop()
    return vertices


def logo_contours():
    e = sample_path([
        ('M',263,200), ('L',804,200), ('L',804,333),
        ('C',792,266,761,223,689,223), ('L',411,223), ('L',411,875),
        ('L',690,875), ('C',766,875,805,841,818,773),
        ('L',818,895), ('L',263,895),
        ('C',302,881,321,853,321,808), ('L',321,648),
        ('C',321,604,343,579,380,569),
        ('C',342,562,321,540,321,502), ('L',321,295),
        ('C',321,252,301,218,263,200)])
    small = sample_path([
        ('M',488,322), ('C',487,355,470,381,435,387),
        ('C',468,391,482,417,486,452),
        ('C',491,416,504,395,537,387),
        ('C',505,382,490,358,488,322)])
    large = sample_path([
        ('M',594,441), ('C',590,511,553,558,487,570),
        ('C',552,582,585,629,594,700),
        ('C',604,632,642,581,707,570),
        ('C',638,557,602,510,594,441)])
    scale = LOGO_RADIUS/540
    return [[(LOGO_X+(x-540)*scale, LOGO_Y+(540-y)*scale)
             for x,y in contour] for contour in (e,small,large)]


def qr_runs(rows):
    for row, values in enumerate(rows):
        start = None
        for col,value in enumerate(values+'0'):
            if value == '1' and start is None:
                start = col
            elif value == '0' and start is not None:
                yield row,start,col
                start = None


def sector_contour(cx,cy,radius,stroke,start,end,segments=32):
    angles = [math.radians(start+(end-start)*i/segments)
              for i in range(segments+1)]
    outer = [(cx+(radius+stroke/2)*math.cos(a),
              cy+(radius+stroke/2)*math.sin(a)) for a in angles]
    inner = [(cx+(radius-stroke/2)*math.cos(a),
              cy+(radius-stroke/2)*math.sin(a)) for a in reversed(angles)]
    return outer+inner


def row_layout():
    return [('Instagram', INSTAGRAM_ROWS, 81.0), ('Google', GOOGLE_ROWS, 4.0)]


class BuildCancelled(Exception):
    pass


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    progress = None
    current_stage = 'Preparing'
    try:
        if FIT_CLEARANCE_PER_SIDE < 0 or END_CLEARANCE_PER_SIDE < 0:
            raise ValueError('Fit clearances cannot be negative.')
        slot_depth = TONGUE_DEPTH + BOTTOM_CLEARANCE
        if slot_depth >= BASE_HEIGHT:
            raise ValueError('Base must have a solid floor below the slot.')
        if TONGUE_WIDTH >= PANEL_WIDTH - 16:
            raise ValueError('Leave shoulders on both sides of the tongue.')
        if not 0 < ENTRY_DEPTH < slot_depth:
            raise ValueError('Invalid entry depth.')
        if NFC_CAVITY_DIAMETER <= NFC_TAG_DIAMETER:
            raise ValueError('Tag cavity requires clearance.')
        if NFC_CAVITY_FLOOR_Z <= 0 or NFC_CAVITY_HEIGHT <= 0:
            raise ValueError('NFC cavity requires a solid floor and space.')
        if PANEL_THICKNESS-NFC_PAUSE_Z < 1.0:
            raise ValueError('Keep at least 1 mm of plastic above the tag.')

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = True
        progress.cancelButtonText = 'Cancel'
        progress.show('Clinica Essencial V4', 'Preparing (%p%)', 0, 100, 0)

        def update_progress(value, message):
            nonlocal current_stage
            current_stage = message
            progress.progressValue = value
            progress.message = message+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:
                raise BuildCancelled()

        update_progress(1, 'Creating components')
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        ops = adsk.fusion.FeatureOperations
        warnings = []

        # These parameters record the fit dimensions. Edit the constants above
        # and rerun to regenerate; all other geometry is dimensioned by Python.
        for name, value, description in [
            ('panelThickness', PANEL_THICKNESS, 'Plate and tongue thickness'),
            ('fitPerSide', FIT_CLEARANCE_PER_SIDE, 'Fit clearance on each side'),
            ('slotWidth', PANEL_THICKNESS + 2*FIT_CLEARANCE_PER_SIDE,
             'Slot throat width'),
            ('tongueDepth', TONGUE_DEPTH, 'Insertion length'),
            ('bottomClearance', BOTTOM_CLEARANCE, 'Space below inserted tongue')]:
            design.userParameters.add(name, adsk.core.ValueInput.createByReal(
                value / 10), 'mm', description)

        def point(x, y, z=0):
            return adsk.core.Point3D.create(x/10, y/10, z/10)

        def component(name):
            c = root.occurrences.addNewComponent(
                adsk.core.Matrix3D.create()).component
            c.name = name
            return c

        plate_component = component('01 - Plate and spine')
        base_component = component('02 - Slotted base')

        def sketch(c, name, z=0):
            plane = c.xYConstructionPlane
            if z:
                inp = c.constructionPlanes.createInput()
                inp.setByOffset(plane, adsk.core.ValueInput.createByReal(z/10))
                plane = c.constructionPlanes.add(inp)
            sk = c.sketches.add(plane)
            sk.name = name
            sk.isVisible = False
            sk.isComputeDeferred = True
            return sk

        def extrude(c, sk, name, depth):
            sk.isComputeDeferred = False
            if sk.profiles.count != 1:
                raise RuntimeError(name + ': expected one closed profile')
            feature = c.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), adsk.core.ValueInput.createByReal(depth/10),
                ops.NewBodyFeatureOperation)
            sk.isVisible = False
            body = feature.bodies.item(0)
            body.name = name
            return body

        def polygon(c, name, vertices, z, depth):
            sk = sketch(c, name, z)
            for a, b in zip(vertices, vertices[1:]+vertices[:1]):
                sk.sketchCurves.sketchLines.addByTwoPoints(point(*a), point(*b))
            return extrude(c, sk, name, depth)

        def rectangle(c, name, x, y, w, h, z, depth):
            return polygon(c, name, [(x,y), (x+w,y), (x+w,y+h), (x,y+h)],
                           z, depth)

        def rounded_rectangle(c, name, x, y, w, h, radius, z, depth):
            r = min(radius, w/2-0.01, h/2-0.01)
            sk = sketch(c, name, z)
            lines = sk.sketchCurves.sketchLines
            arcs = sk.sketchCurves.sketchArcs
            # A counterclockwise closed contour with tangent quarter circles.
            segments = [((x+r,y),(x+w-r,y)),
                        ((x+w,y+r),(x+w,y+h-r)),
                        ((x+w-r,y+h),(x+r,y+h)),
                        ((x,y+h-r),(x,y+r))]
            corners = [((x+w-r,y+r),(x+w-r,y)),
                       ((x+w-r,y+h-r),(x+w,y+h-r)),
                       ((x+r,y+h-r),(x+r,y+h)),
                       ((x+r,y+r),(x,y+r))]
            for (a,b), (center,start) in zip(segments,corners):
                lines.addByTwoPoints(point(*a),point(*b))
                arcs.addByCenterStartSweep(point(*center),point(*start),math.pi/2)
            return extrude(c, sk, name, depth)

        def disk(c, name, x, y, radius, z, depth):
            sk = sketch(c, name, z)
            sk.sketchCurves.sketchCircles.addByCenterRadius(point(x,y),radius/10)
            return extrude(c, sk, name, depth)

        def combine(c, target, tool, operation):
            collection = adsk.core.ObjectCollection.create()
            collection.add(tool)
            inp = c.features.combineFeatures.createInput(target, collection)
            inp.operation = operation
            inp.isKeepToolBodies = False
            c.features.combineFeatures.add(inp)

        def colour(body, name, rgb):
            try:
                appearance = design.appearances.addByCopy(body.appearance,name)
                prop = adsk.core.ColorProperty.cast(
                    appearance.appearanceProperties.itemById('generic_diffuse'))
                if prop:
                    prop.value = adsk.core.Color.create(*rgb,255)
                    body.appearance = appearance
            except Exception:
                pass

        update_progress(5, 'Plate and logo silhouette')
        c = plate_component
        plate = rounded_rectangle(c,'Plate',0,0,PANEL_WIDTH,PANEL_HEIGHT,
                                  6,0,PANEL_THICKNESS)
        logo = disk(c,'Flush logo silhouette',LOGO_X,LOGO_Y,LOGO_RADIUS,
                    0,PANEL_THICKNESS)
        combine(c,plate,logo,ops.JoinFeatureOperation)

        # A dedicated tongue leaves the ornamentation clear of the fit.
        tongue_x = (PANEL_WIDTH-TONGUE_WIDTH)/2
        tongue = rounded_rectangle(c,'Insertion tongue',tongue_x,-TONGUE_DEPTH,
                                   TONGUE_WIDTH,TONGUE_DEPTH+2,1,
                                   0,PANEL_THICKNESS)
        combine(c,plate,tongue,ops.JoinFeatureOperation)

        update_progress(12, 'Curved clinic logo')
        # Engraved custom serif E, two curved stars and dot.
        # No horizontal middle bar; all contours follow the supplied reference.
        for name, contour in zip(('Serif E', 'Small star', 'Large star'),
                                 logo_contours()):
            tool = polygon(c, name+' engraving', contour,
                           PANEL_THICKNESS-0.6, 0.8)
            combine(c, plate, tool, ops.CutFeatureOperation)
        dot_scale = LOGO_RADIUS/540
        dot = disk(c, 'Logo dot', LOGO_X+(680-540)*dot_scale,
                   LOGO_Y+(540-327)*dot_scale, 18*dot_scale,
                   PANEL_THICKNESS-0.6, 0.8)
        combine(c, plate, dot, ops.CutFeatureOperation)

        # Curved lateral processes. Three arcs create a rounded, hooked outline.
        def process(name, x, y, scale):
            sk = sketch(c,name,PANEL_THICKNESS-0.1)
            def p(dx,dy):
                return point(x+dx*scale,y+dy*scale)
            arcs = sk.sketchCurves.sketchArcs
            arcs.addByThreePoints(p(0,1),p(4,0.5),p(8,-1))
            arcs.addByThreePoints(p(8,-1),p(9,-2),p(8,-3))
            # The middle point must be off the chord: (4,-2) was collinear
            # with the endpoints and Fusion correctly rejected that arc.
            arcs.addByThreePoints(p(8,-3),p(4,-2.7),p(0,-1))
            sk.sketchCurves.sketchLines.addByTwoPoints(p(0,-1),p(0,1))
            return extrude(c,sk,name,SPINE_RELIEF+0.1)

        for spine_index,(region,index,x,y,w,h) in enumerate(vertebra_layout()):
            update_progress(20+spine_index, 'Spine: vertebra %d/24' % (spine_index+1))
            name = '%s%d' % (region,index)
            vertebra = rounded_rectangle(c,name+' rounded vertebra',
                x-w/2,y-h/2,w,h,min(1.8,h*0.27),
                PANEL_THICKNESS-0.1,SPINE_RELIEF+0.1)
            combine(c,plate,vertebra,ops.JoinFeatureOperation)
            # Every lateral feature overlaps its body and the backing plate.
            scale = 1.0 if region=='C' else (1.15 if region=='T' else 1.35)
            extension = process(name+' curved process',x+w*0.2,y,scale)
            combine(c,plate,extension,ops.JoinFeatureOperation)

        sacrum = polygon(c,'Sacrum',[(x+SPINE_X_OFFSET,y) for x,y in
            [(141,43),(153,43),(157,38),(157,33),(151,28),(150,22),
             (146,21),(141,29),(138,36)]],
            PANEL_THICKNESS-0.1,SPINE_RELIEF+0.1)
        combine(c,plate,sacrum,ops.JoinFeatureOperation)
        tail = process('Coccyx',145+SPINE_X_OFFSET,22,1.0)
        combine(c,plate,tail,ops.JoinFeatureOperation)

        # Each row: social symbol -> functional QR -> contactless symbol.
        # Icons and QR share the plate body. Exactly two internal tag cavities.
        def relief_polygon(name, contour):
            body = polygon(c, name, contour, PANEL_THICKNESS-0.02, 0.62)
            combine(c, plate, body, ops.JoinFeatureOperation)

        update_progress(46, 'Social and contactless symbols')
        def build_qr(platform, rows, bottom):
            # All disjoint strips in one deferred sketch and one extrusion.
            pitch = QR_SIZE/len(rows)
            strips = list(qr_runs(rows))
            sk = sketch(c, platform+' QR - batched', PANEL_THICKNESS-0.02)
            try:
                lines = sk.sketchCurves.sketchLines
                for index,(row,start,end) in enumerate(strips):
                    x0=QR_X+start*pitch+0.01
                    x1=QR_X+end*pitch-0.01
                    y0=bottom+(len(rows)-row-1)*pitch+0.01
                    y1=bottom+(len(rows)-row)*pitch-0.01
                    # Explicit lines avoid unnecessary horizontal/vertical
                    # constraints automatically created by the rectangle helper.
                    corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
                    for a,b in zip(corners,corners[1:]+corners[:1]):
                        lines.addByTwoPoints(point(*a),point(*b))
                    if index % 64 == 0:
                        update_progress(76 if platform=='Instagram' else 86,
                            platform+' QR: drawing %d/%d strips' %
                            (index+1,len(strips)))
            finally:
                sk.isComputeDeferred = False
            if sk.profiles.count != len(strips):
                raise RuntimeError(platform+' QR: unexpected profile count %d/%d' %
                                   (sk.profiles.count,len(strips)))
            profiles=adsk.core.ObjectCollection.create()
            for index in range(sk.profiles.count):
                profiles.add(sk.profiles.item(index))
            update_progress(80 if platform=='Instagram' else 90,
                            platform+' QR: joining all strips (one operation)')
            feature=c.features.extrudeFeatures.addSimple(profiles,
                adsk.core.ValueInput.createByReal(0.062),
                ops.JoinFeatureOperation)
            feature.name=platform+' QR - single extrusion'
            sk.isVisible=False

        for platform, rows, bottom in row_layout():
            update_progress(48 if platform=='Instagram' else 58, platform+' symbols and tag pocket')
            center_y = bottom+QR_SIZE/2
            cx = ICON_X
            if platform == 'Instagram':
                outline = rounded_rectangle(c,'Instagram outline',cx-12,
                    center_y-12,24,24,6,PANEL_THICKNESS-0.02,0.62)
                inner = rounded_rectangle(c,'Instagram outline hollow',cx-10.4,
                    center_y-10.4,20.8,20.8,4.4,PANEL_THICKNESS-0.1,0.8)
                combine(c,outline,inner,ops.CutFeatureOperation)
                combine(c,plate,outline,ops.JoinFeatureOperation)
                ring = disk(c,'Instagram lens',cx,center_y,7.0,
                            PANEL_THICKNESS-0.02,0.62)
                inner = disk(c,'Instagram lens hollow',cx,center_y,5.4,
                             PANEL_THICKNESS-0.1,0.8)
                combine(c,ring,inner,ops.CutFeatureOperation)
                combine(c,plate,ring,ops.JoinFeatureOperation)
                dot = disk(c,'Instagram camera dot',cx+6.7,center_y+6.7,1.45,
                           PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,dot,ops.JoinFeatureOperation)
            else:
                relief_polygon('Google G curved outline',
                    sector_contour(cx,center_y,10.5,2.8,45,315))
                bar = rectangle(c,'Google G horizontal stroke',cx+0.4,
                    center_y-1.4,11.4,2.8,PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,bar,ops.JoinFeatureOperation)
                bar = rectangle(c,'Google G right stroke',cx+9,
                    center_y-7.5,2.8,7.5,PANEL_THICKNESS-0.02,0.62)
                combine(c,plate,bar,ops.JoinFeatureOperation)

            # Three contactless arcs, 1.4 mm strokes, over the concealed tag.
            for radius in (3.7,7.0,10.3):
                relief_polygon(platform+' contactless wave %.1f' % radius,
                    sector_contour(NFC_X-5,center_y,radius,1.4,-55,55))

            # A fully enclosed void. At the pause the upper wall isn't printed yet.
            pocket = disk(c,platform+' concealed NFC cavity',NFC_X,center_y,
                          NFC_CAVITY_DIAMETER/2,NFC_CAVITY_FLOOR_Z,
                          NFC_CAVITY_HEIGHT)
            combine(c,plate,pocket,ops.CutFeatureOperation)

        def label(message,x,y,width,height):
            sk = None
            try:
                sk = sketch(c,message,PANEL_THICKNESS)
                inp = sk.sketchTexts.createInput2(message,height/10)
                inp.setAsMultiLine(point(x,y),point(x+width,y+height+3),
                    adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                    adsk.core.VerticalAlignments.MiddleVerticalAlignment,0)
                text = sk.sketchTexts.add(inp)
                sk.isComputeDeferred = False
                if EMBOSS_TEXT:
                    c.features.extrudeFeatures.addSimple(text,
                        adsk.core.ValueInput.createByReal(0.06),
                        ops.JoinFeatureOperation)
                    sk.isVisible = False
                else:
                    sk.isVisible = True
            except Exception:
                if sk:
                    sk.isComputeDeferred = False
                    sk.isVisible = True
                warnings.append('Label remains a sketch: '+message)

        update_progress(70, 'Clinic lettering')
        label('CLINICA',18,168,116,9)
        label('ESSENCIAL',18,152,116,11)
        # Join QR geometry last, after all plate cutting/decorative features.
        for platform, rows, bottom in row_layout():
            build_qr(platform, rows, bottom)
        plate.name = 'Plate - one solid with integrated spine'
        colour(plate,'Ivory plate',(246,239,233))

        # Base is placed to the right, with its slot facing upward (+Z).
        # Both parts are separate components, one solid body each.
        update_progress(94, 'Slotted base')
        b = base_component
        bx = PANEL_WIDTH+30
        base = rounded_rectangle(b,'Base',bx,0,BASE_WIDTH,BASE_DEPTH,
                                 7,0,BASE_HEIGHT)
        slot_width = PANEL_THICKNESS+2*FIT_CLEARANCE_PER_SIDE
        slot_length = TONGUE_WIDTH+2*END_CLEARANCE_PER_SIDE
        sx = bx+(BASE_WIDTH-slot_length)/2
        sy = (BASE_DEPTH-slot_width)/2
        slot = rectangle(b,'Tongue socket',sx,sy,slot_length,slot_width,
                         BASE_HEIGHT-slot_depth,slot_depth+1)
        combine(b,base,slot,ops.CutFeatureOperation)
        # A wider shallow entry step guides the tongue into the narrower throat.
        entry = rectangle(b,'Wider socket entry',sx-ENTRY_EXTRA_PER_SIDE,
            sy-ENTRY_EXTRA_PER_SIDE,slot_length+2*ENTRY_EXTRA_PER_SIDE,
            slot_width+2*ENTRY_EXTRA_PER_SIDE,BASE_HEIGHT-ENTRY_DEPTH,
            ENTRY_DEPTH+1)
        combine(b,base,entry,ops.CutFeatureOperation)
        base.name = 'Base - one solid with open-top socket'
        colour(base,'Pink base',(205,79,125))

        # Enforce the two-piece contract in the actual Fusion result.
        if c.bRepBodies.count != 1 or b.bRepBodies.count != 1:
            raise RuntimeError('Expected exactly one solid body per component.')
        if not c.bRepBodies.item(0).isSolid or not b.bRepBodies.item(0).isSolid:
            raise RuntimeError('A component is not a solid.')
        update_progress(100, 'Checking two solids')
        app.activeViewport.fit()
        progress.hide()
        ui.messageBox('V4 created: TWO parts in separate components.\n'
            'Plate + logo + spine: one body. Base: one body.\n'
            'Plate: 200 x 220 mm; both QR fields: 64 x 64 mm.\n'
            'Socket: %.2f mm wide x %.2f mm long x %.2f mm deep.\n'
            'Fit: %.2f mm per side. Tongue: %.1f mm deep.\n'
            'Parts shown separated, not assembled.\n'
            'Print a fit sample before committing to the full plate.\n'
            'Two 25.8 mm concealed NFC pockets: pause AFTER z=3.8 mm, BEFORE roof.\n'
            'Instagram + Google QR. Logo manually redrawn from image, not exact vector.\n'
            'Save as .f3d; export each component separately.\n%s' % (
                slot_width,slot_length,slot_depth,FIT_CLEARANCE_PER_SIDE,
                TONGUE_DEPTH,'\n'.join(warnings)))
    except BuildCancelled:
        if progress:
            progress.hide()
        ui.messageBox('Cancelled. You can close the partial NEW document without saving.')
    except Exception:
        if progress:
            progress.hide()
        ui.messageBox('V4 failed during '+current_stage+':\n'+traceback.format_exc())
    finally:
        if progress:
            progress.hide()
