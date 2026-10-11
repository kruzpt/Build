"""Lightweight chick tray prototype. All dimensions mm; Fusion API uses cm.

Creates a NEW document: universal plate, clip and sample edge. Print plate face down: flat contact surface on the bed,
feet upwards. Prototype: enlarged 8 mm apertures; check actual chick footing before
using all modules. Physical loads and animal use have not been tested here.
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
HOLE = 8.0  # Enlarged prototype based on the user's observation of chick feet.
WEB = 1.6
MIN_BORDER = 2.4
CORNER_RADIUS = 3.0
RIB_DEPTH = 4.0
FOOT_SPAN = 12.0

# Eight identical underside sockets. Nothing protrudes beyond the plate edge.
BOSS_DEPTH = 4.2
BOSS_LENGTH = 22.0
BOSS_END_Z = 14.8
SOCKET_NEAR = 0.8
SOCKET_HEAD_FAR = 3.4
SOCKET_THROAT_FAR = 2.8
SOCKET_WIDTH = 7.0
SOCKET_HEAD_Z = 5.6
SOCKET_SHOULDER_Z = 7.8
RELEASE_WINDOW_Z = 9.4
RELEASE_WINDOW_HEIGHT = 4.4

# Coordinates are in plate printing orientation: Z=0 is the walking surface.
# Clip arm is 1.2 mm thick, printed in XY, not as a standing layer stack.
CLIP_INNER = 1.4
CLIP_NECK_OUTER = 2.6
CLIP_HOOK_REACH = 3.2
CLIP_TIP_Z = 5.8
CLIP_HOOK_END_Z = 7.6
CLIP_BRIDGE_Z = 15.0
CLIP_BRIDGE_THICKNESS = 2.0
CLIP_WIDTH = 6.4
COUPON_WIDTH = 14.0
COUPON_LENGTH = 32.0


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


def socket_sites():
    """(edge x,y, inward nx,ny, tangent tx,ty), symmetric quarter positions."""
    sites = []
    for fraction in (0.25,0.75):
        sites += [(0,DEPTH*fraction,1,0,0,1),
                  (WIDTH,DEPTH*fraction,-1,0,0,1),
                  (WIDTH*fraction,0,0,1,1,0),
                  (WIDTH*fraction,DEPTH,0,-1,1,0)]
    return sites


def socket_polygon(site,near,far,length):
    x,y,nx,ny,tx,ty = site
    return [(x+nx*u+tx*d,y+ny*u+ty*d)
            for u,d in [(near,-length/2),(far,-length/2),
                        (far,length/2),(near,length/2)]]


def clip_contour(reach=None,deflection=0):
    """Across-seam X versus plate Z; optional idealised spring clearance check.

    Deflection translates the fingers towards the seam; it is a geometric
    insertion check, not an elasticity or force simulation.
    """
    reach = CLIP_HOOK_REACH if reach is None else reach
    b,n,i = BOSS_DEPTH,CLIP_NECK_OUTER,CLIP_INNER
    z0,z1,z2 = CLIP_TIP_Z,CLIP_HOOK_END_Z,CLIP_BRIDGE_Z
    ramp = z0+reach-n  # 45 degree lead-in.
    vertices = [(-b,z2+CLIP_BRIDGE_THICKNESS),(b,z2+CLIP_BRIDGE_THICKNESS),
                (b,z2),(n,z2),(n,z1),(reach,z1),(reach,ramp),(n,z0),
                (i,z0),(i,z2),(-i,z2),(-i,z0),(-n,z0),(-reach,ramp),
                (-reach,z1),(-n,z1),(-n,z2),(-b,z2)]
    return [(x-(math.copysign(deflection,x) if abs(x)<b else 0),z)
            for x,z in reversed(vertices)]


def clip_print_contour(reach=None):
    return [(x+BOSS_DEPTH,z-CLIP_TIP_Z) for x,z in clip_contour(reach)]


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
    if not (GRID_THICKNESS < SOCKET_HEAD_Z < CLIP_TIP_Z <
            CLIP_HOOK_END_Z < SOCKET_SHOULDER_Z < BOSS_END_Z <
            CLIP_BRIDGE_Z < CLIP_BRIDGE_Z+CLIP_BRIDGE_THICKNESS < HEIGHT):
        raise ValueError('Invalid socket or clip vertical clearances.')
    if min(SOCKET_NEAR,BOSS_DEPTH-SOCKET_HEAD_FAR) < 0.79:
        raise ValueError('Keep at least 0.8 mm socket side walls.')
    if CLIP_WIDTH >= SOCKET_WIDTH or CLIP_NECK_OUTER >= SOCKET_THROAT_FAR:
        raise ValueError('Clip must have clearance in socket.')
    if not SOCKET_THROAT_FAR < CLIP_HOOK_REACH < SOCKET_HEAD_FAR:
        raise ValueError('Clip hook must retain behind the socket shoulder.')
    if CLIP_NECK_OUTER-CLIP_INNER < 1.19:
        raise ValueError('Keep 1.2 mm clip spring thickness.')
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
        c.name = 'Grelha pintos V3 - prototype'
        ops = adsk.fusion.FeatureOperations
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = True
        progress.show('Grelha Pintos V3', 'Preparing (%p%)', 0, 100, 0)

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

        def add_sockets(sites):
            sk = sketch('Underside socket reinforcement',GRID_THICKNESS)
            for site in sites:
                polygon(sk,socket_polygon(site,0,BOSS_DEPTH,BOSS_LENGTH))
            extrude(sk,'Socket reinforcement',BOSS_END_Z-GRID_THICKNESS,
                    ops.JoinFeatureOperation,len(sites))
            sk = sketch('Wider hook cavities',SOCKET_HEAD_Z)
            for site in sites:
                polygon(sk,socket_polygon(site,SOCKET_NEAR,SOCKET_HEAD_FAR,
                                          SOCKET_WIDTH))
            extrude(sk,'Hook cavities',SOCKET_SHOULDER_Z-SOCKET_HEAD_Z,
                    ops.CutFeatureOperation,len(sites))
            sk = sketch('Bottom-open narrow socket mouths',SOCKET_SHOULDER_Z)
            for site in sites:
                polygon(sk,socket_polygon(site,SOCKET_NEAR,SOCKET_THROAT_FAR,
                                          SOCKET_WIDTH))
            extrude(sk,'Socket mouths',BOSS_END_Z-SOCKET_SHOULDER_Z+1,
                    ops.CutFeatureOperation,len(sites))
            sk = sketch('Inner release access windows',RELEASE_WINDOW_Z)
            for site in sites:
                polygon(sk,socket_polygon(site,SOCKET_THROAT_FAR,BOSS_DEPTH+1,
                                          SOCKET_WIDTH))
            extrude(sk,'Release access windows',RELEASE_WINDOW_HEIGHT,
                    ops.CutFeatureOperation,len(sites))

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
        sk = sketch('All apertures - 8 mm')
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

        update(90,'Eight universal underside sockets')
        add_sockets(socket_sites())

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
        plate = c

        update(96,'Separate PETG clip - flat printing orientation')
        c = design.rootComponent.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()).component
        c.name = '02 - Clip standard - print on side'
        bx = WIDTH+15
        sk = sketch('Spring clip side outline')
        polygon(sk,[(x+bx,y) for x,y in clip_print_contour()])
        extrude(sk,'Clip standard',CLIP_WIDTH,ops.NewBodyFeatureOperation,1)
        clip_component = c

        update(98,'One sample edge - print TWO copies')
        c = design.rootComponent.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()).component
        c.name = '03 - Sample edge - print TWO copies'
        by = 30
        sk = sketch('Sample top face')
        rectangle(sk,bx,by,COUPON_WIDTH,COUPON_LENGTH)
        extrude(sk,'Sample top',GRID_THICKNESS,ops.NewBodyFeatureOperation,1)
        add_sockets([(bx,by+COUPON_LENGTH/2,1,0,0,1)])
        for part in (plate,clip_component,c):
            if part.bRepBodies.count != 1 or not part.bRepBodies.item(0).isSolid:
                raise RuntimeError('Each component must be one closed solid.')
        app.activeViewport.fit()
        update(100,'Done')
        progress.hide()
        ui.messageBox('V3 created: universal plate, clip and sample edge.\n'
            '%.1f x %.1f x %.1f mm; apertures %.1f x %.1f mm.\n'
            'Reduction: %.1f mm PER MODULE in both axes.\n'
            'Flat chick-contact face at Z=0: PRINT THIS FACE ON THE BED.\n'
            'Feet point upwards while printing, downwards during use.\n'
            'No supports required. Export in mm at 100%% scale.\n'
            'Eight underside sockets: two per side, no outer protrusions.\n'
            '26 clips for the 2 x 5 array. Print TWO sample edges first.\n'
            'Print clips FLAT ON THEIR SIDE in PETG; verify snap retention.\n'
            'Fusion shows parts separated: export each component separately.\n'
            'Not validated for hatchling feet or physical loads.\n'
            'Check actual chick footing on the enlarged apertures; observe them.\n'
            'Print one module and check fit/stability before printing ten.' %
            (WIDTH,DEPTH,HEIGHT,HOLE,HOLE,MODULE_REDUCTION))
    except Cancelled:
        ui.messageBox('Cancelled. Close the partial NEW document without saving.')
    except Exception:
        ui.messageBox('Failed during '+stage+':\n'+traceback.format_exc())
    finally:
        if progress:
            progress.hide()
