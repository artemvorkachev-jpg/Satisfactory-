import bpy, math, os
from mathutils import Vector

# Four original blockout alternatives for logistics, power and player-transport infrastructure.
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
OUT=os.path.join(ROOT,"assets","models","infrastructure")
os.makedirs(OUT,exist_ok=True)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=1.0

def mat(n,c,m=.35,r=.4,e=0):
    x=bpy.data.materials.get(n) or bpy.data.materials.new(n); x.diffuse_color=(*c,1); x.use_nodes=True
    p=x.node_tree.nodes.get("Principled BSDF"); p.inputs["Base Color"].default_value=(*c,1); p.inputs["Metallic"].default_value=m; p.inputs["Roughness"].default_value=r
    if e and "Emission Color" in p.inputs: p.inputs["Emission Color"].default_value=(*c,1); p.inputs["Emission Strength"].default_value=e
    return x
A=mat("Infrastructure amber enamel",(.82,.29,.055),.48,.32); D=mat("Infrastructure graphite",(.045,.06,.07),.82,.28)
S=mat("Infrastructure brushed steel",(.34,.39,.41),.86,.25); Y=mat("Infrastructure safety yellow",(1,.61,.025),.18,.34)
G=mat("Infrastructure inspection glass",(.025,.16,.19),.45,.18); C=mat("Infrastructure status cyan",(.02,.42,.52),.25,.22,1.4)
R=mat("Infrastructure rubber",(.018,.022,.025),.02,.78)
def root(n):
    o=bpy.data.objects.new(n,None); bpy.context.collection.objects.link(o); return o
def finish(o,n,m,b=.025):
    o.name=n
    if m:o.data.materials.append(m)
    if b and o.type=="MESH":
        q=o.modifiers.new("Manufactured edge radii","BEVEL");q.width=b;q.segments=3;o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o
def box(n,p,d,m,r,b=.025,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d
    if rot:o.rotation_euler=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m,b);o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0),v=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=dep,location=p,rotation=rot);o=finish(bpy.context.object,n,m,min(.025,rad*.12));o.parent=r;return o
def tor(n,p,major,minor,m,r,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=p,rotation=rot);o=finish(bpy.context.object,n,m,0);o.parent=r;return o
def pipe(r,pts,rad=.08):
    for p,q in zip(pts,pts[1:]):
        a,b=Vector(p),Vector(q);o=cyl("Pipe segment",(a+b)*.5,rad,(b-a).length,S,r);o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
        cyl("Pipe flange",p,rad*1.3,.08,Y,r);cyl("Pipe flange",q,rad*1.3,.08,Y,r)
