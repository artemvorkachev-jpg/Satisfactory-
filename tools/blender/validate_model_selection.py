#!/usr/bin/env python3
"""Validate every four-variant model path and its selected default."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CATALOG = os.path.join(ROOT, "viewer", "catalog.json")
MANIFEST = os.path.join(ROOT, "assets", "model-selection.json")

with open(CATALOG, encoding="utf-8") as f:
    catalog = json.load(f)
with open(MANIFEST, encoding="utf-8") as f:
    manifest = json.load(f)

selection = {a["id"]: a for a in manifest.get("assets", [])}
errors = []
checked = 0
reviewed = 0

for asset in catalog.get("assets", []):
    aid = asset["id"]
    record = selection.get(aid)
    if not record:
        errors.append(f"{aid}: missing from model-selection.json")
        continue
    if set(asset.get("variants", {})) != set("abcd"):
        errors.append(f"{aid}: expected A/B/C/D variants")
        continue
    for letter, rel in asset["variants"].items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"{aid}: missing variant {letter}: {rel}")
    preview = asset.get("preview")
    if not preview or not os.path.isfile(os.path.join(ROOT, preview)):
        errors.append(f"{aid}: missing four-variant preview")
    if record.get("selectionStatus") not in ("out-of-scope", "pending-noncombat-review", "pending-visual-review"):
        selected = record.get("selectedVariant")
        if selected not in asset["variants"]:
            errors.append(f"{aid}: invalid selected variant {selected!r}")
        if record.get("selectionStatus") == "preview-reviewed-initial":
            reviewed += 1
    checked += 1

if len(selection) != len(manifest.get("assets", [])):
    errors.append("duplicate asset IDs in selection manifest")
if checked < 294:
    errors.append(f"expected at least 294 model families, found {checked}")

print(f"Validated {checked} model families; {reviewed} have initial preview review.")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("All four GLB variants, preview sheets and selected defaults resolve.")
