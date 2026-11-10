#!/usr/bin/env python3
"""Marca o nome V6 como Text Shape nativa, editável e resolvida por face name."""
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
 labels=["Corpo vermelho","Detalhes brancos",f"Nome editável — {name} ({profile})"]
 target=None
 for i,part in enumerate(root.findall(".//part")):
  label=part.find("metadata[@key='name']")
  if label is not None: label.set("value",labels[i])
  ET.SubElement(part,"metadata",key="extruder",value=["1","2","1"][i])
  source_volume=part.find("metadata[@key='source_volume_id']")
  if source_volume is not None and source_volume.get("value")=="2": target=part
 if target is None: raise RuntimeError("volume do nome não encontrado")
 size={"curto":"15.5","medio":"14.5","comprido":"10.8"}[profile]
 target.insert(max(0,len(target)-1),ET.Element("text_info",{
  "text":name,"font_name":"Lobster","font_version":"2.8",
  "style_name":"Lobster","boldness":"0","skew":"0","font_index":"-1",
  "font_size":size,"thickness":"0.8","embeded_depth":"0",
  "rotate_angle":"0","text_gap":"0","horizontal_align":"center",
  "vertical_align":"middle","bold":"0","italic":"0","surface_type":"0",
  "hit_mesh":"-1","hit_position":"0 0 0","hit_normal":"0 0 1"}))
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
 font_home=Path("/tmp/gorro-v6-bambu-font-data");(font_home/"fonts").mkdir(parents=True,exist_ok=True)
 shutil.copy2(Path(__file__).parent/"fonts/Lobster-Regular.ttf",font_home/"fonts/Lobster-Regular.ttf")
 env["XDG_DATA_HOME"]=str(font_home);env.setdefault("XDG_CACHE_HOME","/tmp/gorro-v6-bambu-font-cache")
 for profile,name in EXAMPLES.items():
  slug=name.lower().replace("á","a");source=a.downloads/f"gorro-natal-v6-{profile}-{slug}-2-cores.3mf"
  with tempfile.TemporaryDirectory() as td:
   native=Path(td)/source.name
   subprocess.run([str(a.bambu),"--export-3mf",str(native),str(source)],check=True,env=env)
   configure(native,name,profile)
   reopened=Path(td)/f"reopened-{source.name}"
   subprocess.run([str(a.bambu),"--export-3mf",str(reopened),str(native)],check=True,env=env)
   shutil.move(reopened,source)
  with zipfile.ZipFile(source) as z:
   cfg=z.read("Metadata/model_settings.config")
   if b'font_index="-1"' not in cfg or b'font_name="Lobster"' not in cfg:
    raise RuntimeError(f"Text Shape inválida: {source}")
  print(source)
if __name__=="__main__":main()
