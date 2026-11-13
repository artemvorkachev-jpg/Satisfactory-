import bpy, math, os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."));OUT=os.path.join(ROOT,"assets","models","equipment")
os.makedirs(OUT,exist_ok=True);bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1.0
def mat(n,c,m=.3,r=.4,e=0):
 x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.diffuse_color=(*c,1);x.use_nodes=True;p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=m;p.inputs["Roughness"].default_value=r
 if e and "Emission Color" in p.inputs:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
 return x
A=mat("Equipment amber enamel",(.82,.29,.055),.48,.32);D=mat("Equipment graphite",(.045,.06,.07),.82,.28);S=mat("Equipment steel",(.34,.39,.41),.86,.25);G=mat("Equipment glass",(.025,.16,.19),.45,.18);Y=mat("Equipment safety yellow",(1,.61,.025),.18,.34);C=mat("Equipment cyan",(.02,.42,.52),.25,.22,1.5);R=mat("Equipment rubber",(.018,.022,.025),.02,.78)
def root(n):o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);return o
def box(n,p,d,m,r,b=.02,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d
 if rot:o.rotation_euler=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.name=n;o.data.materials.append(m)
 if b:q=o.modifiers.new("Manufactured edge radii","BEVEL");q.width=b;q.segments=3;o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 o.parent=r;return o
def cyl(n,p,rad,dep,m,r,rot=(0,0,0),v=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=dep,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
def tor(n,p,major,minor,m,r,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.parent=r;return o
spec={"beacon":"Beacon","zipline":"Zipline","build_gun":"Build Gun","color_gun":"Color Gun","boombox":"Boom Box","medicinal_inhaler":"Medicinal Inhaler"}
def build(kind,letter,v):
 r=root(spec[kind]+"_Variant_"+letter)
 # hand-held tools use a consistent 0.3-0.5 m form factor.
 if kind=="beacon":
  cyl("Beacon base",(0,0,.12),.22,.18,D,r);cyl("Beacon mast",(0,0,.48),.055,.62,S,r);cyl("Beacon lamp",(0,0,.82),.20,.22,C if v%2==0 else Y,r)
  tor("Lamp guard",(0,0,.82),.22,.035,Y,r);box("Mounting magnet",(0,0,.02),(.30,.30,.06),D,r)
 elif kind=="zipline":
  box("Grip handle",(0,0,.15),(.42,.22,.30),R,r);box("Trigger guard",(0,-.08,.25),(.18,.08,.20),S,r)
  cyl("Cable spool",(0,.22,.40),.22,.15,D,r,(math.pi/2,0,0));tor("Spool rim",(0,.22,.40),.20,.025,Y,r,(math.pi/2,0,0))
  box("Cable guide",(0,.38,.40),(.16,.30,.12),A,r);cyl("Attachment eye",(0,.55,.40),.10,.08,S,r,(math.pi/2,0,0))
 elif kind in ("build_gun","color_gun"):
  box("Tool grip",(0,0,.18),(.24,.30,.48),R,r,rot=(.10,0,0));box("Tool body",(0,-.12,.53),(.42,.68,.42),A if kind=="build_gun" else S,r,.05)
  cyl("Tool barrel",(0,-.52,.57),.12,.34,D,r,(math.pi/2,0,0));tor("Emitter rim",(0,-.70,.57),.13,.035,C if kind=="build_gun" else Y,r,(math.pi/2,0,0))
  box("Top display",(0,-.12,.77),(.24,.035,.12),G,r);box("Side module",(.24,-.10,.48),(.12,.32,.20),D,r)
  for z in (.34,.45,.56):cyl("Status indicator",(.30,-.10,z),.025,.025,C,r,(0,math.pi/2,0),16)
  if kind=="color_gun":
   cyl("Color cartridge",(0,.26,.50),.12,.40,Y,r);tor("Cartridge ring",(0,.26,.50),.13,.025,A,r,(math.pi/2,0,0))
 elif kind=="boombox":
  box("Speaker cabinet",(0,0,.40),(.86,.28,.52),D,r,.06)
  for x in (-.25,.25):
   cyl("Speaker cone",(x,-.16,.42),.17,.06,S,r,(math.pi/2,0,0));tor("Speaker surround",(x,-.20,.42),.17,.025,A,r,(math.pi/2,0,0))
  box("Display",(0,-.17,.70),(.30,.035,.10),C,r);box("Handle",(0,0,.74),(.56,.10,.07),Y,r)
  for x in (-.32,.32):cyl("Control knob",(x,-.18,.67),.045,.04,S,r,(math.pi/2,0,0),20)
 else:
  box("Inhaler body",(0,0,.35),(.24,.22,.68),A,r,.045);cyl("Mouthpiece",(0,-.17,.68),.07,.20,S,r,(math.pi/2,0,0))
  box("Dose window",(0,-.12,.36),(.12,.035,.24),G,r);cyl("Release button",(0,0,.75),.07,.09,Y,r)
  for z in (.27,.35,.43):box("Dose marking",(0,-.145,z),(.08,.018,.018),C,r,.004)
 # Variant-specific details, while retaining the same item identity and use.
 if v==1:box("Reinforced side armor",(.25,0,.48),(.08,.35,.45),Y,r)
 elif v==2:
  for z in (.2,.4,.6):tor("Service ring",(0,0,z),.17,.018,S,r)
 elif v==3:box("Modular attachment rail",(0,.20,.60),(.10,.12,.34),S,r)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.42));c=bpy.context.object;c.name="COLLIDER_"+kind;c.dimensions=(1.0,.9,1.1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);c.display_type="WIRE";c.hide_render=True;c["physics_role"]="handheld_equipment_proxy";c.parent=r
 r["asset_id"]="equipment-"+kind.replace("_","-");r["variant"]=letter;r["dimensions_status"]="unverified_blockout"
 return r
for kind in spec:
 folder=os.path.join(OUT,kind);os.makedirs(folder,exist_ok=True)
 for i,letter in enumerate("ABCD"):
  bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False);r=build(kind,letter,i)
  bpy.ops.object.select_all(action="DESELECT");r.select_set(True)
  for o in r.children_recursive:o.select_set(True)
  bpy.context.view_layer.objects.active=r
  bpy.ops.export_scene.gltf(filepath=os.path.join(folder,f"{kind}_variant_{letter.lower()}.glb"),export_format="GLB",use_selection=True,export_apply=True)
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 for i,letter in enumerate("ABCD"):
  r=build(kind,letter,i);r.location.x=(i-1.5)*2.0
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,f"{kind}_four_variants.blend"))
 print("Generated noncombat equipment:",kind)
print("Equipment batch complete:",len(spec),"families, 24 GLB exports.")
