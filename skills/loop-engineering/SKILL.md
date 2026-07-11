---
name: loop-engineering
description: Turn a repeatable task into a bounded, evidence-driven agent loop. Use when Codex needs to decide whether a task merits a Goal, Loop, Automation, AutoResearch, or LLMLOOP-style code repair pattern; define a loop contract; check trigger/state/tools/codebase readiness; choose single-agent versus maker-checker versus manager-workers topology; calibrate verifier tiers; prevent runaway iteration, orchestration tax, quiet-success drift, or repair a loop that stalls, self-grades, exceeds review budget, or writes without verified evidence.
metadata:
  version: "6.4"
  updated: "2026-07-02"
  assumes: "The proposed task has a reachable local state, an inspectable output, and a feasible evidence source."
  conflicts_with: "Do not bypass explicit approval, sandbox, permission, or production controls imposed by harness-engineering, agentic-engineering, or agent-teams-command."
---

# Loop Engineering

Design a loop with a control-system frame, not as a repeated prompt. This is an operating analogy for measurement, bounded action, verification, and state; it is not a safety proof. Its only valid form is:

```text
goal + state + tools + budget
            |
            v
plan -> act -> observe -> independently verify -> decide
  ^                                               |
  |---------------- continue / stop / escalate ---|
```

V6 shorthand: every loop must state `Trigger -> Execute -> Verify -> State`. If any field is vague, do a one-shot task or write a review item instead of starting a loop.

Use `scripts/validate_loop_contract.py` before starting a loop. Do not bypass a failed contract.

For a concrete pattern, see `references/ci-repair-loop-example.md`.

## Usage Template

```text
Use loop-engineering for this task.

Mode: [goal | interval loop | automation | autoresearch]
Trigger: [manual | cron | webhook | CI | issue | other]
Objective: [measurable outcome]
Scope: [owned files, systems, or outputs]
Evidence: [test, metric, fixture, review, or inspection]
Limits: [iterations, time, tool/token/request budget]
Permission boundary: [allowed writes and approval gates]
```

## Success Metrics

- A valid contract names the metric, independent verifier, finite caps, recovery path, and durable write-back.
- The selected topology is the lowest-complexity topology that can produce independent evidence.
- The final receipt distinguishes verified success, budget stop, stall, and blocked state.
- Scheduled knowledge loops distinguish unattended objective scans from supervised semantic writes.
- The loop mode, trigger, artifact path, work clock, and review budget are explicit before any repeated execution starts.
- Code loops choose the cheapest sufficient verification ladder and sandbox generated or untrusted tests before execution.
- Loop contracts cap review load and include an understanding checkpoint when quiet success could outpace human ownership.

## 1. Choose The Execution Mode

Do not call every repeated task a loop. Pick the narrowest mode:

| Mode | Use when | Verification |
|---|---|---|
| Goal | A bounded task should run until a concrete state is reached. | Test, grader, diff, or artifact acceptance. |
| Loop | A timeboxed exploration needs periodic observe/steer cycles. | Human steering plus evidence snapshots. |
| Automation | A schedule, webhook, or external event should trigger a routine. | Logs, receipts, metrics, and anomaly alerts. |
| AutoResearch | The agent can run many experiments against a cheap objective metric. | Metric leaderboard, sandbox, and reproducible trials. |

Reject wide-open loops for taste, product strategy, vague quality, or irreversible external action. Convert them into a one-shot draft, review queue, or supervised goal.

## 2. Admit Or Reject The Loop

Use a loop only when the work is repeatable, the output can be checked, and each iteration can leave inspectable evidence.

| Situation | Default |
|---|---|
| One reversible edit or answer | Do the task once; do not create a loop. |
| Objective metric and cheap verification | Use a single-agent loop. |
| Builder cannot objectively verify its own output | Use maker-checker. |
| Independent workstreams with explicit file/output ownership | Use manager-workers with an integration gate. |
| Taste-only, ambiguous, irreversible, or production-changing task | Keep a human approval gate; do not run unattended. |

Reject a loop when its only stopping rule is “until satisfied,” “keep improving,” or “run forever.” Convert those requests into a metric, an acceptance fixture, a review queue, or a one-shot draft.

Reject or narrow the seed prompt if it is vague. A loop does not guess wrong once; it can compound the same bad assumption every iteration. Before admission, write the spec, verifier, and stop condition in inspectable language.

## 2A. Use The Workflow Adoption Ladder

Promote recurring work in this order:

```text
manual run -> skill -> automation -> loop
```

Do the task manually first to prove the agent can produce the desired output. Turn the repeatable procedure into a skill. Automate the skill only when the trigger and receipt are clear. Add a loop only when success criteria and state logging exist. Skipping directly to a loop usually hides fuzzy goals, missing state, or unsafe cadence.

## 3. Check The Loop Harness

A runnable loop needs five building blocks plus memory:

| Building block | Required check |
|---|---|
| Trigger | Manual start, cron, webhook, PR/CI event, queue threshold, or another agent. |
| Worktree / isolation | Independent branch, folder, sandbox, DB branch, or explicit shared-state lock. |
| Skills / rules | Only the task-local procedures needed for this loop. |
| Tools / connectors | Narrow tool contracts, permissions, failure path, and receipts. |
| Subagent / verifier | Separate maker/checker when the builder cannot objectively verify. |
| Memory | Artifact path, loop contract, state ledger, and global work clock/log. |

For code loops, verify the codebase is:
- Legible: `AGENTS.md`, lints, or architecture rules expose forbidden paths and conventions.
- Executable: the agent can run the smallest local command without hidden manual setup.
- Verifiable: tests, E2E, screenshots, static checks, or review tools can catch failure.

If any readiness check fails, first create a one-shot setup task; do not run an autonomous loop.

## 4. Create The Loop Contract

Create `.agent-state/loop-contract.md` or an equivalent durable state file before the first action. Use this exact shape:

