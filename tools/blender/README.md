# Blender asset pipeline

This repository builds original, independently authored Blender blockouts for a mobile Satisfactory-inspired project. The assets are **not extracted from the original game**. Their purpose is to establish separate editable meshes and four alternatives per asset for review.

## Automated build

A push to `main` that changes `tools/blender/**`, `tools/audio/**`, or the workflow starts:

`.github/workflows/build-blender-assets.yml`

The GitHub Actions job installs Blender, runs the generators, renders four-variant review sheets, verifies output counts, and commits the resulting `.blend`, `.glb`, `.png`, and `.wav` files back to `main`.

You can also run it manually from the repository's **Actions** tab using **Build Blender asset blockouts**.

## Generator batches

- `generate_starter_assets.py` — initial constructor, conveyor and portable-miner prototypes.
- `generate_production_buildings_batch.py` — production machines and extraction buildings.
- `generate_logistics_infrastructure_batch.py` — conveyors, pipelines, power infrastructure, hypertubes, storage and AWESOME Sink.
- `generate_remaining_buildings_batch.py` — remaining building-register entries, including architecture, transport structures, research and special buildings.
- `generate_resource_nodes_batch.py` — resource nodes, resource wells, geyser and natural deposits.
- `generate_item_catalog_batch.py` — four blockout variants for each registered non-combat inventory item.
- `generate_noncombat_equipment_batch.py` — remaining non-combat tools and equipment.
- `generate_fauna_flora_batch.py` — fauna and flora blockouts.
- Individual `generate_*_variants.py` scripts — jetpack, hoverpack, Blade Runners, parachute, gas mask, object scanner, hazmat suit, cup, vehicles, train parts and other initial assets.

Each family is written to its own folder below `assets/models/`. A family normally contains one `*_four_variants.blend` source and four independently exported GLBs (`variant_a` through `variant_d`). Review renders are written to `assets/models/previews/`.

## How to interpret the models

- A–D are **design alternatives**, not four approved final models.
- Unless a register explicitly says otherwise, dimensions, pivots, snap points and collision envelopes remain provisional and must be checked against in-game references.
- The first blockouts are not finished final art: topology, UVs, original texture maps, rigging, animations, LODs, collision tuning and mobile performance still require review.
- A model is not `approved` until the user chooses a variant and requests/accepts its revisions.
- Some item families may share one visual mesh when the game uses the same shape; the item manifest should reference shared geometry rather than creating meaningless duplicates.
- Weapons, ammunition, explosives and combat implementation are intentionally excluded from this asset build.

## Scale and physics

Blender uses metric units and a 1-unit = 1-metre target. Any dimensions labelled `provisional` or `unverified_blockout` are not verified Satisfactory measurements.

Blender files contain named collision-proxy objects and metadata. They do not implement runtime physics. The game engine must load collision proxies separately or generate collider shapes. Machine production, inventories, conveyors, fluids and power must remain in the simulation layer and must not pause when render objects are culled or hidden.

## Audio

`tools/audio/generate_original_audio.py` creates original stereo WAV studies (48 kHz, 16-bit) for machine motors, drone rotors, train-wheel rhythm, conveyor movement, fluid pumps, pipeline flow, alien wind and a UI confirmation. `assets/audio/generated/audio_manifest.json` defines loop behavior, source type, gain, pitch variation, distance attenuation, occlusion and reverb guidance.

These are newly synthesized design studies, not recordings or copies of Satisfactory audio. Distance fading, moving-source positioning, stereo spatialization, occlusion and reverb must be implemented in the game audio engine; the WAV files alone do not provide runtime spatial audio.

## Asset policy

Use original meshes, materials, sounds and animations, or assets whose licenses explicitly permit the intended use. Do not extract or redistribute proprietary Satisfactory assets without permission.
