import bpy
import math
import os

# Original Satisfactory-inspired Hoverpack model study.
# The game reference specifies a back-slot personal hover device powered by
# nearby electrical connections. These are original visual concepts, not copies.
# Dimensions are provisional because the reference page does not publish mesh scale.
# Run: blender --background --python tools/blender/generate_hoverpack_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "hoverpack")
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
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
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value = (*color, 1.0)
        bs.inputs["Emission Strength"].default_value = emission
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .48, .32)
DARK = mat("Graphite alloy", (.045, .06, .07), .82, .28)
STEEL = mat("Brushed service metal", (.34, .39, .41), .86, .25)
RUBBER = mat("Harness elastomer", (.018, .022, .025), .02, .78)
GLASS = mat("Power status glass", (.025, .19, .22), .45, .18)
YELLOW = mat("Safety yellow", (1.0, .61, .025), .18, .34)
CYAN = mat("Power-link cyan", (.02, .42, .52), .25, .22, 2.0)

def finish(o, name, material, bevel=.025):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        mod = o.modifiers.new("Manufactured edge radii", "BEVEL")
        mod.width = bevel
        mod.segments = 3
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

def cyl(name, loc, radius, depth, material, rot=(0, 0, 0), parent=None, vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, min(.025, radius * .12))
    if parent:
        o.parent = parent
    return o

def torus(name, loc, major, minor, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=40, minor_segments=10,
                                     location=loc)
    o = finish(bpy.context.object, name, material, 0)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    return o

def harness(root):
    box("Dorsal mounting plate", (0, .15, 0), (.58, .15, .80), DARK, .045, root)
    box("Shoulder yoke", (0, .24, .31), (.68, .12, .13), STEEL, .025, root)
    for x in (-.30, .30):
        strap = box("Shoulder strap", (x, -.005, .10), (.12, .10, .65), RUBBER, .04, root)
        strap.rotation_euler[1] = -x * .75
        box("Lower strap clasp", (x * .7, .02, -.28), (.14, .11, .09), STEEL, .02, root)
    box("Waist stabilizer", (0, .19, -.35), (.66, .12, .11), DARK, .02, root)

def power_core(root, z=0.0, size=1.0):
    box("Power receiver housing", (0, .02, z), (.28*size, .24, .48*size), AMBER, .045, root)
    box("Power status display bezel", (0, -.115, z+.08), (.19*size, .025, .12*size), DARK, .012, root)
    box("Power status display", (0, -.132, z+.08), (.13*size, .012, .07*size), GLASS, .006, root)
    for dx in (-.06, .06):
        cyl("Connection indicator", (dx*size, -.15, z-.055), .018, .012, CYAN,
            (math.pi/2, 0, 0), root, 16)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .06, 0))
    c = bpy.context.object
    c.name = "COLLIDER_Hoverpack"
    c.dimensions = (.90, .50, 1.00)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "equipment_collision_proxy"
    c.parent = root

def export_root(root, name):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, name + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)

def variant_a():
    root = root_empty("Hoverpack_Variant_A_Twin_Lift_Pods")
    harness(root)
    power_core(root, .05)
    for x in (-.29, .29):
        cyl("Vertical lift pod", (x, .08, -.02), .145, .62, AMBER, parent=root)
        torus("Lift emitter ring", (x, .08, -.36), .115, .025, CYAN, root)
        cyl("Emitter face", (x, .08, -.37), .09, .025, DARK, parent=root)
        box("Pod armor stripe", (x, -.07, .02), (.035, .02, .36), YELLOW, .008, root)
    box("Upper cross brace", (0, .13, .40), (.70, .16, .10), STEEL, .025, root)
    root["design_note"] = "Twin compact lift pods with a central wireless power receiver."
    return root

def variant_b():
    root = root_empty("Hoverpack_Variant_B_Armored_Disc_Emitters")
    harness(root)
    box("Armored dorsal shell", (0, .13, .02), (.76, .25, .78), AMBER, .075, root)
    power_core(root, .08, .9)
    for x in (-.27, .27):
        cyl("Recessed emitter housing", (x, .01, -.20), .19, .14, DARK,
            (math.pi/2, 0, 0), root)
        torus("Emitter luminous ring", (x, -.075, -.20), .145, .025, CYAN, root)
        cyl("Emitter lens", (x, -.08, -.20), .105, .018, GLASS,
            (math.pi/2, 0, 0), root)
    box("Top service handle", (0, .18, .47), (.34, .12, .075), YELLOW, .02, root)
    root["design_note"] = "Armored shell with two recessed circular lift emitters."
    return root

def variant_c():
    root = root_empty("Hoverpack_Variant_C_Open_Industrial_Frame")
    harness(root)
    power_core(root, .02)
    for x in (-.30, .30):
        box("Structural side rail", (x, .15, 0), (.09, .16, .82), STEEL, .025, root)
        torus("Large levitation ring", (x, .015, -.05), .17, .035, CYAN, root)
        cyl("Ring core", (x, .015, -.05), .105, .10, DARK, parent=root)
        box("Lower stabilizer", (x, .16, -.38), (.18, .18, .09), AMBER, .02, root)
    box("Upper frame crossbar", (0, .18, .36), (.72, .14, .09), DARK, .02, root)
    box("Lower frame crossbar", (0, .18, -.35), (.72, .14, .09), DARK, .02, root)
    root["design_note"] = "Open service frame with visible levitation rings and reinforced crossbars."
    return root

def variant_d():
    root = root_empty("Hoverpack_Variant_D_Modular_Stabilizer_Wings")
    harness(root)
    power_core(root, .0, 1.0)
    box("Central spine armor", (0, .16, .02), (.24, .18, .80), DARK, .035, root)
    for x in (-.36, .36):
        wing = box("Folded stabilizer module", (x, .12, .02), (.25, .23, .62), AMBER, .045, root)
        wing.rotation_euler[1] = x * .18
        cyl("Lower lift emitter", (x, .02, -.34), .12, .12, STEEL, parent=root)
        torus("Emitter rim", (x, .02, -.41), .095, .022, CYAN, root)
        box("Module latch", (x*.78, -.015, .20), (.08, .05, .12), YELLOW, .012, root)
    box("Top wireless pickup mast", (0, .20, .49), (.07, .08, .22), STEEL, .018, root)
    cyl("Pickup antenna cap", (0, .20, .61), .065, .045, CYAN, parent=root)
    root["design_note"] = "Modular side stabilizers and raised power-link pickup mast."
    return root

builders = [variant_a, variant_b, variant_c, variant_d]
roots = []
for i, build in enumerate(builders):
    root = build()
    add_collider(root)
    root["asset_id"] = "equipment-hoverpack"
    root["variant"] = chr(ord("A") + i)
    root["gameplay_reference"] = "Back-slot hover equipment; wirelessly draws power from nearby powered structures and railways."
    root["target_dimensions_m"] = "0.90 x 0.50 x 1.00 provisional; confirm against player scale reference."
    export_root(root, "hoverpack_variant_" + chr(ord("A") + i).lower())
    roots.append(root)

for i, root in enumerate(roots):
    root.location.x = (i - 1.5) * 1.45

bpy.ops.object.select_all(action="DESELECT")
for root in roots:
    root.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "hoverpack_four_variants.blend"))
print("Created four original Hoverpack blockout variants.")
print("Output:", OUT_DIR)
