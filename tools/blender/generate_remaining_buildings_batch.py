import bpy, math, os, re
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
REG=os.path.join(ROOT,"tools","blender","BUILDINGS_AND_INFRASTRUCTURE_REGISTER.md")
OUT=os.path.join(ROOT,"assets","models","buildings")
os.makedirs(OUT,exist_ok=True);bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1.0
def mat(n,c,m=.35,r=.42,e=0):
 x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.diffuse_color=(*c,1);x.use_nodes=True;p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=m;p.inputs["Roughness"].default_value=r
 if e and "Emission Color" in p.inputs:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
 return x
A=mat("Building amber enamel",(.82,.29,.055),.48,.32);D=mat("Building graphite",(.045,.06,.07),.82,.28);S=mat("Building steel",(.34,.39,.41),.86,.25);G=mat("Building glass",(.025,.16,.19),.45,.18);Y=mat("Building safety yellow",(1,.61,.025),.18,.34);C=mat("Building cyan status",(.02,.42,.52),.25,.22,1.4);CON=mat("Building concrete",(.30,.32,.31),.05,.82)
def root(n):o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);return o
def box(n,p,d,m,r,b=.035,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d
 if rot:o.rotation_euler=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.name=n;o.data.materials.append(m)
 if b:q=o.modifiers.new("Manufactured edge radii","BEVEL");q.width=b;q.segments=3;o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0),v=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def tor(n,p,ma,mi,m,r,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=ma,minor_radius=mi,major_segments=32,minor_segments=8,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
skip=set("""building-smelter building-foundry building-constructor building-assembler building-manufacturer building-refinery building-blender building-packager building-particle-accelerator building-quantum-encoder building-converter building-portable-miner building-miner building-oil-extractor building-water-extractor building-power-pole building-power-tower building-power-storage building-power-switch building-conveyor-belt building-conveyor-lift building-conveyor-pole building-conveyor-splitter building-conveyor-merger building-pipeline building-pipeline-junction building-pipeline-pump building-fluid-buffer building-hypertube building-hypertube-entrance building-hypertube-junction building-train-station building-empty-platform building-freight-platform building-fluid-freight-platform building-railway building-storage-container building-awesome-sink""".split())
def build(aid,letter,v):
 slug=aid.replace("building-","");r=root(slug+"_Variant_"+letter)
 # dimensions are generic blockout envelopes, deliberately marked unverified.
 w,d,h=8.0,8.0,5.0
 if any(k in slug for k in ("space-elevator","portal","radar-tower","lookout-tower","power-line")):w,d,h=12,12,22
 if any(k in slug for k in ("drone-port","truck-station","hub","blueprint-designer","nuclear-power-plant")):w,d,h=16,16,10
 if any(k in slug for k in ("wall","window","door","conveyor-wall","conveyor-floor-hole","wall-outlet")):w,d,h=8,.6,4
 if any(k in slug for k in ("beam","pillar","ladder","pipe-support","conveyor-wall-mount","hypertube-support")):w,d,h=2,2,4
 # Foundation and service feet.
 box("Foundation",(0,0,.22),(w*.92,d*.92,.44),CON,r,.06)
 for x in (-w*.38,w*.38):
  for y in (-d*.38,d*.38):box("Mounting foot",(x,y,.10),(.45,.45,.20),S,r,.02)
 if any(k in slug for k in ("generator","pressurizer","extractor","drone-port","truck-station","hub","mam","shop","workshop","crafting-bench","blueprint","radar","space-elevator","portal","depot","elevator","landing-pad","jump-pad")):
  box("Main structural housing",(0,0,h*.38),(w*.72,d*.70,h*.62),D if v%2 else A,r,.12)
  for x in (-w*.24,w*.24):
   box("Service bay",(x,-d*.36,h*.40),(w*.18,.06,h*.30),G,r,.025)
   box("Protective frame",(x,-d*.40,h*.40),(w*.22,.10,h*.36),S,r,.025)
  if any(k in slug for k in ("generator","extractor","pressurizer")):
   for x in (-w*.25,w*.25):
    cyl("Vertical process vessel",(x,0,h*.75),w*.10,h*.55,S,r)
    tor("Vessel rim",(x,0,h*.98),w*.10,.05,Y,r)
   for z in (h*.3,h*.65):box("Service walkway",(0,0,z),(w*.88,d*.78,.12),S,r,.02)
  if "space-elevator" in slug:
   for z in (h*.45,h*.65,h*.85):
    tor("Elevator collar",(0,0,z),w*.42,.25,Y,r)
   box("Central elevator spine",(0,0,h*.75),(w*.22,d*.22,h*.85),S,r,.08)
  if "portal" in slug:
   tor("Portal aperture",(0,0,h*.58),w*.28,.45,C,r,(math.pi/2,0,0))
   tor("Outer portal frame",(0,0,h*.58),w*.38,.30,A,r,(math.pi/2,0,0))
  if "radar" in slug or "lookout" in slug:
   box("Tower mast",(0,0,h*.72),(w*.14,d*.14,h*.9),S,r,.03)
   cyl("Antenna dish",(0,0,h*.98),w*.30,.18,G,r)
  if "drone-port" in slug:
   box("Landing deck",(0,0,h*.80),(w*.90,d*.90,.28),Y,r,.05)
   for x in (-w*.28,w*.28):
    for y in (-d*.28,d*.28):cyl("Landing beacon",(x,y,h*.92),.20,.18,C,r)
  if "truck-station" in slug:
   box("Vehicle bay",(0,-d*.15,h*.55),(w*.9,d*.35,h*.42),S,r,.05)
   for x in (-w*.35,w*.35):box("Loading arm",(x,0,h*.65),(.3,d*.8,.3),Y,r)
  if "jump-pad" in slug or "landing-pad" in slug:
   tor("Launch field ring",(0,0,h*.45),w*.30,.18,C,r)
   box("Landing surface",(0,0,h*.30),(w*.78,d*.78,.18),Y,r)
  if "elevator" in slug and "space-elevator" not in slug:
   box("Lift shaft",(0,0,h*.62),(w*.40,d*.40,h*.95),S,r)
   box("Lift cabin",(0,-d*.30,h*.40),(w*.38,.28,h*.32),A,r)
 elif any(k in slug for k in ("conveyor","pipeline","hypertube","valve","power","train-signal","buffer-stop","vehicle-path")):
  box("Equipment body",(0,0,h*.42),(w*.72,d*.65,h*.65),D,r,.08)
  if "valve" in slug:
   cyl("Valve pipe",(0,0,h*.50),.30,w*.9,S,r,(0,math.pi/2,0))
   tor("Valve wheel",(0,0,h*.85),.42,.06,Y,r)
   cyl("Valve stem",(0,0,h*.78),.08,.42,S,r)
  elif "signal" in slug:
   box("Signal mast",(0,0,h*.70),(.18,.18,h*.95),S,r)
   for z in (h*.55,h*.72,h*.89):cyl("Signal lamp",(0,-.18,z),.16,.08,C if z==h*.72 else Y,r,(math.pi/2,0,0))
  elif "power-line" in slug:
   box("Conductor cable",(0,0,h*.70),(w,.08,.08),S,r)
   for x in (-w*.42,0,w*.42):cyl("Cable clamp",(x,0,h*.70),.16,.16,Y,r)
  else:
   for x in (-w*.28,w*.28):
    box("Support strut",(x,0,h*.5),(.18,.18,h*.8),S,r)
   box("Connection plate",(0,-d*.36,h*.50),(w*.55,.06,.45),Y,r)
 elif any(k in slug for k in ("foundation","ramp","walkway","stairs","shelf","beam","pillar","wall","window","door","ladder","angled-frame")):
  if "foundation" in slug:box("Foundation slab",(0,0,.40),(w,d,.8),CON,r,.06)
  elif "beam" in slug:box("Structural beam",(0,0,h*.5),(w*.95,.45,.45),S,r,.035)
  elif "pillar" in slug:box("Structural pillar",(0,0,h*.5),(.55,.55,h),D,r,.05)
  elif "wall" in slug and "conveyor" not in slug:box("Wall panel",(0,0,h*.5),(w,.28,h),D,r,.04)
  elif "window" in slug or "angled-frame" in slug:
   box("Window frame",(0,0,h*.5),(w,.22,h),S,r,.03)
   box("Glazing",(0,-.13,h*.5),(w*.82,.05,h*.78),G,r,.015)
  elif "door" in slug:
   box("Door leaf",(0,0,h*.5),(w*.45,.20,h*.9),A,r,.04)
   for x in (-w*.25,w*.25):box("Door jamb",(x,0,h*.5),(.20,.3,h),S,r)
  elif "ramp" in slug:box("Ramp deck",(0,0,h*.32),(w,d*.9,.28),S,r,.025,rot=(0,.28,0))
  elif "stairs" in slug:
   for i in range(8):box("Stair tread",(0,-d*.42+i*d*.12,.25+i*.24),(w*.75,.55,.18),S,r,.02)
  elif "walkway" in slug:
   box("Walkway deck",(0,0,.75),(w,d*.45,.18),S,r)
   for x in (-w*.45,w*.45):box("Walkway rail",(x,0,1.3),(.10,d*.45,.10),Y,r)
  elif "ladder" in slug:
   for x in (-.35,.35):box("Ladder rail",(x,0,h*.5),(.10,.12,h),S,r)
   for z in [i*.35+.2 for i in range(1,10)]:box("Ladder rung",(0,0,z),(.8,.12,.08),Y,r)
  elif "shelf" in slug:
   for z in (.6,1.6,2.6):box("Shelf deck",(0,0,z),(w*.8,d*.45,.14),S,r)
   for x in (-w*.35,w*.35):box("Shelf upright",(x,0,1.6),(.12,.12,3.2),D,r)
  else:box("Architecture panel",(0,0,h*.5),(w*.8,d*.5,h*.8),D,r)
 else:
  # Smaller electrical, fluid, sign and lighting fixtures.
  box("Fixture housing",(0,0,h*.45),(w*.68,d*.55,h*.62),D,r,.06)
  box("Control face",(0,-d*.30,h*.55),(w*.36,.05,h*.25),G,r,.015)
  if "light" in slug or "fan" in slug:
   if "fan" in slug:
    tor("Fan guard",(0,-d*.34,h*.55),w*.25,.05,S,r,(math.pi/2,0,0))
    cyl("Fan hub",(0,-d*.36,h*.55),.12,.10,Y,r,(math.pi/2,0,0))
    for a in range(4):box("Fan blade",(math.cos(a*math.pi/2)*.22,-d*.37,h*.55+math.sin(a*math.pi/2)*.22),(.12,.04,.42),S,r,.015,rot=(0,a*math.pi/2,0))
   else:
    cyl("Light lens",(0,-d*.32,h*.55),.28,.10,C,r,(math.pi/2,0,0))
  if "sign" in slug:box("Display panel",(0,-d*.38,h*.62),(w*.7,.08,h*.42),C,r,.02)
 # Generic snap/collision metadata. Connectors are not yet runtime-tested.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,h*.5));c=bpy.context.object;c.name="COLLIDER_"+slug;c.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);c.display_type="WIRE";c.hide_render=True;c["physics_role"]="building_collision_proxy";c.parent=r
 r["asset_id"]=aid;r["variant"]=letter;r["dimensions_status"]="unverified_blockout";r["target_dimensions_m"]=f"{w} x {d} x {h} provisional, verify from in-game build menu and reference views."
 return r
ids=[]
with open(REG,encoding="utf-8") as f:
 for line in f:
  m=re.match(r"^\|\s*(building-[a-z0-9-]+)\s*\|",line)
  if m and m.group(1) not in skip:ids.append(m.group(1))
for aid in ids:
 slug=aid.replace("building-","");folder=os.path.join(OUT,slug);os.makedirs(folder,exist_ok=True)
 for i,letter in enumerate("ABCD"):
  bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False);r=build(aid,letter,i)
  bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
  for o in r.children_recursive:o.select_set(True)
  bpy.context.view_layer.objects.active=r
  bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{slug}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 for i,letter in enumerate("ABCD"):
  r=build(aid,letter,i);r.location.x=(i-1.5)*18
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{slug}_four_variants.blend"))
 print("Generated remaining building:",aid)
print("Remaining building batch complete:",len(ids),"families,",len(ids)*4,"GLB exports.")
