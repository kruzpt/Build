"""64 mm QR layout and batch extrusion regression checks."""
import ast
from pathlib import Path
import unittest

import test_v3_geometry as geometry_tests
import test_v3_fast as fast_tests

SCRIPT=Path(__file__).resolve().parents[1]/'EssencialV4/EssencialV4.py'


class V4Geometry(geometry_tests.V3Inputs):
    @classmethod
    def setUpClass(cls):
        previous=geometry_tests.SCRIPT
        try:
            geometry_tests.SCRIPT=SCRIPT
            super().setUpClass()
        finally:
            geometry_tests.SCRIPT=previous

    def test_enlarged_fields_and_projections_fit_panel(self):
        v=self.v
        self.assertEqual(v['QR_SIZE'],64)
        self.assertEqual(v['PANEL_WIDTH'],200)
        self.assertEqual(v['PANEL_HEIGHT'],220)
        for name,rows,bottom in v['row_layout']():
            self.assertGreaterEqual(v['QR_SIZE']/len(rows)-0.02,1.4)
            self.assertGreater(bottom,0)
            self.assertLess(bottom+v['QR_SIZE'],v['PANEL_HEIGHT'])
        for region,number,x,y,w,h in v['vertebra_layout']():
            scale=1 if region=='C' else (1.15 if region=='T' else 1.35)
            self.assertLess(x+w*.2+9*scale,v['PANEL_WIDTH'])
        # Clinic text boxes must be above the upper field, below the logo.
        labels=[]
        for node in ast.walk(self.tree):
            if (isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                    and node.func.id=='label'):
                labels.append([ast.literal_eval(arg) for arg in node.args])
        highest_qr=max(bottom+v['QR_SIZE'] for _,_,bottom in v['row_layout']())
        for name,x,y,width,height in labels:
            self.assertGreater(y,highest_qr)
            self.assertLess(y+height+3,v['LOGO_Y']-v['LOGO_RADIUS'])


class V4Batch(unittest.TestCase):
    def test_batch_keeps_links_fit_and_pause_but_scales_modules(self):
        previous=fast_tests.SCRIPT
        try:
            fast_tests.SCRIPT=SCRIPT
            v,original,sketches,extrusions=fast_tests.BatchAPI().fixture()
        finally:
            fast_tests.SCRIPT=previous
        for name in ['PANEL_HEIGHT','PANEL_THICKNESS','BASE_WIDTH','BASE_DEPTH',
                     'BASE_HEIGHT','TONGUE_WIDTH','TONGUE_DEPTH',
                     'FIT_CLEARANCE_PER_SIDE','END_CLEARANCE_PER_SIDE',
                     'BOTTOM_CLEARANCE','NFC_CAVITY_DIAMETER','NFC_PAUSE_Z']:
            self.assertEqual(v[name],original[name],name)
        self.assertEqual(v['INSTAGRAM_ROWS'],original['INSTAGRAM_ROWS'])
        self.assertEqual(v['GOOGLE_ROWS'],original['GOOGLE_ROWS'])
        self.assertEqual(v['logo_contours'](),original['logo_contours']())
        for name,rows,bottom in v['row_layout']():
            v['build_qr'](name,rows,bottom)
            p=64/len(rows)
            expected=[(v['QR_X']+start*p+0.01,
                       bottom+(len(rows)-row-1)*p+0.01,
                       v['QR_X']+end*p-0.01,
                       bottom+(len(rows)-row)*p-0.01)
                      for row,start,end in v['qr_runs'](rows)]
            actual=[edges[0][0]+edges[1][1] for edges in extrusions[-1][0]]
            self.assertEqual(actual,expected)
        self.assertEqual(len(sketches),2)
        self.assertEqual(len(extrusions),2)
        self.assertEqual([len(e[0]) for e in extrusions],[352,276])


if __name__=='__main__':
    unittest.main()
