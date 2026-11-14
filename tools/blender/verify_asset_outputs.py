#!/usr/bin/env python3
"""Fail the build if any four-variant family lacks source, exports or review image."""
import os, glob, sys, wave

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
MODELS=os.path.join(ROOT,"assets","models")
PREVIEWS=os.path.join(MODELS,"previews")
AUDIO=os.path.join(ROOT,"assets","audio","generated")
blends=sorted(glob.glob(os.path.join(MODELS,"**","*_four_variants.blend"),recursive=True))
errors=[]
if len(blends)<300:
    errors.append(f"Expected at least 300 four-variant Blender source files, found {len(blends)}")
checked=0
for blend in blends:
    folder=os.path.dirname(blend)
    stem=os.path.basename(blend)[:-len("_four_variants.blend")]
    exports=sorted(glob.glob(os.path.join(folder,stem+"_variant_*.glb")))
    letters={os.path.basename(p)[-5:-4].lower() for p in exports}
    if len(exports)!=4 or letters!={"a","b","c","d"}:
        errors.append(f"{blend}: expected A/B/C/D GLB exports, found {[os.path.basename(p) for p in exports]}")
    preview=os.path.join(PREVIEWS,stem+"_four_variants_preview.png")
    if not os.path.isfile(preview) or os.path.getsize(preview)<2048:
        errors.append(f"{blend}: missing/empty review preview {preview}")
    checked+=1
# Check the original stereo audio deliverables and their format.
audio_names=[
 "machine_motor_loop","drone_rotors_loop","train_wheel_rail_loop",
 "conveyor_belt_loop","fluid_pump_loop","pipeline_flow_loop",
 "alien_planet_wind_loop","soft_ui_confirmation"
]
for name in audio_names:
    path=os.path.join(AUDIO,name+".wav")
    if not os.path.isfile(path):
        errors.append(f"Missing generated audio: {path}")
        continue
    try:
        with wave.open(path,"rb") as wav:
            if wav.getnchannels()!=2 or wav.getframerate()!=48000 or wav.getsampwidth()!=2:
                errors.append(f"{path}: expected stereo 48 kHz 16-bit PCM, got {wav.getnchannels()}ch {wav.getframerate()}Hz {wav.getsampwidth()*8}-bit")
    except wave.Error as exc:
        errors.append(f"{path}: invalid WAV: {exc}")
manifest=os.path.join(AUDIO,"audio_manifest.json")
if not os.path.isfile(manifest):
    errors.append(f"Missing audio manifest: {manifest}")
print(f"Verified {checked} Blender variant families.")
if errors:
    print("ASSET VALIDATION FAILED:")
    for err in errors: print(" -",err)
    sys.exit(1)
print("All variant families have four GLB exports and a preview; stereo WAV deliverables are present.")
