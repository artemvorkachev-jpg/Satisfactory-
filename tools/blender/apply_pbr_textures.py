import bpy, os, math, glob, struct, json
from array import array

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEXTURE_DIR = os.path.join(ROOT, "assets", "textures", "procedural")
os.makedirs(TEXTURE_DIR, exist_ok=True)

SIZE = 512
TEXTURE_SUFFIX = "_v2"
FAMILIES = ("metal", "polymer", "rubber", "organic", "glass")

def make_map(family, channel):
    path = os.path.join(TEXTURE_DIR, family + "_" + channel + TEXTURE_SUFFIX + ".png")
    if os.path.isfile(path) and os.path.getsize(path) > 2048:
        return path
    img = bpy.data.images.new(family + "_" + channel, width=SIZE, height=SIZE, alpha=False, float_buffer=False)
    pixels = array('f')
    for y in range(SIZE):
        v = y / SIZE
        for x in range(SIZE):
            u = x / SIZE
            a = math.sin(2*math.pi*(u*13 + math.sin(v*2*math.pi*3)*.018))
            b = math.sin(2*math.pi*(v*23 + math.sin(u*2*math.pi*5)*.014))
            c = math.sin(2*math.pi*(u*67 + v*41))
            d = math.sin(2*math.pi*(u*127 - v*97))
            fine = math.sin(2*math.pi*(u*193 + v*151))
            noise = a*.31 + b*.24 + c*.18 + d*.14 + fine*.13
            if family == "metal":
                scratches = math.sin(2*math.pi*(v*79 + math.sin(u*2*math.pi*2)*.045))
                brushed = math.sin(2*math.pi*(v*151 + u*7))
                noise = noise*.48 + scratches*.34 + brushed*.18
            elif family == "polymer":
                orange_peel = math.sin(2*math.pi*u*37)*math.sin(2*math.pi*v*43)
                noise = noise*.58 + orange_peel*.42
            elif family == "rubber":
                grain = math.sin(2*math.pi*u*53)*math.sin(2*math.pi*v*53)
                ribs = math.sin(2*math.pi*(u*19 + v*3))
                noise = noise*.48 + grain*.36 + ribs*.16
            elif family == "organic":
                veins = math.sin(2*math.pi*(u*11 + math.sin(v*2*math.pi*4)*.035))
                veins *= math.sin(2*math.pi*(v*5))
                flecks = math.sin(2*math.pi*(u*79 + v*67))
                noise = noise*.47 + veins*.38 + flecks*.15
            else:
                smudges = math.sin(2*math.pi*(u*7 + v*9))
                noise = noise*.68 + smudges*.32
            if channel == "albedo":
                value = .82 + noise*.17
            elif channel == "roughness":
                base = {"metal":.38,"polymer":.64,"rubber":.86,"organic":.82,"glass":.22}[family]
                value = base + noise*.18
            else:
                value = .5 + noise*.29
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
    if not principled:
        return

    base_input = principled.inputs.get("Base Color")
    if not base_input:
        return

    # Peel away every previous albedo multiply layer. This makes repeated
    # runs idempotent even when a material was processed by an earlier pass.
    while base_input.is_linked:
        candidate = base_input.links[0].from_node
        is_generated_mix = (
            candidate.type == "MIX_RGB" and any(
                link.from_node.name.startswith("PBR Albedo - ") and link.to_socket == candidate.inputs[2]
                for link in candidate.inputs[2].links
            )
        )
        if not is_generated_mix:
            break
        source_links = list(candidate.inputs[1].links)
        source_socket = source_links[0].from_socket if source_links else None
        source_value = tuple(candidate.inputs[1].default_value)
        for link in list(base_input.links):
            links.remove(link)
        if source_socket:
            links.new(source_socket, base_input)
        else:
            base_input.default_value = source_value
        nodes.remove(candidate)

    original_links = list(base_input.links)
    original_source = original_links[0].from_socket if original_links else None
    original_value = tuple(base_input.default_value)

    family = material_family(mat)

    # Find only nodes previously generated by this PBR pass; leave the
    # model's authored material graph intact.
    old_albedo = [n for n in nodes if n.name.startswith("PBR Albedo - ")]
    old_roughness = [n for n in nodes if n.name.startswith("PBR Roughness - ")]
    old_height = [n for n in nodes if n.name.startswith("PBR Height - ")]
    old_bumps = []
    for node in nodes:
        if node.type != "BUMP":
            continue
        if any(link.from_node in old_height for link in node.inputs["Height"].links):
            old_bumps.append(node)

    for node in old_bumps + old_albedo + old_roughness + old_height:
        if node.name in nodes:
            nodes.remove(node)

    for link in list(base_input.links):
        links.remove(link)

    tex_albedo = image_node(nodes, MAPS[family]["albedo"], "PBR Albedo - " + family)
    tex_albedo.location = (-760, 220)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.name = "PBR Generated - Albedo Mix"
    multiply.label = "PBR Generated - Albedo Mix"
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.0
    multiply.location = (-350, 220)
    if original_source:
        links.new(original_source, multiply.inputs[1])
    else:
        multiply.inputs[1].default_value = original_value
    links.new(tex_albedo.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], base_input)

    tex_rough = image_node(nodes, MAPS[family]["roughness"], "PBR Roughness - " + family, True)
    tex_rough.location = (-620, -40)
    rough = principled.inputs.get("Roughness")
    if rough and not rough.is_linked:
        links.new(tex_rough.outputs["Color"], rough)

    tex_height = image_node(nodes, MAPS[family]["height"], "PBR Height - " + family, True)
    tex_height.location = (-620, -300)
    bump = nodes.new("ShaderNodeBump")
    bump.name = "PBR Generated - Height Bump"
    bump.label = "PBR Generated - Height Bump"
    bump.inputs["Strength"].default_value = .24
    bump.inputs["Distance"].default_value = .035
    bump.location = (-300, -240)
    links.new(tex_height.outputs["Color"], bump.inputs["Height"])
    normal = principled.inputs.get("Normal")
    if normal and not normal.is_linked:
        links.new(bump.outputs["Normal"], normal)

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
if "/equipment/" in blend.replace("\\", "/"):
    print("Skipping excluded category:", blend, flush=True)
    raise SystemExit(0)
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
