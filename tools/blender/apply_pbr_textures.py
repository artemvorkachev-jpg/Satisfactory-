import bpy, os, math, glob, struct, json
from array import array

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEXTURE_DIR = os.path.join(ROOT, "assets", "textures", "procedural")
os.makedirs(TEXTURE_DIR, exist_ok=True)

SIZE = 256
FAMILIES = ("metal", "polymer", "rubber", "organic", "glass")

def make_map(family, channel):
    path = os.path.join(TEXTURE_DIR, family + "_" + channel + ".png")
    if os.path.isfile(path) and os.path.getsize(path) > 2048:
        return path
    img = bpy.data.images.new(family + "_" + channel, width=SIZE, height=SIZE, alpha=False, float_buffer=False)
    pixels = array('f')
    for y in range(SIZE):
        v = y / SIZE
        for x in range(SIZE):
            u = x / SIZE
            a = math.sin(2*math.pi*(u*17 + math.sin(v*2*math.pi*3)*.012))
            b = math.sin(2*math.pi*(v*29 + math.sin(u*2*math.pi*5)*.008))
            c = math.sin(2*math.pi*(u*71 + v*37))
            d = math.sin(2*math.pi*(u*113 - v*89))
            noise = (a*.38 + b*.28 + c*.20 + d*.14)
            if family == "metal":
                noise = noise*.62 + math.sin(2*math.pi*(v*137 + u*2))*.38
            elif family == "polymer":
                noise = noise*.72 + math.sin(2*math.pi*(u*53)*math.sin(v*53))*.28
            elif family == "rubber":
                noise = noise*.55 + math.sin(2*math.pi*u*43)*math.sin(2*math.pi*v*43)*.45
            elif family == "organic":
                noise = noise*.5 + math.sin(2*math.pi*u*9)*math.sin(2*math.pi*v*11)*.5
            else:
                noise = noise*.9 + math.sin(2*math.pi*(u*101+v*97))*.1
            if channel == "albedo":
                value = .91 + noise*.075
            elif channel == "roughness":
                base = {"metal":.34,"polymer":.62,"rubber":.84,"organic":.78,"glass":.19}[family]
                value = base + noise*.10
            else:
                value = .42 + noise*.13
            value = max(0.0, min(1.0, value))
            pixels.extend((value, value, value, 1.0))
    img.pixels.foreach_set(pixels)
    img.file_format = "PNG"
    img.filepath_raw = path
    img.save()
    bpy.data.images.remove(img)
    return path

MAPS = {}
for family in FAMILIES:
    MAPS[family] = {channel: make_map(family, channel) for channel in ("albedo","roughness","height")}

def material_family(material):
    name = material.name.lower()
    if "rubber" in name or "tire" in name: return "rubber"
    if "organic" in name or "foliage" in name or "leaf" in name or "wood" in name: return "organic"
    if "glass" in name or "crystal" in name or "emission" in name or "screen" in name: return "glass"
    if "polymer" in name or "plastic" in name or "fabric" in name: return "polymer"
    return "metal"

def image_node(nodes, path, name, non_color=False):
    image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    node = nodes.new("ShaderNodeTexImage")
    node.image = image
    node.label = name
    node.name = name
    node.interpolation = "Linear"
    return node

def texture_material(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not principled: return
    base_input = principled.inputs.get("Base Color")
    if not base_input or base_input.is_linked: return
    base = tuple(base_input.default_value)
    family = material_family(mat)
    tex_albedo = image_node(nodes, MAPS[family]["albedo"], "PBR Albedo - " + family)
    tex_albedo.location = (-620, 220)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.0
    multiply.inputs[1].default_value = base
    multiply.location = (-350, 220)
    links.new(tex_albedo.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], base_input)
    tex_rough = image_node(nodes, MAPS[family]["roughness"], "PBR Roughness - " + family, True)
    tex_rough.location = (-620, -40)
    rough = principled.inputs.get("Roughness")
    if rough and not rough.is_linked: links.new(tex_rough.outputs["Color"], rough)
    tex_height = image_node(nodes, MAPS[family]["height"], "PBR Height - " + family, True)
    tex_height.location = (-620, -300)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .16
    bump.inputs["Distance"].default_value = .018
    bump.location = (-300, -240)
    links.new(tex_height.outputs["Color"], bump.inputs["Height"])
    normal = principled.inputs.get("Normal")
    if normal and not normal.is_linked: links.new(bump.outputs["Normal"], normal)

def unwrap_object(obj):
    if obj.type != "MESH" or not obj.data.polygons: return
    if obj.data.uv_layers and len(obj.data.uv_layers) > 0: return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=.025)
    bpy.ops.object.mode_set(mode="OBJECT")

blend = bpy.data.filepath
if not blend.endswith("_four_variants.blend"):
    raise RuntimeError("Expected a *_four_variants.blend source file")
for obj in bpy.data.objects:
    unwrap_object(obj)
for mat in bpy.data.materials:
    if mat.users > 0:
        texture_material(mat)

# Keep texture images available to Blender users opening the .blend source.
bpy.ops.file.pack_all()

# Re-export each separately addressable A/B/C/D root as a textured GLB.
roots = [o for o in bpy.data.objects if o.type == "EMPTY" and o.get("variant")]
if len(roots) != 4:
    raise RuntimeError("Expected four variant roots, found " + str(len(roots)))
folder = os.path.dirname(blend)
stem = os.path.basename(blend)[:-len("_four_variants.blend")]
for root in roots:
    letter = str(root.get("variant","")).lower()
    if letter not in ("a","b","c","d"): raise RuntimeError("Unknown variant label")
    bpy.ops.object.select_all(action="DESELECT")
    selected = [root] + list(root.children_recursive)
    for obj in selected: obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    out = os.path.join(folder, stem + "_variant_" + letter + ".glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True)
    print("Textured export:", out, flush=True)

bpy.ops.wm.save_as_mainfile(filepath=blend)
print("Applied PBR textures and UVs:", blend, flush=True)
