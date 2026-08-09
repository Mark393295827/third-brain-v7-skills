# Third Brain V7.2 Skills — Claude Code

For detailed installation, usage, and workflow scenarios, see **[GUIDE.md](GUIDE.md)**.

You have access to the 20 Agent Skills defined in `~/.claude/skills/` or `~/.agents/skills/`.

## V7.2 Multi-Domain Taxonomy Specification

V7.2 defines a multi-domain taxonomy for the active Obsidian vault (`C:\Users\高杰\Documents\Obsidian Vault`):

1. **`wiki/concepts/` (13 Domain Subdirectories):**
   `ai-engineering`, `ai-economics`, `ai-science`, `behavioral-econ`, `business-strategy`, `entrepreneurship`, `general-concepts`, `geopolitics-energy`, `identity-culture`, `investing-macro`, `investing-quant`, `investing-vc`, `knowledge-systems`.

2. **`wiki/entities/` (5 Category Subdirectories):**
   `people`, `companies`, `funds-investors`, `products`, `orgs`.

3. **`sources/` (6 Pool Subdirectories):**
   `YYYY-MM/` (e.g. `2026-07/`), `pre-2026/`, `books/` (>100KB).

4. **`wiki/outputs/` (3 Category Subdirectories):**
   `gmail-digests/`, `evaluations/`, `compilations/`.

5. **`maps/` (4 Map Tier Subdirectories):**
   `domain-mocs/`, `system-indexes/`, `project-maps/`, `canvases/` (plus `Home.md` & `中央索引.md`).

6. **`system/` (Log Rotation Contract):**
   Active log at `system/log.md` (keep <100KB); archive historical entries to `system/logs/log-archive-historical.md`.

---

## 20 Core Skills Overview

### 📥 Knowledge Pipeline
- **wiki-ingest** — STOW pipeline with 13-domain concept placement, 5-category entity placement, block refs, Karpathy understanding gate, governance notes, and post-ingest lint.
- **knowledge-ops** — Multi-layer knowledge management with Markdown-first retrieval, optional ChromaDB vector support, evidence hierarchy, deduplication, and knowledge debt queues.
- **wiki-lint** — Health-check the wiki across graph health, link integrity, taxonomy compliance, provenance debt, clipping lifecycle, understanding integrity, and drift.

### 🔄 Daily Loop
- **daily-okr** — 7 Key Results daily cycle (Input → Cognition → Wiki → Behavior → Creativity → Output → Feedback).
- **cognitive-compile** — 8-section deep learning compile (Question → Facts → Concepts → Patterns → Conflicts → Hypotheses → Decision → Action).

### 🎨 Behavior & Creativity
- **behavior-design** — Behavior change system with HAS framework.
- **creativity-engine** — Combinatorial ideation (Bending / Breaking / Blending) + minimum experiments.

### 🔬 Research & Quality
- **deep-research** — STOW-compatible research harness with preflight, source/claim ledgers, activity trace, citations, and wiki-ingest handoff.
- **verify-before-claim** — Empirical verification gate before completion claims.

### 🔄 Learning & Workflow
- **session-learn** — Extract knowledge signal types from sessions with Closure Protocol.
- **project-flow-ops** — Triage, plan, track, and review across projects.

### 📊 Context & Cost
- **context-manager** — Runtime-derived budgets, checkpoints, compaction, retrieval, and capability routing.
- `token-cost-tracker` — command for estimate/log/report.

### 🏗️ Engineering & Multi-Agent Architecture
- **loop-engineering** — Temporal-depth control through bounded Goal/Loop/Automation/AutoResearch contracts with state, verification, retry, and recovery.
- **graph-engineering** — Dependency-width control through bounded static DAGs with explicit dependencies, independent branches, typed joins, and node-local recovery.
- **agentic-engineering** — Refactor skills and workflows as agent processes with autonomy defaults, state checkpoints, write-back, and verification gates.
- **harness-engineering** — Agent runtime kernel: scheduler, permissions, tools as system calls, provenance ledgers, observability, and recovery.
- **agent-teams-command** — Multi-agent process ownership, parallel subagent orchestration, IPC, async budget envelopes, integration, cleanup, and evidence gates.

### 💼 Strategy & Operations
- **startup-evaluation** — Startup health diagnosis with entrepreneurship, VC 5T, PMF, runway, team, and next-test frameworks.
- **anthropic-os** — Self-evolving work method engine with 3B creativity algorithms.
- **ai-six-sigma-property-os** — AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, and MVP quality control.

---

## Karpathy LLM OS

LLM=CPU · Context=RAM · Storage=Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes
