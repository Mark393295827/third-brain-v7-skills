# Third Brain V7.2 Skills — Codex / Antigravity CLI

This repository contains Agent Skills for Codex CLI & Antigravity CLI environments. Place skills in `~/.agents/skills/` or `~/.gemini/skills/`.

V7.2 updates the Obsidian Vault Taxonomy to a multi-domain architecture (13 concept domains, 5 entity categories, 6 source pools, 3 output types, and 4 maps tiers). Every skill uses a profile-aware execution contract and resolves target paths via `system/config.md`.

## Skills Summary (20 Skills)

### 📥 Knowledge Pipeline
- **wiki-ingest** — STOW pipeline (Source → Transform → Organize → Write-back) with 13-domain concept placement, 5-category entity placement, block refs, Karpathy understanding gate, and post-ingest lint.
- **knowledge-ops** — Multi-layer knowledge management with Markdown-first retrieval, optional vector storage, evidence hierarchy, deduplication, Agent/Wiki flywheel, and knowledge debt queues.
- **wiki-lint** — Wiki health check for graph integrity, provenance, link health, taxonomy compliance, clipping lifecycle, understanding, and promotion readiness.

### 🔄 Daily Loop
- **daily-okr** — 7 Key Results daily knowledge compound cycle (Input → Cognition → Wiki → Behavior → Creativity → Output → Feedback).
- **cognitive-compile** — 8-section deep learning compile framework (Question → Facts → Concepts → Patterns → Conflicts → Hypotheses → Decision → Action).

### 🎨 Behavior & Creativity
- **behavior-design** — Behavior change system with HAS (Human Agency Scale) framework.
- **creativity-engine** — Combinatorial ideation (Bending / Breaking / Blending) + minimum experiments.

### 🔬 Research & Quality
- **deep-research** — STOW-compatible research harness with preflight, source/claim ledgers, activity trace, citations, and wiki-ingest handoff.
- **verify-before-claim** — Verification-first quality gate. No completion claims without empirical logs or test receipts.

### 🔄 Learning & Workflow
- **session-learn** — Knowledge extraction with Closure Protocol.
- **project-flow-ops** — Project triage, state tracking, and execution governance.

### 📊 Context & Cost
- **context-manager** — Runtime-derived context budgets, checkpoints, compaction, retrieval, and capability routing.
- `token-cost-tracker` is a command under `commands/`, not an Agent Skill.

### 🏗️ Engineering & Multi-Agent Architecture
- **agentic-engineering** — Agent-as-process workflow refactoring with autonomy defaults, delegated-action boundaries, state checkpoints, write-back, and verification gates.
- **loop-engineering** — Temporal-depth control through bounded Trigger → Execute → Verify → State loops, durable contracts, hard budgets, and stop/recovery rules.
- **graph-engineering** — Dependency-width control for bounded static DAGs with explicit dependencies, independent branches, typed joins, and node-local recovery.
- **harness-engineering** — Runtime kernel design: scheduler, permissions, tools as system calls, MCP/Skills/Hooks selection, provenance ledgers, observability, and recovery.
- **agent-teams-command** — Multi-agent process ownership, IPC, worktree isolation, async budget envelopes, parallel subagent orchestration, and evidence gates.

### 💼 Strategy & Operations
- **startup-evaluation** — Startup health diagnosis with entrepreneurship, VC 5T, PMF, runway, team, and next-test frameworks.
- **anthropic-os** — Self-evolving work method engine with 3B creativity algorithms.
- **ai-six-sigma-property-os** — AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, and MVP quality control.

---

## V7.2 Vault Taxonomy Contract (`system/config.md`)

- **`wiki/concepts/` (13 Domains):** `ai-engineering`, `ai-economics`, `ai-science`, `behavioral-econ`, `business-strategy`, `entrepreneurship`, `general-concepts`, `geopolitics-energy`, `identity-culture`, `investing-macro`, `investing-quant`, `investing-vc`, `knowledge-systems`.
- **`wiki/entities/` (5 Categories):** `people`, `companies`, `funds-investors`, `products`, `orgs`.
- **`sources/` (6 Pools):** `YYYY-MM/` (e.g. `2026-07/`), `pre-2026/`, `books/` (>100KB).
- **`wiki/outputs/` (3 Categories):** `gmail-digests/`, `evaluations/`, `compilations/`.
- **`maps/` (4 Tiers):** `domain-mocs/`, `system-indexes/`, `project-maps/`, `canvases/` (plus `Home.md` & `中央索引.md`).

---

## Skill Contract & Execution

When selecting a skill, read its frontmatter before executing:
- `assumes` — required operating assumptions.
- `conflicts_with` — boundaries that must not be silently overridden.
- `metadata.profile` — `one-shot`, `stateful`, `loop`, or `high-risk` controls.
- `## Failure Protocol` and `## Output Contract` — standard stop status and receipt.
- `## Success Metrics` — minimum observable result for one successful run.
- `## Quality Gates` — checks that must pass before claiming completion.

---

## Karpathy LLM OS

LLM=CPU · Context=RAM · Storage=Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes
