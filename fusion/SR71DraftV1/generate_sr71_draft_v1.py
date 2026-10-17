"""SR-71A display miniature: printable derivative of the GPL FlightGear model.

Exterior sections and wing/fin outlines come from the included source AC files.
The solids, joins and FDM surface details below are new printable adaptations.
Units: mm. X is span, Y runs nose to tail, Z is up; joint plane is Z=0.
License for this derivative and its sources: GPL-2.0.
"""
from pathlib import Path
import json
import math
import hashlib
import shutil

import manifold3d as md
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial import ConvexHull
import trimesh
from PIL import Image, ImageDraw, ImageFont

from sr71_reference import load_ac
from generate_universo_stand import render_meshes, mesh_of

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'fusion/SR71DraftV1'
PREFIX = 'sr71-1-144-draft-v1'
LENGTH = 32740 / 144
SPAN = 16940 / 144
LONG_SCALE = LENGTH / (12.365 + 20.256)
SPAN_SCALE = SPAN / (2 * 7.980999946594238)
SPLIT_SOURCE_HEIGHT = .32
BLACK = '#41464D'
GREY = '#56616D'
BLUE = '#17385B'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def log(message):
    print(message, flush=True)


def union(solids):
    return md.Manifold.batch_boolean(list(solids), md.OpType.Add)


def xy(points):
    return md.CrossSection([np.asarray(points).tolist()], md.FillRule.EvenOdd)


def xyz(points):
    p = np.asarray(points)
    return np.column_stack((p[:, 2] * SPAN_SCALE,
                            (p[:, 0] + 20.256) * LONG_SCALE,
                            (p[:, 1] - SPLIT_SOURCE_HEIGHT) * LONG_SCALE))


def manifold(mesh):
    mesh = mesh.copy()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()
    assert mesh.is_watertight and mesh.is_winding_consistent
    solid = md.Manifold(md.Mesh(mesh.vertices.astype('float32'), mesh.faces.astype('uint32')))
    assert solid.status() == md.Error.NoError, solid.status()
    return solid


def loft(rings):
    """Closed triangulated loft of equal-size convex profile rings."""
    rings = np.asarray(rings)
    count, n, _ = rings.shape
    vertices = rings.reshape(-1, 3).tolist()
    vertices += [rings[0].mean(0).tolist(), rings[-1].mean(0).tolist()]
    faces = []
    for j in range(count - 1):
        for k in range(n):
            a = j*n+k; b = j*n+(k+1)%n; c = (j+1)*n+(k+1)%n; d = (j+1)*n+k
            faces.extend(((a, b, c), (a, c, d)))
    for k in range(n):
        faces.extend(((count*n, (k+1)%n, k),
                      (count*n+1, (count-1)*n+k, (count-1)*n+(k+1)%n)))
    return manifold(trimesh.Trimesh(vertices, faces, process=True))


def project(mesh, columns=(0, 1)):
    triangles = mesh.triangles[:, :, columns]
    sections = []
    for tri in triangles:
        area = np.linalg.det(np.stack((tri[1]-tri[0], tri[2]-tri[0]))) / 2
        if abs(area) > 1e-7:
            sections.append(xy(tri))
    return md.CrossSection.batch_boolean(sections, md.OpType.Add)


def rectangle(x, y, w, h, radius=0):
    if radius:
        return md.CrossSection.square((w-2*radius, h-2*radius)).translate((x+radius, y+radius)).offset(radius, circular_segments=20)
    return md.CrossSection.square((w, h)).translate((x, y))


