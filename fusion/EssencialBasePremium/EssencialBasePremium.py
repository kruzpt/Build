"""Standalone replacement base for the Essencial A1 Reviews plaque.

Run in Fusion > Utilities > Scripts and Add-Ins. Creates a NEW document.
Dimensions below are mm; the Fusion API uses cm. No external dependencies.
Change constants and rerun to regenerate; timeline features use fixed values.
"""
import math
import traceback
import adsk.core
import adsk.fusion

# Match the existing plaque, without scaling the insertion tongue.
PANEL_THICKNESS = 5.0
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

# Exterior changes only. Front is Y=0; the socket stays centred and vertical.
CORNER_RADIUS = 12.0
TOP_EDGE_RADIUS = 2.0
FRONT_BEVEL = 8.0


def dimensions():
    """Independent fit geometry, also used by the validation checks."""
    length = TONGUE_WIDTH + 2 * END_CLEARANCE_PER_SIDE
    width = PANEL_THICKNESS + 2 * FIT_CLEARANCE_PER_SIDE
    depth = TONGUE_DEPTH + BOTTOM_CLEARANCE
    return {
        'slot_length': length,
        'slot_width': width,
        'slot_depth': depth,
        'slot_x': (BASE_WIDTH - length) / 2,
        'slot_y': (BASE_DEPTH - width) / 2,
        'slot_floor': BASE_HEIGHT - depth,
        'entry_length': length + 2 * ENTRY_EXTRA_PER_SIDE,
        'entry_width': width + 2 * ENTRY_EXTRA_PER_SIDE,
        'entry_floor': BASE_HEIGHT - ENTRY_DEPTH,
        'front_height': BASE_HEIGHT - FRONT_BEVEL,
    }


def bevel_profile():
    """(Y,Z) triangle. Its lower boundary is Z=H-B+Y over 0<=Y<=B.

    Extend above and in front of the solid for a clean through-cut. The
    actual bevel remains 8 x 8 mm at 45 degrees, even at the rounded corners.
    """
    return [(-1.0, BASE_HEIGHT - FRONT_BEVEL - 1.0),
            (-1.0, BASE_HEIGHT + 1.0),
            (FRONT_BEVEL + 1.0, BASE_HEIGHT + 1.0)]


def validate_dimensions():
    d = dimensions()
    if not all(value > 0 for value in (
            PANEL_THICKNESS, TONGUE_WIDTH, TONGUE_DEPTH,
            FIT_CLEARANCE_PER_SIDE, END_CLEARANCE_PER_SIDE,
            BOTTOM_CLEARANCE, ENTRY_EXTRA_PER_SIDE, ENTRY_DEPTH)):
        raise ValueError('Fit dimensions and clearances must be positive.')
    if not 0 < CORNER_RADIUS < min(BASE_WIDTH, BASE_DEPTH) / 2:
        raise ValueError('Invalid outer corner radius.')
    if not 0 < TOP_EDGE_RADIUS < min(CORNER_RADIUS, BASE_HEIGHT / 2):
        raise ValueError('Invalid top edge radius.')
    if not 0 < FRONT_BEVEL < BASE_HEIGHT:
        raise ValueError('Front bevel must leave a solid front wall.')
    if d['slot_floor'] < 4.0:
        raise ValueError('Keep at least 4 mm below the socket.')
    if not 0 < ENTRY_DEPTH < d['slot_depth']:
        raise ValueError('Entry must be shallower than the socket.')
    # The entrance sits entirely inside the untouched flat deck, clear of
    # the bevel, outer fillets and rounded corners.
    if d['slot_y'] - ENTRY_EXTRA_PER_SIDE <= FRONT_BEVEL + TOP_EDGE_RADIUS:
        raise ValueError('Front bevel is too close to the socket entrance.')
    if d['slot_y'] - ENTRY_EXTRA_PER_SIDE <= CORNER_RADIUS + TOP_EDGE_RADIUS:
        raise ValueError('Rounded outline is too close to the socket entrance.')
    if d['slot_x'] - ENTRY_EXTRA_PER_SIDE <= CORNER_RADIUS + TOP_EDGE_RADIUS:
        raise ValueError('Socket entrance is too close to the side corners.')
    return d


