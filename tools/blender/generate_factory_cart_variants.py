import bpy
import math
import os

# Original Satisfactory-inspired Factory Cart variants.
# A/B are standard and golden finish variants; C/D are concept options.
# Cart is a small hand-slot vehicle; dimensions are provisional.
# Run: blender --background --python tools/blender/generate_factory_cart_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "factory_cart")
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

WHITE=mat("FICSIT cart enamel",(.78,.80,.76),.3,.28)
GOLD=mat("Golden cart finish",(.83,.56,.12),.78,.2)
DARK=mat("Graphite chassis",(.035,.045,.05),.82,.28)
STEEL=mat("Brushed metal",(.34,.39,.41),.84,.25)
RUBBER=mat("Grip wheel rubber",(.018,.022,.025),.02,.78)
GLASS=mat("Smoked windshield",(.025,.16,.19),.45,.18)
RED=mat("Siren red",(.7,.025,.018),.2,.22,1.3)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.3)

def finish(o,name,material,bevel=.025):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radius","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.025,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def cyl(name,loc,radius,depth,material,rot=(0,0,0),parent=None,vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
                                        location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,min(.02,radius*.1))
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def wheel(root,x,y):
    cyl("Grip wheel",(x,y,.36),.32,.15,RUBBER,(0,math.pi/2,0),root,32)
    cyl("Wheel hub",(x*1.02,y,.36),.15,.17,STEEL,(0,math.pi/2,0),root,24)
    cyl("Hub cap",(x*1.03,y,.36),.07,.18,GOLD if root.get("variant")=="B" else WHITE,(0,math.pi/2,0),root,20)

def base(root,finish_mat,style):
    box("Lower chassis",(0,0,.62),(1.55,2.15,.20),DARK,.045,root)
    for x in (-.68,.68):
        for y in (-.72,.72):
            wheel(root,x,y)
    box("Front bumper",(0,-1.08,.58),(1.75,.15,.20),STEEL,.025,root)
    box("Rear bumper",(0,1.08,.58),(1.75,.15,.20),STEEL,.025,root)
    if style=="classic":
        box("Cart body",(0,0,.90),(1.55,1.85,.50),finish_mat,.10,root)
        box("Front dashboard",(0,-.72,1.22),(1.38,.22,.26),DARK,.035,root)
    elif style=="gold":
        box("Gold cart body",(0,0,.92),(1.58,1.90,.52),finish_mat,.12,root)
        box("Gold front fascia",(0,-.98,.92),(1.45,.08,.25),GOLD,.025,root)
        box("Gold dashboard",(0,-.72,1.24),(1.40,.20,.24),DARK,.035,root)
    elif style=="utility":
        box("Utility frame",(0,0,.85),(1.48,1.95,.36),DARK,.06,root)
        box("Upper body panel",(0,.10,1.12),(1.42,1.30,.18),finish_mat,.04,root)
        box("Front fascia",(0,-.82,1.08),(1.40,.10,.22),STEEL,.025,root)
    else:
        box("Low-profile shell",(0,0,.88),(1.62,2.0,.48),finish_mat,.14,root)
        box("Front fascia",(0,-.98,.90),(1.50,.08,.24),DARK,.03,root)

def cabin(root,style):
    box("Driver seat base",(0,.12,1.18),(.62,.62,.12),DARK,.025,root)
    box("Driver seat back",(0,.40,1.50),(.64,.14,.56),RUBBER,.05,root)
    box("Steering column",(0,-.48,1.30),(.08,.08,.42),STEEL,.015,root)
    box("Steering wheel",(0,-.55,1.52),(.48,.08,.07),DARK,.025,root)
    if style in ("classic","gold"):
        for x in (-.70,.70):
            box("Windshield support",(x,-.82,1.72),(.06,.06,.66),STEEL,.012,root)
        box("Folded windshield",(0,-.84,1.88),(1.30,.04,.48),GLASS,.025,root)
        box("Roof support crossbar",(0,-.12,2.12),(1.45,.08,.08),DARK,.02,root)
    elif style=="utility":
        for x in (-.70,.70):
            box("Safety rail",(x,0,1.55),(.06,1.30,.06),STEEL,.012,root)
    else:
        box("Low wind deflector",(0,-.88,1.52),(1.35,.05,.22),GLASS,.025,root)
    for x in (-.55,.55):
        box("Headlight housing",(x,-1.08,.94),(.22,.07,.15),DARK,.02,root)
        box("Headlight lens",(x,-1.12,.94),(.15,.025,.08),CYAN,.01,root)
    # The siren is a separate optional accessory state.
    box("Siren base",(0,-.08,2.18),(.25,.16,.07),DARK,.015,root)
    cyl("Siren lens",(0,-.08,2.28),.095,.16,RED,parent=root)

def build(letter,label,finish_mat,style,canonical):
    r=root_empty("FactoryCart_Variant_"+letter+"_"+label)
    r["variant"]=letter
    base(r,finish_mat,style)
    cabin(r,style)
    r["asset_id"]="vehicle-factory-cart"
    r["canonical_status"]=canonical
    r["gameplay_reference"]="Compact hand-slot factory vehicle, one inventory slot, no normal fuel requirement."
    r["target_dimensions_m"]="Unverified; provisional 1.8 x 2.5 x 2.3 m envelope; confirm against game and Pioneer scale."
    r["design_note"]="Independent cart geometry; A/B reflect confirmed base and gold finish variants."
    return r

variants=[
    ("A","Standard_FICSIT_Cart",WHITE,"classic","confirmed in-game variant"),
    ("B","Golden_Factory_Cart",GOLD,"gold","confirmed in-game variant"),
    ("C","Utility_Service_Cart",STEEL,"utility","optional concept, not a canonical variant"),
    ("D","Low_Profile_Cart",WHITE,"low","optional concept, not a canonical variant"),
]
roots=[]
for letter,label,material,style,canonical in variants:
    r=build(letter,label,material,style,canonical)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.1))
    c=bpy.context.object; c.name="COLLIDER_FactoryCart"; c.dimensions=(1.8,2.5,2.3)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"factory_cart_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*2.5
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"factory_cart_four_variants.blend"))
print("Created four original Factory Cart blockout variants:",OUT_DIR)
