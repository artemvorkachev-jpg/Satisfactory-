import bpy
import math
import os
from mathutils import Vector

# Independently authored industrial production-building blockouts.
# Four design alternatives per asset. All dimensions are provisional unless
# a verified in-game envelope is recorded in the manifest.
# Run from repo root:
# blender --background --python tools/blender/generate_production_buildings_batch.py

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "models", "buildings")
os.makedirs(OUT, exist_ok=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

def material(name, color, metallic=.3, rough=.4, emission=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = rough
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value = (*color, 1)
        bs.inputs["Emission Strength"].default_value = emission
    return m

AMBER = material("Outpost amber enamel", (.82,.29,.055), .48,.32)
DARK = material("Graphite structural alloy", (.045,.06,.07), .82,.28)
STEEL = material("Brushed service metal", (.34,.39,.41), .86,.25)
GLASS = material("Inspection glass", (.025,.16,.19), .45,.18)
YELLOW = material("Safety yellow", (1,.61,.025), .18,.34)
CYAN = material("Status cyan", (.02,.42,.52), .25,.22,1.4)
RUBBER = material("Industrial elastomer", (.018,.022,.025), .02,.78)
CONCRETE = material("Foundation concrete", (.30,.32,.31), .05,.82)

def finish(o, name, mat, bevel=.04):
    o.name=name
    if mat: o.data.materials.append(mat)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, mat, parent, bevel=.04, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.dimensions=dims
    if rot: o.rotation_euler=rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o,name,mat,bevel); o.parent=parent
    return o

def cyl(name, loc, radius, depth, mat, parent, rot=(0,0,0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc,rotation=rot)
    o=finish(bpy.context.object,name,mat,min(.035,radius*.12)); o.parent=parent
    return o

def torus(name, loc, major, minor, mat, parent, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=loc,rotation=rot)
    o=finish(bpy.context.object,name,mat,0); o.parent=parent
    return o

def empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

# Geometry builders use a common 8 m foundation grid. This is a visual blockout,
# not a claim that every machine has an 8 m footprint.
def base(root, w, d, style):
    box("Foundation skid",(0,0,.22),(w*.92,d*.92,.44),DARK,root,.06)
    for x in (-w*.38,w*.38):
        for y in (-d*.38,d*.38):
            box("Mounting foot",(x,y,.10),(.42,.42,.20),STEEL,root,.025)
    box("Amber safety sill",(0,-d*.47,.52),(w*.72,.08,.08),YELLOW,root,.012)

def service_panels(root,w,d,h,style):
    for side in (-1,1):
        x=side*(w*.505)
        box("Side access panel",(x,0,h*.46),(.06,d*.48,h*.38),AMBER if style%2==0 else DARK,root,.025)
        for y in (-d*.16,d*.16):
            cyl("Panel latch",(x*1.015,y,h*.46),.045,.035,STEEL,root,(0,math.pi/2,0),16)
    box("Status panel",(0,-d*.51,h*.72),(w*.22,.045,.18),GLASS,root,.018)
    for x in (-.18,0,.18):
        cyl("Status indicator",(x,-d*.54,h*.72),.035,.025,CYAN if x==0 else YELLOW,root,(math.pi/2,0,0),16)

def pipe_run(root, points, radius=.11, mat=STEEL):
    # Straight pipe segments between authored points.
    for a,b in zip(points,points[1:]):
        va,vb=Vector(a),Vector(b); delta=vb-va
        mid=(va+vb)*.5
        o=cyl("Process pipe",mid,radius,delta.length,mat,root)
        o.rotation_euler=delta.to_track_quat("Z","Y").to_euler()
        for p in (a,b): cyl("Pipe coupling",p,radius*1.35,.10,YELLOW,root)

def make_machine(kind, letter, style):
    specs={
      "smelter":("Smelter",4.0,4.0,4.0),
      "foundry":("Foundry",6.0,5.0,5.0),
      "constructor":("Constructor",5.0,5.0,4.5),
      "assembler":("Assembler",8.0,6.0,5.0),
      "manufacturer":("Manufacturer",10.0,8.0,7.0),
      "refinery":("Refinery",10.0,8.0,10.0),
      "blender":("Blender",8.0,8.0,8.0),
      "packager":("Packager",5.0,5.0,5.0),
      "particle_accelerator":("Particle Accelerator",16.0,16.0,12.0),
      "quantum_encoder":("Quantum Encoder",12.0,10.0,9.0),
      "converter":("Converter",8.0,8.0,7.0),
      "miner":("Miner",8.0,8.0,6.0),
      "oil_extractor":("Oil Extractor",10.0,10.0,7.0),
      "water_extractor":("Water Extractor",8.0,8.0,7.0),
    }
    label,w,d,h=specs[kind]
    root=empty(label+"_Variant_"+letter)
    base(root,w,d,style)
    # Main housing silhouette varies by production class.
    if kind=="particle_accelerator":
        # A circular accelerator chamber, raised ring and radial supports.
        cyl("Accelerator core",(0,0,h*.52),w*.30,h*.32,DARK,root,verts=64)
        torus("Accelerator containment ring",(0,0,h*.66),w*.36,.28,AMBER,root)
        torus("Inner field ring",(0,0,h*.66),w*.27,.12,CYAN,root)
        for a in range(8):
            ang=2*math.pi*a/8
            x,y=math.cos(ang)*w*.39,math.sin(ang)*d*.39
            box("Radial support",(x,y,h*.32),(.38,.38,h*.58),STEEL,root,.035,rot=(0,0,ang))
            cyl("Capacitor node",(x,y,h*.66),.24,.5,YELLOW,root)
    elif kind in ("refinery","oil_extractor","water_extractor"):
        box("Industrial lower housing",(0,0,h*.32),(w*.78,d*.70,h*.48),DARK,root,.12)
        for x in (-w*.25,w*.25):
            cyl("Process vessel",(x,d*.12,h*.66),w*.105,h*.52,STEEL,root,verts=40)
            cyl("Vessel cap",(x,d*.12,h*.93),w*.12,.22,AMBER,root)
            torus("Vessel seam",(x,d*.12,h*.45),w*.105,.035,YELLOW,root)
        pipe_run(root,[(-w*.38,-d*.35,h*.30),(-w*.38,-d*.35,h*.82),(0,-d*.35,h*.82),(0,-d*.50,h*.82)],.10)
        for x in (-w*.36,w*.36):
            box("Service platform",(x,0,h*.56),(.9,d*.55,.12),STEEL,root,.025)
            box("Safety rail",(x,0,h*.68),(.08,d*.55,.08),YELLOW,root,.01)
    elif kind=="quantum_encoder":
        box("Encoder containment body",(0,0,h*.40),(w*.70,d*.68,h*.65),DARK,root,.12)
        for x in (-w*.22,w*.22):
            cyl("Quantum chamber",(x,0,h*.66),w*.12,h*.45,GLASS,root,verts=48)
            torus("Chamber field ring",(x,0,h*.66),w*.13,.10,CYAN,root)
        box("Upper gantry",(0,0,h*.82),(w*.72,.5,.35),AMBER,root,.05)
    elif kind=="miner":
        box("Miner chassis",(0,0,h*.40),(w*.72,d*.72,h*.62),AMBER,root,.10)
        box("Drill head housing",(0,0,h*.78),(w*.38,d*.38,.75),DARK,root,.08)
        cyl("Rotary drill spindle",(0,0,h*.56),w*.13,h*.38,STEEL,root)
        for x in (-w*.22,w*.22):
            box("Lift column",(x,0,h*.58),(.34,.34,h*.68),STEEL,root,.03)
        cyl("Drill bit",(0,0,.75),w*.11,.8,YELLOW,root,verts=12)
    elif kind=="blender":
        box("Mixer lower cabinet",(0,0,h*.30),(w*.72,d*.72,h*.45),DARK,root,.10)
        cyl("Mixing vessel",(0,0,h*.64),w*.25,h*.42,STEEL,root,verts=48)
        cyl("Vessel lid",(0,0,h*.87),w*.28,.22,AMBER,root)
        cyl("Mixer motor",(0,0,h*.98),w*.13,.42,DARK,root)
        pipe_run(root,[(-w*.34,0,h*.42),(-w*.34,0,h*.80),(w*.34,0,h*.80),(w*.34,0,h*.42)],.10)
    else:
        # Enclosed machine with a visibly distinct process window and top modules.
        box("Main machine shell",(0,0,h*.44),(w*.76,d*.72,h*.70),AMBER if style in (0,3) else DARK,root,.12)
        if kind in ("assembler","manufacturer"):
            for x in (-w*.22,0,w*.22):
                box("Workcell frame",(x,0,h*.50),(.20,d*.62,h*.54),STEEL,root,.025)
                box("Workcell viewing window",(x,-d*.37,h*.53),(.55,.05,h*.25),GLASS,root,.025)
                cyl("Actuator",(x,d*.08,h*.79),.16,.6,YELLOW,root)
        elif kind=="foundry":
            box("Smelting furnace mouth",(0,-d*.38,h*.48),(w*.40,.08,h*.32),GLASS,root,.04)
            for x in (-w*.22,w*.22):
                cyl("Exhaust stack",(x,d*.18,h*.88),.25,h*.45,STEEL,root)
                cyl("Stack collar",(x,d*.18,h*.98),.31,.12,YELLOW,root)
        elif kind=="smelter":
            box("Furnace viewing aperture",(0,-d*.38,h*.48),(w*.40,.08,h*.26),GLASS,root,.035)
            box("Heat shield",(0,0,h*.86),(w*.52,d*.48,.20),STEEL,root,.04)
        elif kind=="packager":
            box("Packaging throat",(0,-d*.38,h*.40),(w*.36,.10,h*.28),GLASS,root,.025)
            box("Canister loading tray",(0,-d*.54,h*.25),(w*.50,.45,.14),STEEL,root,.025)
            for x in (-w*.22,w*.22):
                cyl("Clamp piston",(x,-d*.2,h*.65),.09,.72,YELLOW,root)
        elif kind=="converter":
            box("Conversion chamber",(0,0,h*.68),(w*.42,d*.42,h*.35),GLASS,root,.05)
            torus("Chamber containment ring",(0,0,h*.68),w*.24,.10,CYAN,root)
        else:
            box("Process access window",(0,-d*.38,h*.50),(w*.36,.06,h*.26),GLASS,root,.03)
            box("Upper service module",(0,d*.12,h*.86),(w*.54,d*.38,.42),STEEL,root,.05)
    # Shared functional details: ports, service doors, guards, status.
    for x in (-w*.28,w*.28):
        box("Input output port",(x,-d*.42,.92),(.55,.22,.55),STEEL,root,.04)
        cyl("Port coupling",(x,-d*.55,.92),.18,.12,YELLOW,root,(math.pi/2,0,0))
    service_panels(root,w,d,h,style)
    for x in (-w*.34,w*.34):
        for y in (-d*.34,d*.34):
            box("Corner protective upright",(x,y,h*.40),(.13,.13,h*.68),YELLOW,root,.018)
    # Every variant receives an explicit coarse collision proxy.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,h*.52))
    col=bpy.context.object; col.name="COLLIDER_"+kind
    col.dimensions=(w,d,h); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    col.display_type="WIRE"; col.hide_render=True
    col["physics_role"]="static_building_collision_proxy"; col.parent=root
    root["asset_id"]="building-"+kind.replace("_","-")
    root["variant"]=letter
    root["target_dimensions_m"]=f"{w} x {d} x {h} provisional blockout envelope; verify against game references."
    root["dimensions_status"]="unverified_blockout"
    root["design_note"]=["A: closest functional silhouette","B: enclosed modular service layout","C: exposed service-frame layout","D: futuristic reinforced layout"][style]
    return root

assets=["smelter","foundry","constructor","assembler","manufacturer","refinery","blender","packager","particle_accelerator","quantum_encoder","converter","miner","oil_extractor","water_extractor"]
for kind in assets:
    folder=os.path.join(OUT,kind); os.makedirs(folder,exist_ok=True)
    variants=[]
    for idx,letter in enumerate(("A","B","C","D")):
        bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
        root=make_machine(kind,letter,idx)
        bpy.ops.object.select_all(action="DESELECT")
        root.select_set(True)
        for o in root.children_recursive: o.select_set(True)
        bpy.context.view_layer.objects.active=root
        bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{kind}_variant_{letter.lower()}.glb"),
                                  export_format="GLB",use_selection=True,export_apply=True)
        variants.append(root)
    # Rebuild a combined review scene: one variant per bay with identical scale.
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    for idx,letter in enumerate(("A","B","C","D")):
        root=make_machine(kind,letter,idx)
        root.location.x=(idx-1.5)*22.0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{kind}_four_variants.blend"))
    print("Generated",kind,"four Blender variants and four GLB exports")
print("Production-building batch complete:",len(assets),"asset families, 56 GLB exports.")
