"""Illustration from the exported connector and foot STL, with sample rods."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, rgb, rough=.57):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = rough
    return m

green = mat('PETG verde',(.055,.30,.19))
wood = mat('Cabo de madeira',(.55,.31,.13))
background = mat('fundo',(.91,.94,.91))

def stl(name, loc, material):
    bpy.ops.wm.stl_import(filepath=str(HERE/f'{name}.stl'))
    o=bpy.context.object
    o.name=name
    o.location=loc
    o.data.materials.append(material)
    return o

def rod(name, loc, radius, length, axis):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=length, location=loc)
    o=bpy.context.object
    o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    o.data.materials.append(wood)

# Two levels show the uncut vertical post passing through identical connectors.
stl('connector',(0,0,0),green)
stl('connector',(0,0,136),green)
stl('foot',(0,0,-35),green)
rod('Poste continuo',(0,0,84),11.0,230,'Z')
for z in (22,158):
    rod(f'Varão X {z}',(104,0,z),11.0,132,'X')
    rod(f'Varão Y {z}',(0,104,z),11.0,132,'Y')

bpy.ops.mesh.primitive_plane_add(size=500,location=(0,0,-35.8))
bpy.context.object.data.materials.append(background)
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.82,.87,.82,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for loc,power,size in [((140,-130,290),1300,130),((-110,170,260),900,150)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object
    o.data.energy=power
    o.data.shape='DISK'
    o.data.size=size
    o.rotation_euler=(Vector((35,35,80))-o.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(270,290,215))
camera=bpy.context.object
camera.rotation_euler=(Vector((48,48,94))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=300
bpy.context.scene.camera=camera
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=24
sc.cycles.use_denoising=False
sc.render.resolution_x=1100
sc.render.resolution_y=900
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath=str(ROOT/'designs/movel-filamentos-modular-v2-conector-cad.png')
bpy.ops.render.render(write_still=True)

# Vista da peça isolada por baixo: dois acessos às tomadas e um ao poste.
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'connector':
        o.hide_render=True
camera.location=(-120,-140,-110)
camera.rotation_euler=(Vector((16,16,26))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.ortho_scale=145
sc.render.filepath=str(ROOT/'designs/movel-filamentos-modular-v2-furos-cad.png')
bpy.ops.render.render(write_still=True)
