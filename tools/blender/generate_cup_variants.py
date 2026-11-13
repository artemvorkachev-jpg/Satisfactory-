import bpy
import math
import os

# Original Satisfactory-inspired Cup asset study.
# A/B correspond to the two confirmed in-game cup variants. C/D are optional
# concept directions for review, not claimed to be additional canonical items.
# Run: blender --background --python tools/blender/generate_cup_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "cup")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.38):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

WHITE = mat("FICSIT ceramic enamel", (.82, .84, .78), .18, .26)
GRAPHITE = mat("Graphite ceramic", (.045, .06, .07), .22, .28)
GOLD = mat("Employee award gold finish", (.82, .55, .12), .72, .2)
STEEL = mat("Brushed steel", (.34, .39, .41), .82, .24)
AMBER = mat("Industrial amber", (.82, .29, .055), .35, .32)
COFFEE = mat("Coffee surface", (.075, .035, .018), .0, .22)

def finish(o, name, material):
    o.name = name
    if material:
        o.data.materials.append(material)
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def make_mug(root, body_mat, style):
    # Cup axis is Z. Mesh dimensions are provisional small handheld prop scale.
    if style == "standard":
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.105, radius2=.135, depth=.22,
                                        location=(0, 0, .11))
        body = finish(bpy.context.object, "Cup body", body_mat)
        body.parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.127, minor_radius=.012,
                                         major_segments=48, minor_segments=10,
                                         location=(0, 0, .22))
        finish(bpy.context.object, "Rolled rim", STEEL).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.073, minor_radius=.018,
                                         major_segments=48, minor_segments=12,
                                         location=(.13, 0, .12), rotation=(math.pi/2, 0, 0))
        finish(bpy.context.object, "Cup handle", body_mat).parent = root
    elif style == "gold":
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.105, radius2=.135, depth=.22,
                                        location=(0, 0, .11))
        finish(bpy.context.object, "Gold cup body", body_mat).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.127, minor_radius=.014,
                                         major_segments=48, minor_segments=10,
                                         location=(0, 0, .22))
        finish(bpy.context.object, "Gold rolled rim", GOLD).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.073, minor_radius=.019,
                                         major_segments=48, minor_segments=12,
                                         location=(.13, 0, .12), rotation=(math.pi/2, 0, 0))
        finish(bpy.context.object, "Gold cup handle", body_mat).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.105, minor_radius=.008,
                                         major_segments=48, minor_segments=8,
                                         location=(0, 0, .055))
        finish(bpy.context.object, "Gold base ring", STEEL).parent = root
    elif style == "insulated":
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.115, radius2=.14, depth=.24,
                                        location=(0, 0, .12))
        finish(bpy.context.object, "Insulated cup shell", body_mat).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.132, minor_radius=.012,
                                         major_segments=48, minor_segments=10,
                                         location=(0, 0, .24))
        finish(bpy.context.object, "Insulated cup rim", STEEL).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.075, minor_radius=.018,
                                         major_segments=48, minor_segments=12,
                                         location=(.14, 0, .13), rotation=(math.pi/2, 0, 0))
        finish(bpy.context.object, "Insulated cup handle", GRAPHITE).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.11, minor_radius=.018,
                                         major_segments=48, minor_segments=10,
                                         location=(0, 0, .035))
        finish(bpy.context.object, "Insulated grip band", AMBER).parent = root
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.11, radius2=.135, depth=.23,
                                        location=(0, 0, .115))
        finish(bpy.context.object, "Travel mug body", body_mat).parent = root
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.135, depth=.035,
                                            location=(0, 0, .25))
        finish(bpy.context.object, "Travel lid", GRAPHITE).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.12, minor_radius=.01,
                                         major_segments=48, minor_segments=8,
                                         location=(0, 0, .275))
        finish(bpy.context.object, "Lid seal ring", STEEL).parent = root
        bpy.ops.mesh.primitive_torus_add(major_radius=.07, minor_radius=.018,
                                         major_segments=48, minor_segments=12,
                                         location=(.14, 0, .12), rotation=(math.pi/2, 0, 0))
        finish(bpy.context.object, "Travel mug handle", body_mat).parent = root

    # Coffee surface is separate so it can be hidden when the cup is dropped/empty.
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.115, depth=.006,
                                        location=(0, 0, .205))
    finish(bpy.context.object, "Coffee surface", COFFEE).parent = root

def build(letter, label, body_mat, style, canonical):
    root = root_empty("Cup_Variant_" + letter + "_" + label)
    make_mug(root, body_mat, style)
    root["asset_id"] = "item-cup"
    root["variant"] = letter
    root["canonical_status"] = canonical
    root["target_dimensions_m"] = "Approx. 0.30 m tall, 0.28 m handle width; provisional handheld scale."
    root["design_note"] = "Original geometry; use canonical variants A/B as reference candidates."
    return root

variants = [
    ("A", "FICSIT_Coffee_Cup", WHITE, "standard", "confirmed in-game item"),
    ("B", "Employee_of_the_Planet_Cup", GOLD, "gold", "confirmed in-game cosmetic variant"),
    ("C", "Insulated_Service_Cup", GRAPHITE, "insulated", "optional concept, not a canonical item"),
    ("D", "Lidded_Travel_Cup", AMBER, "travel", "optional concept, not a canonical item"),
]
roots = []
for letter, label, material, style, canonical in variants:
    r = build(letter, label, material, style, canonical)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .12))
    c = bpy.context.object
    c.name = "COLLIDER_Cup"
    c.dimensions = (.40, .40, .34)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "small_handheld_prop_proxy"
    c.parent = r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "cup_variant_" + letter.lower() + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
    roots.append(r)

for i, r in enumerate(roots):
    r.location.x = (i-1.5)*.65
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "cup_four_variants.blend"))
print("Created Cup blockout variants:", OUT_DIR)
