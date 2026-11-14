import * as THREE from "three";
import {GLTFLoader} from "three/addons/loaders/GLTFLoader.js";
import {initPhysics,addStaticCollider,createPlayerBody,stepPlayer,getPhysicsStats,probeDown} from "./physics.js";
import {createMachineState,tickMachine,setMachineRecipe,transferBelt,RECIPES,simulatePowerGrid} from "./production.js";
import {createAssetWorld,applyPbrTextures} from "./model-world.js";
const gltfLoader=new GLTFLoader();
const modelPaths={Hub:"../assets/models/buildings/hub/hub_variant_b.glb",Miner:"../assets/models/buildings/miner/miner_variant_b.glb",PortableMiner:"../assets/models/portable_miner/portable_miner_variant_b.glb",Smelter:"../assets/models/buildings/smelter/smelter_variant_b.glb",Constructor:"../assets/models/buildings/constructor/constructor_variant_b.glb",Storage:"../assets/models/infrastructure/storage_container/storage_container_variant_b.glb",BiomassBurner:"../assets/models/buildings/biomass-burner/biomass-burner_variant_b.glb",ConveyorBelt:"../assets/models/infrastructure/conveyor_belt/conveyor_belt_variant_b.glb",PowerPole:"../assets/models/infrastructure/power_pole/power_pole_variant_b.glb"};
const itemModelPaths={"Iron Ore":"../assets/models/items/item-iron-ore/item-iron-ore_variant_a.glb","Copper Ore":"../assets/models/items/item-copper-ore/item-copper-ore_variant_a.glb","Limestone":"../assets/models/items/item-limestone/item-limestone_variant_b.glb","Iron Ingot":"../assets/models/items/item-iron-ingot/item-iron-ingot_variant_b.glb","Copper Ingot":"../assets/models/items/item-copper-ingot/item-copper-ingot_variant_a.glb","Iron Plate":"../assets/models/items/item-iron-plate/item-iron-plate_variant_b.glb","Iron Rod":"../assets/models/items/item-iron-rod/item-iron-rod_variant_b.glb","Wire":"../assets/models/items/item-wire/item-wire_variant_a.glb","Cable":"../assets/models/items/item-cable/item-cable_variant_a.glb"};
function attachModel(parent,path,targetWidth=3){if(!path)return;const modelUrl=path+(path.includes("?")?"&":"?")+"v=20261114-pbr2";gltfLoader.load(modelUrl,g=>{const obj=g.scene;const b=new THREE.Box3().setFromObject(obj);const size=b.getSize(new THREE.Vector3());const center=b.getCenter(new THREE.Vector3());const scale=targetWidth/Math.max(size.x,size.z,0.01);obj.scale.setScalar(scale);obj.position.set(-center.x*scale,-b.min.y*scale,-center.z*scale);obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});applyPbrTextures(obj,parent.userData.node?"resources":"buildings");parent.add(obj);if(parent.userData.physicsStatic||parent.userData.machine||parent.userData.node||parent.userData.powerPoleId)addStaticModelCollider(parent);},undefined,e=>{console.warn("Model load failed:",path,e);if(parent.userData.physicsStatic||parent.userData.machine||parent.userData.node||parent.userData.powerPoleId)addStaticCollider(parent,{shape:"compound-building"})});}

const $=s=>document.querySelector(s);
const scene=new THREE.Scene();scene.background=new THREE.Color(0x78b9e8);scene.fog=new THREE.FogExp2(0xa8cbd8,0.00088);
const camera=new THREE.PerspectiveCamera(72,innerWidth/innerHeight,.1,1200);camera.position.set(0,2,8);
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:"high-performance"});renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.6));renderer.setSize(innerWidth,innerHeight); renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;$("#game").append(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xd8edff,0x43513b,2));
const sun=new THREE.DirectionalLight(0xfff2d8,2.9);sun.position.set(-35,55,25);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-180;sun.shadow.camera.right=180;sun.shadow.camera.top=180;sun.shadow.camera.bottom=-180;sun.shadow.bias=-0.00018;sun.shadow.normalBias=0.025;scene.add(sun);
const mat=(color,roughness=.85,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness});
function createGroundMaps(){
 const size=1024;
 let seed=82431;
 const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
 const colorCanvas=document.createElement("canvas");colorCanvas.width=colorCanvas.height=size;
 const ctx=colorCanvas.getContext("2d",{alpha:false});
 ctx.fillStyle="#7f9f52";ctx.fillRect(0,0,size,size);

 // Broad, softly blended Grass Fields colour variation: fresh grass, moss and sun-dried ground.
 const patches=[
  "#6f9148","#86a852","#789a4a","#93aa5d","#638648","#9bac62","#b19c6b","#a5a16a"
 ];
 for(let i=0;i<1400;i++){
  const x=rnd()*size,y=rnd()*size,rx=8+rnd()*100,ry=7+rnd()*75;
  ctx.globalAlpha=.035+rnd()*.105;
  ctx.fillStyle=patches[Math.floor(rnd()*patches.length)];
  ctx.beginPath();ctx.ellipse(x,y,rx,ry,rnd()*Math.PI,0,Math.PI*2);ctx.fill();
 }
 ctx.globalAlpha=1;

 // Fine grass blades, leaf litter and small ochre soil grains.
 for(let i=0;i<52000;i++){
  const x=rnd()*size,y=rnd()*size,len=1+rnd()*6;
  const palette=["#426b35","#527d3d","#9bb765","#b0b76a","#688a43","#789b4c"];
  ctx.strokeStyle=palette[Math.floor(rnd()*palette.length)];
  ctx.globalAlpha=.08+rnd()*.25;ctx.lineWidth=.35+rnd()*.8;
  const angle=-.55+rnd()*1.1;
  ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+Math.cos(angle)*len,y+Math.sin(angle)*len);ctx.stroke();
 }
 ctx.globalAlpha=1;
 for(let i=0;i<1700;i++){
  const x=rnd()*size,y=rnd()*size,r=.5+rnd()*1.8;
  ctx.fillStyle=rnd()>.82?"#c0aa70":rnd()>.5?"#536f3c":"#9ead62";
  ctx.globalAlpha=.18+rnd()*.35;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
 }
 // Small yellow field flowers, characteristic of the bright open Grass Fields palette.
 for(let i=0;i<180;i++){
  const x=rnd()*size,y=rnd()*size;
  ctx.globalAlpha=.5+rnd()*.4;ctx.fillStyle=rnd()>.35?"#e5d36e":"#d8c45b";
  for(let p=0;p<5;p++){
   const a=p*Math.PI*2/5,px=x+Math.cos(a)*2,py=y+Math.sin(a)*2;
   ctx.beginPath();ctx.arc(px,py,.8,0,Math.PI*2);ctx.fill();
  }
  ctx.fillStyle="#a87a36";ctx.beginPath();ctx.arc(x,y,.75,0,Math.PI*2);ctx.fill();
 }
 ctx.globalAlpha=1;

 const detailCanvas=document.createElement("canvas");detailCanvas.width=detailCanvas.height=size;
 const dctx=detailCanvas.getContext("2d",{alpha:false});
 dctx.fillStyle="#858585";dctx.fillRect(0,0,size,size);
 for(let i=0;i<38000;i++){
  const x=rnd()*size,y=rnd()*size,r=.5+rnd()*4;
  const v=Math.floor(92+rnd()*94);
  dctx.fillStyle="rgb("+v+","+v+","+v+")";dctx.globalAlpha=.12+rnd()*.3;
  dctx.beginPath();dctx.ellipse(x,y,r,r*(.35+rnd()*.75),rnd()*Math.PI,0,Math.PI*2);dctx.fill();
 }
 dctx.globalAlpha=1;
 for(let i=0;i<1200;i++){
  const x=rnd()*size,y=rnd()*size,len=3+rnd()*16,v=Math.floor(105+rnd()*80);
  dctx.strokeStyle="rgb("+v+","+v+","+v+")";dctx.lineWidth=.6+rnd()*1.5;
  dctx.beginPath();dctx.moveTo(x,y);dctx.lineTo(x+len*(rnd()-.5),y+len*(rnd()-.5));dctx.stroke();
 }
 const makeTexture=(canvas,colorSpace=THREE.NoColorSpace)=>{
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=colorSpace;texture.wrapS=texture.wrapT=THREE.RepeatWrapping;
  texture.repeat.set(12,12);texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  texture.generateMipmaps=true;texture.minFilter=THREE.LinearMipmapLinearFilter;texture.magFilter=THREE.LinearFilter;
  return texture;
 };
 return {map:makeTexture(colorCanvas,THREE.SRGBColorSpace),bumpMap:makeTexture(detailCanvas),roughnessMap:makeTexture(detailCanvas)};
}
const groundMaps=createGroundMaps();
const groundMaterial=mat(0xffffff,.96,0);
groundMaterial.map=groundMaps.map;groundMaterial.roughnessMap=groundMaps.roughnessMap;
groundMaterial.bumpMap=groundMaps.bumpMap;groundMaterial.bumpScale=.045;
const ground=new THREE.Mesh(new THREE.PlaneGeometry(700,700,1,1),groundMaterial);
ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);

