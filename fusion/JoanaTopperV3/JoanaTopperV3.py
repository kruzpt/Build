"""Joana 12 V3 — four color components, uniform stems and cake support ledge.

Keep contours.json next to this script. Creates a new Fusion document.
The inscription is fixed vector geometry; TARGET_WIDTH_MM scales XY only.
"""
import json
from pathlib import Path
import traceback
import adsk.core
import adsk.fusion

TARGET_WIDTH_MM=180.0
THICKNESS_SCALE=1.0


def edge_key(line):
    a=line.startSketchPoint.geometry;b=line.endSketchPoint.geometry
    return tuple(sorted([(round(a.x,6),round(a.y,6)),(round(b.x,6),round(b.y,6))]))


def extrude_region(component,region,factor,name,join=False):
    plane=component.xYConstructionPlane
    if region['z']:
        pi=component.constructionPlanes.createInput()
        pi.setByOffset(plane,adsk.core.ValueInput.createByReal(region['z']*THICKNESS_SCALE/10))
        plane=component.constructionPlanes.add(pi)
    sketch=component.sketches.add(plane);sketch.name='Contours '+name
    sketch.isComputeDeferred=True;outer=[]
    try:
        for group in region['groups']:
            for loop_index,loop in enumerate(group):
                points=[adsk.core.Point3D.create(x*factor/10,y*factor/10,0) for x,y in loop]
                first=None;previous=None
                for vertex in range(len(points)):
                    a=previous.endSketchPoint if previous else points[vertex]
                    b=first.startSketchPoint if vertex==len(points)-1 else points[(vertex+1)%len(points)]
                    line=sketch.sketchCurves.sketchLines.addByTwoPoints(a,b)
                    if first is None:first=line
                    previous=line
                if loop_index==0:outer.append(first)
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
        raise RuntimeError(f'{name}: {selected.count} profiles; expected {len(region["groups"])}')
    ops=adsk.fusion.FeatureOperations
    feature=component.features.extrudeFeatures.createInput(selected,
        ops.JoinFeatureOperation if join else ops.NewBodyFeatureOperation)
    distance=adsk.core.ValueInput.createByReal(region['height']*THICKNESS_SCALE/10)
    feature.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(distance),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    result=component.features.extrudeFeatures.add(feature);result.name=name
    sketch.isVisible=False
    return result


def run(context):
    app=adsk.core.Application.get();ui=app.userInterface;progress=None
    try:
        data=json.loads((Path(__file__).parent/'contours.json').read_text(encoding='utf-8'))
        if not 120<=TARGET_WIDTH_MM<=200 or THICKNESS_SCALE<1:
            raise ValueError('Width must be 120–200 mm; keep thickness scale at least 1.')
        factor=TARGET_WIDTH_MM/data['width_mm']
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design=adsk.fusion.Design.cast(app.activeProduct)
        design.designType=adsk.fusion.DesignTypes.ParametricDesignType
        design.unitsManager.defaultLengthUnits='mm';root=design.rootComponent
        root.name='Joana 12 V3 - topper com apoio'
        progress=ui.createProgressDialog();progress.isCancelButtonShown=True
        progress.show('Joana 12 V3','Creating (%p%)',0,4,0)
        for index,part in enumerate(data['parts']):
            progress.progressValue=index;progress.message=part['name']+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:return
            component=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
            component.name=f'{index+1:02d} - {part["name"]}'
            extrude_region(component,part,factor,'Relief '+part['name'])
            for addition in part.get('additions',[]):
                extrude_region(component,addition,factor,addition['name'],join=True)
            rgb=tuple(int(part['color'][i:i+2],16) for i in (1,3,5))
            for n,body in enumerate(component.bRepBodies):
                body.name=f'{part["name"]} {n+1}'
                try:
                    appearance=design.appearances.addByCopy(body.appearance,f'Joana V3 {part["name"]} {n+1}')
                    for key in ('generic_diffuse','opaque_albedo'):
                        prop=adsk.core.ColorProperty.cast(appearance.appearanceProperties.itemById(key))
                        if prop:
                            prop.value=adsk.core.Color.create(*rgb,255);body.appearance=appearance;break
                except Exception:pass
        progress.progressValue=4;app.activeViewport.fit()
        ui.messageBox(f'Joana 12 V3 created. Width: {TARGET_WIDTH_MM:.0f} mm.\n'
                      'Four colors, uniform stems and a cake support. Save as .f3d.\n'
                      'Use the supplied V3 3MF for aligned AMS printing.')
    except Exception:ui.messageBox('Joana V3 failed:\n'+traceback.format_exc())
    finally:
        if progress:progress.hide()


def stop(context):pass