spec={
"conveyor_belt":("Conveyor Belt",4.0,1.4,1.0),
"conveyor_lift":("Conveyor Lift",2.0,2.0,5.0),
"conveyor_splitter":("Conveyor Splitter",2.0,2.0,1.7),
"conveyor_merger":("Conveyor Merger",2.0,2.0,1.7),
"conveyor_pole":("Conveyor Pole",1.2,1.2,3.0),
"pipeline":("Pipeline",4.0,1.2,1.2),
"pipeline_junction":("Pipeline Junction",2.0,2.0,2.0),
"pipeline_pump":("Pipeline Pump",2.0,2.0,2.6),
"fluid_buffer":("Fluid Buffer",4.0,4.0,5.0),
"power_pole":("Power Pole",1.5,1.5,8.0),
"power_storage":("Power Storage",4.0,4.0,5.0),
"power_switch":("Power Switch",1.5,1.0,2.2),
"power_tower":("Power Tower",4.0,4.0,18.0),
"hypertube":("Hypertube",4.0,1.5,1.5),
"hypertube_entrance":("Hypertube Entrance",3.0,3.0,3.0),
"hypertube_junction":("Hypertube Junction",3.0,3.0,3.0),
"storage_container":("Storage Container",4.0,4.0,5.0),
"awesome_sink":("AWESOME Sink",5.0,5.0,6.0)
}
def build(kind,letter,style):
    name,w,d,h=spec[kind];r=root(name+"_Variant_"+letter)
    box("Foundation",(0,0,.12),(w*.9,d*.9,.24),D,r)
    if kind=="conveyor_belt":
        box("Belt frame",(0,0,.55),(w,d*.72,.32),D,r)
        box("Moving belt",(0,0,.74),(w*.94,d*.58,.08),R,r,.01)
        for x in (-w*.38,-w*.12,w*.12,w*.38):
            cyl("Roller",(x,0,.54),d*.20,d*.78,S,r,(math.pi/2,0,0))
            cyl("Roller axle cap",(x,-d*.40,.54),.08,.05,Y,r,(math.pi/2,0,0))
        for y in (-d*.42,d*.42):box("Side guard",(0,y,.85),(w,.07,.20),A,r)
    elif kind=="conveyor_lift":
        box("Lift tower",(0,0,h*.48),(w*.70,d*.60,h*.85),D,r,.08)
        for z in (.65,h*.35,h*.70):
            box("Lift service window",(0,-d*.32,z),(w*.38,.04,.48),G,r)
        for z in (.5,h*.25,h*.5,h*.75):
            box("Belt cleat",(0,-d*.36,z),(w*.50,.07,.12),A,r)
        box("Upper belt mouth",(0,-d*.48,h*.87),(w*.8,.24,.55),S,r)
    elif kind in ("conveyor_splitter","conveyor_merger"):
        box("Junction body",(0,0,.92),(w*.82,d*.82,.85),D,r,.08)
        ports=[(0,-d*.48),(0,d*.48),(-w*.48,0)] if kind.endswith("splitter") else [(0,-d*.48),(0,d*.48),(w*.48,0)]
        for x,y in ports:
            box("Conveyor port",(x,y,1.0),(.72,.22,.62),A,r,.035)
            box("Port opening",(x,y*1.04,1.0),(.48,.04,.38),R,r,.01)
        box("Logic indicator",(0,0,1.43),(.45,.06,.18),C,r,.015)
    elif kind=="conveyor_pole":
        box("Pole foot",(0,0,.28),(1.0,1.0,.40),S,r)
        box("Pole shaft",(0,0,h*.50),(.26,.26,h*.82),D,r)
        box("Belt support arm",(0,0,h*.82),(w*1.4,.25,.24),A,r)
        for x in (-w*.5,w*.5):box("Belt cradle",(x,0,h*.82),(.18,.55,.18),Y,r)
    elif kind=="pipeline":
        cyl("Pipe body",(0,0,.85),.42,w,S,r,(0,math.pi/2,0),48)
        for x in (-w*.35,w*.35):cyl("Pipe flange",(x,0,.85),.62,.16,Y,r,(0,math.pi/2,0),48)
        box("Pipe support",(0,0,.34),(.36,.36,.72),D,r)
    elif kind=="pipeline_junction":
        cyl("Junction main",(0,0,1.0),.48,1.5,S,r)
        cyl("Branch left",(-.6,0,1.0),.42,1.3,S,r,(0,math.pi/2,0))
        cyl("Branch right",(.6,0,1.0),.42,1.3,S,r,(0,math.pi/2,0))
        for p,rot in [((0,0,.2),(0,0,0)),((-.6,0,1),(0,math.pi/2,0)),((.6,0,1),(0,math.pi/2,0))]:cyl("Flanged port",p,.57,.13,Y,r,rot)
    elif kind=="pipeline_pump":
        box("Pump housing",(0,0,1.15),(w*.8,d*.75,1.5),D,r,.08)
        cyl("Pump motor",(0,0,2.0),.62,1.0,A,r)
        cyl("Pump inlet",(-w*.48,0,1.1),.34,.35,S,r,(0,math.pi/2,0))
        cyl("Pump outlet",(w*.48,0,1.1),.34,.35,S,r,(0,math.pi/2,0))
        tor("Motor cooling ring",(0,0,2.0),.65,.05,Y,r)
    elif kind=="fluid_buffer":
        cyl("Tank shell",(0,0,h*.52),w*.34,h*.72,S,r,v=48)
        cyl("Tank top cap",(0,0,h*.90),w*.35,.25,D,r)
        tor("Tank seam",(0,0,h*.28),w*.34,.045,Y,r)
        for x in (-w*.25,w*.25):box("Tank support",(x,0,h*.22),(.25,.3,h*.4),D,r)
        pipe(r,[(0,-d*.35,.8),(0,-d*.35,1.3),(0,0,1.3)],.12)
        box("Level indicator",(0,-d*.37,h*.58),(.18,.08,1.2),C,r)
    elif kind in ("power_pole","power_tower"):
        box("Pole base",(0,0,.5),(w*.55,d*.55,1.0),D,r)
        box("Mast",(0,0,h*.5),(.42,.42,h*.9),S,r)
        for z in (h*.72,h*.82,h*.92):
            box("Crossarm",(0,0,z),(w*1.8,.28,.18),A,r)
            for x in (-w*.7,0,w*.7):
                cyl("Insulator",(x,0,z+.25),.15,.45,G,r)
                tor("Insulator cap",(x,0,z+.48),.13,.035,Y,r)
        if kind=="power_tower":
            for side in (-1,1):
                box("Lattice leg",(side*w*.42,0,h*.43),(.18,.18,h*.78),D,r)
                box("Diagonal brace",(side*w*.25,0,h*.35),(.15,.15,h*.55),Y,r,rot=(0,side*.5,0))
    elif kind=="power_storage":
        box("Battery cabinet",(0,0,h*.50),(w*.76,d*.76,h*.80),D,r,.10)
        for x in (-w*.22,0,w*.22):
            box("Battery cell",(x,-d*.40,h*.50),(.55,.10,h*.55),A,r)
            box("Charge window",(x,-d*.47,h*.55),(.32,.035,h*.25),C,r)
        box("Top busbar",(0,0,h*.94),(w*.55,.35,.18),S,r)
    elif kind=="power_switch":
        box("Switch enclosure",(0,0,1.2),(w*.82,d*.75,1.7),D,r,.08)
        box("Switch lever",(0,-d*.42,1.25),(.16,.12,.65),Y,r,.025,rot=(.35,0,0))
        box("Status display",(0,-d*.43,1.85),(.48,.04,.25),C,r)
    elif kind=="hypertube":
        cyl("Tube section",(0,0,.85),.58,w,A,r,(0,math.pi/2,0),48)
        cyl("Tube inner bore",(0,0,.85),.46,w*1.01,R,r,(0,math.pi/2,0),48)
        for x in (-w*.36,w*.36):tor("Tube reinforcement ring",(x,0,.85),.58,.07,Y,r,(0,math.pi/2,0))
        box("Tube support",(0,0,.28),(.28,.28,.58),D,r)
    elif kind in ("hypertube_entrance","hypertube_junction"):
        box("Tube support base",(0,0,.25),(w*.85,d*.85,.5),D,r)
        if kind=="hypertube_entrance":
            tor("Entrance acceleration ring",(0,0,h*.60),1.0,.18,A,r,(math.pi/2,0,0))
            tor("Inner energy ring",(0,0,h*.60),.72,.08,C,r,(math.pi/2,0,0))
            box("Entry control panel",(0,-d*.45,h*.40),(.65,.10,.7),G,r)
        else:
            for angle in (0,2*math.pi/3,4*math.pi/3):
                x,y=math.cos(angle)*.85,math.sin(angle)*.85
                tor("Junction tube socket",(x,y,h*.65),.55,.12,S,r,(0,0,angle))
            cyl("Junction core",(0,0,h*.65),.42,.7,D,r)
    elif kind=="storage_container":
        box("Storage cabinet",(0,0,h*.52),(w*.82,d*.82,h*.85),A if style%2==0 else D,r,.10)
        for z in (h*.25,h*.5,h*.75):
            box("Door seam",(0,-d*.42,z),(w*.68,.035,.045),D,r,.005)
        for x in (-w*.3,w*.3):
            box("Door latch",(x,-d*.45,h*.52),(.08,.05,.35),Y,r)
        box("Inventory display",(0,-d*.45,h*.84),(.7,.05,.28),C,r)
    elif kind=="awesome_sink":
        box("Sink body",(0,0,h*.42),(w*.76,d*.72,h*.66),D,r,.10)
        tor("Sink intake ring",(0,-d*.15,h*.75),w*.22,.18,A,r)
        cyl("Sink intake",(0,-d*.15,h*.75),w*.15,.25,R,r)
        box("Output chute",(0,-d*.45,h*.38),(w*.48,.55,.55),S,r)
        box("Score display",(0,-d*.48,h*.83),(w*.40,.05,.25),C,r)
    # Shared safety markings, connection tags and coarse collision proxy.
    box("Asset ID plate",(0,-d*.51,h*.88),(.7,.045,.20),Y,r,.012)
    for x in (-w*.38,w*.38):
        box("Service foot",(x,d*.35,.34),(.3,.3,.5),S,r)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,h*.5))
    col=bpy.context.object;col.name="COLLIDER_"+kind;col.dimensions=(w,d,h)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    col.display_type="WIRE";col.hide_render=True;col["physics_role"]="static_infrastructure_collision_proxy";col.parent=r
    r["asset_id"]="building-"+kind.replace("_","-");r["variant"]=letter
    r["target_dimensions_m"]=f"{w} x {d} x {h} provisional; verify footprint and snap points in game."
    r["dimensions_status"]="unverified_blockout"
    r["design_note"]=["A: functional reference-oriented silhouette","B: enclosed armored variant","C: open service-frame variant","D: modular futuristic variant"][style]
    return r

for kind in spec:
    folder=os.path.join(OUT,kind);os.makedirs(folder,exist_ok=True)
    for i,letter in enumerate("ABCD"):
        bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
        r=build(kind,letter,i)
        bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
        for o in r.children_recursive:o.select_set(True)
        bpy.context.view_layer.objects.active=r
        bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{kind}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
    bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
    for i,letter in enumerate("ABCD"):
        r=build(kind,letter,i);r.location.x=(i-1.5)*12
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{kind}_four_variants.blend"))
    print("Generated infrastructure variants:",kind)
print("Infrastructure batch complete:",len(spec),"families, 72 GLB exports.")
