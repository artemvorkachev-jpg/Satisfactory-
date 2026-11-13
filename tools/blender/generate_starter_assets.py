import bpy
import math
from mathutils import Vector

# Original, independently designed starter assets for the Satisfactory- project.
# Run with: blender --background --python tools/blender/generate_starter_assets.py
# Output: assets/models/generated/*.blend and *.glb

ROOT = bpy.path.abspath("//")
OUT = ROOT + "assets/models/generated/"
os = __import__("os")
os.makedirs(OUT, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    pass

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

PAINT = material("Industrial enamel - amber", (0.82, 0.29, 0.055), 0.42, 0.32)
DARK = material("Graphite steel", (0.055, 0.072, 0.082), 0.78, 0.3)
STEEL = material("Brushed steel", (0.34, 0.39, 0.41), 0.82, 0.27)
RUBBER = material("Conveyor rubber", (0.018, 0.023, 0.025), 0.05, 0.82)
GLASS = material("Inspection glass", (0.08, 0.28, 0.31), 0.55, 0.18)
YELLOW = material("Safety yellow", (1.0, 0.62, 0.035), 0.18, 0.35)

def cube(name, loc, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat: o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Soft manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def cylinder(name, loc, radius, depth, mat, rotation=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    if mat: o.data.materials.append(mat)
    bevel = o.modifiers.new("Edge chamfer", "BEVEL")
    bevel.width = min(radius * 0.12, 0.035)
    bevel.segments = 2
    o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o

def empty(name, loc):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return o

def collider(name, loc, scale):
    o = cube("COLLIDER_" + name, loc, scale, None, 0)
    o.display_type = "WIRE"
    o.hide_render = True
    o["physics_role"] = "static_collision_proxy"
    return o

def export_asset(name, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(filepath=OUT + name + ".glb", export_format="GLB",
                              use_selection=True, export_apply=True)


def make_constructor():
    made = []
    root = empty("Constructor_Original_Design", (0,0,0)); made.append(root)
    def add(o):
        o.parent = root; made.append(o); return o
    add(cube("Main armored housing", (0,0,1.45), (2.45,1.85,2.35), PAINT, .13))
    add(cube("Lower chassis", (0,0,.28), (2.65,2.0,.38), DARK, .06))
    for x in (-.92,.92):
        for y in (-.67,.67):
            add(cube("Adjustable support foot", (x,y,.08), (.22,.22,.16), STEEL, .025))
            add(cube("Support column", (x,y,.55), (.13,.13,.58), DARK, .025))
    add(cube("Front service door", (0,-.94,1.45), (1.42,.075,1.35), DARK, .045))
    add(cube("Inspection window", (0,-.99,1.65), (.72,.035,.48), GLASS, .025))
    add(cube("Control panel", (.83,-.99,1.25), (.36,.07,.55), STEEL, .025))
    for z in (1.12,1.27,1.42):
        add(cylinder("Panel indicator", (.83,-1.04,z), .045,.025,YELLOW,(math.pi/2,0,0),16))
    for i in range(7):
        add(cube("Cooling vent", (-.82+i*.12,-.99,.78), (.055,.035,.34), DARK,.012))
    for x in (-.72,.72):
        add(cylinder("Upper exhaust", (x,.28,2.68), .13,.42, DARK))
        add(cylinder("Exhaust cap", (x,.28,2.91), .17,.08, STEEL))
    add(cube("Top safety rail", (0,.78,2.66), (1.7,.08,.08), YELLOW,.025))
    add(cube("Output chute", (0,-1.22,.63), (.68,.58,.28), STEEL,.045))
    for i in range(4):
        roller = add(cylinder("Output roller", (-.24+i*.16,-1.42,.49), .075,.12,DARK,(0,math.pi/2,0)))
        roller["animation_note"] = "Rotate around local X for conveyor movement"
    add(collider("Constructor", (0,0,1.45), (2.8,2.35,3.1)))
    root["asset_type"] = "production_machine"
    root["physics"] = "static building; moving subassemblies animated separately"
    export_asset("constructor_prototype", made)
    return made

def make_conveyor():
    made=[]
    root=empty("Conveyor_Module_Original_Design",(0,0,0)); made.append(root)
    def add(o): o.parent=root; made.append(o); return o
    add(cube("Left structural beam",(0,-.48,.72),(4.0,.13,.22),DARK,.035))
    add(cube("Right structural beam",(0,.48,.72),(4.0,.13,.22),DARK,.035))
    add(cube("Moving belt surface",(0,0,.86),(3.92,.88,.075),RUBBER,.025))
    for x in (-1.8,-1.2,-.6,0,.6,1.2,1.8):
        r=add(cylinder("Roller", (x,0,.69), .095,.98,STEEL,(math.pi/2,0,0)))
        r["animation_note"]="Continuous rotation while belt is powered"
    for x in (-1.65,1.65):
        for y in (-.49,.49):
            add(cube("Support leg",(x,y,.34),(.12,.12,.68),STEEL,.025))
            add(cube("Foot plate",(x,y,.035),(.32,.25,.07),DARK,.018))
    for y in (-.49,.49):
        add(cube("Safety edge strip",(0,y,.91),(3.65,.035,.07),YELLOW,.01))
    add(collider("Conveyor", (0,0,.48), (4.15,1.18,1.05)))
    root["asset_type"]="logistics_conveyor"
    root["physics"]="static frame; belt and rollers are animated by simulation state"
    export_asset("conveyor_module_prototype",made)
    return made

def make_portable_miner():
    made=[]
    root=empty("Portable_Miner_Original_Design",(0,0,0)); made.append(root)
    def add(o): o.parent=root; made.append(o); return o
    add(cylinder("Main motor casing",(0,0,1.2),.42,.95,PAINT))
    add(cylinder("Motor end cap",(0,0,1.72),.36,.16,DARK))
    add(cylinder("Drive collar",(0,0,.68),.28,.2,STEEL))
    add(cylinder("Drill spindle",(0,0,.25),.13,.72,DARK))
    add(cylinder("Drill bit",(0,0,-.16),.19,.22,STEEL,vertices=8))
    for a in (0,2*math.pi/3,4*math.pi/3):
        x=math.cos(a)*.56; y=math.sin(a)*.56
        leg=add(cube("Tripod leg",(x*.72,y*.72,.34),(.13,.13,.78),DARK,.025))
        leg.rotation_euler[1]=math.cos(a)*-.34
        leg.rotation_euler[0]=math.sin(a)*.34
        add(cube("Foot pad",(x,y,.035),(.3,.25,.07),STEEL,.02))
    add(cube("Carry handle",(0,-.48,1.68),(.62,.12,.12),DARK,.04))
    add(cube("Status light",(0,-.43,1.28),(.18,.06,.12),YELLOW,.02))
    add(collider("PortableMiner",(0,0,.8),(1.55,1.55,2.15)))
    root["asset_type"]="portable_resource_extractor"
    root["physics"]="placeable static machine; drill spindle animation driven by mining state"
    export_asset("portable_miner_prototype",made)
    return made

make_constructor()
make_conveyor()
make_portable_miner()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.wm.save_as_mainfile(filepath=OUT + "starter_asset_library.blend")
print("Generated 3 original prototype assets in", OUT)
