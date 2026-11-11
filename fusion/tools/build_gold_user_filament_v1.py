"""Create and validate the reusable Amazon Basics Silk PLA Gold preset."""
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile

from build_pintos_pla_3mf import flatten_profile, read_project, run_cli

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "downloads/essencial-compacto-v6-base-acabamento-A1-AMS-2-pratos.3mf"
TARGET = ROOT / "downloads/amazon-basics-silk-pla-gold-09702-A1-04.json"
REPORT = ROOT / "fusion/FilamentLibraryA1/gold-validation.json"
NAME = "Amazon Basics Silk PLA Gold 0.9702 @BBL A1 0.4"
PARENT = "Generic PLA Silk @BBL A1"
SLOT = 2
META = {
    "name", "type", "from", "setting_id", "inherits", "instantiation",
    "filament_id", "version", "filament_settings_id", "compatible_printers",
    "compatible_printers_condition", "compatible_prints", "compatible_prints_condition",
}


def main():
    profiles = Path("/tmp/bambu-studio-2.9.1/squashfs-root/resources/profiles/BBL")
    binary = Path("/tmp/bambu-studio-2.9.1/squashfs-root/bin/bambu-studio")
    work = Path("/tmp/gold-user-filament-v1")
    (work / "user").mkdir(parents=True, exist_ok=True)
    os.environ["LD_LIBRARY_PATH"] = "/tmp/bambu-libs/usr/lib/x86_64-linux-gnu:" + str(binary.parent)

    parent = flatten_profile(profiles, "filament", PARENT)
    with ZipFile(SOURCE) as archive:
        project = json.loads(archive.read("Metadata/project_settings.config"))

    preset = {}
    for key, value in parent.items():
        if key in META:
            continue
        saved = project.get(key)
        if isinstance(saved, list) and len(saved) == 4:
            value = [saved[SLOT]]
        elif isinstance(saved, list) and len(saved) == 1:
            value = saved
        elif saved is not None and isinstance(value, list) and not isinstance(saved, list):
            value = [str(saved)]
        preset[key] = value

    preset.update({
        "type": "filament", "name": NAME, "from": "User", "inherits": PARENT,
        "version": "2.9.1.70", "instantiation": "true",
        "filament_settings_id": [NAME],
        "compatible_printers": ["Bambu Lab A1 0.4 nozzle"],
        "compatible_printers_condition": "", "compatible_prints": [],
        "compatible_prints_condition": "", "default_filament_colour": ["#DDB34E"],
        "filament_vendor": ["Amazon Basics"],
    })

    expected = {
        "filament_flow_ratio": ["0.9702"], "nozzle_temperature": ["215"],
        "nozzle_temperature_initial_layer": ["215"], "filament_retraction_length": ["0.5"],
        "filament_max_volumetric_speed": ["5"], "textured_plate_temp": ["55"],
    }
    for key, value in expected.items():
        assert preset[key] == value, (key, preset[key])
    TARGET.write_text(json.dumps(preset, ensure_ascii=False, indent=2) + "\n")

    run_cli(binary, ["--datadir", str(work / "user"), "--debug", "3", "--load-filaments", str(TARGET),
                     "--orient", "0", "--arrange", "0", "--outputdir", str(work),
                     "--export-3mf", "loaded.3mf", str(SOURCE)], work / "load.log")
    loaded, _, _ = read_project(work / "loaded.3mf")
    effective = json.loads(loaded["Metadata/project_settings.config"])
    for key, value in expected.items():
        assert effective[key][0] == value[0], (key, effective[key])

    report = {
        "profile_name": NAME,
        "profile_file": TARGET.name,
        "profile_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "preset_kind": "Bambu Studio user filament JSON",
        "parent": PARENT,
        "compatible_printers": preset["compatible_printers"],
        "material": "Amazon Basics Silk PLA Gold 1.75 mm",
        "source_project": SOURCE.name,
        "source_material_slot": 3,
        "flow_ratio": 0.9702,
        "nozzle_temperature_c": 215,
        "textured_pei_temperature_c": 55,
        "retraction_mm": 0.5,
        "maximum_volumetric_speed_mm3_s": 5,
        "native_profile_load_exit": 0,
        "windows_library_install_performed": False,
        "dynamic_flow_K_not_stored_in_filament_preset": True,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
