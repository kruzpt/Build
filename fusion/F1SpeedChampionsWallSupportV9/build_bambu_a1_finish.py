"""Build the high-finish A1 profile for the approved V9 support."""
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import trimesh

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "fusion" / "tools"))
from build_pintos_pla_3mf import flatten_profile, read_project, run_cli
from build_m7_prototypes_v1_3mf import annotate, plate_meshes

FOLDER = ROOT / "fusion" / "F1SpeedChampionsWallSupportV9"
PREFIX = "suporte-f1-speed-champions-piloto-v9"
PROJECT_PREFIX = "suporte-f1-speed-champions-piloto-v9-acabamento"
BAMBU = Path("/tmp/bambu-studio-2.9.1/squashfs-root/bin/bambu-studio")
PROFILES = BAMBU.parent.parent / "resources" / "profiles" / "BBL"
WORK = Path("/tmp/f1-speed-champions-wall-support-v9-finish")


def orient(source, target, rotation):
    mesh = trimesh.load(source, force="mesh")
    matrix = trimesh.transformations.rotation_matrix(np.radians(rotation[0]), [1, 0, 0])
    matrix = trimesh.transformations.rotation_matrix(np.radians(rotation[1]), [0, 1, 0]) @ matrix
    mesh.apply_transform(matrix)
    mesh.apply_translation([0, 0, -mesh.bounds[0, 2]])
    mesh.export(target)
    check = trimesh.load(target, force="mesh")
    assert check.is_watertight
    return check


