# Base Skill Template

Use this V7 template when creating or refactoring a skill. Keep the hot path below 350 `SKILL.md` lines; move detailed domain material and long examples into `references/`.

## Execution Profiles

| Profile | Use when | Required control |
|---|---|---|
| One-shot | One bounded transformation with a cheap check | Intake, execute, evaluate, receipt |
| Stateful | Work spans multiple calls or sessions | One-shot controls plus durable state |
| Loop | A verifier can drive bounded correction | Stateful controls plus retry, time, and cost caps |
| High-risk | Output affects security, money, production, external users, or trust | Independent evaluator plus explicit approval/rollback |

Do not hard-code model brands, prices, or context-window sizes. Select runtime capabilities such as `fast`, `reasoning`, `multimodal`, or `independent-evaluator` from the available harness.

## Copyable Template

````markdown
---
name: skill-name
description: Perform the core transformation and name its output. Use when the user asks for the specific task, artifact, or workflow this skill owns.
metadata:
  version: "7.0.0"
  updated: "YYYY-MM-DD"
  profile: "one-shot"
  assumes: "State the minimum condition required to execute safely."
  conflicts_with: "State the boundary or workflow this skill must not silently override."
---

# Skill Name

<skill_contract>
  <input>Required input or artifact.</input>
  <output>Durable result or concrete answer.</output>
  <done>Observable evidence that proves completion.</done>
  <non_goals>Adjacent work this skill must not absorb.</non_goals>

## Usage Template

```text
Use skill-name for this task.

Objective: [measurable outcome]
Scope: [owned files, systems, or topics]
Inputs: [paths, data, source, or prior state]
Constraints: [permissions, compatibility, quality ceiling]
Evidence: [test, lint, citation, render, metric, or review]
State path: [required for multi-call work; otherwise none]
Budget: [attempt, time, tool, token, or cost cap]
```

## Success Metrics

- The declared output exists and satisfies its acceptance check.
- Every completion claim cites fresh evidence.
- Assumptions, unresolved unknowns, and residual risk are explicit.
- Multi-call work can resume from the state artifact without replaying chat history.

## Workflow

<intake>
1. Read the objective, local instructions, prior state, and minimum required artifacts.
2. Confirm scope, authority, verifier, budget, and write-back target.
3. Classify material uncertainty with the unknowns gate.
4. Choose the lowest sufficient execution profile.
</intake>

<unknowns_gate>
- Known known: execute from verified local context.
- Known unknown: ask one focused question only when the answer changes architecture, authority, irreversibility, or acceptance criteria.
- Unknown known: inspect the environment, run a read-only probe, or build a disposable prototype.
- Unknown unknown: run a blind-spot pass for novel, unfamiliar, or high-risk work.
- Missing non-critical detail: make the conservative reversible assumption and record it.
- Insufficient critical information: stop with `NEEDS_INPUT`; never fabricate.
</unknowns_gate>

<execute>
1. Plan the smallest reversible action that can improve the acceptance metric.
2. Prefer deterministic scripts, parsers, and tools for mechanical work.
3. Act only inside the declared scope and permission boundary.
4. Record deviations from the plan in durable state.
</execute>

<evaluate>
1. Run the cheapest check that exercises the likely failure mode.
2. Check format, logic, evidence, scope, permissions, and state consistency.
3. Use an independent evaluator when the builder cannot objectively judge the result.
4. Route the result to `SUCCESS`, `RETRY`, or a controlled stop status.
</evaluate>

<retry_policy>
- Retry only when evaluation identifies a repairable defect.
- Change the hypothesis or action; do not replay the same failed attempt.
- Set a finite `max_attempts` and timeout before execution.
- Stop after the same failure appears twice or no metric improves.
- Preserve the last known-good artifact and rollback path.
</retry_policy>

<state_contract>
```yaml
schema_version: 1
objective: ""
status: intake | ready | executing | evaluating | retry | success | stopped
attempt: 0
budget_used: ""
assumptions: []
decisions: []
deviations: []
artifacts: []
evidence: []
open_unknowns: []
last_error: ""
next_action: ""
```

