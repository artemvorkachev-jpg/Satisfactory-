import bpy
import math
import os

# Original Satisfactory-inspired cargo Drone blockout variants.
# The in-game drone is a port-based freight vehicle with cargo storage and
# four rotor/propulsion assemblies. Geometry is independently authored.
# Wiki dimensions are used only as a provisional envelope; confirm with game views.
# Run: blender --background --python tools/blender/generate_drone_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "drone")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.4, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value = (*color, 1)
        bs.inputs["Emission Strength"].default_value = emission
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .48, .32)
DARK = mat("Graphite structural alloy", (.045, .06, .07), .82, .28)
STEEL = mat("Brushed service metal", (.34, .39, .41), .86, .25)
RUBBER = mat("Landing elastomer", (.018, .022, .025), .02, .78)
GLASS = mat("Sensor glass", (.025, .16, .19), .45, .18)
YELLOW = mat("Safety yellow", (1, .61, .025), .18, .34)
CYAN = mat("Navigation cyan", (.02, .42, .52), .25, .22, 1.5)

def finish(o, name, material, bevel=.035):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b=o.modifiers.new("Manufactured edge radii","BEVEL")
        b.width=bevel
        b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.035, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def cyl(name, loc, radius, depth, material, rot=(0,0,0), parent=None, vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
                                        location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,min(.035,radius*.1))
    if parent: o.parent=parent
    return o

def torus(name, loc, major, minor, material, rot=(0,0,0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,
                                     major_segments=40,minor_segments=10,
                                     location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,0)
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(r)
    return r

def central_fuselage(root, style):
    if style=="rounded":
        box("Central fuselage",(0,0,0),(4.6,2.4,1.55),AMBER,.35,root)
    elif style=="angular":
        box("Central fuselage",(0,0,0),(4.8,2.2,1.5),DARK,.12,root)
        box("Upper armor shell",(0,0,.72),(4.2,2.0,.20),AMBER,.08,root)
    elif style=="open":
        box("Central spine",(0,0,0),(4.4,1.0,1.25),DARK,.08,root)
        box("Cargo support rails",(0,0,-.48),(4.8,2.0,.16),STEEL,.035,root)
    else:
        box("Central fuselage",(0,0,0),(4.4,2.0,1.45),STEEL,.18,root)
        box("Modular upper cover",(0,0,.73),(3.6,1.7,.18),AMBER,.06,root)

    # Cargo bay remains a separate logical/visual subassembly.
    box("Cargo bay shell",(0,.0,-.30),(2.35,1.55,.75),DARK,.08,root)
    box("Cargo bay access panel",(0,-.80,-.28),(1.45,.045,.42),STEEL,.025,root)
    box("Cargo latch",(0,-.84,-.30),(.35,.04,.08),YELLOW,.012,root)
    box("Forward sensor panel",(0,-1.12,.18),(.55,.05,.28),DARK,.025,root)
    box("Forward sensor lens",(0,-1.16,.18),(.24,.02,.13),GLASS,.012,root)
    for x in (-.85,.85):
        box("Navigation light",(x,-.96,.48),(.16,.05,.07),CYAN,.012,root)

def rotor_assembly(root, x, y, style, index):
    # Four independent rotor units; blade geometry is a display-only blockout.
    z=.88
    if style=="ducted":
        cyl("Ducted rotor housing",(x,y,z),.82,.30,DARK,(math.pi/2,0,0),root,48)
        torus("Rotor safety duct",(x,y-.18,z),.72,.075,STEEL,(math.pi/2,0,0),root)
        cyl("Rotor hub",(x,y-.20,z),.16,.20,AMBER,(math.pi/2,0,0),root)
    else:
        cyl("Rotor motor pod",(x,y,z),.42,.58,AMBER,(math.pi/2,0,0),root,40)
        cyl("Motor cap",(x,y-.32,z),.30,.08,DARK,(math.pi/2,0,0),root)
        torus("Motor service ring",(x,y-.37,z),.26,.025,YELLOW,(math.pi/2,0,0),root)
        cyl("Rotor hub",(x,y,z+.30),.18,.18,STEEL, parent=root)

    # Blades are intentionally low-detail; runtime will rotate this subassembly.
    for b in range(4):
        a=2*math.pi*b/4
        bx=x+math.cos(a)*.52
        by=y+math.sin(a)*.52
        blade=box("Rotor blade",(bx,by,z+.40),(.88,.14,.035),DARK,.025,root)
        blade.rotation_euler[2]=a
    box("Rotor arm",(x*.58,y*.58,.25),(.38,.38,1.10),STEEL,.05,root)
    box("Arm safety marking",(x*.58,y*.58,.45),(.40,.40,.08),YELLOW,.012,root)

def landing_gear(root):
    for x in (-1.25,1.25):
        for y in (-.65,.65):
            leg=box("Landing strut",(x,y,-1.0),(.15,.15,.85),STEEL,.025,root)
            leg.rotation_euler[1]=x*.06
            box("Landing foot",(x,y,-1.46),(.52,.38,.12),RUBBER,.035,root)
            box("Foot warning plate",(x,y-.01,-1.385),(.28,.25,.025),YELLOW,.008,root)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0))
    c=bpy.context.object
    c.name="COLLIDER_Drone"
    c.dimensions=(16,6,3)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"
    c.hide_render=True
    c["physics_role"]="vehicle_collision_proxy"
    c.parent=root

def export_root(root,name):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in root.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,name+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)

def build(letter,label,style):
    r=root_empty("Drone_Variant_"+letter+"_"+label)
    central_fuselage(r,style)
    if style=="open":
        positions=[(-2.4,-1.8),(2.4,-1.8),(-2.4,1.8),(2.4,1.8)]
    else:
        positions=[(-3.0,-2.1),(3.0,-2.1),(-3.0,2.1),(3.0,2.1)]
    for i,(x,y) in enumerate(positions):
        rotor_assembly(r,x,y,style,i)
    landing_gear(r)
    box("Upper navigation mast",(0,.65,1.0),(.14,.14,.45),STEEL,.025,r)
    cyl("Navigation beacon",(0,.65,1.25),.10,.08,CYAN,parent=r)
    r["asset_id"]="vehicle-drone"
    r["variant"]=letter
    r["gameplay_reference"]="Autonomous freight vehicle built on a Drone Port; 9 cargo slots; takeoff, route flight, hover queue, landing and docking states."
    r["target_dimensions_m"]="16 x 6 x 3 m provisional envelope from wiki dimensions; confirm orientation and exact bounds in-game."
    r["design_note"]="Independent industrial cargo-drone concept; variant for user review, not an approved final."
    return r

variants=[
    ("A","Twin_Spar_Industrial","rounded"),
    ("B","Angular_Armored_Cargo","angular"),
    ("C","Open_Service_Frame","open"),
    ("D","Modular_Ducted_Rotor","ducted"),
]
roots=[]
for letter,label,style in variants:
    r=build(letter,label,style)
    add_collider(r)
    export_root(r,"drone_variant_"+letter.lower())
    roots.append(r)

for i,r in enumerate(roots):
    r.location.x=(i-1.5)*18.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"drone_four_variants.blend"))
print("Created four original Drone blockout variants:",OUT_DIR)
