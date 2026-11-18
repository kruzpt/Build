"""Create Universo do Saber V11: V10 finish plus anti-warp settings."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "downloads/universo-saber-suporte-v10-topo-sem-ironing-A1-AMS-2-pratos.3mf"
TARGET = ROOT / "downloads/universo-saber-suporte-v11-anti-empeno-A1-AMS-2-pratos.3mf"
FOLDER = ROOT / "fusion/UniversoSaberStandV11AntiEmpeno"
PREVIEW = ROOT / "designs/universo-saber-suporte-v11-anti-empeno-pratos.png"
BIN = Path("/tmp/bambu291/squashfs-root/bin/bambu-studio")
WORK = Path("/tmp/universo-v11-anti-empeno")


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


def run_cli(args: list[str], log: Path) -> None:
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:" + str(BIN.parent)
    with log.open("w") as stream:
        done = subprocess.run(
            [str(BIN), "--datadir", str(WORK / "user"), "--debug", "2", *args],
            cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT,
        )
    if done.returncode:
        raise RuntimeError(f"Bambu Studio exit {done.returncode}: {log}")


def create_project() -> dict[str, bytes]:
    source = read_zip(SOURCE)
    blobs = dict(source)
    config = json.loads(blobs["Metadata/project_settings.config"])
    config.update({
        "print_settings_id": "Universo V11 anti-empeno sem ironing A1 0.20",
        # 65 C no projeto anterior não impediu os cantos de levantar. 60 C
        # constante reduz a diferença térmica sem sacrificar a adesão do PLA.
        "textured_plate_temp_initial_layer": ["60", "60"],
        "textured_plate_temp": ["60", "60"],
        "hot_plate_temp_initial_layer": ["60", "60"],
        "hot_plate_temp": ["60", "60"],
        "brim_type": "outer_only",
        "brim_width": "5",
        "brim_object_gap": "0.15",
        "initial_layer_speed": ["15"],
        "initial_layer_infill_speed": ["25"],
        "initial_layer_acceleration": ["400"],
        "close_fan_the_first_x_layers": ["4", "4"],
        "full_fan_speed_layer": ["8", "8"],
        "fan_min_speed": ["50", "50"],
        "fan_max_speed": ["70", "70"],
        "auxiliary_fan": "0",
        # Preserve the approved V10 top finish settings.
        "ironing_type": "no ironing",
        "top_one_wall_type": "all top",
        "top_shell_layers": "8",
        "top_shell_thickness": "1.6",
        "top_surface_pattern": "monotonicline",
        "top_surface_speed": ["20"],
        "top_surface_acceleration": ["800"],
    })
    blobs["Metadata/project_settings.config"] = json.dumps(
        config, ensure_ascii=False, indent=2
    ).encode()

    model = etree.fromstring(blobs["Metadata/model_settings.config"])
    names = ("01 - V11 Placa anti-empeno", "02 - V11 Base anti-empeno")
    for plate, name in zip(model.findall("plate"), names):
        metadata_set(plate, "plater_name", name)
    blobs["Metadata/model_settings.config"] = etree.tostring(
        model, encoding="utf-8", xml_declaration=True
    )

    pictures = []
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    for index, title in enumerate(names, 1):
        image = Image.open(io.BytesIO(blobs[f"Metadata/plate_{index}.png"])).convert("RGB")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, 60), fill="white")
        draw.text((20, 17), title, font=font, fill="#17385B")
        stream = io.BytesIO(); image.save(stream, format="PNG")
        blobs[f"Metadata/plate_{index}.png"] = stream.getvalue()
        stream = io.BytesIO(); image.resize((128, 145)).save(stream, format="PNG")
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
    return source


def validate(source: dict[str, bytes]) -> dict:
    result = read_zip(TARGET)
    target_geometry = {n: hashlib.sha256(b).hexdigest() for n, b in result.items() if n.startswith("3D/")}
    source_geometry = {n: hashlib.sha256(b).hexdigest() for n, b in source.items() if n.startswith("3D/")}
    assert target_geometry == source_geometry
    cfg = json.loads(result["Metadata/project_settings.config"])
    expected = {
        "textured_plate_temp_initial_layer": ["60", "60"],
        "textured_plate_temp": ["60", "60"],
        "brim_type": "outer_only", "brim_width": "5", "brim_object_gap": "0.15",
        "initial_layer_speed": ["15"], "initial_layer_infill_speed": ["25"],
        "initial_layer_acceleration": ["400"],
        "close_fan_the_first_x_layers": ["4", "4"],
        "full_fan_speed_layer": ["8", "8"],
        "fan_min_speed": ["50", "50"], "fan_max_speed": ["70", "70"],
        "ironing_type": "no ironing", "top_one_wall_type": "all top",
    }
    for key, value in expected.items():
        assert cfg[key] == value, (key, cfg[key], value)

    WORK.mkdir(parents=True, exist_ok=True)
    reopen = WORK / "reopen"; reopen.mkdir(exist_ok=True)
    run_cli(["--info", "--outputdir", str(reopen), str(TARGET)], WORK / "reopen.log")
    sliced = WORK / "sliced"; sliced.mkdir(exist_ok=True)
    run_cli(["--slice", "0", "--orient", "0", "--arrange", "0",
             "--outputdir", str(sliced), "--export-3mf", "validation-only.3mf",
             str(TARGET)], WORK / "slice.log")
    slicing = json.loads((sliced / "result.json").read_text())
    assert slicing["return_code"] == 0 and len(slicing["sliced_plates"]) == 2
    assert all(not plate.get("warning_message") for plate in slicing["sliced_plates"])
    with ZipFile(sliced / "validation-only.3mf") as archive:
        gcodes = [archive.read(f"Metadata/plate_{i}.gcode").decode() for i in (1, 2)]
    for code in gcodes:
        assert "; FEATURE: Ironing" not in code
        assert re.search(r"M140 S60(?:\.0)?", code), "bed target 60 C missing"
        assert "; FEATURE: Brim" in code

    report = {
        "project": TARGET.name,
        "sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "source": SOURCE.name,
        "geometry_identical_to_v10": True,
        "machine": "Bambu Lab A1 0.4 nozzle",
        "material_assumption": "PLA; white nozzle range supplied by user 200-230 C",
        "nozzle_temperature_changed": False,
        "textured_plate_c": {"first_layer": 60, "other_layers": 60},
        "brim": {"type": "outer_only", "width_mm": 5, "object_gap_mm": 0.15},
        "first_layer": {"wall_mm_s": 15, "infill_mm_s": 25, "acceleration_mm_s2": 400},
        "cooling": {"fan_off_first_layers": 4, "full_fan_layer": 8, "min_percent": 50, "max_percent": 70, "auxiliary_fan": 0},
        "ironing": False,
        "one_wall_on_top_surfaces": "all top",
        "archive_reopened": True,
        "sliced_in_bambu_studio": True,
        "physical_anti_warp_tested": False,
        "plates": [{
            "name": "Placa branca e relevo azul" if i == 0 else "Base azul",
            "estimated_minutes": round(p["total_predication"] / 60, 1),
            "estimated_g": round(sum(f["total_used_g"] for f in p["filaments"]), 2),
            "warnings": p["warning_message"],
        } for i, p in enumerate(slicing["sliced_plates"])],
    }
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(validate(create_project()), ensure_ascii=False, indent=2))
