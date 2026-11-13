import bpy, math, os
from mathutils import Vector

# Fast, consistent Workbench review sheet. Intended for headless preview generation.
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
PREVIEW=os.path.join(ROOT,"assets","models","previews")
os.makedirs(PREVIEW,exist_ok=True)
blend=bpy.data.filepath
if not blend: raise RuntimeError("Open a *_four_variants.blend file first.")
stem=os.path.splitext(os.path.basename(blend))[0]
if not stem.endswith("_four_variants"): raise RuntimeError("Expected *_four_variants.blend.")

scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=960
scene.render.resolution_y=540
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.render.image_settings.compression=18
scene.render.filepath=os.path.join(PREVIEW,stem+"_preview.png")
scene.display.shading.light="STUDIO"
scene.display.shading.studio_light="paint.sl"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.25
scene.display.shading.curvature_valley_factor=1.0
scene.display.shading.background_type="WORLD"
scene.display.shading.show_specular_highlight=True
scene.render.film_transparent=False

# Workbench uses material viewport colors and does not need EEVEE shader compilation.
points=[]
for obj in scene.objects:
    if obj.type!="MESH" or obj.hide_render: continue
    for corner in obj.bound_box: points.append(obj.matrix_world @ Vector(corner))
if not points: raise RuntimeError("No renderable mesh objects.")
mins=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
maxs=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
center=(mins+maxs)*.5
extent=maxs-mins
span=max(extent.x,extent.y,extent.z,1.0)
aspect=scene.render.resolution_x/scene.render.resolution_y
ortho=max(extent.x*1.12,extent.z*aspect*1.18,extent.y*1.45,2.0)
cam_data=bpy.data.cameras.new("Review_Camera");cam_data.type="ORTHO";cam_data.ortho_scale=ortho
cam=bpy.data.objects.new("Review_Camera",cam_data);scene.collection.objects.link(cam)
cam.location=center+Vector((span*.10,-span*2.25,span*1.05))
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
cam_data.clip_start=.01;cam_data.clip_end=max(1000.0,span*20);scene.camera=cam

roots=[o for o in scene.objects if o.type=="EMPTY" and o.get("variant")]
for root in roots:
    letter=str(root.get("variant","?"))
    data=bpy.data.curves.new("Review_Label_"+letter,"FONT")
    data.body=letter;data.align_x="CENTER";data.align_y="CENTER";data.size=max(.12,span*.035)
    label=bpy.data.objects.new("Review_Label_"+letter,data);scene.collection.objects.link(label)
    label.location=(root.location.x,mins.y-span*.045,mins.z-span*.06)
    label.rotation_euler=(math.radians(90),0,0)
    data.materials.append(bpy.data.materials.new("Review_Label_Material"))
    data.materials[0].diffuse_color=(.95,.72,.20,1)

bpy.ops.render.render(write_still=True)
print("Rendered Workbench preview:",scene.render.filepath,flush=True)
