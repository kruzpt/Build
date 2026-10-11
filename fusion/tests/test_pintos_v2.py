"""Inspect the exported STL, not just the code that generated it."""
import ast
import json
import math
from pathlib import Path
import unittest

import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'fusion/GrelhaPintosV2'
STL=ROOT/'downloads/grelha-pintos-v2-217.3x179.8x30.stl'


class PintosPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree=ast.parse((FOLDER/'GrelhaPintosV2.py').read_text())
        pure=[n for n in tree.body if isinstance(n,ast.Assign) or
              (isinstance(n,ast.FunctionDef) and n.name in
               ('layout','foot_contour','validate'))]
        cls.v={'math':math}
        exec(compile(ast.Module(body=pure,type_ignores=[]),'pintos parameters','exec'),cls.v)
        cls.mesh=trimesh.load(STL,force='mesh')
        cls.stats=json.loads((FOLDER/'validation.json').read_text())

    def test_actual_stl_is_one_closed_consistently_wound_solid(self):
        self.assertTrue(self.mesh.is_watertight)
        self.assertTrue(self.mesh.is_winding_consistent)
        self.assertEqual(len(self.mesh.split()),1)
        self.assertGreater(self.mesh.volume,0)
        np.testing.assert_allclose(self.mesh.bounds,
                                   [[0,0,0],[217.3,179.8,30]],atol=0.0001)

    def test_user_clearance_is_per_module_and_correct_for_two_by_five(self):
        self.assertEqual(self.v['MODULE_REDUCTION'],0.2)
        np.testing.assert_allclose(self.mesh.extents[:2],
                                   np.array([217.5,180])-0.2,atol=0.0001)
        envelope=self.mesh.extents[:2]*[2,5]
        np.testing.assert_allclose(envelope,[434.6,899],atol=0.001)
        np.testing.assert_allclose([435,900]-envelope,[0.4,1],atol=0.001)
        self.assertLess(max(self.mesh.extents[:2]+10),256)

    def test_every_exported_aperture_has_the_confirmed_eight_mm_opening(self):
        section=self.mesh.section(plane_origin=[0,0,1.6],plane_normal=[0,0,1])
        self.assertTrue(all(entity.closed for entity in section.entities))
        loops=[section.vertices[entity.points] for entity in section.entities]
        self.assertEqual(len(loops),397)
        holes=[]
        for loop in loops:
            size=np.ptp(loop[:,:2],axis=0)
            if max(size)<10:
                holes.append(size)
        self.assertEqual(len(holes),396)
        np.testing.assert_allclose(holes,np.full((396,2),8),atol=0.0001)

    def test_all_nine_feet_reach_same_height_without_hollow_pockets(self):
        section=self.mesh.section(plane_origin=[0,0,29],plane_normal=[0,0,1])
        self.assertTrue(all(entity.closed for entity in section.entities))
        loops=[section.vertices[entity.points] for entity in section.entities]
        self.assertEqual(len(loops),9)
        for loop in loops:
            np.testing.assert_allclose(np.ptp(loop[:,:2],axis=0),[12,12],atol=0.0001)
            x,y=loop[:,0],loop[:,1]
            area=abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/2
            self.assertAlmostEqual(area,2*12*1.6-1.6**2,delta=0.001)

    def test_saved_volume_matches_report_and_less_material_than_reference_union(self):
        self.assertAlmostEqual(self.mesh.volume,self.stats['new_volume_mm3'],delta=0.2)
        ref=self.stats['reference']['union_volume_mm3']
        reduction=100*(1-self.mesh.volume/ref)
        self.assertAlmostEqual(reduction,self.stats['solid_volume_reduction_percent'],places=3)
        self.assertGreater(reduction,35)
        self.assertLess(reduction,45)


if __name__=='__main__':
    unittest.main()