def package(project):
    entries = [
        project,
        ROOT / "downloads" / f"{PREFIX}.stl",
        ROOT / "downloads" / "suporte-f1-v9-amostra-berco-pneu.stl",
        ROOT / "downloads" / "suporte-f1-v9-amostras-piloto.stl",
        FOLDER / "F1SpeedChampionsWallSupportV9.scad",
        FOLDER / "README.md",
        FOLDER / "bambu-validation-acabamento.json",
        Path(__file__),
        ROOT / "designs" / "suporte-f1-v9-conceito-piloto-integrado-berco.png",
        ROOT / "designs" / f"{PROJECT_PREFIX}-pratos.png",
    ]
    target = ROOT / "downloads" / f"{PROJECT_PREFIX}-pacote.zip"
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for entry in entries:
            archive.write(entry, entry.name)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ["LD_LIBRARY_PATH"] = "/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:" + str(BAMBU.parent)

    complete = orient(ROOT / "downloads" / f"{PREFIX}.stl", WORK / "complete-flat.stl", (90, 0))
    cradle = orient(ROOT / "downloads" / "suporte-f1-v9-amostra-berco-pneu.stl", WORK / "cradle-flat.stl", (0, 90))
    pilot = orient(ROOT / "downloads" / "suporte-f1-v9-amostras-piloto.stl", WORK / "pilot-flat.stl", (0, 0))

    machine = flatten_profile(PROFILES, "machine", "Bambu Lab A1 0.4 nozzle")
    process = flatten_profile(PROFILES, "process", "0.12mm High Quality @BBL A1")
    process.update({
        "name": "Suporte F1 V9 A1 PLA 0.12 acabamento overhang", "from": "User",
        "layer_height": "0.12", "initial_layer_print_height": "0.20",
        "wall_loops": "4", "wall_generator": "arachne",
        "sparse_infill_density": "25%", "sparse_infill_pattern": "gyroid",
        "top_shell_layers": "5", "bottom_shell_layers": "5",
        "outer_wall_speed": ["30"], "inner_wall_speed": ["60"],
        "top_surface_speed": ["25"], "bridge_speed": ["20"],
        "overhang_1_4_speed": ["25"], "overhang_2_4_speed": ["20"],
        "overhang_3_4_speed": ["15"], "overhang_4_4_speed": ["10"],
        "seam_position": "back", "resolution": "0.008",
        "initial_layer_speed": ["20"], "initial_layer_infill_speed": ["30"],
        "enable_support": ["1"], "support_type": "normal(auto)", "support_style": "snug",
        "support_on_build_plate_only": "0", "support_threshold_angle": "30",
        "support_top_z_distance": "0.12", "support_object_xy_distance": "0.30",
        "support_interface_top_layers": "3",
        "brim_type": "no_brim", "enable_prime_tower": "0",
        "curr_bed_type": "Textured PEI Plate", "ironing_type": "no ironing",
    })
    filament = flatten_profile(PROFILES, "filament", "Generic PLA @BBL A1")
    filament.update({"name": "Generic PLA - suporte F1 V9 acabamento", "from": "User",
        "filament_colour": ["#25282B"], "overhang_fan_threshold": ["25%"],
        "overhang_fan_speed": ["100"]})
    for name, data in (("machine", machine), ("process", process), ("filament", filament)):
        (WORK / f"{name}.json").write_text(json.dumps(data))

    def item(path, support):
        return {"path": str(path), "count": 1, "filaments": [1],
                "print_params": {"enable_support": "1" if support else "0"}}

    plan = {"plates": [
        {"plate_name": "01 TESTE - berco do pneu", "need_arrange": True,
         "objects": [item(WORK / "cradle-flat.stl", False)]},
        {"plate_name": "02 TESTE - pinos do piloto 4.65 4.75 4.85", "need_arrange": True,
         "objects": [item(WORK / "pilot-flat.stl", False)]},
        {"plate_name": "03 COMPLETO - imprimir apos os testes", "need_arrange": True,
         "objects": [item(WORK / "complete-flat.stl", True)]},
    ]}
    (WORK / "assembly.json").write_text(json.dumps(plan))
    common = ["--datadir", str(WORK / "user"), "--debug", "2"]
    run_cli(BAMBU, common + ["--load-settings", str(WORK / "machine.json") + ";" + str(WORK / "process.json"),
        "--load-filaments", str(WORK / "filament.json"), "--load-assemble-list", str(WORK / "assembly.json"),
        "--orient", "0", "--arrange", "1", "--outputdir", str(WORK), "--export-3mf", "native.3mf"], WORK / "export.log")

    target = ROOT / "downloads" / f"{PROJECT_PREFIX}-A1-PLA-3-pratos.3mf"
    annotate(WORK / "native.3mf", target, ["#25282B"], PROJECT_PREFIX)
    blobs, settings, plates = read_project(target)
    native = plate_meshes(blobs, settings)
    assert len(plates) == 3 and [len(p) for p in native] == [1, 1, 1]
    refs = [cradle, pilot, complete]
    for plate, ref in zip(native, refs):
        actual = plate[0][2]
        assert actual.is_watertight and abs(actual.volume - ref.volume) < 0.2
        assert actual.bounds[0, :2].min() > 0 and actual.bounds[1, :2].max() < 254

    run_cli(BAMBU, common + ["--info", "--outputdir", str(WORK / "reopen"), str(target)], WORK / "reopen.log")
    run_cli(BAMBU, common + ["--slice", "0", "--orient", "0", "--arrange", "0",
        "--outputdir", str(WORK / "slice"), "--export-3mf", "validation.3mf", str(target)], WORK / "slice.log")
    result = json.loads((WORK / "slice" / "result.json").read_text())
    assert result["return_code"] == 0 and len(result["sliced_plates"]) == 3
    report = {"project": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "printer": "Bambu Lab A1 0.4 nozzle", "bambu_version": "02.09.01.70",
        "material": "Generic PLA", "layer_height_mm": 0.12, "wall_loops": 4,
        "infill_percent": 25, "infill_pattern": "gyroid", "brim": False,
        "physical_print_tested": False, "plates": []}
    for plate in result["sliced_plates"]:
        assert not plate.get("warning_message"), plate.get("warning_message")
        report["plates"].append({"id": plate["id"], "estimated_seconds": plate["total_predication"],
            "estimated_total_grams": sum(f["total_used_g"] for f in plate["filaments"]),
            "filament_changes": plate["filament_change_times"], "warnings": plate.get("warning_message")})
    (FOLDER / "bambu-validation-acabamento.json").write_text(json.dumps(report, indent=2) + "\n")
    package(target)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
