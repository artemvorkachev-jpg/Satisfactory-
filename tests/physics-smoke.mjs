import { chromium } from "playwright";
import assert from "node:assert/strict";

const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));
  await page.goto("http://127.0.0.1:4173/game/", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForSelector("#game canvas", { timeout: 30000 });
  await page.waitForFunction(() => window.__SATISFACTORY_PHYSICS__?.().available === true, { timeout: 30000 });
  await page.waitForTimeout(1500);
  const result = await page.evaluate(() => {
    const api = window.__SATISFACTORY_PHYSICS__();
    return {
      available: api.available,
      staticObjects: api.staticObjects,
      colliders: api.colliders,
      dynamicBodies: api.dynamicBodies,
      pendingStatic: api.pendingStatic,
      player: api.player,
      probes: {
        ground: api.probeDown(90, 5, 90, 20),
        landingPad: api.probeDown(2, 5, 4.5, 20),
        hub: api.probeDown(0, 10, -1, 30)
      }
    };
  });
  assert.equal(result.available, true, "Rapier did not initialize in Chromium");
  assert.ok(result.staticObjects >= 140, `Expected at least 140 static scene objects, got ${result.staticObjects}`);
  assert.ok(result.colliders >= 140, `Expected at least 140 colliders, got ${result.colliders}`);
  assert.equal(result.dynamicBodies, 1, "Player dynamic body was not created");
  assert.equal(result.pendingStatic, 0, "Some static colliders remained queued");
  assert.ok(result.player.grounded, "Player did not settle onto the ground collider");
  assert.ok(result.probes.ground !== null, "Ground ray missed the world ground");
  assert.ok(result.probes.landingPad !== null, "Ray missed the landing pad collider");
  assert.ok(result.probes.hub !== null, "Ray missed the HUB collider");
  assert.deepEqual(pageErrors, [], `Browser runtime errors: ${pageErrors.join("; ")}`);
  console.log("Browser physics smoke test passed:", JSON.stringify(result));
} finally {
  await browser.close();
}
