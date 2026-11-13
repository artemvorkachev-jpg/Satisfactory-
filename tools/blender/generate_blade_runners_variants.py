import bpy
import math
import os

# Original Satisfactory-inspired Blade Runners mobility exoskeleton study.
# The reference defines these as leg-slot equipment that increases running/jump
# capability and dampens landing. Geometry is independently designed.
# Dimensions are provisional; confirm using a Pioneer scale reference.
# Run: blender --background --python tools/blender/generate_blade_runners_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "blade_runners")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.4, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value = (*color, 1)
        bs.inputs["Emission Strength"].default_value = emission
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .48, .32)
DARK = mat("Graphite structural alloy", (.045, .06, .07), .82, .28)
STEEL = mat("Brushed service metal", (.34, .39, .41), .86, .25)
RUBBER = mat("Foot grip elastomer", (.018, .022, .025), .02, .78)
YELLOW = mat("Safety yellow", (1, .61, .025), .18, .34)
CYAN = mat("Status cyan", (.02, .42, .52), .25, .22, 1.5)

def finish(o, name, material, bevel=.02):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Manufactured edge radii", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.02, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, bevel)
    if parent:
        o.parent = parent
    return o

def cyl(name, loc, radius, depth, material, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, min(.02, radius*.1))
    if parent:
        o.parent = parent
    return o

def torus(name, loc, major, minor, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=8,
                                     location=loc)
    o = finish(bpy.context.object, name, material, 0)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def make_boot(root, x, style):
    # Local boot length axis is Y; toe faces negative Y.
    box("Boot sole", (x, -.10, -.40), (.22, .48, .075), RUBBER, .025, root)
    box("Toe armor", (x, -.27, -.31), (.22, .19, .12), AMBER, .035, root)
    box("Heel block", (x, .08, -.32), (.20, .16, .13), DARK, .025, root)
    box("Ankle cuff", (x, .06, -.05), (.20, .18, .15), STEEL, .025, root)
    for y in (-.28, -.08, .12):
        box("Sole traction pad", (x, y, -.445), (.15, .08, .018), YELLOW, .006, root)
    if style == "spring":
        for side in (-1, 1):
            cyl("Impact damper", (x + side*.12, .02, -.20), .035, .32,
                STEEL, (0, 0, 0), root)
            torus("Damper collar", (x + side*.12, .02, -.20), .045, .012, YELLOW, root)
    elif style == "rail":
        box("External shin rail", (x, .12, .03), (.07, .10, .54), DARK, .018, root)
        for z in (-.12, .04, .20):
            box("Rail clamp", (x, .04, z), (.24, .09, .045), STEEL, .012, root)
    elif style == "shell":
        box("Shin shell", (x, .09, .08), (.27, .16, .42), AMBER, .045, root)
        box("Shin inset", (x, -.005, .08), (.13, .02, .22), DARK, .012, root)
    elif style == "modular":
        box("Outer shin module", (x + .12, .06, .05), (.09, .14, .40), AMBER, .02, root)
        cyl("Pivot joint", (x + .13, .02, -.18), .07, .06, STEEL,
            (math.pi/2, 0, 0), root)
        box("Status tab", (x + .12, -.02, .18), (.05, .02, .07), CYAN, .006, root)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -.03))
    c = bpy.context.object
    c.name = "COLLIDER_BladeRunners_Pair"
    c.dimensions = (.72, .76, .92)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "equipment_collision_proxy"
    c.parent = root

def export_root(root, name):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in root.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, name + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)

def build_a():
    r = root_empty("BladeRunners_Variant_A_Dual_Damper")
    for x in (-.18, .18):
        make_boot(r, x, "spring")
        box("Outer support strut", (x + (.12 if x > 0 else -.12), .08, .06),
            (.06, .12, .50), AMBER, .018, r)
    r["design_note"] = "Compact pair with exposed landing dampers and reinforced soles."
    return r

def build_b():
    r = root_empty("BladeRunners_Variant_B_Armored_Shin")
    for x in (-.18, .18):
        make_boot(r, x, "shell")
        box("Rear support rail", (x, .19, -.01), (.07, .08, .48), STEEL, .018, r)
    box("Pair sync bridge", (0, .25, .28), (.54, .08, .06), DARK, .018, r)
    r["design_note"] = "Armored shin shells with compact rear support rails."
    return r

def build_c():
    r = root_empty("BladeRunners_Variant_C_Exposed_Frame")
    for x in (-.18, .18):
        make_boot(r, x, "rail")
        for side in (-1, 1):
            box("Exoskeleton side strut", (x + side*.11, .09, .02),
                (.045, .07, .50), AMBER if side > 0 else STEEL, .012, r)
        cyl("Ankle pivot", (x, -.02, -.12), .09, .08, DARK,
            (math.pi/2, 0, 0), r)
    r["design_note"] = "Open mechanical exoskeleton with visible rails and ankle pivots."
    return r

def build_d():
    r = root_empty("BladeRunners_Variant_D_Modular")
    for x in (-.18, .18):
        make_boot(r, x, "modular")
        box("Replaceable heel damper", (x, .16, -.28), (.13, .12, .16), STEEL, .025, r)
        torus("Heel damper ring", (x, .16, -.28), .055, .015, YELLOW, r)
        box("Outer ankle guard", (x + (.14 if x > 0 else -.14), .04, -.03),
            (.06, .18, .28), DARK, .018, r)
    r["design_note"] = "Modular ankle units with replaceable heel damping cartridges."
    return r

builders = [build_a, build_b, build_c, build_d]
roots = []
for i, builder in enumerate(builders):
    r = builder()
    add_collider(r)
    r["asset_id"] = "equipment-blade-runners"
    r["variant"] = chr(ord("A") + i)
    r["gameplay_reference"] = "Leg-slot exoskeleton for increased running speed and jump height with landing impact damping."
    r["target_dimensions_m"] = "0.72 x 0.76 x 0.92 pair blockout; provisional, verify against Pioneer scale."
    export_root(r, "blade_runners_variant_" + chr(ord("a") + i))
    roots.append(r)

for i, r in enumerate(roots):
    r.location.x = (i - 1.5) * 1.15

bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "blade_runners_four_variants.blend"))
print("Created four original Blade Runners blockout variants:", OUT_DIR)
