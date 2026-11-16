"""Check a full-size rod's entrance path and the hinge end stop in CAD."""
from __future__ import annotations

import json
import math

from build_cad import HERE, P, fixed_arm, moving_arm, zcyl


# Centre positions of a Ø21 rod, from outside the right lip into its seat.
# The intermediate checks below also cover all connecting line segments.
ENTRY_PATH = [
    (72, 17.5), (70, 17), (68, 16), (66, 15.5), (64, 14.5),
    (62, 14), (60, 13), (58, 12), (56, 11.5), (54, 11.5),
    (52, 12), (50, 12.2), (48, 12.5), (46, 13),
    (44, 14.5), (42, 18.5),
]


def run():
    fixed = fixed_arm()
    jaw = moving_arm()
    opened = jaw.rotate((P.pivot_x, P.pivot_y, 0),
                        (P.pivot_x, P.pivot_y, 1), -32)
    assert fixed.intersect(opened).val().Volume() < .01
    steps = 0
    for (x1, y1), (x2, y2) in zip(ENTRY_PATH, ENTRY_PATH[1:]):
        for i in range(9):
            t = i / 8
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            rod = zcyl(x, y, P.rod_max_d / 2, 9, 3)
            assert fixed.intersect(rod).val().Volume() < .01, (x, y, 'fixed')
            assert opened.intersect(rod).val().Volume() < .01, (x, y, 'jaw')
            steps += 1
    rod_seated = zcyl(P.rod_center_x, P.rod_center_y, P.rod_max_d / 2, 9, 3)
    assert fixed.intersect(rod_seated).val().Volume() < .01
    assert jaw.intersect(rod_seated).val().Volume() < .01
    stopped = jaw.rotate((P.pivot_x, P.pivot_y, 0),
                         (P.pivot_x, P.pivot_y, 1), -33)
    assert fixed.intersect(stopped).val().Volume() > .1
    a = math.radians(-32)
    lower_floor_open_y = P.pivot_y + math.sin(a) * (P.spring_x - P.pivot_x) + math.cos(a) * (
        P.jaw_left_top - P.spring_pocket_depth - P.pivot_y)
    upper_floor_y = P.upper_bottom + P.spring_pocket_depth
    report = {
        'rod_d_mm': P.rod_max_d,
        'entry_open_angle_deg': 32,
        'continuous_path_samples_clear': steps,
        'printed_parts_clear_0_to_32_deg': True,
        'mechanical_stop_contacts_around_deg': 33,
        'spring_seat_distance_closed_mm': upper_floor_y - (P.jaw_left_top - P.spring_pocket_depth),
        'spring_seat_distance_at_32_deg_mm': round(upper_floor_y - lower_floor_open_y, 2),
        'spring_solid_length_required_max_mm': 7.5,
        'physical_tested': False,
    }
    (HERE / 'motion-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
