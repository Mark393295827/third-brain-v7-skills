---
title: "Third Brain V7.2 / V5.0 Path & Taxonomy Configuration"
type: system-config
updated: "2026-07-31"
version: "7.2.0"
status: active
---

# Third Brain V7.2 / V5.0 Path & Taxonomy Configuration

This document defines the authoritative path and taxonomy contracts for skills reading from or writing to the Obsidian vault (`C:\Users\高杰\Documents\Obsidian Vault`).

---

## 1. Vault Directory Contracts

| Variable | Base Path | Taxonomy Subdirectories | Purpose |
|---|---|---|---|
| `VAULT_ROOT` | `.` | — | Root directory for the active Obsidian vault. |
| `SOURCES_DIR` | `sources/` | `YYYY-MM/`, `pre-2026/`, `books/` | Immutable source notes, clippings, and books (>100KB). |
| `WIKI_DIR` | `wiki/` | — | Living synthesis pages and structured knowledge. |
| `CONCEPTS_DIR` | `wiki/concepts/` | 13 Domain Subdirectories (see Section 2) | Concept, framework, method, and theory notes. |
| `ENTITIES_DIR` | `wiki/entities/` | 5 Category Subdirectories (see Section 3) | People, company, fund, product, and organization notes. |
| `OUTPUTS_DIR` | `wiki/outputs/` | `gmail-digests/`, `evaluations/`, `compilations/` | Reusable briefs, evaluations, playbooks, and analyses. |
| `DECISIONS_DIR` | `wiki/decisions/` | — | Architecture and strategy decision records. |
| `SOPS_DIR` | `wiki/sops/` | — | Standard operating procedures. |
| `MAPS_DIR` | `maps/` | `domain-mocs/`, `system-indexes/`, `project-maps/`, `canvases/` | Maps of Content, system dashboards, and visual graphs. |
| `SYSTEM_DIR` | `system/` | `logs/`, `templates/`, `scripts/`, `assets/`, `references/` | Governance, path config, log archives, and scripts. |
| `LOG_FILE` | `system/log.md` | — | Append-only active log (current quarter entries only). |
| `LOG_ARCHIVE` | `system/logs/log-archive-historical.md` | — | Archived historical log entries (Batches 1–130). |
| `LINT_REPORT_FILE`| `system/lint-report.md` | — | Latest wiki health and link lint report. |

---

## 2. Concept Domain Taxonomy (`wiki/concepts/`)

All concept notes must be placed into one of the following 13 domain subdirectories based on their primary subject matter:

```
wiki/concepts/
├── ai-engineering/        # Agentic AI, Loop Engineering, Harness, Claude Code, SDLC, Graph Engineering, MCP
├── ai-economics/          # Tokenomics, CapEx, Compute, Data Centers, GPUs, Cloud Infrastructure, Hardware
├── ai-science/            # AGI, Interpretability, World Models, RL, Distillation, Pre-Training, Test-Time
├── behavioral-econ/       # Kahneman, Nudges, Decision Frameworks, Cognitive Friction, Mental Models, Bias
├── business-strategy/     # Moats, 7 Powers, Competitive Strategy, Pricing, Disruption, Operating Leverage
├── entrepreneurship/      # Startups, PMF, GTM, Founder Operations, Company Building, Scaling
├── general-concepts/      # Multidisciplinary core concepts, general mental models
├── geopolitics-energy/    # Semiconductors, Export Controls, Nuclear/SMR, Power Grid, Critical Minerals
├── identity-culture/      # Philosophy, Sociology, Education, Human Relationships, Storytelling, Civics
├── investing-macro/       # Fed, FOMC, Bonds, Housing, Inflation, Interest Rates, Liquidity, Debt Cycles
├── investing-quant/       # Quantitative Trading, Factor Investing, Smart Beta, Signal-to-Noise, Portfolio Risk
├── investing-vc/          # VC Frameworks, Private Equity, Term Sheets, Deal Sourcing, Valuation, Pitching
└── knowledge-systems/     # PARA, Second Brain, LLM Wiki, Obsidian, STOW/CODE Pipelines, Knowledge Ops
```

---

## 3. Entity Category Taxonomy (`wiki/entities/`)

All entity notes must be placed into one of the following 5 category subdirectories:

```
wiki/entities/
├── people/          # Individuals, founders, researchers, authors, investors (e.g. Dario Amodei, Jensen Huang)
├── companies/       # Tech companies, startups, enterprises (e.g. Anthropic, SpaceX, Tesla, Nvidia)
├── funds-investors/ # Venture capital funds, PE firms, hedge funds, endowments (e.g. Sequoia, Benchmark, a16z)
├── products/        # AI products, models, tools, developer platforms (e.g. Claude Code, Cursor, NotebookLM)
└── orgs/            # Universities, government bodies, research institutes (e.g. Stanford, NASA, WEF, CFTC)
```

---

## 4. Source Taxonomy (`sources/`)

All source clipping notes and transcripts must be placed into chronological or size-based subdirectories:

```
sources/
├── 2026-07/    # July 2026 sources & clippings
├── 2026-06/    # June 2026 sources & clippings
├── 2026-05/    # May 2026 sources & clippings
├── 2026-04/    # April 2026 sources & clippings
├── pre-2026/   # Pre-2026 historical sources (2011–2025)
└── books/      # Full-length books, whitepapers, and long-form sources (>100KB)
```

---

## 5. Output Taxonomy (`wiki/outputs/`)

```
wiki/outputs/
├── gmail-digests/   # Periodic unread email MECE pyramid summaries
├── evaluations/     # 5T evaluations, architecture benchmarks, VC audits
└── compilations/    # Cognitive compiles, synthesis playbooks, booklists
```

---

## 6. Resolution & Writing Rules

1. **Path Resolution:** Skills writing new concept or entity notes MUST resolve the exact subfolder using the taxonomy rules above.
2. **Immutable Sources:** Never modify files in `sources/` after creation unless explicitly requested to fix a transcript error.
3. **Log Rotation:** Keep `system/log.md` under 100 KB. Archive entries older than 30 days to `system/logs/log-archive-historical.md`.
4. **Wikilink Resolution:** Wikilinks in Obsidian automatically resolve across subdirectories (e.g., `[[Dario Amodei]]` links to `wiki/entities/people/Dario Amodei.md`). Absolute relative links in system indexes should use explicit paths.
