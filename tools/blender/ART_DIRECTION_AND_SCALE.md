# Visual and scale bible

## Core art direction
Build a believable industrial outpost on a vast, lonely alien planet. Equipment should feel engineered for long-term resource extraction and harsh field conditions, not like present-day consumer machinery and not like ornate fantasy spacecraft.

Visual language:
- Heavy, practical silhouettes with clear functional parts.
- Modular armor panels, service hatches, exposed structural frames, protected cables and pipes.
- Graphite/dark metal structure, restrained amber safety panels, steel wear surfaces, dark rubber, small cyan/amber status lights.
- Weathering only where plausible: dust, abrasion at contact points, heat discoloration near exhausts.
- Futuristic details must communicate function (sensors, sealed connectors, status indicators), not be random decoration.
- Keep silhouettes readable from first-person distance and on a phone display.

## Scale convention
- Blender scene units are metric.
- 1 Blender unit = 1 metre.
- Every asset root must have its origin at a meaningful placement point and carry `target_dimensions_m` metadata.
- Every asset must be checked against a common human character scale reference, a standard build grid, and the dimensions of connected assets.
- Conveyor modules must remain compact industrial equipment. Their width, height, supports and belt surface must be dimensionally compatible with item meshes and machine ports; they must never be scaled like a vehicle or train.
- Vehicles must be checked against road width, wheelbase, clearance and player scale.
- Buildings must be checked against foundations, access routes, doors, stairs, ports and conveyor connection heights.
- Never resize individual assets arbitrarily to make a screenshot look right. Adjust the shared measurement spec and revalidate connected assets.

## Provisional starter dimensions
These are initial engineering targets from our own blockout, **not verified measurements of Satisfactory's proprietary models**. Replace them only after collecting reliable visual references and a consistent scale reference.

| Asset | Initial bounding target | Notes |
|---|---:|---|
| Constructor prototype | 2.8 x 2.35 x 3.1 m | Building-sized machine; validate access and port heights |
| Straight conveyor module | 4.15 x 1.18 x 1.05 m | Belt surface 0.88 m wide; compact logistics module |
| Portable miner prototype | 1.55 x 1.55 x 2.15 m | Validate against character and placement footprint |

## Required reference workflow
For each asset:
1. Collect multiple lawful reference views: front, side, rear, top and in-world view where available.
2. Record proportions against a shared scale anchor (character, foundation/build grid, known connection size).
3. Create a dimension sheet before detailed modeling.
4. Model silhouette first, then functional subassemblies, then bolts/panels/vents.
5. Create original materials and texture maps; do not paint over or edit proprietary source textures.
6. Add collision proxies and mark moving subassemblies separately.
7. Export GLB and inspect it in the target runtime at near, medium and far distances.
8. Validate fit with connected objects: belt-to-port, vehicle-to-road, player-to-door, machine-to-foundation.
9. Reject assets that violate scale, silhouette readability, mobile triangle/material budgets or gameplay clearance.

## Runtime physics and simulation
Blender source stores mesh, material, rig and collision-proxy authoring. The game runtime owns actual rigid-body/collision behavior. Production state, item flow and power simulation must remain independent of rendering visibility. Hiding an object must never reset its timers, inventories, belt contents or machine state.

## Completion standard
Do not label a model "finished" until its dimensions are checked, its collision proxy is tested, its materials are authored, and it is visibly inspected in the game runtime. Current generated meshes are prototypes only.
