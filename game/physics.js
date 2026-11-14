import * as THREE from "three";
// Rapier runtime physics. Render meshes are never used as high-poly collision meshes.
let RAPIER = null;
let world = null;
const pendingStatic = [];
const staticBodies = new WeakMap();
let colliderCount = 0;
let staticObjectCount = 0;
let dynamicBodyCount = 0;
let meshColliderCount = 0;
const staticPartCounts = new WeakMap();
const staticMeshParts = new WeakMap();

export async function initPhysics() {
  if (world) return world;
  try {
    const rapierModule = await import("@dimforge/rapier3d-compat");
    RAPIER = rapierModule.default || rapierModule;
    await RAPIER.init();
    world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
    world.timestep = 1 / 60;
    const ground = world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(0, -0.12, 0));
    world.createCollider(RAPIER.ColliderDesc.cuboid(1000, 0.12, 1000).setFriction(0.9), ground);
    colliderCount++;
    for (const entry of pendingStatic.splice(0)) addStaticCollider(entry.object, entry.options);
    return world;
  } catch (error) {
    console.warn("Rapier physics unavailable; using safe movement fallback.", error);
    return null;
  }
}

function colliderParts(size, shape) {
  const hx = Math.max(0.08, size.x * 0.5);
  const hy = Math.max(0.08, size.y * 0.5);
  const hz = Math.max(0.08, size.z * 0.5);
  if (shape === "capsule") {
    const radius = Math.max(0.12, Math.min(hx, hz) * 0.82);
    return [{ shape: "capsule", halfHeight: Math.max(0.08, hy - radius), radius, y: 0 }];
  }
  if (shape === "cylinder") return [{ shape: "cylinder", halfHeight: hy, radius: Math.max(0.12, Math.min(hx, hz)) }];
  if (shape === "compound-building") {
    // Three low-poly tiers approximate a machine/building silhouette without colliding with bolts or trim.
    return [
      { shape: "box", x: hx * 0.96, y: Math.max(0.12, hy * 0.34), z: hz * 0.96, offsetY: -hy * 0.52 },
      { shape: "box", x: hx * 0.78, y: Math.max(0.12, hy * 0.27), z: hz * 0.78, offsetY: hy * 0.08 },
      { shape: "box", x: hx * 0.48, y: Math.max(0.1, hy * 0.18), z: hz * 0.48, offsetY: hy * 0.57 }
    ];
  }
  return [{ shape: "box", x: hx, y: hy, z: hz, offsetY: 0 }];
}

export function addStaticCollider(object, options = {}) {
  if (!object || staticBodies.has(object)) return;
  if (!world || !RAPIER) {
    pendingStatic.push({ object, options });
    return;
  }
  object.updateWorldMatrix(true, true);
  const bounds = new THREE.Box3().setFromObject(object);
  if (bounds.isEmpty()) return;
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  if (![size.x, size.y, size.z].every(Number.isFinite)) return;
  const shape = options.shape || "box";
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(center.x, center.y, center.z));
  const parts = colliderParts(size, shape);
  for (const part of parts) {
    let desc;
    if (part.shape === "capsule") {
      desc = RAPIER.ColliderDesc.capsule(part.halfHeight, part.radius);
    } else if (part.shape === "cylinder") {
      desc = RAPIER.ColliderDesc.cylinder(part.halfHeight, part.radius);
    } else {
      desc = RAPIER.ColliderDesc.cuboid(part.x, part.y, part.z);
    }
    if (part.offsetY) desc.setTranslation(0, part.offsetY, 0);
    desc.setFriction(options.friction ?? 0.82).setRestitution(0);
    world.createCollider(desc, body);
    colliderCount++;
  }
  staticBodies.set(object, body);
  staticPartCounts.set(object, parts.length);
  staticObjectCount++;
}


