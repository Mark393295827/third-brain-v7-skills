# Ender-Palantir-Von Neumann Command Patterns

Use this reference when a multi-agent project needs durable state, messy workflow discovery, long-running coordination, feedback-driven improvement, or a structured command architecture.

## Source Boundary

This pattern is promoted from durable Obsidian pages, not from a single clipping:

- `wiki/concepts/Claude Code Agent Teams 操作指南.md`
- `wiki/outputs/enders-game-commander-training-framework.md`
- `sources/2026-05-09-enders-game-trilogy.md`
- `sources/2026-04-11-the-man-from-the-future.md`
- `wiki/entities/约翰·冯·诺依曼.md`
- `wiki/concepts/冯·诺依曼体系结构.md`
- `wiki/concepts/自复制自动机.md`
- `wiki/concepts/元胞自动机.md`
- `wiki/entities/Palantir.md`
- `wiki/concepts/数据本体论 Data Ontology.md`
- `wiki/concepts/智能体前线部署工程师.md`
- `wiki/concepts/智能体协调器 Agentic Orchestrator.md`
- `wiki/concepts/评估驱动开发.md`
- `wiki/concepts/Loop编程.md`
- `wiki/concepts/编排税.md`
- `wiki/concepts/默然成功风险.md`

Do not promote source-specific military, investment, or vendor claims into a project rule unless independently verified.

## Structured Framework

Use the three lenses together:

| Lens | Question | Output |
|---|---|---|
| Ender | What does the commander need to understand before acting? | Intent, squad autonomy, asymmetric plan, after-action learning. |
| Palantir | What objects and actions make the work operationally legible? | Mission, workstream, evidence, feedback, decision, allowed verbs. |
| Von Neumann | What executable architecture makes the team inspectable and recoverable? | Program, control path, memory, IPC bus, I/O tools, disk, verifier, promotion boundary. |

Reject the launch if any lens is blank. A team without Ender becomes brute-force delegation; a team without Palantir becomes chat-only coordination; a team without von Neumann becomes an uninspectable process.

## Ender Safety Translation

Reusable:

- Give the commander strategic choices, not every tactical instruction.
- Empower team leads and squad owners with clear territories.
- Train through bounded scenarios, immediate feedback, and after-action review.
- Use asymmetric tactics: maker-checker, red-team review, and parallel reconnaissance.
- Understand the opponent, user, bug, or market before trying to overpower it.

Forbidden:

- Hidden real-world consequences.
- Manipulative isolation or no-rest pressure.
- "Win at any cost" goals.
- Psychological stress as a management tool.
- Treating victory as correctness without moral or operational review.

## Von Neumann Command Architecture

Convert the mission into a stored program before launching workers:

```markdown
# Command Program

Program:
  objective:
  non_goals:
  finite_actions:
  stop_condition:

Control:
  commander:
  lead:
  checkpoint_cadence:
  interrupt_policy:

Memory:
  hot_context:
  cold_context:
  state_path:
  artifact_path:

Bus:
  message_schema:
  dependency_states:
  handoff_required_fields:

I/O:
  allowed_tools:
  denied_tools:
  receipt_format:
  rollback_path:

Verifier:
  command_or_fixture:
  reviewer:
  pass_threshold:
  regression_check:

Self-improvement:
  candidate_destination:
  required_evidence:
  human_review:
```

Design rule: strategic control is usually serial, while execution can be parallel. If the commander has not fixed intent, ownership, and verifier, adding agents only amplifies ambiguity.

Automata rule: local worker rules create global behavior. Every worker must know its state transition:

```text
current state + evidence -> next action -> verifier -> next state | stop | escalate
```

Self-reproduction rule: a team may generate reusable process artifacts, but it cannot install them as skills, hooks, schemas, or automations without the V7 promotion gate and a cheap check.

## Ontology Command Board

Represent the team as objects and actions, not chat only.

```markdown
# Command Board

Mission:
  id:
  objective:
  non_goals:
  commander:
  review_budget:
  permission_boundary:

Workstreams:
  - id:
    owner:
    territory:
    inputs:
    allowed_actions:
    denied_actions:
    dependencies:
    verifier:
    stop_condition:

Evidence:
  - id:
    workstream:
    path_or_command:
    result:
    timestamp:

Feedback:
  - id:
    source: operator | reviewer | user | test | telemetry
    correction:
    specificity: high | medium | low
    becomes: eval_case | review_item | contract_update | backlog

Decisions:
  - id:
    decision:
    basis:
    owner:
    rollback:
```

Minimum verbs:

- `claim territory`
- `request input`
- `handoff`
- `verify`
- `reject`
- `integrate`
- `rollback`
- `close`

## Data-Logic-Action Mapping

Before launch, map the team plan:

| Palantir layer | Agent team equivalent |
|---|---|
| Data | Mission, files, source notes, user workflow, artifacts, logs, evidence. |
| Logic | Ownership rules, dependency graph, evaluator, eval suite, decision policy. |
| Action | Tool calls, file edits, messages, PRs, deployments, wiki writes. |
| Feedback | Operator corrections, review comments, test failures, telemetry, user rejects. |

No teammate should act on a domain object it cannot name, verify, and write back.

## FDE Reconnaissance

Use before building in messy enterprise, workflow, ops, customer, compliance, or domain-specific systems.

```text
FDE RECON:
Real workflow observed:
Operator roles:
Systems touched:
Permissions and audit boundary:
Exceptions and edge cases:
Current friction:
Hidden manual step:
Existing artifact/log/source of truth:
Gravel-road artifact to ship first:
Paved-path abstraction candidate:
```

Rule: do not abstract a platform rule from one customer, one workflow, or one demo. First ship a narrow artifact, collect feedback, then decide what generalizes.

## EDD Integration Gate

For each workstream:

```text
Baseline:
Eval suite or fixture:
Grader:
Pass threshold:
Failure triage:
Allowed repair action:
Regression check:
Feedback-to-eval path:
```

Eyeballing a demo is not enough for integration. If feedback is vague, assign a feedback-quality agent to ask for concrete examples and convert them into eval cases or review items.

## Long-Running Orchestrator State

Use when the team may run across hours, days, external approvals, or multiple sessions:

```text
Checkpoint path:
Await condition:
Resume trigger:
Trace/log path:
Human task object:
Timeout:
Retry scope:
Abort condition:
```

Retry the failed step, not the whole mission. Preserve prompt, tool output, artifact path, and decision basis so the team can resume without replaying chat.

## Orchestration Tax And Quiet Success Controls

Use these controls before scaling workers, loops, or generated PR volume:

```text
Review bandwidth:
  max open PRs:
  max changed lines per review batch:
  max files per workstream:
  reviewer:

Understanding checkpoint:
  architecture delta summary:
  invariants:
  demo or trace path:
  rollback plan:
  owner can explain? yes/no

Quiet-success stop:
  if commits or artifacts exceed review cap:
  if lead cannot explain the diff:
  if tests pass but architecture ownership is unclear:
```

Automation can reduce low-level review, but it cannot remove ownership. Use custom evals, PR summaries, traces, demos, and independent reviewers to shrink the review surface; stop launching new teammates when the review queue grows faster than integration.
