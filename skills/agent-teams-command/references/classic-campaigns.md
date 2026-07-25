# Agent Teams Classic Campaigns

Use these as copy-ready templates when `agent-teams-command` needs concrete multi-agent orders.

## Full-Stack System Development

```text
GOAL: Build a full-stack app (REST API + React) running on localhost.

ORDERS: Create a team of 3 teammates; route each by implementation/tool-use capability and runtime policy.

RISK BUDGET:
  Max blast radius: each teammate edits only its owned directory.
  Kill/downweight signals: repeated failing tests, API contract drift, or writes outside ownership.
  Rebalance: add QA critic or switch to sequential integration if contracts conflict.

TEAMMATE 1 (BACKEND)
  TASK: FastAPI + SQLite + REST endpoints
  OWNERSHIP: backend/
  BLAST RADIUS: backend/ only; no frontend edits
  DEPENDENCY: Notify FRONTEND when done

TEAMMATE 2 (FRONTEND)
  TASK: React frontend + API integration
  OWNERSHIP: frontend/
  BLAST RADIUS: frontend/ only; no backend edits
  DEPENDENCY: Wait for BACKEND's API spec

TEAMMATE 3 (QA)
  TASK: E2E tests + API tests
  OWNERSHIP: tests/
  BLAST RADIUS: tests/ and QA report only
  DEPENDENCY: Wait for all teammates

QUALITY GATES:
- All tests passing
- API response time <200ms
- No frontend console errors
```

## Technical Decision Research

```text
GOAL: Evaluate PostgreSQL -> MongoDB migration feasibility.

ORDERS: Create a team of 3 teammates; route each by deep-reasoning/research capability and runtime policy.

RISK BUDGET:
  Max blast radius: research artifacts only; no production data or schema writes.
  Kill/downweight signals: unverifiable claims, missing benchmark method, or migration-risk blind spot.
  Rebalance: add red-team review before any recommendation that changes production architecture.

TEAMMATE 1 (DATABASE)
  TASK: Query pattern analysis + performance benchmarks
  OWNERSHIP: research/performance/
  BLAST RADIUS: benchmark notes and reproducible scripts

TEAMMATE 2 (MIGRATION)
  TASK: Migration tool evaluation + downtime analysis
  OWNERSHIP: research/migration/
  BLAST RADIUS: migration notes only

TEAMMATE 3 (CRITIC)
  TASK: Challenge the first two teammates' conclusions
  OWNERSHIP: research/risks/
  BLAST RADIUS: risk review and counterarguments
  DEPENDENCY: Wait for DATABASE + MIGRATION to complete
```

## Security Audit And Fix

```text
GOAL: Find and fix all security vulnerabilities in the auth module.

ORDERS: Create a team of 2 teammates; route each by security-analysis or implementation capability.

RISK BUDGET:
  Max blast radius: AUDITOR reads broadly; FIXER edits only src/auth/ after issue handoff.
  Kill/downweight signals: unverified vulnerability, secret exposure risk, or fix without regression proof.
  Rebalance: add a separate red-team pass before final integration.

TEAMMATE 1 (AUDITOR)
  TASK: OWASP Top 10 scan + code audit
  OWNERSHIP: security/audit/
  BLAST RADIUS: read/report only
  DEPENDENCY: Submit issues to FIXER when done

TEAMMATE 2 (FIXER)
  TASK: Fix all discovered security issues
  OWNERSHIP: src/auth/
  BLAST RADIUS: src/auth/ only unless commander approves broader change
  DEPENDENCY: Wait for AUDITOR's issue list
```

## FDE Ontology Workflow Automation

```text
GOAL: Turn one messy operator workflow into a verified agent-assisted workflow.

ORDERS: Create a team of 4 teammates; route by domain discovery, modeling, implementation, and evaluation capability.

RISK BUDGET:
  Max blast radius: discovery artifacts and sandbox branch only; no production mutation.
  Kill/downweight signals: unverified operator claim, missing permission boundary, vague feedback, or demo without eval.
  Command board: .agent-state/command-board.md
  Rebalance: add feedback-quality reviewer if operator corrections are vague.

TEAMMATE 1 (FDE RECON)
  TASK: Observe the real workflow, roles, systems, permissions, exceptions, and hidden manual steps.
  OWNERSHIP: research/workflow/
  OUTPUT: FDE recon note plus gravel-road artifact proposal

TEAMMATE 2 (ONTOLOGY MODELER)
  TASK: Define mission, workstream, evidence, feedback, decision, and action objects.
  OWNERSHIP: .agent-state/command-board.md
  DEPENDENCY: Wait for FDE RECON

TEAMMATE 3 (BUILDER)
  TASK: Build the smallest sandboxed workflow slice.
  OWNERSHIP: sandbox/ or feature branch only
  DEPENDENCY: Wait for ONTOLOGY MODELER

TEAMMATE 4 (EDD QA)
  TASK: Build eval cases, grader, and feedback-to-eval path; reject eyeballing-only demos.
  OWNERSHIP: tests/ or evals/
  DEPENDENCY: Wait for BUILDER

QUALITY GATES:
- Command board has Data, Logic, Action, and Feedback objects
- Workflow has permission and audit boundary
- Eval gate passes before integration
- Operator feedback is converted into review items or eval cases
```
