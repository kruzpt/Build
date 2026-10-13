"""Check attached relief, source/STL agreement and native AMS project evidence."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import manifold3d as md
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
import generate_joana_topper as generator
import build_joana_topper_3mf as builder
from build_pintos_pla_3mf import read_project


class JoanaTopper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((generator.FOLDER/'contours.json').read_text())
        cls.solids=generator.models(cls.data)
        cls.blobs,cls.settings,cls.plates=read_project(builder.TARGET)
        cls.report=json.loads((generator.FOLDER/'bambu-validation.json').read_text())

    def test_entire_topper_is_connected_with_correct_dimensions(self):
        solid=md.Manifold.batch_boolean(list(self.solids.values()),md.OpType.Add)
        self.assertEqual(len(solid.decompose()),1)
        mesh=trimesh.load(ROOT/'downloads/joana-topper-v1-completo.stl',force='mesh')
        self.assertTrue(mesh.is_watertight and mesh.is_winding_consistent)
        np.testing.assert_allclose(mesh.extents,[180,200.327,3.2],atol=.01)
        self.assertAlmostEqual(mesh.volume,solid.volume(),delta=.1)

    def test_color_parts_are_supported_and_do_not_overlap_each_other(self):
        base=generator.cross_section(self.data['parts'][0]['groups'])
        for part in self.data['parts'][1:]:
            section=generator.cross_section(part['groups'])
            self.assertLess((section-base).area(),1e-5)
            self.assertEqual(part['z'],2.4)
        values=list(self.solids.values())
        for i,a in enumerate(values):
            for b in values[:i]:self.assertLess((a^b).volume(),1e-5)

    def test_stls_match_contours_and_fusion_has_no_submicron_edges(self):
        for part in self.data['parts']:
            mesh=trimesh.load(ROOT/f'downloads/joana-topper-v1-{part["name"]}.stl',force='mesh')
            self.assertTrue(mesh.is_watertight and mesh.is_winding_consistent)
            self.assertAlmostEqual(mesh.volume,self.solids[part['name']].volume(),delta=.1)
            for group in part['groups']:
                for loop in group:
                    p=np.array(loop)
                    self.assertGreater(np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1).min(),.01)
        ast.parse((generator.FOLDER/'JoanaTopper.py').read_text())

    def test_native_project_has_four_aligned_parts_and_correct_filament_slots(self):
        self.assertEqual(len(self.plates),1)
        self.assertEqual(len(self.plates[0]['items']),1)
        cfg=json.loads(self.blobs['Metadata/project_settings.config'])
        self.assertEqual(cfg['printer_settings_id'],'Bambu Lab A1 0.4 nozzle')
        self.assertEqual(cfg['filament_type'],['PLA']*4)
        self.assertEqual(cfg['filament_colour'],[p['color'].upper() for p in self.data['parts']])
        native=builder.native_parts(self.blobs)
        self.assertEqual(len(native),4)
        parts=self.settings.find('object').findall('part')
        self.assertEqual([p.find("metadata[@key='extruder']").get('value') for p in parts],['1','2','3','4'])
        for (_,mesh),part in zip(native,self.data['parts']):
            self.assertAlmostEqual(mesh.volume,self.solids[part['name']].volume(),delta=.1)
        bounds=self.plates[0]['items'][0]['mesh'].bounds
        self.assertGreaterEqual(bounds.min(),-1e-5)
        self.assertLessEqual(bounds[1,:2].max(),256)

    def test_native_validation_hash_and_all_four_filaments_used(self):
        r=self.report
        self.assertEqual(r['project_sha256'],hashlib.sha256(builder.TARGET.read_bytes()).hexdigest())
        self.assertEqual((r['native_export_exit'],r['native_reopen_exit'],r['native_slice_exit']),(0,0,0))
        self.assertEqual(r['layers'],16)
        self.assertEqual(r['warnings'],[])
        self.assertEqual([f['id'] for f in r['filaments']],[1,2,3,4])
        self.assertTrue(all(f['main_used_g']>0 for f in r['filaments']))
        self.assertFalse(r['fusion_runtime_tested'])
        self.assertFalse(any(n.endswith('.gcode') for n in self.blobs))
        for rel in ET.fromstring(self.blobs['_rels/.rels']):
            self.assertIn(rel.get('Target').lstrip('/'),self.blobs)

    def test_download_bundle_contains_matching_fusion_data_and_native_project(self):
        with ZipFile(ROOT/'downloads/joana-topper-v1-pacote.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.read('JoanaTopper/contours.json'),(generator.FOLDER/'contours.json').read_bytes())
            self.assertEqual(z.read(builder.TARGET.name),builder.TARGET.read_bytes())
            self.assertIn('JoanaTopper/JoanaTopper.py',z.namelist())


if __name__=='__main__':unittest.main()
