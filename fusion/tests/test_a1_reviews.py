"""Review-link QR regression checks on the A1-sized model."""
import ast
import math
from pathlib import Path
import unittest

import test_a1_envelope as a1_tests
import test_v3_fast as fast_tests

SCRIPT=Path(__file__).resolve().parents[1]/'EssencialA1Reviews/EssencialA1Reviews.py'
GOOGLE_URL='https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg'


def pure_values(path):
    tree=ast.parse(path.read_text())
    names={'sample_path','logo_contours','sector_contour','row_layout',
           'qr_runs','vertebra_layout'}
    nodes=[n for n in tree.body if isinstance(n,ast.Assign)
           or (isinstance(n,ast.FunctionDef) and n.name in names)]
    v={'math':math}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),v)
    return v


class A1ReviewsGeometry(a1_tests.A1Geometry):
    @classmethod
    def setUpClass(cls):
        original=a1_tests.SCRIPT
        try:
            a1_tests.SCRIPT=SCRIPT
            super().setUpClass()
        finally:
            a1_tests.SCRIPT=original

    def test_no_global_scaling_of_qr_nfc_or_fit(self):
        # Changing the Google matrix is intentional; every physical dimension
        # must stay equal to the A1 version, not the previous oversized V4.
        v=self.v
        original=pure_values(a1_tests.SCRIPT)
        for name in ['QR_SIZE','INSTAGRAM_ROWS','NFC_X','ICON_X','QR_X',
                     'NFC_TAG_DIAMETER','NFC_CAVITY_DIAMETER',
                     'NFC_CAVITY_HEIGHT','NFC_PAUSE_Z','PANEL_THICKNESS',
                     'PANEL_WIDTH','PANEL_HEIGHT','LOGO_RADIUS','LOGO_X','LOGO_Y',
                     'TONGUE_WIDTH','TONGUE_DEPTH','BASE_WIDTH','BASE_DEPTH',
                     'BASE_HEIGHT','FIT_CLEARANCE_PER_SIDE','END_CLEARANCE_PER_SIDE',
                     'BOTTOM_CLEARANCE']:
            self.assertEqual(v[name],original[name],name)
        self.assertEqual(v['logo_contours'](),original['logo_contours']())
        self.assertEqual(v['vertebra_layout'](),original['vertebra_layout']())
        self.assertEqual(v['GOOGLE_REVIEW_URL'],GOOGLE_URL)
        self.assertNotEqual(v['GOOGLE_ROWS'],original['GOOGLE_ROWS'])
        self.assertEqual(v['GOOGLE_QR_ERROR_CORRECTION'],'M')
        self.assertEqual(len(v['GOOGLE_ROWS']),45)
        self.assertGreaterEqual(v['QR_SIZE']/len(v['GOOGLE_ROWS'])-0.02,1.4)

    def test_embedded_qr_matrices_decode_to_correct_destinations(self):
        import cv2
        import numpy as np
        expected={'Google':GOOGLE_URL,
                  'Instagram':'https://www.instagram.com/clinicaessencial_setubal/'}
        for name,rows,bottom in self.v['row_layout']():
            pixels=np.array([[0 if v=='1' else 255 for v in row] for row in rows],
                            dtype=np.uint8)
            pixels=cv2.resize(pixels,None,fx=20,fy=20,interpolation=cv2.INTER_NEAREST)
            decoded,_,_=cv2.QRCodeDetector().detectAndDecode(pixels)
            self.assertEqual(decoded,expected[name])


class ReviewBatch(unittest.TestCase):
    def test_new_google_matrix_still_uses_one_extrusion_per_code(self):
        previous=fast_tests.SCRIPT
        try:
            fast_tests.SCRIPT=SCRIPT
            v,original,sketches,extrusions=fast_tests.BatchAPI().fixture()
        finally:
            fast_tests.SCRIPT=previous
        for name,rows,bottom in v['row_layout']():
            v['build_qr'](name,rows,bottom)
            p=64/len(rows)
            expected=[(v['QR_X']+start*p+0.01,
                       bottom+(len(rows)-row-1)*p+0.01,
                       v['QR_X']+end*p-0.01,
                       bottom+(len(rows)-row)*p-0.01)
                      for row,start,end in v['qr_runs'](rows)]
            self.assertEqual([e[0][0]+e[1][1] for e in extrusions[-1][0]],expected)
        self.assertEqual(len(sketches),2)
        self.assertEqual(len(extrusions),2)
        self.assertEqual([len(e[0]) for e in extrusions],[352,353])


if __name__=='__main__':
    unittest.main()
