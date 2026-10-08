"""Validate V3 manufacturing inputs without requiring Fusion."""
import ast
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'EssencialV3' / 'EssencialV3.py'


def orientation(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def segments_cross(a,b,c,d):
    return (orientation(a,b,c)*orientation(a,b,d)<-1e-10
            and orientation(c,d,a)*orientation(c,d,b)<-1e-10)


class V3Inputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree=ast.parse(SCRIPT.read_text(encoding='utf-8'))
        pure={'sample_path','logo_contours','qr_runs','sector_contour',
              'row_layout','vertebra_layout'}
        subset=[node for node in cls.tree.body if isinstance(node,ast.Assign)
                or (isinstance(node,ast.FunctionDef) and node.name in pure)]
        cls.v={'math':math}
        exec(compile(ast.Module(body=subset,type_ignores=[]),str(SCRIPT),'exec'),cls.v)

    def test_two_cavities_with_floor_roof_and_tag_clearance(self):
        v=self.v
        self.assertEqual(len(v['row_layout']()),2)
        self.assertGreater(v['NFC_CAVITY_DIAMETER'],v['NFC_TAG_DIAMETER'])
        self.assertGreater(v['NFC_CAVITY_FLOOR_Z'],0)
        self.assertGreaterEqual(v['NFC_CAVITY_HEIGHT'],0.6)
        self.assertGreaterEqual(v['PANEL_THICKNESS']-v['NFC_PAUSE_Z'],1.0)
        # Pause after 19 completed 0.2 mm layers, before the roof layer.
        self.assertAlmostEqual(v['NFC_PAUSE_Z']/0.2,19)
        for name,rows,bottom in v['row_layout']():
            radius=v['NFC_CAVITY_DIAMETER']/2
            y=bottom+v['QR_SIZE']/2
            self.assertGreater(v['NFC_X']-radius,v['QR_X']+v['QR_SIZE'])
            self.assertGreater(y-radius,0)
            self.assertLess(y+radius,v['PANEL_HEIGHT'])

    def test_qr_fields_have_quiet_zones_and_printable_modules(self):
        v=self.v
        for name,rows,bottom in v['row_layout']():
            n=len(rows)
            self.assertTrue(all(len(row)==n for row in rows))
            self.assertTrue(all(set(row)<=set('01') for row in rows))
            self.assertGreater(v['QR_SIZE']/n-0.02,1.0)
            self.assertTrue(all(set(row)=={'0'} for row in rows[:4]+rows[-4:]))
            self.assertTrue(all(set(row[:4]+row[-4:])=={'0'} for row in rows))
            rebuilt=[['0']*n for _ in range(n)]
            for row,start,end in v['qr_runs'](rows):
                for col in range(start,end):
                    rebuilt[row][col]='1'
            self.assertEqual([''.join(row) for row in rebuilt],rows)

    def test_social_icons_do_not_intrude_into_qr_fields(self):
        v=self.v
        self.assertGreater(v['QR_X']-(v['ICON_X']+12),4)
        layout=v['row_layout']()
        upper,lower=layout
        self.assertGreater(upper[2]-(lower[2]+v['QR_SIZE']),8)
        # Check buried tags are clear of the spine's vertebral bodies.
        for name,rows,bottom in layout:
            cy=bottom+v['QR_SIZE']/2
            for region,number,x,y,w,h in v['vertebra_layout']():
                if abs(y-cy)<v['NFC_CAVITY_DIAMETER']/2+h/2:
                    self.assertGreater(x-w/2-(v['NFC_X']+
                        v['NFC_CAVITY_DIAMETER']/2),1)

    def test_logo_contours_are_simple_and_inside_logo_circle(self):
        v=self.v
        contours=v['logo_contours']()
        self.assertEqual(len(contours),3)  # E + two curved stars, dot is a disk.
        for contour in contours:
            edges=list(zip(contour,contour[1:]+contour[:1]))
            for x,y in contour:
                self.assertLess(math.hypot(x-v['LOGO_X'],y-v['LOGO_Y']),
                                v['LOGO_RADIUS'])
            for i,(a,b) in enumerate(edges):
                self.assertGreater(math.dist(a,b),1e-6)
                for j in range(i+2,len(edges)):
                    if i==0 and j==len(edges)-1:
                        continue
                    self.assertFalse(segments_cross(a,b,*edges[j]))

    def test_contactless_strokes_and_no_qr_nfc_word_labels(self):
        v=self.v
        for radius in (3.7,7,10.3):
            contour=v['sector_contour'](0,0,radius,1.4,-55,55)
            self.assertAlmostEqual(math.dist(contour[0],contour[-1]),1.4)
        labels=[]
        for node in ast.walk(self.tree):
            if (isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                    and node.func.id=='label'):
                labels.append(ast.literal_eval(node.args[0]))
        self.assertEqual(labels,['CLINICA','ESSENCIAL'])


if __name__=='__main__':
    unittest.main()
