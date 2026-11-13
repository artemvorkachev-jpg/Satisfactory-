import bpy
import math
import os

# Original Satisfactory-inspired Railway construction variants.
# Wiki reference: 6 m width, 12-100 m segment length, visual rail height ~1.3 m.
# The four variants are straight, curved, inclined and turnout sections.
# Run: blender --background --python tools/blender/generate_railway_variants.py

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT_DIR, "assets", "models", "railway")
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

STEEL=mat("Rail steel",(.34,.39,.41),.88,.24)
DARK=mat("Graphite rail base",(.045,.06,.07),.82,.28)
CONCRETE=mat("Sleeper concrete",(.30,.32,.31),.05,.82)
YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)

def finish(o,name,material,bevel=.02):
    o.name=name
    if material: o.data.materials.append(material)
    if bevel and o.type=="MESH":
        b=o.modifiers.new("Edge radius","BEVEL"); b.width=bevel; b.segments=2
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def box(name,loc,dims,material,bevel=.02,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,material,bevel)
    if parent: o.parent=parent
    return o

def curve(name,points,material,radius=.08,parent=None):
    data=bpy.data.curves.new(name+"_Curve","CURVE")
    data.dimensions="3D"
    data.bevel_depth=radius
    data.bevel_resolution=3
    spline=data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    if parent: o.parent=parent
    return o

def root_empty(name):
    r=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(r); return r

def track_path(root, centerline, sleeper_spacing=.75):
    left=[]; right=[]
    for x,y,z in centerline:
        left.append((x-1.0,y,z+1.3))
        right.append((x+1.0,y,z+1.3))
    curve("Left rail",left,STEEL,.10,root)
    curve("Right rail",right,STEEL,.10,root)
    for i,(x,y,z) in enumerate(centerline):
        if i % max(1,int(sleeper_spacing/.25)) == 0:
            box("Rail sleeper",(x,y,z+.78),(3.3,.22,.20),CONCRETE,.025,root)
            box("Left rail clip",(x-1.0,y,z+.94),(.22,.30,.12),DARK,.012,root)
            box("Right rail clip",(x+1.0,y,z+.94),(.22,.30,.12),DARK,.012,root)

def line_points(y0,y1,n=48,zfunc=None,xfunc=None):
    pts=[]
    for i in range(n+1):
        t=i/n
        y=y0+(y1-y0)*t
        x=xfunc(t) if xfunc else 0
        z=zfunc(t) if zfunc else 0
        pts.append((x,y,z))
    return pts

def build_straight(root):
    pts=line_points(-6,6,48)
    track_path(root,pts,.75)
    box("Track base",(0,0,.55),(3.5,12,.25),DARK,.03,root)

def build_curve(root):
    pts=[]
    for i in range(65):
        t=i/64
        angle=(t-.5)*math.pi/2.6
        radius=14.0
        x=radius*math.sin(angle)
        y=radius*(math.cos(angle)-math.cos(math.pi/5.2)) + (t-.5)*12.0
        pts.append((x,y,0))
    track_path(root,pts,.75)
    box("Curve base",(0,0,.55),(3.5,12,.22),DARK,.03,root)

def build_incline(root):
    pts=line_points(-6,6,48,zfunc=lambda t: 1.0*t)
    track_path(root,pts,.75)
    box("Incline base",(0,0,1.0),(3.5,12,.25),DARK,.03,root)

def build_turnout(root):
    main=line_points(-6,6,48)
    branch=[]
    for i in range(65):
        t=i/64
        y=-6+12*t
        x=0 if t<.20 else 4.2*((t-.20)/.80)**2
        branch.append((x,y,0))
    track_path(root,main,.75)
    # Branch rails use a separate centerline and sleeper sequence.
    left=[]; right=[]
    for x,y,z in branch:
        left.append((x-1.0,y,z+1.3))
        right.append((x+1.0,y,z+1.3))
    curve("Turnout branch left rail",left,STEEL,.10,root)
    curve("Turnout branch right rail",right,STEEL,.10,root)
    for i,(x,y,z) in enumerate(branch):
        if i%3==0:
            box("Turnout sleeper",(x,y,z+.78),(5.0,.22,.20),CONCRETE,.025,root)
    for x in (-.8,.8):
        box("Switch actuator housing",(x,-2.2,1.05),(.48,.75,.45),DARK,.035,root)
        box("Switch status strip",(x,-2.60,1.05),(.25,.025,.12),YELLOW,.01,root)

variants=[
    ("A","Straight_Section",build_straight),
    ("B","Curved_Section",build_curve),
    ("C","Inclined_Section",build_incline),
    ("D","Turnout_Junction",build_turnout),
]
roots=[]
for letter,label,builder in variants:
    r=root_empty("Railway_Variant_"+letter+"_"+label)
    builder(r)
    r["asset_id"]="building-railway"
    r["variant"]=letter
    r["gameplay_reference"]="Powered railway segment; connects stations and supports train movement, signaling and power transfer."
    r["target_dimensions_m"]="12 m segment length, 6 m width, visual rail height about 1.3 m; curves/turnouts need exact snap-point verification."
    r["design_note"]="Track geometry blockout; validate rail gauge, curvature, snap endpoints and support clearance."
    bpy.ops.object.select_all(action="DESELECT")
    r.select_set(True)
    for o in r.children_recursive: o.select_set(True)
    bpy.context.view_layer.objects.active=r
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR,"railway_variant_"+letter.lower()+".glb"),
                              export_format="GLB",use_selection=True,export_apply=True)
    roots.append(r)

for i,r in enumerate(roots): r.location.x=(i-1.5)*8.0
bpy.ops.object.select_all(action="DESELECT")
for r in roots: r.select_set(True)
bpy.context.view_layer.objects.active=roots[0]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR,"railway_four_variants.blend"))
print("Created four original Railway blockout variants:",OUT_DIR)
