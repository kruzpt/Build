"""Create the M7 brick V3 BRep bodies in a NEW Autodesk Fusion document.

Keep geometry.json beside this script. Units in file: mm, Fusion API: cm.
The supplied Bambu projects are ready independently of this optional script.
"""
from pathlib import Path
import json
import traceback
import adsk.core
import adsk.fusion


def placement(rows):
    m=adsk.core.Matrix3D.create()
    p=adsk.core.Point3D.create(*(rows[i][3]/10 for i in range(3)))
    axes=[adsk.core.Vector3D.create(*(rows[i][j] for i in range(3))) for j in range(3)]
    if not m.setWithCoordinateSystem(p,*axes):raise RuntimeError('Transformação inválida')
    return m


def edge_key(line):
    a=line.startSketchPoint.geometry;b=line.endSketchPoint.geometry
    return tuple(sorted([(round(a.x,6),round(a.y,6)),(round(b.x,6),round(b.y,6))]))


def extrude(component,region,name):
    plane=component.xYConstructionPlane
    if region['z']:
        pi=component.constructionPlanes.createInput()
        pi.setByOffset(plane,adsk.core.ValueInput.createByReal(region['z']/10))
        plane=component.constructionPlanes.add(pi)
    sketch=component.sketches.add(plane);sketch.name=name
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
    keys={edge_key(v) for v in outer};profiles=adsk.core.ObjectCollection.create()
    for profile in sketch.profiles:
        include=False
        for loop in profile.profileLoops:
            if not loop.isOuter:continue
            for curve in loop.profileCurves:
                line=adsk.fusion.SketchLine.cast(curve.sketchEntity)
                if line and edge_key(line) in keys:include=True;break
        if include:profiles.add(profile)
    if profiles.count!=len(region['groups']):
        raise RuntimeError(f'{name}: {profiles.count} perfis; esperados {len(region["groups"])}')
    pi=component.features.extrudeFeatures.createInput(profiles,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    pi.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(region['height']/10)),adsk.fusion.ExtentDirections.PositiveExtentDirection)
    feature=component.features.extrudeFeatures.add(pi);feature.name=name
    sketch.isVisible=False
    bodies=[feature.bodies.item(i) for i in range(feature.bodies.count)]
    rows=region['transform']
    if any(abs(rows[i][j]-(1 if i==j else 0))>1e-10 for i in range(4) for j in range(4)):
        collection=adsk.core.ObjectCollection.create()
        for body in bodies:collection.add(body)
        mi=component.features.moveFeatures.createInput(collection,placement(rows))
        component.features.moveFeatures.add(mi).name='Posicionar '+name
    return bodies


def appearance(design,component,color):
    if not component.bRepBodies.count:return
    rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
    a=design.appearances.addByCopy(component.bRepBodies.item(0).appearance,'M7 '+color)
    for key in ('generic_diffuse','opaque_albedo'):
        prop=adsk.core.ColorProperty.cast(a.appearanceProperties.itemById(key))
        if prop:
            prop.value=adsk.core.Color.create(*rgb,255)
            for body in component.bRepBodies:body.appearance=a
            return


def run(context):
    app=adsk.core.Application.get();ui=app.userInterface;progress=None
    try:
        data=json.loads((Path(__file__).parent/'geometry.json').read_text(encoding='utf-8'))
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design=adsk.fusion.Design.cast(app.activeProduct)
        design.designType=adsk.fusion.DesignTypes.ParametricDesignType
        design.unitsManager.defaultLengthUnits='mm'
        root=design.rootComponent;root.name='Clinica Essencial Arcos 220 mm'
        progress=ui.createProgressDialog();progress.isCancelButtonShown=True
        progress.show('M7 - criar protótipos','A modelar (%p%)',0,len(data['parts']),0)
        for i,part in enumerate(data['parts']):
            progress.progressValue=i;progress.message=part['name']+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:return
            occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            component=occ.component;component.name=f'{part["product"]} - {part["name"]}'
            targets=[]
            for j,r in enumerate(part['regions']):
                created=extrude(component,r,f'{j+1:02d} - {part["name"]}')
                if r['operation']=='new':targets+=created
                else:
                    tools=adsk.core.ObjectCollection.create()
                    for body in created:tools.add(body)
                    ci=component.features.combineFeatures.createInput(targets[0],tools)
                    ci.operation=(adsk.fusion.FeatureOperations.JoinFeatureOperation if r['operation']=='join'
                                  else adsk.fusion.FeatureOperations.CutFeatureOperation)
                    ci.isKeepToolBodies=False
                    result=component.features.combineFeatures.add(ci)
                    targets=[result.bodies.item(0)]
            appearance(design,component,part['color'])
            tm=[row[:] for row in part['assembly']]
            occ.transform2=placement(tm)
        if design.snapshots.hasPendingSnapshot:design.snapshots.add()
        progress.progressValue=len(data['parts']);app.activeViewport.fit()
        ui.messageBox('Expositor Essencial 220 criado num documento novo.\n'
            'Conjunto: 220 x 80 x 220 mm; dois encaixes independentes.\n'
            'Use o projeto 3MF Essencial Arcos 220 para imprimir.\n'
            'Faça a montagem a seco antes de colar.')
    except Exception:ui.messageBox('Falha ao criar M7:\n'+traceback.format_exc())
    finally:
        if progress:progress.hide()


def stop(context):pass
