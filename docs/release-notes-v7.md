# Third Brain V7 Release Notes

V7 refactors all 19 Agent Skills around one profile-aware execution contract derived from bounded loop design, explicit unknown handling, and high-signal modular architecture.

Operational guidance: [V7 最大潜力使用手册](v7-max-potential-guide-zh.md).

## V7.1 Additive Update

V7.1 adds `graph-engineering` as the 20th Agent Skill. It governs dependency width through bounded static DAGs with explicit dependencies, independently executable branches, typed joins, deterministic readiness, and node-local recovery. Dynamic expansion and cyclic graphs remain out of scope.

Strict Graph validation treats failure routes as control arcs and binds every
external effect to an exact approval scope, a direct typed human-gate receipt,
explicitly allowed write targets, and compensation. Loop validation rejects
unbounded fallback language even when an earlier numeric cap is present.

The engineering boundaries remain explicit:

- Loop Engineering = temporal depth.
- Graph Engineering = dependency width.
- Agent Teams Command = process ownership, IPC, and integration.
- Harness Engineering = runtime scheduler, permissions, and observability.

Adopt `graph-engineering` after `loop-engineering` only when its admission value exceeds orchestration and review cost.

## Execution Contract

Every skill now provides:

- nested governance metadata with `version`, `updated`, `profile`, `assumes`, and `conflicts_with`;
- structured `intake -> unknowns_gate -> execute -> evaluate` control flow;
- standard failure codes and an inspectable output receipt;
- two domain-specific edge cases;
- durable state for stateful, loop, and high-risk profiles;
- bounded retry for loop/high-risk profiles;
- independent verification, approval, and rollback for high-risk profiles.

## Adaptability

- Durable skills route by runtime capability rather than model name.
- Context limits, prices, tools, permissions, and budgets are discovered at runtime.
- Repeated teaching material and low-frequency schemas moved into lazy `references/` files.
- Missing hook examples were removed; a hook is valid only when its executable exists and is tested.

## Current V7.1 Profiles

| Profile | Skills |
|---|---|
| One-shot | `cognitive-compile`, `creativity-engine`, `startup-evaluation` |
| Stateful | `behavior-design`, `context-manager`, `daily-okr`, `knowledge-ops`, `project-flow-ops`, `session-learn`, `wiki-lint` |
| Loop | `loop-engineering` |
| High-risk | `agent-teams-command`, `agentic-engineering`, `ai-six-sigma-property-os`, `anthropic-os`, `deep-research`, `graph-engineering`, `harness-engineering`, `verify-before-claim`, `wiki-ingest` |

## Verification

- `python tools/lint-agent-skills.py` validates all 20 current skills; the original V7 release contained 19.
- `python -m unittest tools.test_lint_agent_skills -v` covers the V7 linter and canonical template.
- The strict CI repair loop example passes `validate_loop_contract.py`.
- The strict diamond graph example passes `validate_graph_contract.py`.

V6 notes remain as historical migration context. V7 does not relax source immutability, review queues, permission boundaries, or the promotion gate.
