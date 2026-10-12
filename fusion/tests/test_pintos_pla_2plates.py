"""Verify the requested two-plate layout and unchanged geometry/print settings."""
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
import build_pintos_pla_3mf as builder


class TwoPlatePLAProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=ROOT/'downloads/grelha-pintos-v3-A1-PLA-2-pratos.3mf'
        cls.blobs,_,cls.plates=builder.read_project(cls.path)
        cls.previous,_,cls.old_plates=builder.read_project(builder.TARGET)
        cls.report=json.loads((builder.FOLDER/'validation-2-pratos.json').read_text())

    def test_two_plates_by_part_type_with_no_samples_or_duplicate_grids(self):
        builder.validate_project(self.path,two_plates=True)
        self.assertEqual([len(p['items']) for p in self.plates],[1,26])
        names=[item['settings']['name'] for p in self.plates for item in p['items']]
        self.assertIn('placa-universal',names[0])
        self.assertTrue(all('presilha-padrao' in n for n in names[1:]))
        plan=builder.assembly_plan(two_plates=True)
        self.assertEqual([len(p['objects']) for p in plan['plates']],[1,26])

    def test_dimensions_and_solid_volume_match_unscaled_v3_sources(self):
        for plate,filename in zip(self.plates,[
            'grelha-pintos-v3-placa-universal.stl',
            'grelha-pintos-v3-presilha-padrao.stl']):
            source=trimesh.load(ROOT/'downloads'/filename,force='mesh')
            for item in plate['items']:
                mesh=item['mesh']
                self.assertTrue(mesh.is_watertight and mesh.is_winding_consistent)
                # Native mesh serialization rounds coordinates; allow 0.02 mm³
                # on a grid of about 65,912 mm³, without allowing scaled parts.
                self.assertAlmostEqual(mesh.volume,source.volume,delta=0.02)
                np.testing.assert_allclose(sorted(mesh.extents[:2]),
                                           sorted(source.extents[:2]),atol=0.0001)
                self.assertAlmostEqual(mesh.extents[2],source.extents[2],places=4)

    def test_every_global_and_object_setting_is_identical_to_previous_project(self):
        key='Metadata/project_settings.config'
        self.assertEqual(json.loads(self.blobs[key]),json.loads(self.previous[key]))
        self.assertEqual(self.plates[0]['items'][0]['settings'],
                         self.old_plates[2]['items'][0]['settings'])
        old_clip=self.old_plates[12]['items'][0]['settings']
        for item in self.plates[1]['items']:
            self.assertEqual(item['settings'],old_clip)

    def test_native_slice_evidence_matches_delivered_file_and_thumbnails(self):
        r=self.report
        self.assertEqual(r['project_sha256'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual((r['project_plates'],r['project_objects'],r['sliced_plates']),(2,27,2))
        self.assertEqual((r['native_export_exit'],r['native_reopen_exit'],r['native_slice_exit']),(0,0,0))
        self.assertEqual(r['actual_gcode_layer_counts'],[150,40])
        self.assertEqual(r['slice_warnings'],[])
        self.assertFalse(any(n.endswith('.gcode') for n in self.blobs))
        for p in self.plates:
            with Image.open(io.BytesIO(self.blobs[p['properties']['thumbnail_file']])) as im:
                pixels=np.asarray(im.convert('RGB'))
                self.assertGreater(np.all(pixels==[98,167,159],axis=2).sum(),4)


if __name__=='__main__': unittest.main()
