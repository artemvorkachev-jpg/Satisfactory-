import bpy, math, os, re, random
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."));REG=os.path.join(ROOT,"tools","blender","FAUNA_AND_FLORA_REGISTER.md");OUT=os.path.join(ROOT,"assets","models")
os.makedirs(OUT,exist_ok=True);bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1.0
def mat(n,c,m=.05,r=.8,e=0):
 x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.diffuse_color=(*c,1);x.use_nodes=True;p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=m;p.inputs["Roughness"].default_value=r
 if e and "Emission Color" in p.inputs:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
 return x
SKIN=mat("Fauna hide",(.34,.28,.20));DARK=mat("Fauna dark hide",(.09,.12,.13));PLATE=mat("Fauna carapace",(.24,.31,.26),.08,.62);EYE=mat("Fauna eye",(.02,.025,.03),.05,.2);GLOW=mat("Bioluminescent accent",(.08,.48,.46),.1,.25,1.0)
GREEN=mat("Alien foliage",(.12,.30,.12));GREEN2=mat("Alien leaf",(.28,.42,.12));BROWN=mat("Alien bark",(.22,.14,.08));PURPLE=mat("Alien flora purple",(.34,.18,.42));BLUE=mat("Alien flora blue",(.10,.28,.42));FLOWER=mat("Alien flower",(.88,.50,.12))
def root(n):o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);return o
def ico(n,p,s,m,r,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0),v=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def cone(n,p,rad,dep,m,r,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=rad,radius2=0,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def box(n,p,d,m,r,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;o.rotation_euler=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);o.parent=r;return o
def build_fauna(aid,letter,v):
 r=root(aid+"_Variant_"+letter);rng=random.Random(sum(map(ord,aid))+v*29);base=[SKIN,DARK,PLATE,SKIN][v];accent=[GLOW,PLATE,GLOW,FLOWER][v]
 slug="slug" in aid;bird="bird" in aid or "bat" in aid;manta="manta" in aid;crab=any(k in aid for k in ("crab","stinger","spitter","beetle","leaf-bug"));hog="hog" in aid;dog="doggo" in aid;giraffe="giraffe" in aid
 if slug or "power-slug" in aid:
  ico("Soft creature body",(0,0,.45),(.72,.48,.42),base,r,3)
  for x in (-.32,.32):cone("Sensory stalk",(x,-.02,.88),.10,.40,accent,r)
  ico("Creature eye",(0,-.42,.58),(.12,.06,.12),EYE,r,2)
  for i in range(4):
   a=math.tau*i/4;ico("Luminous spot",(math.cos(a)*.48,math.sin(a)*.28,.66),(.10,.10,.08),accent,r,1)
 elif manta:
  ico("Manta central body",(0,0,.55),(.65,1.0,.22),base,r,3)
  for side in (-1,1):
   ico("Manta wing",(side*1.0,.05,.48),(1.0,.78,.12),base,r,2)
   cone("Wing tip",(side*1.82,.12,.48),.22,.55,accent,r,(0,side*.35,0))
  ico("Manta tail",(0,1.35,.48),(.10,.65,.10),base,r,2)
 elif bird:
  ico("Bird body",(0,0,.55),(.35,.65,.38),base,r,2);ico("Bird head",(0,-.48,.82),(.28,.28,.27),base,r,2)
  cone("Beak",(0,-.78,.80),.13,.35,Y if False else accent,r,(math.pi/2,0,0))
  for side in (-1,1):
   ico("Wing",(side*.52,-.02,.64),(.65,.30,.12),accent,r,2)
   cyl("Leg",(side*.13,.12,.18),.045,.38,base,r)
 elif crab:
  ico("Creature thorax",(0,0,.55),(.48,.48,.35),base,r,2)
  ico("Carapace",(0,.02,.75),(.58,.58,.22),PLATE,r,2)
  for side in (-1,1):
   ico("Head",(side*.35,-.38,.62),(.20,.22,.18),base,r,1)
   for j in range(3):
    y=-.30+j*.30
    cyl("Jointed limb",(side*.62,y,.42),.07,.58,base,r,(0,side*.55,0))
    ico("Foot",(side*.90,y-.08,.12),(.10,.16,.10),DARK,r,1)
   cone("Antenna",(side*.32,-.58,1.0),.06,.35,accent,r,(.35*side,0,0))
 else:
  # Four-legged terrestrial forms: hogs, doggo, giraffe-like fauna.
  body_len=1.05 if not giraffe else 1.45
  ico("Creature torso",(0,0,.72),(body_len,.48,.48),base,r,3)
  head_y=-.70 if not giraffe else -.95
  ico("Creature head",(0,head_y,.88),(.38,.34,.35),base,r,2)
  if dog:
   for side in (-1,1):cone("Ear",(side*.24,head_y-.02,1.22),.13,.42,base,r,(0,side*.28,0))
  elif hog:
   for side in (-1,1):cone("Ear",(side*.24,head_y,1.15),.12,.28,accent,r,(0,side*.35,0))
   ico("Snout",(0,head_y-.30,.80),(.25,.18,.18),DARK,r,1)
  elif giraffe:
   cyl("Long neck",(0,-.58,1.25),.18,1.1,base,r,(math.pi/2.8,0,0))
   for z in (1.15,1.45,1.75):ico("Neck marking",(0,-.64,z),(.19,.08,.12),accent,r,1)
  for x in (-.34,.34):
   for y in (-.32,.38):
    cyl("Leg",(x,y,.35),.12,.65,base,r)
    ico("Foot",(x,y,.06),(.17,.22,.10),DARK,r,1)
  ico("Tail",(0,.82,.64),(.10,.38,.10),base,r,1)
 # Add eyes to all non-slug types.
 if not slug:
  for side in (-1,1):ico("Eye",(side*.16,-.74,.88),(.055,.045,.06),EYE,r,1)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.65));c=bpy.context.object;c.name="COLLIDER_"+aid;c.dimensions=(3.8,3.8,2.5);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);c.display_type="WIRE";c.hide_render=True;c["physics_role"]="fauna_collision_proxy";c.parent=r
 r["asset_id"]=aid;r["variant"]=letter;r["rig_status"]="static_blockout_not_rigged";r["dimensions_status"]="unverified_blockout"
 return r
