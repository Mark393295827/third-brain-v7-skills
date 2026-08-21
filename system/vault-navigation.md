---
title: "Third Brain V8.1 Vault Navigation"
type: system-navigation
contract_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# V8.1 Vault Navigation

This is the compact, top-down entry point for an agent or operator. It is a
navigation aid, not an inventory receipt: counts, freshness, debt, and run
status must be read from a fresh generated receipt.

## Top-down route

1. **Codex control plane:** read [`system/config.md`](config.md),
   [`system/codex.md`](codex.md), and the deployed machine contract at
   `system/contracts/v8.1/vault-contract.json`.
2. **Evidence intake:** inspect `Clippings/` and immutable
   `sources/YYYY-MM/`, `sources/pre-2026/`, or `sources/books/`.
3. **Knowledge:** route a concept to one contracted domain and an entity to
   one contracted category; route reviewed outputs to their output category.
4. **Graph:** use the four map tiers and their Home/Central Index entry points.
5. **State:** inspect generated run receipts and queues before describing
   completion or current health.

## Contracted knowledge destinations

### Concept domains (`wiki/concepts/`)

The canonical domain set is deliberately listed here so navigation remains
complete even when a Vault has no note in a domain yet.

| Domain | Path |
|---|---|
| ai-engineering | `wiki/concepts/ai-engineering/` |
| ai-economics | `wiki/concepts/ai-economics/` |
| ai-science | `wiki/concepts/ai-science/` |
| behavioral-econ | `wiki/concepts/behavioral-econ/` |
| business-strategy | `wiki/concepts/business-strategy/` |
| entrepreneurship | `wiki/concepts/entrepreneurship/` |
| general-concepts | `wiki/concepts/general-concepts/` |
| geopolitics-energy | `wiki/concepts/geopolitics-energy/` |
| identity-culture | `wiki/concepts/identity-culture/` |
| investing-macro | `wiki/concepts/investing-macro/` |
| investing-quant | `wiki/concepts/investing-quant/` |
| investing-vc | `wiki/concepts/investing-vc/` |
| knowledge-systems | `wiki/concepts/knowledge-systems/` |

### Entity categories (`wiki/entities/`)

`people/`, `companies/`, `funds-investors/`, `products/`, and `orgs/` are the
only contracted entity destinations.

| Category | Path |
|---|---|
| people | `wiki/entities/people/` |
| companies | `wiki/entities/companies/` |
| funds-investors | `wiki/entities/funds-investors/` |
| products | `wiki/entities/products/` |
| orgs | `wiki/entities/orgs/` |

Outputs are routed to `wiki/outputs/gmail-digests/`,
`wiki/outputs/evaluations/`, or `wiki/outputs/compilations/`.

## Graph and state surfaces

| Surface | Contracted location | Use |
|---|---|---|
| Domain MOCs | `maps/domain-mocs/` | domain-level navigation |
| System indexes | `maps/system-indexes/` | operational indexes |
| Project maps | `maps/project-maps/` | project-level graph |
| Canvases | `maps/canvases/` | visual graph artifacts |
| Root indexes | `maps/Home.md`, `maps/中央索引.md` | top-level map entry points |
| Run history | `system/runs/` and [`system/run-history-index.md`](run-history-index.md) | generated receipts and recovery state |
| Debt/queues | `system/queues/`, `system/lint-report.md`, [`system/review-queue.md`](review-queue.md), [`system/run-history-index.md`](run-history-index.md) | known unresolved work |

Use [`system/workflow-registry.md`](workflow-registry.md) to determine whether
an action is read-only, staged, host-dependent, or unavailable. Use
[`system/agentic-os-command-center.md`](agentic-os-command-center.md) for the
operator snapshot and typed action-receipt rules.

## Evidence boundary

Templates and this navigation page describe contracts. They do not prove that
a run happened, a queue is empty, or a Vault is healthy. A claim of execution
requires the matching generated receipt under `system/runs/` plus verifier
evidence; a missing or stale receipt is an explicit unknown.
