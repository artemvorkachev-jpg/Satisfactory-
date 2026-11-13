import bpy
import math
import os

# Original Satisfactory-inspired Train Station building blockout variants.
# Wiki envelope: 34 m wide x 16 m long x 20 m high.
# Includes its own rail segment, support frame, roof and service/control module.
# Run: blender --background --python tools/blender/generate_train_station_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "train_station")
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
CONCRETE=mat("Industrial concrete",(.30,.32,.31),.05,.82)
GLASS=mat("Control room glass",(.025,.16,.19),.45,.18)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Status cyan",(.02,.42,.52),.25,.22,1.4)

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

def track(root):
    box("Track bed",(0,0,.55),(6.0,16.0,.35),DARK,.04,root)
    for x in (-1.0,1.0):
        box("Rail",(x,0,.86),(.18,16.0,.18),STEEL,.025,root)
    for y in range(-7,8):
        box("Sleeper",(0,y,.68),(3.2,.24,.18),CONCRETE,.025,root)
    for x in (-2.6,2.6):
        box("Track edge guard",(x,0,.95),(.12,16,.18),YELLOW,.02,root)

def support_frame(root,style):
    if style=="portal":
        for x in (-14,14):
            for y in (-6.5,6.5):
                box("Main support column",(x,y,8.8),(.9,.9,15.8),DARK,.06,root)
                box("Column safety band",(x,y,2.0),(1.0,1.0,.18),YELLOW,.02,root)
        for y in (-6.5,6.5):
            box("Roof cross beam",(0,y,16.4),(29,.85,.85),STEEL,.06,root)
    elif style=="cantilever":
        for x in (-13,13):
            for y in (-6.4,6.4):
                box("Heavy support pier",(x,y,7.6),(1.2,1.2,14.0),STEEL,.08,root)
        box("Cantilever roof spine",(0,0,15.2),(30,1.0,1.0),DARK,.08,root)
        for x in (-10,-5,0,5,10):
            box("Cantilever arm",(x,0,15.2),(.32,15,.32),AMBER,.025,root)
    elif style=="open":
        for x in (-14,14):
            for y in (-6.5,6.5):
                box("Open frame post",(x,y,8.0),(.55,.55,14.8),STEEL,.035,root)
        for z in (12.5,15.8):
            for y in (-6.5,6.5):
                box("Open truss beam",(0,y,z),(28,.45,.45),DARK,.025,root)
        for x in range(-12,13,4):
            box("Roof truss rib",(x,0,15.8),(.30,13,.30),AMBER,.025,root)
    else:
        for x in (-13,13):
            for y in (-6.5,6.5):
                box("Enclosed hall column",(x,y,8.5),(.75,.75,15.2),DARK,.05,root)
        box("Roof shell",(0,0,16.0),(27,14.0,.65),AMBER,.10,root)
        for x in (-8,8):
            box("Side cladding",(x,0,8.0),(.20,12.8,13.5),STEEL,.04,root)

def station_building(root,style):
    box("Raised service platform",(0,0,1.25),(25,14,.45),CONCRETE,.08,root)
    box("Platform edge marking",(0,-6.95,1.52),(24,.10,.10),YELLOW,.015,root)
    box("Control module",(0,-4.6,5.0),(7.2,3.6,6.2),AMBER,.10,root)
    box("Control room glazing",(0,-6.43,5.6),(5.6,.05,2.7),GLASS,.04,root)
    box("Station name display",(0,-6.48,7.25),(3.8,.08,.45),DARK,.025,root)
    box("Name display lens",(0,-6.54,7.25),(3.1,.025,.22),CYAN,.01,root)
    for x in (-2.2,2.2):
        box("Service door",(x,-6.45,3.8),(1.0,.06,2.1),DARK,.025,root)
    box("Power connection housing",(10,-4.5,2.2),(1.6,1.4,1.5),STEEL,.05,root)
    box("Power status panel",(10,-5.25,2.35),(.9,.05,.45),GLASS,.015,root)
    for x in (-10,10):
        box("Platform light mast",(x,-5.8,9.0),(.18,.18,14.0),DARK,.02,root)
        box("Light head",(x,-5.8,16.1),(1.1,.5,.35),STEEL,.035,root)
        box("Light lens",(x,-6.08,16.1),(.75,.025,.18),CYAN,.012,root)
    box("Platform service canopy",(0,-5.8,9.0),(17,1.0,.22),STEEL,.04,root)

def build(letter,label,style):
    r=root_empty("TrainStation_Variant_"+letter+"_"+label)
    track(r)
    support_frame(r,style)
    station_building(r,style)
    box("Arrival direction arrow",(0,6.8,1.6),(2.2,.10,.18),YELLOW,.02,r)
    r["asset_id"]="building-train-station"
    r["variant"]=letter
    r["gameplay_reference"]="Rail hub with integrated track; names station, powers connected rail network, and docks trains on a timetable."
    r["target_dimensions_m"]="34 m wide x 16 m long x 20 m high; wiki envelope, verify included track/roof orientation."
    r["design_note"]="Original station architecture variants; A is a portal-frame reference direction."
    return r

variants=[
    ("A","Portal_Frame_Canopy","portal"),
    ("B","Cantilever_Service_Hall","cantilever"),
    ("C","Open_Industrial_Truss","open"),
    ("D","Enclosed_Modular_Hall","enclosed"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,10))
    c=bpy.context.object; c.name="COLLIDER_TrainStation"; c.dimensions=(34,16,20)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="station_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"train_station_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*38.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"train_station_four_variants.blend"))
print("Created four original Train Station blockout variants:",OUT_DIR)
