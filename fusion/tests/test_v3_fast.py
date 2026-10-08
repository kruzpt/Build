"""Execute the batch routine with a minimal Fusion API substitute."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import test_v3_geometry as geometry_tests

SCRIPT=Path(__file__).resolve().parents[1]/'EssencialV3Fast/EssencialV3Fast.py'


class FastGeometry(geometry_tests.V3Inputs):
    @classmethod
    def setUpClass(cls):
        original=geometry_tests.SCRIPT
        try:
            geometry_tests.SCRIPT=SCRIPT
            super().setUpClass()
        finally:
            geometry_tests.SCRIPT=original


class Collection(list):
    def add(self,value):
        self.append(value)


class BatchAPI(unittest.TestCase):
    def fixture(self,profile_bias=0):
        tree=ast.parse(SCRIPT.read_text())
        original_tree=ast.parse(geometry_tests.SCRIPT.read_text())
        pure={'sample_path','logo_contours','qr_runs','sector_contour',
              'row_layout','vertebra_layout'}
        def values(tree):
            import math
            v={'math':math}
            subset=[n for n in tree.body if isinstance(n,ast.Assign)
                    or (isinstance(n,ast.FunctionDef) and n.name in pure)]
            exec(compile(ast.Module(body=subset,type_ignores=[]),'pure geometry','exec'),v)
            return v
        v=values(tree)
        original=values(original_tree)
        sketches=[]
        extrusions=[]

        class Lines:
            def __init__(self):
                self.edges=[]
            def addByTwoPoints(self,a,b):
                self.edges.append((a,b))

        class Sketch:
            def __init__(self,name):
                self.name=name
                self.isComputeDeferred=True
                self.isVisible=False
                self.lines=Lines()
                self.sketchCurves=SimpleNamespace(sketchLines=self.lines)
                self.profiles=Profiles(self)

        class Profiles:
            def __init__(self,sk):
                self.sk=sk
            @property
            def count(self):
                # Accessing profiles must occur after the deferred solve ends.
                assert not self.sk.isComputeDeferred
                return len(self.sk.lines.edges)//4+profile_bias
            def item(self,index):
                return self.sk.lines.edges[index*4:(index+1)*4]

        def sketch(c,name,z):
            sk=Sketch(name)
            sketches.append(sk)
            return sk

        def extrude(profiles,distance,operation):
            extrusions.append((profiles,distance,operation))
            return SimpleNamespace(name='')

        v.update({
            'c':SimpleNamespace(features=SimpleNamespace(
                extrudeFeatures=SimpleNamespace(addSimple=extrude))),
            'sketch':sketch,
            'point':lambda x,y:(x,y),
            'update_progress':lambda value,message:None,
            'ops':SimpleNamespace(JoinFeatureOperation='join'),
            'adsk':SimpleNamespace(core=SimpleNamespace(
                ObjectCollection=SimpleNamespace(create=Collection),
                ValueInput=SimpleNamespace(createByReal=lambda value:value)))})
        function=next(n for n in ast.walk(tree)
                      if isinstance(n,ast.FunctionDef) and n.name=='build_qr')
        exec(compile(ast.Module(body=[function],type_ignores=[]),'batch routine','exec'),v)
        return v,original,sketches,extrusions

    def test_two_extrusions_preserve_all_original_qr_rectangles(self):
        v,original,sketches,extrusions=self.fixture()
        self.assertEqual(v['row_layout'](),original['row_layout']())
        self.assertEqual(v['logo_contours'](),original['logo_contours']())
        self.assertEqual(v['vertebra_layout'](),original['vertebra_layout']())
        for name,rows,bottom in original['row_layout']():
            v['build_qr'](name,rows,bottom)
            sk=sketches[-1]
            actual=[edges[0][0]+edges[1][1]
                    for edges in extrusions[-1][0]]
            p=original['QR_SIZE']/len(rows)
            expected=[(original['QR_X']+start*p+0.01,
                       bottom+(len(rows)-row-1)*p+0.01,
                       original['QR_X']+end*p-0.01,
                       bottom+(len(rows)-row)*p-0.01)
                      for row,start,end in original['qr_runs'](rows)]
            self.assertEqual(actual,expected)
            self.assertFalse(sk.isComputeDeferred)
            self.assertFalse(sk.isVisible)
            self.assertEqual(extrusions[-1][1:],(0.062,'join'))
        self.assertEqual(len(sketches),2)
        self.assertEqual(len(extrusions),2)
        self.assertEqual([len(e[0]) for e in extrusions],[352,276])

    def test_missing_profile_is_reported_before_extrusion(self):
        v,original,sketches,extrusions=self.fixture(profile_bias=-1)
        name,rows,bottom=original['row_layout']()[0]
        with self.assertRaisesRegex(RuntimeError,'unexpected profile count'):
            v['build_qr'](name,rows,bottom)
        self.assertEqual(extrusions,[])


if __name__=='__main__':
    unittest.main()
