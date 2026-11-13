import bpy, math, os, re, hashlib
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
REG=os.path.join(ROOT,"tools","blender","ITEMS_AND_NONCOMBAT_EQUIPMENT_REGISTER.md")
ADD=os.path.join(ROOT,"tools","blender","ITEMS_REGISTER_ADDENDUM.md")
OUT=os.path.join(ROOT,"assets","models","items")
os.makedirs(OUT,exist_ok=True)
bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1.0

def mat(n,c,m=.25,r=.42,e=0):
 x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.diffuse_color=(*c,1);x.use_nodes=True;p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=m;p.inputs["Roughness"].default_value=r
 if e and "Emission Color" in p.inputs:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
 return x
D=mat("Item graphite alloy",(.055,.07,.075),.78,.3);S=mat("Item brushed metal",(.48,.52,.52),.82,.25)
A=mat("Item amber enamel",(.85,.32,.06),.42,.34);Y=mat("Item safety yellow",(1,.65,.06),.18,.38)
G=mat("Item dark glass",(.025,.18,.20),.45,.18);C=mat("Item cyan emission",(.02,.48,.58),.2,.22,1.4)
R=mat("Item rubber",(.018,.022,.025),.02,.8);P=mat("Item polymer",(.18,.22,.23),.05,.7)
Q=mat("Item crystal",(.22,.58,.65),.2,.22);O=mat("Item organic",(.30,.42,.18),.02,.82)
def root(n):o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);return o
def cube(n,p,d,m,r,b=.018,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d
 if rot:o.rotation_euler=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.name=n;o.data.materials.append(m)
 if b:q=o.modifiers.new("Soft manufactured edges","BEVEL");q.width=b;q.segments=2;o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0),v=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def ico(n,p,sc,m,r,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.name=n;o.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);o.parent=r;return o
