"""Fusion 360 concept draft. Dimensions below are millimetres."""
import traceback
import adsk.core
import adsk.fusion

WIDTH = 180
HEIGHT = 220
THICKNESS = 5
LOGO_RADIUS = 38
LOGO_X = 28
LOGO_Y = HEIGHT


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        # Work in a new document: never modify the user's open design.
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        component = root.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()).component
        component.name = 'Clinica Essencial - concept v1'
        new_body = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

        def point(x, y, z=0):
            return adsk.core.Point3D.create(x / 10, y / 10, z / 10)

        def sketch(name, z=0):
            plane = component.xYConstructionPlane
            if z:
                inp = component.constructionPlanes.createInput()
                inp.setByOffset(plane, adsk.core.ValueInput.createByReal(z / 10))
                plane = component.constructionPlanes.add(inp)
            result = component.sketches.add(plane)
            result.name = name
            return result

        def extrude(sk, name, depth):
            if sk.profiles.count != 1:
                raise RuntimeError(name + ': expected one closed profile')
            feature = component.features.extrudeFeatures.addSimple(
                sk.profiles.item(0),
                adsk.core.ValueInput.createByReal(depth / 10), new_body)
            body = feature.bodies.item(0)
            body.name = name
            sk.isVisible = False
            return body

        def polygon(name, vertices, z, depth):
            sk = sketch(name, z)
            lines = sk.sketchCurves.sketchLines
            for a, b in zip(vertices, vertices[1:] + vertices[:1]):
                lines.addByTwoPoints(point(*a), point(*b))
            return extrude(sk, name, depth)

        def box(name, x, y, w, h, z, depth):
            return polygon(name, [(x, y), (x+w, y),
                                  (x+w, y+h), (x, y+h)], z, depth)

        def disk(name, x, y, radius, z, depth):
            sk = sketch(name, z)
            sk.sketchCurves.sketchCircles.addByCenterRadius(
                point(x, y), radius / 10)
            return extrude(sk, name, depth)

        def combine(target, tool, operation):
            collection = adsk.core.ObjectCollection.create()
            collection.add(tool)
            inp = component.features.combineFeatures.createInput(target, collection)
            inp.operation = operation
            inp.isKeepToolBodies = False
            component.features.combineFeatures.add(inp)

        def colour(body, name, rgb):
            # Use an installed appearance; do not depend on downloadable materials.
            try:
                appearance = design.appearances.addByCopy(body.appearance, name)
                prop = adsk.core.ColorProperty.cast(
                    appearance.appearanceProperties.itemById('generic_diffuse'))
                if prop:
                    prop.value = adsk.core.Color.create(*rgb, 255)
                    body.appearance = appearance
            except Exception:
                pass

        white = (246, 239, 233)
        pink = (205, 79, 125)
        panel = box('Panel', 0, 0, WIDTH, HEIGHT, 0, THICKNESS)
        # The circular silhouette overlaps the panel and is fused at equal thickness.
        logo = disk('Logo silhouette', LOGO_X, LOGO_Y, LOGO_RADIUS, 0, THICKNESS)
        combine(panel, logo, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        panel.name = 'One-piece panel and logo silhouette'
        colour(panel, 'Ivory panel', white)

        # Flush coloured inlays, cut from the panel; no extra front-face height.
        # This E is a geometric approximation, not a tracing of the brand artwork.
        def inlay(name, vertices):
            cutter = polygon(name + ' pocket tool', vertices, THICKNESS-1, 1)
            combine(panel, cutter, adsk.fusion.FeatureOperations.CutFeatureOperation)
            body = polygon(name, vertices, THICKNESS-1, 1)
            colour(body, name + ' pink', pink)

        x, y = LOGO_X-17, LOGO_Y-24
        inlay('Logo E - approximate', [
            (x,y), (x+33,y), (x+33,y+5), (x+6,y+5),
            (x+6,y+22), (x+25,y+22), (x+25,y+27),
            (x+6,y+27), (x+6,y+43), (x+33,y+43),
            (x+33,y+48), (x,y+48)])
        inlay('Logo sparkle', [(LOGO_X+8, LOGO_Y+4),
            (LOGO_X+12, LOGO_Y+11), (LOGO_X+16, LOGO_Y+4),
            (LOGO_X+12, LOGO_Y-3)])

        # Decorative vertebrae: simplified connected blocks for a first CAD draft.
        for i in range(12):
            y = 12 + i * 17
            x = 158 + 3 * ((i % 4) - 1.5)
            vertebra = box('Vertebra %02d' % (i+1), x, y, 15, 12,
                           THICKNESS, 2)
            combine(panel, vertebra, adsk.fusion.FeatureOperations.JoinFeatureOperation)

        qr = box('QR placeholder - not scannable', 18, 30, 52, 52,
                 THICKNESS, 0.6)
        colour(qr, 'QR placeholder white', white)
        nfc = disk('NFC touch zone', 113, 56, 19, THICKNESS, 0.6)
        colour(nfc, 'NFC zone pink', pink)
        # Rear-access NFC recess, leaving 1 mm of plastic toward the front.
        pocket = disk('NFC rear pocket tool', 113, 56, 13, 0, THICKNESS-1)
        combine(panel, pocket, adsk.fusion.FeatureOperations.CutFeatureOperation)

        # Separate base shown in assembly position. Slot open at top, 0.3 mm clearance.
        base = box('Base', -8, -12, WIDTH+16, 24, -40, 85)
        slot = box('Base slot tool', -0.15, 0, WIDTH+0.3, 12, -0.15,
                   THICKNESS+0.3)
        combine(base, slot, adsk.fusion.FeatureOperations.CutFeatureOperation)
        colour(base, 'Base pink', pink)

        warnings = []
        def label(message, x, y, height):
            try:
                sk = sketch(message, THICKNESS)
                inp = sk.sketchTexts.createInput2(message, height / 10)
                inp.setAsMultiLine(point(x, y), point(x+125, y+height+4),
                    adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                    adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
                sk.sketchTexts.add(inp)
                # Visible sketch labels keep this draft lightweight and editable.
                sk.isVisible = True
            except Exception:
                warnings.append('Text label unavailable: ' + message)

        label('CLINICA ESSENCIAL', 14, 142, 10)
        label('QR - link pending', 18, 15, 4)
        label('NFC', 101, 27, 5)
        app.activeViewport.fit()
        ui.messageBox('Concept created in a NEW document.\n'
            'Units: mm. Panel: 180 x 220 x 5.\n'
            'Logo and panel share a flush front face.\n'
            'Logo artwork and spine are simplified. QR is a placeholder.\n'
            'NFC pocket: 26 mm diameter, rear access.\n'
            'Text is visible sketch geometry, not embossed solids.\n'
            'Save as .f3d before editing.\n' + '\n'.join(warnings))
    except Exception:
        ui.messageBox('Draft creation failed:\n' + traceback.format_exc())
