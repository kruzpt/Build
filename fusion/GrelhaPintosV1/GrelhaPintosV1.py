"""Lightweight chick tray prototype. All dimensions mm; Fusion API uses cm.

Creates a NEW document. Print face down: flat contact surface on the bed,
feet upwards. Prototype: the 6 mm apertures are NOT a day-old chick safety
certification. Use a non-slip temporary cover for hatchlings and observe them.
"""
import math
import traceback
import adsk.core
import adsk.fusion

ORIGINAL_WIDTH = 217.5
ORIGINAL_DEPTH = 180.0
MODULE_REDUCTION = 0.2  # User confirmed: per module, in BOTH axes.
WIDTH = ORIGINAL_WIDTH - MODULE_REDUCTION
DEPTH = ORIGINAL_DEPTH - MODULE_REDUCTION
HEIGHT = 30.0
GRID_THICKNESS = 3.2
HOLE = 6.0  # Retains original aperture; deliberately not enlarged for hatchlings.
WEB = 1.6
MIN_BORDER = 2.4
CORNER_RADIUS = 3.0
RIB_DEPTH = 4.0
FOOT_SPAN = 12.0


def layout():
    nx = math.floor((WIDTH - 2*MIN_BORDER + WEB) / (HOLE + WEB))
    ny = math.floor((DEPTH - 2*MIN_BORDER + WEB) / (HOLE + WEB))
    bx = (WIDTH - (nx*HOLE + (nx-1)*WEB)) / 2
    by = (DEPTH - (ny*HOLE + (ny-1)*WEB)) / 2
    xs = [bx + i*(HOLE+WEB) for i in range(nx)]
    ys = [by + j*(HOLE+WEB) for j in range(ny)]
    # Three real web centre-lines in each direction; feet sit at intersections.
    cx = [xs[i]+HOLE+WEB/2 for i in (0, (nx-2)//2, nx-2)]
    cy = [ys[j]+HOLE+WEB/2 for j in (0, (ny-2)//2, ny-2)]
    return {'nx': nx, 'ny': ny, 'border_x': bx, 'border_y': by,
            'xs': xs, 'ys': ys, 'rib_x': cx, 'rib_y': cy,
            'feet': [(x,y) for x in cx for y in cy]}


def foot_contour(x, y):
    """Open cross-shaped post: no hollow pocket to trap droppings."""
    a, b = FOOT_SPAN/2, WEB/2
    return [(x-a,y-b),(x-b,y-b),(x-b,y-a),(x+b,y-a),
            (x+b,y-b),(x+a,y-b),(x+a,y+b),(x+b,y+b),
            (x+b,y+a),(x-b,y+a),(x-b,y+b),(x-a,y+b)]


def validate():
    if not 0 <= MODULE_REDUCTION <= 2:
        raise ValueError('Keep the module reduction between 0 and 2 mm.')
    if not 0 < GRID_THICKNESS < GRID_THICKNESS+RIB_DEPTH < HEIGHT:
        raise ValueError('Invalid grid, rib or foot heights.')
    if WEB < 1.6 or HOLE <= 0 or MIN_BORDER < 2.4:
        raise ValueError('Invalid web thickness, hole or border.')
    if WIDTH+10 > 256 or DEPTH+10 > 256:
        raise ValueError('Module plus a 5 mm brim must fit the A1 bed.')
    v = layout()
    if v['nx'] < 3 or v['ny'] < 3:
        raise ValueError('Not enough holes to support this layout.')
    if not 0 < CORNER_RADIUS <= min(v['border_x'],v['border_y'])+1:
        raise ValueError('Outer corner radius is too large.')
    for x,y in v['feet']:
        if min(x, WIDTH-x, y, DEPTH-y) <= FOOT_SPAN/2:
            raise ValueError('A foot would protrude past the module.')
    return v


class Cancelled(Exception):
    pass


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    progress = None
    stage = 'Validate'
    try:
        v = validate()
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        c = design.rootComponent.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()).component
        c.name = 'Grelha pintos V1 - prototype'
        ops = adsk.fusion.FeatureOperations
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = True
        progress.show('Grelha Pintos V1', 'Preparing (%p%)', 0, 100, 0)

        def update(number, message):
            nonlocal stage
            stage = message
            progress.progressValue = number
            progress.message = message+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:
                raise Cancelled()

        def point(x,y,z=0):
            return adsk.core.Point3D.create(x/10,y/10,z/10)

        def sketch(name,z=0):
            plane = c.xYConstructionPlane
            if z:
                inp = c.constructionPlanes.createInput()
                inp.setByOffset(plane,adsk.core.ValueInput.createByReal(z/10))
                plane = c.constructionPlanes.add(inp)
            sk = c.sketches.add(plane)
            sk.name = name
            sk.isVisible = False
            sk.isComputeDeferred = True
            return sk

        def polygon(sk, vertices):
            for a,b in zip(vertices,vertices[1:]+vertices[:1]):
                sk.sketchCurves.sketchLines.addByTwoPoints(point(*a),point(*b))

        def rectangle(sk,x,y,w,h):
            polygon(sk,[(x,y),(x+w,y),(x+w,y+h),(x,y+h)])

        def extrude(sk,name,distance,operation,count):
            sk.isComputeDeferred = False
            if sk.profiles.count != count:
                raise RuntimeError('%s: expected %d profiles, found %d' %
                                   (name,count,sk.profiles.count))
            profiles = adsk.core.ObjectCollection.create()
            for i in range(sk.profiles.count):
                profiles.add(sk.profiles.item(i))
            feature = c.features.extrudeFeatures.addSimple(profiles,
                adsk.core.ValueInput.createByReal(distance/10),operation)
            feature.name = name
            sk.isVisible = False

        update(5,'Outline')
        sk = sketch('Outer rounded outline')
        w,h,r = WIDTH,DEPTH,CORNER_RADIUS
        segments = [((r,0),(w-r,0)),((w,r),(w,h-r)),
                    ((w-r,h),(r,h)),((0,h-r),(0,r))]
        corners = [((w-r,r),(w-r,0)),((w-r,h-r),(w,h-r)),
                   ((r,h-r),(r,h)),((r,r),(0,r))]
        for (a,b),(centre,start) in zip(segments,corners):
            sk.sketchCurves.sketchLines.addByTwoPoints(point(*a),point(*b))
            sk.sketchCurves.sketchArcs.addByCenterStartSweep(
                point(*centre),point(*start),math.pi/2)
        extrude(sk,'Grid slab',GRID_THICKNESS,ops.NewBodyFeatureOperation,1)

        update(15,'Apertures - deferred sketch, one cut')
        sk = sketch('All 6 mm apertures')
        for i,x in enumerate(v['xs']):
            for y in v['ys']:
                rectangle(sk,x,y,HOLE,HOLE)
            if i % 4 == 0:
                update(15+int(30*(i+1)/v['nx']),'Apertures')
        update(48,'Solving aperture sketch and cutting - may take a moment')
        extrude(sk,'All apertures - one operation',GRID_THICKNESS+1,
                ops.CutFeatureOperation,v['nx']*v['ny'])

        update(65,'Underside ribs along X')
        sk = sketch('X reinforcement ribs',GRID_THICKNESS)
        for y in v['rib_y']:
            rectangle(sk,0,y-WEB/2,WIDTH,WEB)
        extrude(sk,'X ribs',RIB_DEPTH,ops.JoinFeatureOperation,3)
        update(75,'Underside ribs along Y')
        sk = sketch('Y reinforcement ribs',GRID_THICKNESS)
        for x in v['rib_x']:
            rectangle(sk,x-WEB/2,0,WEB,DEPTH)
        extrude(sk,'Y ribs',RIB_DEPTH,ops.JoinFeatureOperation,3)

        update(85,'Nine open cross-shaped feet')
        sk = sketch('Feet',GRID_THICKNESS)
        for x,y in v['feet']:
            polygon(sk,foot_contour(x,y))
        extrude(sk,'Feet',HEIGHT-GRID_THICKNESS,ops.JoinFeatureOperation,9)

        update(95,'Checking one solid and complete dimensions')
        if c.bRepBodies.count != 1 or not c.bRepBodies.item(0).isSolid:
            raise RuntimeError('Expected one connected printable solid.')
        body = c.bRepBodies.item(0)
        box = body.boundingBox
        actual = (box.minPoint.x*10,box.minPoint.y*10,box.minPoint.z*10,
                  box.maxPoint.x*10,box.maxPoint.y*10,box.maxPoint.z*10)
        expected = (0,0,0,WIDTH,DEPTH,HEIGHT)
        if any(abs(a-b)>0.01 for a,b in zip(actual,expected)):
            raise RuntimeError('Unexpected bounding box: '+repr(actual))
        body.name = 'Pintos - one-piece prototype - print face down'
        app.activeViewport.fit()
        update(100,'Done')
        progress.hide()
        ui.messageBox('Prototype created in a NEW document.\n'
            '%.1f x %.1f x %.1f mm; apertures %.1f x %.1f mm.\n'
            'Reduction: %.1f mm PER MODULE in both axes.\n'
            'Flat chick-contact face at Z=0: PRINT THIS FACE ON THE BED.\n'
            'Feet point upwards while printing, downwards during use.\n'
            'No supports required. Export in mm at 100%% scale.\n'
            'Not validated for hatchling feet or physical loads.\n'
            'Use a non-slip temporary cover for day-old chicks; observe footing.\n'
            'Print one module and check fit/stability before printing ten.' %
            (WIDTH,DEPTH,HEIGHT,HOLE,HOLE,MODULE_REDUCTION))
    except Cancelled:
        ui.messageBox('Cancelled. Close the partial NEW document without saving.')
    except Exception:
        ui.messageBox('Failed during '+stage+':\n'+traceback.format_exc())
    finally:
        if progress:
            progress.hide()
