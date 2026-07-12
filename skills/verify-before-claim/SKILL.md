---
name: verify-before-claim
description: Use when an agent is about to claim completion, correctness, safety, publication, deployment, or any consequential external fact.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "high-risk"
  assumes: "At least one objective verification method or authoritative source can be identified."
  conflicts_with: "Inferring success from effort, stale evidence, partial checks, or self-authored assertions."
---

# Verify Before Claim

<skill_contract>

No evidence, no claim. Match the check to the exact claim, use fresh evidence, and keep execution authority separate from approval authority for consequential actions.

## Usage Template

Provide: proposed claim, artifact or system, risk level, available checks, expected result, permissions, and rollback path.

## Workflow

<intake>

1. Rewrite the proposed statement as one falsifiable claim.
2. Classify risk: low, material, or consequential.
3. Select the cheapest check that directly tests the claim.
4. Record expected signal, time boundary, and acceptable evidence.

</intake>

<unknowns_gate>

If the artifact, expected behavior, or verification method is missing, return `NEEDS_INPUT`. If only indirect evidence exists, return `INSUFFICIENT_EVIDENCE` or narrow the claim; never fill the gap with confidence language.

</unknowns_gate>

<execute>

Run the selected check after the final material change. Examples: targeted test, lint, build, link check, read-after-write, diff inspection, source comparison, dashboard query, or deployment health check. Capture command/query, timestamp, scope, exit status, and key output.

For material or consequential claims, obtain independent verification from a separate check, reviewer, or evidence source. Require human approval before irreversible publication, deployment, spending, deletion, credential use, or policy change. Confirm the rollback path before execution.

</execute>

<evaluate>

Compare observed versus expected result. Decide `supported`, `partially_supported`, `unsupported`, or `blocked`. Check scope: passing one test cannot prove the full suite; a successful write cannot prove link integrity. State residual risk and evidence age.

</evaluate>

<retry_policy>

`max_attempts: 2`. Retry only after diagnosing the failure and changing input, tool, scope, or strategy. Stop on repeated signature or `NO_PROGRESS`; never rerun an unchanged check to manufacture confidence.

</retry_policy>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus claim, risk, check specification, expected/observed results, approval receipt, and rollback readiness. Append verification events so evidence age remains visible.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: the claim or expected result is ambiguous; ask one discriminating probe.
- `INSUFFICIENT_EVIDENCE`: no direct check supports the requested scope; narrow or withhold the claim.
- `BLOCKED_PERMISSION`: approval or access is absent; do not perform the action.
- `VERIFY_FAILED`: observed evidence contradicts the claim; report failure and recovery.
- `NO_PROGRESS`: the same verification signature fails twice; stop and escalate.
- `BUDGET_STOP`: verification budget is exhausted; preserve evidence and do not claim completion. `max_attempts: 2`.

## Output Contract

Return `status`, `result` (claim decision and allowed wording), `evidence` (fresh receipts), `unknowns` (including residual risk), and `next_action` (repair, approval, rollback, or stop).

## Edge Cases

- Tests passed before a final edit: evidence is stale; rerun the relevant checks after the edit.
- An authoritative page is unavailable: report `INSUFFICIENT_EVIDENCE`; do not substitute an uncited recollection for the external fact.

## Success Metrics

- Every material completion claim has a fresh, scope-matched receipt.
- Consequential actions have independent verification, approval, and rollback readiness.
- Failed checks change the claim or execution state immediately.

## Quality Gates

- [ ] Claim, expected result, and check scope match.
- [ ] Evidence was produced after the last material change.
- [ ] Partial checks lead to partial wording.
- [ ] Approval and rollback controls match risk.

</skill_contract>
