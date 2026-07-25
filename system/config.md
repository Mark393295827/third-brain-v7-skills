---
title: "Third Brain V7 Path Configuration"
type: system-config
updated: "2026-05-22"
status: default
---

# Third Brain V7 Path Configuration

This file is the default path contract for skills that read from or write to a wiki vault. Projects may override these values in their local `system/config.md`, `CLAUDE.md`, or equivalent agent rules file.

## Vault Paths

| Variable | Default path | Purpose |
|---|---|---|
| `VAULT_ROOT` | `.` | Root directory for the active markdown/Obsidian vault. |
| `SOURCES_DIR` | `sources/` | Immutable source notes and provenance. |
| `WIKI_DIR` | `wiki/` | Living synthesis pages. |
| `CONCEPTS_DIR` | `wiki/concepts/` | Concept, framework, and method pages. |
| `ENTITIES_DIR` | `wiki/entities/` | People, company, product, and project pages. |
| `ATOMIC_NOTES_DIR` | `wiki/atomic-notes/` | Small single-claim knowledge atoms. |
| `OUTPUTS_DIR` | `wiki/outputs/` | Briefs, reports, reusable artifacts, and analyses. |
| `DECISIONS_DIR` | `wiki/decisions/` | Architecture and strategy decisions. |
| `SOPS_DIR` | `wiki/sops/` | Standard operating procedures. |
| `MAPS_DIR` | `maps/` | Maps of Content and navigation pages. |
| `SYSTEM_DIR` | `system/` | Logs, templates, lint reports, governance, and config. |
| `LOG_FILE` | `system/log.md` | Append-only operation log. |
| `LINT_REPORT_FILE` | `system/lint-report.md` | Latest wiki health report. |
| `BEHAVIORS_DIR` | `08_behaviors/` | Behavior systems, SOPs, and reviews. |
| `CREATIVITY_DIR` | `09_creativity/` | Ideas, experiments, and prototypes. |

## Resolution Rules

1. If a project has a local `system/config.md`, use its paths before the defaults above.
2. If a user provides an explicit vault path in the prompt, treat it as `VAULT_ROOT` for that run.
3. If a listed directory does not exist, create it only when the active skill is supposed to write there.
4. Never modify `SOURCES_DIR` files after creation unless the user explicitly asks for source correction.
5. When installed outside this repository, copy this file or declare equivalent variables in the agent's project rules.
