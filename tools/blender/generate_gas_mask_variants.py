import bpy
import math
import os

# Original Satisfactory-inspired Gas Mask concept variants.
# Head-slot protective equipment; geometry is independently designed.
# Dimensions are provisional and must be checked against the Pioneer head scale.
# Run: blender --background --python tools/blender/generate_gas_mask_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "gas_mask")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .35, .35)
DARK = mat("Graphite polymer", (.035, .045, .05), .25, .45)
STEEL = mat("Brushed filter metal", (.34, .39, .41), .78, .28)
RUBBER = mat("Flexible face seal", (.012, .016, .018), .0, .8)
GLASS = mat("Smoked visor", (.025, .12, .15), .42, .16)
YELLOW = mat("Safety yellow", (1, .61, .025), .12, .38)

def finish(o, name, material, bevel=.015):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Molded edge radius", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.015, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, bevel)
    if parent:
        o.parent = parent
    return o

def uv_sphere(name, loc, scale, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, 0)
    if parent:
        o.parent = parent
    return o

def cyl(name, loc, radius, depth, material, rot=(math.pi/2, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, .012)
    if parent:
        o.parent = parent
    return o

def torus(name, loc, major, minor, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=8,
                                     location=loc, rotation=(math.pi/2, 0, 0))
    o = finish(bpy.context.object, name, material, 0)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def straps(root):
    for side in (-1, 1):
        strap = box("Head strap", (side*.36, .08, .10), (.10, .10, .48), RUBBER, .035, root)
        strap.rotation_euler[1] = side*.20
        box("Strap adjuster", (side*.39, .04, .18), (.11, .07, .07), STEEL, .012, root)
    box("Rear strap bridge", (0, .14, .22), (.62, .08, .09), DARK, .025, root)

def filter_canister(root, x, z, radius=.105):
    cyl("Filter housing", (x, -.20, z), radius, .20, STEEL, parent=root)
    torus("Filter retaining ring", (x, -.31, z), radius*.82, .018, YELLOW, root)
    cyl("Filter grille", (x, -.315, z), radius*.68, .025, DARK, parent=root)
    for i in range(8):
        a = 2*math.pi*i/8
        uv_sphere("Filter perforation", (x+math.cos(a)*radius*.42, -.333, z+math.sin(a)*radius*.42),
                  (.009,.006,.009), STEEL, root)

def build_a():
    r = root_empty("GasMask_Variant_A_Dual_Filter")
    uv_sphere("Facepiece", (0, -.10, 0), (.38,.18,.34), DARK, r)
    uv_sphere("Face seal", (0, -.235, -.015), (.36,.06,.29), RUBBER, r)
    box("Central nose bridge", (0, -.28, .08), (.10,.06,.22), STEEL, .025, r)
    for x in (-.23, .23):
        filter_canister(r, x, -.12, .10)
    for x in (-.18, .18):
        uv_sphere("Eye lens", (x, -.245, .19), (.105,.035,.08), GLASS, r)
        torus("Lens rim", (x, -.27, .19), .09, .012, STEEL, r)
    straps(r)
    r["design_note"] = "Classic industrial facepiece with twin side filter canisters."
    return r

def build_b():
    r = root_empty("GasMask_Variant_B_Central_Filter")
    uv_sphere("Facepiece", (0, -.10, 0), (.39,.18,.34), AMBER, r)
    uv_sphere("Face seal", (0, -.23, -.02), (.37,.06,.30), RUBBER, r)
    box("Wide visor frame", (0, -.24, .19), (.48,.07,.18), DARK, .045, r)
    box("Panoramic lens", (0, -.282, .19), (.39,.025,.10), GLASS, .025, r)
    filter_canister(r, 0, -.17, .125)
    box("Lower chin guard", (0, -.18, -.25), (.34,.12,.10), STEEL, .035, r)
    straps(r)
    r["design_note"] = "Broad panoramic visor and a single central filter module."
    return r

def build_c():
    r = root_empty("GasMask_Variant_C_Compact_Respirator")
    uv_sphere("Compact face shell", (0, -.10, 0), (.34,.17,.28), DARK, r)
    uv_sphere("Soft seal", (0, -.225, -.02), (.33,.055,.25), RUBBER, r)
    for x in (-.14, .14):
        uv_sphere("Eye cup", (x, -.24, .17), (.11,.055,.09), GLASS, r)
        torus("Eye cup rim", (x, -.275, .17), .09, .014, STEEL, r)
    filter_canister(r, 0, -.13, .09)
    box("Lower intake cover", (0, -.20, -.23), (.20,.07,.09), AMBER, .025, r)
    straps(r)
    r["design_note"] = "Compact low-profile mask with small twin lenses and centered intake."
    return r

def build_d():
    r = root_empty("GasMask_Variant_D_Armored_Field_Mask")
    uv_sphere("Armored face shell", (0, -.09, 0), (.40,.19,.35), AMBER, r)
    uv_sphere("Full perimeter seal", (0, -.23, -.02), (.38,.065,.30), RUBBER, r)
    for x in (-.22, .22):
        box("Angular lens frame", (x, -.25, .18), (.19,.07,.16), DARK, .035, r)
        uv_sphere("Angular lens", (x, -.29, .18), (.075,.025,.055), GLASS, r)
        filter_canister(r, x*.72, -.16, .085)
    box("Forehead ID plate", (0, -.25, .31), (.18,.04,.055), STEEL, .012, r)
    box("Chin guard", (0, -.17, -.26), (.36,.13,.10), DARK, .035, r)
    straps(r)
    r["design_note"] = "Armored field mask with angular twin lenses and paired compact filters."
    return r

builders = [build_a, build_b, build_c, build_d]
roots = []
for i, build in enumerate(builders):
    r = build()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    c = bpy.context.object
    c.name = "COLLIDER_GasMask"
    c.dimensions = (.92, .58, .72)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c.display_type = "WIRE"
    c.hide_render = True
    c["physics_role"] = "head_equipment_collision_proxy"
    c.parent = r
    r["asset_id"] = "equipment-gas-mask"
    r["variant"] = chr(ord("A")+i)
    r["gameplay_reference"] = "Head-slot equipment that filters the ambient gas hazard; replaceable filter item is separate."
    r["target_dimensions_m"] = "0.92 x 0.58 x 0.72 provisional; verify against Pioneer head reference."
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active = r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "gas_mask_variant_" + chr(ord("a")+i) + ".glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
    roots.append(r)

for i, r in enumerate(roots):
    r.location.x = (i-1.5)*1.25
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active = roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "gas_mask_four_variants.blend"))
print("Created four original Gas Mask blockout variants:", OUT_DIR)