const world=new THREE.Group();scene.add(world);createGroundFoliage(world);
function createGroundFoliage(parent){
 let foliageSeed=0x51a7f1;const rnd=()=>{foliageSeed=(foliageSeed*1664525+1013904223)>>>0;return foliageSeed/4294967296};
 const vertices=[];
 for(let blade=0;blade<3;blade++){
  const angle=blade*Math.PI*2/3,dx=Math.cos(angle),dz=Math.sin(angle),px=-dz*.045,pz=dx*.045;
  const bx=dx*.018,bz=dz*.018,h=.23+blade*.025;
  vertices.push(px,0,pz,-px,0,-pz,bx,h,bz);
 }
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute("position",new THREE.Float32BufferAttribute(vertices,3));geometry.computeVertexNormals();
 const material=new THREE.MeshStandardMaterial({color:0xffffff,roughness:1,side:THREE.DoubleSide});
 const count=2450,grass=new THREE.InstancedMesh(geometry,material,count),dummy=new THREE.Object3D();
 for(let i=0;i<count;i++){
  const a=rnd()*Math.PI*2,r=14+Math.sqrt(rnd())*112,h=.65+rnd()*1.25;
  dummy.position.set(Math.cos(a)*r,.015,Math.sin(a)*r);dummy.rotation.set(0,rnd()*Math.PI*2,0);
  dummy.scale.set(.65+rnd()*.6,h,.65+rnd()*.6);dummy.updateMatrix();grass.setMatrixAt(i,dummy.matrix);
  const col=new THREE.Color().setHSL(.235+rnd()*.075,.28+rnd()*.22,.25+rnd()*.2);grass.setColorAt(i,col);
 }
 grass.instanceMatrix.needsUpdate=true;if(grass.instanceColor)grass.instanceColor.needsUpdate=true;
 grass.castShadow=false;grass.receiveShadow=true;parent.add(grass);

 const flowerGeometry=new THREE.DodecahedronGeometry(.045,0);
 const flowerMaterial=new THREE.MeshStandardMaterial({color:0xe5cf64,roughness:.9});
 const flowerCount=260,flowers=new THREE.InstancedMesh(flowerGeometry,flowerMaterial,flowerCount);
 for(let i=0;i<flowerCount;i++){
  const a=rnd()*Math.PI*2,r=12+Math.sqrt(rnd())*112;
  dummy.position.set(Math.cos(a)*r,.07,Math.sin(a)*r);dummy.rotation.set(rnd(),rnd()*Math.PI*2,rnd());
  const s=.65+rnd()*.85;dummy.scale.set(s,s,s);dummy.updateMatrix();flowers.setMatrixAt(i,dummy.matrix);
  flowers.setColorAt(i,new THREE.Color().setHSL(.12+rnd()*.035,.48+rnd()*.32,.48+rnd()*.2));
 }
 flowers.instanceMatrix.needsUpdate=true;if(flowers.instanceColor)flowers.instanceColor.needsUpdate=true;
 parent.add(flowers);

 const rockGeometry=new THREE.DodecahedronGeometry(.55,0);
 const rockMaterial=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.96});
 const rockCount=190,rocks=new THREE.InstancedMesh(rockGeometry,rockMaterial,rockCount);
 for(let i=0;i<rockCount;i++){
  const a=rnd()*Math.PI*2,r=16+Math.sqrt(rnd())*112;
  dummy.position.set(Math.cos(a)*r,.1,Math.sin(a)*r);dummy.rotation.set(rnd()*.3,rnd()*Math.PI*2,rnd()*.3);
  const s=.25+rnd()*.95;dummy.scale.set(s,.3+rnd()*.55,s*(.65+rnd()*.8));dummy.updateMatrix();rocks.setMatrixAt(i,dummy.matrix);
  rocks.setColorAt(i,new THREE.Color().setHSL(.53+rnd()*.06,.08+rnd()*.11,.34+rnd()*.2));
 }
 rocks.instanceMatrix.needsUpdate=true;if(rocks.instanceColor)rocks.instanceColor.needsUpdate=true;
 rocks.castShadow=true;rocks.receiveShadow=true;parent.add(rocks);
}

