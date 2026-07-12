# Third Brain V7 Skills — Claude Code

For detailed installation, usage, and workflow scenarios, see **[GUIDE.md](GUIDE.md)**.

You have access to the following Agent Skills. Each skill is a markdown file in `~/.claude/skills/` that defines a specific capability.

## Skill Categories

### 📥 Knowledge Pipeline
- **wiki-ingest** — Ingest sources into an interlinked wiki with source-risk classification, macro-action scope, block refs, clipping archive, Karpathy understanding gate, governance notes, and post-ingest lint. STOW pipeline: Source → Think → Organize → Write.
- **knowledge-ops** — Multi-layer knowledge management with Markdown-first retrieval, optional ChromaDB vector support, evidence hierarchy, deduplication, and knowledge debt queues.
- **wiki-lint** — Health-check the wiki across P0/P1 graph health, source refs, frontmatter, links, provenance debt, clipping lifecycle, understanding integrity, and drift.

### 🔄 Daily Loop
- **daily-okr** — 7 Key Results daily cycle: Input → Cognition → Wiki → Behavior → Creativity → Output → Feedback, each with evidence.
- **cognitive-compile** — 8-section deep learning compile: Question → Facts → Concepts → Patterns → Conflicts → Hypotheses → Decision → Action.

### 🎨 Behavior & Creativity
- **behavior-design** — Behavior change system: goals → habits → triggers → SOPs → review. Includes HAS (Human Agency Scale).
- **creativity-engine** — Combinatorial ideation with Lego Building Blocks method. Cross-domain analogies + minimum experiments.

### 🔬 Research & Quality
- **deep-research** — STOW-compatible research harness with ChatGPT-style preflight, source/claim ledgers, activity trace, citations, privacy checks, and wiki-ingest handoff.
- **verify-before-claim** — No completion claims without fresh, scope-matched verification evidence.

### 🔄 Learning
- **session-learn** — Extract 7 knowledge signal types from sessions. Closure Protocol for feedback loops.
- **project-flow-ops** — Triage, plan, track, review across projects.

### 📊 Context & Cost
- **context-manager** — Runtime-derived budgets, checkpoints, compaction, retrieval, and capability routing.
- `token-cost-tracker` — command for estimate/log/report; it is not an Agent Skill.

### 🏗️ Engineering
- **loop-engineering** — Bounded Goal/Loop/Automation/AutoResearch contracts with state, verification, retry, and recovery.
- **agentic-engineering** — Refactor skills and workflows as agent processes with autonomy defaults, delegated-action boundaries, state checkpoints, write-back, and verification gates.
- **harness-engineering** — Agent runtime kernel: three-tier permissions, tools as system calls, provenance ledgers, delegated-action gates, observability, recovery, and closed-loop design.
- **agent-teams-command** — Multi-agent process orchestration with ownership, IPC, async budget envelopes, integration, cleanup, and evidence gates.

### 💼 Strategy & Operations
- **startup-evaluation** — Startup health diagnosis with entrepreneurship, VC 5T, PMF, runway, team, and next-test frameworks.
- **anthropic-os** — Cognitive Symbiont Engine. Livewired + 3B creativity algorithms (Bending/Breaking/Blending). Predictive coding, time-arrow diagnostics.
- **ai-six-sigma-property-os** — AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, and MVP quality control.

## Usage

Invoke any skill naturally:
- "Ingest this article into my wiki"
- "Run a cognitive compile on X"
- "Create an agent team to build Y"
- "Launch Anthropic OS for my team" — includes 3B creativity algorithms
- "Design my Property Agent OS with AI Six Sigma"
- "Apply 3B to our growth strategy" — Bending/Breaking/Blending
- "Estimate token cost for this task"

## Skill Contract

Before executing a selected skill, read the skill frontmatter and enforce:

- `assumes`: required operating assumptions for safe use.
- `conflicts_with`: workflows or assumptions that must not be silently overridden.
- `metadata.profile`: `one-shot`, `stateful`, `loop`, or `high-risk` control depth.
- `## Failure Protocol` and `## Output Contract`: standard stop status and receipt.
- `## Success Metrics`: minimum measurable result for one successful run.
- `## Quality Gates`: checks required before completion claims.

For wiki-writing skills, resolve `SOURCES_DIR`, `CONCEPTS_DIR`, `ENTITIES_DIR`, `OUTPUTS_DIR`, and `LOG_FILE` from `system/config.md` when available. If no config exists, use the default STOW layout.

## Recommended Adoption Ladder

1. Week 1: `wiki-ingest` + `verify-before-claim`.
2. Weeks 2-4: add `daily-okr` + `session-learn`.
3. Month 2+: add `cognitive-compile`, `behavior-design`, and `creativity-engine`.
4. Month 3+: add `knowledge-ops`, `harness-engineering`, and `agentic-engineering`.
5. Multi-agent scale: add `agent-teams-command` and `project-flow-ops`.

## Grounding Principles

### Karpathy LLM OS
LLM=CPU · Context=RAM · Storage=Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes

### 3B Creativity Algorithms
- **Bending**: Mutate existing success patterns into new contexts
- **Breaking**: Eliminate worst-performing patterns; break path dependency
- **Blending**: Fuse elements from different domains for novel patterns

### Agent Teams

When the runtime exposes isolated workers, use `agent-teams-command` for admission, ownership, IPC, integration, evidence, and cleanup. Do not bind the durable skill to a product version or model name.
