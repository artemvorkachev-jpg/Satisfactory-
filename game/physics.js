import * as THREE from "three";
// Rapier runtime physics. Render meshes are never used as high-poly collision meshes.
let RAPIER = null;
let world = null;
const pendingStatic = [];
const staticBodies = new WeakMap();
let colliderCount = 0;
let staticObjectCount = 0;
let dynamicBodyCount = 0;

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
  staticObjectCount++;
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

export function physicsAvailable() {
  return !!world;
}

export function getPhysicsStats() {
  return { available: !!world, staticObjects: staticObjectCount, colliders: colliderCount, dynamicBodies: dynamicBodyCount, pendingStatic: pendingStatic.length };
}
