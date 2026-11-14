import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { addStaticModelCollider, removeStaticCollider } from "./physics.js";

const NATURAL_CATEGORIES = new Set(["flora", "resources", "creatures"]);
const RENDER_DISTANCE = 155;
const UNLOAD_DISTANCE = 185;
const MAX_LOADED = 34;
const MAX_CONCURRENT = 4;

function seededRandom(seed) {
  let value = seed >>> 0;
  return () => {
    value = (value * 1664525 + 1013904223) >>> 0;
    return value / 4294967296;
  };
}
function hashId(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i++) hash = Math.imul(hash ^ value.charCodeAt(i), 16777619);
  return hash >>> 0;
}
function naturalPlacements(assets) {
  const random = seededRandom(0x5a771fac);
  const placements = [];
  const flora = assets.filter(asset => asset.category === "flora");
  const resources = assets.filter(asset => asset.category === "resources");
  const creatures = assets.filter(asset => asset.category === "creatures");

  // The landing area stays clear; native vegetation grows in irregular patches beyond it.
  for (const asset of flora) {
    const copies = asset.id.includes("wood") || asset.id.includes("plant-clusters") || asset.id.includes("vines") ? 4 : 2;
    for (let copy = 0; copy < copies; copy++) {
      const angle = random() * Math.PI * 2;
      const radius = 18 + Math.sqrt(random()) * 132;
      const cluster = 0.72 + random() * 0.75;
      placements.push({
        id: asset.id + "__flora_" + copy,
        asset,
        kind: "flora",
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        scale: cluster,
        yaw: random() * Math.PI * 2
      });
    }
  }

  // Resource deposits form believable, separated outcrops around the starter clearing.
  const resourceAngles = resources.map((asset, index) => ({
    asset,
    angle: (index / Math.max(1, resources.length)) * Math.PI * 2 + (random() - 0.5) * 0.45,
    radius: 38 + random() * 102
  }));
  for (const item of resourceAngles) {
    placements.push({
      id: item.asset.id,
      asset: item.asset,
      kind: "resource",
      x: Math.cos(item.angle) * item.radius,
      z: Math.sin(item.angle) * item.radius,
      scale: item.asset.id.includes("boulder") ? 1.15 : 1,
      yaw: random() * Math.PI * 2
    });
  }

  // Fauna is kept farther from the initial HUB site; no industrial display rows.
  for (const asset of creatures) {
    const angle = random() * Math.PI * 2;
    const radius = 75 + Math.sqrt(random()) * 100;
    placements.push({
      id: asset.id,
      asset,
      kind: "creature",
      x: Math.cos(angle) * radius,
      z: Math.sin(angle) * radius,
      scale: 0.85 + random() * 0.45,
      yaw: random() * Math.PI * 2
    });
  }

  return placements;
}

function disposeObject(root) {
  root.traverse(object => {
    if (!object.isMesh) return;
    object.geometry?.dispose();
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (!material) continue;
      for (const key of ["map", "normalMap", "roughnessMap", "metalnessMap", "aoMap", "emissiveMap", "alphaMap"]) {
        material[key]?.dispose();
      }
      material.dispose();
    }
  });
}