const resourceNodes=[];const machines=[];const belts=[];const powerPoles=[];const powerConnections=[];let powerStart=null;let powerStats={capacity:0,consumption:0,poweredMachines:0,connectedMachines:0};let beltStart=null;const inventory={Leaves:0,Wood:0,Biomass:0,"Solid Biofuel":0,"Iron Ore":0,"Copper Ore":0,Limestone:0,"Iron Ingot":0,"Copper Ingot":0,"Iron Plate":0,"Iron Rod":0,Wire:0,Cable:0,Concrete:0,ReinforcedIronPlate:0};
const progression={stage:0,gathered:{},crafted:{},built:{}};
const milestones=[{name:"Первые ресурсы",goal:"Соберите по 20 железной руды, медной руды и известняка.",test:()=>["Iron Ore","Copper Ore","Limestone"].every(k=>(progression.gathered[k]||0)>=20)},{name:"Ручное производство",goal:"Изготовьте 10 железных слитков, 10 медных слитков и 10 бетона.",test:()=>["Iron Ingot","Copper Ingot","Concrete"].every(k=>(progression.crafted[k]||0)>=10)},{name:"Основные детали",goal:"Изготовьте 10 железных пластин, 10 стержней и 10 проволоки.",test:()=>["Iron Plate","Iron Rod","Wire"].every(k=>(progression.crafted[k]||0)>=10)},{name:"Первая фабрика",goal:"Постройте плавильню, конструктор и биомассовый генератор.",test:()=>["Smelter","Constructor","Biomass Burner"].every(k=>(progression.built[k]||0)>=1)},{name:"Автоматизация",goal:"Постройте добытчик и соедините машины конвейером.",test:()=>((progression.built.Miner||0)>=1&&(progression.built["Conveyor Belt"]||0)>=1)}];
const labels={"Iron Ore":"Железная руда","Copper Ore":"Медная руда","Limestone":"Известняк","Coal":"Уголь","Caterium Ore":"Катериумовая руда","Bauxite":"Боксит","Crude Oil":"Сырая нефть","Raw Quartz":"Сырой кварц","Sulfur":"Сера","SAM":"SAM-руда","Resource Well":"Ресурсная скважина","Geothermal Geyser":"Геотермальный гейзер","Resource Boulder":"Ресурсный валун","Leaves":"Листья","Wood":"Древесина","Beryl Nut":"Берилловый орех","Paleberry":"Палеягода","Bacon Agaric":"Беконный мухомор","Iron Ingot":"Железный слиток","Copper Ingot":"Медный слиток","Iron Plate":"Железная пластина","Iron Rod":"Железный стержень","Wire":"Проволока","Cable":"Кабель","Concrete":"Бетон","ReinforcedIronPlate":"Усиленная железная пластина"};
const recipes={
 "Iron Ingot":{inputs:{"Iron Ore":1},time:2,machine:"Smelter"},
 "Copper Ingot":{inputs:{"Copper Ore":1},time:2,machine:"Smelter"},
 "Iron Plate":{inputs:{"Iron Ingot":3},output:2,time:6,machine:"Constructor"},
 "Iron Rod":{inputs:{"Iron Ingot":1},time:4,machine:"Constructor"},
 "Wire":{inputs:{"Copper Ingot":1},output:2,time:.5,machine:"Constructor"},
 "Cable":{inputs:{Wire:2},time:2,machine:"Constructor"},
 "Concrete":{inputs:{Limestone:3},time:4,machine:"Constructor"}
};
let yaw=0,pitch=0,moveX=0,moveY=0,velocityY=0,onGround=true,menuMode="",selectedNode=null,selectedMachine=null,buildType=null,buildGhost=null,lastSave=0,toastTimer=0;
const player={position:new THREE.Vector3(0,1.7,8),speed:8};
window.__SATISFACTORY_PHYSICS__=()=>({...getPhysicsStats(),player:{x:player.position.x,y:player.position.y,z:player.position.z,grounded:onGround},probeDown,assets:assetWorld?.getStats()||null});
let playerBody=null,jumpBuffer=0;
initPhysics().then(async()=>{playerBody=createPlayerBody(player.position.x,0,player.position.z);assetWorld=await createAssetWorld(world,{skipIds:["hub"],onProgress:stats=>{const label=$("#objective");if(label&&progression.stage===0)label.textContent="После высадки: исследуйте биом · найдите железо, медь и известняк · природа загружена "+stats.loadedModels+"/"+stats.placedModels}});assetWorld.setResourceState(pendingResourceState);for(const item of pendingPlacedAssets){assetWorld.placeConstruction(item.id,new THREE.Vector3(item.x,item.y,item.z),item.rotationY||0).catch(e=>console.warn("Saved model restore failed",item.id,e))}assetWorld.update(player.position);ui("Окружение загружено. Исследуйте территорию и начинайте строить фабрику.");}).catch(e=>{console.warn("World/physics initialization failed",e);ui("Не удалось загрузить окружение планеты: "+e.message)});
const keys={};const raycaster=new THREE.Raycaster();const center=new THREE.Vector2(0,0);
function box(parent,x,y,z,sx,sy,sz,color){const m=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),mat(color));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m}
function makeTree(x,z,scale=1){const g=new THREE.Group();g.position.set(x,0,z);world.add(g);const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.16*scale,.23*scale,2.1*scale,7),mat(0x59412d));trunk.position.y=1.05*scale;trunk.castShadow=true;g.add(trunk);for(let i=0;i<3;i++){const crown=new THREE.Mesh(new THREE.ConeGeometry((1.1-i*.18)*scale,2.1*scale,7),mat([0x315b3a,0x3e7045,0x4a7947][i]));crown.position.y=(2.2+i*.68)*scale;crown.castShadow=true;g.add(crown)}addStaticCollider(trunk,{shape:"capsule",friction:0.95})}
function makeRock(x,z,color=0x777d78,s=1,collidable=true){const g=new THREE.Group();g.position.set(x,0,z);world.add(g);const r=new THREE.Mesh(new THREE.DodecahedronGeometry(s,1),mat(color));r.position.y=s*.6;r.scale.set(1,.8,1.15);r.castShadow=true;r.receiveShadow=true;g.add(r);if(collidable)addStaticCollider(g,{shape:"box",friction:0.9});return g}
function node(type,x,z,amount=240){const g=new THREE.Group();g.position.set(x,0,z);g.userData.node={type,amount};world.add(g);const path=type==="Iron Ore"?"../assets/models/resources/iron_ore_node/iron_ore_node_variant_c.glb":type==="Copper Ore"?"../assets/models/resources/copper_ore_node/copper_ore_node_variant_c.glb":"../assets/models/resources/limestone_node/limestone_node_variant_c.glb";attachModel(g,path,3.2);resourceNodes.push(g)}
// Starter outpost: real GLB assets replace the former primitive forest and mock factory.
// Natural resource outcrops are streamed from the planet's selected resource models.
const hub=new THREE.Group();hub.position.set(0,0,-1);hub.userData.physicsStatic=true;world.add(hub);attachModel(hub,modelPaths.Hub,5);
const pad=new THREE.Mesh(new THREE.CylinderGeometry(2.7,3.1,.4,32),mat(0x737e83,.78,.24));pad.position.set(0,.2,4.5);pad.castShadow=true;pad.receiveShadow=true;world.add(pad);addStaticCollider(pad,{shape:"cylinder",friction:0.9});
let assetWorld=null;let pendingResourceState={};let pendingPlacedAssets=[];
function makeMachine(type,pos,visualOverride=null){const g=new THREE.Group();g.position.copy(pos);const sim=createMachineState(type,"machine-"+(machines.length+1));g.userData.machine={...sim,buffer:sim.input,progress:0,powered:false,node:null};world.add(g);attachModel(g,modelPaths[visualOverride||type],3.1);machines.push(g);return g}
const clock=new THREE.Clock();
function ui(message){const toast=$("#toast");if(!toast)return;toast.textContent=message||"";toast.classList.toggle("show",Boolean(message));clearTimeout(toastTimer);if(message)toastTimer=setTimeout(()=>toast.classList.remove("show"),2600)}
function updateProgression(){while(progression.stage<milestones.length&&milestones[progression.stage].test())progression.stage++;const m=milestones[Math.min(progression.stage,milestones.length-1)];$("#objective").textContent=progression.stage>=milestones.length?"Автоматизация запущена · продолжайте расширять производство":m.name+" — "+m.goal;$("#stats").innerHTML="Этап: "+Math.min(progression.stage+1,milestones.length)+" / "+milestones.length+"<br>Построено машин: "+machines.length;}
function invText(){const entries=Object.entries(inventory).filter(([,v])=>v>0);$("#inventory").innerHTML="<b>Инвентарь</b><br>"+(entries.length?entries.map(([k,v])=>(labels[k]||k)+": "+v).join(" · "):"пусто")}
function showMenu(mode){
 menuMode=mode;
 $("#menu").style.display="grid";
 const grid=$("#menuGrid"),filters=$("#menuFilters"),search=$("#menuSearch"),category=$("#menuCategory");
 grid.replaceChildren();
 $("#menuTitle").textContent=mode==="build"?"Строительство":"Ручное производство";
 filters.style.display=mode==="build"?"grid":"none";
 $("#menuInfo").textContent=mode==="build"?"Основные установки и выбранные модели из каталога. Выберите объект, затем нажмите «Действие» для установки перед собой.":"Рецепты раннего этапа. Для машинного производства сначала постройте установку.";
 const buildItems=[
  ["Smelter","Плавильня","Iron Plate",5,2],["Constructor","Конструктор","Iron Rod",8,2],
  ["Storage","Контейнер","Iron Plate",4,3],["Biomass Burner","Биомассовый генератор","Iron Rod",15,3],
  ["Power Pole","Опора питания · 4 подключения","Iron Rod",1,2],["Power Line","Кабель электросети · до 100 м","Cable",1,2],
  ["Portable Miner","Переносной добытчик","Iron Plate",4,4],["Conveyor Belt","Конвейер Mk.1 · 60 предметов/мин","Iron Plate",1,4]
 ];
 const craftItems=[
  ["Biomass","10 листьев → 5 биомассы","Leaves",10,1],["Iron Ingot","1 железная руда → 1 слиток","Iron Ore",1,1],
  ["Copper Ingot","1 медная руда → 1 слиток","Copper Ore",1,1],["Concrete","3 известняка → 1 бетон","Limestone",3,1],
  ["Iron Plate","3 слитка → 2 пластины","Iron Ingot",3,2],["Iron Rod","1 слиток → 1 стержень","Iron Ingot",1,2],
  ["Wire","1 медный слиток → 2 проволоки","Copper Ingot",1,2],["Cable","2 проволоки → 1 кабель","Wire",2,3]
 ];
 const addButton=(name,description,callback)=>{
  const b=document.createElement("button");
  const title=document.createElement("b");title.textContent=name;
  const detail=document.createElement("span");detail.className="small";detail.textContent=description;
  b.append(title,document.createElement("br"),detail);
  b.addEventListener("click",callback);
  grid.append(b);
 };
 if(mode==="build"){
  for(const [name,description] of buildItems)addButton(name,description,()=>startBuild(name));
  const reserved=new Set(["smelter","constructor","storage_container","biomass-burner","power_pole","power-line","conveyor_belt","portable_miner","miner","hub"]);
  const catalog=assetWorld?.constructionCatalog||[];
  const categoryNames={buildings:"Здания",infrastructure:"Логистика",railway:"Железная дорога",portable_miner:"Добыча",items:"Предметы",tractor:"Тракторы",truck:"Грузовики",explorer:"Вездеходы",cyber_wagon:"Cyber Wagon",factory_cart:"Тележки",locomotive:"Локомотивы",train_station:"Ж/д станции",freight_car:"Грузовые вагоны",freight_platform:"Грузовые платформы",drone:"Дроны",blade_runners:"Экипировка",hoverpack:"Экипировка",jetpack:"Экипировка",parachute:"Экипировка",gas_mask:"Экипировка",hazmat_suit:"Экипировка",object_scanner:"Инструменты",cup:"Предметы"};
  const availableCategories=[...new Set(catalog.map(asset=>asset.category))].sort();
  const existingCategories=new Set(Array.from(category.options,option=>option.value));
  for(const value of availableCategories)if(!existingCategories.has(value)){
   const option=document.createElement("option");option.value=value;option.textContent=categoryNames[value]||value.replace(/[_-]+/g," ").replace(/\b\w/g,ch=>ch.toUpperCase());category.append(option);
  }
  const query=search.value.trim().toLowerCase(),kind=category.value;
  const extras=catalog.filter(asset=>!reserved.has(asset.id)&&(!kind||asset.category===kind)&&(!query||(asset.name+" "+asset.id+" "+asset.category).toLowerCase().includes(query)));
  for(const asset of extras){
   const categoryName=({buildings:"Здание",railway:"Железная дорога",portable_miner:"Добыча",infrastructure:"Инфраструктура",items:"Предмет",tractor:"Транспорт",truck:"Транспорт",explorer:"Транспорт",cyber_wagon:"Транспорт",factory_cart:"Транспорт",locomotive:"Железная дорога",train_station:"Железная дорога",freight_car:"Железная дорога",freight_platform:"Железная дорога",drone:"Дрон"})[asset.category]||"Экипировка и оборудование";
   addButton(asset.name,categoryName+" · модель "+String(asset.selectedVariant||"b").toUpperCase(),()=>startBuildAsset(asset.id,asset.name));
  }
  $("#menuInfo").textContent=catalog.length
   ?"Основные установки и "+extras.length+" моделей каталога. Фильтр помогает быстро найти объект."
   :"Каталог моделей ещё загружается. Основные установки уже доступны.";
 }else{
  for(const [name,description] of craftItems)addButton(name,description,()=>craftItem(name));
 }
 $("#menuStatus").textContent="Ресурсы: "+Object.entries(inventory).filter(([,v])=>v).map(([k,v])=>(labels[k]||k)+" "+v).join(", ");
}
function startBuildAsset(id,name){
 if(!assetWorld){ui("Каталог моделей ещё загружается. Повторите выбор через секунду.");return}
 buildType="asset:"+id;
 closeMenu();
 ui("Выбрано: "+name+". Нажмите «Действие», чтобы установить модель перед собой.");
}
function closeMenu(){$("#menu").style.display="none";menuMode=""}
function craftItem(name){const r=recipes[name];if(name==="Biomass"){if((inventory.Leaves||0)<10){ui("Не хватает листьев: 10");return}inventory.Leaves-=10;inventory.Biomass=(inventory.Biomass||0)+5;progression.crafted.Biomass=(progression.crafted.Biomass||0)+5;invText();updateProgression();ui("Изготовлено 5 биомассы.");return}if(!r){ui("Этот рецепт пока не открыт.");return}for(const [k,v] of Object.entries(r.inputs)){if((inventory[k]||0)<v){ui("Не хватает: "+(labels[k]||k));return}}for(const [k,v] of Object.entries(r.inputs))inventory[k]-=v;const made=r.output||1;inventory[name]=(inventory[name]||0)+made;progression.crafted[name]=(progression.crafted[name]||0)+made;invText();updateProgression();ui("Изготовлено: "+(labels[name]||name));}
function startBuild(type){const costs={"Power Line":{},"Power Pole":{"Iron Rod":1,"Wire":3,"Concrete":1},"Portable Miner":{"Iron Plate":4,"Iron Rod":4},"Smelter":{"Iron Plate":5,"Iron Rod":8},"Constructor":{"Iron Plate":6,"Iron Rod":8},"Storage":{"Iron Plate":4,"Iron Rod":4},"Biomass Burner":{"Iron Plate":15,"Iron Rod":15,"Wire":25},"Conveyor Belt":{"Iron Plate":1}};const c=costs[type];for(const [k,v] of Object.entries(c))if((inventory[k]||0)<v){ui("Для "+type+" не хватает "+(labels[k]||k)+": "+v);return}for(const [k,v] of Object.entries(c))inventory[k]-=v;buildType=type;closeMenu();ui("Наведите на землю и нажмите E, чтобы установить: "+type);invText()}
function buildAt(){
 if(!buildType)return;
 if(buildType.startsWith("asset:")){
  const assetId=buildType.slice(6);
  if(!assetWorld){ui("Каталог моделей ещё загружается.");return}
  const direction=new THREE.Vector3();camera.getWorldDirection(direction);direction.y=0;
  if(direction.lengthSq()<1e-6)direction.set(0,0,-1);direction.normalize();
  const position=player.position.clone().addScaledVector(direction,5);position.y=0;
  position.x=Math.round(position.x/2)*2;position.z=Math.round(position.z/2)*2;
  if(Math.hypot(position.x-player.position.x,position.z-player.position.z)>12){ui("Слишком далеко для строительства.");return}
  const asset=assetWorld.constructionCatalog.find(item=>item.id===assetId);
  if(!asset){ui("Эта модель отсутствует в выбранном каталоге.");buildType=null;return}
  buildType=null;
  assetWorld.placeConstruction(assetId,position,yaw).then(()=>ui(asset.name+" установлен.")).catch(error=>{console.warn("Model placement failed",assetId,error);ui("Не удалось загрузить модель "+asset.name+". Проверьте GLB-файл.")});
  return;
 }
 const target=targetObject();if(buildType==="Power Line"){const endpoint=target?.userData.machine?target.userData.machine.id:target?.userData.powerPoleId;if(!endpoint){ui("Подключайте кабель к машине или опоре электросети.");return}if(!powerStart){powerStart=endpoint;ui("Начало кабеля выбрано. Выберите вторую машину или опору.");return}if(powerStart===endpoint){ui("Выберите другой объект.");return}const a=powerStart,b=endpoint;const poleA=powerPoles.find(p=>p.userData.powerPoleId===a),poleB=powerPoles.find(p=>p.userData.powerPoleId===b);const degree=id=>powerConnections.filter(c=>c.a===id||c.b===id).length;if((poleA&&degree(a)>=4)||(poleB&&degree(b)>=4)||(!poleA&&degree(a)>=1)||(!poleB&&degree(b)>=1)){ui(poleA||poleB?"У опоры заняты все 4 разъёма или у машины уже есть кабель.":"У каждой машины может быть только один кабель.");return}const ga=[...machines,...powerPoles].find(g=>(g.userData.machine?.id||g.userData.powerPoleId)===a),gb=[...machines,...powerPoles].find(g=>(g.userData.machine?.id||g.userData.powerPoleId)===b);if(!ga||!gb||!(poleA||poleB)){ui("На этом этапе кабель соединяет здание только с опорой электросети.");return}const distance=ga.position.distanceTo(gb.position);if(distance>100){ui("Кабель не достаёт: максимум 100 м.");return}const cableCost=Math.max(1,Math.ceil(distance/25));if((inventory.Cable||0)<cableCost){ui("Для линии нужно кабеля: "+cableCost);return}inventory.Cable-=cableCost;invText();const curve=new THREE.LineCurve3(ga.position.clone().add(new THREE.Vector3(0,2,0)),gb.position.clone().add(new THREE.Vector3(0,2,0)));const wire=new THREE.Mesh(new THREE.TubeGeometry(curve,12,.035,6,false),mat(0x252a2b,.45,.4));world.add(wire);powerConnections.push({a,b,wire});powerStart=null;buildType=null;ui("Кабель подключён к электросети.");return}if(buildType==="Conveyor Belt"){if(!target?.userData.machine){ui("Для ленты сначала наведитесь на производственную машину и нажмите E.");return}if(!beltStart){beltStart=target;ui("Начало ленты выбрано. Теперь наведитесь на машину-получатель и нажмите E.");return}if(target===beltStart){ui("Выберите другую машину-получатель.");return}makeBelt(beltStart,target);progression.built["Conveyor Belt"]=(progression.built["Conveyor Belt"]||0)+1;updateProgression();beltStart=null;buildType=null;ui("Конвейер Mk.1 соединён: до 60 предметов в минуту.");return}const dir=new THREE.Vector3();camera.getWorldDirection(dir);let p=player.position.clone().add(dir.multiplyScalar(5));p.y=0;let linkedNode=null;if(buildType==="Portable Miner"){if(target?.userData.node){linkedNode=target;p=target.position.clone()}else{ui("Для Portable Miner наведитесь на ресурсный узел.");return}}p.x=Math.round(p.x/2)*2;p.z=Math.round(p.z/2)*2;if(Math.hypot(p.x-player.position.x,p.z-player.position.z)>12){ui("Слишком далеко для строительства.");return}const placedType=buildType;if(placedType==="Power Pole"){const pole=new THREE.Group();pole.position.copy(p);pole.userData.powerPoleId="power-pole-"+(powerPoles.length+1);world.add(pole);attachModel(pole,modelPaths.PowerPole,2.2);powerPoles.push(pole);buildType=null;ui("Опора электросети установлена. Выберите «Кабель электросети», чтобы подключить её.");return}const type=buildType==="Portable Miner"?"Miner":buildType;const m=makeMachine(type,p,buildType==="Portable Miner"?"PortableMiner":null);progression.built[placedType]=(progression.built[placedType]||0)+1;updateProgression();if(linkedNode){m.userData.machine.node=linkedNode;m.userData.machine.nodeType=linkedNode.userData.node.type;m.userData.machine.nodeRemaining=linkedNode.userData.node.amount}buildType=null;ui(type+" установлен. Подойдите и нажмите E для настройки.");}
