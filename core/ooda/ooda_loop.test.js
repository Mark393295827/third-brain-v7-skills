const assert = require('assert');
const { runOODALoop } = require('./index');

async function testOODALoop() {
  console.log("Starting OODA Loop Integration Test...");

  // Mock Context Store (Vector DB)
  const mockContextStore = {
    'search: weather in Tokyo': 'Memory: User likes checking weather before traveling. Historical preference is Celsius.',
    'calculate: 5 + 5': 'Memory: Simple arithmetic operation.'
  };

  // Mock Tools available
  const mockTools = {
    searchTool: async (params) => {
      return `Search results for: ${params.query}. It is 22 degrees Celsius.`;
    },
    calculatorTool: async (params) => {
      // Very naive calculator mock
      return 10;
    },
    taskExecutorTool: async (params) => {
      return `Task ${params.taskId} executed successfully.`;
    },
    idleTool: async (params) => {
      return `Idled for ${params.duration}ms.`;
    }
  };

  // Initial inputs representing a multi-turn scenario setup
  const initialInputs = {
    userInputs: ['search: weather in Tokyo'],
    systemTriggers: []
  };

  const initialState = {
    activeTasks: [
      { id: 'task_001', name: 'Background Data Sync' }
    ]
  };

  try {
    // Run loop
    const finalState = await runOODALoop(initialState, initialInputs, mockContextStore, mockTools, 10);

    // Assertions to verify state passes through phases and terminates correctly

    // 1. Terminated due to idling (no more tasks/inputs)
    assert.strictEqual(finalState.phase, 'act', "Final phase should be 'act'");
    assert.ok(finalState.totalIterations > 1, "Loop should run multiple iterations");

    // 2. Initial input triggered a search
    // Check if the first iteration handled the search and task execution
    assert.ok(
      finalState.totalIterations >= 3,
      "Should take at least 3 iterations (1 for search, 1 for task, 1 for idle)"
    );

    // 3. No active tasks left
    assert.strictEqual(finalState.activeTasks.length, 0, "All tasks should be completed");

    // 4. Action results reflect executed tools
    const toolNamesExecuted = finalState.actionResults.map(r => r.tool);
    assert.ok(toolNamesExecuted.includes('idleTool'), "Final iteration should have executed idleTool");

    console.log(`✅ OODA Loop test passed successfully! Iterations run: ${finalState.totalIterations}`);
    console.log("Final State Summary:", {
      totalIterations: finalState.totalIterations,
      remainingTasks: finalState.activeTasks.length,
      lastDecision: finalState.decision.rationale
    });

  } catch (error) {
    console.error("❌ OODA Loop test failed:", error);
    process.exit(1);
  }
}

// Run the test
testOODALoop();
