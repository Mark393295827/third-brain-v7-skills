# Agentic OS Demo Alignment — Sol Requirements Matrix

Source evidence: `Clippings/The Agentic OS Setup That Will 10x Claude Code.md`
Planner receipt: T01, read-only, 2026-08-20.

Implementation target: **Codex OS**. The clipping demonstrates transferable
AIOS patterns; Claude-specific commands, billing, folders, and headless runtime
are not project requirements.

## Level 1 — Workflow Backbone

| Requirement | Current evidence | Required delta |
|---|---|---|
| Audit manual work, prior sessions, or an operator interview | 20 contract-bearing skills and examples | Add a workflow-audit command/skill, durable repeated-task evidence, and audit-to-skill decisions |
| Codify repeatable work as skills | 20 V8.1 skills with lint coverage | Generate a machine-readable registry; eliminate hard-coded UI parity claims |
| Decide what can be automated or scheduled | One strict knowledge loop and canonical worker CLI | Add eligibility, trigger, permission, verifier, stop, and receipt metadata for each exposed action |
| Learn from prior runs without autonomous policy mutation | Durable state, receipts, finite retries, CAS, rollback | Add run-history/feedback surfaces and supervised promotion decisions |

## Level 2 — Memory, State, Navigation

| Requirement | Current evidence | Required delta |
|---|---|---|
| Coherent Markdown store with a top-down map | V8.1 taxonomy, Home, central index, MOCs, system indexes | Make compact navigation reproducible from the repository rather than depending on oversized live-only notes |
| Folder-level indexes where useful | Existing map tiers | Add compact system/navigation and run/debt indexes without weakening source immutability |
| Current agent navigation instructions | `system/codex.md` and root `AGENTS.md` are the Codex authority; `system/claude.md` is a compatibility redirect | Deploy the Codex contract without changing the legacy `.claude/` compatibility tree |
| Durable history and feedback state | One committed system-bundle run; inventory/freshness queries | Add a run index and surface material debt without claiming it is resolved |

## Level 3 — Visual Command Center

| Requirement | Current evidence | Required delta |
|---|---|---|
| Real customized metrics | `tools/index.html` is a bilingual navigator | Bind it to a host-generated snapshot of repository, Vault, debt, freshness, and run evidence |
| One-click actions | Existing links open documentation/tools | Add an allowlisted host dispatcher with queued/running/result states and typed receipts |
| No mock success | Runtime already requires receipts and approvals | Disable host-dependent/unavailable actions and retire or label stale V5 dashboards as historical |

## Level 4 — Distribution

| Requirement | Current evidence | Required delta |
|---|---|---|
| Shareable cross-harness setup | Installers, adapters, CI canaries | Package/probe the command center, runtime, Vault bundle, and dependencies—not only skills |
| Nontechnical onboarding | README, GUIDE, quickstarts | Correct direct-write guidance; add capability/permission readiness and an isolated end-to-end canary |

## Host-Dependent Boundaries

Schedulers, services, headless model invocation, billing, credentials, connectors, voice, external metrics, Obsidian plugin installation, external publication, and live Vault commit require explicit host evidence or approval. Productivity multipliers remain unverified claims. “Self-improvement” means supervised, receipt-backed promotion with rollback—not autonomous policy mutation.

## Integration Priority

1. Freeze registry, snapshot, action-state, and receipt interfaces.
2. T02 builds workflow audit, registry, snapshot, and allowlisted dispatcher primitives.
3. T03 builds compact navigation/run/debt surfaces and bundle deployment entries.
4. T04 binds the UI/package only to stable T02 contracts.
5. T05 integrates serially, verifies every requirement, then uses the approved V8.1 deployment path.
