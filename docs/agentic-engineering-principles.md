# Agentic Engineering Principles

This standard translates the Obsidian note `wiki/concepts/Agentic Engineering`
into operating rules for Third Brain V7 Skills.

## Doctrine

Agentic Engineering is not faster prompting. It is the discipline of coordinating
fallible but powerful AI agents so delivery speed rises while the quality ceiling
does not fall.

Use this distinction:

| Mode | Optimizes for | Failure mode |
|---|---|---|
| Vibe coding | Accessibility and speed | Fast output without durable quality gates |
| Agentic engineering | Speed plus professional quality | Over-orchestration if specs and evals are weak |

## Five Practices

1. **Spec-driven development**: convert intent into a concrete spec before broad execution.
2. **Verification-first work**: define proof before claiming success.
3. **Macro action orchestration**: delegate features, research, plans, and verification as bounded agent jobs.
4. **Security-aware integration**: red-team high-risk outputs before release.
5. **Closed-loop optimization**: use cheap objective metrics when the task can be evaluated repeatedly.

## Workflow Complexity Ladder

Start at the lowest sufficient runtime:

| Runtime | Use for | Upgrade only when |
|---|---|---|
| Prompt | One-off answer, small edit, short analysis | The workflow repeats or needs reuse |
| Skill | Repeatable recipe or domain method | It needs isolated execution |
| Subagent | Side task with isolated context | It needs peer communication or shared state |
| Agent team | Coordinated roles, review, dependencies | Ownership, IPC, and join gates are clear |
| Long-running goal | Depth: iterate until objective criteria pass | Completion criteria and budget are explicit |
| Dynamic workflow | Width: many independent shards in parallel | Script review, cost envelope, and observability exist |

Higher orchestration is not automatically better. It raises token cost, permission
surface, and audit burden. Dynamic workflows are a width tool; long-running goals
are a depth tool; agent teams are a communication tool.

## Full-Stack Agent Surfaces

The Google I/O '26 wiki update expands the operating standard: agents are no
longer only coding helpers. They are entering IDEs, personal assistants, search,
commerce, generative media, and ambient devices. A skill should therefore treat
agent execution as a full-stack system:

```text
model -> context -> tools -> product surface -> verification -> governance
```

Use this surface checklist when designing or revising agent workflows:

| Surface | Required control |
|---|---|
| Developer IDE/CLI | tests, diffs, subagent ownership, task queue, hooks |
| Personal agent | user mandate, memory scope, resumable log |
| Agentic search | source provenance, comparison criteria, action preview |
| Agentic commerce | budget, payment boundary, receipt, rollback path |
| Generative media | prompt/edit history, watermark or disclosure path |
| Ambient device | sensor consent, privacy mode, fallback and interrupt controls |

If the workflow can act through a user's account, change external state, spend
money, publish content, or use sensors, it needs an explicit mandate and audit
trail before execution.

## AIOS Runtime Audit

When a workflow becomes a personal or team operating system, audit four layers:

| Layer | Required check |
|---|---|
| Context | Files, memory, wiki, logs, and prior outputs are current and scoped. |
| Connections | Each app/API account has read/write/send/delete boundaries. |
| Capabilities | Skills, commands, and SOPs have triggers, outputs, and proof gates. |
| Cadence | Scheduled or event-triggered routines have alerts, receipts, and rollback. |

Use the permission Bike Method before adding real-world capabilities: observe,
co-drive, scoped action, supervised autonomy, then autonomy. Text instructions
do not replace endpoint, credential, budget, and approval boundaries.

## Macro Action Contract

Use this contract before assigning an agent or skill a large unit of work:

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

If any field is missing, shrink the macro action until it can be verified.

## Quality Ceiling Gates

Every agentic workflow should answer:

- What professional standard must not drop?
- What evidence proves the standard was met?
- Which failures require a critic, evaluator, or adversarial agent?
- Which outputs need human judgment for taste, architecture, or risk?
- Where is reusable learning written back?

## AutoResearch Boundary

Use autonomous iteration only when all three are true:

- The task has an objective metric.
- The metric is cheap enough to run many times.
- The search space is bounded by safety, cost, and time limits.

When any condition is false, use a supervised loop with explicit review gates.

## Single-Source Product Claims

Launch demos and keynotes can inspire skill updates, but do not convert them into
guarantees. Mark product availability, scale metrics, benchmark numbers, protocol
status, and security claims as `single-source` until independently verified.

## Skill Mapping

| Skill | Agentic role |
|---|---|
| `agentic-engineering` | Convert workflows into specs, macro actions, loops, and gates. |
| `harness-engineering` | Provide runtime permissions, observability, security, and recovery. |
| `agent-teams-command` | Coordinate parallel agents with ownership, IPC, joins, and cleanup. |
| `verify-before-claim` | Enforce proof before completion claims. |
| `session-learn` | Capture reusable learning after each loop. |
