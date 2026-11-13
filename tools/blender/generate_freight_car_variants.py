import bpy
import math
import os

# Original Satisfactory-inspired Freight Car blockout variants.
# Wiki envelope: 6 m wide x 16 m long x 6 m high.
# The loaded solid container and fluid tank are separate visual states.
# Run: blender --background --python tools/blender/generate_freight_car_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "freight_car")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name,color,metallic=0.0,roughness=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    return m

AMBER=mat("Industrial amber enamel",(.82,.29,.055),.48,.32)
DARK=mat("Graphite structural alloy",(.045,.06,.07),.82,.28)
STEEL=mat("Brushed service metal",(.34,.39,.41),.86,.25)
RUBBER=mat("Wheel contact rubber",(.018,.022,.025),.02,.78)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
GLASS=mat("Tank inspection glass",(.025,.16,.19),.45,.18)

def finish(o,name,material,bevel=.04):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL"); b.width=bevel; b.segments=3
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

def torus(name,loc,major,minor,material,rot=(0,0,0),parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,
                                     major_segments=40,minor_segments=10,
                                     location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,0)
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def bogie(root,y):
    box("Bogie frame",(0,y,1.0),(4.3,3.1,.40),DARK,.08,root)
    for axle_y in (y-1.0,y+1.0):
        for x in (-2.15,2.15):
            cyl("Rail wheel",(x,axle_y,.72),.60,.42,STEEL,(0,math.pi/2,0),root,40)
            cyl("Wheel hub",(x*1.01,axle_y,.72),.27,.44,AMBER,(0,math.pi/2,0),root,32)
            cyl("Hub center",(x*1.02,axle_y,.72),.10,.46,DARK,(0,math.pi/2,0),root,24)

def underframe(root):
    box("Freight underframe",(0,0,1.45),(5.0,14.8,.65),DARK,.10,root)
    for x in (-2.2,2.2):
        box("Longitudinal beam",(x,0,1.52),(.22,14.5,.42),STEEL,.035,root)
    for y in (-5.1,5.1):
        bogie(root,y)
    for y in (-7.75,7.75):
        cyl("Coupler body",(0,y,1.45),.22,.42,DARK,(math.pi/2,0,0),root)
        box("Coupler head",(0,y*1.02,1.45),(.42,.22,.28),STEEL,.035,root)
    for x in (-1.8,1.8):
        for y in (-3.6,-1.2,1.2,3.6):
            box("Container mounting pad",(x,y,1.92),(.35,.45,.16),YELLOW,.02,root)

def solid_container(root,style):
    if style=="standard":
        box("Freight container",(0,0,3.55),(4.7,13.0,3.05),AMBER,.10,root)
        for x in (-2.25,2.25):
            for y in range(-6,7,2):
                box("Container corrugation",(x,y,3.55),(.05,.08,2.72),STEEL,.012,root)
        box("Container end doors",(0,6.54,3.55),(4.55,.06,2.80),DARK,.025,root)
        for x in (-.75,0,.75):
            box("Door locking bar",(x,6.59,3.55),(.05,.04,2.35),STEEL,.01,root)
    else:
        box("Reinforced freight shell",(0,0,3.55),(4.8,13.0,3.10),DARK,.08,root)
        for x in (-2.38,2.38):
            box("Reinforced side rail",(x,0,3.55),(.08,13.1,3.0),STEEL,.025,root)
        for y in (-5.8,-3.0,0,3.0,5.8):
            box("Container rib",(0,y,3.55),(4.82,.12,3.1),AMBER,.025,root)
        box("Rear access door",(0,6.56,3.55),(4.5,.06,2.65),STEEL,.025,root)

def fluid_tank(root,style):
    if style=="cylindrical":
        cyl("Fluid tank body",(0,0,3.45),1.72,12.7,STEEL,(math.pi/2,0,0),root,56)
        cyl("Tank front cap",(0,-6.4,3.45),1.68,.12,AMBER,(math.pi/2,0,0),root,56)
        cyl("Tank rear cap",(0,6.4,3.45),1.68,.12,AMBER,(math.pi/2,0,0),root,56)
        for y in (-4.6,-2.2,2.2,4.6):
            box("Tank support saddle",(0,y,2.15),(4.2,.24,.28),DARK,.035,root)
        box("Top service walkway",(0,0,5.25),(2.0,11.8,.10),DARK,.02,root)
    else:
        # Alternative original tank concept, not a canonical shape claim.
        box("Tank skid frame",(0,0,2.2),(4.7,13.0,.42),DARK,.06,root)
        for x in (-1.35,1.35):
            cyl("Modular fluid vessel",(x,0,3.55),1.25,12.3,STEEL,(math.pi/2,0,0),root,48)
            cyl("Vessel end cap",(x,-6.2,3.55),1.20,.12,AMBER,(math.pi/2,0,0),root,48)
            cyl("Vessel rear cap",(x,6.2,3.55),1.20,.12,AMBER,(math.pi/2,0,0),root,48)
        box("Central maintenance walkway",(0,0,4.85),(.55,11.8,.12),DARK,.02,root)
    box("Tank service manifold",(0,6.58,2.35),(1.35,.18,.65),AMBER,.04,root)
    for x in (-.42,0,.42):
        cyl("Fluid coupling",(x,6.70,2.36),.12,.20,STEEL,(math.pi/2,0,0),root,24)
    box("Inspection gauge panel",(0,-6.55,2.55),(.65,.08,.42),DARK,.02,root)
    box("Gauge lens",(0,-6.60,2.55),(.34,.02,.20),GLASS,.01,root)

def build(letter,label,load_state):
    r=root_empty("FreightCar_Variant_"+letter+"_"+label)
    underframe(r)
    if load_state=="solid":
        solid_container(r,"standard")
    elif load_state=="reinforced":
        solid_container(r,"reinforced")
    elif load_state=="fluid":
        fluid_tank(r,"cylindrical")
    elif load_state=="modular-fluid":
        fluid_tank(r,"modular")
    r["asset_id"]="vehicle-freight-car"
    r["variant"]=letter
    r["gameplay_reference"]="Non-motorized rail car; supports solid cargo or fluid cargo as separate mutually exclusive load states."
    r["target_dimensions_m"]="6 m wide x 16 m long x 6 m high; wiki envelope, verify container and underframe bounds."
    r["design_note"]="A-D represent empty, solid-container, standard fluid-tank and alternate tank concept states."
    return r

variants=[
    ("A","Empty_Undercarriage","empty"),
    ("B","Solid_Cargo_Container","solid"),
    ("C","Fluid_Tank","fluid"),
    ("D","Modular_Fluid_Tank_Concept","modular-fluid"),
]
roots=[]
for letter,label,state in variants:
    r=build(letter,label,state)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,3))
    c=bpy.context.object; c.name="COLLIDER_FreightCar"; c.dimensions=(6,16,6)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="rail_vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"freight_car_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*18.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"freight_car_four_variants.blend"))
print("Created four original Freight Car blockout variants:",OUT_DIR)
