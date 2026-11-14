#!/usr/bin/env python3
"""Validate Blender sources, four GLB variants, embedded PBR textures, previews and audio."""
import os, glob, sys, wave, struct, json

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
MODELS=os.path.join(ROOT,"assets","models")
PREVIEWS=os.path.join(MODELS,"previews")
AUDIO=os.path.join(ROOT,"assets","audio","generated")
TEXTURES=os.path.join(ROOT,"assets","textures","procedural")
blends=sorted(glob.glob(os.path.join(MODELS,"**","*_four_variants.blend"),recursive=True))
errors=[]
if len(blends)<300:
    errors.append(f"Expected at least 300 four-variant Blender source files, found {len(blends)}")
expected_textures=[f"{family}_{channel}.png" for family in ("metal","polymer","rubber","organic","glass") for channel in ("albedo","roughness","height")]
for name in expected_textures:
    path=os.path.join(TEXTURES,name)
    if not os.path.isfile(path) or os.path.getsize(path)<2048:
        errors.append(f"Missing or empty PBR texture: {path}")

def inspect_glb(path):
    with open(path,"rb") as f:
        header=f.read(12)
        if len(header)!=12: raise ValueError("truncated GLB header")
        magic,version,total=struct.unpack("<III",header)
        if magic!=0x46546C67 or version!=2 or total<20: raise ValueError("invalid GLB 2.0 header")
        chunk_len,chunk_type=struct.unpack("<II",f.read(8))
        if chunk_type!=0x4E4F534A or chunk_len>total-20: raise ValueError("missing JSON chunk")
        doc=json.loads(f.read(chunk_len).decode("utf-8").rstrip(" \x00"))
        if not doc.get("meshes"): raise ValueError("no meshes")
        if not doc.get("materials"): raise ValueError("no materials")
        if not doc.get("images") or not doc.get("textures"): raise ValueError("no embedded image textures")
        return len(doc["images"]),len(doc["materials"]),len(doc["meshes"])

checked=0
for blend in blends:
    folder=os.path.dirname(blend)
    stem=os.path.basename(blend)[:-len("_four_variants.blend")]
    exports=sorted(glob.glob(os.path.join(folder,stem+"_variant_*.glb")))
    letters={os.path.basename(p)[-5:-4].lower() for p in exports}
    if len(exports)!=4 or letters!={"a","b","c","d"}:
        errors.append(f"{blend}: expected A/B/C/D GLB exports, found {[os.path.basename(p) for p in exports]}")
    for export in exports:
        try:
            images,materials,meshes=inspect_glb(export)
            if images<1: errors.append(f"{export}: no image textures")
        except Exception as exc:
            errors.append(f"{export}: invalid/untextured GLB: {exc}")
    preview=os.path.join(PREVIEWS,stem+"_four_variants_preview.png")
    if not os.path.isfile(preview) or os.path.getsize(preview)<2048:
        errors.append(f"{blend}: missing/empty review preview {preview}")
    checked+=1

audio_names=["machine_motor_loop","drone_rotors_loop","train_wheel_rail_loop","conveyor_belt_loop","fluid_pump_loop","pipeline_flow_loop","alien_planet_wind_loop","soft_ui_confirmation","footsteps_surface_loop","item_pickup","building_placed","building_dismantled","ui_cancel","ui_error","ui_open","power_switch","resource_scanner_ping","player_jump","player_landing","waterfall_ambience_loop","cave_ambience_loop","rain_ambience_loop","alien_creature_chirp","portable_miner_loop","smelter_loop","refinery_loop","power_generator_loop","nuclear_reactor_loop"]
for name in audio_names:
    path=os.path.join(AUDIO,name+".wav")
    if not os.path.isfile(path):
        errors.append(f"Missing generated audio: {path}")
        continue
    try:
        with wave.open(path,"rb") as wav:
            if wav.getnchannels()!=2 or wav.getframerate()!=48000 or wav.getsampwidth()!=2:
                errors.append(f"{path}: expected stereo 48 kHz 16-bit PCM")
            if wav.getnframes()<wav.getframerate()//4:
                errors.append(f"{path}: audio is unexpectedly short")
    except wave.Error as exc:
        errors.append(f"{path}: invalid WAV: {exc}")
manifest=os.path.join(AUDIO,"audio_manifest.json")
if not os.path.isfile(manifest):
    errors.append(f"Missing audio manifest: {manifest}")

print(f"Verified {checked} Blender model families, {len(expected_textures)} PBR texture maps and {len(audio_names)} WAV assets.")
if errors:
    print("ASSET VALIDATION FAILED:")
    for err in errors: print(" -",err)
    sys.exit(1)
print("All families have four valid textured GLB exports and preview sheets; PBR maps and stereo WAV files are present.")
