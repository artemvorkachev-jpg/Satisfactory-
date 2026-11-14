// Deterministic production simulation for the browser build.
// Rates and recipes are expressed in items/second; rendering is kept outside this module.
export const RECIPES = {
  Smelter: {
    "Iron Ingot": { inputs: { "Iron Ore": 1 }, output: { "Iron Ingot": 1 }, seconds: 2 },
    "Copper Ingot": { inputs: { "Copper Ore": 1 }, output: { "Copper Ingot": 1 }, seconds: 2 }
  },
  Constructor: {
    "Iron Plate": { inputs: { "Iron Ingot": 3 }, output: { "Iron Plate": 2 }, seconds: 6 },
    "Iron Rod": { inputs: { "Iron Ingot": 1 }, output: { "Iron Rod": 1 }, seconds: 4 },
    "Wire": { inputs: { "Copper Ingot": 1 }, output: { Wire: 2 }, seconds: 0.5 },
    "Cable": { inputs: { Wire: 2 }, output: { Cable: 1 }, seconds: 2 },
    "Concrete": { inputs: { Limestone: 3 }, output: { Concrete: 1 }, seconds: 4 }
  }
};

export const BELT_MK1_ITEMS_PER_SECOND = 1;
export const MINER_MK1_NORMAL_ITEMS_PER_SECOND = 1;

export function createMachineState(type, id, nodeType = null) {
  return {
    id, type, recipe: null, nodeType, nodeRemaining: Infinity,
    input: {}, output: {}, elapsed: 0, active: true
  };
}

export function canRunRecipe(machine) {
  const recipe = RECIPES[machine.type]?.[machine.recipe];
  if (!recipe) return false;
  const hasInputs = Object.entries(recipe.inputs).every(([item, count]) => (machine.input[item] || 0) >= count);
  const hasOutputSpace = Object.entries(recipe.output).every(([item, count]) => (machine.output[item] || 0) + count <= 100);
  return hasInputs && hasOutputSpace;
}

export function tickMachine(machine, dt) {
  if (!machine.active || dt <= 0) return;
  if (machine.type === "Miner") {
    if (!machine.nodeType || machine.nodeRemaining <= 0 || (machine.output[machine.nodeType] || 0) >= 100) return;
    machine.elapsed += dt;
    while (machine.elapsed >= 1 && machine.nodeRemaining > 0) {
      machine.elapsed -= 1;
      machine.nodeRemaining -= 1;
      machine.output[machine.nodeType] = (machine.output[machine.nodeType] || 0) + 1;
    }
    return;
  }
  const recipe = RECIPES[machine.type]?.[machine.recipe];
  if (!recipe) return;
  if (!canRunRecipe(machine)) return;
  machine.elapsed += dt;
  while (machine.elapsed >= recipe.seconds && canRunRecipe(machine)) {
    machine.elapsed -= recipe.seconds;
    for (const [item, count] of Object.entries(recipe.inputs)) machine.input[item] -= count;
    for (const [item, count] of Object.entries(recipe.output)) machine.output[item] = (machine.output[item] || 0) + count;
  }
}

export function transferBelt(belt, source, target, dt) {
  if (!source || !target || !belt.active) return 0;
  belt.elapsed += dt;
  let moved = 0;
  while (belt.elapsed >= 1 / belt.itemsPerSecond) {
    const item = belt.item;
    if (!item || (source.output[item] || 0) < 1) break;
    source.output[item] -= 1;
    target.input[item] = (target.input[item] || 0) + 1;
    belt.elapsed -= 1 / belt.itemsPerSecond;
    moved += 1;
  }
  return moved;
}

export function setMachineRecipe(machine, recipeName) {
  if (!RECIPES[machine.type]?.[recipeName]) return false;
  machine.recipe = recipeName;
  machine.elapsed = 0;
  return true;
}


