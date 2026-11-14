import { chromium } from "playwright";
import assert from "node:assert/strict";

const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const pageErrors = [];
  const consoleErrors = [];
  const failedRequests = [];
  const badResponses = [];
  page.on("pageerror", error => pageErrors.push({ message: error.message, stack: error.stack }));
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("requestfailed", request => failedRequests.push({ url: request.url(), error: request.failure()?.errorText || "request failed" }));
  page.on("response", response => { if (response.status() >= 400) badResponses.push({ url: response.url(), status: response.status() }); });
  const response = await page.goto("http://127.0.0.1:4173/game/", { waitUntil: "domcontentloaded", timeout: 60000 });
  try {
    await page.waitForSelector("#game canvas", { timeout: 30000 });
  } catch (error) {
    const dom = await page.evaluate(() => ({
      readyState: document.readyState,
      title: document.title,
      gameElement: !!document.querySelector("#game"),
      gameMarkup: document.querySelector("#game")?.innerHTML?.slice(0, 300),
      moduleScript: document.querySelector('script[type="module"]')?.src || null,
      orientation: window.matchMedia("(orientation: portrait)").matches ? "portrait" : "landscape",
      importMap: document.querySelector('script[type="importmap"]')?.textContent?.slice(0, 500) || null
    })).catch(() => null);
    throw new Error("Game canvas did not initialize. HTTP=" + response?.status() +
      " DOM=" + JSON.stringify(dom) +
      " PAGE_ERRORS=" + JSON.stringify(pageErrors) +
      " CONSOLE_ERRORS=" + JSON.stringify(consoleErrors) +
      " FAILED_REQUESTS=" + JSON.stringify(failedRequests) +
      " BAD_RESPONSES=" + JSON.stringify(badResponses) +
      " WAIT_ERROR=" + error.message);
  }
  await page.waitForFunction(() => {
    const state = window.__SATISFACTORY_PHYSICS__?.();
    return state?.available === true && state?.assets?.loadedModels >= 2 && state?.meshColliders > 0;
  }, { timeout: 90000 });
  await page.waitForFunction(() => window.__SATISFACTORY_PHYSICS__?.().player?.grounded === true, { timeout: 20000 });
  await page.waitForFunction(() => {
    const state = window.__SATISFACTORY_PHYSICS__?.();
    return state?.worldSurface?.colorMap &&
      state?.worldSurface?.roughnessMap &&
      state?.worldSurface?.bumpMap &&
      state?.worldSurface?.foliageInstances >= 2000 &&
      state?.assets?.pbr?.textureMapsExpected === 15 &&
      state?.assets?.pbr?.textureMapsLoaded === 15 &&
      state?.assets?.pbr?.detailMaterials > 0 &&
      state?.resources?.some(node => node.amount > 0);
  }, { timeout: 90000 });

  const depletionCheck = await page.evaluate(() => {
    const state = window.__SATISFACTORY_PHYSICS__();
    const node = state.resources.find(item => item.amount > 0);
    if (!node) return { ok: false, reason: "No loaded resource node available" };
    const before = node.amount;
    const changed = window.__SATISFACTORY_SET_RESOURCE_AMOUNT__(node.id, 0);
    const depleted = window.__SATISFACTORY_PHYSICS__().resources.find(item => item.id === node.id);
    const visualChanged = changed && depleted?.amount === 0 &&
      depleted.modelVisible === false && depleted.remainsVisible === true &&
      depleted.collider === false;
    const restored = window.__SATISFACTORY_SET_RESOURCE_AMOUNT__(node.id, before);
    return { ok: visualChanged && restored, before, depleted, restored };
  });
  assert.equal(depletionCheck.ok, true,
    "Exhausted resource did not switch to visible rubble: " + JSON.stringify(depletionCheck));

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
      worldSurface: api.worldSurface,
      resources: api.resources,
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
  assert.ok(result.assets.placedModels >= 70, "Natural planet placement manifest is incomplete");
  assert.ok(result.assets.naturalFamilies >= 55, "Natural flora, resource and fauna families are missing");
  assert.ok(result.assets.industrialFamiliesAvailable >= 50, "Industrial construction catalogue is missing");
  assert.ok(result.assets.placedModels < result.assets.selectedFamilies, "Industrial construction pieces were incorrectly scattered as a showroom");
  assert.equal(result.worldSurface.colorMap, true, "Terrain colour map is missing");
  assert.equal(result.worldSurface.roughnessMap, true, "Terrain roughness map is missing");
  assert.equal(result.worldSurface.bumpMap, true, "Terrain height detail map is missing");
  assert.ok(result.worldSurface.foliageInstances >= 2000, "Detailed Grass Fields ground vegetation is missing");
  assert.equal(result.assets.pbr.textureMapsExpected, 15, "Expected five v2 PBR families with three maps each");
  assert.equal(result.assets.pbr.textureMapsLoaded, 15, "Not all v2 PBR maps loaded in the game scene");
  assert.ok(result.assets.pbr.detailMaterials > 0, "No streamed materials received the PBR albedo detail overlay");
  assert.ok(result.assets.pbr.detailMaterials <= result.assets.pbr.materialCount, "PBR material diagnostics are inconsistent");
  assert.ok(result.resources.some(node => node.amount > 0), "No interactive resource nodes streamed into the world");
  assert.ok(result.assets.loadedModels >= 2, "Nearby GLB models did not stream into the world");
  assert.ok(result.probes.ground !== null, "Ground ray missed the world ground");
  assert.ok(result.probes.landingPad !== null, "Ray missed the landing pad collider");
  assert.ok(result.probes.hub !== null, "Ray missed the HUB collider");
  assert.deepEqual(pageErrors, [], "Browser runtime errors: " + pageErrors.join("; "));
  console.log("World materials, resource depletion and Rapier geometry-collision smoke test passed:", JSON.stringify({ ...result, depletionCheck }));
} finally {
  await browser.close();
}
