"""Check uniform stems, an actual thicker cake stop and added broom gold."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

import manifold3d as md
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
from generate_joana_topper import cross_section,models
from build_pintos_pla_3mf import read_project
from build_joana_topper_3mf import native_parts
from refine_joana_topper_v3 import stop_section,STEM_CENTERS

FOLDER=ROOT/'fusion/JoanaTopperV3'
PROJECT=ROOT/'downloads/joana-topper-v3-A1-AMS-4-cores.3mf'


class JoanaTopperV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((FOLDER/'contours.json').read_text())
        cls.old=json.loads((ROOT/'fusion/JoanaTopperV2/contours.json').read_text())
        cls.solids=models(cls.data)
        cls.blobs,cls.settings,cls.plates=read_project(PROJECT)

    def test_both_stems_have_identical_width_tip_and_root_height(self):
        base=cross_section(self.data['parts'][0]['groups'])
        stems=[]
        for center in STEM_CENTERS:
            crop=md.CrossSection.square((20,43.99)).translate((center-10,0))
            shape=(base^crop).translate((-center,0))
            points=np.vstack(shape.to_polygons())
            self.assertAlmostEqual(points[:,0].max()-points[:,0].min(),8.5,places=4)
            self.assertAlmostEqual(points[:,1].min(),0,places=4)
            self.assertAlmostEqual(points[:,1].max(),43.99,places=4)
            stems.append(shape)
        self.assertLess((stems[0]-stems[1]).area()+(stems[1]-stems[0]).area(),1e-4)

    def test_thicker_support_exists_only_in_the_bar_and_does_not_hide_letters(self):
        top_section=self.solids['preto'].slice(7)
        expected=stop_section()
        self.assertLess((top_section-expected).area()+(expected-top_section).area(),1e-3)
        for name in ('dourado','castanho','bordo'):
            self.assertLess((self.solids['preto']^self.solids[name]).volume(),1e-5)
        self.assertEqual(self.data['cake_stop']['depth_mm'],8)

    def test_gold_now_covers_each_old_bristle_groove_and_end_of_handle(self):
        gold=cross_section(self.data['parts'][1]['groups'])
        holes=[hole for group in self.old['parts'][2]['groups'] for hole in group[1:]]
        self.assertEqual(len(holes),3)
        for hole in holes:
            section=md.CrossSection([hole],md.FillRule.NonZero)
            self.assertGreater((gold^section).area()/section.area(),.98)
        handle_tip=md.CrossSection.square((4,4)).translate((110,70))
        self.assertGreater((gold^handle_tip).area(),3)

    def test_final_geometry_is_closed_connected_and_all_detail_has_black_support(self):
        self.assertEqual([len(g) for g in self.data['parts'][0]['groups']],[1])
        union=md.Manifold.batch_boolean(list(self.solids.values()),md.OpType.Add)
        self.assertEqual(len(union.decompose()),1)
        mesh=trimesh.load(ROOT/'downloads/joana-topper-v3-completo.stl',force='mesh')
        self.assertTrue(mesh.is_watertight and mesh.is_winding_consistent)
        np.testing.assert_allclose(mesh.extents,[180,200.327,8],atol=.02)
        base=cross_section(self.data['parts'][0]['groups'])
        for part in self.data['parts'][1:]:
            self.assertLess((cross_section(part['groups'])-base).area(),1e-4)

    def test_native_project_and_slice_evidence_match_v3_and_four_color_parts(self):
        report=json.loads((FOLDER/'bambu-validation.json').read_text())
        self.assertEqual(report['project_sha256'],hashlib.sha256(PROJECT.read_bytes()).hexdigest())
        self.assertEqual((report['native_export_exit'],report['native_reopen_exit'],report['native_slice_exit']),(0,0,0))
        self.assertEqual(report['layers'],40)
        self.assertEqual(report['warnings'],[])
        self.assertEqual(len(native_parts(self.blobs)),4)
        self.assertEqual([len(p['items']) for p in self.plates],[1])
        self.assertIn('V3',self.plates[0]['properties']['plater_name'])
        self.assertFalse(any(n.endswith('.gcode') for n in self.blobs))
        for (_,mesh),part in zip(native_parts(self.blobs),self.data['parts']):
            self.assertAlmostEqual(mesh.volume,self.solids[part['name']].volume(),delta=.1)

    def test_zip_contains_current_fusion_data_and_support_drawing(self):
        ast.parse((FOLDER/'JoanaTopperV3.py').read_text())
        with ZipFile(ROOT/'downloads/joana-topper-v3-pacote.zip') as z:
            self.assertIsNone(z.testzip())
            for name in ('contours.json','JoanaTopperV3.py','README.md'):
                self.assertEqual(z.read('JoanaTopperV3/'+name),(FOLDER/name).read_bytes())
            self.assertEqual(z.read(PROJECT.name),PROJECT.read_bytes())
            self.assertIn('imagens/joana-topper-v3-apoio.png',z.namelist())


if __name__=='__main__':unittest.main()
