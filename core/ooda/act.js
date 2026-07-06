/**
 * The Act phase of the OODA loop.
 * Acts as an execution router that triggers the tools defined in the decision phase,
 * captures the outputs, and feeds them directly back into the Observe module
 * (by setting up action results for the next iteration).
 *
 * @param {Object} state - The current state of the OODA loop.
 * @param {Object} toolsAvailable - Dictionary of available tool execution functions.
 * @returns {Object} The updated state containing the results of actions taken.
 */
async function act(state, toolsAvailable = {}) {
  if (!state || state.phase !== 'decide') {
    throw new Error("Act phase must follow Decide phase.");
  }

  const { decision, observations } = state;
  const actionResults = [];

  for (const toolDef of decision.tools) {
    const { name, parameters } = toolDef;
    let result;

    try {
      if (toolsAvailable[name]) {
        // Execute the real tool if available
        result = await toolsAvailable[name](parameters);
      } else {
        // Mock tool execution for testing
        result = `Mock result from ${name} with params: ${JSON.stringify(parameters)}`;
      }

      actionResults.push({
        tool: name,
        status: 'success',
        result,
        timestamp: Date.now()
      });
    } catch (error) {
      actionResults.push({
        tool: name,
        status: 'error',
        error: error.message,
        timestamp: Date.now()
      });
    }
  }

  // Manage active tasks based on action completion
  let updatedActiveTasks = observations.activeTasks ? [...observations.activeTasks] : [];

  // If the decision was to work on a pending task, we might remove or update it here
  if (decision.tools.some(t => t.name === 'taskExecutorTool') && updatedActiveTasks.length > 0) {
    // Just simulating task completion by removing the first task
    updatedActiveTasks.shift();
  }

  return {
    ...state,
    phase: 'act',
    actionResults,       // Captured outputs for the next Observe phase
    activeTasks: updatedActiveTasks, // Updated active tasks list
    // Clear raw inputs so we don't re-process them next loop unless resubmitted
    rawInputs: {}
  };
}

module.exports = { act };
