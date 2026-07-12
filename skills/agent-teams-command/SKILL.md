---
name: agent-teams-command
description: Use when work has genuinely independent streams or distinct builder, evaluator, domain, and integration roles that require bounded multi-agent command.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "high-risk"
  assumes: "The runtime supports isolated workers or equivalent processes, durable shared state, and explicit integration ownership."
  conflicts_with: "Parallelism for its own sake, overlapping write ownership, chat-only coordination, or workers crossing permission boundaries."
---

# Agent Teams Command

<skill_contract>

Strategic intent and final integration remain serial; owned execution may run in parallel. Use the Ender lens for commander understanding, Palantir for operational objects/actions, and von Neumann for executable, inspectable process architecture. Detailed patterns: `references/ender-palantir-command-patterns.md`; examples: `references/classic-campaigns.md`.

## Usage Template

Provide: mission, non-goals, workstreams, dependencies, files/systems, acceptance criteria, permissions, review bandwidth, runtime capabilities, budget, and integration owner.

## Workflow

<intake>

Admit a team only when at least two workstreams can proceed with low coordination, or distinct roles materially improve evaluation/safety. Calculate orchestration tax: setup, context duplication, IPC, merge conflict, review, and cleanup. If one process can finish within the same review budget, keep one process.

</intake>

<unknowns_gate>

Resolve commander intent, object/state vocabulary, ownership, dependency direction, verifier, join gate, and permission boundary before recruiting. Return `NEEDS_INPUT` when an irreversible business decision or authority cannot be discovered locally. Workers may probe implementation unknowns only inside their territory.

</unknowns_gate>

<execute>

1. Write a command program: objective, non-goals, finite actions, commander, checkpoint cadence, interrupt policy, state/artifact paths, IPC schema, allowed/denied tools, verifier, stop, recovery, and promotion boundary.
2. Atomically decompose work by interface/territory. Each task has one owner, inputs, output artifact, dependencies, definition of done, verifier, budget, and blast radius.
3. Select the smallest topology: maker-checker, manager-workers, or specialist pipeline. Route workers by required capabilities and runtime policy, never fixed model names.
4. Isolate mutable work with separate worktrees/branches or disjoint files. Shared schemas/contracts are commander-owned until published.
5. Use typed IPC: `{task_id, state, artifact, evidence, decision, unknowns, dependency, next_action}`. Messages change state; status chatter does not.
6. Require workers to run `state + evidence -> next action -> verifier -> next state | stop | escalate` and checkpoint after each material action.
7. Monitor attention and review budgets, repeated failures, idle dependencies, ownership violations, and architecture drift. Rebalance or serialize when coordination cost rises.
8. Integrate one verified workstream at a time in dependency order. The integration owner runs broader regression/eval checks and records accepted/rejected artifacts.
9. Run an independent reviewer/red team for consequential behavior. Human approval precedes production, publication, spending, destructive/shared-state actions, credentials, and policy changes; prepare rollback first.
10. Close workers, remove temporary worktrees/state, reconcile tasks, preserve receipts, and extract only promotion-gated reusable patterns.

Hooks are optional executable infrastructure, not prose. Configure one only when its referenced program exists, has tests, and emits a verified receipt; never copy illustrative hook commands as if installed.

</execute>

<evaluate>

Evaluate mission outcome, per-workstream evidence, interface compatibility, ownership compliance, integration diff, regression suite, reviewability, residual risk, and cleanup. Quiet green checks are insufficient if the commander cannot explain architecture delta and rollback.

</evaluate>

<retry_policy>

`max_attempts: 2` per failed task/integration signature. Retry the failed unit only after changing diagnosis, owner, scope, or strategy. Stop/rebalance on repeated signature, ownership conflict, rising orchestration tax, exhausted review budget, or `NO_PROGRESS`.

</retry_policy>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus mission/contract version, command board, task graph, ownership map, worker/worktree registry, IPC events, attention budget, approvals, integration ledger, rollback points, and cleanup receipt.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: intent, ownership, verifier, join, or authority is unresolved; do not launch.
- `BLOCKED_DEPENDENCY`: checkpoint the worker and advance only independent tasks.
- `BLOCKED_PERMISSION`: stop the affected stream and request approval.
- `VERIFY_FAILED`: reject the artifact at its integration gate; preserve evidence.
- `NO_PROGRESS`: the same signature repeats after changed strategy. `max_attempts: 2`.
- `BUDGET_STOP`: interrupt workers, checkpoint, and emit a partial integration/cleanup plan.

## Output Contract

Return `status`, `result` (mission and integrated artifacts), `evidence` (task/integration/cleanup receipts), `unknowns`, and `next_action` including approval or rollback.

## Edge Cases

- Two workers need the same schema file: commander publishes the contract first; serialize schema edits and let workers consume it read-only.
- All workers report success but integration fails: mission status is `VERIFY_FAILED`; reject incompatible artifacts rather than averaging reports.

## Success Metrics

- Parallel work reduces elapsed time or improves independent evaluation beyond its coordination cost.
- Ownership is exclusive, IPC is typed, and integration is serial and evidence-gated.
- Final state is reproducible, reviewable, recoverable, and clean.

## Quality Gates

- [ ] Team admission and orchestration-tax calculation justify multi-agent use.
- [ ] Every task has one owner, artifact, verifier, budget, and stop condition.
- [ ] Independent review, approval, and rollback match risk.
- [ ] Integration and cleanup receipts match actual repository/runtime state.
- [ ] Capability routing contains no durable model binding.

</skill_contract>