Update state after every attempt and before every return, compaction, handoff, or stop. Store artifact and evidence paths instead of lossy narrative summaries.
</state_contract>

## Failure Protocol

| Code | Emit when | Required response |
|---|---|---|
| `NEEDS_INPUT` | A user-owned decision blocks correct execution | Ask one precise question and preserve state |
| `INSUFFICIENT_EVIDENCE` | Available evidence cannot support the requested claim | State the evidence gap and safest next check |
| `BLOCKED_PERMISSION` | Required action exceeds authority | Name the denied action and approval boundary |
| `BLOCKED_DEPENDENCY` | A required file, tool, service, or environment is unavailable | Name the dependency and fallback |
| `VERIFY_FAILED` | Output exists but acceptance checks fail | Report failing evidence and bounded repair attempted |
| `NO_PROGRESS` | The same failure repeats or the metric does not improve | Stop retries, preserve evidence, change strategy or escalate |
| `BUDGET_STOP` | Attempt, time, tool, token, or cost cap is reached | Preserve state and distinguish stop from success |

Fallback order:

1. Retry one changed hypothesis inside the same scope.
2. Use a deterministic or lower-complexity method.
3. Produce a partial artifact clearly marked unverified.
4. Stop with a standard code and resumable state.

## Output Contract

<receipt>
```yaml
status: success | needs-input | blocked | verify-failed | no-progress | budget-stop
result: ""
evidence: []
unknowns: []
artifacts: []
attempts: 0
assumptions: []
residual_risks: []
state_path: ""
next_action: ""
```
</receipt>

Do not report success when the verifier failed, evidence is stale, or a cap stopped execution.

## Handoffs

Define an explicit handoff only when another skill owns the next transformation:

```yaml
handoff_to: skill-name
when: "Observable routing condition"
payload: [artifact paths, evidence, state path, open unknowns]
return_contract: "Expected result or receipt"
```

Never describe an automatic trigger unless a command, hook, workflow, or scheduler actually implements it.

## Edge Cases

- **Ambiguous irreversible choice:** for "Migrate production to the best schema," emit `NEEDS_INPUT` because “best” hides a user-owned decision; ask one discriminating question and do not mutate production.
- **Verification fails after plausible output:** record the failing integration test, change one hypothesis, and retry within the cap; on repetition emit `NO_PROGRESS` or `VERIFY_FAILED` and preserve the last known-good artifact.

## Quality Gates

- [ ] Description contains the complete trigger and avoids a duplicate `When to Use` section.
- [ ] Contract names input, output, done evidence, and non-goals.
- [ ] Unknowns gate distinguishes conservative assumptions from decisions that require a probe.
- [ ] Mechanical checks use deterministic tools outside model context when possible.
- [ ] Evaluation runs after output and before any success claim.
- [ ] Retry changes the hypothesis and has finite attempt, time, and cost limits.
- [ ] Multi-call work updates durable state before returning.
- [ ] Failure emits a standard code instead of fabricated completion.
- [ ] Handoffs name a real implementation and typed payload.
- [ ] High-risk work defines approval, rollback, audit, and independent review.
- [ ] One or two skill-specific edge cases cover the most expensive failure modes.
- [ ] Detailed teaching, histories, and large examples live in `references/`.

## Anti-Patterns

- Loading all available context because the model supports a large window.
- Encoding deterministic validation as repeated natural-language reminders.
- Hard-coding a model brand where a capability class is sufficient.
- Asking broad clarification questions for reversible low-risk details.
- Letting the builder be the only evaluator for subjective or high-risk output.
- Keeping state only in conversation.
- Retrying without new evidence or a changed hypothesis.
- Treating a partial result, timeout, or budget stop as success.

</skill_contract>
````

## Refactor Rule

Preserve domain-specific procedures and verified safety boundaries. Remove duplicated trigger prose, generic explanations, model-version assumptions, fake automation, and examples that do not cover a real failure mode. A shorter skill is better only when it preserves input, authority, state, evaluation, recovery, and proof.
