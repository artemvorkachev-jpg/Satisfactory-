import bpy
import math
import os

# Original Satisfactory-inspired Portable Miner blockout variants.
# It is hand-slot equipment that can be placed on a solid resource node.
# No exact mesh dimensions are published; all dimensions are provisional.
# Run: blender --background --python tools/blender/generate_portable_miner_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "portable_miner")
os.makedirs(OUT_DIR, exist_ok=True)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

AMBER = mat("Industrial amber enamel", (.82, .29, .055), .45, .32)
DARK = mat("Graphite structural alloy", (.045, .06, .07), .82, .28)
STEEL = mat("Brushed service metal", (.34, .39, .41), .82, .27)
RUBBER = mat("Foot grip elastomer", (.018, .022, .025), .0, .82)
GLASS = mat("Inspection glass", (.025, .16, .19), .35, .18)
YELLOW = mat("Safety yellow", (1, .61, .025), .15, .36)
CYAN = mat("Status cyan", (.02, .42, .52), .25, .22)

def finish(o, name, material, bevel=.025):
    o.name = name
    if material:
        o.data.materials.append(material)
    if bevel and o.type == "MESH":
        b = o.modifiers.new("Manufactured edge radius", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def box(name, loc, dims, material, bevel=.025, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, name, material, bevel)
    if parent:
        o.parent = parent
    return o

def cyl(name, loc, radius, depth, material, rot=(0,0,0), parent=None, vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = finish(bpy.context.object, name, material, min(.025, radius*.12))
    if parent:
        o.parent = parent
    return o

def torus(name, loc, major, minor, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=8,
                                     location=loc)
    o = finish(bpy.context.object, name, material, 0)
    if parent:
        o.parent = parent
    return o

def root_empty(name):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    return r

def base_frame(root, spread=.48):
    box("Lower chassis", (0, 0, .20), (.72, .68, .16), DARK, .04, root)
    for x in (-spread, spread):
        for y in (-spread, spread):
            box("Rubberized foot", (x*.72, y*.72, .035), (.20, .18, .07), RUBBER, .02, root)
            box("Foot bracket", (x*.72, y*.72, .10), (.12, .12, .12), STEEL, .02, root)

def motor_and_drill(root, body_radius=.25, motor_height=.58):
    cyl("Motor housing", (0, 0, .78), body_radius, motor_height, AMBER, parent=root)
    cyl("Motor upper cap", (0, 0, 1.10), body_radius*.92, .10, DARK, parent=root)
    torus("Motor service collar", (0, 0, .50), body_radius*.94, .025, STEEL, root)
    cyl("Drive spindle", (0, 0, .27), .095, .42, DARK, parent=root)
    cyl("Mining bit", (0, 0, .045), .14, .12, STEEL, vertices=8, parent=root)
    for a in range(6):
        angle = 2*math.pi*a/6
        box("Cooling fin", (math.cos(angle)*body_radius*.88,
                            math.sin(angle)*body_radius*.88, .82),
            (.06,.12,.32), DARK, .012, root).rotation_euler[2] = angle

def service_details(root, panel_loc=(0,-.30,.83)):
    box("Service panel bezel", panel_loc, (.22,.035,.17), DARK, .015, root)
    box("Inspection window", (panel_loc[0], panel_loc[1]-.025, panel_loc[2]),
        (.13,.012,.09), GLASS, .008, root)
    for z in (panel_loc[2]-.045, panel_loc[2]+.045):
        cyl("Panel indicator", (panel_loc[0]+.085, panel_loc[1]-.04, z),
            .018,.012,CYAN,(math.pi/2,0,0),root,16)
    box("Carry handle", (0,-.33,1.17), (.42,.10,.08), STEEL, .025, root)
    box("Safety stripe", (0,-.325,.56), (.35,.025,.045), YELLOW, .008, root)

def add_collider(root):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,.62))
    c=bpy.context.object
    c.name="COLLIDER_PortableMiner"
    c.dimensions=(1.35,1.25,1.40)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.display_type="WIRE"
    c.hide_render=True
    c["physics_role"]="placeable_equipment_collision_proxy"
    c.parent=root

