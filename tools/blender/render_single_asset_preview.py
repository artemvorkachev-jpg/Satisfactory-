import bpy
import math
import os
from mathutils import Vector

# Render one review sheet per *_four_variants.blend file.
# Run with: blender --background <file.blend> --python tools/blender/render_single_asset_preview.py
# The image shows all four blockouts in the same camera/light setup for comparison.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PREVIEW_DIR = os.path.join(ROOT_DIR, "assets", "models", "previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

blend_path = bpy.data.filepath
if not blend_path:
    raise RuntimeError("Open a .blend file before running the preview renderer.")

stem = os.path.splitext(os.path.basename(blend_path))[0]
if not stem.endswith("_four_variants"):
    raise RuntimeError("Preview renderer only accepts *_four_variants.blend files.")

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.image_settings.compression = 18
scene.render.filepath = os.path.join(PREVIEW_DIR, stem + "_preview.png")

# Dark neutral studio world.
if scene.world is None:
    scene.world = bpy.data.worlds.new("Preview World")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.018, 0.025, 0.032, 1)
bg.inputs["Strength"].default_value = 0.45

# Remove stale cameras/lights from a previous preview invocation.
for obj in list(scene.objects):
    if obj.type in {"CAMERA", "LIGHT"} and obj.name.startswith("PREVIEW_"):
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.context.view_layer.update()

# Calculate visible mesh bounds in world space; collision proxies are hidden from render.
points = []
for obj in scene.objects:
    if obj.type != "MESH" or obj.hide_render:
        continue
    for corner in obj.bound_box:
        points.append(obj.matrix_world @ Vector(corner))

if not points:
    raise RuntimeError("No renderable mesh objects found in this .blend.")

mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
center = (mins + maxs) * 0.5
extent = maxs - mins
span = max(extent.x, extent.y, extent.z, 1.0)
aspect = scene.render.resolution_x / scene.render.resolution_y
ortho_width = max(extent.x * 1.12, extent.z * aspect * 1.18, extent.y * 1.45, 2.0)

# Orthographic camera: all four alternatives remain comparable in one frame.
cam_data = bpy.data.cameras.new("PREVIEW_Camera")
cam_data.type = "ORTHO"
cam_data.ortho_scale = ortho_width
cam = bpy.data.objects.new("PREVIEW_Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = center + Vector((span * 0.10, -span * 2.25, span * 1.05))
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.lens = 50
cam_data.clip_start = 0.01
cam_data.clip_end = max(1000.0, span * 20)
scene.camera = cam

def area_light(name, offset, energy_factor, size_factor):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = max(500.0, span * span * energy_factor)
    data.shape = "DISK"
    data.size = max(1.0, span * size_factor)
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = center + Vector(offset) * span
    obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

area_light("PREVIEW_Key", ( -1.2, -1.5, 1.8), 38.0, 0.9)
area_light("PREVIEW_Fill", ( 1.8, -0.8, 0.8), 16.0, 1.1)
area_light("PREVIEW_Rim", ( 0.2, 1.5, 1.6), 28.0, 0.8)

# Add small A/B/C/D labels beneath each variant root.
roots = [o for o in scene.objects if o.type == "EMPTY" and o.get("variant")]
label_size = max(0.12, span * 0.035)
for root in roots:
    letter = str(root.get("variant", "?"))
    data = bpy.data.curves.new("PREVIEW_Label_" + letter, "FONT")
    data.body = letter
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = label_size
    data.extrude = 0
    label = bpy.data.objects.new("PREVIEW_Label_" + letter, data)
    scene.collection.objects.link(label)
    label.location = (root.location.x, mins.y - span * 0.045, mins.z - span * 0.06)
    label.rotation_euler = (math.radians(90), 0, 0)
    data.materials.append(bpy.data.materials.new("PREVIEW_Label_Material"))
    data.materials[0].diffuse_color = (0.95, 0.72, 0.20, 1)

# Clean studio render settings.
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.render.film_transparent = False

bpy.ops.render.render(write_still=True)
print("Rendered preview:", scene.render.filepath)
