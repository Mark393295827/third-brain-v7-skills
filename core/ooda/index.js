const { observe } = require('./observe');
const { orient } = require('./orient');
const { decide } = require('./decide');
const { act } = require('./act');

/**
 * Runs a single iteration of the OODA loop.
 *
 * @param {Object} state - The current state of the system.
 * @param {Object} inputs - Incoming inputs for this cycle.
 * @param {Object} contextStore - Optional mock store to simulate a vector database.
 * @param {Object} toolsAvailable - Dictionary of available tool execution functions.
 * @returns {Object} The updated state after one full loop.
 */
async function runOODALoopOnce(state, inputs = {}, contextStore = {}, toolsAvailable = {}) {
  // 1. Observe
  let currentState = observe(state, inputs);

  // 2. Orient
  currentState = orient(currentState, contextStore);

  // 3. Decide
  currentState = decide(currentState);

  // 4. Act
  currentState = await act(currentState, toolsAvailable);

  return currentState;
}

/**
 * Runs the OODA loop continuously until a termination condition is met or max iterations reached.
 *
 * @param {Object} initialState - The starting state.
 * @param {Array|Object} initialInputs - Initial inputs to bootstrap the loop.
 * @param {Object} contextStore - Optional mock store to simulate a vector database.
 * @param {Object} toolsAvailable - Dictionary of available tool execution functions.
 * @param {number} maxIterations - Maximum number of iterations before forcing termination.
 * @returns {Object} The final state.
 */
async function runOODALoop(initialState = {}, initialInputs = {}, contextStore = {}, toolsAvailable = {}, maxIterations = 5) {
  let state = initialState;
  let inputs = initialInputs;
  let iteration = 0;

  while (iteration < maxIterations) {
    iteration++;

    state = await runOODALoopOnce(state, inputs, contextStore, toolsAvailable);

    // Check termination condition
    // For this simulation: terminate if there are no more active tasks and no new inputs
    const { actionResults, activeTasks, decision } = state;

    const isIdling = decision.tools.some(t => t.name === 'idleTool');

    if (isIdling && activeTasks.length === 0) {
      // Loop finished naturally
      break;
    }

    // For subsequent iterations, we don't pass the initial inputs again.
    // The state already carries over activeTasks and actionResults into the next Observe phase.
    inputs = {};
  }

  return {
    ...state,
    totalIterations: iteration
  };
}

module.exports = {
  observe,
  orient,
  decide,
  act,
  runOODALoopOnce,
  runOODALoop
};