export function addStaticModelCollider(root, options = {}) {
  if (!root || !world || !RAPIER || staticBodies.has(root)) return null;
  root.updateWorldMatrix(true, true);

  const inverseRoot = new THREE.Matrix4().copy(root.matrixWorld).invert();
  const candidates = [];
  root.traverse(object => {
    if (!object.isMesh || !object.geometry?.attributes?.position) return;
    const attribute = object.geometry.attributes.position;
    if (attribute.count < 12) return;
    const localMatrix = new THREE.Matrix4().multiplyMatrices(inverseRoot, object.matrixWorld);
    const stride = Math.max(1, Math.ceil(attribute.count / 320));
    const points = [];
    for (let i = 0; i < attribute.count; i += stride) {
      const point = new THREE.Vector3().fromBufferAttribute(attribute, i).applyMatrix4(localMatrix);
      if (Number.isFinite(point.x) && Number.isFinite(point.y) && Number.isFinite(point.z)) {
        points.push(point.x, point.y, point.z);
      }
    }
    if (points.length >= 36) candidates.push({ points, vertices: attribute.count });
  });

  candidates.sort((a, b) => b.vertices - a.vertices);
  const selected = candidates.slice(0, 6);
  const worldPosition = root.getWorldPosition(new THREE.Vector3());
  const body = world.createRigidBody(
    RAPIER.RigidBodyDesc.fixed().setTranslation(worldPosition.x, worldPosition.y, worldPosition.z)
  );
  let created = 0;
  for (const candidate of selected) {
    const descriptor = RAPIER.ColliderDesc.convexHull(new Float32Array(candidate.points));
    if (!descriptor) continue;
    descriptor.setFriction(options.friction ?? 0.86).setRestitution(0);
    world.createCollider(descriptor, body);
    created++;
  }

  if (created === 0) {
    const bounds = new THREE.Box3().setFromObject(root);
    if (!bounds.isEmpty()) {
      const size = bounds.getSize(new THREE.Vector3());
      const center = bounds.getCenter(new THREE.Vector3()).applyMatrix4(inverseRoot);
      const descriptor = RAPIER.ColliderDesc.cuboid(
        Math.max(0.08, size.x * 0.5),
        Math.max(0.08, size.y * 0.5),
        Math.max(0.08, size.z * 0.5)
      ).setTranslation(center.x, center.y, center.z);
      descriptor.setFriction(options.friction ?? 0.86).setRestitution(0);
      world.createCollider(descriptor, body);
      created = 1;
    }
  }

  if (created === 0) {
    world.removeRigidBody(body);
    return null;
  }
  staticBodies.set(root, body);
  staticPartCounts.set(root, created);
  staticMeshParts.set(root, created);
  staticObjectCount++;
  colliderCount += created;
  meshColliderCount += created;
  return body;
}

export function removeStaticCollider(object) {
  const body = staticBodies.get(object);
  if (!body || !world) return false;
  world.removeRigidBody(body);
  const parts = staticPartCounts.get(object) || 0;
  colliderCount = Math.max(1, colliderCount - parts);
  staticObjectCount = Math.max(0, staticObjectCount - 1);
  meshColliderCount = Math.max(0, meshColliderCount - (staticMeshParts.get(object) || 0));
  staticBodies.delete(object);
  staticPartCounts.delete(object);
  staticMeshParts.delete(object);
  return true;
}

export function createPlayerBody(x, feetY, z) {
  if (!world || !RAPIER) return null;
  const body = world.createRigidBody(
    RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(x, feetY + 0.86, z)
      .setLinearDamping(1.6)
      .setAngularDamping(1.0)
      .lockRotations()
      .setCanSleep(false)
  );
  world.createCollider(
    RAPIER.ColliderDesc.capsule(0.48, 0.34)
      .setFriction(0.9)
      .setRestitution(0),
    body
  );
  colliderCount++;
  dynamicBodyCount++;
  return body;
}

export function stepPlayer(body, vx, vz, jump, dt) {
  if (!world || !body) return null;
  const t = Math.min(1 / 30, Math.max(1 / 120, dt));
  world.timestep = t;
  const current = body.linvel();
  const pos = body.translation();
  const ray = new RAPIER.Ray({ x: pos.x, y: pos.y, z: pos.z }, { x: 0, y: -1, z: 0 });
  const floorHit = world.castRay(ray, 1.02, true, undefined, undefined, undefined, body);
  const grounded = !!floorHit && current.y <= 0.5;
  body.setLinvel({ x: vx, y: jump && grounded ? 8.0 : current.y, z: vz }, true);
  world.step();
  const p = body.translation();
  const v = body.linvel();
  const probe = new RAPIER.Ray({ x: p.x, y: p.y, z: p.z }, { x: 0, y: -1, z: 0 });
  const afterHit = world.castRay(probe, 1.02, true, undefined, undefined, undefined, body);
  return { x: p.x, y: p.y - 0.86, z: p.z, grounded: !!afterHit && v.y <= 0.5 };
}

export function probeDown(x, y, z, maxDistance = 30) {
  if (!world || !RAPIER) return null;
  const ray = new RAPIER.Ray({ x, y, z }, { x: 0, y: -1, z: 0 });
  const hit = world.castRay(ray, maxDistance, true);
  return hit ? hit.timeOfImpact : null;
}

export function physicsAvailable() {
  return !!world;
}

export function getPhysicsStats() {
  return { available: !!world, staticObjects: staticObjectCount, colliders: colliderCount, meshColliders: meshColliderCount, dynamicBodies: dynamicBodyCount, pendingStatic: pendingStatic.length };
}
