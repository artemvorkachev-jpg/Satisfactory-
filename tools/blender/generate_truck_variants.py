import bpy
import math
import os

# Original Satisfactory-inspired Truck / Fluid Truck blockout variants.
# Wiki envelope: approx. 6.5 m wide x 10.5 m long x 6 m high.
# Solid and fluid body forms are both represented; all geometry is independent.
# Run: blender --background --python tools/blender/generate_truck_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "truck")
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
RUBBER=mat("Heavy tire rubber",(.018,.022,.025),.02,.78)
GLASS=mat("Cab glazing",(.025,.16,.19),.45,.18)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.4)

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
    o=finish(bpy.context.object,name,material,min(.045,radius*.1))
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

def wheels(root):
    # Three axles; front steering axle and two rear axles.
    for y in (-3.25,0.0,3.25):
        for x in (-2.55,2.55):
            cyl("Heavy all-terrain tire",(x,y,.92),.82,.52,RUBBER,(0,math.pi/2,0),root,48)
            cyl("Wheel hub",(x*1.01,y,.92),.40,.55,STEEL,(0,math.pi/2,0),root,40)
            cyl("Hub cap",(x*1.02,y,.92),.18,.57,AMBER,(0,math.pi/2,0),root,24)
            for a in range(8):
                ang=2*math.pi*a/8
                uv("Wheel bolt",(x*1.03,y+math.cos(ang)*.28,.92+math.sin(ang)*.28),
                   (.035,.035,.035),YELLOW,root)

def chassis(root):
    box("Heavy ladder frame",(0,0,1.15),(4.6,8.8,.42),DARK,.10,root)
    for x in (-1.85,1.85):
        box("Longitudinal frame rail",(x,0,1.28),(.28,9.4,.42),STEEL,.06,root)
    for y in (-3.25,0,3.25):
        box("Axle housing",(0,y,.98),(5.1,.28,.26),DARK,.04,root)
    wheels(root)
    box("Front bumper",(0,-4.8,1.22),(5.8,.28,.42),STEEL,.06,root)
    box("Rear bumper",(0,4.8,1.22),(5.8,.28,.42),STEEL,.06,root)
    for x in (-2.15,2.15):
        box("Side step",(x,-1.6,1.52),(.55,1.35,.16),DARK,.035,root)

def cab(root,style):
    if style=="classic":
        box("Cab lower shell",(0,-3.10,2.42),(4.35,2.45,1.35),AMBER,.14,root)
        box("Cab roof",(0,-3.10,3.52),(4.55,2.55,.24),DARK,.08,root)
        box("Wide windshield",(0,-4.34,2.95),(3.75,.06,.86),GLASS,.035,root)
        for x in (-2.08,2.08):
            box("Side window",(x,-3.10,2.98),(.05,1.95,.82),GLASS,.025,root)
    elif style=="panoramic":
        box("Cab lower shell",(0,-3.10,2.35),(4.50,2.45,1.25),DARK,.18,root)
        box("Panoramic cab roof",(0,-3.10,3.45),(4.65,2.65,.22),AMBER,.08,root)
        box("Panoramic windshield",(0,-4.35,2.93),(4.05,.05,.92),GLASS,.08,root)
        for x in (-2.18,2.18):
            box("Side glass",(x,-3.08,2.90),(.05,2.0,.88),GLASS,.05,root)
    elif style=="open":
        for x in (-2.0,2.0):
            for y in (-4.25,-2.0):
                box("Cab frame post",(x,y,2.92),(.15,.15,1.35),STEEL,.025,root)
        box("Cab roof frame",(0,-3.12,3.60),(4.35,2.55,.16),DARK,.04,root)
        box("Front windshield",(0,-4.30,2.95),(3.8,.05,.80),GLASS,.025,root)
    else:
        box("Modular cab lower shell",(0,-3.10,2.38),(4.35,2.40,1.28),AMBER,.10,root)
        box("Armored roof module",(0,-3.10,3.48),(4.55,2.5,.25),STEEL,.06,root)
        box("Front glass",(0,-4.32,2.92),(3.8,.05,.82),GLASS,.03,root)
        for x in (-2.1,2.1):
            box("Side window",(x,-3.10,2.92),(.05,1.85,.78),GLASS,.025,root)
    # Front lights, mirrors and roof equipment.
    for x in (-1.72,1.72):
        box("Headlight housing",(x,-4.43,1.95),(.52,.12,.28),DARK,.04,root)
        box("Headlight lens",(x,-4.50,1.95),(.38,.025,.17),CYAN,.015,root)
        box("Mirror arm",(x*1.18,-3.55,2.88),(.08,.55,.08),STEEL,.02,root)
        box("Mirror head",(x*1.22,-3.82,2.95),(.26,.14,.24),DARK,.025,root)
    box("Roof service rail",(0,-3.0,3.78),(1.0,.15,.10),YELLOW,.025,root)

