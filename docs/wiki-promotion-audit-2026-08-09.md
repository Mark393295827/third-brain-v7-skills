# Wiki Promotion Audit - 2026-08-09

## Scope

Reviewed Obsidian intake written on 2026-08-08 and 2026-08-09, with priority
on `wiki/concepts/ai-engineering/`, the local ingest receipts in
`system/log.md`, and the multi-source `AI价值捕获` concept. Immutable vault
sources were read only.

## Promotion Gate

A pattern was promoted only when it had two durable supports or one strong
source plus local verification, could be expressed as a bounded execution
contract, preserved permission/provenance boundaries, and had a cheap check.

## Promoted

### 1. Deterministic Runtime Envelope

Target skills: `harness-engineering`, `agentic-engineering`,
`loop-engineering`, `agent-teams-command`, `context-manager`, and
`verify-before-claim`.

Durable support:

- `wiki/concepts/ai-engineering/确定性护栏的智能体工作流.md`
- `wiki/concepts/ai-engineering/AI Agent零信任与最小代理权.md`
- `wiki/concepts/ai-engineering/软件工厂的可验证自动化.md`
- `wiki/concepts/ai-engineering/Agent Skill质量治理.md`
- `wiki/concepts/ai-engineering/人机协同开发共享表面.md`

Representative source locators include
`sources/2026-08/2026-08-09-realtime-multiplayer-automation-idan-gazit.md#^gazit-deterministic-guardrails`,
`#^gazit-safe-quiet-outputs`, `#^gazit-agent-security-principles`,
`sources/2026-08/src-20260807-ai-agent-database-delete.md#^agent-risk-zero-trust`,
and `sources/2026-08/src-20260806-snyk-skill-review.md#^snyk-skill-iteration`.

Promoted rule: keep a human-reviewable intent plan, compile and validate a
host-enforced runtime envelope, normalize termination routing, isolate secrets,
stage writes, cap outputs, and accept quiet `NO_OP` only with direct evidence.

Local verification:

- `skills/harness-engineering/scripts/validate_runtime_envelope.py`
- `skills/harness-engineering/references/runtime-envelope-example.json`
- `tools/test_validate_runtime_envelope.py`
- `tools/test_promoted_skill_contracts.py`

### 2. Concurrent Ingest Idempotency

Target skills: `wiki-ingest` and `knowledge-ops`.

Durable support:

- Local clipping receipt `20260809-100533-365` reused the existing real-time
  multiplayer source after an exact-URL search instead of creating a duplicate.
- A controller reconciliation event in batch `20260809-100533-365` detected a
  concurrent Otis source race, selected one canonical source, repointed derived
  citations, and logged reconciliation.
- Existing STOW and storage-governance contracts already prohibited duplicate
  canonical sources and required provenance-preserving receipts.

Promoted rule: derive a stable source identity, search before staging, recheck
at commit and after write, converge concurrent writers to one canonical path,
and deduplicate machine log appends with an idempotency key.

### 3. AI-Native Value-Capture Ledger

Target skill: `startup-evaluation`.

Durable support:

- `wiki/concepts/ai-economics/AI价值捕获.md` is marked `multi-source` and
  separates adoption, productivity, customer ROI, supplier profit, model
  commoditization, and institutional-learning ownership.
- `wiki/concepts/ai-economics/AI支出者与AI盈利者.md` provides a recent
  single-source case that remains subordinate to the multi-source framework.

Promoted rule: evaluate usage, productivity, customer ROI, and vendor profit
separately; split the spending engine from the earning engine; test who owns
workflow exceptions, context, permissions, and feedback write-back.

## Deferred

- CCA exam details, provider-specific stop values, batch discounts, and product
  availability remain single-source mediated claims. Only the provider-neutral
  termination-control pattern was promoted.
- Wisedocs benchmark numbers, fixed success thresholds, and a universal
  monorepo-first refactor rule remain single-source. The skill only promotes
  bounded task-horizon probes and decomposition with local verifiers.
- Otis figures and the installed-base service flywheel remain single-source
  company evidence. No cross-industry rule was added to property or startup
  skills.
- Claimed multi-model cost savings, plugin portability, and specific product
  formats remain single-source or time-sensitive and were not embedded as
  durable model/vendor rules.

## Verification Contract

Run:

```powershell
python tools/lint-agent-skills.py
python -m unittest tools.test_validate_runtime_envelope -v
python -m unittest tools.test_promoted_skill_contracts -v
python skills/harness-engineering/scripts/validate_runtime_envelope.py `
  skills/harness-engineering/references/runtime-envelope-example.json --strict
```

The pre-existing untracked `test_multi_agent_vault_team` test timed out during
the baseline full-tool suite before these skill edits. It is not used as
evidence for this promotion and is reported separately from changed-file tests.
