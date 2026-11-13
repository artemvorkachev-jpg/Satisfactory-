import bpy, math, os, random
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
OUT=os.path.join(ROOT,"assets","models","resources")
os.makedirs(OUT,exist_ok=True)
bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1.0

def mat(n,c,m=.15,r=.8,e=0):
    x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.diffuse_color=(*c,1);x.use_nodes=True
    p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=m;p.inputs["Roughness"].default_value=r
    if e and "Emission Color" in p.inputs:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
    return x
ROCK=mat("Alien basalt",(.13,.15,.15),.08,.92);DARK=mat("Basalt shadow",(.045,.055,.06),.05,.95)
IRON=mat("Iron ore",(.42,.22,.12),.22,.76);COPPER=mat("Copper ore",(.70,.30,.12),.52,.45)
LIME=mat("Limestone",(.62,.62,.52),.03,.95);COAL=mat("Coal",(.018,.022,.025),.03,.92)
GOLD=mat("Caterium",(.88,.62,.16),.75,.28);QUARTZ=mat("Quartz",(.65,.86,.88),.18,.22)
SULFUR=mat("Sulfur",(.93,.76,.12),.05,.72);BAUXITE=mat("Bauxite",(.56,.19,.12),.08,.9)
SAM=mat("SAM mineral",(.24,.12,.45),.42,.35,.12);OIL=mat("Crude petroleum",(.025,.035,.04),.15,.18)
CYAN=mat("Resource node glow",(.02,.42,.52),.25,.22,1.4);YELLOW=mat("Safety yellow",(1,.61,.025),.18,.34)
MATS={"iron_ore":IRON,"copper_ore":COPPER,"limestone":LIME,"coal":COAL,"caterium_ore":GOLD,"raw_quartz":QUARTZ,"sulfur":SULFUR,"bauxite":BAUXITE,"sam":SAM}
spec={
"iron_ore_node":("Iron Ore Resource Node","iron_ore",3.2),
"copper_ore_node":("Copper Ore Resource Node","copper_ore",3.0),
"limestone_node":("Limestone Resource Node","limestone",3.0),
"coal_node":("Coal Resource Node","coal",3.1),
"caterium_ore_node":("Caterium Ore Resource Node","caterium_ore",3.0),
"raw_quartz_node":("Raw Quartz Resource Node","raw_quartz",3.0),
"sulfur_node":("Sulfur Resource Node","sulfur",3.0),
"bauxite_node":("Bauxite Resource Node","bauxite",3.1),
"sam_node":("SAM Resource Node","sam",3.2),
"resource_well_main":("Resource Well Main Node","sam",4.5),
"resource_well_satellite":("Resource Well Satellite Node","sam",2.0),
"geyser":("Geothermal Geyser","sam",3.0),
"crude_oil_node":("Crude Oil Resource Node","oil",3.2),
"cracked_resource_boulder":("Cracked Resource Boulder","iron_ore",3.6)
}
def root(n):
    o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);return o
