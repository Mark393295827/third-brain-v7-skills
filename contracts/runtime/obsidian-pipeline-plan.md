# Obsidian V8.1 Runtime Intent Plan

## Mandate

The vault owner authorized repository updates that turn the approved V8.1 blueprint into an automated workflow and explicitly expanded the rollout to the live vault's `maps/`, `sources/`, `system/`, and `wiki/` surfaces. Live changes remain limited to a reviewed canary and require separate, explicit staging and commit approvals; this authority does not permit unbounded migration, deletion, or parallel shared-file writes.

## Objective

Provide one auditable host-controlled path for:

1. scanning clipping and freshness queues;
2. preserving immutable source evidence with stable identities, hashes, and block locators;
3. preparing bounded context for a semantic author;
4. validating Gold-Standard concept/entity candidates;
5. planning graph changes without parallel shared-file mutation;
6. independently governing and serially committing staged changes;
7. archiving only after post-commit verification; and
8. emitting a verified no-op when no eligible work exists.

## Authority and effects

- The repository owns schemas, templates, workflow contracts, runtime code, migrations, and tests.
- Obsidian Markdown owns source evidence, compiled knowledge, graph navigation, outputs, and durable run receipts.
- Model output is a proposal. Host code validates arguments, paths, state, hashes, budgets, and permissions before any tool effect.
- Workers write only to per-run staging. One Integration Owner applies canonical writes in dependency order.
- Source notes and append-only receipts are never silently rewritten or deleted.
- Shared graph targets use expected preimage hashes and fail closed on conflict.
- Live-vault commit, external publication, credentials, and irreversible actions require separate approval.

## Temporal knowledge contract

Knowledge freshness is claim metadata, not a prose assumption.

| Tier | Default review window | Meaning |
|---|---:|---|
| `snapshot` | none | Immutable statement about what a source said at `valid_as_of`; never relabeled as current. |
| `stable` | 365 days | Foundational mechanism or historical fact unlikely to change quickly. |
| `slow` | 180 days | Organization, product, or policy context with gradual change. |
| `dynamic` | 30 days | Active software, company, market, or research state. |
| `volatile` | 7 days | Prices, leadership, laws, schedules, benchmarks, and fast-moving model/product claims. |
| `realtime` | 1 day | Operational status, live counts, availability, or event state. |

Every compiled note declares `freshness_tier`, `valid_as_of`, `last_verified`, `next_review`, and `freshness_status`. A stale note remains readable evidence but cannot support wording such as “current”, “latest”, or “now” until a fresh source and verifier receipt are attached. Refresh creates a new evidence snapshot and appends an evolution event; it does not rewrite the historical source.

## Runtime topology

- Commander: owns intent hash, state, leases, budgets, and routing.
- Ingest worker: deterministic source identity, metadata extraction, full-content preservation, and evidence blocks.
- Cognitive worker: current-model semantic author operating only on the supplied context manifest.
- Graph planner: emits typed graph deltas and target preimage hashes.
- Governance checker: independently verifies source/anchor/schema/understanding/freshness/no-regression gates.
- Integration Owner: the only canonical writer and clipping lifecycle owner.
- Deliverable worker: optional and disabled unless an explicit output trigger exists.

## Trigger, no-op, stop, and recovery

- Trigger: 30-minute schedule, explicit CLI event, or freshness queue event.
- Legal no-op: a fresh eligibility query returns no unprocessed clipping and no due freshness item; output count is zero and no content/archive side effect occurred.
- Attempts: at most 2 per item/failure signature.
- Stop: success, verified no-op, contract/hash mismatch, permission denial, preimage conflict, verification failure, repeated signature, or budget exhaustion.
- Recovery: reload the last atomic state; replay no completed mutation; restore derived targets from rollback data; preserve sources and receipts.

## Initial rollout boundary

The implementation phase begins in temporary or explicitly supplied test vaults. The live-vault canary may proceed only after fresh acceptance evidence, a staged manifest, a bounded target list, rollback data, and explicit owner approval. Controlled domain batches remain outside the canary and advance only from clean touched-set receipts.