class Fuselage:
    def __init__(self, a, b):
        meshes = [a[i]['mesh'] for i in (0, 7, 22, 23, 24, 25, 26, 28)]
        meshes += [b[i]['mesh'] for i in (82, 83, 84, 89)]
        stations = np.unique(np.r_[np.linspace(-18.995, 12.36, 90), np.linspace(-15.5, -10.3, 55)])
        angles = np.linspace(0, 2*np.pi, 96, endpoint=False)
        self.directions = np.column_stack((np.cos(angles), np.sin(angles)))
        radii, centers = [], []
        for station in stations:
            points = []
            for mesh in meshes:
                lines = trimesh.intersections.mesh_plane(mesh, (1, 0, 0), (station, 0, 0))
                if len(lines):
                    p = lines.reshape(-1, 3)
                    points.append(np.column_stack((p[:, 2]*SPAN_SCALE,
                                                   (p[:, 1]-SPLIT_SOURCE_HEIGHT)*LONG_SCALE)))
            p = np.vstack(points)
            # Symmetry is intentional for a static miniature in neutral flight.
            p = np.vstack((p, p*np.array([-1, 1])))
            hull = ConvexHull(p)
            center = np.array([0, (p[:, 1].min()+p[:, 1].max())/2])
            eq = hull.equations
            den = eq[:, :2] @ self.directions.T
            distances = -(eq[:, :2]@center+eq[:, 2])[:, None] / np.where(den > 1e-9, den, np.nan)
            r = np.nanmin(distances, axis=0)
            assert r.min() > 0
            radii.append(r); centers.append(center[1])
        self.ys = (stations+20.256)*LONG_SCALE
        self.radius = PchipInterpolator(self.ys, radii, axis=0)
        self.center = PchipInterpolator(self.ys, centers)
        ys = np.linspace(self.ys[0], self.ys[-1], 460)
        profiles = self.profiles(ys)
        self.solid = loft([np.column_stack((p[:, 0], np.full(len(p), y), p[:, 1])) for y, p in zip(ys, profiles)])

    def profiles(self, ys):
        r = self.radius(np.asarray(ys))
        p = r[..., None]*self.directions
        p[..., 1] += self.center(np.asarray(ys))[..., None]
        return p

    def top(self, x, y):
        y = float(np.clip(y, self.ys[0], self.ys[-1]))
        polygon = self.profiles([y])[0]
        heights = []
        for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
            if abs(b[0]-a[0]) > 1e-8 and min(a[0], b[0])-1e-7 <= x <= max(a[0], b[0])+1e-7:
                t = (x-a[0])/(b[0]-a[0]); heights.append(a[1]+t*(b[1]-a[1]))
        return max(heights) if heights else .25


def ribbon(path, height, width=.38, depth=.20):
    """Groove cutter that follows the actual exterior height, with a closed floor."""
    points = []
    for a, b in zip(path[:-1], path[1:]):
        a, b = np.asarray(a), np.asarray(b)
        n = max(1, int(np.ceil(np.linalg.norm(b-a)/.75)))
        points.extend(a+(b-a)*t for t in np.linspace(0, 1, n, endpoint=False))
    points.append(np.asarray(path[-1]))
    p = np.asarray(points)
    tangent = np.gradient(p, axis=0)
    normal = np.column_stack((-tangent[:, 1], tangent[:, 0]))
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    left, right = p+normal*width/2, p-normal*width/2
    rings = []
    for a, b in zip(left, right):
        za, zb = max(.20, height(*a)-depth), max(.20, height(*b)-depth)
        rings.append([[a[0], a[1], za], [b[0], b[1], zb],
                      [b[0], b[1], zb+1.5], [a[0], a[1], za+1.5]])
    return loft(rings)


def axis_y(solid, x=0, y=0, z=0):
    # Print Z becomes assembled +Y; print X becomes assembled X.
    return solid.transform([[1, 0, 0, x], [0, 0, 1, y], [0, -1, 0, z]])


