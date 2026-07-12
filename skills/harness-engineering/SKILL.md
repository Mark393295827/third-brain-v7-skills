---
name: harness-engineering
description: Use when an agent workflow needs production-like runtime controls for context, tools, permissions, observability, scheduling, evaluation, recovery, or maintenance.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "high-risk"
  assumes: "The workflow uses tools or delegated actions whose environment, permissions, and event trail can be controlled."
  conflicts_with: "Prompt-only safety, broad credentials, hidden tool effects, or autonomous routines without finite budgets and rollback."
---

# Harness Engineering

<skill_contract>

Treat the harness as the kernel around an LLM OS: context is RAM, durable state is disk, tools are system calls, skills are programs, the scheduler is control, and evals are verifiers. Load `references/runtime-control-patterns.md` for matrices and schemas.

## Usage Template

Provide: workflow, users, agent roles, environment, tools/connections, data sensitivity, delegated actions, cadence, throughput/SLA, failure history, and risk tolerance.

## Workflow

<intake>

Run the trace gate: the harness must be able to show what the agent saw, decided, called, changed, and verified. Separate **Agent** (instructions/capabilities), **Environment** (network/files/credentials), and **Session** (mounted context/events/state). Define one auditable control path for high-risk intent and final joins.

</intake>

<unknowns_gate>

If state ownership, credential scope, external side effects, retention, or approval authority is unclear, return `NEEDS_INPUT`. Probe tools with read-only discovery where possible; unknown side effects default to denied.

</unknowns_gate>

<execute>

1. Pass Four-C: **Context** truth/retrieval, **Connections** scoped accounts/APIs, **Capabilities** versioned skills/scripts/evals, **Cadence** trigger/receipt/anomaly/stop.
2. Map runtime: stored program, control unit, hot context, durable disk, event bus, I/O tools, verifier, and garbage collector.
3. Choose the lowest-context primitive: deterministic script/hook, skill, connector, dynamic workflow, or agent team. Load capabilities lazily.
4. Define each tool as a narrow system call with purpose, explicit inputs, bounds, timeout, idempotency, failure path, evidence, and audit location.
5. Enforce least privilege in the environment, not only prose. Escalate autonomy through observe -> co-drive -> scoped reversible action -> monitored routine -> audited low-risk autonomy.
6. For delegated action require mandate, scope, limit, preview, receipt, and rollback. Human approval governs irreversible/shared/financial/published/credentialed actions.
7. Add deterministic feedback (tests, lint, LSP, policy checks) outside context when possible; add independent evaluator/red team for high-risk semantic output.
8. Persist an append-only session event log and checkpoint; define alerts, fallback, incident response, cleanup, permission review, and stale-context/rule review.
9. For scheduled work define Trigger, Context, Steering, Receipt, budget, stop, recovery, and executor health. A schedule firing is not task success.

</execute>

<evaluate>

Threat-model normal, denied, timeout, partial-write, stale-context, duplicate-trigger, compromised-input, evaluator-disagreement, and rollback paths. Verify permissions with actual environment boundaries and run an independent end-to-end trace. Adoption fails if operators cannot inspect or recover the system.

</evaluate>

<retry_policy>

`max_attempts: 3` per tool/failure class. Retry only idempotent or compensated actions after changing diagnosis/strategy. Use exponential delay for transient dependencies. Stop on repeated signature, permission denial, ambiguous side effect, or `NO_PROGRESS`.

</retry_policy>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus agent/environment/session versions, context manifest, tool/permission registry, event offsets, approvals, evals, alerts, recovery point, and rollback receipts. State transitions are auditable and replayable.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: ownership, effect, retention, or approval authority is ambiguous.
- `BLOCKED_PERMISSION`: deny the call and continue with a safer read-only path when useful.
- `BLOCKED_DEPENDENCY`: checkpoint, back off, and expose executor health.
- `VERIFY_FAILED`: trace, eval, guardrail, or rollback test fails; block autonomy escalation.
- `NO_PROGRESS`: changed attempts repeat the signature. `max_attempts: 3`.
- `BUDGET_STOP`: stop scheduler/workers, checkpoint, and emit a recovery receipt.

## Output Contract

Return `status`, `result` (runtime architecture and controls), `evidence` (trace/eval/failure tests), `unknowns`, and `next_action` including approval or rollback.

## Edge Cases

- A connector exposes broad account access for a narrow task: create a scoped proxy/allowlist or keep the workflow manual; instructions alone are insufficient.
- The scheduler ran on time but the state store was stale: block mutation, mark the run failed, and recover from the last verified checkpoint.

## Success Metrics

- Every delegated action is bounded, observable, independently verifiable, and recoverable.
- Runtime state can be replayed across sessions without relying on chat history.
- Autonomy level follows measured reliability and operator review capacity.

## Quality Gates

- [ ] Agent, Environment, Session, and serial control ownership are explicit.
- [ ] Tool effects are enforced by real permissions and contracts.
- [ ] Independent eval, approval, manual fallback, and rollback match risk.
- [ ] Schedules have executor receipts, hard budgets, stop, and recovery.
- [ ] Maintenance includes cleanup, permission audit, and rule half-life.

</skill_contract>
