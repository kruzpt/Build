"""Clínica Essencial v2 — two printable parts. All dimensions in mm.

Run in Autodesk Fusion: Utilities > Scripts and Add-Ins > Scripts.
Creates a NEW document, with the parts separated in their own components.
"""
import math
import traceback
import adsk.core
import adsk.fusion

QR_ROWS = [
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

PANEL_WIDTH = 180.0
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
DISC_GAP = 1.0
NFC_TAG_DIAMETER = 26.0
NFC_FRONT_WALL = 1.2
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
            x = 145.0 + 5.0 * math.sin((y - 44.0) / 154.0 * 2 * math.pi)
            result.append((region, count-index, x, y, width*taper, height))
            bottom += height + DISC_GAP
    return result


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
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
        if not 0 < NFC_FRONT_WALL < PANEL_THICKNESS:
            raise ValueError('Invalid NFC front wall.')

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
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
            return sk

        def extrude(c, sk, name, depth):
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

        # Engraved approximate logo keeps the plate a single printable body.
        x, y = LOGO_X-17, LOGO_Y-24
        e = [(x,y),(x+33,y),(x+33,y+5),(x+6,y+5),(x+6,y+22),
             (x+25,y+22),(x+25,y+27),(x+6,y+27),(x+6,y+43),
             (x+33,y+43),(x+33,y+48),(x,y+48)]
        for name, vertices in [('E logo engraving',e),('Sparkle engraving',[
                (LOGO_X+8,LOGO_Y+4),(LOGO_X+12,LOGO_Y+11),
                (LOGO_X+16,LOGO_Y+4),(LOGO_X+12,LOGO_Y-3)])]:
            cutter = polygon(c,name,vertices,PANEL_THICKNESS-0.6,0.8)
            combine(c,plate,cutter,ops.CutFeatureOperation)

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

        for region,index,x,y,w,h in vertebra_layout():
            name = '%s%d' % (region,index)
            vertebra = rounded_rectangle(c,name+' rounded vertebra',
                x-w/2,y-h/2,w,h,min(1.8,h*0.27),
                PANEL_THICKNESS-0.1,SPINE_RELIEF+0.1)
            combine(c,plate,vertebra,ops.JoinFeatureOperation)
            # Every lateral feature overlaps its body and the backing plate.
            scale = 1.0 if region=='C' else (1.15 if region=='T' else 1.35)
            extension = process(name+' curved process',x+w*0.2,y,scale)
            combine(c,plate,extension,ops.JoinFeatureOperation)

        sacrum = polygon(c,'Sacrum',[(141,43),(153,43),(157,38),
            (157,33),(151,28),(150,22),(146,21),(141,29),(138,36)],
            PANEL_THICKNESS-0.1,SPINE_RELIEF+0.1)
        combine(c,plate,sacrum,ops.JoinFeatureOperation)
        tail = process('Coccyx',145,22,1.0)
        combine(c,plate,tail,ops.JoinFeatureOperation)

        # Functional Instagram QR, joined into the plate: no third part.
        # Includes a four-module quiet zone. Keep the field white and modules black.
        qr_pitch = 52.0/len(QR_ROWS)
        edge_inset = 0.01  # Avoid degenerate corner contacts between strips.
        for row, values in enumerate(QR_ROWS):
            start = None
            for col, value in enumerate(values+'0'):
                if value == '1' and start is None:
                    start = col
                elif value == '0' and start is not None:
                    sk = sketch(c,'QR row %d run %d' % (row,start),
                                PANEL_THICKNESS-0.02)
                    sk.sketchCurves.sketchLines.addTwoPointRectangle(
                        point(17+start*qr_pitch+edge_inset,
                              30+(len(QR_ROWS)-row-1)*qr_pitch+edge_inset),
                        point(17+col*qr_pitch-edge_inset,
                              30+(len(QR_ROWS)-row)*qr_pitch-edge_inset))
                    c.features.extrudeFeatures.addSimple(sk.profiles.item(0),
                        adsk.core.ValueInput.createByReal(0.062),
                        ops.JoinFeatureOperation)
                    sk.isVisible = False
                    start = None
        nfc = disk(c,'NFC raised touch marker',110,56,18,
                   PANEL_THICKNESS-0.1,0.7)
        combine(c,plate,nfc,ops.JoinFeatureOperation)
        pocket = disk(c,'Rear NFC pocket',110,56,NFC_TAG_DIAMETER/2,
                      0,PANEL_THICKNESS-NFC_FRONT_WALL)
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
                if EMBOSS_TEXT:
                    c.features.extrudeFeatures.addSimple(text,
                        adsk.core.ValueInput.createByReal(0.06),
                        ops.JoinFeatureOperation)
                    sk.isVisible = False
                else:
                    sk.isVisible = True
            except Exception:
                if sk:
                    sk.isVisible = True
                warnings.append('Label remains a sketch: '+message)

        label('CLINICA',18,163,116,9)
        label('ESSENCIAL',18,145,116,11)
        label('Instagram',18,17,70,5)
        label('NFC',98,27,30,5)
        plate.name = 'Plate - one solid with integrated spine'
        colour(plate,'Ivory plate',(246,239,233))

        # Base is placed to the right, with its slot facing upward (+Z).
        # Both parts are separate components, one solid body each.
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
        app.activeViewport.fit()
        ui.messageBox('Instagram version created: TWO parts in separate components.\n'
            'Plate + logo + spine: one body. Base: one body.\n'
            'Socket: %.2f mm wide x %.2f mm long x %.2f mm deep.\n'
            'Fit: %.2f mm per side. Tongue: %.1f mm deep.\n'
            'Parts shown separated, not assembled.\n'
            'Print a fit sample before committing to the full plate.\n'
            'NFC rear pocket may need bridging/support in the slicer.\n'
            'QR: Instagram clinicaessencial_setubal. Logo still approximate.\n'
            'Save as .f3d; export each component separately.\n%s' % (
                slot_width,slot_length,slot_depth,FIT_CLEARANCE_PER_SIDE,
                TONGUE_DEPTH,'\n'.join(warnings)))
    except Exception:
        ui.messageBox('V2 creation failed:\n'+traceback.format_exc())