def engine_outer(center_x):
    stations = np.array([-1.96, -1.6, 0, 2.1, 5.9, 7.1, 8.252])
    ys = (stations+20.256)*LONG_SCALE
    radii = np.array([.895, .925, .925, .91, .90, .87, .81])*LONG_SCALE
    yf = np.linspace(ys[0], ys[-1], 140)
    radius = PchipInterpolator(ys, radii)
    a = np.linspace(0, 2*np.pi, 128, endpoint=False)
    center_z = (.5-SPLIT_SOURCE_HEIGHT)*LONG_SCALE
    rings = [np.column_stack((center_x+float(radius(y))*np.cos(a), np.full(len(a), y),
                              center_z+float(radius(y))*np.sin(a))) for y in yf]
    return loft(rings), radius, center_z, ys[0], ys[-1]


def opening(radius):
    # Internal pointed roof stays behind the visible circular engine detail.
    # Faces climb at >=45 degrees rather than closing a broad round ceiling.
    return xy([(-radius, 0), (-.87*radius, .40*radius), (0, 1.27*radius),
               (.87*radius, .40*radius), (radius, 0), (.87*radius, -.40*radius),
               (0, -1.27*radius), (-.87*radius, -.40*radius)])


def fit_sample():
    """Small optional coupon reproducing pin and tail-tab clearances."""
    block=md.Manifold.cube((22,14,5))
    block-=md.Manifold.cylinder(2.25,1.35,1.35,circular_segments=64).translate((5,7,0))
    block-=rectangle(12,6.25,5.1,1.5,.15).extrude(2.35)
    pin=md.Manifold.cylinder(4.2,1.2,1.2,circular_segments=64).translate((29,6,0))
    tab=(rectangle(35,3,8,4,.4)+rectangle(36.6,6.8,4.8,2.2,.15)).extrude(1.2)
    raw=union([block,pin,tab]).to_mesh()
    mesh=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
    assert mesh.is_watertight and len(mesh.split())==3
    path=ROOT/'downloads'/f'{PREFIX}-amostra-encaixes.stl'
    mesh.export(path)
    return path


def main():
    log('Reading reference exterior sections and wing outlines')
    a = load_ac(FOLDER/'reference/SR-71A-Blackbird.ac')
    b = load_ac(FOLDER/'reference/SR-71-Blackbird-Base.ac')
    fuselage = Fuselage(a, b)
    log('Closed fuselage loft created')
    wing_sections = []
    for i in (41, 42, 63, 64, 65, 67):
        m = b[i]['mesh'].copy(); m.vertices = xyz(m.vertices)
        wing_sections.append(project(m))
    wing = md.CrossSection.batch_boolean(wing_sections, md.OpType.Add).offset(.025, circular_segments=16)
    wing_solid = wing.extrude(1.44).translate((0, 0, -.72))
    pitot = axis_y(md.Manifold.cylinder(11.2, .35, .62, circular_segments=48), y=0, z=0)
    engines = []
    center_x = 4.128*SPAN_SCALE
    for side in (-1, 1):
        engines.append(engine_outer(side*center_x))
    body = union([fuselage.solid, wing_solid, pitot]+[e[0] for e in engines])
    log('Wings and engine nacelles joined')

    cuts = []
    # Curved transverse and longitudinal access panel seams, deliberately sparse.
    for yy in (24, 73, 92, 116, 140, 163, 188, 211):
        section = fuselage.profiles([yy])[0]
        width = np.max(np.abs(section[:, 0]))*.93
        cuts.append(ribbon([(-width, yy), (width, yy)], fuselage.top))
    for side in (-1, 1):
        cuts.append(ribbon([(side*5.8, 78), (side*6.8, 120), (side*7.1, 160), (side*4.5, 198)], fuselage.top))
        # Sensor/access hatch ahead of the cockpit.
        path=[(side*3.0,29),(side*6.0,31),(side*7.0,36),(side*3.5,35),(side*3.0,29)]
        cuts.append(ribbon(path, fuselage.top, .36, .18))
    # Dorsal refuelling receptacle, matching the location of the reference doors.
    cuts.append(ribbon([(-1.6,76.3),(1.6,76.3),(1.6,81.0),(-1.6,81.0),(-1.6,76.3)], fuselage.top, .38, .24))
    # Real windshield/window outlines projected from the source glass objects.
    for i in (23, 25, 28):
        m = a[i]['mesh'].copy(); m.vertices = xyz(m.vertices)
        window = project(m)
        for polygon in window.to_polygons():
            p = np.asarray(polygon)
            if len(p)>2:
                cuts.append(ribbon(np.vstack((p,p[0])), fuselage.top, .36, .22))
    for yy in (48.8, 63.8):
        cuts.append(ribbon([(-4.0,yy),(0,yy),(4.0,yy)],fuselage.top,.40,.24))
    # Simplified exterior release handles beside the two canopy sections.
    for yy in (45.5, 58.3):
        cuts.append(ribbon([(4.9,yy),(5.8,yy),(5.8,yy+1.5),(4.9,yy+1.5),(4.9,yy)],fuselage.top,.34,.20))
    log('Panel and canopy grooves: '+str(len(cuts)))
    body -= union(cuts)
    # Corrugated wing areas; these are geometric grooves, not painted render lines.
    grooves=[]
    for side in (-1,1):
        for x in np.arange(38.5,55.5,1.20):
            grooves.append(md.Manifold.cube((.42,30,.20)).translate((side*x-.21,174,.56)))
        for yy in (181,191,201):
            grooves.append(md.Manifold.cube((22,.38,.20)).translate((side*48-11,yy,.56)))
        for yy in (205.6,):
            grooves.append(md.Manifold.cube((25,.45,.22)).translate((side*47-12.5,yy,.53)))
    body -= union(grooves)
    log('Wing corrugations cut')

    parts=[]; poses={}; cones=[]; nozzles=[]
    for side, (outer, radius, cz, front, rear) in zip((-1,1),engines):
        cx=side*center_x
        # Open intake: the round spike hides the rear pointed internal roof.
        cone_base=front+11.8
        intake=axis_y(opening(4.4).extrude(12.0),cx,front-.10,cz)
        body-=intake
        # Flat-bottom locating recess for the separate cone, total diameter gap .30.
        recess=axis_y(md.Manifold.cylinder(.65,3.95,3.95,circular_segments=96),cx,cone_base-.05,cz)
        body-=recess
        cone=md.Manifold.cylinder(26.0,3.80,.20,circular_segments=96)
        # Cone base sits on the recessed bulkhead; small face gap is for glue.
        cone_pose=np.array([[1,0,0,cx],[0,0,-1,cone_base+.45],[0,1,0,cz],[0,0,0,1]],float)
        cones.append((f'cone-{"esquerdo" if side<0 else "direito"}',cone,cone_pose))
        # Exhaust socket is recessed; printed inserts carry the visible detail.
        body-=axis_y(opening(3.8).extrude(5.0),cx,rear-5,cz)
        body-=axis_y(md.Manifold.cylinder(1.45,5.20,5.20,circular_segments=96),cx,rear-1.4,cz)
        disc=md.Manifold.cylinder(.60,5.05,5.05,circular_segments=128)
        ring=(md.CrossSection.circle(5.05,128)-md.CrossSection.circle(4.10,112)).extrude(.90).translate((0,0,.60))
        inner=md.Manifold.cylinder(.42,3.75,3.45,circular_segments=96).translate((0,0,.60))
        hub=md.Manifold.cylinder(.90,1.28,.45,circular_segments=64).translate((0,0,.60))
        blades=[]
        for deg in np.linspace(0,360,16,endpoint=False):
            blade=xy([(1.15,-.25),(3.95,-.12),(3.45,.47),(1.15,.25)]).extrude(.50).translate((0,0,.82)).rotate((0,0,float(deg)))
            blades.append(blade)
        nozzle=union([disc,ring,inner,hub]+blades)
        # Shallow radial divisions of the outer nozzle ring.
        for deg in np.linspace(0,360,16,endpoint=False):
            gap=md.Manifold.cube((1.15,.26,.30)).translate((3.98,-.13,1.22)).rotate((0,0,float(deg)))
            nozzle-=gap
        nozzle_pose=np.array([[1,0,0,cx],[0,0,1,rear-1.20],[0,-1,0,cz],[0,0,0,1]],float)
        nozzles.append((f'tubeira-{"esquerda" if side<0 else "direita"}',nozzle,nozzle_pose))
        # Circumferential nacelle panel seams and bypass slots.
        seams=[]
        for yy in (front+7,front+24,front+43,front+58):
            rr=float(radius(yy))-.06
            torus=md.CrossSection.circle(.20,16).translate((rr,0)).revolve(circular_segments=128)
            seams.append(axis_y(torus,cx,yy,cz))
        top=lambda x,y:cz+np.sqrt(max(0,float(radius(y))**2-(x-cx)**2))
        for k in range(7):
            yy=front+15+k*1.0
            seams.append(ribbon([(cx-2.6,yy),(cx+2.6,yy)],top,.40,.20))
        body-=union(seams)
    log('Intakes, exhaust seats and engine details created')

    # Tail profiles come from both the root fairing and the movable source fin.
    tail_points=[]
    for i in (27,28):
        v=b[i]['mesh'].vertices
        v=v[v[:,2]>0]
        tail_points.append(v[:,[0,1]])
    p=np.vstack(tail_points);hull=ConvexHull(p);outline=p[hull.vertices]
    root_x=float(outline[:,0].min());root_h=float(outline[:,1].min())
    outline=(outline-[root_x,root_h])*LONG_SCALE
    tail_profile=xy(outline).offset(-.12,circular_segments=20).offset(.12,circular_segments=20)
    tabs=rectangle(9,-2.20,4.8,2.60,.25)+rectangle(18,-2.20,4.8,2.60,.25)
    tail_shape=tail_profile+tabs
    tail=tail_shape.extrude(1.20)
    # Rudder hinge line, simplified to a printable recessed line on the upper face.
    tail-=xy([(23.0,2),(25.5,12),(25.9,12),(23.4,2)]).extrude(.22).translate((0,0,.99))
    angle=math.radians(15)
    fins=[]
    for side in (-1,1):
        cx=side*center_x
        y=(root_x+20.256)*LONG_SCALE
        z=(root_h-SPLIT_SOURCE_HEIGHT)*LONG_SCALE
        matrix=np.array([[0,-side*math.sin(angle),math.cos(angle),cx-.60*math.cos(angle)],
                         [1,0,0,y],
                         [0,math.cos(angle),side*math.sin(angle),z-side*.60*math.sin(angle)],
                         [0,0,0,1]],float)
        # Offset profile and thickness together for .15 mm clearance on each side.
        tool=tail_shape.offset(.15,circular_segments=20).extrude(1.50).translate((0,0,-.15))
        body-=tool.transform(matrix[:3].tolist())
        fins.append((f'deriva-{"esquerda" if side<0 else "direita"}',tail,matrix))
    log('Inward-canted tails and locating sockets created')

    # All mating faces stay flat on the print bed; therefore alignment pins are separate.
    pin_locations=[(0,60),(0,121),(0,184)]
    for x,y in pin_locations:
        body-=md.Manifold.cylinder(4.50,1.35,1.35,circular_segments=64).translate((x,y,-2.25))
    # Split before removing microscopic disconnected groove debris: the blind
    # alignment bores become open to the mating plane and stay in each shell.
    for x,y in pin_locations:
        check=md.Manifold.cylinder(4.2,1.20,1.20,circular_segments=64).translate((x,y,-2.10))
        assert (body^check).volume()<.001,'Alignment bore was not cut'
    upper=body.trim_by_plane((0,0,1),0)
    lower=body.trim_by_plane((0,0,-1),0)
    for label,half in [('upper',upper),('lower',lower)]:
        if len(half.decompose())!=1:
            log(str([(label,float(s.volume()),mesh_of(s).bounds.tolist()) for s in half.decompose()]))
    upper_shells=[s for s in upper.decompose() if abs(s.volume())>=.0001]
    lower_shells=[s for s in lower.decompose() if abs(s.volume())>=.0001]
    assert len(upper_shells)==len(lower_shells)==1
    upper,lower=upper_shells[0],lower_shells[0]
    assert (upper^lower).volume()<.001
    assert len(upper.decompose())==1,('Upper components',len(upper.decompose()))
    assert len(lower.decompose())==1,('Lower components',len(lower.decompose()))
    # Flip lower half to put its joint face at Z=0 during printing.
    lower_print=lower.rotate((180,0,0))
    poses['superior']=np.eye(4)
    poses['inferior']=np.diag([1,-1,-1,1])
    parts=[('superior',upper,poses['superior']),('inferior',lower_print,poses['inferior'])]
    parts+=fins+cones+nozzles
    pin=md.Manifold.cylinder(4.20,1.20,1.20,circular_segments=64)
    for i,(x,y) in enumerate(pin_locations,1):
        matrix=np.eye(4);matrix[:3,3]=[x,y,-2.10]
        parts.append((f'cavilha-{i}',pin,matrix))

    meshes=[];assembled=[];records=[];repairs=[]
    for key,solid,pose in parts:
        assert solid.status()==md.Error.NoError
        solid=solid.set_tolerance(.015 if key in ('superior','inferior') else .003)
        raw=solid.to_mesh64()
        mesh=trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=True)
        # Validate the actual STL precision. Removing collapsed zero-area CSG
        # triangles can expose microscopic triangular loops; cap only loops
        # whose total new surface is below 0.001 mm2, never a real opening.
        mesh.vertices=mesh.vertices.astype('float32').astype('float64')
        mesh.merge_vertices(digits_vertex=5)
        mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
        mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
        if not mesh.is_watertight:
            count=len(mesh.faces)
            assert trimesh.repair.fill_holes(mesh),(key,'Non-triangular topology defect')
            area=float(mesh.area_faces[count:].sum())
            assert area<.001,(key,'Repair would change a real feature',area)
            repairs.append({'part':key,'triangles':len(mesh.faces)-count,'surface_mm2':area})
        mesh.fix_normals()
        assert mesh.is_watertight and mesh.is_winding_consistent,(key,mesh.is_watertight)
        assert len(mesh.split())==1,key
        assert abs(mesh.bounds[0,2])<.001,(key,mesh.bounds)
        path=ROOT/'downloads'/f'{PREFIX}-{key}.stl';mesh.export(path)
        roundtrip=trimesh.load(path,force='mesh')
        assert roundtrip.is_watertight and roundtrip.is_winding_consistent,key
        posed=solid.transform(pose[:3].tolist())
        assembled.append((posed,BLACK));meshes.append(mesh)
        records.append({'key':key,'file':path.name,'assembly':pose.tolist(),'bounds_mm':mesh.bounds.tolist(),
                        'size_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),
                        'closed':True,'faces':len(mesh.faces)})
    collisions=[]
    for i,(sa,_) in enumerate(assembled):
        for j,(sb,_) in enumerate(assembled[i+1:],i+1):
            v=(sa^sb).volume()
            if v>.005:collisions.append([parts[i][0],parts[j][0],v])
    assert not collisions,collisions
    # Actual insertion travel, not only a final-position intersection check.
    insertion_checks=0
    for key,solid,pose in fins+cones+nozzles:
        direction=pose[:3,1] if key.startswith('deriva') else pose[:3,2]
        placed=solid.transform(pose[:3].tolist())
        for distance in np.linspace(0,5,11):
            hit=(placed.translate((direction*distance).tolist())^body).volume()
            assert hit<.005,(key,distance,hit)
            insertion_checks+=1
    all_vertices=np.vstack([mesh_of(s).vertices for s,c in assembled])
    bounds=[all_vertices.min(0).tolist(),all_vertices.max(0).tolist()]
    report={'draft':True,'version':1,'variant':'SR-71A, static display, gear retracted',
            'scale_nominal':'1:144','target_length_span_mm':[LENGTH,SPAN],
            'assembled_bounds_mm':bounds,'assembled_size_mm':np.ptp(all_vertices,axis=0).tolist(),
            'principal_parts':8,'alignment_pins':3,'all_parts_closed':True,
            'fuselage_source_profiles':145,'fuselage_loft_rings':460,'profile_samples':96,
            'wing_nominal_full_thickness_mm':1.44,'wing_thickness_at_corrugations_mm':1.28,'fin_thickness_mm':1.2,'pitot_min_diameter_mm':.7,
            'tail_cant_degrees_inward':15,'pin_diameter_mm':2.4,'pin_socket_diameter_mm':2.7,
            'pin_length_mm':4.2,'pin_socket_total_depth_mm':4.5,
            'fin_and_engine_insert_clearance_per_side_mm':.15,
            'intake_internal_roof_min_nominal_wall_mm':.65,
            'exhaust_round_socket_depth_mm':1.45,
            'panel_groove_width_range_mm':[.34,.42],'panel_groove_depth_range_mm':[.18,.24],
            'wing_corrugation_grooves_mm':[.42,.16],'insertion_positions_checked':insertion_checks,
            'pairwise_collisions_mm3':collisions,'physical_fit_tested':False,
            'microscopic_stl_precision_repairs':repairs,
            'engineering_accuracy_claimed':False,'individual_airframe_markings_included':False,
            'source':'FGMEMBERS/SR71-BlackBird, commit 1de3f88ab7255b54f8cc22eec36d4632c2ce16a0',
            'source_authors':'Gerard Robin, with modifications by l0k1; see original README',
            'license':'GPL-2.0, applies to this derivative and included FlightGear sources',
            'geometry_notes':'Printable loft reconstructed from convex exterior sections; dimensions calibrated independently in span/length. Panel/groove placement and engine internal segments simplified for FDM.',
            'parts':records}
    (FOLDER/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (FOLDER/'assembly.json').write_text(json.dumps({'units':'mm','parts':records},indent=2)+'\n')
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (FOLDER/'reference').iterdir() if p.is_file()}
    (FOLDER/'source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
    fit_sample()
    # A digital assembly for inspection (not the print arrangement).
    scene=trimesh.Scene()
    for record,(solid,color) in zip(records,assembled):
        mesh=mesh_of(solid);mesh.visual.vertex_colors=trimesh.visual.color.hex_to_rgba(color)
        scene.add_geometry(mesh,node_name=record['key'])
    scene.export(ROOT/'downloads'/f'{PREFIX}-montado.glb')
    # Render the validated serialized solids. The unsimplified CSG history has
    # many redundant coplanar triangles and is needlessly expensive to draw.
    draw_parts=[(record['key'],manifold(mesh),np.array(record['assembly']))
                for record,mesh in zip(records,meshes)]
    draw_assembly=[(solid.transform(pose[:3].tolist()),BLACK) for key,solid,pose in draw_parts]
    illustrate(draw_assembly,draw_parts,report)
    shutil.copy2(Path(__file__),FOLDER/'generate_sr71_draft_v1.py')
    shutil.copy2(Path(__file__).with_name('sr71_reference.py'),FOLDER/'sr71_reference.py')
    log(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2))


