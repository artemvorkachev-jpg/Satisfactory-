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

 
// Raw leaves and wood are not valid direct fuels for a Biomass Burner.
generator.userData.machine.fuel = { Leaves: 100, Wood: 100 };
state = simulatePowerGrid([generator, smelter], [pole], [{ a: "gen-1", b: "pole-1" }, { a: "pole-1", b: "smelter-1" }], 1);
assert.equal(state.capacity, 0);
assert.equal(smelter.userData.machine.powered, false);

// A second connected burner can cover demand when the first runs out mid-step.
const nearlyEmpty = { userData: { machine: { id: "gen-2", type: "Biomass Burner", fuel: { Biomass: 0.04 } } } };
generator.userData.machine.fuel = { Biomass: 0.01 };
const secondPole = { userData: { powerPoleId: "pole-2" } };
const secondConsumer = { userData: { machine: { id: "constructor-1", type: "Constructor", recipe: "Iron Plate", active: true, input: { "Iron Ingot": 3 }, output: {}, powered: false } } };
state = simulatePowerGrid([generator, nearlyEmpty, smelter, secondConsumer], [pole, secondPole], [
  { a: "gen-1", b: "pole-1" }, { a: "pole-1", b: "smelter-1" },
  { a: "gen-2", b: "pole-1" }, { a: "pole-1", b: "constructor-1" }
], 1);
assert.equal(state.capacity, 60);
assert.equal(smelter.userData.machine.powered, true);
assert.equal(secondConsumer.userData.machine.powered, true);
