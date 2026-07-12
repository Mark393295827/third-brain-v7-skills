---
name: agentic-engineering
description: Use when designing or refactoring a model-native engineering workflow with bounded autonomy, probes, custom evaluation, durable state, and verified write-back.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "high-risk"
  assumes: "The repository, objective, acceptance criteria, and execution permissions can be inspected."
  conflicts_with: "Agent complexity without adoption value, coding before probing material unknowns, or completion claims without fresh tests."
---

# Agentic Engineering

<skill_contract>

An agent is a stateful engineering process, not a prompt. Its quality ceiling is the combination of objective, context, tools, taste/evaluation, permissions, recovery, and feedback latency.

## Usage Template

Provide: engineering objective, repository/workflow, users, acceptance criteria, constraints, permissions, risk, current evidence, and durable state location.

## Workflow

<intake>

1. Inspect repository guidance, code, tests, state, and current failure before proposing architecture.
2. Define the observable end state, non-goals, owner, budget, and review bandwidth.
3. Run the adoption gate: use an agent only when ambiguity/adaptation outweigh orchestration, verification, and maintenance cost. Prefer deterministic code for stable transformations.

</intake>

<unknowns_gate>

Map unknowns into: known, probeable from tools/files, testable by prototype, and externally blocked. Probe boundary/interface unknowns before implementation. Return `NEEDS_INPUT` only when a missing business decision, permission, or irreversible tradeoff cannot be discovered locally; otherwise label assumptions and test them.

</unknowns_gate>

<execute>

1. Write the macro action: `trigger -> objective -> inputs -> constraints -> artifact -> verifier -> state -> stop/recovery`.
2. Define quality with domain-specific examples, anti-examples, guardrails, and cheap checks; generic “good quality” is invalid.
3. Decompose into the fewest independently verifiable units with one owner each.
4. Route by capability (reasoning, tool use, latency, context, modality, cost) and runtime policy; keep vendor/model names out of durable contracts.
5. Establish harness controls: least privilege, tool schemas, timeouts, observability, checkpoints, idempotency, and rollback.
6. Run a thin loop: understand -> plan -> smallest change -> targeted test -> inspect diff/state -> broader check.
7. Use independent evaluation or adversarial review for consequential logic, interfaces, and claims.
8. Remove temporary scaffolding, duplicate abstractions, and context that no longer changes decisions.
9. Write back only reusable, verified deltas. Promotion into skills/SOPs requires repeated support or local verification plus a cheap objective check.

Human approval is mandatory before production, publication, spending, destructive mutation, credentials, policy, or other delegated external action. Prepare rollback before crossing that boundary.

</execute>

<evaluate>

Compare the result with acceptance criteria, custom evals, tests, diff scope, security/permission boundaries, and user workflow. Check both task success and adoption cost. A large reasoning trace is not evidence; receipts are.

</evaluate>

<retry_policy>

`max_attempts: 3` per failure class. Retry only after updating the diagnosis and changing strategy, input, or tool. Stop on repeated signature, expanding blast radius, exhausted review bandwidth, or `NO_PROGRESS`.

</retry_policy>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus objective/non-goals, decisions, probes, active files, tool receipts, diff, eval results, permissions, approval, rollback point, and write-back candidates. Version checkpoints at phase boundaries.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: a blocked business/permission decision cannot be discovered safely.
- `BLOCKED_DEPENDENCY`: required repository, tool, or environment is unavailable.
- `BLOCKED_PERMISSION`: the next delegated action lacks approval.
- `VERIFY_FAILED`: tests, evals, or guardrails contradict the requested claim.
- `NO_PROGRESS`: changed attempts repeat the same failure. `max_attempts: 3`.
- `BUDGET_STOP`: preserve state and return the smallest reviewable handoff.

## Output Contract

Return `status`, `result` (implemented/design outcome), `evidence` (tests, evals, diff, receipts), `unknowns`, and `next_action` including approval or rollback when relevant.

## Edge Cases

- The user requests multi-agent work for a one-file deterministic edit: use one bounded process and explain that coordination cost exceeds expected value.
- Tests pass but the user-facing workflow regresses: return `VERIFY_FAILED`; acceptance evidence outranks local unit success.

## Success Metrics

- The smallest sufficient architecture reaches the observable end state.
- Unknowns are probed or explicitly bounded before they become code.
- Fresh independent evidence supports completion and write-back.

## Quality Gates

- [ ] Adoption value exceeds orchestration and review cost.
- [ ] Objective, non-goals, permissions, budgets, evals, and recovery are explicit.
- [ ] Independent verification covers consequential behavior.
- [ ] Approval and rollback precede delegated external action.
- [ ] Promoted knowledge passes the governance gate.

</skill_contract>
