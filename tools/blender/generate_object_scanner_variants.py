import bpy
import math
import os

# Original Satisfactory-inspired Object Scanner concept variants.
# Hand-slot exploration equipment; independent geometry, not extracted assets.
# Dimensions are provisional; verify against first-person hand scale.
# Run: blender --background --python tools/blender/generate_object_scanner_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "object_scanner")
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

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .42, .34)
DARK = mat("Graphite polymer", (.035, .045, .05), .35, .42)
STEEL = mat("Brushed service metal", (.34, .39, .41), .82, .27)
RUBBER = mat("Grip elastomer", (.015, .02, .022), .0, .8)
GLASS = mat("Scanner display glass", (.02, .16, .19), .35, .16)
CYAN = mat("Active scan cyan", (.02, .42, .52), .2, .2, 2.0)
YELLOW = mat("Safety yellow", (1, .61, .025), .12, .38)

def finish(o, name, material, bevel=.018):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Manufactured edge radii", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.018, parent=None):
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
    o = finish(bpy.context.object, name, material, .012)
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

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def common_grip(root):
    box("Pistol grip", (0, .12, -.34), (.22, .24, .34), RUBBER, .04, root)
    box("Grip end cap", (0, .12, -.52), (.24, .25, .07), DARK, .02, root)
    box("Trigger guard", (0, -.015, -.22), (.16, .08, .08), STEEL, .02, root)

def display(root, loc=(0, -.16, .12), size=(.34, .035, .24)):
    box("Display bezel", loc, size, DARK, .025, root)
    box("Display glass", (loc[0], loc[1]-.022, loc[2]), (size[0]*.82, .012, size[2]*.72),
        GLASS, .012, root)
    for x in (-.10, 0, .10):
        box("Signal bar", (x, loc[1]-.031, loc[2]-.065), (.035, .008, .012), CYAN, .003, root)

def scanner_head(root, style):
    if style == "dish":
        cyl("Scanner head housing", (0, .02, .42), .22, .18, AMBER, parent=root)
        torus("Scanner antenna ring", (0, .02, .53), .16, .018, CYAN, parent=root)
        cyl("Scanner lens", (0, .02, .54), .11, .025, GLASS, parent=root)
    elif style == "bar":
        box("Scanner head housing", (0, .02, .42), (.48, .22, .16), AMBER, .04, root)
        box("Antenna window", (0, -.02, .51), (.30, .05, .035), CYAN, .01, root)
    elif style == "orb":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.20,
                                             location=(0, .02, .42))
        o = finish(bpy.context.object, "Scanner sensor orb", GLASS, 0)
        if root: o.parent = root
        torus("Orb protective ring", (0, .02, .42), .22, .025, STEEL, parent=root)
    else:
        box("Scanner head housing", (0, .02, .42), (.40, .24, .20), DARK, .05, root)
        cyl("Directional sensor", (0, -.02, .48), .12, .05, CYAN,
            (math.pi/2, 0, 0), root)
        box("Protective sensor hood", (0, .13, .53), (.48, .22, .07), AMBER, .025, root)

def build_a():
    r = root_empty("ObjectScanner_Variant_A_Round_Dish")
    box("Main housing", (0, .02, 0), (.48, .30, .62), AMBER, .055, r)
    scanner_head(r, "dish")
    display(r)
    common_grip(r)
    box("Side mode switch", (.26, .02, .13), (.055, .13, .10), YELLOW, .012, r)
    r["design_note"] = "Compact handheld scanner with a circular directional sensor head."
    return r

def build_b():
    r = root_empty("ObjectScanner_Variant_B_Wide_Array")
    box("Main housing", (0, .02, 0), (.58, .30, .58), DARK, .05, r)
    scanner_head(r, "bar")
    display(r, (0, -.16, .08), (.40, .035, .27))
    common_grip(r)
    for x in (-.18, .18):
        cyl("Array end cap", (x, .02, .42), .055, .18, STEEL, parent=r)
    r["design_note"] = "Wide linear sensor array with a broad screen."
    return r

def build_c():
    r = root_empty("ObjectScanner_Variant_C_Sensor_Orb")
    box("Main housing", (0, .02, 0), (.44, .28, .62), AMBER, .045, r)
    scanner_head(r, "orb")
    display(r, (0, -.15, .10), (.34, .035, .22))
    common_grip(r)
    box("Status strip", (0, -.17, -.12), (.20, .025, .045), CYAN, .01, r)
    r["design_note"] = "Spherical sensor element in a protective circular cage."
    return r

def build_d():
    r = root_empty("ObjectScanner_Variant_D_Rugged_Field")
    box("Main housing", (0, .02, 0), (.52, .32, .64), STEEL, .045, r)
    scanner_head(r, "hood")
    display(r, (0, -.17, .10), (.36, .035, .24))
    common_grip(r)
    for x in (-.25, .25):
        box("Side armor rail", (x, .02, .02), (.06, .28, .40), AMBER, .018, r)
    box("Top carry loop", (0, .18, .25), (.22, .08, .06), DARK, .018, r)
    r["design_note"] = "Rugged field scanner with protected directional sensor."
    return r

builders = [build_a, build_b, build_c, build_d]
roots = []
for i, build in enumerate(builders):
    r = build()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -.05))
    c = bpy.context.object
    c.name = "COLLIDER_ObjectScanner"
    c.dimensions = (.68, .60, 1.12)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "hand_equipment_collision_proxy"
    c.parent = r
    r["asset_id"] = "equipment-object-scanner"
    r["variant"] = chr(ord("A")+i)
    r["gameplay_reference"] = "Hand-slot exploration scanner; scans selected points of interest and indicates direction/proximity."
    r["target_dimensions_m"] = "0.68 x 0.60 x 1.12 provisional; verify against first-person hand scale."
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "object_scanner_variant_" + chr(ord("a")+i) + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
    roots.append(r)

for i, r in enumerate(roots):
    r.location.x = (i-1.5)*1.1
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "object_scanner_four_variants.blend"))
print("Created four original Object Scanner blockout variants:", OUT_DIR)
