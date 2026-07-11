---
name: agentic-engineering
description: Design or refactor agent skills, workflows, operating loops, Agentic OS upgrades, and V6 knowledge-OS upgrades for model-native Agentic Engineering. Use when making skills more autonomous, concise, verifiable, long-horizon capable, token-efficient, lower-friction for human-LLM collaboration, ready to move from manual workflow to skill/automation/loop, preserve human taste through custom evals, manage 1000x-engineer leverage claims, or promote Obsidian wiki learning into reusable agent behavior.
version: "6.2"
updated: "2026-07-02"
assumes: "The workflow can be expressed as a bounded agent loop with observable verification evidence."
conflicts_with: "Do not override harness-engineering safety boundaries or verify-before-claim evidence requirements."
---

# Agentic Engineering

Refactor a skill or workflow so the model can execute more work with less human steering, while preserving verification, provenance, security, and the professional quality ceiling.

Agentic Engineering is the step after vibe coding: speed is useful only if quality does not degrade. Humans keep ownership of taste, judgment, architecture, and risk boundaries; agents execute bounded macro actions with evidence.

## Agent Understanding Model

Use the Karpathy-style LLM OS mapping as the design baseline:

| OS concept | Agent workflow meaning |
|---|---|
| LLM = CPU | The model runs the next reasoning/action loop. |
| Context = RAM | Load only the state needed for the next step. |
| Wiki/logs = Disk | Durable knowledge lives outside chat memory. |
| Tools = System calls | Actions must have contracts, permissions, and evidence. |
| Loop = Scheduler | Plan -> Act -> Observe -> Iterate controls work. |

The agent is a process with state, tools, permissions, and write-back duties. Do not design skills as advice pages; design them as executable control loops.

## Full-Stack Agent Pattern

Use the Google I/O '26 wiki update as the new maturity signal: useful agents are moving from chat boxes into full-stack product surfaces.

| Surface | Agentic engineering requirement |
|---|---|
| Developer IDE or CLI | subagents, hooks, async queues, tests, diffs, task state |
| Personal agent | user intent, memory boundary, tool allowlist, resumable tasks |
| Agentic search | source grounding, comparison criteria, reversible action preview |
| Agentic commerce | explicit mandate, budget, payment boundary, audit trail |
| Generative media | provenance, edit history, watermark or disclosure path |
| Ambient device | sensor boundary, privacy mode, interrupt and fallback controls |

Do not treat these as separate prompt styles. They are one full-stack agent design problem: model -> context -> tool calls -> product surface -> verification -> governance.

## Workflow Complexity Gate

Before adding orchestration, classify the work at the lowest sufficient level:

| Level | Use when | Gate before upgrading |
|---|---|---|
| Prompt | One-off answer, small edit, short analysis | Is the work repeating? |
| Skill | Reusable workflow or domain method | Does it need isolated execution? |
| Subagent | Independent side task or context isolation | Does it need communication or shared state? |
| Agent team | Multiple roles must coordinate or review each other | Can file ownership, IPC, and join gates be defined? |
| Long-running goal | Depth problem: iterate until objective criteria pass | Is `done` externally verifiable and budgeted? |
| Dynamic workflow | Width problem: many independent shards can run in parallel | Is script review, cost envelope, and runtime observability in place? |

Default to the lower level when value, independence, or verification is unclear. Higher orchestration increases token cost, permission surface, and audit burden.

## Agentic OS Adoption Gate

Use this gate when turning an ad hoc workflow into a durable operating surface:

| Stage | Promotion check | Output |
|---|---|---|
| Manual run | Has the agent completed the workflow once with hands-on steering? | Example transcript, artifact, and failure notes. |
| Skill | Is the procedure repeatable with a specific input, output, and verifier? | Compact `SKILL.md` or SOP. |
| Automation | Is the trigger, context, receipt, and rollback path clear? | Routine, cron, webhook, or button with audit log. |
| Loop | Is there success criteria, state logging, budget, and stop condition? | Loop contract plus verifier evidence. |

Check the Agentic OS four C's before packaging a workflow for repeated or team use: Context, Connections, Capabilities, and Cadence. Do not build a dashboard, button, or routine before Levels 1-2 are real: codified capabilities plus durable state. UI distribution raises the floor only when it wraps a verified workflow rather than hiding an untested prompt.

## Taste And Custom Eval Gate

When quality depends on product taste, user trust, domain nuance, or "AI slop" avoidance, do not rely on public benchmarks or the builder's self-rating. Capture representative traces, label a few good/bad examples, define the rubric, and route outputs through deterministic checks plus an independent grader or human reviewer. Cross-model graders are useful only when disagreements become eval cases, not when they replace human taste.

Treat 1000x-engineer language as an ambition and leverage pattern, not a benchmark. The reusable procedure is: turn successful traces into skills, route work through resolvers/tools, run evals, cap review load, and keep humans responsible for architecture, taste, and risk.