def illustrate(assembled,parts,report):
    font=lambda n:ImageFont.truetype(FONT,n)
    canvas=Image.new('RGB',(1800,1320),'#f4f6f8');d=ImageDraw.Draw(canvas)
    d.text((40,25),'SR-71A Blackbird — primeiro draft CAD',font=font(38),fill=BLUE)
    d.text((40,82),'1:144 · cerca de 227 × 118 mm · 8 peças principais + 3 cavilhas · geometria real do draft',font=font(25),fill=BLUE)
    canvas.paste(render_meshes(assembled,(1380,1130),direction=(.65,-.8,.85)),(0,140))
    engine_parts=[p for p in assembled if mesh_of(p[0]).bounds[0,0]>15]
    # A clipped engine detail from the actual assembled model.
    clip=md.Manifold.cube((25,105,45)).translate((18,108,-15))
    detail=[(s^clip,c) for s,c in assembled if (s^clip).volume()>.01]
    canvas.paste(render_meshes(detail,(440,510),direction=(.7,.9,.8),margin=35),(1340,150))
    d.text((1350,685),'Motores: cones, grelhas',font=font(21),fill=BLUE)
    d.text((1350,717),'e tubeiras com segmentos.',font=font(21),fill=BLUE)
    d.text((1350,800),'Painéis e cabine gravados;',font=font(21),fill=BLUE)
    d.text((1350,833),'corrugações nas asas.',font=font(21),fill=BLUE)
    d.text((1350,920),'Derivas inclinadas',font=font(21),fill=BLUE)
    d.text((1350,953),'15° para dentro.',font=font(21),fill=BLUE)
    d.text((40,1270),'Modelo de exposição, adaptado a FDM · detalhes simplificados · montagem física ainda por testar',font=font(24),fill=BLUE)
    canvas.save(ROOT/'designs'/f'{PREFIX}-CAD.png')
    top=Image.new('RGB',(1800,1300),'#f4f6f8');dt=ImageDraw.Draw(top)
    dt.text((40,25),'SR-71A — vistas e detalhes do CAD',font=font(36),fill=BLUE)
    top.paste(render_meshes(assembled,(900,1120),direction=(0,-.00001,1)),(0,110))
    top.paste(render_meshes(assembled,(850,570),direction=(1,0,.035)),(930,130))
    top.paste(render_meshes(detail,(800,480),direction=(.2,1,.18)),(950,710))
    dt.text((960,670),'Vista lateral · dois lugares e derivas inclinadas',font=font(22),fill=BLUE)
    dt.text((960,1200),'Detalhe traseiro do motor: peça separada para imprimir.',font=font(20),fill=BLUE)
    dt.text((40,1255),'A imagem mostra os sólidos para impressão; não representa pintura ou decalques.',font=font(24),fill=BLUE)
    top.save(ROOT/'designs'/f'{PREFIX}-vistas.png')
    exploded=[]
    for key,solid,pose in parts:
        offset=np.zeros(3)
        if key=='superior':offset[2]=17
        elif key.startswith('deriva'):offset[2]=30
        elif key.startswith('cone'):offset[1]=-24
        elif key.startswith('tubeira'):offset[1]=18
        color={'superior':'#536878','inferior':'#92A5B0'}.get(key,'#BD824B' if key.startswith('cavilha') else '#394A5D')
        exploded.append((solid.transform(pose[:3].tolist()).translate(offset.tolist()),color))
    picture=Image.new('RGB',(1800,1320),'#f4f6f8');de=ImageDraw.Draw(picture)
    de.text((40,25),'SR-71A — divisão e montagem das peças',font=font(36),fill=BLUE)
    de.text((40,82),'Cores apenas para distinguir as peças nesta vista; projeto de impressão em preto.',font=font(24),fill=BLUE)
    picture.paste(render_meshes(exploded,(1750,1100),direction=(.65,-.8,.75)),(25,140))
    de.text((40,1270),'União horizontal · cavilhas separadas · cones e tubeiras de encaixar e colar · derivas com dois encaixes',font=font(23),fill=BLUE)
    picture.save(ROOT/'designs'/f'{PREFIX}-montagem.png')


if __name__=='__main__':
    main()
