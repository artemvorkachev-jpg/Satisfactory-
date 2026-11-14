import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { addStaticModelCollider, removeStaticCollider } from "./physics.js";

const VEHICLE_CATEGORIES = new Set([
  "cyber_wagon", "drone", "explorer", "factory_cart", "freight_car",
  "freight_platform", "locomotive", "tractor", "train_station", "truck"
]);

const LAYOUTS = {
  buildings:      { x: 0,    z: -76, columns: 10, spacing: 12, target: 8.5, color: 0x46575b, width: 142, depth: 124, label: "INDUSTRIAL CAMPUS" },
  infrastructure: { x: 142,  z: -50, columns: 5,  spacing: 11, target: 4.3, color: 0x4c5555, width: 72,  depth: 70,  label: "LOGISTICS YARD" },
  resources:      { x: -142, z: -28, columns: 4,  spacing: 14, target: 4.7, color: 0x65584a, width: 76,  depth: 76,  label: "RESOURCE QUARRY" },
  flora:          { x: -155, z: -160,columns: 4,  spacing: 12, target: 7.5, color: 0x354b38, width: 72,  depth: 68,  label: "BIOME GARDEN" },
  creatures:      { x: 0,    z: 178, columns: 8,  spacing: 11, target: 3.2, color: 0x4b5548, width: 112, depth: 78,  label: "WILDLIFE PRESERVE" },
  vehicles:       { x: 155,  z: 155, columns: 4,  spacing: 16, target: 8.0, color: 0x4d5559, width: 82,  depth: 78,  label: "VEHICLE DEPOT" },
  items:          { x: 145,  z: -165,columns: 4,  spacing: 7,  target: 1.6, color: 0x55534a, width: 70,  depth: 64,  label: "MATERIALS STORE" },
  equipment:      { x: -150, z: 145, columns: 4,  spacing: 9,  target: 2.5, color: 0x4b5358, width: 76,  depth: 68,  label: "EQUIPMENT HANGAR" }
};

function groupFor(asset) {
  const category = asset.category;
  if (category === "buildings") return "buildings";
  if (category === "infrastructure" || category === "portable_miner" || category === "railway") return "infrastructure";
  if (category === "resources") return "resources";
  if (category === "flora") return "flora";
  if (category === "creatures") return "creatures";
  if (category === "items") return "items";
  if (VEHICLE_CATEGORIES.has(category)) return "vehicles";
  return "equipment";
}

function makePlacements(assets, skipIds) {
  const buckets = new Map(Object.keys(LAYOUTS).map(key => [key, []]));
  for (const asset of assets) {
    if (skipIds.has(asset.id)) continue;
    if (!asset.selectedVariant || !asset.variants || !asset.variants[asset.selectedVariant]) continue;
    buckets.get(groupFor(asset)).push(asset);
  }
  const placements = [];
  for (const [key, list] of buckets) {
    const layout = LAYOUTS[key];
    list.sort((a, b) => a.id.localeCompare(b.id));
    for (let i = 0; i < list.length; i++) {
      const asset = list[i];
      const col = i % layout.columns;
      const row = Math.floor(i / layout.columns);
      const rows = Math.ceil(list.length / layout.columns);
      let x = layout.x + (col - (layout.columns - 1) / 2) * layout.spacing;
      let z = layout.z + (row - (rows - 1) / 2) * layout.spacing;
      if (key === "buildings" && i === 0) z -= 8;
      placements.push({
        id: asset.id,
        asset,
        zone: key,
        x,
        z,
        target: layout.target,
        url: "../" + asset.variants[asset.selectedVariant]
      });
    }
  }
  return placements;
}

