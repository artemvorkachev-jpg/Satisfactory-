import bpy
import math
import os

# Original Satisfactory-inspired Cyber Wagon concept variants.
# The canonical option uses the game's distinctive angular body and square wheels.
# This is independently designed geometry, not a copy of the Tesla Cybertruck.
# Exact game dimensions are not published in the reference; bounds are provisional.
# Run: blender --background --python tools/blender/generate_cyber_wagon_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "cyber_wagon")
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

STEEL=mat("Brushed angular alloy",(.42,.46,.48),.88,.23)
DARK=mat("Graphite lower chassis",(.035,.045,.05),.82,.28)
GLASS=mat("Smoked panoramic glass",(.025,.12,.15),.55,.16)
RUBBER=mat("Square wheel elastomer",(.018,.022,.025),.02,.78)
AMBER=mat("Industrial amber accents",(.82,.29,.055),.45,.32)
YELLOW=mat("Safety yellow",(1,.61,.025),.15,.34)
CYAN=mat("Headlight cyan",(.02,.42,.52),.25,.22,1.5)

def finish(o,name,material,bevel=.025):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Machined edge radius","BEVEL"); b.width=bevel; b.segments=2
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.025,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def mesh_obj(name,verts,faces,material,parent=None):
    me=bpy.data.meshes.new(name+"_Mesh"); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o)
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def angular_body(root,style):
    if style=="wedge":
        # Low, faceted front with rising roofline and angular rear shoulders.
        verts=[
            (-1.15,-2.15,1.10),(1.15,-2.15,1.10),
            (-1.35,1.85,1.10),(1.35,1.85,1.10),
            (-1.02,-1.10,2.05),(1.02,-1.10,2.05),
            (-.82,.85,2.45),(.82,.85,2.45),
            (-1.22,1.85,1.85),(1.22,1.85,1.85)
        ]
        faces=[
            (0,1,5,4),(4,5,7,6),(6,7,9,8),(0,4,6,8,2),
            (1,3,9,7,5),(0,2,3,1),(2,8,9,3)
        ]
        mesh_obj("Faceted wedge body",verts,faces,STEEL,root)
    elif style=="flat":
        box("Flat armored body",(0,0,1.55),(2.5,4.2,1.05),STEEL,.05,root)
        box("Roof slab",(0,.1,2.15),(2.35,2.2,.16),DARK,.03,root)
    elif style=="modular":
        box("Central chassis shell",(0,0,1.48),(2.45,3.9,.92),DARK,.07,root)
        box("Replaceable upper shell",(0,-.1,2.00),(2.25,2.55,.18),STEEL,.04,root)
        box("Rear service pod",(0,1.25,1.88),(2.1,1.15,.50),AMBER,.06,root)
    else:
        box("Open chassis shell",(0,0,1.38),(2.35,3.9,.68),DARK,.04,root)
        for x in (-1.0,1.0):
            box("Structural side beam",(x,0,1.85),(.12,3.8,.85),STEEL,.02,root)
        box("Upper cross roof",(0,.0,2.35),(2.2,2.0,.15),STEEL,.03,root)

def square_wheel(root,x,y):
    # Square wheel is a deliberate stylized feature of this vehicle.
    wheel=box("Square wheel",(x,y,.70),(.38,.86,.86),RUBBER,.055,root)
    box("Square wheel hub",(x*1.01,y,.70),(.41,.42,.42),STEEL,.035,root)
    box("Hub center",(x*1.02,y,.70),(.43,.18,.18),AMBER,.025,root)

def cabin_details(root,style):
    if style=="wedge":
        windshield=mesh_obj("Angled windshield",
            [(-.93,-1.22,2.08),(.93,-1.22,2.08),(.76,.48,2.43),(-.76,.48,2.43)],
            [(0,1,2,3)],GLASS,root)
        for x in (-1.10,1.10):
            box("Angular side window",(x,-.05,2.02),(.025,1.40,.42),GLASS,.01,root)
        # Small side window cracks are represented as thin etched lines, not broken glass geometry.
        for x in (-1.12,1.12):
            box("Glass scratch accent",(x,-.12,2.05),(.012,.28,.012),YELLOW,.002,root)
    elif style=="flat":
        box("Wide front glass",(0,-2.12,1.86),(1.85,.025,.50),GLASS,.015,root)
        for x in (-1.18,1.18):
            box("Side window",(x,-.05,1.90),(.025,1.4,.50),GLASS,.01,root)
    elif style=="modular":
        box("Panoramic windshield",(0,-1.98,1.93),(1.95,.03,.55),GLASS,.015,root)
        for x in (-1.18,1.18):
            box("Side glazing",(x,-.1,1.92),(.025,1.45,.52),GLASS,.01,root)
    else:
        box("Front screen",(0,-1.98,1.88),(1.85,.03,.46),GLASS,.015,root)
        for x in (-.92,.92):
            box("Roll frame post",(x,-.8,1.98),(.08,.08,.78),AMBER,.015,root)
    # Lights and trunk access.
    box("Front light bar",(0,-2.19,1.22),(1.8,.07,.12),CYAN,.018,root)
    box("Rear cargo hatch",(0,2.06,1.52),(1.35,.06,.42),DARK,.02,root)
    box("Rear hatch handle",(0,2.11,1.53),(.25,.035,.06),YELLOW,.008,root)
    box("Lower chassis skid plate",(0,0,.98),(2.3,3.8,.12),DARK,.02,root)

def build(letter,label,style):
    r=root_empty("CyberWagon_Variant_"+letter+"_"+label)
    angular_body(r,style)
    for x in (-1.45,1.45):
        for y in (-1.35,1.35):
            square_wheel(r,x,y)
    cabin_details(r,style)
    r["asset_id"]="vehicle-cyber-wagon"
    r["variant"]=letter
    r["gameplay_reference"]="Compact special vehicle with a single cargo slot; square-wheel appearance and distinctive angular body."
    r["target_dimensions_m"]="Unverified; provisional 3.2 x 5.0 x 2.8 m envelope for blockout only."
    r["design_note"]="Variant A is the closest independent angular silhouette study; B-D are optional design directions."
    return r

variants=[
    ("A","Faceted_Wedge","wedge"),
    ("B","Flat_Armored_Pod","flat"),
    ("C","Modular_Industrial_Shell","modular"),
    ("D","Open_Service_Frame","open"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.4))
    c=bpy.context.object; c.name="COLLIDER_CyberWagon"; c.dimensions=(3.2,5.0,2.8)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"; c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"; c.parent=r
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"cyber_wagon_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*4.2
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"cyber_wagon_four_variants.blend"))
print("Created four original Cyber Wagon blockout variants:",OUT_DIR)
