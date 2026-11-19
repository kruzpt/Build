"""Cria um 3MF multipartes multicolor, sem inventar perfil de impressão U1."""
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
ASSEMBLY_ID = 10

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
part_stats = []
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
                      {"v1": str(a), "v2": str(b), "v3": str(c),
                       "pid": "5", "p1": str(object_id - 1)})
    part_stats.append((object_id, key, label, len(tri.faces)))

# Um único item de construção composto por quatro partes sobrepostas nas mesmas
# coordenadas. Assim o slicer recebe um conjunto multipartes, não quatro modelos
# soltos, mantendo cada cor selecionável.
assembly = ET.SubElement(resources, f"{{{NS}}}object",
                         {"id": str(ASSEMBLY_ID), "type": "model",
                          "name": "Panda Preguicoso V5 - conjunto 4 cores"})
components = ET.SubElement(assembly, f"{{{NS}}}components")
for object_id, _, _, _ in part_stats:
    ET.SubElement(components, f"{{{NS}}}component", {"objectid": str(object_id)})
build = ET.SubElement(model, f"{{{NS}}}build")
ET.SubElement(build, f"{{{NS}}}item", {"objectid": str(ASSEMBLY_ID)})

# Metadados reconhecidos pela família Orca/Bambu. Só registam a associação das
# quatro partes aos extrusores 1–4; não incluem máquina, nozzle nem perfil.
settings = ET.Element("config")
settings_object = ET.SubElement(settings, "object", {"id": str(ASSEMBLY_ID)})
ET.SubElement(settings_object, "metadata",
              {"key": "name", "value": "Panda Preguicoso V5 - 4 cores"})
for object_id, key, label, faces in part_stats:
    part = ET.SubElement(settings_object, "part",
                         {"id": str(object_id), "subtype": "normal_part"})
    ET.SubElement(part, "metadata", {"key": "name", "value": f"{label} [{key}]"})
    ET.SubElement(part, "metadata", {"key": "extruder", "value": str(object_id)})
    ET.SubElement(part, "mesh_stat",
                  {"face_count": str(faces), "edges_fixed": "0",
                   "degenerate_facets": "0", "facets_removed": "0",
                   "facets_reversed": "0", "backwards_edges": "0"})
plate = ET.SubElement(settings, "plate")
ET.SubElement(plate, "metadata", {"key": "plater_id", "value": "1"})
instance = ET.SubElement(plate, "model_instance")
ET.SubElement(instance, "metadata", {"key": "object_id", "value": str(ASSEMBLY_ID)})
ET.SubElement(instance, "metadata", {"key": "instance_id", "value": "0"})
settings_xml = ET.tostring(settings, encoding="utf-8", xml_declaration=True)

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
    archive.writestr("Metadata/model_settings.config", settings_xml)
with ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    parsed = ET.fromstring(archive.read("3D/3dmodel.model"))
    assert len(parsed.findall(f".//{{{NS}}}object")) == 5
    assert len(parsed.findall(f".//{{{NS}}}components/{{{NS}}}component")) == 4
    assert len(parsed.findall(f".//{{{NS}}}item")) == 1
    assert len(parsed.findall(f".//{{{NS}}}triangle[@pid='5']")) > 0
    parsed_settings = ET.fromstring(archive.read("Metadata/model_settings.config"))
    assert len(parsed_settings.findall(".//part")) == 4
    assert [p.find("metadata[@key='extruder']").get("value")
            for p in parsed_settings.findall(".//part")] == ["1", "2", "3", "4"]
    reopened_parts = {}
    for obj in parsed.findall(f".//{{{NS}}}object[@id]"):
        mesh = obj.find(f"{{{NS}}}mesh")
        if mesh is None:
            continue
        vertices = [[float(v.get(axis)) for axis in ("x", "y", "z")]
                    for v in mesh.findall(f"{{{NS}}}vertices/{{{NS}}}vertex")]
        faces = [[int(t.get(index)) for index in ("v1", "v2", "v3")]
                 for t in mesh.findall(f"{{{NS}}}triangles/{{{NS}}}triangle")]
        reopened = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        assert reopened.is_watertight and reopened.is_winding_consistent
        assert reopened.volume > 0
        reopened_parts[obj.get("name")] = {
            "watertight": True, "winding_consistent": True,
            "positive_volume_mm3": round(float(reopened.volume), 2),
            "components": len(reopened.split()),
        }
report = {"file": TARGET.name, "unit": "millimeter", "mesh_parts": 4,
          "assembly_build_items": 1, "selectable_colour_parts": 4,
          "materials": [label for _, label, _ in colors],
          "triangle_material_properties": True,
          "orca_extruder_mapping": {label: i for i, (_, label, _) in enumerate(colors, 1)},
          "geometry_reopened": True, "reopened_part_checks": reopened_parts,
          "snapmaker_slicer_import_tested": False,
          "print_profile_included": False}
(HERE / "3mf-validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
