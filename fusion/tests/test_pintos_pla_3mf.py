"""Check the deliverable project against source STL and native slice evidence."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image
import io
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
import build_pintos_pla_3mf as builder


class NativePLAProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=ROOT/'downloads/grelha-pintos-v3-A1-PLA-13-pratos.3mf'
        cls.blobs,cls.model_config,cls.plates=builder.read_project(cls.path)
        cls.config=json.loads(cls.blobs['Metadata/project_settings.config'])
        cls.report=json.loads((ROOT/'fusion/GrelhaPintosV3PLA/validation.json').read_text())

    def test_single_project_contains_correct_plate_roles_and_standard_clip_only(self):
        self.assertEqual(len(self.plates),13)
        self.assertEqual([len(p['items']) for p in self.plates],[1]*12+[26])
        self.assertEqual(len(self.plates[0]['items'][0]['mesh'].split()),2)
        self.assertIn('amostra-duas-bordas',self.plates[0]['items'][0]['settings']['name'])
        for index,plate in enumerate(self.plates):
            for item in plate['items']:
                name=item['settings']['name']
                self.assertNotIn('suave',name)
                self.assertNotIn('firme',name)
                if index==1 or index==12: self.assertIn('presilha-padrao',name)
                if 2<=index<=11: self.assertIn('placa-universal',name)

    def test_project_geometry_matches_original_v3_stl_without_scaling(self):
        sources={key:trimesh.load(ROOT/'downloads'/filename,force='mesh') for key,filename in {
            'grid':'grelha-pintos-v3-placa-universal.stl',
            'clip':'grelha-pintos-v3-presilha-padrao.stl',
            'sample':'grelha-pintos-v3-amostra-duas-bordas.stl'}.items()}
        for index,plate in enumerate(self.plates):
            source=sources['sample' if index==0 else 'clip' if index in (1,12) else 'grid']
            for item in plate['items']:
                mesh=item['mesh']
                self.assertTrue(mesh.is_watertight)
                self.assertAlmostEqual(mesh.volume,source.volume,delta=0.5 if index in range(2,12) else 0.01)
                np.testing.assert_allclose(sorted(mesh.extents[:2]),sorted(source.extents[:2]),atol=0.0001)
                self.assertAlmostEqual(mesh.extents[2],source.extents[2],places=4)
                self.assertGreaterEqual(mesh.bounds[0,:2].min(),0)
                self.assertLessEqual(mesh.bounds[1,:2].max(),256)
                self.assertAlmostEqual(mesh.bounds[0,2],0,places=4)

    def test_a1_pla_strength_profiles_and_clip_object_overrides_are_embedded(self):
        self.assertEqual(self.config['printer_settings_id'],'Bambu Lab A1 0.4 nozzle')
        self.assertEqual(self.config['nozzle_diameter'],['0.4'])
        self.assertEqual(self.config['filament_type'],['PLA'])
        self.assertEqual(self.config['nozzle_temperature'],['220'])
        self.assertEqual(self.config['textured_plate_temp'],['65'])
        self.assertEqual(self.config['curr_bed_type'],'Textured PEI Plate')
        self.assertEqual(self.config['enable_support'],'0')
        self.assertEqual(self.config['wall_generator'],'arachne')
        self.assertEqual(self.config['wall_loops'],'3')
        self.assertEqual(self.config['layer_height'],'0.2')
        self.assertEqual(self.config['sparse_infill_density'],'20%')
        for index in (1,12):
            for item in self.plates[index]['items']:
                s=item['settings']
                self.assertEqual(s['layer_height'],'0.16')
                self.assertEqual(s['sparse_infill_density'],'100%')
                self.assertEqual(s['wall_loops'],'4')
                self.assertEqual(s['outer_wall_speed'],'25')
                self.assertEqual(s['brim_type'],'no_brim')

    def test_native_validation_refers_to_this_file_and_proves_actual_layer_heights(self):
        r=self.report
        self.assertEqual(r['project_sha256'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(r['native_cli_version'],self.config['version'])
        self.assertEqual((r['native_export_exit'],r['native_reopen_exit'],r['native_slice_exit']),(0,0,0))
        self.assertEqual(r['sliced_plates'],13)
        self.assertEqual(r['slice_warnings'],[])
        self.assertEqual(r['actual_gcode_layer_counts'],[74,40]+[150]*10+[40])
        self.assertTrue(r['delivery_is_editable_unsliced_project'])
        self.assertFalse(any(n.endswith('.gcode') for n in self.blobs))
        self.assertFalse(r['physical_PLA_clip_retention_tested'])

    def test_every_plate_thumbnail_decodes_and_contains_actual_geometry(self):
        for p in self.plates:
            name=p['properties']['thumbnail_file']
            self.assertIn(name,self.blobs)
            with Image.open(io.BytesIO(self.blobs[name])) as im:
                pixels=np.asarray(im.convert('RGB'))
                drawn=np.all(pixels==[98,167,159],axis=2)
                self.assertGreater(drawn.sum(),4,name)


if __name__=='__main__': unittest.main()
