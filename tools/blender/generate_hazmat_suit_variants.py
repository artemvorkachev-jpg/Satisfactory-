import bpy
import math
import os

# Original Satisfactory-inspired Hazmat Suit concept variants.
# Protective body-slot clothing; original geometry, not a copied game mesh.
# Character scale is provisional. Validate against the project Pioneer rig.
# Run: blender --background --python tools/blender/generate_hazmat_suit_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "hazmat_suit")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.55):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

YELLOW = mat("Protective safety yellow", (1.0, .66, .035), .08, .52)
DARK = mat("Graphite reinforcement", (.035, .045, .05), .3, .48)
STEEL = mat("Brushed fasteners", (.34, .39, .41), .75, .3)
RUBBER = mat("Sealed elastomer", (.018, .022, .025), .0, .82)
GLASS = mat("Inspection lens", (.025, .16, .19), .25, .18)
ORANGE = mat("Warning orange", (.9, .22, .025), .1, .5)

def finish(o, name, material, bevel=.025):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Soft manufactured edges", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.025, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, bevel)
    if parent:
        o.parent = parent
    return o

def uv(name, loc, scale, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, 0)
    if parent:
        o.parent = parent
    return o

def cyl(name, loc, radius, depth, material, rot=(0,0,0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, .015)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def base_body(root, style):
    # Generic neutral mannequin proportions for fit/scale checking, not a character portrait.
    uv("Torso suit shell", (0, 0, 1.08), (.31, .19, .43), YELLOW, root)
    uv("Hip section", (0, .01, .68), (.28, .18, .19), YELLOW, root)
    uv("Neck seal", (0, 0, 1.53), (.16, .15, .09), RUBBER, root)
    uv("Helmet placeholder", (0, .01, 1.73), (.20, .19, .24), YELLOW, root)
    box("Helmet visor", (0, -.16, 1.76), (.25, .035, .12), GLASS, .035, root)
    for x in (-.39, .39):
        uv("Upper arm suit", (x, 0, 1.18), (.14, .16, .32), YELLOW, root)
        uv("Forearm suit", (x*1.12, -.01, .77), (.12, .14, .30), YELLOW, root)
        uv("Glove", (x*1.12, -.02, .48), (.13, .14, .12), RUBBER, root)
        box("Wrist seal", (x*1.12, -.02, .60), (.26, .20, .07), DARK, .02, root)
    for x in (-.16, .16):
        uv("Thigh suit", (x, .01, .40), (.15, .17, .32), YELLOW, root)
        uv("Shin suit", (x, -.01, -.03), (.13, .15, .31), YELLOW, root)
        uv("Boot", (x, -.08, -.34), (.20, .34, .16), DARK, root)
        box("Boot toe cap", (x, -.23, -.31), (.18, .12, .07), STEEL, .015, root)
    if style == "reinforced":
        box("Chest armor plate", (0, -.18, 1.16), (.42, .06, .30), DARK, .035, root)
        for x in (-.22, .22):
            box("Shoulder guard", (x, -.03, 1.38), (.20, .25, .12), ORANGE, .025, root)
        for x in (-.16, .16):
            box("Knee guard", (x, -.15, .02), (.22, .08, .18), DARK, .03, root)
    elif style == "soft":
        for z in (.95, 1.18, 1.38):
            box("Chest seam", (0, -.185, z), (.46, .025, .025), ORANGE, .006, root)
        for x in (-.16, .16):
            box("Knee pad", (x, -.14, .02), (.18, .06, .14), ORANGE, .02, root)
    elif style == "modular":
        box("Central chest module", (0, -.20, 1.12), (.22, .07, .22), DARK, .025, root)
        for x in (-.23, .23):
            box("Chest service panel", (x, -.18, 1.18), (.13, .055, .17), STEEL, .02, root)
        for x in (-.16, .16):
            box("Shin reinforcement rail", (x, -.13, -.02), (.07, .05, .42), DARK, .015, root)

def add_suit_markings(root, style):
    box("Chest identification plate", (0, -.225, 1.38), (.17, .025, .065), STEEL, .01, root)
    box("Chest status lens", (0, -.242, 1.38), (.07, .012, .03), GLASS, .005, root)
    for x in (-.24, .24):
        box("Shoulder safety marking", (x, -.12, 1.34), (.07, .018, .12), ORANGE, .008, root)
    box("Waist utility belt", (0, .0, .68), (.58, .22, .08), DARK, .02, root)

builders = [
    ("A", "Standard_Sealed", "standard"),
    ("B", "Reinforced_Field", "reinforced"),
    ("C", "Flexible_Lightweight", "soft"),
    ("D", "Modular_Service", "modular"),
]
roots = []
for letter, label, style in builders:
    r = root_empty("HazmatSuit_Variant_" + letter + "_" + label)
    base_body(r, style)
    add_suit_markings(r, style)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .70))
    c = bpy.context.object
    c.name = "COLLIDER_HazmatSuit"
    c.dimensions = (.95, .62, 2.15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "wearable_equipment_proxy"
    c.parent = r
    r["asset_id"] = "equipment-hazmat-suit"
    r["variant"] = letter
    r["gameplay_reference"] = "Body-slot protective suit; head protection remains a separate Gas Mask item."
    r["target_dimensions_m"] = "Approx. 1.9 m character height; provisional mannequin fit, verify with Pioneer rig."
    r["design_note"] = "Original safety-yellow industrial suit concept; do not treat blockout as approved."
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "hazmat_suit_variant_" + letter.lower() + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
    roots.append(r)

for i, r in enumerate(roots):
    r.location.x = (i-1.5)*1.35
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "hazmat_suit_four_variants.blend"))
print("Created four original Hazmat Suit blockout variants:", OUT_DIR)
