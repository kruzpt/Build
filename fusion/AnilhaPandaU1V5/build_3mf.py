"""Cria um 3MF geométrico multicolor, sem inventar perfil de impressão U1."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET
import json
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = ROOT / "downloads/anilha-panda-preguicoso-v5-Snapmaker-U1-4-cores.3mf"
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)

colors = (("black", "Preto", "#252525FF"),
          ("ivory", "Branco creme", "#F2E9DAFF"),
          ("green", "Verde bambu", "#73AE18FF"),
          ("tan", "Bege almofadas", "#D8A36BFF"))
model = ET.Element(f"{{{NS}}}model", {"unit": "millimeter", "xml:lang": "pt-PT"})
metadata = ET.SubElement(model, f"{{{NS}}}metadata", {"name": "Title"})
metadata.text = "Panda Preguiçoso V5 — Snapmaker U1 — quatro cores"
resources = ET.SubElement(model, f"{{{NS}}}resources")
materials = ET.SubElement(resources, f"{{{NS}}}basematerials", {"id": "5"})
for _, label, color in colors:
    ET.SubElement(materials, f"{{{NS}}}base", {"name": label, "displaycolor": color})
build = ET.SubElement(model, f"{{{NS}}}build")

for object_id, (key, label, _) in enumerate(colors, 1):
    tri = trimesh.load(HERE / "stl" / f"panda-{key}.stl", force="mesh")
    obj = ET.SubElement(resources, f"{{{NS}}}object",
                        {"id": str(object_id), "type": "model", "name": label,
                         "pid": "5", "pindex": str(object_id - 1)})
    mesh = ET.SubElement(obj, f"{{{NS}}}mesh")
    vertices = ET.SubElement(mesh, f"{{{NS}}}vertices")
    for x, y, z in tri.vertices:
        ET.SubElement(vertices, f"{{{NS}}}vertex",
                      {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
    triangles = ET.SubElement(mesh, f"{{{NS}}}triangles")
    for a, b, c in tri.faces:
        ET.SubElement(triangles, f"{{{NS}}}triangle",
                      {"v1": str(a), "v2": str(b), "v3": str(c)})
    ET.SubElement(build, f"{{{NS}}}item", {"objectid": str(object_id)})

model_xml = ET.tostring(model, encoding="utf-8", xml_declaration=True)
content_types = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>'''
rels = b'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
TARGET.parent.mkdir(exist_ok=True)
with ZipFile(TARGET, "w", ZIP_DEFLATED) as archive:
    archive.writestr("[Content_Types].xml", content_types)
    archive.writestr("_rels/.rels", rels)
    archive.writestr("3D/3dmodel.model", model_xml)
with ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    parsed = ET.fromstring(archive.read("3D/3dmodel.model"))
    assert len(parsed.findall(f".//{{{NS}}}object")) == 4
    assert len(parsed.findall(f".//{{{NS}}}item")) == 4
report = {"file": TARGET.name, "unit": "millimeter", "objects": 4,
          "materials": [label for _, label, _ in colors],
          "geometry_reopened": True, "snapmaker_slicer_import_tested": False,
          "print_profile_included": False}
(HERE / "3mf-validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
