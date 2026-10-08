"""Build the optimized V3 without changing the original V3 geometry."""
import ast
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]

BATCH_HELPER='''        def build_qr(platform, rows, bottom):
            # All disjoint strips in one deferred sketch and one extrusion.
            pitch = QR_SIZE/len(rows)
            strips = list(qr_runs(rows))
            sk = sketch(c, platform+' QR - batched', PANEL_THICKNESS-0.02)
            try:
                lines = sk.sketchCurves.sketchLines
                for index,(row,start,end) in enumerate(strips):
                    x0=QR_X+start*pitch+0.01
                    x1=QR_X+end*pitch-0.01
                    y0=bottom+(len(rows)-row-1)*pitch+0.01
                    y1=bottom+(len(rows)-row)*pitch-0.01
                    # Explicit lines avoid unnecessary horizontal/vertical
                    # constraints automatically created by the rectangle helper.
                    corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
                    for a,b in zip(corners,corners[1:]+corners[:1]):
                        lines.addByTwoPoints(point(*a),point(*b))
                    if index % 64 == 0:
                        update_progress(76 if platform=='Instagram' else 86,
                            platform+' QR: drawing %d/%d strips' %
                            (index+1,len(strips)))
            finally:
                sk.isComputeDeferred = False
            if sk.profiles.count != len(strips):
                raise RuntimeError(platform+' QR: unexpected profile count %d/%d' %
                                   (sk.profiles.count,len(strips)))
            profiles=adsk.core.ObjectCollection.create()
            for index in range(sk.profiles.count):
                profiles.add(sk.profiles.item(index))
            update_progress(80 if platform=='Instagram' else 90,
                            platform+' QR: joining all strips (one operation)')
            feature=c.features.extrudeFeatures.addSimple(profiles,
                adsk.core.ValueInput.createByReal(0.062),
                ops.JoinFeatureOperation)
            feature.name=platform+' QR - single extrusion'
            sk.isVisible=False

'''


def main():
    source=(ROOT/'fusion/EssencialV3/EssencialV3.py').read_text()
    source=source.replace('def run(context):',
        'class BuildCancelled(Exception):\n    pass\n\n\ndef run(context):')
    source=source.replace('    ui = app.userInterface\n    try:',
        '''    ui = app.userInterface
    progress = None
    current_stage = 'Preparing'
    try:''',1)
    marker='        design = adsk.fusion.Design.cast(app.activeProduct)'
    source=source.replace(marker,'''        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = True
        progress.cancelButtonText = 'Cancel'
        progress.show('Clinica Essencial V3 Fast', 'Preparing (%p%)', 0, 100, 0)

        def update_progress(value, message):
            nonlocal current_stage
            current_stage = message
            progress.progressValue = value
            progress.message = message+' (%p%)'
            adsk.doEvents()
            if progress.wasCancelled:
                raise BuildCancelled()

        update_progress(1, 'Creating components')
'''+marker,1)
    source=source.replace('            sk.name = name\n            return sk',
        '''            sk.name = name
            sk.isVisible = False
            sk.isComputeDeferred = True
            return sk''',1)
    source=source.replace('        def extrude(c, sk, name, depth):\n',
        '''        def extrude(c, sk, name, depth):
            sk.isComputeDeferred = False
''',1)
    source=source.replace('        c = plate_component\n',
                          "        update_progress(5, 'Plate and logo silhouette')\n        c = plate_component\n",1)
    source=source.replace('        # Engraved custom serif E',
        "        update_progress(12, 'Curved clinic logo')\n        # Engraved custom serif E",1)
    source=source.replace('        for region,index,x,y,w,h in vertebra_layout():',
        '''        for spine_index,(region,index,x,y,w,h) in enumerate(vertebra_layout()):
            update_progress(20+spine_index, 'Spine: vertebra %d/24' % (spine_index+1))''',1)
    source=source.replace('        for platform, rows, bottom in row_layout():',
        "        update_progress(46, 'Social and contactless symbols')\n"+BATCH_HELPER+
        "        for platform, rows, bottom in row_layout():\n"+
        "            update_progress(48 if platform=='Instagram' else 58, platform+' symbols and tag pocket')",1)
    start=source.index('            pitch = QR_SIZE/len(rows)\n',
                       source.index('        for platform, rows, bottom in row_layout():'))
    end=source.index('            # Three contactless arcs',start)
    source=source[:start]+source[end:]
    source=source.replace('                text = sk.sketchTexts.add(inp)\n',
        '                text = sk.sketchTexts.add(inp)\n                sk.isComputeDeferred = False\n',1)
    source=source.replace('            except Exception:\n                if sk:\n',
        '            except Exception:\n                if sk:\n                    sk.isComputeDeferred = False\n',1)
    source=source.replace("        label('CLINICA',18,163,116,9)",
        "        update_progress(70, 'Clinic lettering')\n        label('CLINICA',18,163,116,9)",1)
    source=source.replace("        plate.name = 'Plate - one solid with integrated spine'",
        '''        # Join QR geometry last, after all plate cutting/decorative features.
        for platform, rows, bottom in row_layout():
            build_qr(platform, rows, bottom)
        plate.name = 'Plate - one solid with integrated spine' ''',1)
    source=source.replace("        plate.name = 'Plate - one solid with integrated spine' \n",
                          "        plate.name = 'Plate - one solid with integrated spine'\n")
    source=source.replace('        b = base_component',
        "        update_progress(94, 'Slotted base')\n        b = base_component",1)
    source=source.replace('        app.activeViewport.fit()',
        "        update_progress(100, 'Checking two solids')\n        app.activeViewport.fit()\n        progress.hide()",1)
    source=source.replace('V3 created: TWO parts','V3 Fast created: TWO parts')
    old_tail="    except Exception:\n        ui.messageBox('V3 creation failed:\\n'+traceback.format_exc())\n"
    new_tail='''    except BuildCancelled:
        if progress:
            progress.hide()
        ui.messageBox('Cancelled. You can close the partial NEW document without saving.')
    except Exception:
        if progress:
            progress.hide()
        ui.messageBox('V3 Fast failed during '+current_stage+':\\n'+traceback.format_exc())
    finally:
        if progress:
            progress.hide()

'''
    assert source.endswith(old_tail), 'Original exception handler changed.'
    source=source[:-len(old_tail)]+new_tail
    source=source.rstrip()+'\n'
    ast.parse(source)
    folder=ROOT/'fusion/EssencialV3Fast'
    folder.mkdir(exist_ok=True)
    (folder/'EssencialV3Fast.py').write_text(source)
    with ZipFile(ROOT/'downloads/essencial-fusion-v3-fast.zip','w',ZIP_DEFLATED) as z:
        z.write(folder/'EssencialV3Fast.py','EssencialV3Fast/EssencialV3Fast.py')
        z.write(folder/'README.md','README.md')
        z.write(ROOT/'designs/essencial-v3-esquema.png','essencial-v3-esquema.png')
    print('Optimized V3 generated; batched QR sketches, deferred solves and progress dialog.')


if __name__=='__main__':
    main()
