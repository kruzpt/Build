#!/usr/bin/env python3
"""Converte os 3MF V3 e marca o volume do nome como Text shape Lobster."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, tempfile, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EXAMPLES={"curto":"Lia","medio":"Tomás","comprido":"Alexandre"}
ROOT=Path(__file__).resolve().parents[2]
PROFILE_TEMPLATE=ROOT/"downloads/universo-saber-suporte-v6-A1-AMS-2-pratos.3mf"

def rewrite_text_info(path: Path, name: str, profile: str) -> None:
    with zipfile.ZipFile(path) as src:
        files={n:src.read(n) for n in src.namelist()}
    root=ET.fromstring(files["Metadata/model_settings.config"])
    target=None
    labels=["Corpo vermelho", "Detalhes brancos", f"Nome {name} ({profile})"]
    extruders=["1", "2", "1"]
    for index, part in enumerate(root.findall(".//part")):
        label=part.find("metadata[@key='name']")
        if label is not None: label.set("value", labels[index])
        ET.SubElement(part, "metadata", key="extruder", value=extruders[index])
        source_volume=part.find("metadata[@key='source_volume_id']")
        if source_volume is not None and source_volume.get("value")=="2":
            target=part
    if target is None: raise RuntimeError("volume do nome nao encontrado")
    size={"curto":"15.5","medio":"14.5","comprido":"10.8"}[profile]
    info=ET.Element("text_info", {
        "text":name, "font_name":"Lobster", "font_version":"2.3",
        "style_name":"Lobster V3", "boldness":"0", "skew":"0",
        "font_index":"0", "font_size":size, "thickness":"0.8",
        "embeded_depth":"0", "rotate_angle":"0", "text_gap":"0",
        "horizontal_align":"center", "vertical_align":"middle",
        "bold":"0", "italic":"1", "surface_type":"0", "hit_mesh":"0",
        "hit_position":"0 0 3.8", "hit_normal":"0 0 1"})
    target.insert(max(0, len(target)-1), info)
    files["Metadata/model_settings.config"]=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    with zipfile.ZipFile(PROFILE_TEMPLATE) as donor:
        settings=json.loads(donor.read("Metadata/project_settings.config"))
    settings["filament_colour"]=["#B21632", "#F2E6CF"]
    settings["brim_type"]="no_brim"; settings["brim_width"]="0"
    settings["enable_support"]="0"
    files["Metadata/project_settings.config"]=(json.dumps(settings,ensure_ascii=False,indent=4)+"\n").encode()
    tmp=path.with_suffix(".tmp")
    with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED) as dst:
        for n,b in files.items(): dst.writestr(n,b)
    os.replace(tmp,path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--bambu",required=True,type=Path); ap.add_argument("--downloads",type=Path,default=Path("downloads")); a=ap.parse_args()
    env=os.environ.copy(); env.setdefault("LC_ALL","C")
    for profile,name in EXAMPLES.items():
        slug=name.lower().replace("á","a")
        source=a.downloads/f"gorro-natal-v3-{profile}-{slug}-2-cores.3mf"
        with tempfile.TemporaryDirectory() as td:
            native=Path(td)/source.name
            subprocess.run([str(a.bambu),"--export-3mf",str(native),str(source)],check=True,env=env)
            rewrite_text_info(native,name,profile)
            shutil.move(native,source)
        with zipfile.ZipFile(source) as z:
            cfg=z.read("Metadata/model_settings.config")
            if b"text_info" not in cfg: raise RuntimeError(f"Text shape ausente: {source}")
        print(source)
if __name__=="__main__": main()
