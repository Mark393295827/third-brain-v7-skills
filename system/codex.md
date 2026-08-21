---
title: "Third Brain V8.1 Codex OS Agent Navigation"
type: system-agent-instructions
contract_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# Codex OS Agent Navigation — V8.1

Codex is the primary host and execution surface for this project. The
workspace `AGENTS.md`, repository machine contracts, and deployed Vault
system bundle are authoritative. Claude, Gemini, Cursor, and Windsurf are
compatibility adapters; they do not define the operating model.

## Start here

1. Read [`vault-navigation.md`](vault-navigation.md) for the compact Vault map.
2. Read [`workflow-registry.md`](workflow-registry.md) before selecting an
   action or automation.
3. Read [`run-history-index.md`](run-history-index.md) and generated receipts
   before describing current state or completion.
4. Resolve skills from the manifest-verified Codex installation under
   `~/.agents/skills/`; do not rely on a copied skill count in prose.

## Codex host boundary

- Codex supplies model context, tool routing, approval interaction, and
  optional multi-agent execution.
- `tools.worker_flow` remains the deterministic transactional runtime for
  canonical Vault writes.
- Model text and browser requests are proposals. Only host code resolves an
  allowlisted action ID to literal argv and executes without a shell.
- Live Vault writes require staging, Governance, explicit approval,
  compare-and-set preimages, post-write verification, and a typed receipt.
- Schedulers, connectors, credentials, voice, publication, and external
  metrics remain host-dependent until fresh capability evidence exists.

Never embed a personal absolute path in a durable contract. Never use a
rendered dashboard, scheduled trigger, or model completion as proof that an
action succeeded.
