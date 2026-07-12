# Third Brain V7 Skills — Gemini CLI

This repository contains Agent Skills for the Gemini CLI environment. Place skills in `~/.gemini/skills/`.

## Skills

### 📥 Knowledge Pipeline
- **wiki-ingest** — STOW pipeline with source-risk classification, macro-action scope, block refs, clipping archive, Karpathy understanding gate, governance notes, and post-ingest lint.
- **knowledge-ops** — Multi-layer knowledge management with Markdown-first retrieval, optional vector storage, evidence hierarchy, deduplication, and knowledge debt queues.
- **wiki-lint** — Wiki health check for P0/P1 graph health, source refs, frontmatter, links, provenance debt, clipping lifecycle, and understanding integrity.

### 🔄 Daily Loop
- **daily-okr** — 7 Key Results daily knowledge compound cycle.
- **cognitive-compile** — 8-section deep learning compile framework.

### 🎨 Behavior & Creativity
- **behavior-design** — Behavior change system with HAS framework.
- **creativity-engine** — Combinatorial ideation + minimum experiments.

### 🔬 Research & Quality
- **deep-research** — STOW-compatible research harness with ChatGPT-style preflight, source/claim ledgers, activity trace, citations, privacy checks, and wiki-ingest handoff.
- **verify-before-claim** — Verification-first quality gate.

### 🔄 Learning
- **session-learn** — Knowledge extraction with Closure Protocol.
- **project-flow-ops** — Project triage and tracking.

### 📊 Context & Cost
- **context-manager** — Runtime-derived context budgets, checkpoints, compaction, retrieval, and capability routing.
- `token-cost-tracker` is a command under `commands/`, not an Agent Skill.

### 🏗️ Engineering
- **loop-engineering** — Bounded Goal/Loop/Automation/AutoResearch contracts with state, verification, retry, and recovery.
- **agentic-engineering** — Agent-as-process workflow refactoring with autonomy defaults, delegated-action boundaries, state checkpoints, write-back, and verification gates.
- **harness-engineering** — Agent runtime kernel design: permissions, tools as system calls, provenance ledgers, delegated-action gates, observability, and recovery.
- **agent-teams-command** — Multi-agent process orchestration with ownership, IPC, async budget envelopes, integration, cleanup, and evidence gates.

### 💼 Strategy & Operations
- **startup-evaluation** — Startup health diagnosis with entrepreneurship, VC 5T, PMF, runway, team, and next-test frameworks.
- **anthropic-os** — Self-evolving work method engine.
- **ai-six-sigma-property-os** — AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, and MVP quality control.

## Compatibility

All skills follow the [Agent Skills](https://agentskills.io) open format. Skills are model-agnostic markdown files compatible with Gemini CLI.

## Skill Contract

When selecting a skill, read its frontmatter before executing:

- `assumes` — required operating assumptions.
- `conflicts_with` — boundaries that must not be silently overridden.
- `metadata.profile` — `one-shot`, `stateful`, `loop`, or `high-risk` controls.
- `## Failure Protocol` and `## Output Contract` — standard stop status and receipt.
- `## Success Metrics` — the minimum observable result for one successful run.
- `## Quality Gates` — checks that must pass before claiming completion.

For wiki-writing skills, resolve paths from `system/config.md` when available. Defaults include `SOURCES_DIR=sources/`, `CONCEPTS_DIR=wiki/concepts/`, `ENTITIES_DIR=wiki/entities/`, and `LOG_FILE=system/log.md`.

## Adoption Ladder

1. Start with `wiki-ingest` + `verify-before-claim`.
2. Add `daily-okr` + `session-learn` after daily ingest and evidence checks are working.
3. Add `cognitive-compile`, `behavior-design`, and `creativity-engine` when the wiki has enough material to synthesize.
4. Add `knowledge-ops`, `harness-engineering`, `agentic-engineering`, and `agent-teams-command` only when scale, reliability, or multi-agent ownership requires them.

## Karpathy LLM OS

LLM=CPU · Context=RAM · Storage=Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes
