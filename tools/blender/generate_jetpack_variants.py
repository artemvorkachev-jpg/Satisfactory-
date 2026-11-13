import bpy
import math
import os
from mathutils import Vector

# Original, independently designed Satisfactory-inspired Jetpack study.
# The Wiki documents the Jetpack as back-slot flight equipment with automatic
# fuel consumption/refill. No official mesh dimensions are published here;
# all dimensions are provisional blockout targets, not claimed game measurements.
# Run: blender --background --python tools/blender/generate_jetpack_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "jetpack")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

# Clear scene for deterministic output.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=0.42, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if emission:
        if "Emission Color" in bs.inputs:
            bs.inputs["Emission Color"].default_value = (*color, 1.0)
            bs.inputs["Emission Strength"].default_value = emission
    return m

AMBER = mat("FICSIT-inspired amber enamel", (0.82, 0.29, 0.055), 0.48, 0.32)
GRAPHITE = mat("Graphite structural alloy", (0.045, 0.06, 0.07), 0.82, 0.28)
STEEL = mat("Brushed service metal", (0.34, 0.39, 0.41), 0.86, 0.25)
RUBBER = mat("Harness elastomer", (0.018, 0.022, 0.025), 0.02, 0.78)
GLASS = mat("Fuel inspection glass", (0.035, 0.19, 0.21), 0.45, 0.18)
SAFETY = mat("Safety yellow", (1.0, 0.61, 0.025), 0.18, 0.34)
LIGHT = mat("Status cyan", (0.02, 0.42, 0.52), 0.25, 0.22, 1.8)

def finish(obj, name, material, bevel=0.025):
    obj.name = name
    if material:
        obj.data.materials.append(material)
    if bevel and obj.type == "MESH":
        mod = obj.modifiers.new("Manufactured edge radii", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

def box(name, loc, dims, material, bevel=0.025, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, bevel)
    if parent:
        o.parent = parent
    return o

def cyl(name, loc, radius, depth, material, rot=(0, 0, 0), parent=None, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, min(0.025, radius * 0.12))
    if parent:
        o.parent = parent
    return o

def torus(name, loc, major, minor, material, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=8,
                                     location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, 0)
    if parent:
        o.parent = parent
    return o

def empty(name):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    return root

def add_harness(root):
    # Rear-facing backpack plate; straps wrap around the wearer's torso.
    box("Backplate", (0, 0.12, 0), (0.54, 0.16, 0.78), GRAPHITE, .045, root)
    box("Upper harness bridge", (0, 0.24, 0.30), (0.66, 0.10, 0.13), STEEL, .025, root)
    for x in (-0.30, 0.30):
        strap = box("Shoulder strap", (x, -0.005, 0.12), (0.12, 0.11, 0.64), RUBBER, .04, root)
        strap.rotation_euler[1] = -x * 0.85
        box("Lower harness clasp", (x * .72, -0.02, -0.27), (.14, .12, .10), STEEL, .02, root)
    box("Waist stabilizer", (0, 0.19, -0.34), (.66, .12, .12), GRAPHITE, .025, root)

def add_status(root, x=0.0, z=0.30):
    box("Status panel bezel", (x, -0.105, z), (.20, .035, .14), GRAPHITE, .018, root)
    box("Status display", (x, -0.127, z), (.13, .012, .075), GLASS, .008, root)
    for dx in (-.055, 0, .055):
        cyl("Status indicator", (x + dx, -0.14, z - .09), .018, .012,
            LIGHT if dx == 0 else SAFETY, (math.pi / 2, 0, 0), root, 16)

def add_twin_thrusters(root, radius=.16, height=.60, spread=.27, angle=0.0):
    for side in (-1, 1):
        x = side * spread
        z = 0.02
        body = cyl("Thruster pod", (x, 0.10, z), radius, height, AMBER,
                   (0, angle * side, 0), root, 40)
        cyl("Upper turbine cap", (x, 0.10, z + height * .52), radius * 1.04,
            .075, GRAPHITE, (0, 0, 0), root)
        cyl("Lower exhaust collar", (x, 0.10, z - height * .52), radius * .82,
            .09, STEEL, (0, 0, 0), root)
        torus("Nozzle rim", (x, 0.10, z - height * .57), radius * .62,
              .025, SAFETY, (0, 0, 0), root)
        cyl("Nozzle dark throat", (x, 0.10, z - height * .58), radius * .53,
            .025, GRAPHITE, (0, 0, 0), root)
        box("Pod service stripe", (x, -radius * .96, z), (.045, .018, height * .54),
            SAFETY, .008, root)

def add_fuel_cell(root, width=.22, height=.48, depth=.22, z=0.0):
    box("Fuel cell shell", (0, -0.01, z), (width, depth, height), STEEL, .04, root)
    box("Fuel level window", (0, -depth * .56, z), (width * .52, .018, height * .56),
        GLASS, .012, root)
    for zz in (z - height * .30, z, z + height * .30):
        box("Fuel level marker", (0, -depth * .58, zz), (width * .60, .012, .018),
            SAFETY, .004, root)
    cyl("Fuel coupling", (0, depth * .54, z + height * .40), .045, .10,
        GRAPHITE, (math.pi / 2, 0, 0), root)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.06, 0))
    c = bpy.context.object
    c.name = "COLLIDER_Jetpack"
    c.dimensions = (.82, .48, 1.02)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "equipment_collision_proxy"
    c.parent = root