def ico(n,p,scale,m,r,sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.name=n;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    for poly in o.data.polygons:poly.use_smooth=False
    o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=rad,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def tor(n,p,major,minor,m,r):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def build(kind,letter,variant):
    label,resource,size=spec[kind];rng=random.Random(1000+variant*31+sum(map(ord,kind)))
    r=root(label+"_Variant_"+letter)
    if kind=="resource_well_main":
        ico("Main geological mound",(0,0,.9),(size*.85,size*.85,1.4),ROCK,r,3)
        cyl("Pressurized well throat",(0,0,2.0),.9,1.8,DARK,r)
        for z,rad in ((1.5,1.0),(2.2,.8),(2.8,.62)):tor("Energy containment ring",(0,0,z),rad,.10,CYAN if z==2.2 else YELLOW,r)
        for i in range(8):
            a=math.tau*i/8;x,y=math.cos(a)*1.7,math.sin(a)*1.7
            ico("Satellite mineral spur",(x,y,.7),(.45,.45,.65),SAM,r,2)
    elif kind=="resource_well_satellite":
        ico("Satellite geological base",(0,0,.55),(1.4,1.2,.7),ROCK,r,2)
        cyl("Extraction socket",(0,0,1.1),.45,.7,DARK,r)
        tor("Socket energy ring",(0,0,1.45),.50,.08,CYAN,r)
        for i in range(5):
            a=math.tau*i/5;x,y=math.cos(a)*.8,math.sin(a)*.8
            ico("Mineral crystal",(x,y,1.1),(.25,.25,.55),SAM,r,1)
    elif kind=="geyser":
        ico("Geyser mound",(0,0,.5),(1.6,1.6,.7),ROCK,r,2)
        for i in range(7):
            a=math.tau*i/7;x,y=math.cos(a)*.85,math.sin(a)*.85
            ico("Vent rock",(x,y,.85),(.35,.35,.48),DARK,r,1)
        cyl("Vent throat",(0,0,.95),.62,.35,DARK,r)
        tor("Geothermal rim",(0,0,1.15),.68,.10,YELLOW,r)
        for z in (1.6,2.1,2.7):ico("Steam plume volume",(rng.uniform(-.15,.15),rng.uniform(-.15,.15),z),(.35,.35,.55),CYAN,r,1)
    elif kind=="crude_oil_node":
        ico("Oil-bearing rock",(0,0,.7),(size,size,.95),ROCK,r,3)
        cyl("Oil seep",(0,0,1.35),.85,.12,OIL,r)
        for i in range(5):
            a=math.tau*i/5;x,y=math.cos(a)*1.1,math.sin(a)*1.1
            ico("Oil stained stone",(x,y,.7),(.35,.4,.22),OIL,r,1)
    elif kind=="cracked_resource_boulder":
        ico("Cracked boulder core",(0,0,1.1),(size*.72,size*.68,1.3),DARK,r,2)
        # Visible split seam is a visual crack only; no explosive or weapon behavior.
        for i in range(8):
            a=math.tau*i/8
            ico("Ore-bearing fracture",(math.cos(a)*1.8,math.sin(a)*1.8,1.0),(.48,.36,.55),MATS[resource],r,1)
        box=None
    else:
        ico("Resource node bedrock",(0,0,.65),(size,size,.85),ROCK,r,3)
        count=9+variant*2
        for i in range(count):
            a=math.tau*i/count+rng.uniform(-.15,.15);rad=rng.uniform(.65,1.9)
            x,y=math.cos(a)*rad,math.sin(a)*rad
            h=rng.uniform(.45,1.25);s=rng.uniform(.28,.65)
            ico("Exposed ore formation",(x,y,.65+h*.40),(s,s*rng.uniform(.7,1.3),h),MATS[resource],r,1 if i%3 else 2)
        # small mineral inclusions around the crown
        for i in range(5):
            a=math.tau*i/5;x,y=math.cos(a)*.45,math.sin(a)*.45
            ico("Mineral inclusion",(x,y,1.35),(.18,.18,.25),MATS[resource],r,1)
    # Collision proxy; visual mesh remains separate.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1.1))
    c=bpy.context.object;c.name="COLLIDER_"+kind;c.dimensions=(size*2.5,size*2.5,3.2)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);c.display_type="WIRE";c.hide_render=True
    c["physics_role"]="resource_node_collision_proxy";c.parent=r
    r["asset_id"]="resource-"+kind.replace("_","-");r["variant"]=letter
    r["resource_family"]=resource;r["target_dimensions_m"]="provisional natural formation envelope; validate from in-game views."
    r["dimensions_status"]="unverified_blockout"
    return r
for kind in spec:
    folder=os.path.join(OUT,kind);os.makedirs(folder,exist_ok=True)
    for i,letter in enumerate("ABCD"):
        bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
        r=build(kind,letter,i);bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
        for o in r.children_recursive:o.select_set(True)
        bpy.context.view_layer.objects.active=r
        bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{kind}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
    bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
    for i,letter in enumerate("ABCD"):
        r=build(kind,letter,i);r.location.x=(i-1.5)*10
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{kind}_four_variants.blend"))
    print("Generated resource variants:",kind)
print("Resource-node batch complete:",len(spec),"families, 56 GLB exports.")
