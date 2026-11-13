import bpy
import math
import os

# Original Satisfactory-inspired Electric Locomotive blockout variants.
# Verified wiki envelope: 6 m wide x 16 m long x 6 m high.
# The geometry is independently designed; no original game mesh is extracted.
# Run: blender --background --python tools/blender/generate_locomotive_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "locomotive")
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
GLASS=mat("Cab glazing",(.025,.16,.19),.45,.18)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.5)
RUBBER=mat("Wheel contact rubber",(.018,.022,.025),.02,.78)

def finish(o,name,material,bevel=.05):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.05,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def cyl(name,loc,radius,depth,material,rot=(0,0,0),parent=None,vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
                                        location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,min(.04,radius*.1))
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def bogie(root,y):
    box("Bogie frame",(0,y,1.05),(4.4,3.1,.42),DARK,.08,root)
    for axle_y in (y-1.0,y+1.0):
        for x in (-2.15,2.15):
            cyl("Rail wheel",(x,axle_y,.75),.62,.42,STEEL,(0,math.pi/2,0),root,40)
            cyl("Wheel hub",(x*1.01,axle_y,.75),.28,.44,AMBER,(0,math.pi/2,0),root,32)
            cyl("Hub center",(x*1.02,axle_y,.75),.10,.46,DARK,(0,math.pi/2,0),root,24)

def chassis(root):
    box("Locomotive underframe",(0,0,1.55),(5.1,14.8,.72),DARK,.12,root)
    for x in (-2.25,2.25):
        box("Longitudinal frame rail",(x,0,1.62),(.20,14.4,.45),STEEL,.035,root)
    bogie(root,-5.1)
    bogie(root,5.1)
    box("Front buffer beam",(0,-7.65,1.55),(5.4,.28,.45),STEEL,.05,root)
    box("Rear buffer beam",(0,7.65,1.55),(5.4,.28,.45),STEEL,.05,root)
    for y in (-7.85,7.85):
        cyl("Coupler body",(0,y,1.55),.22,.42,DARK,(math.pi/2,0,0),root)
        box("Coupler head",(0,y*1.03,1.55),(.42,.22,.28),STEEL,.035,root)

def motor_banks(root,style):
    for side in (-1,1):
        for i in range(3):
            y=1.0+i*1.65
            if style=="exposed":
                cyl("Traction motor",(side*2.38,y,2.0),.42,1.0,AMBER,(0,math.pi/2,0),root,32)
                cyl("Motor cap",(side*2.92,y,2.0),.25,.10,STEEL,(0,math.pi/2,0),root,24)
            else:
                box("Traction motor housing",(side*2.35,y,2.0),(.48,1.18,.75),DARK,.06,root)
                box("Motor access panel",(side*2.61,y,2.0),(.06,.66,.36),AMBER,.02,root)
                cyl("Cooling fan hub",(side*2.66,y,2.0),.13,.08,STEEL,(0,math.pi/2,0),root,24)

def cab(root,style):
    if style=="classic":
        box("Front cab shell",(0,-4.55,3.25),(4.8,4.2,2.7),AMBER,.16,root)
        box("Front windshield",(0,-6.68,3.55),(4.05,.05,1.35),GLASS,.06,root)
        for x in (-2.34,2.34):
            box("Side cab window",(x,-4.5,3.55),(.05,3.35,1.30),GLASS,.035,root)
    elif style=="armored":
        box("Armored front cab",(0,-4.6,3.22),(5.0,4.1,2.55),DARK,.12,root)
        box("Amber roof fairing",(0,-4.6,4.65),(5.1,4.2,.25),AMBER,.06,root)
        box("Panoramic windshield",(0,-6.67,3.55),(4.1,.05,1.18),GLASS,.05,root)
        for x in (-2.45,2.45):
            box("Side window",(x,-4.55,3.55),(.05,3.15,1.10),GLASS,.035,root)
    elif style=="dual":
        box("Front cab shell",(0,-4.85,3.20),(4.7,3.8,2.5),AMBER,.13,root)
        box("Rear control cab",(0,4.85,3.20),(4.7,3.8,2.5),DARK,.13,root)
        for y in (-6.75,6.75):
            box("Cab windshield",(0,y,3.50),(4.0,.05,1.15),GLASS,.05,root)
    else:
        box("Service cab lower",(0,-4.55,3.10),(4.6,4.0,2.35),STEEL,.10,root)
        box("Upper equipment pod",(0,-4.55,4.45),(4.9,4.0,.25),AMBER,.05,root)
        box("Front glass",(0,-6.58,3.48),(3.9,.05,1.10),GLASS,.04,root)
        for x in (-2.3,2.3):
            box("Side glass",(x,-4.55,3.48),(.05,3.1,1.05),GLASS,.035,root)
    for x in (-1.75,1.75):
        box("Headlight housing",(x,-6.85,2.25),(.55,.12,.30),DARK,.035,root)
        box("Headlight lens",(x,-6.92,2.25),(.40,.025,.18),CYAN,.015,root)
        box("Cab mirror arm",(x*1.25,-5.8,3.85),(.08,.50,.08),STEEL,.015,root)
        box("Cab mirror head",(x*1.28,-6.05,3.90),(.24,.12,.22),DARK,.025,root)
    box("Roof service rail",(0,-4.3,4.82),(1.25,.16,.10),YELLOW,.025,root)
    box("Side identification plate",(2.55,-2.2,3.0),(.035,1.0,.24),YELLOW,.01,root)

def build(letter,label,style):
    r=root_empty("ElectricLocomotive_Variant_"+letter+"_"+label)
    chassis(r)
    motor_banks(r,"exposed" if style=="exposed" else "covered")
    cab(r,style)
    box("Roof equipment spine",(0,1.8,3.20),(2.1,5.2,.38),DARK,.06,r)
    for y in (0.2,1.8,3.4):
        box("Roof service hatch",(0,y,3.43),(1.2,.8,.05),STEEL,.015,r)
    r["asset_id"]="vehicle-electric-locomotive"
    r["variant"]=letter
    r["gameplay_reference"]="Powered railway locomotive; moves freight cars and can be manually driven or scheduled between stations."
    r["target_dimensions_m"]="6 m wide x 16 m long x 6 m high; wiki envelope, validate orientation and bogie spacing."
    r["design_note"]="Independent industrial rail vehicle concept; A is the reference-oriented single-cab option."
    return r

variants=[
    ("A","Single_Cab_Covered_Motors","classic"),
    ("B","Armored_Cab","armored"),
    ("C","Dual_Cab_Configuration","dual"),
    ("D","Exposed_Motor_Service","exposed"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,3))
    c=bpy.context.object; c.name="COLLIDER_ElectricLocomotive"; c.dimensions=(6,16,6)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="rail_vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"locomotive_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*18.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"locomotive_four_variants.blend"))
print("Created four original Electric Locomotive blockout variants:",OUT_DIR)
