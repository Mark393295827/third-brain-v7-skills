# Third Brain V7 Skills — Installation & Usage Guide

> **19 profile-aware skills** for a persistent knowledge and agent execution system. Compatible with Claude Code, Codex CLI, Gemini CLI, Cursor, Windsurf, and other rule/context-based AI IDEs.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Platform Setup](#2-platform-setup)
3. [Quick Start Wizard](#3-quick-start-wizard)
4. [Skill Reference](#4-skill-reference)
5. [Workflow Scenarios](#5-workflow-scenarios)
6. [Daily Routine](#6-daily-routine)
7. [Advanced Configurations](#7-advanced-configurations)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Installation

### Prerequisites

- One supported AI coding tool: **Claude Code**, **Codex CLI**, **Gemini CLI**, **Cursor**, **Windsurf**, or another tool that can read project rules/context files
- **Git** (`git --version`)
- **Python 3.8+** (for linting, loop validation, token-cost utility, and optional vector adapters)
- **Obsidian** (recommended for wiki knowledge base)

### One-Line Install

```bash
# Clone the repository
git clone https://github.com/Mark393295827/third-brain-v5-skills.git
cd third-brain-v5-skills
bash install.sh
```

Explicit targets:

```bash
bash install.sh codex
bash install.sh claude
bash install.sh gemini
bash install.sh cursor
bash install.sh windsurf
bash install.sh all
```

### Install for Your Platform

#### Claude Code (Recommended)

```bash
# Personal skills (available across all projects)
cp -r skills/* ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/ | wc -l
# Expected output: 19
```

#### Codex CLI

```bash
mkdir -p ~/.agents/skills
cp -r skills/* ~/.agents/skills/
```

#### Gemini CLI

```bash
mkdir -p ~/.gemini/skills/
cp -r skills/* ~/.gemini/skills/
```

#### Cursor

Cursor support uses a project-rule adapter that routes requests to the `skills/*/SKILL.md` files kept in this repository.

```bash
mkdir -p .cursor/rules
cp adapters/cursor/third-brain-skills.mdc .cursor/rules/third-brain-skills.mdc
```

#### Windsurf / Cascade

Windsurf can use these as native workspace skills, with an optional routing rule.

```bash
mkdir -p .windsurf/skills .windsurf/rules
cp -r skills/* .windsurf/skills/
cp adapters/windsurf/third-brain-skills.md .windsurf/rules/third-brain-skills.md
```

For details, see [docs/compatibility.md](docs/compatibility.md).

#### Commands (Optional)

```bash
# Copy command files for token tracking
cp commands/* ~/.claude/commands/
```

---

## 2. Platform Setup

### 2.1 Agent Teams (Optional)

First inspect whether the installed runtime exposes isolated workers, task state, and integration controls. Product/version-specific flags belong in local runtime configuration, not durable skills. If workers are unavailable, use one agent plus an independent verifier.

Use `agent-teams-command` only after its admission gate shows that independent workstreams justify coordination and review cost.

### 2.2 Wiki Path Configuration

Skills read the default vault contract from `system/config.md`. If your Obsidian vault already has a different structure, copy that file into the vault and edit the path values before running write-heavy skills.

Create the default layout when starting a new vault:

```bash
mkdir -p {sources,wiki/{concepts,entities,atomic-notes,outputs,decisions,sops},maps,system/templates}
```

Minimum required variables:

| Variable | Default |
|---|---|
| `SOURCES_DIR` | `sources/` |
| `CONCEPTS_DIR` | `wiki/concepts/` |
| `ENTITIES_DIR` | `wiki/entities/` |
| `OUTPUTS_DIR` | `wiki/outputs/` |
| `SYSTEM_DIR` | `system/` |
| `LOG_FILE` | `system/log.md` |

### 2.3 Token Tracking (Optional)

```bash
# Create token log
touch .token-log.csv
echo "date,task,model_id,capability_class,input_tokens,cached_input_tokens,output_tokens,input_rate,cached_input_rate,output_rate,currency,cost,rate_source,notes" > .token-log.csv
```

### 2.4 Vector Search (Optional, for knowledge-ops)

```bash
pip install chromadb sentence-transformers watchdog
```

---

## 3. Quick Start Wizard

Run this sequence to verify everything works:

```bash
# Step 1: Verify skills are installed
claude "What skills do I have?"

# Step 2: Ingest a piece of knowledge
claude "I just read that Curiosity Rover found organic molecules on Mars. Ingest this into my wiki."

# Step 3: Run daily OKR
claude "Run my daily OKR."

# Step 4: Check wiki health
claude "Lint my wiki."

# Step 5: Create an agent team (if enabled)
claude "Create a team of 3 agents to research this topic."
```

---

## 4. Skill Reference

### 📥 Ingestion & Knowledge Pipeline

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **wiki-ingest** | Ingests sources with risk classification, macro-action scope, wiki pages, clipping archive, Karpathy understanding gate, governance notes, and post-ingest lint | "ingest this into my wiki" |
| **knowledge-ops** | Manages multi-layer knowledge; dedup, classify, preserve evidence hierarchy, use Markdown-first retrieval, vectorize optionally, and queue knowledge debt | "save this to my knowledge base" |
| **wiki-lint** | Health-check: P0/P1 graph health, source refs, frontmatter, links, provenance debt, clipping lifecycle, and understanding integrity | "lint my wiki" |

### 🔄 Daily Workflow

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **daily-okr** | 7-KR cycle: Input→Cognition→Wiki→Behavior→Creativity→Output→Feedback | "run my daily OKR" |
| **cognitive-compile** | 8-section deep learning compile: Question→Facts→Concepts→Patterns→Conflicts→Hypotheses→Decision→Action | "do a cognitive compile on X" |

### 🎨 Behavior & Creativity

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **behavior-design** | Convert outcomes into minimum behavior, cues, SOPs, evidence, recovery, and review | "design a habit for X" |
| **creativity-engine** | Generate mechanism-diverse options and falsifiable minimum experiments | "generate ideas about X" |

### 🔬 Research & Quality

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **deep-research** | Research harness with preflight, source/claim ledgers, activity trace, citations, privacy checks, and STOW handoff | "research X for me" |
| **verify-before-claim** | No completion claims without fresh verification evidence | "verify before I ship" |

### 🔄 Learning & Flow

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **session-learn** | Extract 7 knowledge signals from sessions. Closure Protocol | "extract what we learned" |
| **project-flow-ops** | Triage, plan, track, review across projects | "triage my tasks" |

### 📊 Context & Cost

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **context-manager** | Runtime budgets, checkpoint replay, compaction, retrieval, capability routing | "I'm hitting context limits" |

`token-cost-tracker` is a utility command under `commands/`, not an Agent Skill.

### 🏗️ Engineering

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **loop-engineering** | Designs bounded Goal/Loop/Automation/AutoResearch contracts with state and recovery | "turn this into a verified loop" |
| **agentic-engineering** | Refactors workflows into spec-driven macro actions with quality ceilings, delegated-action boundaries, autonomy defaults, write-back, and verification | "make this workflow more agentic" |
| **harness-engineering** | Agent runtime kernel: permissions, tools as system calls, delegated-action gates, provenance ledgers, observability, recovery, adversarial review | "how do I make this agent safe?" |
| **agent-teams-command** | Multi-agent macro action orchestration with ownership, IPC, async budget envelopes, integration, cleanup, evidence gates, and red-team review | "create an agent team to build X" |

### 💼 Strategy & Operations

| Skill | What It Does | Trigger Phrase |
|-------|-------------|----------------|
| **startup-evaluation** | Startup health diagnosis: customer pain, market, PMF, team, unit economics, runway, VC 5T, and next cheapest test | "evaluate this startup" |
| **anthropic-os** | Self-evolving work method engine. CASH, 70/30, hive mind, 3B algorithms | "launch Anthropic OS" |
| **ai-six-sigma-property-os** | AI + Ontology + DMAIC Black Belt model for property work orders, dispatch, quotes, evidence, CTQ metrics, and quality dashboards | "design my Property Agent OS" |

---

## 5. Workflow Scenarios

For copyable, standalone workflow files, see [examples/](examples/). The recommended starting workflows are:

| Workflow | Example File | Best Skill Entry |
|----------|--------------|------------------|
| 3-minute source ingest | [examples/3-minute-quickstart.md](examples/3-minute-quickstart.md) | `wiki-ingest` |
| Research PDF to wiki brief | [examples/research-pdf-to-wiki.md](examples/research-pdf-to-wiki.md) | `wiki-ingest` + `cognitive-compile` |
| Deep research to STOW handoff | [examples/deep-research-stow-handoff.md](examples/deep-research-stow-handoff.md) | `deep-research` + optional `wiki-ingest` |
| Verified code session | [examples/verified-code-session.md](examples/verified-code-session.md) | `verify-before-claim` |
| Daily knowledge loop | [examples/daily-knowledge-loop.md](examples/daily-knowledge-loop.md) | `daily-okr` |
| Startup evaluation sprint | [examples/startup-evaluation-sprint.md](examples/startup-evaluation-sprint.md) | `startup-evaluation` |

### Scenario 1: Knowledge Capture & Compounding

**Goal**: Capture an article, understand it deeply, and make the knowledge compound.

```
Step 1 — Ingest:
  "I just read a fascinating article about AlphaFold 3.
   Ingest it into my wiki."

Step 2 — Deep Understanding:
  "Run a cognitive compile on AlphaFold 3's impact on drug discovery."

Step 3 — Behavioral Action:
  "Design a habit to follow AI-in-biology news weekly."

Step 4 — Generate Ideas:
  "Use the creativity engine to generate 5 startup ideas at the
   intersection of AI and protein folding."

Step 5 — Extract Learning:
  "Extract what we learned from this session."
```

### Scenario 2: Full-Stack Development Sprint

**Goal**: Build a feature with an agent team.

```
Step 1 — Plan with Context:
  "I'm building a CLI tool for tracking TODO comments.
   Run a cognitive compile on the best architecture."

Step 2 — Create Agent Team:
  "Create a team of 3 teammates and route them by implementation,
   domain, and independent-evaluation capability.
   Teammate 1: Frontend (React).
   Teammate 2: Backend (FastAPI).
   Teammate 3: QA (Playwright tests).
   Build me a working prototype."

Step 3 — Quality Check:
  "Verify before I ship: run tests and check for edge cases."

Step 4 — Document:
  "Save the architecture decisions to my wiki."
```

### Scenario 3: Startup Evaluation

**Goal**: Evaluate a startup idea systematically.

```
Step 1 — Market Analysis:
  "Run a cognitive compile on the AI-powered legal tech market."

Step 2 — Startup Evaluation:
  "Evaluate this startup idea:
   An AI that automates contract review for small businesses.
   Use the startup-evaluation framework."

Step 3 — Research:
  "Use deep-research to analyze existing competitors in AI legal tech.
   Include source access, claim ledger, activity trace, and STOW handoff."

Step 4 — Strategy:
  "Launch anthropic-os. Evaluate this idea using 70/30 allocation.
   What's the Big Bet vs BAU growth strategy?"
```

### Scenario 4: Marketing Campaign Design

**Goal**: Design and execute a marketing campaign.

```
Step 1 — Research:
  "Use deep-research on latest trends in AI marketing automation.
   Run the preflight, source ledger, claim ledger, and activity trace."

Step 2 — Creativity:
  "Generate 10 campaign ideas combining AI and emotional storytelling."

Step 3 — Behavior Design:
  "Design a daily content creation habit."

Step 4 — Knowledge Capture:
  "Extract what we learned. Save the winning ideas to my wiki."
```

### Scenario 5: Startup Evaluation Sprint

**Goal**: Turn an early idea into an evidence map and validation plan.

```
Step 1 — Frame the Idea:
  "Use startup-evaluation on this idea:
   An AI coach that turns reading notes into daily behavior experiments."

Step 2 — Separate Facts from Assumptions:
  "List what we know, what we assume, and what would kill the idea."

Step 3 — Define the Cheapest Test:
  "Design a 7-day validation test with one target customer segment,
   one success metric, and one interview script."

Step 4 — Preserve Learning:
  "Use session-learn to save the decision, assumptions, and next test
   into my wiki."
```

---

## 6. Daily Routine

### Morning Session (15 min)

```
1.  "Run my daily OKR."
    └── KR1: Input → Scan 3 high-quality sources
    └── KR2: Cognition → Extract 1 key insight
    └── KR3: Wiki → Save insight to wiki
    └── KR4: Behavior → Plan 1 action ≤15 min
    └── KR5: Creativity → 1 new idea
    └── KR6: Output → 1 reusable artifact
    └── KR7: Feedback + Stop Doing List (Buffett/Munger)
```

### Deep Work Session (2-4 hours)

```
1. "Run a cognitive compile on [topic]."
2. "Research [topic] with deep-research, including source boundary,
    claim ledger, activity trace, and STOW handoff if durable."
3. "Ingest findings into wiki."

For complex build tasks:
4. "Create an agent team to build [feature]."
5. "Verify before I ship."

For strategic decisions:
6. "Launch anthropic-os for this decision."
```

### Evening Review (10 min)

```
1. "Extract what we learned from today."
2. "Update project status with project-flow-ops."
3. "Estimate token cost for tomorrow's planned tasks."
```

---

## 7. Advanced Configurations

### 7.1 Capability Routing by Task

| Task | Required capability | Runtime preference |
|------|---------------------|-------------------|
| Daily OKR | Structured extraction, low latency | Lowest-cost capable route |
| Cognitive Compile | Deep reasoning, evidence separation | Reasoning route with adequate context |
| Wiki Ingest | File/tool use, structured output | Reliable tool-use route |
| Agent Teams | Role-specific capability plus independent evaluator | Smallest justified team |
| Deep Research | Search, synthesis, citation discipline | Research-capable route with current access |
| Creativity Engine | Divergence plus constraint evaluation | Fast route unless domain risk is high |
| Token Estimation | Arithmetic or deterministic calculator | Script/tool before a model |

### 7.2 Runtime Settings

Discover team, sandbox, connector, and approval settings from the installed runtime. Keep product/version-specific flags in local configuration, not durable skills; verify the feature is active before claiming workers were launched.

### 7.3 Git Hooks Integration

```bash
# Post-commit hook: auto-lint wiki
cat > .git/hooks/post-commit << 'EOF'
claude "Lint my wiki after this change."
EOF
chmod +x .git/hooks/post-commit
```

### 7.4 Token Budget Management

```bash
# Estimate before expensive tasks
claude "Estimate token cost for a cognitive compile on this 50-page PDF."

# Log after tasks
claude "Log this task: cognitive-compile, runtime-model-id, 150K input, 35K output, using today's billing rates."

# Weekly report
claude "Generate my weekly token report."
```

---

## 8. Troubleshooting

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| Skill not found | Skills not copied to correct directory | Run `cp -r skills/* ~/.claude/skills/` |
| Agent Teams not working | Runtime lacks workers or team mode is disabled | Inspect current runtime capabilities/settings; use one process if unavailable |
| Token cost too high | Capability route or context scope is oversized | Use runtime pricing plus context-manager budget and compaction rules |
| Wiki links broken | Wiki structure not set up or config paths mismatch | Check `system/config.md`, then create the configured concept/entity folders. |
| Vector search failing | ChromaDB not installed | `pip install chromadb sentence-transformers` |
| Session-learn empty | No reusable, source-grounded delta exists | Return no-op evidence or provide the missing session artifact |
| Cognitive compile too long | Question or source boundary is too broad | Narrow the decision question and preserve source locators |
| LLM context full | No truncation strategy | Use context-manager to budget and trim |

### Quick Diagnostics

```bash
# Check skills installed
ls ~/.claude/skills/

# Verify Claude Code version
claude --version

# Check settings
cat ~/.claude/settings.json | grep agentTeams

# Check token log
cat .token-log.csv | tail -5
```

---

## Appendix: Skill Interaction Map

```
                    ┌──────────────────┐
                    │   External       │
                    │   Sources        │
                    └────────┬─────────┘
                             ▼
              ┌──────────────────────────┐
              │    wiki-ingest            │◄── daily-okr (KR1)
              │    knowledge-ops          │
              └──────┬──────────┬────────┘
                     │          │
              ┌──────▼          └──────────┐
              │  Knowledge Layers           │
              │  ├ wiki-lint (health check) │
              │  └ session-learn (extract)  │
              └─────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        ▼            ▼            ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ daily-okr   │ │cognitive │ │ behavior │ │ creativity   │
│ (7 KR loop) │ │-compile  │ │ -design  │ │ -engine      │
│ + evidence  │ │ 8 parts  │ │ + review │ │ + experiments│
└─────────────┘ └──────────┘ └──────────┘ └──────────────┘
        │            │            │              │
        └────────────┼────────────┼──────────────┘
                     ▼
    ┌───────────────────────────────────────────────┐
    │ verify-before-claim   ← quality gate          │
    │ deep-research         ← synthesis             │
    │ project-flow-ops      ← execution             │
    │ loop-engineering      ← bounded execution     │
    │ context-manager       ← context optimization  │
    │ harness-engineering   ← agent infrastructure  │
    └───────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐         ┌─────────────────┐
│ agent-teams  │         │ anthropic-os    │
│ -command     │         │ + CASH + 3B     │
│ (fleet ops)  │         │ + Predictive    │
└──────────────┘         │   Coding        │
                         └─────────────────┘
```

---

> **Next**: Open Claude Code and say: "Run my daily OKR."
