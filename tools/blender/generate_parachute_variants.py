import bpy
import math
import os

# Original Satisfactory-inspired Parachute blockout study.
# The game reference confirms a reusable back-slot parachute; canopy shapes below
# are concept variants for user review, not copies of the original proprietary mesh.
# Dimensions are provisional and require a Pioneer scale reference.
# Run: blender --background --python tools/blender/generate_parachute_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "parachute")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .42, .34)
DARK = mat("Graphite alloy", (.045, .06, .07), .75, .32)
STEEL = mat("Brushed service metal", (.34, .39, .41), .8, .28)
FABRIC = mat("Technical canopy fabric", (.72, .76, .70), .0, .8)
FABRIC_DARK = mat("Canopy reinforced panels", (.15, .22, .24), .0, .78)
SAFETY = mat("Safety yellow", (1, .61, .025), .12, .42)
STRAP = mat("Harness webbing", (.025, .03, .032), .0, .82)

def finish(o, name, material, bevel=.02):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Manufactured edge radii", "BEVEL")
        b.width = bevel
        b.segments = 2
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

def curve_line(name, points, material, radius=.006, parent=None):
    data = bpy.data.curves.new(name + "_Curve", "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spline = data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def harness_pack(root, style):
    box("Dorsal mounting plate", (0, .15, 0), (.48, .14, .62), DARK, .04, root)
    box("Upper harness yoke", (0, .24, .23), (.62, .10, .11), STEEL, .02, root)
    for x in (-.27, .27):
        strap = box("Shoulder strap", (x, -.01, .08), (.10, .09, .52), STRAP, .03, root)
        strap.rotation_euler[1] = -x*.65
        box("Strap buckle", (x*.75, -.03, -.20), (.12, .08, .07), SAFETY, .012, root)
    box("Waist belt", (0, .18, -.28), (.62, .10, .10), STRAP, .02, root)
    if style == "capsule":
        box("Rounded pack shell", (0, .02, 0), (.56, .27, .58), AMBER, .10, root)
        box("Release latch", (0, -.13, .04), (.16, .025, .12), SAFETY, .012, root)
    elif style == "canister":
        box("Canopy canister", (0, .02, .02), (.50, .30, .50), DARK, .04, root)
        box("Canister cover", (0, -.145, .02), (.38, .025, .36), AMBER, .025, root)
        box("Release handle", (0, -.17, -.17), (.18, .045, .06), SAFETY, .012, root)
    elif style == "modular":
        box("Central pack spine", (0, .02, .02), (.22, .25, .62), STEEL, .03, root)
        for x in (-.22, .22):
            box("Side fabric pod", (x, .04, .02), (.18, .24, .48), AMBER, .035, root)
            box("Pod latch", (x, -.10, .12), (.06, .025, .10), SAFETY, .01, root)
    else:
        box("Fabric pack body", (0, .02, 0), (.52, .24, .52), AMBER, .055, root)
        box("Inspection panel", (0, -.11, .03), (.26, .02, .18), DARK, .018, root)
    for x in (-.17, .17):
        box("Lower deployment tab", (x, -.12, -.19), (.08, .035, .08), SAFETY, .012, root)

def canopy_mesh(root, kind, material):
    # Canopy is placed above the backpack for a deployed-state preview.
    rings = 7
    segments = 32
    verts = []
    faces = []
    for ri in range(rings):
        t = (ri + 1) / rings
        for si in range(segments):
            a = 2 * math.pi * si / segments
            if kind == "elliptic":
                radius = 1.65 * t
                z = 2.35 - .50 * t * t
                x_scale, y_scale = 1.25, .78
            elif kind == "segmented":
                scallop = 1.0 + .045 * math.cos(8 * a)
                radius = 1.55 * t * scallop
                z = 2.25 - .62 * t * t
                x_scale, y_scale = 1.0, 1.0
            elif kind == "rectangular":
                radius = 1.55 * t
                z = 2.10 - .35 * t * t
                x_scale, y_scale = 1.35, .65
            else:
                radius = 1.55 * t
                z = 2.30 - .70 * t * t
                x_scale, y_scale = 1.0, 1.0
            verts.append((math.cos(a)*radius*x_scale, math.sin(a)*radius*y_scale, z))
    for ri in range(rings-1):
        for si in range(segments):
            a = ri*segments + si
            b = ri*segments + (si+1) % segments
            c = (ri+1)*segments + (si+1) % segments
            d = (ri+1)*segments + si
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new("CanopyMesh_" + kind)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    canopy = bpy.data.objects.new("DEPLOYED_CANOPY_" + kind, mesh)
    bpy.context.collection.objects.link(canopy)
    canopy.parent = root
    canopy["animation_note"] = "Separate deployed-state mesh; show only while parachute is deployed."
    # Reinforcement seams follow radial lines down the canopy.
    for si in range(0, segments, 4):
        a = 2*math.pi*si/segments
        pts = []
        for ri in range(rings):
            v = verts[ri*segments + si]
            pts.append(v)
        curve_line("Canopy seam", pts, SAFETY, .004, root)
    return canopy

def suspension_lines(root, kind):
    for i in range(8):
        a = 2*math.pi*i/8
        top = (math.cos(a)*1.0, math.sin(a)*.65, 1.75)
        bottom = (math.cos(a)*.22, .08, -.20)
        curve_line("Suspension line", [bottom, (bottom[0]*.55, bottom[1], .65), top],
                   STRAP, .006, root)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .05, 0))
    c = bpy.context.object
    c.name = "COLLIDER_Parachute_Pack"
    c.dimensions = (.78, .46, .82)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "equipment_collision_proxy"
    c.parent = root

def export_root(root, filename):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in root.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, filename + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)

variants = [
    ("A", "Round_Dome", "round", "fabric"),
    ("B", "Elliptical_Canopy", "elliptic", "capsule"),
    ("C", "Segmented_Canopy", "segmented", "canister"),
    ("D", "Rectangular_Canopy", "rectangular", "modular"),
]
roots = []
for letter, label, canopy_kind, pack_style in variants:
    root = root_empty("Parachute_Variant_" + letter + "_" + label)
    harness_pack(root, pack_style)
    canopy_mesh(root, canopy_kind, FABRIC)
    suspension_lines(root, canopy_kind)
    add_collider(root)
    root["asset_id"] = "equipment-parachute"
    root["variant"] = letter
    root["gameplay_reference"] = "Reusable back-slot parachute; slows descent and prevents fall damage while deployed."
    root["target_dimensions_m"] = "folded pack 0.78 x 0.46 x 0.82 provisional; canopy size provisional."
    root["design_note"] = "Original visual concept; compare silhouette against current in-game reference."
    export_root(root, "parachute_variant_" + letter.lower())
    roots.append(root)

for i, root in enumerate(roots):
    root.location.x = (i - 1.5) * 4.0

bpy.ops.object.select_all(action="DESELECT")
for root in roots:
    root.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "parachute_four_variants.blend"))
print("Created four original Parachute blockout variants:", OUT_DIR)
