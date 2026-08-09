# Third Brain V7.2 / V5.0 Skills

<p align="center">
  <img src="assets/third-brain-v5-system-architecture.png" alt="Third Brain V7 knowledge OS architecture: LLM, Skills, Obsidian, behavior design, creativity engine, governance, and compounding loops" width="600">
</p>

**Verification-first Agent Skills for Claude Code, Codex, Gemini, Cursor, and Windsurf.** Build a persistent knowledge operating system with Obsidian provenance, scheduled loops, bounded static dependency graphs, context management, and multi-agent orchestration.

Install 20 reusable agent skills for ingesting sources, compiling interlinked wikis, running daily knowledge loops, verifying claims before shipping, managing token costs, engineering bounded loops and static dependency graphs, and orchestrating multi-agent teams.

**Use this if:**
- Your AI agent keeps forgetting context between sessions
- You want to enforce verification gates before "done" claims
- You need to structure knowledge as linked pages (like Obsidian) instead of scattered chat history
- You're building agent workflows that should learn and compound over time
- You want Obsidian wiki knowledge to update skills, SOPs, schemas, and automation through supervised promotion gates

[![GitHub stars](https://img.shields.io/github/stars/Mark393295827/third-brain-v5-skills?style=social)](https://github.com/Mark393295827/third-brain-v5-skills/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-Rules%20Compatible-111827)](GUIDE.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Mark393295827/third-brain-v5-skills.git
cd third-brain-v5-skills
bash install.sh claude  # or: codex, gemini, cursor, windsurf, all
```

Windows PowerShell uses `.\install.ps1 claude` with the same target names.

### 2. Try a Skill

Paste this into Claude Code or your agent:

```text
Use wiki-ingest on this source. Create source notes, concept pages, entity pages, navigation updates, and a verification summary.
```

Then paste a URL, article, PDF text, or any source you want to capture.

### 3. Next Steps

See the **[3-Minute Quickstart](examples/3-minute-quickstart.md)** for a complete walkthrough.

Full guide: **[GUIDE.md](GUIDE.md)**

中文进阶手册：**[V7 最大潜力使用手册](docs/v7-max-potential-guide-zh.md)**

---

## The Problem

| Scenario | Before | After |
|----------|--------|-------|
| **Research PDF** | Summarized once, then forgotten | `wiki-ingest`: source notes, concept pages, linked wiki |
| **Coding session** | Agent: "I fixed it" (no proof) | `verify-before-claim`: requires test output + exit code before any claim |
| **Daily work** | Tasks and ideas scatter across chat | `daily-okr`: one insight, one wiki update, one action, one output, daily score |

---

## V7 Operating Model

V7 keeps the wiki as durable disk and governance, then gives every skill a profile-aware execution contract:

```text
Input -> Source -> Wiki compile -> Daily loop -> Agent/Wiki flywheel -> Skill/SOP upgrade -> Verification
```

The upgrade adds seven hard defaults:

- **Profiles match risk**: one-shot, stateful, loop, and high-risk work load only the controls they need.
- **Source provenance stays immutable**: raw source notes and block refs remain the audit layer.
- **Loops have contracts**: Trigger -> Execute -> Verify -> State, with budgets and recovery.
- **Context is zero-overhead by default**: hot paths load only what the task needs.
- **Automation is bounded**: scans and queues can run unattended; semantic writes stay supervised.
- **Teams need ownership**: multi-agent work requires write scopes, IPC, join gates, cleanup, and evidence.
- **Rules promote through evidence**: wiki insights become schema or skill rules only after repeated support and a cheap check.

See [V7 release notes](docs/release-notes-v7.md) and the [Agent Skills standard](docs/agent-skills-standard.md).

V7.1 adds `graph-engineering` as the 20th skill. It supports bounded static DAGs only; dynamic expansion and cyclic graphs remain out of scope.

---

## Core Skills (Start Here)

### 🧠 **Knowledge & Verification**

| Skill | What it does |
|-------|-------------|
| **[wiki-ingest](skills/wiki-ingest/SKILL.md)** | Preserve an immutable source, compile linked understanding, enforce promotion boundaries, and verify every touched file. |
| **[verify-before-claim](skills/verify-before-claim/SKILL.md)** | **Iron rule**: no completion claim without fresh, scope-matched evidence; consequential actions also require independent verification, approval, and rollback. |

### 📅 **Daily Loop**

| Skill | What it does |
|-------|-------------|
| **[daily-okr](skills/daily-okr/SKILL.md)** | Execute a 7-KR cycle: Input → Cognition → Wiki → Behavior → Creativity → Output → Feedback, with an artifact or receipt for every completed KR. |

### 🎯 **Behavior & Creativity**

| Skill | What it does |
|-------|-------------|
| **[behavior-design](skills/behavior-design/SKILL.md)** | Turn outcomes into observable minimum behavior, cues, SOPs, recovery, evidence, and review. |
| **[creativity-engine](skills/creativity-engine/SKILL.md)** | Generate mechanism-diverse options, rank evidence gaps, and define three bounded minimum experiments. |

### 🔬 **Research & Quality**

| Skill | What it does |
|-------|-------------|
| **[deep-research](skills/deep-research/SKILL.md)** | STOW-compatible research harness with evidence trails, source/claim ledgers, privacy checks, and direct handoff to wiki-ingest. |
| **[session-learn](skills/session-learn/SKILL.md)** | Extract knowledge patterns from sessions — concepts, entities, corrections, patterns, ideas, decisions, gaps. Closure protocol ensures learning feeds back into the wiki. |

### 📊 **Context & Engineering**

| Skill | What it does |
|-------|-------------|
| **[context-manager](skills/context-manager/SKILL.md)** | Derive budgets at runtime, checkpoint state, compact with KEEP/SUMMARIZE/DROP/RETRIEVE, and route by capability. |
| **[loop-engineering](skills/loop-engineering/SKILL.md)** | Control temporal depth: turn repeatable work into a bounded Trigger -> Execute -> Verify -> State loop with durable state, finite budgets, and explicit stop/recovery rules. |
| **[graph-engineering](skills/graph-engineering/SKILL.md)** | Control dependency width: validate bounded static DAGs with explicit dependencies, independent branches, typed joins, and node-local recovery. |
| **[agentic-engineering](skills/agentic-engineering/SKILL.md)** | Design agent workflows as spec-driven macro actions with quality ceilings, verification gates, delegated-action boundaries, and state checkpoints. |
| **[harness-engineering](skills/harness-engineering/SKILL.md)** | Provide the runtime scheduler, permissions, leases, tools, provenance, and observability needed to execute agent workflows safely. |
| **[agent-teams-command](skills/agent-teams-command/SKILL.md)** | Admit and command multi-agent processes with exclusive ownership, typed IPC, isolated writes, serial integration, evidence, and cleanup. |

---

## Complete Skill List

### 📥 Ingestion & Knowledge

- `wiki-ingest` — Ingest sources with source-risk taxonomy, Karpathy understanding gate, concept/entity pages, wikilinks
- `knowledge-ops` — Multi-layer knowledge management: classify, deduplicate, preserve evidence hierarchy, vector + Markdown retrieval
- `wiki-lint` — Health check: P0/P1 graph health, frontmatter, source refs, wikilink density, provenance debt

### 🔄 Daily Workflow

- `daily-okr` — 7-KR evidence cycle with minimum-day degradation and durable closeout
- `cognitive-compile` — 8-section framework: Question → Facts → Concepts → Pattern Recognition → Conflict Detection → Hypothesis Generation

### 🎨 Behavior & Creativity

- `behavior-design` — Outcome → minimum behavior → cue → SOP → evidence → review
- `creativity-engine` — Mechanism-diverse combinations, scoring, and falsifiable minimum tests

### 🔬 Research & Quality

- `deep-research` — STOW-compatible research harness, evidence trails, source/claim ledgers
- `verify-before-claim` — Fresh scope-matched evidence, independent checks, approval, rollback

### 🔄 Learning & Flow

- `session-learn` — 7 signal types: concepts, entities, corrections, patterns, ideas, decisions, gaps
- `project-flow-ops` — Execution flow: triage, plan, track, review across projects

### 📊 Context

- `context-manager` — Runtime budgets, checkpoint replay, compaction, retrieval, capability routing

Utility command: `commands/token-cost-tracker.md` estimates, logs, and reports token usage; it is not one of the 20 Agent Skills.

### 🏗️ Engineering

- `loop-engineering` — Temporal depth through bounded loop contracts, independent verification, finite budgets, and stop/recovery rules
- `graph-engineering` — Dependency width through bounded static DAGs, explicit branches, typed joins, and node-local recovery
- `agentic-engineering` — Spec-driven macro actions, quality ceilings, verification gates, state checks
- `harness-engineering` — Runtime scheduler, permissions, system-call tools, delegated gates, provenance, observability
- `agent-teams-command` — Multi-agent process ownership, IPC, integration, async budgets, and evidence gates

### 💼 Strategy & Operations

- `startup-evaluation` — Startup health: entrepreneurship, VC 5T, PMF, runway, team, unit economics
- `anthropic-os` — Governed operating-system experiments: Four-C, 3B, prediction errors, permission ladder
- `ai-six-sigma-property-os` — AI + Ontology + DMAIC for property work orders, dispatch, quotes, evidence

---

## How These Skills Fit Together

```
                        LLM (CPU) + Context (RAM) + Wiki (Disk)

External Sources ──→ wiki-ingest + knowledge-ops ──→ Knowledge Layers
                            ↓
                    Daily Loop (daily-okr)
                    /    /    \    \    \
               Input  Cognition  Wiki  Behavior  Creativity
                            |
                        Output → Feedback
                            ↓
                    session-learn (extract patterns)
                            ↓
                    verify-before-claim (quality gate)
                             ↓
             Loop depth / Graph dependency width
                             ↓
                Multi-agent teams (agent-teams-command)
```

The system is a **closed loop**: ingest sources → process daily → extract learning → verify claims → promote rules → scale to teams.

---

## Architecture & Design

**Third Brain V7 treats agents as LLM OS processes:**
- LLM = CPU
- Context = RAM
- Wiki/Obsidian = Disk
- Tools = System calls
- Skills = Executable programs
- Harness = Kernel
- Agent teams = Processes

### Design Layers

| Layer | Principle | Skills |
|-------|-----------|--------|
| **🧠 Knowledge OS** | Capture, structure, lint, and promote knowledge over time | wiki-ingest, knowledge-ops, wiki-lint |
| **⚡ Daily Loop** | Close the knowledge-to-action cycle every day | daily-okr, cognitive-compile |
| **🎯 Behavior & Creativity** | Turn knowledge into habits and novel ideas | behavior-design, creativity-engine |
| **🔬 Research & Quality** | Verify before claiming, research with rigor | deep-research, verify-before-claim |
| **🔄 Continuous Learning** | Extract patterns from every session | session-learn, project-flow-ops |
| **📊 Context** | Manage hot context, durable checkpoints, and runtime budgets | context-manager |
| **🏗️ Engineering** | Design bounded loops, static dependency graphs, harnesses, agent workflows, and multi-agent systems | loop-engineering, graph-engineering, agentic-engineering, harness-engineering, agent-teams-command |
| **💼 Strategy & Operations** | Evaluate startups, design AI quality systems | startup-evaluation, anthropic-os, ai-six-sigma-property-os |

Engineering boundaries are deliberate: Loop Engineering controls temporal depth; Graph Engineering controls dependency width; Agent Teams Command controls process ownership, IPC, and integration; Harness Engineering supplies the runtime scheduler, permissions, and observability. A graph node may contain a Loop or Agent Team, but V7.1 does not support dynamic or cyclic graphs.

---

## Skill Adoption Path

Start small. Add skills as you need them.

| Stage | Core Skills | Unlock When |
|-------|------------|-------------|
| **Week 1** | `wiki-ingest` + `verify-before-claim` | You can ingest 1 source/day + every claim has fresh evidence |
| **Weeks 2-4** | + `daily-okr` + `session-learn` | Daily artifacts and verified learnings feed back to the wiki |
| **Month 2+** | + `cognitive-compile` + `behavior-design` + `creativity-engine` | Wiki has 50+ pages or repeated decisions need synthesis |
| **Month 3+** | + `knowledge-ops` + `loop-engineering` + `harness-engineering` + `agentic-engineering` | Retrieval, looping reliability, permissions, or delegated actions become bottlenecks |
| **Dependency graph** | + `graph-engineering` after `loop-engineering` | Explicit dependencies, independent branches, typed joins, or node-local recovery create more value than orchestration and review cost |
| **Multi-agent** | + `agent-teams-command` + `project-flow-ops` | Work splits into separate owners with clear integration gates |
| **Strategy** | + `startup-evaluation` + `anthropic-os` + `deep-research` | Need startup health, market, operating-system decisions |
| **Operations** | + `ai-six-sigma-property-os` | Need measurable service quality, dispatch, evidence loops |

---

## Installation

### For Claude Code

```bash
# Personal skills (available across all projects)
bash install.sh claude
```

### For Cursor

```bash
bash install.sh cursor
```

### For Windsurf

```bash
bash install.sh windsurf
```

### For Codex CLI / Gemini CLI

```bash
bash install.sh codex
bash install.sh gemini
```

Full guide: **[GUIDE.md](GUIDE.md)**

---

## Example Workflows

Each workflow is copyable into your agent. See **[examples/](examples/)** for complete, verified examples:

- [3-minute quickstart](examples/3-minute-quickstart.md) — Fastest path to useful output
- [Research PDF to wiki](examples/research-pdf-to-wiki.md) — Turn a source into linked pages
- [Verified code session](examples/verified-code-session.md) — Use verification gates before claiming a fix
- [Daily knowledge loop](examples/daily-knowledge-loop.md) — Run a compact daily OKR workflow
- [Startup evaluation sprint](examples/startup-evaluation-sprint.md) — Turn an idea into validated assumptions

---

## Wiki Structure

Skills default to STOW paths (configurable via `system/config.md`):

```
sources/          ← Immutable source notes (articles, PDFs, transcripts)
wiki/
├── concepts/     ← Ideas, frameworks, methods
├── entities/     ← People, companies, products
├── atomic-notes/ ← Single-fact notes
├── outputs/      ← Reusable reports, analyses
├── decisions/    ← Architecture decisions
└── sops/         ← Standard operating procedures
system/           ← Config, log, schema, templates
08_behaviors/     ← Behavior system (goals, habits, reviews)
09_creativity/    ← Creativity system (ideas, experiments)
```

---

## Tools & References

| Resource | Purpose |
|----------|---------|
| [tools/index.html](tools/index.html) | Visual skill navigator and dashboard |
| [tools/token-calculator.html](tools/token-calculator.html) | Token cost calculator |
| [GUIDE.md](GUIDE.md) | Full installation & troubleshooting |
| [V7 最大潜力使用手册](docs/v7-max-potential-guide-zh.md) | Profile、知识飞轮、Agent 工程、治理和 30 天采用路径 |
| [CLAUDE.md](CLAUDE.md) | Claude Code setup |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute skills |

---

## What This Is NOT

- **Not a chat wrapper.** Skills are executable prompts that agents follow; they're not productivity theater.
- **Not a productivity tool with 100 metrics.** Daily OKR has seven causally linked KRs with evidence.
- **Not an all-in-one framework.** Pick skills incrementally. You don't need all 20 to start.
- **Not prescriptive.** Adapt paths, frontmatter, and skill triggers to your workflow.

---

## Philosophy

**Three core principles:**

1. **Verification first**: No "done" without proof. No claims without evidence. Expected value over confidence.
2. **Knowledge compounds**: Every session should improve the wiki, not scatter across chat history.
3. **Closed loops**: Ingest → Process → Learn → Scale → Verify. No loose ends.

---

## Related Work

- [Agent Skills Format](https://agentskills.io) — Open specification for agent skills
- [llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — Original STOW pattern implementation by SamurAIGPT
- [Karpathy LLM OS](https://karpathy.ai) — Conceptual framework

---

## Contributing

Bug reports, skill improvements, and PRs are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT — see [LICENSE](LICENSE).

---

## Transparency Note

This project includes **growth and outreach tools** (in `tools/` and `outreach/`) designed to help the repository reach users via GitHub search and Awesome lists. These tools are optional, dry-run-by-default, and separate from the core skills. If you're installing skills for your own workflow, you don't need them.

The skill frameworks and philosophy are genuine. Use what works for you; ignore what doesn't.