```markdown
# Loop Contract

- Objective: Reduce the selected test suite's failures to zero.
- Mode: Goal.
- Trigger: Manual start from failing CI evidence.
- Scope: `packages/payments/**` and its tests only.
- Non-goals: No API redesign, dependency upgrades, or production deployment.
- Owner: Primary agent; checker owns verification only.
- Inputs: Failing test output and repository guidance files.
- Artifacts path: `.agent-state/payments-artifacts/`.
- State path: `.agent-state/payments-loop.md`.
- Work clock: Read and update `.agent-state/work-clock.md` before and after each iteration.
- Success metric: Selected test command exits 0 with no skipped failures.
- Evidence: `pnpm test --filter payments` output and changed-file diff.
- Verifier: Independent test command plus a checker agent or reviewer.
- Topology: maker-checker.
- Max iterations: 5.
- Time limit: 45 minutes.
- Budget: 20 tool calls; stop before context or cost cap.
- Review budget: Stop if the diff exceeds 1000 changed lines, 10 files, or the human review cap.
- Understanding checkpoint: Stop if the human/lead cannot explain the architecture delta, invariants, and rollback plan.
- Context policy: Compact state after every iteration; prune stale context when the tool, model, code, or bug changes.
- Stop condition: Success metric passes, or any cap/stall condition fires.
- Write-back: Update `.agent-state/payments-loop.md` and the task log.
- Permission boundary: Local branch writes only; no push, merge, or production action.
- Recovery: Revert the last iteration if tests regress; escalate with evidence after two repeated failures.
```

For scheduled knowledge-management loops, add:

```markdown
- Trigger: Cron, automation, webhook, or daily note refresh.
- Execute: Objective scans, queue generation, dashboard refresh, or one supervised KR.
- Verify: Script receipt, lint report, link check, diff, or review receipt.
- State: Daily note, governance dashboard, backlog, log, or skill/SOP candidate.
- Automation boundary: No source-body mutation, concept merge/delete/rename, provenance invention, or semantic rule promotion without review.
```

Run:

```powershell
python scripts/validate_loop_contract.py .agent-state/loop-contract.md --strict
```

Treat a budget cap or stall condition as a controlled stop, not success.

## 5. Calibrate The Verification Tier

Choose the cheapest verifier that still exercises the failure mode the loop could create. An LLM checker may interpret evidence, but for code, infrastructure, external systems, or durable wiki changes it cannot replace deterministic evidence.

Treat the Model-in-the-Loop / Software-in-the-Loop / Hardware-in-the-Loop vocabulary below as a verifier-fidelity analogy borrowed from embedded-system validation. It does not certify agent-loop safety.

| Loop risk | Minimum verifier |
|---|---|
| Draft, plan, rubric, or contract work | Fixture, checklist, schema, or reviewer inspection. |
| Local code or document transformation | Real local command, parser, linter, render, diff, or targeted test. |
| Concurrent repository writes | Isolated branch/worktree plus integration diff and tests. |
| External connector, scheduled, staging, or production-like loop | Explicit approval, rollback path, audit log, and telemetry or dry-run evidence. |

If no telemetry can reveal whether the loop helped, reject the loop or convert it into a one-shot draft with human review.

Use the five-tier verifier ladder for fuzzy loops:

| Tier | Use when | Boundary |
|---|---|---|
| 1 Deterministic | Compile, tests, lints, parsers, schema checks. | Preferred for unattended loops. |
| 2 Rule/constraint | Runtime, length, file count, budget, coverage, complexity. | Define threshold before launch. |
| 3 External metric | Clicks, likes, revenue, latency, issue count. | Watch for proxy-metric gaming. |
| 4 Independent AI judge | Subjective review needs scale. | The builder cannot judge itself. |
| 5 Human-in-loop | Taste, strategy, ambiguity, high stakes. | Supervised loop only. |

For code-repair loops, use an LLMLOOP-style cascade when the toolchain exists:

```text
compile/package -> given tests -> static analysis -> generated tests -> mutation or fault-injection test
```

Run the earliest failing verifier first; do not pay for later loops until earlier physical preconditions pass. Execute generated tests, fuzzers, mutation tests, and untrusted code inside Docker, a sandbox, or an isolated worktree with hard timeouts. If the same failure repeats twice, change the hypothesis, topology, prompt, or search diversity; do not keep replaying the same deterministic retry.

## 6. Run The Thin Loop

For each iteration:

1. Read only the contract, current state, last evidence, and minimum task context.
2. Plan one smallest reversible action that can affect the metric.
3. Act inside the contract's file, tool, and permission boundary.
4. Observe tool output, diffs, logs, tests, screenshots, or telemetry.
5. Have the declared verifier evaluate the evidence. The builder cannot be the sole verifier.
6. Record metric delta, changed files, evidence path, budget used, and next decision in state.
7. Stop, continue, or escalate according to the contract.

Keep context lean. Persist state and evidence in files rather than replaying a long chat transcript.

For long-lived loops, use "dreaming" only as a compaction step: summarize repeated failures, decisions, and durable lessons into the state file, project `AGENTS.md`, or a related skill. Treat old synthetic memory as having a half-life; remove stale context after the underlying tool, model, code, or bug has changed.

## 7. Select Topology Conservatively

| Topology | Use when | Required controls |
|---|---|---|
| Single-agent | One owner and an objective check exist. | External test/linter/fixture; finite budget. |
| Maker-checker | Generation and evaluation need separate judgment. | Checker has a separate prompt or tool evidence and cannot edit before reporting. |
| Manager-workers | Work decomposes into independent territories. | Per-worker ownership, branch/worktree isolation for concurrent repo writes, integration order, shared-state rule, and final evaluator. |

Do not use manager-workers merely to make a task feel more autonomous. Escalate to `agent-teams-command` when real multi-agent ownership, IPC, or integration work is required. Escalate to `harness-engineering` when permissions, credentials, scheduling, or production observability are the primary problem.

## 8. Stop, Recover, Or Escalate

Stop successfully only when the declared verifier accepts the declared evidence. Stop without success when a hard cap fires.

| Signal | Action |
|---|---|
| Success metric passes | Record proof, write back learning, stop. |
| Same failure twice | Stop editing that hypothesis; choose a different diagnosis or escalate. |
| No measurable progress for three iterations | Stop and request a human decision or redefine the metric. |
| Time, tool, token, or request cap reached | Preserve evidence and state; report budget stop. |
| Regression, permission denial, or shared-state conflict | Revert or isolate the last action; escalate with the receipt. |
| Change volume outpaces human comprehension | Stop for review, shrink scope, or add an architecture summary before continuing. |
| Diff exceeds review budget or approaches 1000 changed lines | Split the loop into smaller goals or stop for human review. |
| Review queue grows faster than human review | Lower parallelism, batch by risk, or stop new loop launches. |
| Loop succeeds but humans stop understanding it | Stop for architecture review; require summary, invariants, demo, and rollback evidence. |
| Need to push, merge, deploy, publish, pay, message, or mutate shared production state | Stop for explicit approval. |
| Scheduled loop wants to rewrite meaning from signal heat alone | Write a candidate to review queue; do not promote. |

## 9. Close The Memory Loop

At termination, write one compact receipt:

```markdown
Result: success | budget-stop | stalled | blocked
Metric: before -> after
Evidence: command, output path, screenshot, or diff
Iterations: N / cap
Changes: files or external actions
Residual risk: what remains unverified
Next action: only if not successful
```

Promote reusable constraints to a project `AGENTS.md`, SOP, or related skill. Do not promote an unverified heuristic as a rule.

When promoting memory, include an expiry condition. Examples: "remove after the CI bug is fixed," "review after model upgrade," or "delete if the command no longer fails." Stale loop memory is hidden token debt.

For compounding loops, write signals to shared artifacts only when each artifact has its own README/contract and timeline. A downstream loop may consume those signals, but it must cite the artifact evidence and keep its own budget and stop condition.

## Quality Gates

- [ ] Contract passes `validate_loop_contract.py --strict` before execution.
- [ ] Mode is Goal, Loop, Automation, or AutoResearch; the trigger is concrete.
- [ ] Trigger, isolation, skills/rules, tools/connectors, verifier, and memory path are defined.
- [ ] Codebase readiness is checked for legible, executable, and verifiable conditions when code is touched.
- [ ] Success metric and stop condition are separately stated.
- [ ] Verifier is independent from the builder or backed by external evidence.
- [ ] Verifier tier is calibrated; unattended loops use deterministic, rule, or telemetry evidence.
- [ ] Code loops run the cheapest useful verifier cascade and sandbox generated or untrusted tests.
- [ ] Iteration, time, and tool/token/request budgets are finite.
- [ ] Review budget is finite and diff growth is capped before human comprehension fails.
- [ ] Seed prompt/spec is precise enough that repeated execution will not compound one bad assumption.
- [ ] Quiet-success risk has an understanding checkpoint for long-running or high-volume loops.
- [ ] State, evidence, and write-back paths are durable and explicit.
- [ ] Production or external mutations have approval, rollback, and audit boundaries.
- [ ] Multi-agent use has independent ownership and an integration gate.
- [ ] Long-lived memory has a pruning or half-life policy.
- [ ] Completion claim cites fresh verifier evidence; budget stop never masquerades as success.
- [ ] V6 loop form states Trigger, Execute, Verify, and State, with unattended vs supervised actions separated.

## Anti-Patterns

- Letting the builder score itself and treating that score as proof.
- Treating maker-checker agreement as proof when no deterministic evidence was run.
- Adding more agents before the task, metric, or ownership is clear.
- Treating “no errors observed” as success without a declared check.
- Carrying state only in chat memory.
- Running a scheduled or production loop without caps, rollback, and anomaly escalation.
- Repeating the same failed hypothesis without changing evidence or diagnosis.
- Running expensive generated-test, fuzz, or mutation loops before compile and base tests pass.
- Treating engagement, AI judgment, or taste as objective proof without proxy-risk review.
- Using one wide-open while-loop for layered work that needs orchestrator, planner, researcher, coder, validator, and memory roles.
- Letting quiet success accumulate large unreviewed changes that humans no longer understand.
- Treating the loop itself as the compound asset; skills, evals, and state artifacts compound, while the loop is plumbing.
