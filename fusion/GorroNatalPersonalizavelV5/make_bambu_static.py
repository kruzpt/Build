#!/usr/bin/env python3
"""Converte V5 em projeto Bambu estável; o nome permanece geometria."""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,tempfile,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EXAMPLES={"curto":"Lia","medio":"Tomás","comprido":"Alexandre"}
ROOT=Path(__file__).resolve().parents[2]
PROFILE_TEMPLATE=ROOT/"downloads/universo-saber-suporte-v6-A1-AMS-2-pratos.3mf"

def configure(path:Path,name:str,profile:str)->None:
 with zipfile.ZipFile(path) as src: files={n:src.read(n) for n in src.namelist()}
 root=ET.fromstring(files["Metadata/model_settings.config"])
 labels=["Corpo vermelho","Detalhes brancos",f"Nome {name} ({profile}, geometria)"]
 for i,part in enumerate(root.findall(".//part")):
  label=part.find("metadata[@key='name']")
  if label is not None: label.set("value",labels[i])
  ET.SubElement(part,"metadata",key="extruder",value=["1","2","1"][i])
 files["Metadata/model_settings.config"]=ET.tostring(root,encoding="utf-8",xml_declaration=True)
 with zipfile.ZipFile(PROFILE_TEMPLATE) as donor: settings=json.loads(donor.read("Metadata/project_settings.config"))
 settings["filament_colour"]=["#B21632","#F2E6CF"]
 settings["brim_type"]="no_brim";settings["brim_width"]="0";settings["enable_support"]="0"
 files["Metadata/project_settings.config"]=(json.dumps(settings,ensure_ascii=False,indent=4)+"\n").encode()
 tmp=path.with_suffix(".tmp")
 with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED) as dst:
  for n,b in files.items():dst.writestr(n,b)
 os.replace(tmp,path)

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--bambu",required=True,type=Path);ap.add_argument("--downloads",type=Path,default=Path("downloads"));a=ap.parse_args()
 env=os.environ.copy();env.setdefault("LC_ALL","C")
 for profile,name in EXAMPLES.items():
  slug=name.lower().replace("á","a");source=a.downloads/f"gorro-natal-v5-{profile}-{slug}-2-cores.3mf"
  with tempfile.TemporaryDirectory() as td:
   native=Path(td)/source.name
   subprocess.run([str(a.bambu),"--export-3mf",str(native),str(source)],check=True,env=env)
   configure(native,name,profile);shutil.move(native,source)
  print(source)
if __name__=="__main__":main()
