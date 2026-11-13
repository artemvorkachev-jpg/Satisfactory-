import bpy
import math
import os

# Original Satisfactory-inspired Explorer off-road vehicle blockout variants.
# The Wiki describes a compact, nimble, one-seat exploration vehicle.
# No verified dimensions are available in the reference page; envelope is provisional.
# Run: blender --background --python tools/blender/generate_explorer_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "explorer")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name,color,metallic=0.0,roughness=.4,emission=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value=(*color,1)
        bs.inputs["Emission Strength"].default_value=emission
    return m

AMBER=mat("Industrial amber enamel",(.82,.29,.055),.48,.32)
DARK=mat("Graphite structural alloy",(.045,.06,.07),.82,.28)
STEEL=mat("Brushed service metal",(.34,.39,.41),.86,.25)
RUBBER=mat("Off-road tire rubber",(.018,.022,.025),.02,.78)
GLASS=mat("Cab and sensor glass",(.025,.16,.19),.45,.18)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.5)

def finish(o,name,material,bevel=.035):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.035,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def cyl(name,loc,radius,depth,material,rot=(0,0,0),parent=None,vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
                                        location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,min(.03,radius*.1))
    if parent: o.parent=parent
    return o

def uv(name,loc,scale,material,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
    o=bpy.context.object; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,0)
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def wheel(root,x,y,radius=.48):
    cyl("Off-road tire",(x,y,radius),radius,.25,RUBBER,(0,math.pi/2,0),root,40)
    cyl("Wheel hub",(x*1.01,y,radius),radius*.48,.28,STEEL,(0,math.pi/2,0),root,32)
    cyl("Hub cap",(x*1.02,y,radius),radius*.20,.30,AMBER,(0,math.pi/2,0),root,24)
    for a in range(8):
        ang=2*math.pi*a/8
        uv("Hub bolt",(x*1.03,y+math.cos(ang)*radius*.32,radius+math.sin(ang)*radius*.32),
           (.022,.022,.022),YELLOW,root)

def chassis(root):
    box("Tubular chassis",(0,0,.70),(2.25,3.7,.22),DARK,.07,root)
    for x in (-.90,.90):
        box("Longitudinal frame rail",(x,0,.76),(.12,3.8,.22),STEEL,.025,root)
    for y in (-1.25,1.25):
        box("Axle crossmember",(0,y,.70),(2.2,.14,.18),STEEL,.025,root)
    for x in (-1.05,1.05):
        for y in (-1.35,1.35):
            wheel(root,x,y,.48)
            box("Suspension arm",(x*.75,y,.62),(.48,.14,.13),AMBER,.025,root)
    box("Front skid plate",(0,-1.85,.48),(1.95,.30,.13),STEEL,.03,root)
    box("Rear bumper",(0,1.88,.55),(2.0,.22,.20),DARK,.03,root)

def cabin(root,style):
    if style=="open":
        box("Floor pan",(0,-.05,.92),(1.75,2.0,.14),DARK,.03,root)
        for x in (-.83,.83):
            for y in (-.92,.82):
                box("Roll cage post",(x,y,1.70),(.09,.09,1.45),STEEL,.02,root)
        box("Roll cage roof",(0,-.05,2.42),(1.82,1.95,.10),DARK,.025,root)
        box("Front windscreen",(0,-1.02,1.82),(1.48,.04,.66),GLASS,.025,root)
    elif style=="shell":
        box("Lower cabin shell",(0,-.08,1.25),(1.95,2.05,.68),AMBER,.12,root)
        box("Roof canopy",(0,-.05,2.20),(1.98,1.95,.18),DARK,.07,root)
        box("Front windshield",(0,-1.12,1.80),(1.65,.05,.60),GLASS,.05,root)
        for x in (-.93,.93):
            box("Side window",(x,-.05,1.83),(.04,1.52,.56),GLASS,.04,root)
    elif style=="armored":
        box("Armored tub",(0,-.05,1.23),(2.05,2.05,.75),DARK,.12,root)
        box("Amber upper shell",(0,-.08,1.70),(1.92,1.72,.28),AMBER,.07,root)
        box("Panoramic glass",(0,-1.12,1.90),(1.60,.05,.52),GLASS,.05,root)
        for x in (-.96,.96):
            box("Side armor plate",(x,-.05,1.38),(.08,1.55,.40),STEEL,.025,root)
    else:
        box("Central cockpit pod",(0,-.05,1.30),(1.82,1.85,.72),AMBER,.16,root)
        box("Upper cockpit frame",(0,-.05,1.90),(1.85,1.72,.18),STEEL,.06,root)
        box("Front visor",(0,-1.0,1.80),(1.52,.05,.56),GLASS,.04,root)
        for x in (-.88,.88):
            box("Side glazing",(x,-.02,1.72),(.04,1.2,.48),GLASS,.035,root)

def equipment(root,style):
    # Single-seat interior; rear service/storage hatch is a visible separate part.
    box("Driver seat base",(0,.10,1.08),(.68,.72,.18),DARK,.04,root)
    box("Driver seat back",(0,.42,1.50),(.72,.18,.82),RUBBER,.07,root)
    box("Dashboard",(0,-.72,1.58),(1.30,.22,.22),DARK,.04,root)
    box("Dashboard display",(0,-.85,1.60),(.46,.025,.12),GLASS,.01,root)
    cyl("Steering column",(0,-.56,1.38),.06,.35,STEEL,(math.pi/2,0,0),root)
    torus=None
    # Rear storage/workbench hatch.
    box("Rear storage hatch",(0,1.22,1.28),(1.12,.10,.48),STEEL,.025,root)
    box("Rear hatch handle",(0,1.29,1.28),(.24,.04,.07),YELLOW,.01,root)
    if style=="sensor":
        for x in (-.50,.50):
            box("Sensor pod",(x,-.92,2.08),(.18,.20,.18),DARK,.025,root)
            uv("Sensor lens",(x,-1.03,2.08),(.055,.025,.055),CYAN,root)
    for x in (-.72,.72):
        box("Headlight housing",(x,-1.82,1.05),(.30,.10,.16),DARK,.025,root)
        box("Headlight lens",(x,-1.88,1.05),(.20,.025,.09),CYAN,.01,root)
        box("Mirror stem",(x*1.12,-.78,1.95),(.05,.32,.05),STEEL,.012,root)
        box("Mirror head",(x*1.18,-.96,2.0),(.16,.08,.13),DARK,.02,root)

def build(letter,label,style):
    r=root_empty("Explorer_Variant_"+letter+"_"+label)
    chassis(r)
    cabin(r,style)
    equipment(r,style)
    r["asset_id"]="vehicle-explorer"
    r["variant"]=letter
    r["gameplay_reference"]="Fast, nimble off-road exploration vehicle; 12 inventory slots and built-in Craft Bench."
    r["target_dimensions_m"]="Unverified; provisional 4.2 x 4.8 x 2.8 m envelope for scale blockout only."
    r["design_note"]="Original one-seat exploration buggy concept; compare against in-game reference before approval."
    return r

variants=[
    ("A","Open_Roll_Cage","open"),
    ("B","Enclosed_Explorer","shell"),
    ("C","Armored_Terrain_Pod","armored"),
    ("D","Sensor_Equipped_Cockpit","sensor"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.4))
    c=bpy.context.object; c.name="COLLIDER_Explorer"; c.dimensions=(4.2,4.8,2.8)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"explorer_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*5.5
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"explorer_four_variants.blend"))
print("Created four original Explorer blockout variants:",OUT_DIR)
