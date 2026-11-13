# Blender asset pipeline

This directory contains procedural Blender source for original, independently designed game assets.

## Generate the starter assets

Install Blender 4.x, then run from the repository root:

```bash
blender --background --python tools/blender/generate_starter_assets.py
```

The script writes three editable `.blend` scenes and corresponding `.glb` exports under `assets/models/generated/`:

- `constructor_prototype`
- `conveyor_module_prototype`
- `portable_miner_prototype`

These are **first-pass blockout/prototype assets**, not finished replicas or production-ready final art. They use original geometry and newly authored procedural materials. Review proportions, topology, UVs, texture maps, LODs, collision shapes, and mobile performance before shipping.

## Physics boundary

Blender files contain named collision-proxy objects and metadata. They do not implement the game's runtime physics. The game engine must load collision proxies separately or generate collider shapes, while machine production and conveyor state remain in the simulation layer. Hidden meshes must never reset or pause production.

## Asset policy

Use original meshes, materials, sounds, and animations, or assets whose licenses explicitly permit the intended use. Do not extract or redistribute proprietary Satisfactory assets without permission.
