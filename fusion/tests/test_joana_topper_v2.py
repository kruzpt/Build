"""Check the actual V2 fixes, preserved lettering and native four-color delivery."""
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

FOLDER=ROOT/'fusion/JoanaTopperV2'
PROJECT=ROOT/'downloads/joana-topper-v2-A1-AMS-4-cores.3mf'


class JoanaTopperV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new=json.loads((FOLDER/'contours.json').read_text())
        cls.old=json.loads((ROOT/'fusion/JoanaTopper/contours.json').read_text())
        cls.solids=models(cls.new)
        cls.blobs,cls.config,cls.plates=read_project(PROJECT)

    def test_all_four_old_holes_are_filled_by_black_without_extra_color(self):
        backing=cross_section(self.new['parts'][0]['groups'])
        self.assertEqual([len(g) for g in self.new['parts'][0]['groups']],[1])
        holes=self.old['parts'][0]['groups'][0][1:]
        self.assertEqual(len(holes),4)
        for hole in holes:
            shape=md.CrossSection([hole],md.FillRule.NonZero)
            self.assertLess((shape-backing).area(),1e-5)
        cfg=json.loads(self.blobs['Metadata/project_settings.config'])
        self.assertEqual(cfg['filament_colour'],[p['color'].upper() for p in self.new['parts']])
        self.assertEqual(len(cfg['filament_type']),4)

    def test_broom_is_connected_through_collars_and_has_three_internal_grooves(self):
        edit=md.CrossSection.square((64,17)).translate((111,69))
        brown=cross_section(self.new['parts'][2]['groups'])
        collars=cross_section(self.new['parts'][1]['groups'])^edit
        self.assertEqual(len((brown+collars).extrude(.8).decompose()),1)
        self.assertEqual(sum(len(g)-1 for g in self.new['parts'][2]['groups']),3)
        self.assertGreater(brown.area(),250)

    def test_remaining_gold_decoration_and_burgundy_are_preserved(self):
        edit=md.CrossSection.square((64,17)).translate((111,69))
        a=cross_section(self.old['parts'][1]['groups'])-edit
        b=cross_section(self.new['parts'][1]['groups'])-edit
        self.assertLess((a-b).area()+(b-a).area(),1e-4)
        self.assertEqual(self.new['parts'][3]['groups'],self.old['parts'][3]['groups'])

    def test_closed_single_solid_and_supported_nonoverlapping_color_parts(self):
        union=md.Manifold.batch_boolean(list(self.solids.values()),md.OpType.Add)
        self.assertEqual(len(union.decompose()),1)
        mesh=trimesh.load(ROOT/'downloads/joana-topper-v2-completo.stl',force='mesh')
        self.assertTrue(mesh.is_watertight and mesh.is_winding_consistent)
        np.testing.assert_allclose(mesh.extents,[180,200.327,3.2],atol=.01)
        backing=cross_section(self.new['parts'][0]['groups'])
        for part in self.new['parts'][1:]:
            self.assertLess((cross_section(part['groups'])-backing).area(),1e-5)
        for i,a in enumerate(self.solids.values()):
            for b in list(self.solids.values())[:i]:self.assertLess((a^b).volume(),1e-5)

    def test_native_file_matches_validation_and_uses_four_aligned_parts(self):
        report=json.loads((FOLDER/'bambu-validation.json').read_text())
        self.assertEqual(report['project_sha256'],hashlib.sha256(PROJECT.read_bytes()).hexdigest())
        self.assertEqual((report['native_export_exit'],report['native_reopen_exit'],report['native_slice_exit']),(0,0,0))
        self.assertEqual(report['warnings'],[])
        self.assertEqual(report['layers'],16)
        self.assertEqual([f['id'] for f in report['filaments']],[1,2,3,4])
        self.assertEqual([len(p['items']) for p in self.plates],[1])
        self.assertEqual(len(native_parts(self.blobs)),4)
        self.assertFalse(any(n.endswith('.gcode') for n in self.blobs))
        self.assertFalse(report['fusion_runtime_tested'])

    def test_zip_contains_updated_fusion_geometry_and_native_project(self):
        with ZipFile(ROOT/'downloads/joana-topper-v2-pacote.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.read('JoanaTopperV2/contours.json'),(FOLDER/'contours.json').read_bytes())
            self.assertEqual(z.read(PROJECT.name),PROJECT.read_bytes())
            self.assertIn('JoanaTopperV2/JoanaTopperV2.py',z.namelist())
            self.assertIn('JoanaTopperV2/README.md',z.namelist())


if __name__=='__main__':unittest.main()
