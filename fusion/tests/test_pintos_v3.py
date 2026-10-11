"""Measure exported sockets/clips and test actual STL assembly intersections."""
import json
from pathlib import Path
import sys
import unittest

import manifold3d as md
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'fusion/tools'))
import generate_pintos_v3 as generator


def solid(mesh):
    result=md.Manifold(md.Mesh(np.asarray(mesh.vertices,dtype=np.float32),
                               np.asarray(mesh.faces,dtype=np.uint32)))
    assert result.status()==md.Error.NoError
    return result


def loops(mesh,z):
    section=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    assert section is not None and all(e.closed for e in section.entities)
    return [section.vertices[e.points] for e in section.entities]


class UniversalGrate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=generator.parameters()
        cls.files={label:ROOT/'downloads'/('grelha-pintos-v3-'+label+'.stl')
                   for label in ('placa-universal','amostra-duas-bordas',
                                 'presilha-suave','presilha-padrao','presilha-firme')}
        cls.meshes={label:trimesh.load(path,force='mesh')
                    for label,path in cls.files.items()}
        cls.plate=solid(cls.meshes['placa-universal'])
        coupon_parts=cls.meshes['amostra-duas-bordas'].split()
        first=min(coupon_parts,key=lambda p:p.bounds[0,0])
        cls.coupon=solid(first)
        # Transform the saved standard clip from its flat printing coordinates
        # to across-seam X, tangential Y, plate printing Z.
        cls.clip=solid(cls.meshes['presilha-padrao']).transform(np.array(
            [[1,0,0,-cls.v['BOSS_DEPTH']],
             [0,0,1,-cls.v['CLIP_WIDTH']/2],
             [0,1,0,cls.v['CLIP_TIP_Z']]],dtype=float))

    def test_saved_parts_are_closed_and_preserve_dimensions(self):
        for label,mesh in self.meshes.items():
            self.assertTrue(mesh.is_watertight,label)
            self.assertTrue(mesh.is_winding_consistent,label)
            self.assertEqual(len(mesh.split()),2 if label=='amostra-duas-bordas' else 1)
        np.testing.assert_allclose(self.meshes['placa-universal'].bounds,
                                   [[0,0,0],[217.3,179.8,30]],atol=0.0001)
        np.testing.assert_allclose(self.meshes['presilha-padrao'].extents,
                                   [8.4,11.2,6.4],atol=0.0001)
        np.testing.assert_allclose([2*self.v['WIDTH'],5*self.v['DEPTH']],
                                   [434.6,899],atol=0.0001)

    def test_walking_surface_keeps_every_eight_mm_aperture(self):
        contours=loops(self.meshes['placa-universal'],1.6)
        holes=[np.ptp(p[:,:2],axis=0) for p in contours if np.ptp(p[:,:2],axis=0).max()<10]
        self.assertEqual(len(contours),397)
        self.assertEqual(len(holes),396)
        np.testing.assert_allclose(holes,np.full((396,2),8),atol=0.0001)

    def test_eight_real_cavities_are_symmetric_under_half_turn(self):
        contours=loops(self.meshes['placa-universal'],6.6)
        pockets=[p for p in contours if np.allclose(
            sorted(np.ptp(p[:,:2],axis=0)),[2.6,7],atol=0.0001)]
        self.assertEqual(len(pockets),8)
        centres=np.array([(p[:,:2].min(axis=0)+p[:,:2].max(axis=0))/2 for p in pockets])
        for centre in centres:
            reflected=np.array([self.v['WIDTH'],self.v['DEPTH']])-centre
            self.assertLess(np.min(np.linalg.norm(centres-reflected,axis=1)),0.0001)

    def test_sample_holder_matches_all_eight_actual_plate_sockets(self):
        v=self.v
        coupon=self.coupon.translate((0,-v['COUPON_LENGTH']/2,0))
        region=md.Manifold.cube((v['BOSS_DEPTH'],v['BOSS_LENGTH'],
                                v['BOSS_END_Z']-v['GRID_THICKNESS'])).translate(
                                    (0,-v['BOSS_LENGTH']/2,v['GRID_THICKNESS']))
        holder=coupon^region
        for x,y,nx,ny,tx,ty in v['socket_sites']():
            matrix=np.array([[nx,tx,0,x],[ny,ty,0,y],[0,0,1,0]],dtype=float)
            expected=holder.transform(matrix)
            actual=self.plate^region.transform(matrix)
            difference=(actual-expected).volume()+(expected-actual).volume()
            self.assertLess(difference,0.01)

    def test_standard_clip_fits_and_retains_on_both_plate_axes(self):
        # Same clip, rotated 90 degrees, works across the other edge type.
        p=self.plate
        for normal,centre in [('x',self.v['DEPTH']/4),('y',self.v['WIDTH']/4)]:
            if normal=='x':
                pair=p+p.translate((-self.v['WIDTH'],0,0))
                clip=self.clip.translate((0,centre,0))
            else:
                pair=p+p.translate((0,-self.v['DEPTH'],0))
                clip=self.clip.rotate((0,0,90)).translate((centre,0,0))
            self.assertLess((pair^clip).volume(),0.0001)
            self.assertGreater((pair^clip.translate((0,0,1))).volume(),0.1)
        self.assertLess(self.clip.bounding_box()[5],self.v['HEIGHT'])

    def test_release_probe_reaches_arm_without_crossing_sample_wall(self):
        right=self.coupon.translate((0,-self.v['COUPON_LENGTH']/2,0))
        probe=md.Manifold.cube((3,4,2)).translate((2.5,-2,10.5))
        self.assertLess((probe^right).volume(),0.0001)
        self.assertGreater((probe^self.clip).volume(),0.01)

    def test_clip_variants_and_printed_spring_thickness(self):
        for label,reach in [('suave',3.1),('padrao',3.2),('firme',3.3)]:
            generator.assembly_checks(self.v,self.coupon,reach)
            mesh=self.meshes['presilha-'+label]
            nose=mesh.vertices[mesh.vertices[:,1]<=1.8001]
            self.assertAlmostEqual(nose[:,0].max()-self.v['BOSS_DEPTH'],reach,places=4)
        mesh=self.meshes['presilha-padrao']
        section=mesh.section(plane_origin=[0,5,0],plane_normal=[0,1,0])
        self.assertEqual(len(section.entities),2)
        for e in section.entities:
            size=np.ptp(section.vertices[e.points],axis=0)
            np.testing.assert_allclose(size[[0,2]],[1.2,6.4],atol=0.0001)

    def test_geometric_insertion_route_and_total_volume_report(self):
        # Route is an idealised clearance model, not a material simulation.
        generator.assembly_checks(self.v,self.coupon)
        stats=json.loads((ROOT/'fusion/GrelhaPintosV3/validation.json').read_text())
        total=10*self.meshes['placa-universal'].volume+26*self.meshes['presilha-padrao'].volume
        self.assertAlmostEqual(total,stats['complete_2_by_5_solid_volume_mm3'],delta=2)
        ref=10*stats['reference']['union_volume_mm3']
        self.assertAlmostEqual(100*(1-total/ref),stats['complete_2_by_5_reduction_percent'],places=3)


if __name__=='__main__':
    unittest.main()
