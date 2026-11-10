#!/usr/bin/env python3
"""Verificação estrutural dos projetos Bambu V5 com texto em geometria."""
from __future__ import annotations
import json, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EXPECTED={"curto":"Lia","medio":"Tomás","comprido":"Alexandre"}

def verify(path: Path, profile: str, name: str) -> None:
    with zipfile.ZipFile(path) as z:
        required={"3D/3dmodel.model","3D/Objects/object_1.model",
                  "Metadata/model_settings.config","Metadata/project_settings.config"}
        assert required <= set(z.namelist()), f"arquivos internos em falta: {path}"
        model=ET.fromstring(z.read("Metadata/model_settings.config"))
        settings=json.loads(z.read("Metadata/project_settings.config"))
    objects=model.findall("object"); parts=model.findall(".//part")
    assert len(objects)==1 and len(parts)==3, f"montagem incorreta: {path}"
    assert len(model.findall(".//model_instance"))==1
    labels=[]; extruders=[]
    for part in parts:
        labels.append(part.find("metadata[@key='name']").get("value"))
        extruders.append(part.find("metadata[@key='extruder']").get("value"))
    assert labels==["Corpo vermelho","Detalhes brancos",f"Nome {name} ({profile}, geometria)"]
    assert extruders==["1","2","1"]
    texts=model.findall(".//text_info")
    assert len(texts)==0
    assert settings["printer_model"]=="Bambu Lab A1"
    assert settings["nozzle_diameter"]==["0.4"]
    assert settings["filament_colour"]==["#B21632","#F2E6CF"]
    assert settings["brim_type"]=="no_brim" and settings["enable_support"]=="0"
    print(f"OK {path.name}: 1 objeto, 3 volumes alinhados, nome geométrico '{name}', 2 cores")

def main() -> None:
    folder=Path(sys.argv[1] if len(sys.argv)>1 else "downloads")
    for profile,name in EXPECTED.items():
        slug=name.lower().replace("á","a")
        verify(folder/f"gorro-natal-v5-{profile}-{slug}-2-cores.3mf",profile,name)
if __name__=="__main__": main()
