/**
 * The Decide phase of the OODA loop.
 * Simulates an LLM evaluating the oriented context and outputting a strictly
 * typed JSON execution plan containing the exact tools and parameters to use.
 *
 * @param {Object} state - The current state of the OODA loop.
 * @returns {Object} The updated state containing the plan (tools and parameters).
 */
function decide(state) {
  if (!state || state.phase !== 'orient') {
    throw new Error("Decide phase must follow Orient phase.");
  }

  const { orientation, observations } = state;
  let plan = {
    tools: [],
    rationale: 'Evaluated context to determine next actions.'
  };

  // Simulate LLM evaluation
  const { currentSituation } = orientation;

  if (currentSituation.newInputsCount > 0) {
    // If there are new inputs, plan to process them
    const primaryFocus = currentSituation.primaryFocus;

    // Simple heuristic to mock LLM deciding what to do based on input
    if (primaryFocus.includes('search') || primaryFocus.includes('find')) {
      plan.tools.push({
        name: 'searchTool',
        parameters: { query: primaryFocus }
      });
      plan.rationale = `Need to search for information related to: ${primaryFocus}`;
    } else if (primaryFocus.includes('calculate') || primaryFocus.includes('math')) {
      plan.tools.push({
        name: 'calculatorTool',
        parameters: { expression: primaryFocus }
      });
      plan.rationale = `Need to calculate: ${primaryFocus}`;
    } else {
      plan.tools.push({
        name: 'textGeneratorTool',
        parameters: { prompt: `Respond to: ${primaryFocus}` }
      });
      plan.rationale = `Generate response for input: ${primaryFocus}`;
    }
  } else if (currentSituation.hasPendingTasks) {
    // If no new inputs but pending tasks, plan to execute next task
    const nextTask = observations.activeTasks[0];
    plan.tools.push({
      name: 'taskExecutorTool',
      parameters: { taskId: nextTask.id || 'unknown' }
    });
    plan.rationale = `Continue executing pending task: ${nextTask.name || 'unknown'}`;
  } else {
    // Idle state
    plan.tools.push({
      name: 'idleTool',
      parameters: { duration: 1000 }
    });
    plan.rationale = 'No current tasks or inputs. Idling.';
  }

  // Ensure output is strictly typed representation
  const strictlyTypedPlan = {
    ...plan,
    schemaVersion: '1.0',
    timestamp: Date.now()
  };

  return {
    ...state,
    phase: 'decide',
    decision: strictlyTypedPlan
  };
}

module.exports = { decide };
