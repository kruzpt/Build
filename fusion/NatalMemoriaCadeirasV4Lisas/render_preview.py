"""Render the smooth board chairs from their actual exported STL meshes."""
import bpy, math, sys
from mathutils import Matrix, Vector
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
mode='boards'
view='perspective'
if '--' in sys.argv:
    tail=sys.argv[sys.argv.index('--')+1:]
    if tail:mode=tail[0]
    if len(tail)>1:view=tail[1]
assert mode in ('boards','tree')
assert view in ('perspective','front','detail')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,rgb,rough=.55):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=rough
    return m
cream=mat('PLA creme',(.89,.79,.58));brown=mat('PLA castanho',(.22,.105,.05));wood=mat('PLA madeira',(.46,.22,.09));floor=mat('fundo',(.96,.96,.94))

def obj(name,matrix,material):
    bpy.ops.wm.stl_import(filepath=str(HERE/'stl'/f'{name}.stl'))
    o=bpy.context.object;o.name=name;o.matrix_world=matrix;o.data.materials.append(material)
    return o

def M(rows):return Matrix(rows)
I=Matrix.Identity(4)
if view!='detail':
    obj('base',I,cream)
    tree=M([[-1,0,0,0],[0,0,1,64-2.5],[0,1,0,1],[0,0,0,1]])
    obj('tree_cream',tree,cream)
    obj('tree_brown',tree,brown)

def chair(style,loc,yaw):
    s=.75
    root=Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw),4,'Z')
    left=M([[0,0,-1,-26.6*s],[-1,0,0,0],[0,1,0,6],[0,0,0,1]])
    right=M([[0,0,1,26.6*s],[1,0,0,0],[0,1,0,6],[0,0,0,1]])
    obj(style+'_side_A',root@left,wood)
    obj(style+'_side_B',root@right,wood)
    for h in (67,78,89):
        depth=25+(h-61)*.19
        b=M([[1,0,0,0],[0,0,-1,(depth+1.6)*s],[0,1,0,6+h*s],[0,0,0,1]])
        obj(f'{style}_back',root@b,wood)
    for depth in (-11,11):
        seat=Matrix.Translation(Vector((0,depth*s,6+(42-1.6)*s)))
        obj(f'{style}_seat',root@seat,wood)
    bar=M([[1,0,0,0],[0,0,-1,(-26+1.6)*s],[0,1,0,6+17*s],[0,0,0,1]])
    obj(style+'_bar',root@bar,wood)
if mode!='tree':
    if view=='detail':chair(mode,(0,0,-6),18)
    else:
        chair(mode,(-70,-6,0),10)
        chair(mode,(70,-6,0),-10)

bpy.ops.mesh.primitive_plane_add(size=500,location=(0,0,-.7))
bpy.context.object.data.materials.append(floor)
world=bpy.context.scene.world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.88,.92,.90,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for loc,power,size in [((-130,-160,260),1050,200),((150,100,270),900,180)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,85))-o.location).to_track_quat('-Z','Y').to_euler()
if view=='detail':
    camera_loc=(105,-170,145);target=(0,0,47);scale=110
elif mode=='tree':
    camera_loc=(0,-260,105);target=(0,45,105);scale=224
elif view=='front':
    camera_loc=(0,-360,178);target=(0,0,97);scale=300
else:
    camera_loc=(160,-330,205);target=(0,0,97);scale=300
bpy.ops.object.camera_add(location=camera_loc)
camera=bpy.context.object;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=scale;bpy.context.scene.camera=camera
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=18
sc.cycles.use_denoising=False
sc.render.resolution_x=1400 if mode!='tree' else 900
sc.render.resolution_y=1100
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
suffix='-frente' if view=='front' else '-detalhe' if view=='detail' else ''
sc.render.filepath=str(ROOT/f'designs/natal-memoria-v4-tabuas-lisas{suffix}.png')
bpy.ops.render.render(write_still=True)
