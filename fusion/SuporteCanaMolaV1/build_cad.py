"""Parametric rod clip prototype. Coordinates and dimensions are millimetres.

The rod is viewed along Z. The fixed blue arm is above, the pivoting lower arm
below; the compression spring is housed between their left ends.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

import cadquery as cq


HERE = Path(__file__).resolve().parent
OUT = HERE / "stl"


@dataclass(frozen=True)
class Parameters:
    body_width: float = 67.0
    body_height: float = 37.0
    depth: float = 20.0  # permits a flush M3 x 20 pivot screw with a recessed nut
    upper_bottom: float = 23.0
    jaw_left_top: float = 11.0
    rod_center_x: float = 42.0
    rod_center_y: float = 18.5
    rod_max_d: float = 21.0  # provisional maximum, not a measured rod
    rod_radial_clearance: float = 0.7
    pivot_x: float = 20.5
    pivot_y: float = 19.0
    pivot_clearance_d: float = 3.3
    fixed_ear_radius: float = 5.3
    moving_ear_radius: float = 3.65
    ear_thickness: float = 4.6
    moving_ear_z_clearance: float = 0.4
    spring_x: float = 9.0
    spring_z: float = 10.0
    spring_pocket_d: float = 6.3
    spring_pocket_depth: float = 2.0
    spring_free_length: float = 17.0  # specify actual spring before assembly
    mount_clearance_d: float = 3.5
    mount_head_d: float = 6.5
    mount_head_depth: float = 2.8


P = Parameters()


def zcyl(x: float, y: float, radius: float, z0: float, length: float):
    return cq.Workplane("XY").center(x, y).circle(radius).extrude(length).translate((0, 0, z0))


def ycyl(x: float, z: float, radius: float, y0: float, length: float):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def fixed_arm(p: Parameters = P):
    shell = cq.Workplane("XY").box(
        p.body_width, p.body_height - p.upper_bottom, p.depth,
        centered=(False, False, False)).translate((0, p.upper_bottom, 0))
    for z0 in (0, p.depth - p.ear_thickness):
        shell = shell.union(zcyl(p.pivot_x, p.pivot_y, p.fixed_ear_radius, z0, p.ear_thickness))
    rod_r = p.rod_max_d / 2 + p.rod_radial_clearance
    shell = shell.cut(zcyl(p.rod_center_x, p.rod_center_y, rod_r, -1, p.depth + 2))
    # A short 5 mm relief at the entrance lets a full-size rod pass with less
    # jaw rotation. The closed throat stays far narrower than the rod.
    entry_relief = cq.Workplane("XY").box(13, 5, p.depth + 2,
                    centered=(False, False, False)).translate((54, 23, -1))
    shell = shell.cut(entry_relief)
    shell = shell.cut(zcyl(p.pivot_x, p.pivot_y, p.pivot_clearance_d / 2, -1, p.depth + 2))
    # A recessed M3 nut keeps the wall-facing surface flat.
    nut = cq.Workplane("XY").center(p.pivot_x, p.pivot_y).polygon(6, 6.65).extrude(2.7)
    shell = shell.cut(nut)
    for x, y in ((6.0, 30.5), (61.0, 32.5)):
        shell = shell.cut(zcyl(x, y, p.mount_clearance_d / 2, -1, p.depth + 2))
        shell = shell.cut(zcyl(x, y, p.mount_head_d / 2,
                               p.depth - p.mount_head_depth, p.mount_head_depth + 1))
    # The two opposed pockets retain a compression spring without side walls.
    shell = shell.cut(ycyl(p.spring_x, p.spring_z, p.spring_pocket_d / 2,
                          p.upper_bottom - 3, p.spring_pocket_depth + 3))
    return shell.clean()


def moving_arm(p: Parameters = P):
    # The right-hand nose projects 3 mm past the fixed arm; its edge is rounded.
    profile = [
        (0, 0), (p.body_width, 0), (p.body_width, 15.0),
        (70.0, 23.3), (68.8, 23.2), (67.0, 21.4),
        (64.0, 19.6), (56.0, 16.2), (53.0, 19.0),
        (33.0, 19.0), (29.0, 15.0), (24.0, 12.0),
        (0, p.jaw_left_top),
    ]
    jaw = cq.Workplane("XY").polyline(profile).close().extrude(p.depth)
    # Round the exposed entrance point to protect the rod and avoid a fragile tip.
    try:
        jaw = jaw.edges("|Z and >X").fillet(0.55)
    except Exception as exc:
        raise RuntimeError("The entry nose fillet failed") from exc
    # A broad stop at the far left meets the fixed arm just after the required
    # opening travel; it keeps the spring from being crushed by over-rotation.
    stop = cq.Workplane("XY").box(2, 1.5, p.depth,
                centered=(False, False, False)).translate((3, p.jaw_left_top, 0))
    jaw = jaw.union(stop)
    rod_r = p.rod_max_d / 2 + p.rod_radial_clearance
    jaw = jaw.cut(zcyl(p.rod_center_x, p.rod_center_y, rod_r, -1, p.depth + 2))

    z0 = p.ear_thickness + p.moving_ear_z_clearance
    zlen = p.depth - 2 * z0
    boss = zcyl(p.pivot_x, p.pivot_y, p.moving_ear_radius, z0, zlen)
    bridge = cq.Workplane("XY").polyline([
        (16.0, 9.0), (25.0, 9.0), (24.5, 14.0),
        (23.0, 19.0), (18.5, 19.0), (16.0, 13.0),
    ]).close().extrude(zlen).translate((0, 0, z0))
    jaw = jaw.union(bridge).union(boss)
    jaw = jaw.cut(zcyl(p.pivot_x, p.pivot_y, p.pivot_clearance_d / 2, -1, p.depth + 2))
    jaw = jaw.cut(ycyl(p.spring_x, p.spring_z, p.spring_pocket_d / 2,
                        p.jaw_left_top - p.spring_pocket_depth, p.spring_pocket_depth + 3))
    return jaw.clean()


def normalize_step(path: Path):
    # OpenCascade writes line-end spaces; remove them without changing STEP data.
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')


def save():
    OUT.mkdir(exist_ok=True)
    fixed = fixed_arm()
    jaw = moving_arm()
    for name, part in (("fixed_arm", fixed), ("moving_arm", jaw)):
        shape = part.val()
        assert shape.isValid(), name
        assert len(shape.Solids()) == 1, (name, len(shape.Solids()))
        cq.exporters.export(part, str(OUT / f"{name}.stl"), tolerance=0.045, angularTolerance=0.12)
        cq.exporters.export(part, str(HERE / f"{name}.step"))
        normalize_step(HERE / f"{name}.step")

    # First plate: the exact left-hand hinge and spring features, shortened at X=28.
    coupon_clip = cq.Workplane("XY").box(28, 42, P.depth,
                 centered=(False, False, False)).translate((0, -2, 0))
    for name, part in (("fixed_coupon", fixed.intersect(coupon_clip)),
                       ("moving_coupon", jaw.intersect(coupon_clip))):
        assert part.val().isValid() and len(part.val().Solids()) == 1, name
        cq.exporters.export(part, str(OUT / f"{name}.stl"),
                            tolerance=0.045, angularTolerance=0.12)

    assy = cq.Assembly(name="SuporteCanaMolaV1")
    assy.add(fixed, name="braco_fixo", color=cq.Color("#2d4350"))
    assy.add(jaw, name="mordente_movel", color=cq.Color("#e7a258"))
    assy.save(str(HERE / "suporte-cana-mola-v1-assembly.step"))
    normalize_step(HERE / "suporte-cana-mola-v1-assembly.step")

    # At closed and opening positions the two printed solids must not intersect.
    collisions = {}
    for degrees in (0, -5, -10, -15, -20, -25, -30, -32):
        rotated = jaw.rotate((P.pivot_x, P.pivot_y, 0), (P.pivot_x, P.pivot_y, 1), degrees)
        collision = fixed.intersect(rotated).val().Volume()
        collisions[str(degrees)] = round(collision, 4)
        assert collision < 0.01, (degrees, collision)

    report = {
        "parameters_mm": asdict(P),
        "fixed_volume_mm3": round(fixed.val().Volume(), 2),
        "moving_volume_mm3": round(jaw.val().Volume(), 2),
        "fixed_bounds_mm": [[round(v, 3) for v in (fixed.val().BoundingBox().xmin,
                            fixed.val().BoundingBox().ymin, fixed.val().BoundingBox().zmin)],
                            [round(v, 3) for v in (fixed.val().BoundingBox().xmax,
                            fixed.val().BoundingBox().ymax, fixed.val().BoundingBox().zmax)]],
        "moving_bounds_mm": [[round(v, 3) for v in (jaw.val().BoundingBox().xmin,
                             jaw.val().BoundingBox().ymin, jaw.val().BoundingBox().zmin)],
                             [round(v, 3) for v in (jaw.val().BoundingBox().xmax,
                             jaw.val().BoundingBox().ymax, jaw.val().BoundingBox().zmax)]],
        "intersection_volume_mm3_by_angle": collisions,
        "physical_fit_tested": False,
    }
    (HERE / "cad-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    save()
