#!/usr/bin/env python3
"""Gera os STL e 3MF dos tres perfis do gorro personalizavel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCAD = HERE / "GorroNatalPersonalizavelV5.scad"
DOWNLOADS = ROOT / "downloads"
DESIGNS = ROOT / "designs"

PRESETS = {
    "curto": "Lia",
    "medio": "Tomás",
    "comprido": "Alexandre",
}

COLORS = {
    "vermelho": "#A71930FF",
    "branco": "#F4E8D4FF",
}


def run_openscad(output: Path, *, part: str, profile: str, name: str) -> None:
    env = os.environ.copy()
    font_home = Path("/tmp/gorro-v5-font-data")
    (font_home / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "fonts/Lobster-Regular.ttf", font_home / "fonts/Lobster-Regular.ttf")
    env["XDG_DATA_HOME"] = str(font_home)
    env.setdefault("XDG_CACHE_HOME", "/tmp/gorro-natal-font-cache")
    command = [
        "openscad",
        "-o", str(output),
        "-D", f'parte="{part}"',
        "-D", f'perfil="{profile}"',
        "-D", f'nome="{name}"',
        str(SCAD),
    ]
    subprocess.run(command, check=True, env=env, capture_output=True, text=True)


def load_mesh(path: Path) -> trimesh.Trimesh:
    # STL repete vertices por triangulo; o processamento une-os antes da
    # verificacao topologica sem alterar as coordenadas da geometria.
    loaded = trimesh.load(path, force="mesh", process=True)
    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"{path.name} nao produziu uma malha")
    loaded.remove_unreferenced_vertices()
    if not loaded.is_watertight:
        raise ValueError(f"{path.name} nao e estanque")
    return loaded


def mesh_xml(parent: ET.Element, mesh: trimesh.Trimesh) -> None:
    mesh_node = ET.SubElement(parent, "mesh")
    vertices = ET.SubElement(mesh_node, "vertices")
    for x, y, z in np.asarray(mesh.vertices):
        ET.SubElement(vertices, "vertex", x=f"{x:.6f}", y=f"{y:.6f}", z=f"{z:.6f}")
    triangles = ET.SubElement(mesh_node, "triangles")
    for a, b, c in np.asarray(mesh.faces):
        ET.SubElement(triangles, "triangle", v1=str(a), v2=str(b), v3=str(c))


def write_3mf(path: Path, meshes: list[tuple[str, trimesh.Trimesh, int]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", unit="millimeter", **{"xml:lang": "pt-PT"})
    ET.SubElement(model, f"{{{ns}}}metadata", name="Title").text = "Gorro de Natal personalizavel"
    ET.SubElement(model, f"{{{ns}}}metadata", name="Designer").text = "kruzpt/Build"
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    materials = ET.SubElement(resources, f"{{{ns}}}basematerials", id="1")
    ET.SubElement(materials, f"{{{ns}}}base", name="Vermelho", displaycolor=COLORS["vermelho"])
    ET.SubElement(materials, f"{{{ns}}}base", name="Branco", displaycolor=COLORS["branco"])

    object_ids = []
    for object_id, (label, mesh, material_index) in enumerate(meshes, start=2):
        obj = ET.SubElement(
            resources,
            f"{{{ns}}}object",
            id=str(object_id),
            type="model",
            name=label,
            pid="1",
            pindex=str(material_index),
        )
        mesh_xml(obj, mesh)
        object_ids.append(object_id)

    # Um unico objeto composto impede o Bambu Studio de recentrar cada cor
    # separadamente durante a importacao.
    assembly_id = max(object_ids) + 1
    assembly = ET.SubElement(
        resources, f"{{{ns}}}object", id=str(assembly_id), type="model",
        name="Gorro de Natal V5",
    )
    components = ET.SubElement(assembly, f"{{{ns}}}components")
    for object_id in object_ids:
        ET.SubElement(components, f"{{{ns}}}component", objectid=str(object_id))

    build = ET.SubElement(model, f"{{{ns}}}build")
    ET.SubElement(build, f"{{{ns}}}item", objectid=str(assembly_id))

    model_xml = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>'''
    relationships = b'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("3D/3dmodel.model", model_xml)


def bounds_list(mesh: trimesh.Trimesh) -> list[list[float]]:
    return np.round(mesh.bounds, 3).tolist()


def slug_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if char.isascii() and char.isalnum()).lower()


def render_mesh_top(
    draw: ImageDraw.ImageDraw,
    mesh: trimesh.Trimesh,
    *,
    origin: tuple[float, float],
    scale: float,
    color: str,
    minimum_z: float,
) -> None:
    vertices = np.asarray(mesh.vertices)
    normals = np.asarray(mesh.face_normals)
    centroids = np.asarray(mesh.triangles_center)
    for face, normal, centroid in zip(mesh.faces, normals, centroids):
        if normal[2] < 0.99 or centroid[2] < minimum_z:
            continue
        points = []
        for x, y, _ in vertices[face]:
            points.append((origin[0] + x * scale, origin[1] - y * scale))
        draw.polygon(points, fill=color)


def render_preview(
    body: trimesh.Trimesh,
    white: trimesh.Trimesh,
    text_meshes: dict[str, trimesh.Trimesh],
) -> Path:
    factor = 2
    width, height = 1500 * factor, 650 * factor
    image = Image.new("RGB", (width, height), "#F8F2E9")
    draw = ImageDraw.Draw(image)
    scale = 5.0 * factor
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    title_font = ImageFont.truetype(bold_path, 30 * factor)
    label_font = ImageFont.truetype(font_path, 21 * factor)
    small_font = ImageFont.truetype(font_path, 17 * factor)
    draw.text((55 * factor, 30 * factor), "Gorro de Natal V5 — curvas aprovadas", fill="#641522", font=title_font)

    centers = [250, 750, 1250]
    for center, (profile, name) in zip(centers, PRESETS.items()):
        origin = (center * factor, 535 * factor)
        render_mesh_top(draw, body, origin=origin, scale=scale, color="#A71930", minimum_z=2.99)
        render_mesh_top(draw, body, origin=origin, scale=scale, color="#7F1225", minimum_z=3.49)
        render_mesh_top(draw, white, origin=origin, scale=scale, color="#F4E8D4", minimum_z=3.79)
        render_mesh_top(draw, text_meshes[profile], origin=origin, scale=scale, color="#A71930", minimum_z=4.59)
        caption = f"{profile.upper()} — {name}"
        box = draw.textbbox((0, 0), caption, font=label_font)
        draw.text(((center * factor) - (box[2] - box[0]) / 2, 560 * factor), caption, fill="#641522", font=label_font)

    note = "102,5 × 96,1 × 4,6 mm · curvas Bézier · sem suportes"
    box = draw.textbbox((0, 0), note, font=small_font)
    draw.text(((width - (box[2] - box[0])) / 2, 610 * factor), note, fill="#6E5552", font=small_font)
    image = image.resize((1500, 650), Image.Resampling.LANCZOS)
    DESIGNS.mkdir(parents=True, exist_ok=True)
    path = DESIGNS / "gorro-natal-v5-tres-nomes-CAD.png"
    image.save(path, optimize=True)
    return path


def build(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "model": "GorroNatalPersonalizavelV5",
        "units": "mm",
        "printer_assumption": "FDM, bico 0.4 mm",
        "physical_print_tested": False,
        "bambu_studio_tested": False,
        "profiles": {},
    }

    with tempfile.TemporaryDirectory(prefix="gorro-natal-") as tmp:
        tmp_dir = Path(tmp)
        body_path = tmp_dir / "corpo-vermelho.stl"
        white_path = tmp_dir / "detalhes-brancos.stl"
        run_openscad(body_path, part="corpo", profile="medio", name="Tomás")
        run_openscad(white_path, part="branco", profile="medio", name="Tomás")
        body = load_mesh(body_path)
        white = load_mesh(white_path)

        shared_body = output_dir / "gorro-natal-v5-corpo-vermelho.stl"
        shared_white = output_dir / "gorro-natal-v5-detalhes-brancos.stl"
        shared_body.write_bytes(body_path.read_bytes())
        shared_white.write_bytes(white_path.read_bytes())

        text_meshes: dict[str, trimesh.Trimesh] = {}
        for profile, name in PRESETS.items():
            slug = f"gorro-natal-v5-{profile}-{slug_text(name)}"
            text_path = tmp_dir / f"{slug}-nome.stl"
            complete_path = tmp_dir / f"{slug}-completo.stl"
            run_openscad(text_path, part="nome", profile=profile, name=name)
            run_openscad(complete_path, part="completo", profile=profile, name=name)
            text_mesh = load_mesh(text_path)
            text_meshes[profile] = text_mesh
            complete = load_mesh(complete_path)

            final_text = output_dir / f"{slug}-nome-vermelho.stl"
            final_complete = output_dir / f"{slug}-monocor.stl"
            final_3mf = output_dir / f"{slug}-2-cores.3mf"
            final_text.write_bytes(text_path.read_bytes())
            final_complete.write_bytes(complete_path.read_bytes())
            write_3mf(
                final_3mf,
                [
                    ("Corpo vermelho", body, 0),
                    ("Detalhes brancos", white, 1),
                    (f"Nome {name} ({profile})", text_mesh, 0),
                ],
            )
            with zipfile.ZipFile(final_3mf) as archive:
                if "3D/3dmodel.model" not in archive.namelist():
                    raise ValueError(f"3MF incompleto: {final_3mf.name}")

            report["profiles"][profile] = {
                "example_name": name,
                "text_bounds_mm": bounds_list(text_mesh),
                "complete_bounds_mm": bounds_list(complete),
                "complete_watertight": bool(complete.is_watertight),
                "3mf_sha256": hashlib.sha256(final_3mf.read_bytes()).hexdigest(),
            }

        preview = render_preview(body, white, text_meshes)
        report["preview"] = str(preview.relative_to(ROOT))

    (HERE / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DOWNLOADS)
    args = parser.parse_args()
    report = build(args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
