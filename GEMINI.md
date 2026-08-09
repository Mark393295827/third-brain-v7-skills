# Third Brain V7.2 Skills — Gemini / Antigravity CLI

This repository contains Agent Skills for Gemini CLI & Antigravity CLI environments. Place skills in `~/.gemini/skills/` or `~/.agents/skills/`.

## V7.2 Vault Taxonomy & Architecture

V7.2 defines a multi-domain taxonomy for the Obsidian Vault (`C:\Users\高杰\Documents\Obsidian Vault`):
- `wiki/concepts/`: 13 domain subdirectories (`ai-engineering`, `ai-economics`, `ai-science`, `behavioral-econ`, `business-strategy`, `entrepreneurship`, `general-concepts`, `geopolitics-energy`, `identity-culture`, `investing-macro`, `investing-quant`, `investing-vc`, `knowledge-systems`)
- `wiki/entities/`: 5 category subdirectories (`people`, `companies`, `funds-investors`, `products`, `orgs`)
- `sources/`: 6 chronological & book subdirectories (`2026-07`, `2026-06`, `2026-05`, `2026-04`, `pre-2026`, `books`)
- `wiki/outputs/`: 3 output subdirectories (`gmail-digests`, `evaluations`, `compilations`)
- `maps/`: 4 map tier subdirectories (`domain-mocs`, `system-indexes`, `project-maps`, `canvases`)
- `system/`: Active log (`system/log.md`) + Historical log archive (`system/logs/log-archive-historical.md`)

---

## 20 Core Agent Skills

### 📥 Knowledge Pipeline
- **wiki-ingest** — STOW pipeline with multi-domain concept placement, category entity placement, block refs, clipping lifecycle, Karpathy understanding gate, and post-ingest lint.
- **knowledge-ops** — Multi-layer knowledge management with Markdown-first retrieval, optional vector storage, evidence hierarchy, deduplication, and knowledge debt queues.
- **wiki-lint** — Wiki health check for graph health, link integrity, taxonomy compliance, provenance debt, clipping lifecycle, and understanding.

### 🔄 Daily Loop
- **daily-okr** — 7 Key Results daily knowledge compound cycle.
- **cognitive-compile** — 8-section deep learning compile framework.

### 🎨 Behavior & Creativity
- **behavior-design** — Behavior change system with HAS framework.
- **creativity-engine** — Combinatorial ideation (Bending / Breaking / Blending) + minimum experiments.

### 🔬 Research & Quality
- **deep-research** — STOW-compatible research harness with preflight, source/claim ledgers, activity trace, citations, and wiki-ingest handoff.
- **verify-before-claim** — Verification-first quality gate.

### 🔄 Learning & Workflow
- **session-learn** — Knowledge extraction with Closure Protocol.
- **project-flow-ops** — Project triage, state tracking, and execution governance.

### 📊 Context & Cost
- **context-manager** — Runtime-derived context budgets, checkpoints, compaction, retrieval, and capability routing.
- `token-cost-tracker` is a command under `commands/`, not an Agent Skill.

### 🏗️ Engineering & Multi-Agent Architecture
- **loop-engineering** — Temporal-depth control through bounded Goal/Loop/Automation/AutoResearch contracts with state, verification, retry, and recovery.
- **graph-engineering** — Dependency-width control through bounded static DAGs with explicit dependencies, independent branches, typed joins, and node-local recovery.
- **agentic-engineering** — Agent-as-process workflow refactoring with autonomy defaults, delegated-action boundaries, state checkpoints, write-back, and verification gates.
- **harness-engineering** — Agent runtime kernel design: scheduler, permissions, tools as system calls, provenance ledgers, observability, and recovery.
- **agent-teams-command** — Multi-agent process ownership and orchestration with IPC, parallel subagents, async budget envelopes, integration, cleanup, and evidence gates.

### 💼 Strategy & Operations
- **startup-evaluation** — Startup health diagnosis with entrepreneurship, VC 5T, PMF, runway, team, and next-test frameworks.
- **anthropic-os** — Self-evolving work method engine with 3B creativity algorithms.
- **ai-six-sigma-property-os** — AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, and MVP quality control.

---

## Karpathy LLM OS

LLM=CPU · Context=RAM · Storage=Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes
