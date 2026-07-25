# Changelog

All notable changes to Third Brain V7 Skills are documented here.

This project follows a small-release rhythm: ship one focused release every 1-2 weeks when there are meaningful fixes, docs improvements, or skill updates.

## Unreleased

Current V7.1 baseline: 20 Agent Skills.

### Added
- `graph-engineering` for bounded static DAG admission, typed node/edge
  contracts, explicit joins, single-writer ownership, node-local recovery, and
  strict validation. It complements rather than replaces `loop-engineering`.
- A reproducible Loop-vs-Graph experiment with positive and negative admission
  fixtures, provenance hashes, independent review, and explicit claim limits.
- Non-empty `input`, `output`, `done`, and `non_goals` contracts across all
  skills, enforced by the repository linter.

### Fixed
- Installer copies now exclude `__pycache__`, `.pyc`, and `.pyo` artifacts across every skill target.
- Windows now has a native `install.ps1` path with the same targets and cache filtering as `install.sh`.
- Governance and release documentation now use the same lint, test, diff, and strict Loop validation gates as CI.
- Hook documentation now distinguishes non-shipped design examples from executable integrations.
- Graph strict validation now includes failure routes in DAG checks and binds external effects to exact approval scopes, direct human-gate receipts, allowed write targets, and compensation.
- Loop cap validation now rejects unbounded fallback language and parses compound budgets by their relevant units.

### Added
- `ai-six-sigma-property-os` skill for designing an AI + Ontology + DMAIC Black Belt operating model for property work orders, dispatch, quotes, evidence, CTQ dashboards, root-cause loops, and MVP quality control.
- ChatGPT Deep Research STOW comparison report and official-docs digest for testing `deep-research` against plan review, source control, activity trace, and safety behavior.
- GitHub deep-research top-5 digest translating high-star repository patterns into `deep-research` skill upgrades.
- AI workflow skill-iteration digest translating recent Obsidian AIOS, dynamic workflow, managed-agent, and self-compaction notes into repo skill updates.
- Karpathy wiki skill-audit digest translating LLM Wiki, macro actions, AutoResearch boundaries, and agentic education into concrete wiki skill rules.
- Wiki ingest governance digest translating recent Obsidian ingest logs, lint report, governance dashboard, and clipping queue rules into skill updates.
- Startup health framework digest translating Obsidian startup, VC, efficiency, and primary-investor maps into skill rules.
- Google I/O '26 agentic stack digest translating the latest Obsidian wiki ingest into full-stack agent design rules.
- Agent understanding framework wiki concept mapping Karpathy LLM OS ideas to Third Brain agent workflow, harness, and team design.
- Agent Skills open-format standard document and linter for validating skill folder shape, metadata, trigger descriptions, and quality gate sections.
- Agentic Engineering principles document translating spec-driven development, macro actions, security-aware integration, and AutoResearch boundaries into repo standards.
- Skill-level `assumes`, `conflicts_with`, and `## Success Metrics` contracts across all 19 skills.
- `system/config.md` as the default configurable vault path contract for wiki-writing skills.
- README skill adoption ladder that makes `wiki-ingest` + `verify-before-claim` the recommended first stage.

### Changed
- Entry docs, adapters, examples, dashboards, and token-cost benchmarks now describe the upgraded `deep-research` STOW handoff workflow consistently.
- `deep-research` now includes ChatGPT-style preflight, source-access boundaries, activity traces, STOW mapping, private-data safety checks, and wiki-ingest handoff packets.
- `deep-research` now supports research modes, source ledgers, claim ledgers, outline-first synthesis, recency/social signal handling, and Heavy mode gap-fill/adversarial loops.
- `agentic-engineering`, `harness-engineering`, `agent-teams-command`, `anthropic-os`, and `context-manager` now include workflow complexity gates, dynamic-workflow governance, AIOS 4C/Bike Method audits, managed-agent runtime separation, and long-horizon compaction contracts.
- `wiki-ingest`, `wiki-lint`, and `knowledge-ops` now apply a Karpathy-style understanding gate, Markdown-first retrieval default, macro-action scope contract, reusable workflow extraction, and objective-metric boundary for autonomous loops.
- `wiki-ingest`, `wiki-lint`, and `knowledge-ops` now include source-risk taxonomy, clipping lifecycle, targeted post-ingest lint, P0/P1 graph health gates, duplicate-source handling, provenance debt, and weak-link review queues.
- `startup-evaluation` now evaluates startup health with stage, evidence ladder, PMF/traction, unit economics, team/governance, runway, VC 5T, AI/hard-tech addendum, top-constraint diagnosis, and next-cheapest-test design.
- `agentic-engineering`, `harness-engineering`, `agent-teams-command`, and `verify-before-claim` now include full-stack agent surfaces: delegated actions, commerce mandates, generated-media provenance, ambient-device privacy, and single-source product claim rules.
- `agentic-engineering`, `harness-engineering`, and `agent-teams-command` now share a process/kernel/system-call mental model with explicit write-back and cleanup rules.
- README, GUIDE, and CLI entry docs now link or describe the expanded LLM OS architecture mapping.
- README and community discovery docs now include stronger launch/discovery paths for GitHub star conversion.
- Skill descriptions now use explicit `Use when` trigger language for better discovery under progressive disclosure.
- Core engineering skills now emphasize quality ceilings, macro action specs, adversarial review, and objective evaluation boundaries.
- Cursor, Windsurf, Codex, Claude, and Gemini routing docs now enforce assumptions, conflicts, success metrics, and path config before completion claims.
- Wiki examples and commands now refer to configurable path variables instead of hard-coded vault directories.
- The skill linter now requires `assumes`, `conflicts_with`, and `## Success Metrics`.

## v6.0 - 2026-06-27

### Added
- V6 knowledge operating system release notes translating Obsidian Agent/Wiki flywheel evidence into skill, SOP, schema, and automation promotion gates.
- Daily-loop aware operating model: input -> source -> wiki compile -> daily loop -> Agent/Wiki flywheel -> skill/SOP upgrade -> verification.
- V6 promotion gate for wiki insights: repeated durable support, bounded macro action, no provenance relaxation, and cheap objective check before rule promotion.

### Changed
- Core wiki skills now treat `input-skills-obsidian` as the front door of the V6 knowledge OS rather than a one-off importer.
- Core engineering skills now standardize Trigger -> Execute -> Verify -> State loops with hard budgets, recovery paths, independent evidence, and durable write-back.
- Harness and team skills now use zero-overhead context, MCP/Skills/Hooks selection, ownership, IPC, join gates, cleanup, and attention-budget controls as default constraints.

### Notes
- V6 does not rewrite historical V5 vault pages. Existing source notes remain immutable; historical structure debt stays in lint reports or review queues.

## v5.1 - 2026-05-14

### Added
- README-top system architecture infographic for the LLM + Skills + Obsidian integration.
- `agentic-engineering` skill for model-native workflow refactoring, autonomy defaults, state checkpoints, and verification gates.
- GitHub issue templates for bugs and skill requests.
- Pull request template with verification and changelog prompts.
- Release playbook for feedback triage and small-version cadence.
- Simplified README hero diagram.
- 3-minute quickstart prompt for `wiki-ingest`.
- Before/after usage cases in README.
- `examples/` workflows for ingest, verification, daily review, and Obsidian entry.
- Standard skill template reference.
- Cursor and Windsurf compatibility documentation and adapter templates.
- Fifth workflow example for startup evaluation.
- Animated-style install demo SVG and one-click test prompt.
- Community discovery checklist with recommended repository description, topics, and Awesome-list targets.
- V5.2 post-ingest closure rules for input taxonomy, behavior conversion, creativity conversion, and governance review.
- Architecture walkthrough example for the full LLM + Skills + Obsidian closed loop.

### Changed
- Public docs now describe the current 17-skill catalog.
- Cursor and Windsurf routers now cover knowledge ops, wiki lint, context management, agentic engineering, harness engineering, and Anthropic OS.
- Core engineering skills now use a standard `## Quality Gates` heading.
- README first screen now emphasizes value proposition, quick install, try-it prompts, and local demos.
- Each skill now includes a verified-effect statement in its usage template.
- Each skill now includes version, update date, and output example metadata.
- Dashboard now includes visual navigation shortcuts and skill search.
- `install.sh` now supports explicit `codex`, `claude`, `gemini`, `cursor`, `windsurf`, and `all` targets.
- `wiki-ingest`, `cognitive-compile`, and `creativity-engine` now align with the V5 architecture loop from source to behavior, creativity, and governance.

## Release Template

Use this shape for each release:

```markdown
## vX.Y.Z - YYYY-MM-DD

### Fixed
- Short description of the user-visible bug fix.

### Added
- Short description of the new skill, tool, example, or workflow.

### Changed
- Short description of documentation, naming, or behavior changes.

### Notes
- Upgrade or migration notes, if any.
```
