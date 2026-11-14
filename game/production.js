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
  return !!recipe && Object.entries(recipe.inputs).every(([item, count]) => (machine.input[item] || 0) >= count);
}

export function tickMachine(machine, dt) {
  if (!machine.active || dt <= 0) return;
  if (machine.type === "Miner") {
    if (!machine.nodeType || machine.nodeRemaining <= 0) return;
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