export async function createAssetWorld(parent, options = {}) {
  const response = await fetch("../viewer/catalog.json", { cache: "no-cache" });
  if (!response.ok) throw new Error("Не удалось загрузить каталог моделей: " + response.status);
  const catalog = await response.json();
  const selectionResponse = await fetch("../assets/model-selection.json", { cache: "no-cache" });
  if (!selectionResponse.ok) throw new Error("Не удалось загрузить манифест выбора моделей: " + selectionResponse.status);
  const selection = await selectionResponse.json();
  const selectionById = new Map((selection.assets || []).map(asset => [asset.id, asset]));
  const allAssets = catalog.assets || [];
  const assets = allAssets.map(asset => {
    const review = selectionById.get(asset.id);
    const selectedVariant = review?.selectedVariant || asset.selectedVariant;
    if (!review || !selectedVariant || review.selectionStatus === "pending-visual-review" || review.selectionStatus === "pending-noncombat-review") return null;
    const modelPath = review.variants?.[selectedVariant] || asset.variants?.[selectedVariant];
    if (!modelPath) return null;
    return { ...asset, selectedVariant, modelPath, selectionStatus: review.selectionStatus };
  }).filter(Boolean);
  const naturalAssets = assets.filter(asset => NATURAL_CATEGORIES.has(asset.category));
  const placements = naturalPlacements(naturalAssets);
  const loader = new GLTFLoader();
  const loaded = new Map();
  const loading = new Set();
  const onProgress = typeof options.onProgress === "function" ? options.onProgress : () => {};
  let lastUpdate = 0;
  let failed = 0;

  function loadPlacement(placement) {
    if (loaded.has(placement.id) || loading.has(placement.id)) return;
    loading.add(placement.id);
    loader.load("../" + placement.asset.modelPath, gltf => {
      loading.delete(placement.id);
      const wrapper = new THREE.Group();
      wrapper.name = placement.asset.name;
      wrapper.position.set(placement.x, 0, placement.z);
      wrapper.rotation.y = placement.yaw;
      wrapper.userData.asset = {
        id: placement.asset.id,
        name: placement.asset.name,
        category: placement.asset.category,
        variant: placement.asset.selectedVariant,
        kind: placement.kind
      };
      const resourceTypes = {
        iron_ore_node: "Iron Ore", copper_ore_node: "Copper Ore", limestone_node: "Limestone",
        coal_node: "Coal", caterium_ore_node: "Caterium Ore", bauxite_node: "Bauxite",
        crude_oil_node: "Crude Oil", raw_quartz_node: "Raw Quartz", sulfur_node: "Sulfur",
        sam_node: "SAM", resource_well_main: "Resource Well", resource_well_satellite: "Resource Well",
        geyser: "Geothermal Geyser", cracked_resource_boulder: "Resource Boulder"
      };
      if (placement.kind === "resource") {
        const resourceType = resourceTypes[placement.asset.id];
        if (resourceType) wrapper.userData.node = { type: resourceType, amount: 600 };
      } else if (placement.kind === "flora") {
        const floraId = placement.asset.id;
        const harvestType = floraId.includes("wood") || floraId.includes("bacon") ? "Wood" :
          floraId.includes("beryl") ? "Beryl Nut" :
          floraId.includes("paleberry") ? "Paleberry" :
          floraId.includes("agaric") ? "Bacon Agaric" : "Leaves";
        wrapper.userData.node = { type: harvestType, amount: 80 };
      }
      const model = gltf.scene;
      const bounds = new THREE.Box3().setFromObject(model);
      const size = bounds.getSize(new THREE.Vector3());
      const center = bounds.getCenter(new THREE.Vector3());
      const maxDimension = Math.max(size.x, size.y, size.z, 0.001);
      const creatureSize = placement.asset.id.includes("giant-flying-manta") ? 24 :
        placement.asset.id.includes("space-giraffe") ? 11 :
        placement.asset.id.includes("alpha-hog") || placement.asset.id.includes("hog") ? 3.4 :
        placement.asset.id.includes("stinger") || placement.asset.id.includes("spitter") ? 3.0 :
        placement.asset.id.includes("flying-bird") || placement.asset.id.includes("non-flying-bird") ? 1.5 : 2.2;
      const floraSize = placement.asset.id.includes("wood") ? 7.5 :
        placement.asset.id.includes("vines") ? 4.5 :
        placement.asset.id.includes("plant-clusters") ? 3.8 : 2.8;
      const target = placement.kind === "flora" ? floraSize : placement.kind === "resource" ? 4.2 : creatureSize;
      const scale = target / maxDimension * placement.scale;
      model.scale.setScalar(scale);
      model.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
      model.traverse(object => {
        if (!object.isMesh) return;
        object.castShadow = true;
        object.receiveShadow = true;
        const mats = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of mats) {
          if (!material) continue;
          if ("envMapIntensity" in material) material.envMapIntensity = 1.0;
          material.needsUpdate = true;
        }
      });
      wrapper.add(model);
      parent.add(wrapper);
      const body = addStaticModelCollider(wrapper, {
        friction: placement.kind === "flora" ? 0.64 : placement.kind === "creature" ? 0.72 : 0.9
      });
      loaded.set(placement.id, { wrapper, body, placement });
      onProgress(getStats());
    }, undefined, error => {
      loading.delete(placement.id);
      failed++;
      console.warn("Не удалось загрузить модель", placement.id, placement.asset.modelPath, error);
      onProgress(getStats());
    });
  }

  function getStats() {
    return {
      catalogFamilies: allAssets.length,
      selectedFamilies: assets.length,
      naturalFamilies: naturalAssets.length,
      placedModels: placements.length,
      loadedModels: loaded.size,
      loadingModels: loading.size,
      failedModels: failed,
      industrialFamiliesAvailable: assets.filter(asset => asset.category === "buildings" || asset.category === "infrastructure").length
    };
  }

  function update(playerPosition) {
    const now = performance.now();
    if (now - lastUpdate < 350) return;
    lastUpdate = now;
    const nearest = placements
      .map(placement => ({
        placement,
        distance: Math.hypot(placement.x - playerPosition.x, placement.z - playerPosition.z)
      }))
      .filter(item => item.distance < RENDER_DISTANCE)
      .sort((a, b) => a.distance - b.distance)
      .slice(0, MAX_LOADED);
    const wanted = new Set(nearest.map(item => item.placement.id));

    for (const [id, entry] of loaded) {
      const distance = Math.hypot(entry.placement.x - playerPosition.x, entry.placement.z - playerPosition.z);
      if (distance > UNLOAD_DISTANCE || !wanted.has(id)) {
        if (entry.body) removeStaticCollider(entry.wrapper);
        parent.remove(entry.wrapper);
        disposeObject(entry.wrapper);
        loaded.delete(id);
      }
    }

    let started = loading.size;
    for (const item of nearest) {
      if (started >= MAX_CONCURRENT) break;
      if (!loaded.has(item.placement.id) && !loading.has(item.placement.id)) {
        loadPlacement(item.placement);
        started++;
      }
    }
    onProgress(getStats());
  }

  const constructionCatalog = assets.filter(asset =>
    asset.category === "buildings" || asset.category === "infrastructure" ||
    asset.category === "portable_miner" || asset.category === "railway"
  );

  return {
    update,
    getObjects: () => [...loaded.values()].map(entry => entry.wrapper),
    getStats,
    placements,
    constructionCatalog
  };
}
