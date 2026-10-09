"""Check the replacement socket against the existing plaque and API units."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'fusion/EssencialBasePremium/EssencialBasePremium.py'
REFERENCE = ROOT / 'fusion/EssencialA1Reviews/EssencialA1Reviews.py'


def pure_values(path, functions=()):
    tree = ast.parse(path.read_text())
    subset = [n for n in tree.body if isinstance(n, ast.Assign) or
              (isinstance(n, ast.FunctionDef) and n.name in functions)]
    values = {'math': math}
    exec(compile(ast.Module(body=subset, type_ignores=[]), str(path), 'exec'), values)
    return values, tree


class BaseCompatibility(unittest.TestCase):
    def setUp(self):
        self.v, self.tree = pure_values(
            SCRIPT, ('dimensions', 'bevel_profile', 'validate_dimensions'))
        self.original, _ = pure_values(REFERENCE)

    def test_fit_and_footprint_match_existing_plate_without_scaling(self):
        for name in ('PANEL_THICKNESS', 'TONGUE_WIDTH', 'TONGUE_DEPTH',
                     'FIT_CLEARANCE_PER_SIDE', 'END_CLEARANCE_PER_SIDE',
                     'BOTTOM_CLEARANCE', 'ENTRY_EXTRA_PER_SIDE', 'ENTRY_DEPTH',
                     'BASE_WIDTH', 'BASE_DEPTH', 'BASE_HEIGHT'):
            self.assertEqual(self.v[name], self.original[name], name)
        d = self.v['validate_dimensions']()
        for name, expected in {
                'slot_length': 120.6, 'slot_width': 5.5, 'slot_depth': 12.8,
                'slot_floor': 5.2, 'entry_length': 121.6,
                'entry_width': 6.5, 'entry_floor': 17.0}.items():
            self.assertAlmostEqual(d[name], expected, msg=name)

    def test_full_tongue_has_room_without_touching_floor_or_walls(self):
        d = self.v['dimensions']()
        # Actual tongue at the centre of the support with its shoulder at Z18.
        tongue = (20, 32.5, 6, 140, 37.5, 18)
        socket = (d['slot_x'], d['slot_y'], d['slot_floor'],
                  d['slot_x']+d['slot_length'],
                  d['slot_y']+d['slot_width'], 18)
        for actual, expected in zip(
                [tongue[i]-socket[i] for i in range(3)], (0.3, 0.25, 0.8)):
            self.assertAlmostEqual(actual, expected)
        for i, gap in ((3, 0.3), (4, 0.25)):
            self.assertAlmostEqual(socket[i]-tongue[i], gap)
        self.assertLessEqual(160+10, 256)
        self.assertLessEqual(70+10, 256)

    def test_bevel_and_fillets_leave_the_entire_socket_on_flat_deck(self):
        v = self.v
        d = v['dimensions']()
        front = d['slot_y'] - v['ENTRY_EXTRA_PER_SIDE']
        back = front + d['entry_width']
        left = d['slot_x'] - v['ENTRY_EXTRA_PER_SIDE']
        right = left + d['entry_length']
        self.assertGreater(front, v['FRONT_BEVEL'] + v['TOP_EDGE_RADIUS'])
        self.assertGreater(front, v['CORNER_RADIUS'] + v['TOP_EDGE_RADIUS'])
        self.assertGreater(70-back, v['CORNER_RADIUS'] + v['TOP_EDGE_RADIUS'])
        self.assertGreater(left, v['CORNER_RADIUS'] + v['TOP_EDGE_RADIUS'])
        self.assertGreater(160-right, v['CORNER_RADIUS'] + v['TOP_EDGE_RADIUS'])
        # The cutter's diagonal intersects front at Z10 and top at Y8.
        a, _, c = v['bevel_profile']()
        slope = (c[1]-a[1])/(c[0]-a[0])
        self.assertAlmostEqual(slope, 1)
        self.assertAlmostEqual(a[1]-slope*a[0], 10)
        self.assertAlmostEqual((18-a[1])/slope+a[0], 8)
        self.assertEqual(d['front_height'], 10)

    def test_invalid_changes_cannot_silently_remove_socket_floor(self):
        self.v['BASE_HEIGHT'] = 14
        with self.assertRaisesRegex(ValueError, 'below the socket'):
            self.v['validate_dimensions']()

    def test_large_bevel_cannot_reach_socket(self):
        self.v['BASE_HEIGHT'] = 40
        self.v['FRONT_BEVEL'] = 32
        with self.assertRaisesRegex(ValueError, 'too close'):
            self.v['validate_dimensions']()

    def test_rectangle_cut_uses_centimetres_and_correct_actual_extents(self):
        node = next(n for n in ast.walk(self.tree)
                    if isinstance(n, ast.FunctionDef) and n.name == 'rectangle_cut')
        lines, planes, extrusions = [], [], []
        def line(a, b):
            lines.append((a, b))
        def plane(reference, offset):
            planes.append((reference, offset))
            return 'offset plane'
        def extrude(sk, name, distance, operation):
            extrusions.append((distance, operation))
        self.v.update({
            'point': lambda x,y: (x/10, y/10),
            'component': SimpleNamespace(xYConstructionPlane='XY'),
            'offset_plane': plane,
            'sketch': lambda name, p: SimpleNamespace(sketchCurves=SimpleNamespace(
                sketchLines=SimpleNamespace(addByTwoPoints=line))),
            'extrude': extrude,
            'ops': SimpleNamespace(CutFeatureOperation='cut'),
        })
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'socket cut', 'exec'),
             self.v)
        d = self.v['dimensions']()
        self.v['rectangle_cut']('Socket', d['slot_x'], d['slot_y'],
                                d['slot_length'], d['slot_width'], d['slot_floor'])
        self.assertEqual(planes[0][0], 'XY')
        self.assertAlmostEqual(planes[0][1], 5.2)
        xs = [p[0]*10 for line in lines for p in line]
        ys = [p[1]*10 for line in lines for p in line]
        self.assertAlmostEqual(min(xs), 19.7)
        self.assertAlmostEqual(max(xs), 140.3)
        self.assertAlmostEqual(min(ys), 32.25)
        self.assertAlmostEqual(max(ys), 37.75)
        self.assertAlmostEqual(extrusions[0][0], 13.8)
        self.assertEqual(extrusions[0][1], 'cut')
        # Loop closure: no disconnected profile edges.
        for edge, next_edge in zip(lines, lines[1:]+lines[:1]):
            self.assertEqual(edge[1], next_edge[0])


if __name__ == '__main__':
    unittest.main()
