---
trigger: model_decision
description: Route tasks to Third Brain V8.1 workspace skills with profile-aware controls.
---

# Third Brain V8.1 Skill Router

Use this rule when the user asks Cascade for knowledge ingestion, daily review, research, verification, behavior design, creativity, startup evaluation, or agent-team orchestration.

Routing:

- Source, PDF, article, or note ingestion -> `@wiki-ingest`
- Daily review or daily planning -> `@daily-okr`
- Deep understanding or synthesis -> `@cognitive-compile`
- Completion claim, bug fix, tests, shipping -> `@verify-before-claim`
- Habit or behavior change -> `@behavior-design`
- Idea generation -> `@creativity-engine`
- Research report, market scan, competitor analysis, or fast-changing evidence question -> `@deep-research`
- Startup idea or due diligence -> `@startup-evaluation`
- Property operations, dispatch, quotes, evidence, CTQ metrics, or AI Six Sigma -> `@ai-six-sigma-property-os`
- Knowledge organization, deduplication, or vector search -> `@knowledge-ops`
- Wiki health check, broken links, or stale pages -> `@wiki-lint`
- Context limits or token budget -> `@context-manager`
- Project triage, WIP, blockers, or completion state -> `@project-flow-ops`
- Session closure or reusable learning extraction -> `@session-learn`
- Repeatable task, scheduled routine, or bounded correction loop -> `@loop-engineering`
- Explicit dependencies, independently executable branches, typed joins, or node-local recovery -> `@graph-engineering`
- Agent workflow refactor or autonomy design -> `@agentic-engineering`
- Agent permissions, tools, observability, or runtime safety -> `@harness-engineering`
- Team operating system, growth method, or self-evolving work method -> `@anthropic-os`
- Multi-agent execution -> `@agent-teams-command`
- Audit manual work, prior sessions, or interviews for reusable workflows -> `@workflow-audit`

Engineering boundary: Loop = temporal depth; Graph = dependency width; Agent Teams = process ownership, IPC, and integration; Harness = runtime scheduler, permissions, and observability. Use `@graph-engineering` only when admission value exceeds orchestration and review cost. V8.1 supports bounded static DAGs, not dynamic or cyclic graphs.

For each selected skill:

1. Read `metadata.profile`, `assumes`, and `conflicts_with` before acting.
2. Follow `Usage Template` and `Workflow`, including unknowns and evaluation.
3. Use the standard Failure Protocol and Output Contract.
4. Resolve wiki paths from `system/config.md` when present.
5. Summarize created files, verification evidence, and remaining risk.
6. Avoid completion claims unless fresh evidence satisfies Success Metrics and Quality Gates.

For `high-risk` profiles require independent verification, approval boundaries, rollback, and an audit receipt. Persist state before returning from `stateful`, `loop`, and `high-risk` profiles.
