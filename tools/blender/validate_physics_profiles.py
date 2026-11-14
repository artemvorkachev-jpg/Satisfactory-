#!/usr/bin/env python3
"""Validate one physics profile for every model family in the selection manifest."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SELECTION = ROOT / "assets/model-selection.json"
PHYSICS = ROOT / "assets/physics-profiles.json"

def main():
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    physics = json.loads(PHYSICS.read_text(encoding="utf-8"))
    source = {a["id"]: a for a in selection["assets"]}
    profiles = {a["id"]: a for a in physics["assets"]}
    errors = []
    if len(source) != len(selection["assets"]):
        errors.append("duplicate IDs in model-selection.json")
    if len(profiles) != len(physics["assets"]):
        errors.append("duplicate IDs in physics-profiles.json")
    if set(source) != set(profiles):
        errors.append(f"asset coverage mismatch: missing={sorted(set(source)-set(profiles))}; extra={sorted(set(profiles)-set(source))}")
    for asset_id, asset in source.items():
        p = profiles.get(asset_id)
        if not p:
            continue
        if p.get("category") != asset.get("category"):
            errors.append(f"{asset_id}: category mismatch")
        for key in ("profile", "body", "shape", "interaction", "implementationStatus", "validationStatus"):
            if not p.get(key):
                errors.append(f"{asset_id}: missing {key}")
        if p.get("implementationStatus") not in ("planned", "prototype", "implemented"):
            errors.append(f"{asset_id}: invalid implementationStatus")
    print(f"Checked {len(source)} model families and {len(profiles)} physics profiles.")
    print(f"Implemented: {sum(p.get('implementationStatus') == 'implemented' for p in profiles.values())}; planned: {sum(p.get('implementationStatus') == 'planned' for p in profiles.values())}.")
    if errors:
        print("\\n".join(errors))
        return 1
    print("Physics profile coverage is complete; this validates metadata only, not in-game collision behavior.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
