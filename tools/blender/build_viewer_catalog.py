#!/usr/bin/env python3
"""Build a static JSON catalogue for the browser-based GLB viewer."""
import os, glob, re, json
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
MODELS=os.path.join(ROOT,"assets","models")
OUT=os.path.join(ROOT,"viewer","catalog.json")
os.makedirs(os.path.dirname(OUT),exist_ok=True)
families={}\nSELECTION_PATH=os.path.join(ROOT,"assets","model-selection.json")\nselection={}\nif os.path.isfile(SELECTION_PATH):\n    with open(SELECTION_PATH,encoding="utf-8") as sf:\n        selection={a["id"]:a for a in json.load(sf).get("assets",[])}
for path in glob.glob(os.path.join(MODELS,"**","*_variant_*.glb"),recursive=True):
    name=os.path.basename(path)
    match=re.match(r"(.+)_variant_([a-d])\.glb$",name,re.I)
    if not match: continue
    asset_id=match.group(1)
    rel=os.path.relpath(path,ROOT).replace(os.sep,"/")
    category=os.path.relpath(os.path.dirname(path),MODELS).split("/")[0]
    if category == "equipment": continue
    entry=families.setdefault(asset_id,{"id":asset_id,"name":asset_id.replace("-"," ").replace("_"," ").title(),"category":category,"variants":{}})
    entry["variants"][match.group(2).lower()]=rel
    preview=os.path.join(MODELS,"previews",asset_id+"_four_variants_preview.png")
    if os.path.isfile(preview): entry["preview"]=os.path.relpath(preview,ROOT).replace(os.sep,"/")
assets=[]
for entry in sorted(families.values(),key=lambda x:(x["category"],x["name"])):
    if set(entry["variants"])==set("abcd"):\n        review=selection.get(entry["id"],{})\n        if review.get("selectionStatus")=="out-of-scope":\n            entry["selectionStatus"]="out-of-scope"\n        else:\n            entry["selectedVariant"]=review.get("selectedVariant","b") or "b"\n            entry["selectionStatus"]=review.get("selectionStatus","provisional-default-b")\n        assets.append(entry)
with open(OUT,"w",encoding="utf-8") as f: json.dump({"count":len(assets),"assets":assets},f,ensure_ascii=False,indent=2)
print("Built viewer catalogue:",len(assets),"four-variant families")
if len(assets)<294: raise SystemExit("Expected at least 294 permitted model families")
