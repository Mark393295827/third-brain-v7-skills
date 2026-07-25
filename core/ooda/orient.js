/**
 * The Orient phase of the OODA loop.
 * Builds a context module that queries the vector database for historical memory
 * and applies structural frameworks to synthesize the current situation.
 *
 * @param {Object} state - The current state of the OODA loop.
 * @param {Object} contextStore - Optional mock store to simulate a vector database.
 * @returns {Object} The updated state containing context/orientation data.
 */
function orient(state, contextStore = {}) {
  if (!state || state.phase !== 'observe') {
    throw new Error("Orient phase must follow Observe phase.");
  }

  const { observations } = state;
  const memoryQuery = [];

  if (observations.userInputs && observations.userInputs.length > 0) {
    memoryQuery.push(...observations.userInputs);
  }

  if (observations.systemTriggers && observations.systemTriggers.length > 0) {
    memoryQuery.push(...observations.systemTriggers);
  }

  // Simulate querying a vector database for historical memory
  const historicalMemory = memoryQuery.map(query => {
    // In a real system, this would be a vector similarity search
    return contextStore[query] || `Memory related to ${query}`;
  });

  // Synthesize the current situation based on observations and historical memory
  // This applies structural frameworks
  const synthesizedContext = {
    historicalContext: historicalMemory,
    currentSituation: {
      hasPendingTasks: observations.activeTasks.length > 0,
      hasRecentResults: observations.actionResults.length > 0,
      newInputsCount: observations.userInputs.length + observations.systemTriggers.length,
      primaryFocus: memoryQuery[0] || 'idle'
    },
    frameworkApplied: 'basic-situational-awareness'
  };

  return {
    ...state,
    phase: 'orient',
    orientation: synthesizedContext
  };
}

module.exports = { orient };
