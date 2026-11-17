"""Create Universo do Saber V10: controlled top surfaces without ironing."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "downloads/universo-saber-suporte-v9-base-lisa-A1-AMS-2-pratos.3mf"
TARGET = ROOT / "downloads/universo-saber-suporte-v10-topo-sem-ironing-A1-AMS-2-pratos.3mf"
FOLDER = ROOT / "fusion/UniversoSaberStandV10SemIroning"
PREVIEW = ROOT / "designs/universo-saber-suporte-v10-topo-sem-ironing-pratos.png"


def read_zip(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        return {name: archive.read(name) for name in archive.namelist()}


def metadata_set(node, key: str, value: str) -> None:
    entries = node.findall(f"metadata[@key='{key}']")
    if entries:
        entries[0].set("value", value)
        for duplicate in entries[1:]:
            node.remove(duplicate)
    else:
        etree.SubElement(node, "metadata", key=key, value=value)


def metadata_remove(root, key: str) -> None:
    for node in root.xpath(f".//metadata[@key='{key}']"):
        node.getparent().remove(node)


def create_project() -> dict:
    source = read_zip(SOURCE)
    blobs = dict(source)
    config = json.loads(blobs["Metadata/project_settings.config"])
    config.update({
        "print_settings_id": "Universo V10 topo sem ironing A1 0.20",
        "ironing_type": "no ironing",
        "top_one_wall_type": "all top",
        "top_shell_layers": "8",
        "top_shell_thickness": "1.6",
        "top_surface_pattern": "monotonicline",
        "top_surface_speed": ["20"],
        "top_surface_acceleration": ["800"],
        "internal_solid_infill_speed": ["45"],
        "outer_wall_speed": ["35"],
        "inner_wall_speed": ["70"],
        "wall_loops": "3",
        "brim_type": "no_brim",
        "brim_width": "0",
        "enable_support": ["0"],
    })
    blobs["Metadata/project_settings.config"] = json.dumps(
        config, ensure_ascii=False, indent=2
    ).encode()

    model = etree.fromstring(blobs["Metadata/model_settings.config"])
    objects = model.findall("object")
    assert len(objects) == 2
    assembled = next(obj for obj in objects if len(obj.findall("part")) == 2)
    base = next(obj for obj in objects if len(obj.findall("part")) == 1)

    # V7-V9 enabled ironing and disabled the one-wall top rule through object
    # overrides. Remove both families of overrides so the V10 global process
    # settings are authoritative for every printable part.
    metadata_remove(model, "ironing_type")
    metadata_remove(model, "top_one_wall_type")

    # Retain the V9 base reinforcement that reduced infill print-through.
    metadata_set(base, "sparse_infill_density", "35%")
    metadata_set(base, "sparse_infill_pattern", "gyroid")
    metadata_set(base, "wall_loops", "4")
    metadata_set(base, "top_shell_layers", "9")
    metadata_set(base, "top_shell_thickness", "1.8")

    names = (
        "01 - V10 Placa e letras sem ironing",
        "02 - V10 Base azul sem ironing",
    )
    for plate, name in zip(model.findall("plate"), names):
        metadata_set(plate, "plater_name", name)
    blobs["Metadata/model_settings.config"] = etree.tostring(
        model, encoding="utf-8", xml_declaration=True
    )

    pictures = []
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18
    )
    for index, title in enumerate(names, 1):
        image = Image.open(io.BytesIO(blobs[f"Metadata/plate_{index}.png"])).convert("RGB")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, 60), fill="white")
        draw.text((20, 17), title, font=font, fill="#17385B")
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        blobs[f"Metadata/plate_{index}.png"] = stream.getvalue()
        stream = io.BytesIO()
        image.resize((128, 145)).save(stream, format="PNG")
        blobs[f"Metadata/plate_{index}_small.png"] = stream.getvalue()
        pictures.append(image)

    overview = Image.new("RGB", (pictures[0].width * 2, pictures[0].height), "white")
    for index, picture in enumerate(pictures):
        overview.paste(picture, (index * picture.width, 0))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    overview.save(PREVIEW)

    with ZipFile(TARGET, "w", ZIP_DEFLATED) as archive:
        for name, blob in blobs.items():
            archive.writestr(name, blob)

    result = read_zip(TARGET)
    assert result.keys() == blobs.keys()
    assert all(result[name] == blob for name, blob in blobs.items())
    source_geometry = {
        name: hashlib.sha256(blob).hexdigest()
        for name, blob in source.items()
        if name.startswith("3D/")
    }
    target_geometry = {
        name: hashlib.sha256(blob).hexdigest()
        for name, blob in result.items()
        if name.startswith("3D/")
    }
    assert target_geometry == source_geometry

    saved_config = json.loads(result["Metadata/project_settings.config"])
    saved_model = etree.fromstring(result["Metadata/model_settings.config"])
    assert saved_config["ironing_type"] == "no ironing"
    assert saved_config["top_one_wall_type"] == "all top"
    assert saved_config["top_shell_layers"] == "8"
    assert saved_config["top_shell_thickness"] == "1.6"
    assert saved_config["top_surface_speed"] == ["20"]
    assert saved_config["internal_solid_infill_speed"] == ["45"]
    assert not saved_model.xpath(".//metadata[@key='ironing_type']")
    assert not saved_model.xpath(".//metadata[@key='top_one_wall_type']")
    saved_objects = saved_model.findall("object")
    saved_base = next(obj for obj in saved_objects if len(obj.findall("part")) == 1)
    base_values = {m.get("key"): m.get("value") for m in saved_base.findall("metadata")}
    assert base_values["top_shell_layers"] == "9"
    assert base_values["top_shell_thickness"] == "1.8"
    assert base_values["wall_loops"] == "4"
    assert base_values["sparse_infill_density"] == "35%"

    report = {
        "project": TARGET.name,
        "sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "source": SOURCE.name,
        "geometry_identical_to_v9": True,
        "machine_from_source_project": "Bambu Lab A1 0.4 nozzle",
        "layer_height_mm": 0.2,
        "ironing": False,
        "one_wall_on_top_surfaces": "all top",
        "global_top_layers": 8,
        "global_top_thickness_mm": 1.6,
        "base_top_layers": 9,
        "base_top_thickness_mm": 1.8,
        "top_surface_speed_mm_s": 20,
        "top_surface_acceleration_mm_s2": 800,
        "internal_solid_infill_speed_mm_s": 45,
        "top_surface_pattern": "monotonic line",
        "base_infill": "35% gyroid",
        "brim": False,
        "supports": False,
        "archive_and_settings_validated": True,
        "sliced_in_current_environment": False,
        "physical_finish_tested": False,
    }
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(create_project(), ensure_ascii=False, indent=2))
