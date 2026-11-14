import { chromium } from "playwright";
import assert from "node:assert/strict";

const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));
  await page.goto("http://127.0.0.1:4173/game/", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForSelector("#game canvas", { timeout: 30000 });
  await page.waitForFunction(() => {
    const state = window.__SATISFACTORY_PHYSICS__?.();
    return state?.available === true && state?.assets?.loadedModels >= 2 && state?.meshColliders > 0;
  }, { timeout: 90000 });
  await page.waitForFunction(() => window.__SATISFACTORY_PHYSICS__?.().player?.grounded === true, { timeout: 20000 });
  const result = await page.evaluate(() => {
    const api = window.__SATISFACTORY_PHYSICS__();
    return {
      available: api.available,
      staticObjects: api.staticObjects,
      colliders: api.colliders,
      meshColliders: api.meshColliders,
      dynamicBodies: api.dynamicBodies,
      pendingStatic: api.pendingStatic,
      player: api.player,
      assets: api.assets,
      probes: {
        ground: api.probeDown(90, 5, 90, 20),
        landingPad: api.probeDown(2, 5, 4.5, 20),
        hub: api.probeDown(0, 10, -1, 30)
      }
    };
  });
  assert.equal(result.available, true, "Rapier did not initialize in Chromium");
  assert.ok(result.staticObjects >= 6, "Expected loaded model colliders, got " + result.staticObjects);
  assert.ok(result.meshColliders >= 2, "Expected geometry-derived convex hull colliders, got " + result.meshColliders);
  assert.ok(result.colliders >= result.meshColliders, "Collider accounting is inconsistent");
  assert.equal(result.dynamicBodies, 1, "Player dynamic body was not created");
  assert.equal(result.pendingStatic, 0, "Some static colliders remained queued");
  assert.ok(result.player.grounded, "Player did not settle onto the ground collider");
  assert.ok(result.assets.catalogFamilies >= 290, "Full model catalogue was not loaded");
  assert.ok(result.assets.selectedFamilies >= 175, "Reviewed model families were not integrated");
  assert.ok(result.assets.selectedFamilies < result.assets.catalogFamilies, "Unreviewed families were incorrectly treated as selected");
  assert.ok(result.assets.placedModels >= 175, "World placement manifest is incomplete");
  assert.ok(result.assets.loadedModels >= 2, "Nearby GLB models did not stream into the world");
  assert.ok(result.probes.ground !== null, "Ground ray missed the world ground");
  assert.ok(result.probes.landingPad !== null, "Ray missed the landing pad collider");
  assert.ok(result.probes.hub !== null, "Ray missed the HUB collider");
  assert.deepEqual(pageErrors, [], "Browser runtime errors: " + pageErrors.join("; "));
  console.log("Model-streaming and Rapier geometry-collision smoke test passed:", JSON.stringify(result));
} finally {
  await browser.close();
}
