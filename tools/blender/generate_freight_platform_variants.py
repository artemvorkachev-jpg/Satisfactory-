import bpy
import math
import os

# Original Satisfactory-inspired rail platform variants.
# A/B/C correspond to solid freight, fluid freight and empty platform families.
# D is an alternate modular concept, not a claimed canonical variant.
# Wiki envelope for Freight Platform: 34 m wide x 16 m long x 20 m high.
# Run: blender --background --python tools/blender/generate_freight_platform_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "freight_platform")
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
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
CYAN=mat("Status cyan",(.02,.42,.52),.25,.22,1.4)
GLASS=mat("Control glass",(.025,.16,.19),.45,.18)

def finish(o,name,material,bevel=.045):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.045,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def cyl(name,loc,radius,depth,material,rot=(0,0,0),parent=None,vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
                                        location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,min(.035,radius*.1))
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def track_and_platform(root):
    box("Platform foundation",(0,0,1.0),(31,15,.55),CONCRETE,.08,root)
    box("Track bed",(0,0,1.40),(6.0,16,.32),DARK,.035,root)
    for x in (-1.0,1.0):
        box("Rail",(x,0,1.68),(.18,16,.18),STEEL,.025,root)
    for y in range(-7,8):
        box("Rail sleeper",(0,y,1.55),(3.2,.22,.16),CONCRETE,.02,root)
    for x in (-14.8,14.8):
        for y in (-6.6,6.6):
            box("Platform support pier",(x,y,1.6),(.8,.8,2.0),DARK,.05,root)
    for x in (-14.4,14.4):
        box("Platform edge guard",(x,0,2.15),(.15,14.5,.65),YELLOW,.02,root)

def crane(root,style):
    if style=="solid":
        box("Crane portal beam",(0,0,10.5),(25,.8,.8),STEEL,.06,root)
        for x in (-11.5,11.5):
            box("Crane upright",(x,0,6.2),(.65,.65,8.6),DARK,.05,root)
        box("Crane trolley",(0,0,9.9),(3.2,2.0,1.0),AMBER,.08,root)
        for x in (-.8,.8):
            box("Lifting cable",(x,0,7.5),(.07,.07,4.0),DARK,.01,root)
        box("Cargo spreader",(0,0,5.4),(5.4,2.8,.30),STEEL,.05,root)
    elif style=="fluid":
        box("Pipe gantry beam",(0,0,8.6),(24,.65,.65),STEEL,.05,root)
        for x in (-11.5,11.5):
            box("Gantry upright",(x,0,5.3),(.60,.60,6.8),DARK,.04,root)
        for x in (-2.5,-.8,.8,2.5):
            cyl("Flexible transfer hose",(x,0,5.2),.12,4.8,DARK,parent=root)
            cyl("Hose coupling",(x,0,2.7),.19,.25,YELLOW,parent=root)
    elif style=="empty":
        # Empty platform has no transfer crane or transfer ports.
        box("Empty platform canopy",(0,0,6.5),(18,1.0,.18),DARK,.03,root)
        for x in (-8.5,8.5):
            box("Canopy post",(x,0,4.4),(.22,.22,4.2),STEEL,.025,root)
    else:
        box("Modular crane bridge",(0,0,9.5),(24,.7,.7),AMBER,.05,root)
        for x in (-11,11):
            box("Modular crane column",(x,0,5.7),(.55,.55,7.4),STEEL,.035,root)
        box("Service trolley",(0,0,8.9),(2.8,1.8,.9),DARK,.05,root)
        box("Lift frame",(0,0,5.8),(4.8,2.2,.25),YELLOW,.03,root)

def connection_modules(root,style):
    if style=="solid":
        for x in (-10.8,10.8):
            box("Conveyor port housing",(x,-5.6,2.8),(2.2,1.4,1.7),DARK,.06,root)
            box("Conveyor inlet face",(x,-6.35,2.8),(1.2,.05,.9),AMBER,.025,root)
            box("Conveyor status light",(x,-6.40,3.45),(.45,.025,.12),CYAN,.01,root)
        for x in (-9.5,9.5):
            box("Control pedestal",(x,5.6,2.9),(.75,.65,1.4),STEEL,.04,root)
            box("Control panel",(x,5.95,3.0),(.45,.04,.55),GLASS,.012,root)
    elif style=="fluid":
        for x in (-10.5,-7.0,7.0,10.5):
            cyl("Pipeline riser",(x,-5.2,2.8),.25,2.0,STEEL,parent=root)
            cyl("Pipeline flange",(x,-5.2,3.8),.38,.15,YELLOW,parent=root)
        box("Fluid manifold",(0,-5.2,3.2),(8.0,.55,.55),DARK,.04,root)
        for x in (-2.4,-.8,.8,2.4):
            cyl("Fluid connection port",(x,-5.55,3.2),.22,.25,STEEL,(math.pi/2,0,0),root)
    elif style=="empty":
        for x in (-10.0,10.0):
            box("Blank service pedestal",(x,5.3,2.4),(.8,.8,1.0),DARK,.04,root)
    else:
        for x in (-10.5,-7.0,7.0,10.5):
            box("Universal connection housing",(x,-5.5,2.8),(1.4,1.2,1.6),STEEL,.05,root)
            box("Connection status panel",(x,-6.14,3.1),(.65,.025,.30),CYAN,.01,root)

def build(letter,label,style):
    r=root_empty("FreightPlatform_Variant_"+letter+"_"+label)
    track_and_platform(r)
    crane(r,style)
    connection_modules(r,style)
    box("Platform warning line",(0,-7.1,2.0),(27,.10,.08),YELLOW,.01,r)
    box("Platform ID plate",(0,6.95,2.8),(2.0,.08,.55),DARK,.02,r)
    r["asset_id"]="building-freight-platform" if style=="solid" else ("building-fluid-freight-platform" if style=="fluid" else "building-empty-platform")
    r["variant"]=letter
    r["gameplay_reference"]="Rail loading module; solid version uses conveyor ports and a crane, fluid version uses pipeline ports and a tank transfer assembly, empty platform spaces train cars."
    r["target_dimensions_m"]="34 m wide x 16 m long x 20 m high for freight platform family; verify exact footprint and height per variant."
    r["design_note"]="A/B/C are the corresponding canonical platform families; D is an optional modular design concept."
    return r

variants=[
    ("A","Solid_Freight_Platform","solid"),
    ("B","Fluid_Freight_Platform","fluid"),
    ("C","Empty_Platform","empty"),
    ("D","Universal_Modular_Platform_Concept","modular"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,10))
    c=bpy.context.object; c.name="COLLIDER_FreightPlatform"; c.dimensions=(34,16,20)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="rail_platform_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"freight_platform_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*38.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"freight_platform_four_variants.blend"))
print("Created four original Freight Platform blockout variants:",OUT_DIR)
