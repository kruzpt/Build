"""Joana 12 V2 — four-color flat relief for Autodesk Fusion.

Creates a new document from the same millimeter contours used in the STL/3MF.
Keep contours.json next to this script. No external Python packages required.
"""
import json
from pathlib import Path
import traceback
import adsk.core
import adsk.fusion

TARGET_WIDTH_MM=180.0
THICKNESS_SCALE=1.0  # XY scaling preserves the 2.4 mm base by default.


def edge_key(line):
    """Identify an untrimmed contour edge without comparing Fusion entity tokens."""
    a=line.startSketchPoint.geometry
    b=line.endSketchPoint.geometry
    return tuple(sorted([(round(a.x,6),round(a.y,6)),
                         (round(b.x,6),round(b.y,6))]))


def run(context):
    app=adsk.core.Application.get()
    ui=app.userInterface
    progress=None
    try:
        data=json.loads((Path(__file__).parent/'contours.json').read_text(encoding='utf-8'))
        if not 120<=TARGET_WIDTH_MM<=200:
            raise ValueError('Use a width between 120 and 200 mm for this A1 draft.')
        if THICKNESS_SCALE<1:
            raise ValueError('Keep the base thickness at least 2.4 mm.')
        factor=TARGET_WIDTH_MM/data['width_mm']
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design=adsk.fusion.Design.cast(app.activeProduct)
        design.designType=adsk.fusion.DesignTypes.ParametricDesignType
        design.unitsManager.defaultLengthUnits='mm'
        root=design.rootComponent
        root.name='Joana 12 - topper magico'
        progress=ui.createProgressDialog()
        progress.isCancelButtonShown=True
        progress.show('Topper Joana 12','Creating (%p%)',0,4,0)
        for index,part in enumerate(data['parts']):
            progress.progressValue=index
            progress.message='Creating '+part['name']+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled: return
            component=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
            component.name=f'{index+1:02d} - {part["name"]}'
            plane=component.xYConstructionPlane
            z=part['z']*THICKNESS_SCALE
            if z:
                plane_input=component.constructionPlanes.createInput()
                plane_input.setByOffset(plane,adsk.core.ValueInput.createByReal(z/10))
                plane=component.constructionPlanes.add(plane_input)
            sketch=component.sketches.add(plane)
            sketch.name='Contours '+part['name']
            sketch.isComputeDeferred=True
            outer_edges=[]
            lines=sketch.sketchCurves.sketchLines
            try:
                for group in part['groups']:
                    for loop_index,loop in enumerate(group):
                        points=[adsk.core.Point3D.create(x*factor/10,y*factor/10,0) for x,y in loop]
                        first=None;previous=None
                        for vertex in range(len(points)):
                            start=previous.endSketchPoint if previous else points[vertex]
                            end=first.startSketchPoint if vertex==len(points)-1 else points[(vertex+1)%len(points)]
                            line=lines.addByTwoPoints(start,end)
                            if first is None:first=line
                            previous=line
                        if loop_index==0:outer_edges.append(first)
            finally:
                sketch.isComputeDeferred=False
            outer_keys={edge_key(line) for line in outer_edges}
            selected=adsk.core.ObjectCollection.create()
            for profile in sketch.profiles:
                include=False
                for loop in profile.profileLoops:
                    if not loop.isOuter:continue
                    for curve in loop.profileCurves:
                        line=adsk.fusion.SketchLine.cast(curve.sketchEntity)
                        if line and edge_key(line) in outer_keys:
                            include=True;break
                if include:selected.add(profile)
            if selected.count!=len(part['groups']):
                raise RuntimeError(f'{part["name"]}: {selected.count} profiles found; '
                                   f'expected {len(part["groups"])}. Check sketch contours.')
            feature_input=component.features.extrudeFeatures.createInput(
                selected,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance=adsk.core.ValueInput.createByReal(part['height']*THICKNESS_SCALE/10)
            extent=adsk.fusion.DistanceExtentDefinition.create(distance)
            feature_input.setOneSideExtent(extent,adsk.fusion.ExtentDirections.PositiveExtentDirection)
            feature=component.features.extrudeFeatures.add(feature_input)
            feature.name='Relief '+part['name']
            rgb=tuple(int(part['color'][i:i+2],16) for i in (1,3,5))
            for body_index,body in enumerate(feature.bodies):
                body.name=f'{part["name"]} {body_index+1}'
                try:
                    appearance=design.appearances.addByCopy(body.appearance,
                                                          f'Joana {part["name"]} {body_index+1}')
                    for property_id in ('generic_diffuse','opaque_albedo'):
                        prop=adsk.core.ColorProperty.cast(appearance.appearanceProperties.itemById(property_id))
                        if prop:
                            prop.value=adsk.core.Color.create(*rgb,255)
                            body.appearance=appearance;break
                except Exception:pass
            sketch.isVisible=False
        progress.progressValue=4
        app.activeViewport.fit()
        ui.messageBox('Topper Joana 12 created.\n'
                      f'Width: {TARGET_WIDTH_MM:.0f} mm; height: {data["height_mm"]*factor:.1f} mm.\n'
                      'Four color components. Save the document as .f3d.\n'
                      'Use the supplied Bambu 3MF for aligned four-color printing.')
    except Exception:
        ui.messageBox('Joana topper creation failed:\n'+traceback.format_exc())
    finally:
        if progress:progress.hide()


def stop(context):pass