function makeBelt(sourceGroup,targetGroup){const a=sourceGroup.position.clone().add(new THREE.Vector3(0,1.1,0));const b=targetGroup.position.clone().add(new THREE.Vector3(0,1.1,0));const mid=a.clone().lerp(b,.5);mid.y+=Math.min(1.2,a.distanceTo(b)*.12);const curve=new THREE.CatmullRomCurve3([a,mid,b]);const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,Math.max(12,Math.ceil(a.distanceTo(b)*3)),.16,8,false),mat(0x414d50));mesh.castShadow=true;world.add(mesh);const token=new THREE.Group();const fallback=new THREE.Mesh(new THREE.BoxGeometry(.32,.22,.32),mat(0xd4a33b));token.add(fallback);world.add(token);const belt={source:sourceGroup.userData.machine,target:targetGroup.userData.machine,curve,mesh,token,item:sourceGroup.userData.machine.type==="Miner"?sourceGroup.userData.machine.nodeType:sourceGroup.userData.machine.recipe,modelItem:null,elapsed:0,itemsPerSecond:1,active:true,visualT:0};belts.push(belt);}function interact(){if(buildType){buildAt();return}const target=targetObject();if(!target){ui("Здесь нет объекта для взаимодействия.");return}
if(target.userData.node){const n=target.userData.node;if(n.amount<=0){ui("Узел истощён. На месте остались каменные обломки.");return}const gathered=Math.min(25,n.amount);n.amount=Math.max(0,n.amount-gathered);assetWorld?.setNodeAmount?.(target,n.amount);inventory[n.type]=(inventory[n.type]||0)+gathered;progression.gathered[n.type]=(progression.gathered[n.type]||0)+gathered;invText();updateProgression();ui(n.amount===0?"Узел полностью истощён. На месте остались обломки.":"Собрано "+gathered+": "+(labels[n.type]||n.type));return}
if(target.userData.asset){const a=target.userData.asset;ui(a.name+" · "+a.category+" · вариант "+String(a.variant).toUpperCase());return}
if(target.userData.machine){selectedMachine=target;const m=target.userData.machine;if(m.type==="Biomass Burner"){m.fuel=m.fuel||{};let loaded=0;for(const kind of ["Biomass","Solid Biofuel"]){const amount=inventory[kind]||0;if(amount>0){m.fuel[kind]=(m.fuel[kind]||0)+amount;inventory[kind]=0;loaded+=amount}}invText();ui(loaded?"В генератор загружено топлива: "+loaded+". Подключите его кабелем к опоре.":"В генераторе топлива нет. Изготовьте биомассу из листьев или древесины.");return}const ready=Object.entries(m.output).filter(([,v])=>v>0);if(ready.length){for(const [item,count] of ready){inventory[item]=(inventory[item]||0)+count;m.output[item]=0}invText();ui("Готовая продукция забрана из "+m.type+".");return}if(m.type==="Miner"){ui(m.node?"Добытчик подключён к "+(labels[m.nodeType]||m.nodeType)+". Производство: 60 предметов/мин на обычном узле.":"Для работы доб. узла наведите на Miner при установке.");}else{const options=Object.keys(RECIPES[m.type]||{});if(options.length){const current=options.indexOf(m.recipe);const next=options[(current+1)%options.length];setMachineRecipe(m,next);ui(m.type+": выбран рецепт "+next+".");}else ui("У этой установки пока нет доступных рецептов.");}return}
ui("HUB: ранняя производственная площадка. Ручное изготовление доступно через «Крафт».");
}
function targetObject(){raycaster.setFromCamera(center,camera);const candidates=[...resourceNodes,...machines,...powerPoles,hub,...(assetWorld?.getObjects()||[])];const hits=raycaster.intersectObjects(candidates,true);if(!hits.length)return null;let o=hits[0].object;while(o.parent&&o.parent!==world&&!o.userData.node&&!o.userData.machine&&!o.userData.asset&&!o.userData.powerPoleId)o=o.parent;if(o.userData.node||o.userData.machine||o.userData.asset||o.userData.powerPoleId)return o;return hub}
function updateMachines(dt){powerStats=simulatePowerGrid(machines,powerPoles,powerConnections,dt);for(const g of machines){const m=g.userData.machine;const before=m.nodeRemaining;if(m.type==="Biomass Burner"){m.powered=!!Object.values(m.fuel||{}).some(v=>v>0)}else if(m.powered)tickMachine(m,dt);if(m.pendingNodeId&&!m.node){const linked=assetWorld?.getObjects().find(o=>o.userData.node?.id===m.pendingNodeId);if(linked){m.node=linked;m.nodeType=linked.userData.node.type;m.nodeRemaining=linked.userData.node.amount;m.pendingNodeId=null}}if(m.node&&before!==m.nodeRemaining)m.node.userData.node.amount=m.nodeRemaining}for(const belt of belts){if(!belt.item){belt.item=Object.keys(belt.source.output).find(k=>(belt.source.output[k]||0)>0)}if(belt.item){if(belt.modelItem!==belt.item&&itemModelPaths[belt.item]){belt.token.clear();attachModel(belt.token,itemModelPaths[belt.item],.42);belt.modelItem=belt.item}transferBelt(belt,belt.source,belt.target,dt);belt.visualT=(belt.visualT+dt*.6)%1;belt.token.visible=(belt.source.output[belt.item]||0)>0;belt.token.position.copy(belt.curve.getPoint(belt.visualT))}}invText()}function move(dt){
 const forward=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
 const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
 const v=new THREE.Vector3();
 v.addScaledVector(forward,moveY);v.addScaledVector(right,moveX);
 if(keys.KeyW)v.add(forward);if(keys.KeyS)v.sub(forward);if(keys.KeyD)v.add(right);if(keys.KeyA)v.sub(right);
 if(v.lengthSq())v.normalize().multiplyScalar(player.speed);
 if(jumpBuffer>0)jumpBuffer=Math.max(0,jumpBuffer-dt);
 if(playerBody){
  const p=stepPlayer(playerBody,v.x,v.z,jumpBuffer>0,dt);
  if(p){if(p.jumped)jumpBuffer=0;player.position.set(p.x,p.y+1.7,p.z);onGround=p.grounded}
 }else{
  if(jumpBuffer>0&&onGround){velocityY=8;onGround=false;jumpBuffer=0}
  v.multiplyScalar(dt);player.position.add(v);velocityY-=22*dt;player.position.y+=velocityY*dt;
  if(player.position.y<1.7){player.position.y=1.7;velocityY=0;onGround=true}
 }
 camera.position.copy(player.position);camera.rotation.order="YXZ";camera.rotation.y=yaw;camera.rotation.x=pitch;
}
function updatePrompt(){const t=targetObject();if(buildType){$("#prompt").textContent="Разместить "+buildType+" · E";return}if(t?.userData.node)$("#prompt").textContent="Ресурсный узел: "+(labels[t.userData.node.type]||t.userData.node.type)+" · E — собрать";else if(t?.userData.machine)$("#prompt").textContent=t.userData.machine.type+" · E — взаимодействовать";else if(t?.userData.asset)$("#prompt").textContent=t.userData.asset.name+" · E — осмотреть";else $("#prompt").textContent="HUB / площадка · исследуйте окрестности"}
function save(silent=false){const data={version:2,inventory,progression,resources:assetWorld?.getResourceState?.()||{},player:{x:player.position.x,y:player.position.y,z:player.position.z,yaw,pitch},powerPoles:powerPoles.map(g=>({id:g.userData.powerPoleId,x:g.position.x,y:g.position.y,z:g.position.z})),powerConnections:powerConnections.map(c=>({a:c.a,b:c.b})),machines:machines.map(g=>({type:g.userData.machine.type,x:g.position.x,y:g.position.y,z:g.position.z,recipe:g.userData.machine.recipe,input:g.userData.machine.input,output:g.userData.machine.output,elapsed:g.userData.machine.elapsed,nodeType:g.userData.machine.node?.userData.node?.type,nodeId:g.userData.machine.node?.userData.node?.id,nodeRemaining:g.userData.machine.nodeRemaining,fuel:g.userData.machine.fuel||{}})),belts:belts.map(b=>({from:machines.findIndex(g=>g.userData.machine===b.source),to:machines.findIndex(g=>g.userData.machine===b.target),item:b.item})),builtAssets:assetWorld?.getPlacedConstruction?.()||[]};localStorage.setItem("satisfactory-web-save-v1",JSON.stringify(data));if(!silent)ui("Сохранение записано на этом устройстве.");lastSave=Date.now()}
function load(){try{const d=JSON.parse(localStorage.getItem("satisfactory-web-save-v1"));if(!d)return;Object.assign(inventory,d.inventory||{});Object.assign(progression,d.progression||{});pendingResourceState=d.resources||{};pendingPlacedAssets=Array.isArray(d.builtAssets)?d.builtAssets:[];assetWorld?.setResourceState?.(pendingResourceState);Object.assign(player.position,d.player||{});yaw=d.player?.yaw||0;pitch=d.player?.pitch||0;for(const pole of d.powerPoles||[]){const g=new THREE.Group();g.position.set(pole.x,pole.y,pole.z);g.userData.powerPoleId=pole.id;world.add(g);attachModel(g,modelPaths.PowerPole,2.2);powerPoles.push(g)}for(const x of d.machines||[]){const g=makeMachine(x.type,new THREE.Vector3(x.x,x.y,x.z));g.userData.machine.recipe=x.recipe;g.userData.machine.input=x.input||x.buffer||{};g.userData.machine.buffer=g.userData.machine.input;g.userData.machine.output=x.output||{};g.userData.machine.fuel=x.fuel||{};g.userData.machine.elapsed=x.elapsed||0;g.userData.machine.nodeRemaining=x.nodeRemaining??Infinity;if(x.nodeId)g.userData.machine.pendingNodeId=x.nodeId;else if(x.nodeType)g.userData.machine.nodeType=x.nodeType;}for(const c of d.powerConnections||[]){const ga=[...machines,...powerPoles].find(g=>(g.userData.machine?.id||g.userData.powerPoleId)===c.a),gb=[...machines,...powerPoles].find(g=>(g.userData.machine?.id||g.userData.powerPoleId)===c.b);if(ga&&gb){const curve=new THREE.LineCurve3(ga.position.clone().add(new THREE.Vector3(0,2,0)),gb.position.clone().add(new THREE.Vector3(0,2,0)));const wire=new THREE.Mesh(new THREE.TubeGeometry(curve,12,.035,6,false),mat(0x252a2b,.45,.4));world.add(wire);powerConnections.push({...c,wire})}}for(const b of d.belts||[]){const from=machines[b.from],to=machines[b.to];if(from&&to){makeBelt(from,to);belts[belts.length-1].item=b.item||null}}invText();updateProgression()}catch(e){console.warn("Save load failed",e)}}
$("#menuSearch").addEventListener("input",()=>{if(menuMode==="build")showMenu("build")});
$("#menuCategory").addEventListener("change",()=>{if(menuMode==="build")showMenu("build")});
const orientationButton=$("#orientationButton");
orientationButton.addEventListener("click",async()=>{
 try{if(window.screen?.orientation?.lock)await window.screen.orientation.lock("landscape")}catch(error){console.info("Landscape lock is not available in this browser; rotate the device manually.",error)}
});
$("#craft").onclick=()=>showMenu("craft");$("#build").onclick=()=>showMenu("build");$("#save").onclick=save;$("#help").onclick=()=>{ui("Движение — левый стик · обзор — проводите пальцем по правой половине · действие — взаимодействие/установка · прыжок — отдельная кнопка.");};$("#closeMenu").onclick=closeMenu;$("#interact").onclick=interact;$("#menuBtn").onclick=()=>showMenu("build");$("#jump").addEventListener("pointerdown",e=>{e.preventDefault();jumpBuffer=0.28;},{passive:false});
addEventListener("keydown",e=>{if(e.code==="Space")e.preventDefault();keys[e.code]=true;if(e.code==="KeyE")interact();if(e.code==="Space"&&!e.repeat)jumpBuffer=0.28;if(e.code==="Escape")closeMenu()});addEventListener("keyup",e=>keys[e.code]=false);
let pointerLocked=false;renderer.domElement.addEventListener("click",()=>{if(innerWidth>850&&renderer.domElement.requestPointerLock)renderer.domElement.requestPointerLock()});document.addEventListener("pointerlockchange",()=>pointerLocked=document.pointerLockElement===renderer.domElement);document.addEventListener("mousemove",e=>{if(pointerLocked){yaw-=e.movementX*.0022;pitch=Math.max(-1.35,Math.min(1.35,pitch-e.movementY*.0022))}});
let lookTouch=null;renderer.domElement.addEventListener("touchstart",e=>{const t=e.changedTouches[0];if(t.clientX>innerWidth*.48)lookTouch={id:t.identifier,x:t.clientX,y:t.clientY}},{passive:true});renderer.domElement.addEventListener("touchmove",e=>{if(!lookTouch)return;for(const t of e.changedTouches)if(t.identifier===lookTouch.id){yaw-=(t.clientX-lookTouch.x)*.006;pitch=Math.max(-1.25,Math.min(1.25,pitch-(t.clientY-lookTouch.y)*.006));lookTouch.x=t.clientX;lookTouch.y=t.clientY}},{passive:true});renderer.domElement.addEventListener("touchend",()=>lookTouch=null,{passive:true});
const stick=$("#stick"),nub=$("#nub");let stickId=null;stick.addEventListener("pointerdown",e=>{e.preventDefault();stickId=e.pointerId;stick.setPointerCapture(stickId);stickMove(e)});stick.addEventListener("pointermove",e=>{if(e.pointerId===stickId)stickMove(e)});stick.addEventListener("pointerup",stickEnd);stick.addEventListener("pointercancel",stickEnd);function stickMove(e){const r=stick.getBoundingClientRect(),dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2),len=Math.hypot(dx,dy),scale=Math.min(1,44/(len||1));nub.style.transform="translate("+dx*scale+"px,"+dy*scale+"px)";moveX=dx/44;moveY=-dy/44;const l=Math.hypot(moveX,moveY);if(l>1){moveX/=l;moveY/=l}}function stickEnd(){stickId=null;moveX=moveY=0;nub.style.transform="translate(0,0)"}
load();invText();updateProgression();let t=0,hudPhysicsTimer=0;function animate(){requestAnimationFrame(animate);const dt=Math.min(clock.getDelta(),.04);move(dt);assetWorld?.update(player.position);updateMachines(dt);if(Date.now()-lastSave>300000)save(true);t+=dt;hudPhysicsTimer+=dt;if(t>.18){t=0}if(hudPhysicsTimer>1){const ps=getPhysicsStats(),as=assetWorld?.getStats();$("#stats").innerHTML="Энергия: "+powerStats.consumption.toFixed(1)+" / "+powerStats.capacity.toFixed(1)+" МВт · работает: "+powerStats.poweredMachines+"/"+powerStats.connectedMachines+"<br>Физика: "+(ps.available?"Rapier":"нет связи")+" · модели: "+(as?.loadedModels||0)+"/"+(as?.placedModels||0);hudPhysicsTimer=0}renderer.render(scene,camera)}animate();
addEventListener("pagehide",()=>save(true));document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden")save(true)});
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
