# Agent Skills Standard

This repository uses portable Agent Skills folders with a V7 execution contract.

## Package Contract

```text
skill-name/
├── SKILL.md
├── agents/       # recommended UI metadata
├── scripts/      # deterministic execution and validation
├── references/   # selectively loaded detail
└── assets/       # output resources, not prompt context
```

Do not add auxiliary READMEs, changelogs, installation guides, or process diaries inside skill folders.

## Frontmatter

Keep discovery fields at the top level and V7 governance fields under `metadata`:

```yaml
---
name: skill-name
description: State the owned transformation and complete "Use when" trigger.
metadata:
  version: "7.0.0"
  updated: "YYYY-MM-DD"
  profile: "one-shot | stateful | loop | high-risk"
  assumes: "Required operating condition."
  conflicts_with: "Boundary that must not be overridden."
---
```

`name` must match the folder. The description is the discovery layer; do not duplicate it in a `When to Use` section.

## Required Hot Path

Every `SKILL.md` must contain:

- `## Usage Template`
- `## Success Metrics`
- `## Workflow`
- `## Failure Protocol`
- `## Output Contract`
- `## Edge Cases`
- `## Quality Gates`

Use the canonical [Base Skill Template](skill-template.md). Delete optional blocks that do not apply, but preserve the required behavior:

```text
intake -> unknowns gate -> execute -> evaluate -> success | bounded retry | controlled stop -> receipt
```

## Execution Profiles

| Profile | Additional requirement |
|---|---|
| One-shot | One post-output evaluation and receipt |
| Stateful | Durable state updated before every return |
| Loop | Finite attempt/time/cost caps, changed-hypothesis retry, recovery |
| High-risk | Independent evaluator, explicit approval, rollback, audit trail |

Do not force loop machinery into one-shot skills. Do not allow complex skills to omit state and recovery.

## Progressive Disclosure

Use three loading levels:

1. Discovery: `name` and `description`.
2. Activation: compact `SKILL.md` control flow.
3. Execution: load references or run scripts only when routed by the hot path.

Keep `SKILL.md` below 350 lines. Prefer an 80-200 line hot path when the domain permits it. Keep references one level from `SKILL.md` and give long references a table of contents.

## Model Adaptability

- Route by capability (`fast`, `reasoning`, `multimodal`, `independent-evaluator`), not vendor model name.
- Discover context, tools, permissions, and budgets at runtime.
- Treat large context windows as capacity, not permission to load irrelevant material.
- Move deterministic formatting, parsing, linting, and schema checks into scripts or hooks.
- Use model evaluation only after deterministic evidence is exhausted or when judgment is inherently subjective.

## Unknowns And Failure

- Probe only decisions that change architecture, authority, irreversibility, or acceptance criteria.
- Inspect or prototype before guessing about the repository or environment.
- Emit a standard failure status when evidence, permission, dependency, progress, or budget is insufficient.
- Never fabricate missing inputs, successful verification, automation, scripts, citations, or state.

## State And Handoffs

Persist multi-call state with a schema version, objective, status, attempt, assumptions, decisions, deviations, artifacts, evidence, open unknowns, last error, and next action.

Every cross-skill handoff must name:

- destination skill
- observable routing condition
- typed payload
- expected return contract
- real implementation mechanism when claimed as automatic

## Validation

Run:

```powershell
python tools\lint-agent-skills.py
```

The V7 linter should validate frontmatter, required sections, line budgets, resource existence, executable-reference honesty, standard failure coverage, and conditional state/retry controls.