def tor(n,p,major,minor,m,r,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=24,minor_segments=6,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o

def classify(aid):
 s=aid.replace("item-","").replace("consumable-","")
 if any(k in s for k in ("packaged-","canister","fluid-tank")):return "container"
 if any(k in s for k in ("crystal","diamond","shard","sphere","somersloop","matrix","oscillator","singularity")):return "crystal"
 if any(k in s for k in ("plate","sheet","coupon","petals","fabric","concrete","silica","powder","scrap","pasta","resin","plastic","rubber","biomass","protein","remains","nut","berry","agaric","uranium","ore","coal","limestone","bauxite","quartz","sam")):return "material"
 if any(k in s for k in ("ingot",)):return "ingot"
 if any(k in s for k in ("rod","beam","pipe","screw","wire","cable","quickwire")):return "linear"
 if any(k in s for k in ("motor","rotor","stator","engine","cooling-system","heat-sink","modular-frame")):return "mechanical"
 if any(k in s for k in ("frame","system","unit","server","computer","processor","connector","board","control","director","wiring","plating","plating","cell","generator","sculptor","cube","rocket","framework","parts")):return "electronics"
 if "inhaler" in s:return "consumable"
 return "component"

def make(aid,letter,v):
 kind=classify(aid);r=root(aid+"_Variant_"+letter)
 # Palette and silhouette are based on item family, not an assertion of exact in-game mesh.
 accent=[A,S,Y,C][v];base=[D,S,P,R][v]
 if kind=="container":
  cyl("Container shell",(0,0,.34),.30,.62,base,r)
  cyl("Container top",(0,0,.68),.31,.10,accent,r)
  cyl("Container cap",(0,0,.76),.14,.10,D,r)
  tor("Container seam",(0,0,.42),.30,.025,Y,r)
  cube("Fluid label",(0,-.30,.38),(.24,.025,.20),G,r,.008)
  cube("Fill window",(0,-.318,.40),(.08,.012,.12),C,r,.004)
 elif kind=="crystal":
  ico("Faceted crystal",(0,0,.38),(.34,.30,.48),Q if v%2==0 else C,r,2)
  for x in (-.22,.22):
   ico("Crystal shard",(x,.02,.25),(.13,.12,.28),accent,r,1)
  tor("Crystal containment ring",(0,0,.12),.36,.035,D,r)
 elif kind=="ingot":
  cube("Metal ingot",(0,0,.30),(.72,.34,.22),accent,r,.045,rot=(0,0,v*.12))
  cube("Ingot stamped mark",(0,-.18,.30),(.24,.015,.06),D,r,.005)
 elif kind=="linear":
  if "wire" in aid or "cable" in aid or "screw" in aid:
   tor("Coiled conductor",(0,0,.30),.25,.045,accent,r)
   for z in (.12,.48):cyl("Coil end",(0,0,z),.05,.12,S,r)
  else:
   cube("Long component",(0,0,.30),(.16,.16,.72),accent,r,.02,rot=(0,0,v*.10))
   for z in (.08,.52):tor("Machined collar",(0,0,z),.13,.025,Y,r)
 elif kind=="mechanical":
  cyl("Mechanical core",(0,0,.34),.26,.48,D,r)
  tor("Rotor ring",(0,0,.34),.29,.055,accent,r)
  for i in range(6):
   a=math.tau*i/6
   cube("Cooling fin",(math.cos(a)*.28,math.sin(a)*.28,.34),(.08,.08,.34),S,r,.01,rot=(0,0,a))
  cyl("Shaft",(0,0,.68),.09,.24,S,r)
 elif kind=="electronics":
  cube("Electronics carrier",(0,0,.25),(.62,.48,.12),D,r,.025)
  for x in (-.20,0,.20):
   cube("Electronic module",(x,0,.36),(.14,.22,.12),accent,r,.012)
   for y in (-.16,.16):cyl("Connector pin",(x,y,.18),.025,.08,Y,r)
  cube("Circuit display",(0,-.25,.30),(.24,.025,.10),G,r,.006)
  for x in (-.08,0,.08):cube("Circuit trace",(x,.12,.32),(.018,.16,.015),C,r,.002)
 elif kind=="consumable":
  cyl("Consumable canister",(0,0,.32),.18,.55,A,r)
  cyl("Mouthpiece",(0,-.12,.64),.07,.20,S,r,(math.pi/2,0,0))
  cube("Dose window",(0,-.18,.32),(.10,.02,.22),G,r,.006)
 else:
  # Raw/refined materials, compact components and organic items.
  if any(k in aid for k in ("agaric","berry","nut","petals","protein","remains")):
   ico("Organic item",(0,0,.30),(.30,.26,.24),O,r,2)
   for x in (-.15,.15):ico("Organic detail",(x,-.05,.45),(.12,.10,.18),accent,r,1)
  elif "concrete" in aid or "biomass" in aid or "scrap" in aid or "waste" in aid:
   ico("Material chunk",(0,0,.30),(.34,.30,.25),base,r,1)
  elif "plate" in aid or "sheet" in aid or "coupon" in aid or "petals" in aid:
   cube("Flat material sheet",(0,0,.25),(.64,.48,.07),accent,r,.012)
   for x in (-.22,.22):
    for y in (-.14,.14):cyl("Sheet fastener",(x,y,.30),.025,.02,Y,r)
  else:
   cube("Component housing",(0,0,.30),(.48,.40,.30),base,r,.035)
   cube("Component faceplate",(0,-.21,.34),(.30,.025,.16),accent,r,.01)
   for x in (-.12,0,.12):cyl("Face indicator",(x,-.23,.34),.025,.02,C,r,(math.pi/2,0,0),16)
 # Four variants are controlled silhouette/detail alternatives.
 if v==1:cube("Variant reinforcement",(.30,0,.28),(.08,.34,.34),Y,r,.01)
 elif v==2:
  for z in (.16,.28,.40):tor("Variant collar",(0,0,z),.32,.018,S,r)
 elif v==3:cube("Variant modular rail",(0,.24,.32),(.36,.08,.10),Y,r,.01)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.35));col=bpy.context.object;col.name="COLLIDER_"+aid;col.dimensions=(.9,.8,1.0)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);col.display_type="WIRE";col.hide_render=True;col["physics_role"]="small_item_collision_proxy";col.parent=r
 r["asset_id"]=aid;r["variant"]=letter;r["family"]=kind;r["dimensions_status"]="unverified_item_blockout"
 return r

ids=set()
for path in (REG,ADD):
 with open(path,encoding="utf-8") as f:
  for line in f:
   m=re.match(r"^\|\s*((?:item|consumable)-[a-z0-9-]+)\s*\|",line)
   if m:ids.add(m.group(1))
# These are structural/collection records, modeled in their own building or creature families.
ids.discard("item-miner")
ids.discard("item-biomass-organic-variants")
for aid in sorted(ids):
 folder=os.path.join(OUT,aid);os.makedirs(folder,exist_ok=True)
 for i,letter in enumerate("ABCD"):
  bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False);r=make(aid,letter,i)
  bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
  for o in r.children_recursive:o.select_set(True)
  bpy.context.view_layer.objects.active=r
  bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{aid}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 for i,letter in enumerate("ABCD"):
  r=make(aid,letter,i);r.location.x=(i-1.5)*2.5
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{aid}_four_variants.blend"))
 print("Generated item:",aid)
print("Item batch complete:",len(ids),"distinct noncombat item families,",len(ids)*4,"GLB variants.")