function addDistrict(parent, layout) {
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(layout.width, layout.depth),
    new THREE.MeshStandardMaterial({ color: layout.color, roughness: 0.96, metalness: 0.02 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(layout.x, 0.025, layout.z);
  floor.receiveShadow = true;
  parent.add(floor);

  const lineMaterial = new THREE.MeshStandardMaterial({ color: 0xe0ad31, roughness: 0.8, metalness: 0.1 });
  const line = (x, z, sx, sz) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(sx, 0.025, sz), lineMaterial);
    mesh.position.set(x, 0.045, z);
    parent.add(mesh);
  };
  line(layout.x, layout.z - layout.depth / 2 + 1, layout.width - 4, 0.13);
  line(layout.x, layout.z + layout.depth / 2 - 1, layout.width - 4, 0.13);
  line(layout.x - layout.width / 2 + 1, layout.z, 0.13, layout.depth - 4);
  line(layout.x + layout.width / 2 - 1, layout.z, 0.13, layout.depth - 4);

  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(9,18,23,0.86)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#e3b032";
  ctx.lineWidth = 5;
  ctx.strokeRect(3, 3, canvas.width - 6, canvas.height - 6);
  ctx.fillStyle = "#f2f4f3";
  ctx.font = "bold 36px system-ui";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(layout.label, 256, 64);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false }));
  sprite.position.set(layout.x, 10, layout.z - layout.depth / 2 + 8);
  sprite.scale.set(22, 5.5, 1);
  parent.add(sprite);
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
    if (!review || !review.selectedVariant || review.selectionStatus === "pending-noncombat-review") return null;
    return { ...asset, selectedVariant: review.selectedVariant, selectionStatus: review.selectionStatus };
  }).filter(Boolean);
  const skipIds = new Set(options.skipIds || ["hub"]);
  const placements = makePlacements(assets, skipIds);
  const loader = new GLTFLoader();
  const loaded = new Map();
  const loading = new Set();
  const onProgress = typeof options.onProgress === "function" ? options.onProgress : () => {};
  const maxLoaded = 26;
  const maxConcurrent = 3;
  let lastUpdate = 0;
  let failed = 0;

  for (const layout of Object.values(LAYOUTS)) addDistrict(parent, layout);

  function loadPlacement(placement, playerPosition) {
    if (loaded.has(placement.id) || loading.has(placement.id)) return;
    loading.add(placement.id);
    loader.load(placement.url, gltf => {
      loading.delete(placement.id);
      const wrapper = new THREE.Group();
      wrapper.name = placement.asset.name;
      wrapper.position.set(placement.x, 0, placement.z);
      wrapper.userData.asset = {
        id: placement.id,
        name: placement.asset.name,
        category: placement.asset.category,
        variant: placement.asset.selectedVariant
      };
      const model = gltf.scene;
      const bounds = new THREE.Box3().setFromObject(model);
      const size = bounds.getSize(new THREE.Vector3());
      const center = bounds.getCenter(new THREE.Vector3());
      const maxDimension = Math.max(size.x, size.y, size.z, 0.001);
      const scale = placement.target / maxDimension;
      model.scale.setScalar(scale);
      model.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
      model.traverse(object => {
        if (!object.isMesh) return;
        object.castShadow = true;
        object.receiveShadow = true;
        const mats = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of mats) {
          if (!material) continue;
          if ("envMapIntensity" in material) material.envMapIntensity = 1.15;
          material.needsUpdate = true;
        }
      });
      wrapper.add(model);
      const distance = Math.hypot(placement.x - playerPosition.x, placement.z - playerPosition.z);
      if (distance > 145) {
        disposeObject(wrapper);
        return;
      }
      parent.add(wrapper);
      const body = addStaticModelCollider(wrapper, { friction: placement.zone === "flora" ? 0.72 : 0.88 });
      loaded.set(placement.id, { wrapper, body, placement });
      onProgress(getStats());
    }, undefined, error => {
      loading.delete(placement.id);
      failed++;
      console.warn("Не удалось загрузить модель", placement.id, placement.url, error);
      onProgress(getStats());
    });
  }

  function getStats() {
    return {
      catalogFamilies: allAssets.length,
      selectedFamilies: assets.length,
      placedModels: placements.length + skipIds.size,
      loadedModels: loaded.size,
      loadingModels: loading.size,
      failedModels: failed,
      districts: Object.keys(LAYOUTS).length
    };
  }

  function update(playerPosition) {
    const now = performance.now();
    if (now - lastUpdate < 450) return;
    lastUpdate = now;
    const nearest = placements
      .map(placement => ({
        placement,
        distance: Math.hypot(placement.x - playerPosition.x, placement.z - playerPosition.z)
      }))
      .filter(item => item.distance < 105)
      .sort((a, b) => a.distance - b.distance)
      .slice(0, maxLoaded);
    const wanted = new Set(nearest.map(item => item.placement.id));

    for (const [id, entry] of loaded) {
      const distance = Math.hypot(entry.placement.x - playerPosition.x, entry.placement.z - playerPosition.z);
      if (distance > 132 || !wanted.has(id)) {
        removeStaticCollider(entry.wrapper);
        parent.remove(entry.wrapper);
        disposeObject(entry.wrapper);
        loaded.delete(id);
      }
    }

    let started = loading.size;
    for (const item of nearest) {
      if (started >= maxConcurrent) break;
      if (!loaded.has(item.placement.id) && !loading.has(item.placement.id)) {
        loadPlacement(item.placement, playerPosition);
        started++;
      }
    }
    onProgress(getStats());
  }

  return {
    update,
    getObjects: () => [...loaded.values()].map(entry => entry.wrapper),
    getStats,
    placements
  };
}