def export_root(root, filename):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, filename + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)

def build_variant_a():
    root = empty("Jetpack_Variant_A_Compact_Twin_Pods")
    add_harness(root)
    add_twin_thrusters(root, radius=.145, height=.62, spread=.245, angle=.05)
    add_fuel_cell(root, .19, .40, .20, -.03)
    box("Upper protective bridge", (0, .10, .40), (.62, .24, .12), AMBER, .04, root)
    add_status(root)
    root["design_note"] = "Compact twin thrusters with central visible fuel cell; closest-to-function blockout."
    root["target_dimensions_m"] = "0.82 x 0.48 x 1.02 provisional; verify against in-game reference."
    return root

def build_variant_b():
    root = empty("Jetpack_Variant_B_Armored_Dorsal_Frame")
    add_harness(root)
    box("Armored dorsal shell", (0, .12, .02), (.72, .26, .78), AMBER, .075, root)
    for x in (-.25, .25):
        cyl("Recessed turbine housing", (x, .04, -.01), .145, .72, GRAPHITE,
            (0, 0, 0), root, 40)
        torus("Turbine protective ring", (x, .04, -.39), .12, .026, STEEL, parent=root)
        cyl("Nozzle insert", (x, .04, -.405), .095, .035, GRAPHITE, parent=root)
    add_fuel_cell(root, .22, .36, .17, .05)
    box("Top service handle", (0, .15, .48), (.36, .12, .08), SAFETY, .025, root)
    add_status(root, 0, .30)
    root["design_note"] = "Armored single-shell back unit with recessed twin turbines."
    root["target_dimensions_m"] = "0.82 x 0.48 x 1.02 provisional; verify against in-game reference."
    return root

def build_variant_c():
    root = empty("Jetpack_Variant_C_Industrial_Exposed_Frame")
    add_harness(root)
    for x in (-.28, .28):
        box("Vertical load rail", (x, .13, 0), (.10, .18, .86), STEEL, .025, root)
        cyl("Exposed turbine", (x, .02, -.04), .13, .70, AMBER, parent=root, vertices=40)
        cyl("Turbine intake grille", (x, -.07, .32), .12, .035, GRAPHITE,
            (math.pi / 2, 0, 0), root)
        torus("Exhaust safety ring", (x, .02, -.41), .105, .025, SAFETY, parent=root)
    add_fuel_cell(root, .25, .50, .20, .0)
    box("Cross-brace upper", (0, .16, .34), (.68, .15, .10), GRAPHITE, .02, root)
    box("Cross-brace lower", (0, .16, -.30), (.68, .15, .10), GRAPHITE, .02, root)
    add_status(root, 0, .23)
    root["design_note"] = "Open service frame with visible twin propulsion modules and replaceable central cell."
    root["target_dimensions_m"] = "0.82 x 0.48 x 1.02 provisional; verify against in-game reference."
    return root

def build_variant_d():
    root = empty("Jetpack_Variant_D_Modular_Service_Pods")
    add_harness(root)
    box("Central spine", (0, .15, .02), (.24, .20, .86), GRAPHITE, .035, root)
    for x in (-.31, .31):
        box("Removable side pod", (x, .09, .02), (.22, .26, .72), AMBER, .055, root)
        cyl("Lower thrust nozzle", (x, .09, -.39), .105, .12, STEEL, parent=root)
        cyl("Nozzle throat", (x, .09, -.46), .075, .025, GRAPHITE, parent=root)
        box("Pod latch", (x * .72, -.055, .15), (.07, .045, .14), SAFETY, .012, root)
    add_fuel_cell(root, .20, .54, .20, .02)
    box("Top docking rail", (0, .20, .48), (.52, .13, .08), STEEL, .02, root)
    add_status(root, 0, .31)
    root["design_note"] = "Modular side thruster pods and a central fuel/service spine."
    root["target_dimensions_m"] = "0.82 x 0.48 x 1.02 provisional; verify against in-game reference."
    return root

builders = [build_variant_a, build_variant_b, build_variant_c, build_variant_d]
roots = []
for index, builder in enumerate(builders):
    root = builder()
    add_collider(root)
    root["asset_id"] = "equipment-jetpack"
    root["variant"] = chr(ord("A") + index)
    root["gameplay_reference"] = "Back-slot flight equipment; fuel is selected from inventory and replenished while grounded."
    # Export each approved-local-coordinate candidate at the origin.
    export_root(root, "jetpack_variant_" + chr(ord("A") + index).lower())
    roots.append(root)

# Arrange the four candidates side-by-side only in the editable .blend review scene.
for index, root in enumerate(roots):
    root.location.x = (index - 1.5) * 1.35

bpy.ops.object.select_all(action="DESELECT")
for root in roots:
    root.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "jetpack_four_variants.blend"))

print("Created four original Jetpack blockout variants.")
print("GLB exports and review .blend are in:", OUT_DIR)
print("All dimensions are provisional and require in-game visual/scale review.")