def export_root(root, name):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in root.children_recursive:
        o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,name+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)

def variant_a():
    r=root_empty("PortableMiner_Variant_A_Compact_Tripod")
    base_frame(r,.47)
    motor_and_drill(r,.24,.58)
    for a in (0,2*math.pi/3,4*math.pi/3):
        x=math.cos(a)*.55; y=math.sin(a)*.55
        leg=box("Tripod support", (x*.72,y*.72,.43),(.12,.12,.62),DARK,.02,r)
        leg.rotation_euler[1]=math.cos(a)*-.28
        leg.rotation_euler[0]=math.sin(a)*.28
    service_details(r)
    r["design_note"]="Compact three-leg portable miner with a central motor housing."
    return r

def variant_b():
    r=root_empty("PortableMiner_Variant_B_Armored_Cage")
    base_frame(r,.48)
    motor_and_drill(r,.27,.62)
    for x in (-.32,.32):
        box("Armored side rail",(x,.05,.74),(.10,.52,.82),STEEL,.025,r)
        box("Amber armor insert",(x*1.12,-.20,.82),(.04,.035,.38),AMBER,.01,r)
    box("Top carry arch",(0,.10,1.25),(.58,.12,.10),YELLOW,.025,r)
    service_details(r,(0,-.34,.80))
    r["design_note"]="Armored protective cage around the motor and drill assembly."
    return r

def variant_c():
    r=root_empty("PortableMiner_Variant_C_Open_Service_Frame")
    base_frame(r,.50)
    motor_and_drill(r,.22,.54)
    for x in (-.38,.38):
        box("Vertical frame post",(x,.18,.70),(.08,.10,.92),DARK,.018,r)
        cyl("Side tension joint",(x,.18,.34),.075,.09,STEEL,(math.pi/2,0,0),r)
    box("Top cross member",(0,.18,1.20),(.84,.12,.10),STEEL,.025,r)
    box("Open service shelf",(0,-.25,.44),(.48,.08,.12),AMBER,.02,r)
    service_details(r,(0,-.34,.88))
    r["design_note"]="Open service frame with exposed structural supports and visible motor."
    return r

def variant_d():
    r=root_empty("PortableMiner_Variant_D_Modular_Pod")
    base_frame(r,.46)
    motor_and_drill(r,.23,.58)
    for x in (-.34,.34):
        box("Removable side module",(x,.02,.75),(.20,.36,.50),AMBER,.04,r)
        box("Module latch",(x,-.17,.78),(.08,.04,.12),YELLOW,.01,r)
        cyl("Module hinge",(x,.20,.55),.06,.22,STEEL,(0,math.pi/2,0),r)
    box("Top equipment rail",(0,.12,1.18),(.70,.12,.08),DARK,.02,r)
    service_details(r,(0,-.34,.85))
    r["design_note"]="Modular side pods with central motor and removable service panels."
    return r

builders=[variant_a,variant_b,variant_c,variant_d]
roots=[]
for i,build in enumerate(builders):
    r=build()
    add_collider(r)
    r["asset_id"]="equipment-portable-miner"
    r["variant"]=chr(ord("A")+i)
    r["gameplay_reference"]="Hand-slot placeable miner; no power or fuel, no conveyor output, limited internal storage."
    r["target_dimensions_m"]="1.35 x 1.25 x 1.40 provisional; confirm against Pioneer and resource-node scale."
    export_root(r,"portable_miner_variant_"+chr(ord("a")+i))
    roots.append(r)

for i,r in enumerate(roots):
    r.location.x=(i-1.5)*1.65
bpy.ops.object.select_all(action="DESELECT")
for r in roots:
    r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"portable_miner_four_variants.blend"))
print("Created four original Portable Miner blockout variants:",OUT_DIR)
