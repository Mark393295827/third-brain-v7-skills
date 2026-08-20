---
title: "Codex Vault Agent Navigation V8.1"
type: system-agent-navigation
contract_version: "8.1.0"
template_id: vault-agent-navigation
template_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# Codex Vault Agent Navigation — V8.1

Codex is the primary host for this Vault; other harnesses are compatibility
adapters. Use this page as the current Codex workspace entry point after the system bundle
is deployed. Resolve paths from the machine contract; never assume a personal
absolute Vault path.

## Operating sequence

1. Read `system/config.md`, `system/codex.md`, and
   `system/contracts/v8.1/vault-contract.json`.
2. Read `system/vault-navigation.md` to choose the contracted destination.
3. Treat `Clippings/` and `sources/` as evidence; source bodies are immutable.
4. Before claiming work, inspect `system/runs/` and `system/queues/` for a
   generated receipt and unresolved state.
5. Use the canonical worker flow for staging, Governance, commit, and archive.
   Live writes require explicit approval and compare-and-set preimages.

## Routing table

- Concepts: `wiki/concepts/<one-of-13-contract-domains>/`
- Entities: `wiki/entities/<one-of-5-contract-categories>/`
- Outputs: `wiki/outputs/gmail-digests/`, `evaluations/`, or `compilations/`
- Maps: `maps/domain-mocs/`, `system-indexes/`, `project-maps/`, or `canvases/`
- State: `system/runs/` and `system/queues/`

The exact domain/category/tier names are listed in
`system/vault-navigation.md` and are machine-authoritative in the Vault
contract. Do not invent a new top-level taxonomy folder.

## Evidence and completion

This template gives instructions only. A generated run receipt, verifier
evidence, hashes, and side-effect count are required to establish what
happened. Missing access, stale state, unknown freshness, or a blocked run
must be reported as such. A scheduled trigger or rendered page is not proof
of execution.

For action eligibility and safe dispatch, follow
`system/workflow-registry.md`; for the operator view, follow
`system/agentic-os-command-center.md`.
