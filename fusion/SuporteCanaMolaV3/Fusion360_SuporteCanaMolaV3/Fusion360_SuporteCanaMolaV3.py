"""Importa o CAD V3 validado para um documento editável do Autodesk Fusion.

Copiar esta pasta para Scripts and Add-Ins do Fusion e executar o script.
Os STEP devem permanecer um nível acima desta pasta, como no projeto entregue.
"""
import adsk.core
import adsk.fusion
import os
import traceback


PARTS = (
    ("corpo_fixo.step", "Corpo fixo PETG"),
    ("braco_movel.step", "Braço móvel PETG"),
    ("tpu_superior.step", "Inserto TPU superior"),
    ("tpu_inferior.step", "Inserto TPU inferior"),
)

PARAMETERS = (
    ("rodMaxD", "28 mm", "Diâmetro máximo validado da cana"),
    ("rodClearance", "0.8 mm", "Folga radial estrutural"),
    ("tpuThickness", "1.2 mm", "Espessura nominal dos insertos TPU"),
    ("pivotD", "4 mm", "Diâmetro nominal do eixo oculto"),
    ("springOuterD", "7 mm", "Diâmetro exterior máximo da mola"),
    ("springSeatOuterD", "8.6 mm", "Diâmetro exterior do rebaixo anular"),
    ("springSeatIslandD", "4.2 mm", "Diâmetro da ilha central nivelada"),
    ("springSeatDepth", "1.2 mm", "Profundidade do rebaixo anular"),
    ("maxOpenAngle", "45 deg", "Abertura máxima validada"),
)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        missing = [name for name, _ in PARTS
                   if not os.path.isfile(os.path.join(project_dir, name))]
        if missing:
            ui.messageBox("Faltam ficheiros STEP:\n" + "\n".join(missing))
            return

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent
        root.name = "Suporte cana mola V3 — sem parafusos"

        units = design.unitsManager.defaultLengthUnits
        user_params = design.userParameters
        for name, expression, comment in PARAMETERS:
            if user_params.itemByName(name) is None:
                unit = "deg" if expression.endswith("deg") else units
                user_params.add(name, adsk.core.ValueInput.createByString(expression),
                                unit, comment)

        importer = app.importManager
        imported = []
        for filename, label in PARTS:
            path = os.path.join(project_dir, filename)
            before_occ = root.occurrences.count
            before_body = root.bRepBodies.count
            options = importer.createSTEPImportOptions(path)
            importer.importToTarget(options, root)
            if root.occurrences.count > before_occ:
                entity = root.occurrences.item(root.occurrences.count - 1)
                entity.component.name = label
                imported.append(label)
            elif root.bRepBodies.count > before_body:
                for i in range(before_body, root.bRepBodies.count):
                    root.bRepBodies.item(i).name = label
                imported.append(label)
            else:
                raise RuntimeError("O Fusion não devolveu geometria para " + filename)

        output_dir = os.path.join(os.path.expanduser("~"), "Documents")
        output_path = os.path.join(output_dir, "SuporteCanaMolaV3_Fusion.f3d")
        export_note = ""
        if not os.path.exists(output_path):
            export_options = design.exportManager.createFusionArchiveExportOptions(output_path)
            if design.exportManager.execute(export_options):
                export_note = "\nArquivo F3D: " + output_path
        else:
            export_note = "\nF3D existente não foi substituído: " + output_path

        ui.messageBox("Importação concluída.\nComponentes: " +
                      ", ".join(imported) +
                      "\nParâmetros documentados: " + str(len(PARAMETERS)) +
                      export_note)
    except Exception:
        ui.messageBox("Erro no script:\n" + traceback.format_exc())


def stop(context):
    pass
