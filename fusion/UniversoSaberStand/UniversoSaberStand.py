"""Universo do Saber: 200 mm backrest, two interlocking physical pieces.

Keep geometry.json beside this script. Creates a NEW Fusion document, named
sketches/extrusions and an assembled view. Set SHOW_ASSEMBLED=False for print view.
Geometry is fixed at the supplied dimensions; do not scale the mating parts.
"""
import json
from pathlib import Path
import traceback

import adsk.core
import adsk.fusion

SHOW_ASSEMBLED=True


def edge_key(line):
    a=line.startSketchPoint.geometry;b=line.endSketchPoint.geometry
    return tuple(sorted([(round(a.x,6),round(a.y,6)),(round(b.x,6),round(b.y,6))]))


def extrude_region(component,region,name,join=False):
    plane=component.xYConstructionPlane
    if region['z']:
        pi=component.constructionPlanes.createInput()
        pi.setByOffset(plane,adsk.core.ValueInput.createByReal(region['z']/10))
        plane=component.constructionPlanes.add(pi)
    sketch=component.sketches.add(plane);sketch.name='Contornos - '+name
    sketch.isComputeDeferred=True;outer=[]
    try:
        for group in region['groups']:
            for index,loop in enumerate(group):
                points=[adsk.core.Point3D.create(x/10,y/10,0) for x,y in loop]
                first=None;previous=None
                for i in range(len(points)):
                    a=previous.endSketchPoint if previous else points[i]
                    b=first.startSketchPoint if i==len(points)-1 else points[(i+1)%len(points)]
                    line=sketch.sketchCurves.sketchLines.addByTwoPoints(a,b)
                    if first is None:first=line
                    previous=line
                if index==0:outer.append(first)
    finally:sketch.isComputeDeferred=False
    keys={edge_key(line) for line in outer};selected=adsk.core.ObjectCollection.create()
    for profile in sketch.profiles:
        include=False
        for loop in profile.profileLoops:
            if not loop.isOuter:continue
            for curve in loop.profileCurves:
                line=adsk.fusion.SketchLine.cast(curve.sketchEntity)
                if line and edge_key(line) in keys:include=True;break
        if include:selected.add(profile)
    if selected.count!=len(region['groups']):
        raise RuntimeError(f'{name}: {selected.count} perfis; esperados {len(region["groups"])}')
    ops=adsk.fusion.FeatureOperations
    feature=component.features.extrudeFeatures.createInput(selected,
        ops.JoinFeatureOperation if join else ops.NewBodyFeatureOperation)
    feature.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(region['height']/10)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    result=component.features.extrudeFeatures.add(feature);result.name=name
    sketch.isVisible=False
    return result


def cut_foot(component,triangle):
    """Horizontal assembled contact face, cut in local YZ through full width."""
    sketch=component.sketches.add(component.yZConstructionPlane)
    sketch.name='Chanfro de contacto com a mesa'
    points=[sketch.modelToSketchSpace(adsk.core.Point3D.create(0,y/10,z/10))
            for y,z in triangle]
    first=sketch.sketchCurves.sketchLines.addByTwoPoints(points[0],points[1])
    second=sketch.sketchCurves.sketchLines.addByTwoPoints(first.endSketchPoint,points[2])
    sketch.sketchCurves.sketchLines.addByTwoPoints(second.endSketchPoint,first.startSketchPoint)
    if sketch.profiles.count!=1:raise RuntimeError('Perfil inválido no chanfro do pé.')
    feature=component.features.extrudeFeatures.createInput(sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    feature.setSymmetricExtent(adsk.core.ValueInput.createByReal(8.2),True)
    cut=component.features.extrudeFeatures.add(feature);cut.name='Face plana do pé'
    sketch.isVisible=False


def placement(matrix):
    m=adsk.core.Matrix3D.create()
    p=adsk.core.Point3D.create(*(matrix[i][3]/10 for i in range(3)))
    axes=[adsk.core.Vector3D.create(*(matrix[i][j] for i in range(3))) for j in range(3)]
    if not m.setWithCoordinateSystem(p,*axes):raise RuntimeError('Transformação inválida.')
    return m


def colour_component(design,component,hex_value):
    rgb=tuple(int(hex_value[i:i+2],16) for i in (1,3,5))
    if not component.bRepBodies.count:return
    appearance=design.appearances.addByCopy(component.bRepBodies.item(0).appearance,
                                          'Universo '+hex_value)
    for key in ('generic_diffuse','opaque_albedo'):
        prop=adsk.core.ColorProperty.cast(appearance.appearanceProperties.itemById(key))
        if prop:
            prop.value=adsk.core.Color.create(*rgb,255)
            for body in component.bRepBodies:body.appearance=appearance
            return


def run(context):
    app=adsk.core.Application.get();ui=app.userInterface;progress=None
    try:
        data=json.loads((Path(__file__).parent/'geometry.json').read_text(encoding='utf-8'))
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design=adsk.fusion.Design.cast(app.activeProduct)
        design.designType=adsk.fusion.DesignTypes.ParametricDesignType
        design.unitsManager.defaultLengthUnits='mm'
        root=design.rootComponent;root.name='Universo do Saber - suporte 200 mm V1'
        progress=ui.createProgressDialog();progress.isCancelButtonShown=True
        progress.show('Universo do Saber','A criar (%p%)',0,3,0)
        occurrences=[]
        for index,part in enumerate(data['parts']):
            progress.progressValue=index;progress.message=part['name']+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:
                ui.messageBox('Criação cancelada. O documento novo pode estar incompleto.')
                return
            occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            component=occ.component;component.name=f'{index+1:02d} - {part["name"]}'
            extrude_region(component,part,part['name'])
            if part.get('bevel_triangle_yz'):cut_foot(component,part['bevel_triangle_yz'])
            for addition in part.get('additions',[]):
                extrude_region(component,addition,addition['name'],join=True)
            colour_component(design,component,part['color'])
            occurrences.append((occ,part))
        for index,(occ,part) in enumerate(occurrences):
            if SHOW_ASSEMBLED:occ.transform2=placement(part['assembly_transform'])
            elif index==2:
                m=adsk.core.Matrix3D.create();m.translation=adsk.core.Vector3D.create(12,0,0)
                occ.transform2=m
        if design.snapshots.hasPendingSnapshot:design.snapshots.add()
        progress.progressValue=3;app.activeViewport.fit()
        ui.messageBox('Suporte criado: costas 200 mm, apoio a 70°, duas peças físicas.\n'
            'Três componentes separam os materiais branco/azul. Guarde como .f3d.\n'
            'Para imprimir, use o 3MF de dois pratos fornecido.\n'
            'Teste a amostra do encaixe antes das peças completas.')
    except Exception:ui.messageBox('Falha ao criar suporte:\n'+traceback.format_exc())
    finally:
        if progress:progress.hide()


def stop(context):pass
