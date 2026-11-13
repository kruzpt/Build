"""FreeCAD STEP: analytic cylindrical walls, faceted sampled helical profiles.
Run with system Python exposing FreeCAD/Part/Mesh. Requires /tmp/cookie-step
thread meshes generated from generate.thread, not a conversion of the full box.
"""
from pathlib import Path
import sys,json
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as App,Part,Mesh
sys.excepthook=sys.__excepthook__
D=Path(__file__).resolve().parent
p=json.loads((D/'parameters.json').read_text());V=App.Vector
ri=p['cookie_diameter']/2+p['cookie_radial_clearance'];rr=ri+p['wall']
bh=p['base']+p['stack_height']+p['top_clearance'];lh=p['lid_face']+p['lid_skirt']
lr=rr+p['thread_depth']+p['thread_radial_clearance']+p['lid_wall'];az=bh+p['lid_face']

def from_thread(name):
    mesh=Mesh.Mesh('/tmp/cookie-step/'+name)
    shape=Part.Shape();shape.makeShapeFromMesh(mesh.Topology,.001)
    solid=Part.makeSolid(Part.makeShell(shape.Faces))
    assert solid.isValid() and len(solid.Solids)==1
    return solid


def main():
    if "--reuse" in sys.argv:
        return finish(Part.read(str(D/"step/corpo.step")),Part.read(str(D/"step/tampa.step")))
    male=from_thread('male.stl');female=from_thread('female-cut.stl')
    print('Thread BReps ready',flush=True)
    b=Part.makeCylinder(rr,bh-.5).fuse(Part.makeCone(rr,rr-.5,.5,V(0,0,bh-.5)))
    b=b.fuse(male).cut(Part.makeCylinder(ri,bh+.02,V(0,0,p['base']))).removeSplitter()
    print('Body ready',b.isValid(),flush=True)
    female.rotate(V(0,0,0),V(1,0,0),180);female.translate(V(0,0,az))
    female=female.common(Part.makeCylinder(lr+1,p['lid_skirt']+.02,V(0,0,p['lid_face'])))
    c=p['thread_radial_clearance'];ch=p['entry_chamfer']
    cavity=Part.makeCylinder(rr+c,p['lid_skirt']+.02,V(0,0,p['lid_face']))
    cavity=cavity.fuse(Part.makeCone(rr+c,rr+c+ch+.02,ch+.02,V(0,0,lh-ch)))
    l=Part.makeCylinder(lr,lh).cut(cavity.fuse(female)).removeSplitter()
    print('Lid ready',l.isValid(),flush=True)
    assert b.isValid() and l.isValid() and len(b.Solids)==len(l.Solids)==1
    b.exportStep(str(D/'step/corpo.step'));l.exportStep(str(D/'step/tampa.step'))
    for name in ('corpo','tampa'):
        file=D/'step'/f'{name}.step'
        file.write_text(''.join(line.rstrip()+'\n' for line in file.read_text().splitlines()))
    finish(b,l)


def finish(b,l):
    assert b.isValid() and l.isValid()
    geometry=json.loads((D/'validation/geometry.json').read_text())
    volumes={x['name']:x['volume_mm3'] for x in geometry['parts']}
    assert abs(b.Volume-volumes['corpo'])/volumes['corpo']<.001
    assert abs(l.Volume-volumes['tampa-completa-monocor'])/volumes['tampa-completa-monocor']<.001
    # Independent functional STEP solids avoid a fragile compound operation
    # at the coincident lid/rim contact. Both can be assembled using az and Rx180.
    reopened=[]
    for name in ('corpo','tampa'):
        shape=Part.read(str(D/'step'/f'{name}.step'))
        assert shape.isValid() and len(shape.Solids)==1
        reopened.append({'file':name+'.step','solids':1,'volume_mm3':shape.Volume,'valid':True})
    report={'freecad_version':App.Version(),'files':reopened,'export_and_reopen_verified':True,
            'parametric_history':False,'surfaces':'analytic cylinder/cone walls; sampled helical thread facets',
            'interference_validation':'equivalent manifold meshes; geometry.json',
            'lid_assembly_transform':'Rx 180 degrees, then Z + '+str(az)+' mm'}
    (D/'validation/step.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