## V6 Knowledge-OS Upgrade Gate

When updating skills from Obsidian wiki knowledge, classify the rule before editing:

| Rule type | Default destination | Promotion bar |
|---|---|---|
| Source-specific claim | concept/entity/source page | block ref and single-source warning |
| Reusable human/agent procedure | existing skill or SOP | Trigger -> Execute -> Verify -> State |
| Runtime safety boundary | harness or schema | approval, rollback, receipt, objective check |
| Repeated system debt | lint report or governance dashboard | countable metric and queue owner |
| Taste, strategy, or uncertain judgment | review queue | human decision before promotion |

Do not turn a vivid interview, demo, or single wiki page into a universal rule. V6 promotes only rules with repeated durable support or a local verification result.

## Usage Template

**Prompt**
```text
Use agentic-engineering to revise this skill/workflow. Make it model-native, concise, autonomous, verifiable, and long-horizon capable.
```

**Use Case**
- Improving an existing skill, SOP, command, agent workflow, or multi-agent plan.

**Expected Result**
- A compact agentic workflow with clear defaults, state checkpoints, verification gates, and escalation rules.

**Output Example**
- A revised `SKILL.md` with model assumptions, autonomous execution loop, quality gates, and anti-patterns.

**Verification Case**
- A fresh agent can run the workflow without repeated clarification and can prove completion with evidence.

**Verified Effect**
- Human coordination load drops; the LLM spends fewer tokens asking for obvious decisions and more tokens executing, checking, and learning.

## Success Metrics

- Revised workflow has one trigger, one bounded macro action, one state checkpoint, one verification gate, and one write-back target.
- The skill or workflow can be executed without extra clarification for its primary use case.
- Residual human judgment points are explicit rather than hidden in vague prose.
- Obsidian-derived rules pass the V6 promotion gate before entering skills, SOPs, schema, or automation.
- Repeated workflows are promoted through manual run -> skill -> automation -> loop, with Context, Connections, Capabilities, and Cadence checked before OS-level packaging.
- Human taste is translated into project-specific traces, rubrics, fixtures, or custom evals before broad autonomous execution.

## Model Meta-Properties

Design around the model as it is, not as a human assistant metaphor.

| Meta-property | Skill design response |
|---|---|
| Context is scarce working memory | Keep `SKILL.md` short; move examples/details to references; load only what is needed. |
| Output is probabilistic | Require tests, citations, diffs, screenshots, or link checks before claims. |
| Tool use is the action layer | Name allowed tools, denied actions, and idempotent retries. |
| Long-horizon drift is normal | Add checkpoints, state files, stop criteria, and recovery paths. |
| Durable knowledge is external | Persist reusable results into wiki, docs, logs, or state files. |
| The model is strong at synthesis | Do not over-explain generic concepts; specify local constraints and unusual rules. |
| The model can over-ask | Provide safe defaults and ask only for irreversible, high-risk, or genuinely ambiguous decisions. |
| Cost and latency matter | Route simple work to thin loops; reserve deep context for high-uncertainty decisions. |
| Models absorb scaffolding over time | Keep skills small, delete deadweight rules, and prefer intent plus verifier over brittle workaround prompts. |

## Workflow

### 1. Define the Quality Ceiling

Name the standard that must not drop:

```text
Quality ceiling:
User-visible risk:
Security risk:
Verification evidence:
Human judgment required:
```

If quality cannot be measured or inspected, do not delegate broad autonomous work yet.

### 2. Compress the Contract

State the workflow in one sentence:

```text
Input -> transformation -> durable output -> verification evidence
```

If this sentence is vague, fix it before adding steps.

### 3. Write the Macro Action Spec

Before assigning a large unit of work, define:

```text
Objective:
Scope:
Non-goals:
Inputs:
Owned files or territory:
Expected output:
Verification evidence:
Security/risk review:
Write-back destination:
Stop condition:
```

Treat features, research, plans, and verification as macro actions. Shrink the action until ownership and proof are clear.

For delegated actions that can affect a user, account, purchase, external system, public claim, or generated media artifact, add:

```text
User mandate:
Authority boundary:
Budget/cost limit:
Reversibility:
Audit/provenance record:
User confirmation point:
```

### 4. Set Autonomy Defaults

Use this escalation policy:

| Situation | Default |
|---|---|
| Reversible local edit | Proceed, then verify. |
| Missing low-risk detail | Make a conservative assumption and record it. |
| Conflicting existing files | Preserve user changes and adapt. |
| Destructive, irreversible, credential, payment, legal, or production action | Stop and ask. |
| User explicitly requested a choice | Ask once, briefly. |

### 5. Externalize State

For long tasks, create or update one durable state artifact:

```markdown
Goal:
Current step:
Assumptions:
Files touched:
Evidence:
Open risks:
Next action:
```

Avoid relying on chat memory for multi-hour or multi-session continuity.

### 6. Use the Thin Loop

```text
Boot minimal context.
Plan the next smallest useful step.
Act with tools as system calls.
Observe environmental evidence.
Update durable state.
Verify or iterate.
Write back reusable learning.
Stop when definition of done is proven.
```

Keep the loop short. Do not produce broad plans unless the task is broad.

### 7. Add an Evaluator or Red Team When Risk Is High

Use a separate critic, test suite, or adversarial pass when output touches:

- authentication, permissions, secrets, payment, legal, or data deletion
- public-facing claims, launch materials, or user trust
- architecture that is hard to reverse
- generated code without strong tests

For security-sensitive work, the minimum pattern is:

```text
Builder output -> evaluator review -> adversarial test -> fix loop -> final proof
```

### 8. Use AutoResearch Only Inside Evaluation Boundaries

Allow long autonomous experimentation only when:

- the metric is objective
- evaluation is cheap and repeatable
- safety, cost, and runtime limits are explicit

Otherwise keep the loop supervised with human review gates.

### 9. Convert Human Collaboration into Interfaces

Replace repeated human check-ins with artifacts:

| Human need | Agentic interface |
|---|---|
| "What are you doing?" | Task state + changed files + next action |
| "Is it done?" | Verification command/output + residual risk |
| "Why this choice?" | Assumption ledger + tradeoff table |
| "Can this be reused?" | SOP, skill update, or wiki output |

### 10. Verify Before Claiming

Every completion claim needs fresh evidence:

- files exist or diffs show expected edits
- tests, lint, link checks, or schema checks pass
- source references resolve
- known residual risks are named

For vendor-keynote, launch, or product-roadmap claims, mark single-source status until checked against public docs, changelogs, or independent usage evidence.

### 11. Shrink the Scaffolding

Before adding a rule, ask what model failure it prevents and how to verify it still matters. If a rule only patches an old model weakness, move it to a reference, lint warning, or review queue rather than the hot path.

Prefer:
- problem definition over prompt ceremony
- task-local retrieval over context stuffing
- procedure skills over broad ability claims
- hooks, lints, and tests outside context when the check is deterministic
- half-life review for stale project instructions, skills, and system cards

### 12. Close the Memory Loop

After significant output, decide where the result belongs:

| Output | Durable home |
|---|---|
| Source-derived claim | `sources/` reference + `wiki/` synthesis |
| Reusable workflow | skill, SOP, or command file |
| Project decision | `wiki/decisions/` or project log |
| Correction | related wiki page + change log |
| Open risk | review queue or issue tracker |

## Quality Gates

- [ ] Trigger description says exactly when to use the skill.
- [ ] `SKILL.md` removes generic teaching and keeps only non-obvious procedure.
- [ ] Workflow has safe defaults and a narrow ask-user policy.
- [ ] Macro actions have scope, owner, non-goals, proof, and stop condition.
- [ ] Delegated external actions define mandate, authority, cost, reversibility, and audit record.
- [ ] Long-horizon tasks have checkpoints or state artifacts.
- [ ] Workflow complexity is justified at the lowest sufficient level.
- [ ] Repeated workflows passed the manual -> skill -> automation -> loop adoption gate before OS-level packaging.
- [ ] Agentic OS packaging states Context, Connections, Capabilities, and Cadence.
- [ ] Taste-sensitive work has project-specific traces, rubric, custom evals, or human review.
- [ ] 1000x-style leverage claims are treated as unverified unless backed by local metrics and review receipts.
- [ ] Quality gates include executable or inspectable evidence.
- [ ] High-risk work has evaluator, critic, or adversarial review.
- [ ] AutoResearch loops have objective metrics, cheap evals, and explicit limits.
- [ ] Significant outputs have a write-back destination.
- [ ] Anti-patterns name the most likely model failure modes.
- [ ] Output format is concrete enough for another agent to follow.
- [ ] V6 promotion gate checked for Obsidian-derived skill, SOP, schema, or automation changes.

## Anti-patterns

- Asking the user to decide routine reversible details.
- Writing long philosophy where a table or checklist would guide better.
- Claiming completion from confidence instead of verification.
- Keeping state only in conversation.
- Treating tools as magic actions instead of permissioned system calls.
- Optimizing for one impressive answer instead of a reusable loop.
- Delegating a large macro action without non-goals, ownership, proof, or a stop condition.
- Letting an agent buy, publish, message, schedule, or mutate external state without an explicit mandate and audit trail.
- Running autonomous iteration where success depends on taste or risk judgment rather than a cheap metric.
- Letting "boil the ocean" ambition bypass scope, evals, review bandwidth, or ownership checkpoints.
