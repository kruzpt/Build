"""Validate the entire printable outline against the A1, including brim."""
import ast
import math
from pathlib import Path
import unittest

import test_v3_geometry as geometry_tests

SCRIPT=Path(__file__).resolve().parents[1]/'EssencialA1/EssencialA1.py'


class A1Geometry(geometry_tests.V3Inputs):
    @classmethod
    def setUpClass(cls):
        previous=geometry_tests.SCRIPT
        try:
            geometry_tests.SCRIPT=SCRIPT
            super().setUpClass()
        finally:
            geometry_tests.SCRIPT=previous

    def test_complete_outline_including_logo_tongue_and_brim_fits(self):
        v=self.v
        width=max(v['PANEL_WIDTH'],v['LOGO_X']+v['LOGO_RADIUS'])-min(
            0,v['LOGO_X']-v['LOGO_RADIUS'])
        height=max(v['PANEL_HEIGHT'],v['LOGO_Y']+v['LOGO_RADIUS'])+v['TONGUE_DEPTH']
        self.assertEqual((width,height),(208,242))
        self.assertLessEqual(width+10,256)
        self.assertLessEqual(height+10,256)
        self.assertLessEqual(v['BASE_WIDTH']+10,256)
        self.assertLessEqual(v['BASE_DEPTH']+10,256)

    def test_text_is_beside_logo_inside_panel_and_above_qr(self):
        v=self.v
        highest_qr=max(bottom+v['QR_SIZE'] for _,_,bottom in v['row_layout']())
        for node in ast.walk(self.tree):
            if (isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                    and node.func.id=='label'):
                name,x,y,width,height=[ast.literal_eval(a) for a in node.args]
                self.assertGreater(x,v['LOGO_X']+v['LOGO_RADIUS'])
                self.assertGreater(y,highest_qr)
                self.assertLess(y+height+3,v['PANEL_HEIGHT'])
                for region,number,sx,sy,w,h in v['vertebra_layout']():
                    if sy+h/2>=y and sy-h/2<=y+height+3:
                        self.assertGreater(sx-w/2,x+width)

    def test_no_global_scaling_of_qr_nfc_or_fit(self):
        v=self.v
        source=SCRIPT.parents[1]/'EssencialV4/EssencialV4.py'
        tree=ast.parse(source.read_text())
        pure={'sample_path','logo_contours','sector_contour','row_layout',
              'qr_runs','vertebra_layout'}
        subset=[n for n in tree.body if isinstance(n,ast.Assign)
                or (isinstance(n,ast.FunctionDef) and n.name in pure)]
        original={'math':math}
        exec(compile(ast.Module(body=subset,type_ignores=[]),'v4 reference','exec'),original)
        for name in ['QR_SIZE','INSTAGRAM_ROWS','GOOGLE_ROWS','NFC_X',
                     'NFC_TAG_DIAMETER','NFC_CAVITY_DIAMETER',
                     'NFC_CAVITY_HEIGHT','NFC_PAUSE_Z','PANEL_THICKNESS',
                     'TONGUE_WIDTH','TONGUE_DEPTH','BASE_WIDTH','BASE_DEPTH',
                     'BASE_HEIGHT','FIT_CLEARANCE_PER_SIDE',
                     'END_CLEARANCE_PER_SIDE','BOTTOM_CLEARANCE']:
            self.assertEqual(v[name],original[name],name)
        self.assertEqual(v['row_layout'](),original['row_layout']())
        # The same logo paths are rescaled and repositioned, not retraced.
        def normalized(values):
            return [[((x-values['LOGO_X'])/values['LOGO_RADIUS'],
                      (y-values['LOGO_Y'])/values['LOGO_RADIUS'])
                     for x,y in contour] for contour in values['logo_contours']()]
        for current,previous in zip(normalized(v),normalized(original)):
            for a,b in zip(current,previous):
                self.assertAlmostEqual(a[0],b[0])
                self.assertAlmostEqual(a[1],b[1])


if __name__=='__main__':
    unittest.main()