// Early-game power model. Values follow the Satisfactory production rates:
// Biomass Burner 30 MW; Miner Mk.1 5 MW; Smelter 4 MW; Constructor 4 MW.
export const POWER_DEMAND_MW = { Miner: 5, Smelter: 4, Constructor: 4 };
export const BIOMASS_FUEL_MJ = { Leaves: 15, Wood: 100, Biomass: 180, "Solid Biofuel": 450 };

export function simulatePowerGrid(machines, poles, connections, dt) {
  const nodes = new Map();
  for (const group of [...poles, ...machines]) {
    const state = group.userData.machine;
    const id = state?.id || group.userData.powerPoleId;
    if (id) nodes.set(id, { group, state, id });
  }
  const adjacency = new Map([...nodes.keys()].map(id => [id, new Set()]));
  for (const edge of connections) {
    if (!adjacency.has(edge.a) || !adjacency.has(edge.b)) continue;
    adjacency.get(edge.a).add(edge.b);
    adjacency.get(edge.b).add(edge.a);
  }
  const visited = new Set();
  const result = { capacity: 0, consumption: 0, poweredMachines: 0, connectedMachines: 0, fuelUsed: 0 };
  for (const id of nodes.keys()) {
    if (visited.has(id)) continue;
    const component = [];
    const queue = [id];
    visited.add(id);
    while (queue.length) {
      const current = queue.shift();
      component.push(nodes.get(current));
      for (const next of adjacency.get(current)) if (!visited.has(next)) { visited.add(next); queue.push(next); }
    }
    const consumers = component.filter(n => n.state && POWER_DEMAND_MW[n.state.type]);
    const generators = component.filter(n => n.state?.type === "Biomass Burner");
    const demand = consumers.reduce((sum, n) => sum + POWER_DEMAND_MW[n.state.type], 0);
    const available = generators.reduce((sum, n) => {
      const fuel = n.state.fuel || {};
      return sum + (Object.entries(fuel).some(([kind, count]) => count > 0 && BIOMASS_FUEL_MJ[kind]) ? 30 : 0);
    }, 0);
    const supplied = Math.min(demand, available);
    result.capacity += available;
    result.consumption += demand;
    result.connectedMachines += consumers.length;
    const hasEnough = demand <= available + 1e-6;
    for (const consumer of consumers) {
      consumer.state.powered = hasEnough;
      if (hasEnough) result.poweredMachines++;
    }
    if (!hasEnough || demand <= 0) continue;
    let remainingLoad = demand;
    for (const generator of generators) {
      const state = generator.state;
      const fuel = state.fuel || (state.fuel = {});
      const fuelKind = Object.keys(fuel).find(kind => fuel[kind] > 0 && BIOMASS_FUEL_MJ[kind]);
      if (!fuelKind) { state.powered = false; continue; }
      const share = Math.min(30, remainingLoad);
      const energyPerSecond = share;
      let energy = energyPerSecond * dt;
      while (energy > 1e-8) {
        const availableEnergy = fuel[fuelKind] * BIOMASS_FUEL_MJ[fuelKind];
        if (availableEnergy <= energy + 1e-8) {
          energy -= availableEnergy;
          result.fuelUsed += fuel[fuelKind];
          fuel[fuelKind] = 0;
          const next = Object.keys(fuel).find(kind => fuel[kind] > 0 && BIOMASS_FUEL_MJ[kind]);
          if (!next) break;
          // Continue the same load on the next fuel type.
          const consumed = Math.min(fuel[next], energy / BIOMASS_FUEL_MJ[next]);
          fuel[next] -= consumed;
          result.fuelUsed += consumed;
          energy -= consumed * BIOMASS_FUEL_MJ[next];
        } else {
          const consumed = energy / BIOMASS_FUEL_MJ[fuelKind];
          fuel[fuelKind] -= consumed;
          result.fuelUsed += consumed;
          energy = 0;
        }
      }
      remainingLoad -= share;
      state.powered = true;
    }
  }
  return result;
}
