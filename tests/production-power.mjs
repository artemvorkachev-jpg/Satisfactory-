import assert from "node:assert/strict";
import { simulatePowerGrid, createMachineState, setMachineRecipe, tickMachine, transferBelt } from "../game/production.js";

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

// Production must consume recipe inputs and put the correct products into the output buffer.
const smelterProcess = createMachineState("Smelter", "smelter-process");
assert.equal(setMachineRecipe(smelterProcess, "Iron Ingot"), true);
smelterProcess.input["Iron Ore"] = 2;
tickMachine(smelterProcess, 2.1);
assert.equal(smelterProcess.input["Iron Ore"], 1);
assert.equal(smelterProcess.output["Iron Ingot"], 1);
assert.ok(Math.abs(smelterProcess.elapsed - 0.1) < 1e-8);

// The constructor converts three ingots into two plates on its six-second recipe.
const constructorProcess = createMachineState("Constructor", "constructor-process");
assert.equal(setMachineRecipe(constructorProcess, "Iron Plate"), true);
constructorProcess.input["Iron Ingot"] = 3;
tickMachine(constructorProcess, 6);
assert.equal(constructorProcess.input["Iron Ingot"], 0);
assert.equal(constructorProcess.output["Iron Plate"], 2);

// A Miner stops on an exhausted deposit and never creates negative resource amounts.
const minerProcess = createMachineState("Miner", "miner-process", "Iron Ore");
minerProcess.nodeRemaining = 1;
tickMachine(minerProcess, 1.1);
assert.equal(minerProcess.nodeRemaining, 0);
assert.equal(minerProcess.output["Iron Ore"], 1);
tickMachine(minerProcess, 2);
assert.equal(minerProcess.nodeRemaining, 0);
assert.equal(minerProcess.output["Iron Ore"], 1);

// The Mk.1 conveyor transfers buffered products at one item per second.
const beltSource = { output: { "Iron Ingot": 2 } };
const beltTarget = { input: {} };
const beltProcess = { item: "Iron Ingot", elapsed: 0, itemsPerSecond: 1, active: true };
assert.equal(transferBelt(beltProcess, beltSource, beltTarget, 1.1), 1);
assert.equal(transferBelt(beltProcess, beltSource, beltTarget, 0.9), 1);
assert.equal(beltSource.output["Iron Ingot"], 0);
assert.equal(beltTarget.input["Iron Ingot"], 2);
console.log("Machine production, miner depletion and conveyor tests passed.");

const assemblerProcess = createMachineState("Assembler", "assembler-process");
assert.equal(setMachineRecipe(assemblerProcess, "Reinforced Iron Plate"), true);
assemblerProcess.input["Iron Plate"] = 6;
assemblerProcess.input.Screw = 12;
tickMachine(assemblerProcess, 12);
assert.equal(assemblerProcess.input["Iron Plate"], 0);
assert.equal(assemblerProcess.input.Screw, 0);
assert.equal(assemblerProcess.output.ReinforcedIronPlate, 1);

// The 15 MW Assembler is supported by a connected 30 MW Biomass Burner.
const assemblerGenerator = { userData: { machine: { id: "gen-assembler", type: "Biomass Burner", fuel: { Biomass: 1 } } } };
const assemblerPole = { userData: { powerPoleId: "pole-assembler" } };
const assemblerConsumer = { userData: { machine: { id: "assembler-1", type: "Assembler", recipe: "Reinforced Iron Plate", active: true, input: { "Iron Plate": 6, Screw: 12 }, output: {}, powered: false } } };
state = simulatePowerGrid([assemblerGenerator, assemblerConsumer], [assemblerPole], [
  { a: "gen-assembler", b: "pole-assembler" }, { a: "pole-assembler", b: "assembler-1" }
], 1);
assert.equal(state.consumption, 15);
assert.equal(assemblerConsumer.userData.machine.powered, true);
console.log("Assembler reinforced plate production tests passed.");