def solid_cargo(root,style):
    if style=="classic":
        box("Cargo bed",(0,1.60,2.02),(4.30,5.05,.55),DARK,.08,root)
        for x in (-2.05,2.05):
            box("Cargo side wall",(x,1.60,2.80),(.18,5.0,1.10),AMBER,.05,root)
        box("Tailgate",(0,4.08,2.80),(4.20,.18,1.10),STEEL,.04,root)
    else:
        box("Modular cargo platform",(0,1.60,2.0),(4.35,5.1,.48),STEEL,.06,root)
        for x in (-2.1,2.1):
            box("Modular side rail",(x,1.6,2.65),(.14,5.1,.95),DARK,.035,root)
        box("Rear access gate",(0,4.12,2.64),(4.2,.14,.95),AMBER,.035,root)
        for y in (-.2,1.3,2.8):
            box("Cargo tie rail",(0,y,2.28),(4.2,.08,.07),YELLOW,.012,root)

def fluid_tank(root,style):
    if style=="dual":
        for x in (-1.0,1.0):
            cyl("Fluid tank",(x,1.35,2.68),.90,4.8,STEEL,(math.pi/2,0,0),root,48)
            cyl("Tank end cap",(x,-1.08,2.68),.88,.10,AMBER,(math.pi/2,0,0),root,48)
            cyl("Tank rear cap",(x,3.78,2.68),.88,.10,AMBER,(math.pi/2,0,0),root,48)
            for y in (-.5,1.2,2.9):
                box("Tank support saddle",(x,y,1.98),(.30,.24,.25),DARK,.025,root)
    else:
        cyl("Single fluid tank",(0,1.45,2.75),1.35,5.0,STEEL,(math.pi/2,0,0),root,56)
        cyl("Front tank cap",(0,-1.08,2.75),1.32,.12,AMBER,(math.pi/2,0,0),root,56)
        cyl("Rear tank cap",(0,3.98,2.75),1.32,.12,AMBER,(math.pi/2,0,0),root,56)
        for y in (-.6,1.2,3.0):
            box("Tank support saddle",(0,y,1.70),(3.1,.25,.30),DARK,.035,root)
    box("Tank service walkway",(0,1.3,3.98),(3.2,4.7,.12),DARK,.025,root)
    box("Fluid connection panel",(0,4.10,2.4),(.85,.08,.55),YELLOW,.025,root)

def build(letter,label,cab_style,body_style):
    r=root_empty("Truck_Variant_"+letter+"_"+label)
    chassis(r)
    cab(r,cab_style)
    if body_style=="solid":
        solid_cargo(r,"classic" if letter=="A" else "modular")
    else:
        fluid_tank(r,"dual" if letter=="B" else "single")
    box("Rear access/service hatch",(2.25,3.7,1.85),(.05,.55,.40),STEEL,.02,r)
    box("Rear identification plate",(0,4.55,1.62),(.75,.025,.16),YELLOW,.01,r)
    r["asset_id"]="vehicle-truck" if body_style=="solid" else "vehicle-fluid-truck"
    r["variant"]=letter
    r["gameplay_reference"]="Six-wheel motor vehicle; solid cargo truck has 48 inventory slots; Fluid Truck uses twin cylindrical tanks and fluid stations."
    r["target_dimensions_m"]="6.5 m wide x 10.5 m long x 6 m high; provisional wiki envelope, confirm bounding box."
    r["design_note"]="A/B are canonical body types; C/D are alternate visual concepts for user review."
    return r

variants=[
    ("A","Solid_Cargo_Truck","classic","solid"),
    ("B","Fluid_Truck_Dual_Tank","panoramic","fluid"),
    ("C","Open_Frame_Cargo_Truck","open","solid"),
    ("D","Single_Tank_Service_Truck","modular","fluid"),
]
roots=[]
for letter,label,cab_style,body_style in variants:
    r=build(letter,label,cab_style,body_style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,3))
    c=bpy.context.object; c.name="COLLIDER_Truck"; c.dimensions=(6.5,10.5,6)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    export_name="truck_variant_"+letter.lower()
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,export_name+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots):
    r.location.x=(i-1.5)*12.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"truck_four_variants.blend"))
print("Created four original Truck / Fluid Truck blockout variants:",OUT_DIR)