def build_flora(aid,letter,v):
 r=root(aid+"_Variant_"+letter);rng=random.Random(sum(map(ord,aid))+v*13)
 if "vine" in aid:
  for i in range(3):
   x=(i-1)*.28
   cyl("Vine stem",(x,0,1.4),.07,2.8,BROWN,r)
   for z in (.4,.9,1.4,1.9,2.4):
    ico("Vine leaf",(x+(-1 if z%0.8<.4 else 1)*.28,0,z),(.30,.12,.12),GREEN2,r,1)
 elif "wood" in aid:
  cyl("Wood trunk",(0,0,.85),.32,1.7,BROWN,r)
  for i in range(5):
   a=math.tau*i/5;ico("Bark knot",(math.cos(a)*.26,math.sin(a)*.26,.75),(.12,.10,.20),DARK,r,1)
 elif "mushroom" in aid or "agaric" in aid or "spore-flower" in aid:
  cyl("Plant stalk",(0,0,.55),.15,1.1,GREEN,r)
  ico("Mushroom cap",(0,0,1.15),(.65,.65,.30),PURPLE if v%2==0 else BLUE,r,2)
  for i in range(7):
   a=math.tau*i/7;ico("Cap marking",(math.cos(a)*.42,math.sin(a)*.42,1.30),(.06,.06,.04),FLOWER,r,1)
 else:
  for i in range(7):
   a=math.tau*i/7;z=.5+(i%3)*.16
   ico("Leaf cluster",(math.cos(a)*.42,math.sin(a)*.42,z),(.36,.18,.12),GREEN if i%2 else GREEN2,r,2)
  cyl("Plant stem",(0,0,.55),.08,1.0,BROWN,r)
  if "flower" in aid or "petals" in aid:
   for i in range(6):
    a=math.tau*i/6;ico("Flower petal",(math.cos(a)*.18,math.sin(a)*.18,1.05),(.18,.10,.08),FLOWER,r,1)
   ico("Flower center",(0,0,1.08),(.10,.10,.10),Y if False else FLOWER,r,1)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1));c=bpy.context.object;c.name="COLLIDER_"+aid;c.dimensions=(2.4,2.4,3.0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);c.display_type="WIRE";c.hide_render=True;c["physics_role"]="flora_collision_proxy";c.parent=r
 r["asset_id"]=aid;r["variant"]=letter;r["dimensions_status"]="unverified_blockout"
 return r
# Read exact current IDs from the register; legacy and conceptual creatures are excluded.
fauna=[];flora=[]
with open(REG,encoding="utf-8") as f:
 for line in f:
  m=re.match(r"^\|\s*(fauna|flora)-([a-z0-9-]+)\s*\|",line)
  if not m:continue
  aid=m.group(1)+"-"+m.group(2)
  if m.group(1)=="fauna":
   if any(k in aid for k in ("-legacy","-concept","-reference")):continue
   fauna.append(aid)
  else:flora.append(aid)
for group,ids in (("creatures",fauna),("flora",flora)):
 for aid in ids:
  folder=os.path.join(OUT,group,aid);os.makedirs(folder,exist_ok=True)
  for i,letter in enumerate("ABCD"):
   bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
   r=build_fauna(aid,letter,i) if group=="creatures" else build_flora(aid,letter,i)
   bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
   for o in r.children_recursive:o.select_set(True)
   bpy.context.view_layer.objects.active=r
   bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{aid}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
  bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
  for i,letter in enumerate("ABCD"):
   r=build_fauna(aid,letter,i) if group=="creatures" else build_flora(aid,letter,i);r.location.x=(i-1.5)*5
  bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{aid}_four_variants.blend"))
  print("Generated",group,aid)
print("Fauna/flora batch complete:",len(fauna),"fauna and",len(flora),"flora asset families.")
