import bpy
import math
import os

# Original Satisfactory-inspired Tractor blockout variants.
# Wiki envelope: approximately 4 m wide x 5 m long x 3.5 m high.
# Geometry is independently authored; final dimensions must be checked against
# the in-game vehicle and common road/turning-clearance references.
# Run: blender --background --python tools/blender/generate_tractor_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "tractor")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.4, emission=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
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
RUBBER=mat("Tire rubber",(.018,.022,.025),.02,.78)
GLASS=mat("Cab glazing",(.025,.16,.19),.45,.18)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.4)

def finish(o,name,material,bevel=.04):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL")
        b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.04,parent=None):
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
    r=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(r)
    return r

def wheel(root,x,y):
    # Wheel axle axis is X.
    cyl("All-terrain tire",(x,y,.62),.52,.32,RUBBER,(0,math.pi/2,0),root,48)
    cyl("Wheel hub",(x*1.02,y,.62),.26,.34,STEEL,(0,math.pi/2,0),root,32)
    cyl("Hub cap",(x*1.03,y,.62),.12,.36,AMBER,(0,math.pi/2,0),root,24)
    torus=None

def chassis(root):
    box("Ladder chassis",(0,0,1.0),(2.8,4.4,.30),DARK,.08,root)
    box("Front bumper",(0,-2.25,.92),(3.2,.22,.24),STEEL,.04,root)
    box("Rear bumper",(0,2.25,.92),(3.2,.22,.24),STEEL,.04,root)
    for x in (-1.45,1.45):
        for y in (-1.55,1.55):
            wheel(root,x,y)
    box("Lower engine cover",(0,-1.45,1.35),(2.55,1.15,.55),AMBER,.10,root)
    box("Rear cargo body",(0,1.15,1.65),(2.55,1.75,.92),DARK,.08,root)
    box("Rear cargo hatch",(0,2.05,1.66),(2.25,.06,.62),STEEL,.025,root)
    box("Rear access handle",(0,2.10,1.66),(.48,.05,.08),YELLOW,.012,root)
    for x in (-1.05,1.05):
        box("Cargo side rail",(x,1.15,2.12),(.12,1.85,.12),AMBER,.025,root)

def cabin(root,style):
    if style=="square":
        box("Cabin lower shell",(0,-.72,2.10),(2.35,1.65,.82),AMBER,.08,root)
        box("Windshield frame",(0,-1.58,2.64),(2.25,.12,.90),DARK,.04,root)
        box("Windshield glass",(0,-1.65,2.66),(1.95,.035,.66),GLASS,.025,root)
        for x in (-1.05,1.05):
            box("Cab side window",(x,-.72,2.66),(.04,1.35,.62),GLASS,.02,root)
    elif style=="rounded":
        box("Cabin shell",(0,-.70,2.12),(2.45,1.75,.90),AMBER,.20,root)
        box("Panoramic windshield",(0,-1.60,2.66),(2.18,.045,.72),GLASS,.12,root)
        for x in (-1.18,1.18):
            box("Side glazing",(x,-.72,2.65),(.04,1.35,.66),GLASS,.08,root)
    elif style=="open":
        for x in (-1.05,1.05):
            for y in (-1.50,.10):
                box("Cabin support post",(x,y,2.55),(.12,.12,1.10),STEEL,.02,root)
        box("Cabin roof frame",(0,-.70,3.08),(2.30,1.80,.14),DARK,.035,root)
        box("Windshield panel",(0,-1.56,2.63),(1.95,.04,.66),GLASS,.02,root)
    else:
        box("Modular cabin shell",(0,-.70,2.13),(2.38,1.70,.86),DARK,.10,root)
        box("Upper cabin armor",(0,-.70,2.70),(2.50,1.80,.18),AMBER,.06,root)
        box("Wide windshield",(0,-1.58,2.62),(2.05,.04,.60),GLASS,.03,root)
        for x in (-1.18,1.18):
            box("Side window",(x,-.72,2.62),(.04,1.30,.56),GLASS,.025,root)
    # Roof equipment and lights.
    box("Roof service rail",(0,-.70,3.10),(.75,.12,.08),STEEL,.02,root)
    for x in (-.88,.88):
        box("Headlight housing",(x,-1.66,1.75),(.30,.10,.18),DARK,.025,root)
        box("Headlight lens",(x,-1.72,1.75),(.22,.025,.11),CYAN,.012,root)
        box("Mirror arm",(x*1.2,-1.15,2.50),(.06,.36,.06),STEEL,.012,root)
        box("Mirror head",(x*1.22,-1.34,2.54),(.18,.10,.20),DARK,.025,root)
    box("FICSIT-style identification plate",(0,-1.70,1.40),(.58,.025,.14),YELLOW,.01,root)

def build(letter,label,style):
    r=root_empty("Tractor_Variant_"+letter+"_"+label)
    chassis(r)
    cabin(r,style)
    # Fuel/service access is represented as a visual panel only.
    box("Rear service access panel",(1.34,1.85,1.55),(.04,.38,.36),STEEL,.018,r)
    box("Fuel/service hatch",(1.37,1.85,1.55),(.025,.22,.22),AMBER,.012,r)
    box("Side step",(1.35,-.55,1.18),(.48,.58,.10),DARK,.02,r)
    r["asset_id"]="vehicle-tractor"
    r["variant"]=letter
    r["gameplay_reference"]="Small off-road cargo vehicle; 25 inventory slots, built-in crafting bench, player-driven or automated route."
    r["target_dimensions_m"]="4 m wide x 5 m long x 3.5 m high; provisional envelope from wiki, verify orientation and final bounding box."
    r["design_note"]="Original geometry; compare A-D against current in-game reference before approval."
    return r

variants=[
    ("A","Square_Cab_Sugarcube","square"),
    ("B","Rounded_Panoramic_Cab","rounded"),
    ("C","Open_Service_Cage","open"),
    ("D","Modular_Industrial_Cab","modular"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.55))
    c=bpy.context.object; c.name="COLLIDER_Tractor"; c.dimensions=(4,5,3.5)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"tractor_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots):
    r.location.x=(i-1.5)*6.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"tractor_four_variants.blend"))
print("Created four original Tractor blockout variants:",OUT_DIR)