class BuildCancelled(Exception):
    pass


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    progress = None
    stage = 'Checking dimensions'
    try:
        d = validate_dimensions()
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.unitsManager.distanceDisplayUnits = (
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits)
        component = design.rootComponent.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()).component
        component.name = 'Essencial - replacement bevelled base'
        ops = adsk.fusion.FeatureOperations
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = True
        progress.show('Essencial Base Premium', 'Preparing (%p%)', 0, 100, 0)

        def update(value, message):
            nonlocal stage
            stage = message
            progress.progressValue = value
            progress.message = message + ' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:
                raise BuildCancelled()

        def point(x, y, z=0):
            return adsk.core.Point3D.create(x / 10, y / 10, z / 10)

        def value(mm):
            return adsk.core.ValueInput.createByReal(mm / 10)

        def sketch(name, plane):
            sk = component.sketches.add(plane)
            sk.name = name
            sk.isVisible = False
            sk.isComputeDeferred = True
            return sk

        def offset_plane(plane, offset):
            inp = component.constructionPlanes.createInput()
            inp.setByOffset(plane, value(offset))
            return component.constructionPlanes.add(inp)

        def extrude(sk, name, distance, operation):
            sk.isComputeDeferred = False
            if sk.profiles.count != 1:
                raise RuntimeError(name + ': expected one closed profile.')
            feature = component.features.extrudeFeatures.addSimple(
                sk.profiles.item(0), value(distance), operation)
            feature.name = name
            sk.isVisible = False
            return feature

        def rectangle_cut(name, x, y, width, length, floor):
            plane = offset_plane(component.xYConstructionPlane, floor)
            sk = sketch(name, plane)
            vertices = [(x, y), (x + width, y),
                        (x + width, y + length), (x, y + length)]
            for a, b in zip(vertices, vertices[1:] + vertices[:1]):
                sk.sketchCurves.sketchLines.addByTwoPoints(point(*a), point(*b))
            # Cut upwards from the floor, extending beyond the top face.
            extrude(sk, name, BASE_HEIGHT - floor + 1, ops.CutFeatureOperation)

        update(10, 'Rounded outline - 160 x 70 mm')
        sk = sketch('Outline - R12 corners', component.xYConstructionPlane)
        w, h, r = BASE_WIDTH, BASE_DEPTH, CORNER_RADIUS
        segments = [((r, 0), (w-r, 0)), ((w, r), (w, h-r)),
                    ((w-r, h), (r, h)), ((0, h-r), (0, r))]
        corners = [((w-r, r), (w-r, 0)), ((w-r, h-r), (w, h-r)),
                   ((r, h-r), (r, h)), ((r, r), (0, r))]
        for (a, b), (centre, start) in zip(segments, corners):
            sk.sketchCurves.sketchLines.addByTwoPoints(point(*a), point(*b))
            sk.sketchCurves.sketchArcs.addByCenterStartSweep(
                point(*centre), point(*start), math.pi / 2)
        extrude(sk, 'Base - 18 mm height', BASE_HEIGHT, ops.NewBodyFeatureOperation)

        # Round the outside top boundary BEFORE cutting the socket, so no
        # socket edges can accidentally be selected or change the fit.
        update(30, 'Soft outer top edges - R2')
        body = component.bRepBodies.item(0)
        edges = adsk.core.ObjectCollection.create()
        for edge in body.edges:
            box = edge.boundingBox
            if (abs(box.minPoint.z * 10 - BASE_HEIGHT) < 0.001 and
                    abs(box.maxPoint.z * 10 - BASE_HEIGHT) < 0.001):
                edges.add(edge)
        if edges.count != 8:
            raise RuntimeError('Expected eight outside top edges before filleting.')
        fillets = component.features.filletFeatures
        inp = fillets.createInput()
        inp.edgeSetInputs.addConstantRadiusEdgeSet(
            edges, value(TOP_EDGE_RADIUS), False)
        fillets.add(inp).name = 'Outside top softening - R2'

        update(50, 'Front bevel - 8 x 8 mm at 45 degrees')
        # Fusion's YZ plane points along +X. Convert MODEL points to sketch
        # coordinates rather than assuming the sketch's local axis ordering.
        yz_plane = offset_plane(component.yZConstructionPlane, -1)
        sk = sketch('Front bevel side profile', yz_plane)
        vertices = [sk.modelToSketchSpace(point(-1, y, z))
                    for y, z in bevel_profile()]
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            sk.sketchCurves.sketchLines.addByTwoPoints(a, b)
        extrude(sk, 'Front bevel through width', BASE_WIDTH + 2,
                ops.CutFeatureOperation)

        update(70, 'Original socket - 120.6 x 5.5 x 12.8 mm')
        rectangle_cut('Socket - original fit', d['slot_x'], d['slot_y'],
                      d['slot_length'], d['slot_width'], d['slot_floor'])
        update(85, 'Original wider entrance - 1 mm deep')
        rectangle_cut('Socket entrance - original guide',
                      d['slot_x'] - ENTRY_EXTRA_PER_SIDE,
                      d['slot_y'] - ENTRY_EXTRA_PER_SIDE,
                      d['entry_length'], d['entry_width'], d['entry_floor'])

        update(95, 'Checking solid and actual socket floor')
        if component.bRepBodies.count != 1:
            raise RuntimeError('Expected one solid base, without tool bodies.')
        body = component.bRepBodies.item(0)
        if not body.isSolid:
            raise RuntimeError('Base is not a solid.')
        expected = (0, 0, 0, BASE_WIDTH, BASE_DEPTH, BASE_HEIGHT)
        box = body.boundingBox
        actual = (box.minPoint.x * 10, box.minPoint.y * 10,
                  box.minPoint.z * 10, box.maxPoint.x * 10,
                  box.maxPoint.y * 10, box.maxPoint.z * 10)
        if any(abs(a-b) > 0.01 for a, b in zip(actual, expected)):
            raise RuntimeError('Unexpected exterior size: ' + repr(actual))
        # A rectangular floor face proves the socket was cut at its specified
        # coordinates and dimensions, rather than merely trusting constants.
        expected_floor = (d['slot_x'], d['slot_y'], d['slot_floor'],
                          d['slot_x'] + d['slot_length'],
                          d['slot_y'] + d['slot_width'], d['slot_floor'])
        floor_found = False
        for face in body.faces:
            box = face.boundingBox
            bounds = (box.minPoint.x * 10, box.minPoint.y * 10,
                      box.minPoint.z * 10, box.maxPoint.x * 10,
                      box.maxPoint.y * 10, box.maxPoint.z * 10)
            if all(abs(a-b) < 0.01 for a, b in zip(bounds, expected_floor)):
                floor_found = True
                break
        if not floor_found:
            raise RuntimeError('Socket floor dimensions could not be verified.')
        body.name = 'Base Premium - one printable solid'
        try:
            appearance = design.appearances.addByCopy(body.appearance,
                                                      'Essencial pink')
            colour = adsk.core.ColorProperty.cast(
                appearance.appearanceProperties.itemById('generic_diffuse'))
            if colour:
                colour.value = adsk.core.Color.create(205, 79, 125, 255)
                body.appearance = appearance
        except Exception:
            pass  # Display colour does not affect the manufactured geometry.
        update(100, 'Finished')
        app.activeViewport.fit()
        progress.hide()
        ui.messageBox(
            'Replacement base created in a NEW document.\n'
            'Outside: 160 x 70 x 18 mm. Front bevel: 8 mm.\n'
            'Socket: %.2f x %.2f mm, %.2f mm deep.\n'
            'Entry: %.2f x %.2f mm, %.1f mm deep.\n'
            'Solid floor below socket: %.2f mm.\n'
            'Compatible with the existing 120 x 5 x 12 mm tongue.\n'
            'Save as .f3d; export this component in mm at 100%% scale.\n'
            'Print flat bottom down, slot up. Test the fit before final assembly.'
            % (d['slot_length'], d['slot_width'], d['slot_depth'],
               d['entry_length'], d['entry_width'], ENTRY_DEPTH, d['slot_floor']))
    except BuildCancelled:
        ui.messageBox('Cancelled. The partial NEW document can be closed without saving.')
    except Exception:
        ui.messageBox('Base creation failed during ' + stage + ':\n' +
                      traceback.format_exc())
    finally:
        if progress:
            progress.hide()
