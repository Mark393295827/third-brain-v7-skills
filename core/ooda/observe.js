/**
 * The Observe phase of the OODA loop.
 * Captures incoming user inputs, system triggers, and the current state of active tasks.
 *
 * @param {Object} state - The current state of the OODA loop.
 * @param {Object} inputs - Incoming inputs for this cycle.
 * @returns {Object} The updated state containing observation data.
 */
function observe(state, inputs = {}) {
  const currentState = state || {};

  // Extract inputs
  const userInputs = inputs.userInputs || [];
  const systemTriggers = inputs.systemTriggers || [];

  // Active tasks from previous state, or initialize
  const activeTasks = currentState.activeTasks || [];

  // Previous actions results, if any
  const actionResults = currentState.actionResults || [];

  // Observation context
  const observations = {
    timestamp: Date.now(),
    userInputs,
    systemTriggers,
    activeTasks,
    actionResults,
    rawInputs: inputs
  };

  return {
    ...currentState,
    phase: 'observe',
    observations
  };
}

module.exports = { observe };
