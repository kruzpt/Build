"""Checks for Fusion geometry inputs; no Autodesk installation required."""
import ast
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'EssencialV2' / 'EssencialV2.py'


class GeometryInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SCRIPT.read_text(encoding='utf-8'))
        cls.arc_points = []
        for node in ast.walk(cls.tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'addByThreePoints'):
                cls.arc_points.append([
                    tuple(ast.literal_eval(value) for value in point.args)
                    for point in node.args
                ])
        subset = [node for node in cls.tree.body
                  if isinstance(node, ast.Assign)
                  or (isinstance(node, ast.FunctionDef)
                      and node.name == 'vertebra_layout')]
        cls.values = {'math': math}
        exec(compile(ast.Module(body=subset, type_ignores=[]),
                     str(SCRIPT), 'exec'), cls.values)

    def test_three_point_arcs_are_not_collinear(self):
        self.assertEqual(len(self.arc_points), 3)
        for scale in (1.0, 1.15, 1.35):
            for points in self.arc_points:
                with self.subTest(scale=scale, points=points):
                    a, b, c = points
                    cross = ((b[0]-a[0])*(c[1]-a[1])
                             - (b[1]-a[1])*(c[0]-a[0])) * scale**2
                    # A degenerate circle is exactly the user's Fusion failure.
                    self.assertGreater(abs(cross), 1e-6)

    def test_curved_outline_has_connected_arcs(self):
        for previous, following in zip(self.arc_points, self.arc_points[1:]):
            self.assertEqual(previous[-1], following[0])

    def test_vertebrae_stay_inside_panel_with_disc_gaps(self):
        layout = self.values['vertebra_layout']()
        self.assertEqual(len(layout), 24)
        for region, number, x, y, width, height in layout:
            self.assertGreater(x-width/2, 0)
            self.assertLess(x+width/2, self.values['PANEL_WIDTH'])
            self.assertGreater(y-height/2, 0)
            self.assertLess(y+height/2, self.values['PANEL_HEIGHT'])
        for lower, upper in zip(layout, layout[1:]):
            gap = upper[3]-upper[5]/2-lower[3]-lower[5]/2
            self.assertAlmostEqual(gap, self.values['DISC_GAP'])

    def test_socket_has_clearance_and_solid_floor(self):
        v = self.values
        self.assertGreater(v['FIT_CLEARANCE_PER_SIDE'], 0)
        self.assertGreater(v['END_CLEARANCE_PER_SIDE'], 0)
        self.assertGreater(v['BOTTOM_CLEARANCE'], 0)
        floor = v['BASE_HEIGHT']-v['TONGUE_DEPTH']-v['BOTTOM_CLEARANCE']
        self.assertGreaterEqual(floor, 4)
        self.assertLess(v['ENTRY_DEPTH'], v['TONGUE_DEPTH'])


if __name__ == '__main__':
    unittest.main()
