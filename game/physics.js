// Lightweight Rapier physics for the browser build.
// Visual GLB meshes and collision proxies are kept separate.
let RAPIER = null;
let world = null;
const pendingStatic = [];
const staticBodies = new WeakMap();

export async function initPhysics() {
  if (world) return world;
  try {
    RAPIER = await import("@dimforge/rapier3d-compat");
    await RAPIER.init();
    world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
    world.timestep = 1 / 60;
    const ground = world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(0, -0.12, 0));
    world.createCollider(RAPIER.ColliderDesc.cuboid(1000, 0.12, 1000).setFriction(0.9), ground);
    for (const object of pendingStatic.splice(0)) addStaticCollider(object);
    return world;
  } catch (error) {
    console.warn("Rapier physics unavailable; using safe movement fallback.", error);
    return null;
  }
}

export function addStaticCollider(object) {
  if (!object || staticBodies.has(object)) return;
  if (!world || !RAPIER) {
    pendingStatic.push(object);
    return;
  }
  object.updateWorldMatrix(true, true);
  const box = new (object.constructor === Object ? Object : globalThis.THREE?.Box3 || Object)();
  // Box3 is supplied by the caller as a simple world-space bounds object if THREE is not global.
  if (!object.userData?.physicsBounds) return;
  const b = object.userData.physicsBounds;
  const sx = Math.max(0.08, (b.max.x - b.min.x) * 0.5);
  const sy = Math.max(0.08, (b.max.y - b.min.y) * 0.5);
  const sz = Math.max(0.08, (b.max.z - b.min.z) * 0.5);
  const cx = (b.max.x + b.min.x) * 0.5;
  const cy = (b.max.y + b.min.y) * 0.5;
  const cz = (b.max.z + b.min.z) * 0.5;
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(cx, cy, cz));
  world.createCollider(RAPIER.ColliderDesc.cuboid(sx, sy, sz).setFriction(0.85), body);
  staticBodies.set(object, body);
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
  return body;
}

export function stepPlayer(body, vx, vz, jump, dt) {
  if (!world || !body) return null;
  const t = Math.min(1 / 30, Math.max(1 / 120, dt));
  world.timestep = t;
  const current = body.linvel();
  const pos = body.translation();
  const grounded = pos.y <= 0.88 && current.y <= 0.5;
  body.setLinvel({ x: vx, y: jump && grounded ? 8.0 : current.y, z: vz }, true);
  world.step();
  const p = body.translation();
  const v = body.linvel();
  return { x: p.x, y: p.y - 0.86, z: p.z, grounded: p.y <= 0.9 && v.y <= 0.5 };
}

export function physicsAvailable() {
  return !!world;
}
