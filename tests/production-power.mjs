import assert from "node:assert/strict";
import { simulatePowerGrid } from "../game/production.js";

const generator = { userData: { machine: { id: "gen-1", type: "Biomass Burner", fuel: { Biomass: 1 } } }, position: { x: 0, y: 0, z: 0 } };
const pole = { userData: { powerPoleId: "pole-1" }, position: { x: 1, y: 0, z: 0 } };
const smelter = { userData: { machine: { id: "smelter-1", type: "Smelter", recipe: "Iron Ingot", active: true, input: { "Iron Ore": 1 }, output: {}, powered: false } }, position: { x: 2, y: 0, z: 0 } };
let state = simulatePowerGrid([generator, smelter], [pole], [{ a: "gen-1", b: "pole-1" }, { a: "pole-1", b: "smelter-1" }], 1);
assert.equal(smelter.userData.machine.powered, true);
assert.equal(state.capacity, 30);
assert.equal(state.consumption, 4);
assert.ok(Math.abs(generator.userData.machine.fuel.Biomass - (1 - 4 / 180)) < 1e-8);

// Without a cable, a fueled generator must not power an isolated consumer.
smelter.userData.machine.powered = true;
state = simulatePowerGrid([generator, smelter], [pole], [{ a: "gen-1", b: "pole-1" }], 1);
assert.equal(smelter.userData.machine.powered, false);
assert.equal(state.connectedMachines, 1);
assert.equal(state.capacity, 30);

// An empty generator cannot power the connected factory.
generator.userData.machine.fuel.Biomass = 0;
state = simulatePowerGrid([generator, smelter], [pole], [{ a: "gen-1", b: "pole-1" }, { a: "pole-1", b: "smelter-1" }], 1);
assert.equal(smelter.userData.machine.powered, false);
assert.equal(state.capacity, 0);
console.log("Power-grid tests passed.");
