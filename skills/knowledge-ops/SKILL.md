---
name: knowledge-ops
description: Use when an Obsidian knowledge system needs classification, deduplication, retrieval, synchronization, debt queues, or governed Agent/Wiki promotion.
metadata:
  version: "7.1.0"
  updated: "2026-07-25"
  profile: "stateful"
  assumes: "A durable Markdown knowledge base exists and its configured paths can be discovered or supplied."
  conflicts_with: "Treating vector search as canonical storage, silently merging provenance, or promoting one-off wiki signals into rules."
---

# Knowledge Operations

<skill_contract>
  <input>Vault root, operation, scope, canonical-store rules, permissions, destination, and execution budget.</input>
  <output>Verified classification, retrieval, deduplication, synchronization, audit, or governed promotion changes with receipts.</output>
  <done>Canonical Markdown remains authoritative, provenance and immutability are preserved, and representative checks pass.</done>
  <non_goals>Using vectors as canonical storage, silent provenance merges, automatic semantic rewrites, or one-signal rule promotion.</non_goals>

Operate the wiki as durable disk and governance layer. Markdown pages hold understanding and provenance; indexes, memory, vectors, and dashboards are replaceable access paths.

## Usage Template

Provide: vault root, operation (`organize`, `deduplicate`, `retrieve`, `sync`, `audit`, `promote`), scope, destination, permissions, and budget. Load `references/storage-governance.md` only when designing layers or promotion queues.

## Workflow

<intake>

Resolve configured paths and identify the canonical store, immutable sources, active execution truth, optional retrieval indexes, and governance queues. Record file counts, scope, and write authority before mutation.

</intake>

<unknowns_gate>

If canonical ownership, vault identity, or merge authority is ambiguous, return `NEEDS_INPUT`. Treat semantic similarity as a review signal, not proof that two notes or sources are equivalent.

</unknowns_gate>

<execute>

1. **Classify:** assign each item to execution state, quick memory, durable wiki, optional retrieval index, or governance state.
2. **Search first:** exact path/title, wikilinks, and lexical search before semantic retrieval.
3. **Deduplicate:** compare source identity, hash when available, claims, and provenance; merge compiled notes only with traceable reasons.
4. **Store:** write to the canonical Markdown layer, update indexes/maps, preserve immutable sources, and queue unresolved debt.
5. **Retrieve:** return paths and match reasons; load only the top evidence-bearing pages within context budget.
6. **Sync:** update optional indexes from canonical files and record indexed, skipped, removed, or failed items.
7. **Verify:** read after write, check links/source refs, and run representative retrieval queries.
8. **Promote:** require two durable supports or one strong source plus local verification, a bounded execution contract, preserved approvals/provenance, and a cheap objective check.

Automate deterministic counts and index refreshes only. Semantic rewrites, contradiction resolution, and rule promotion remain supervised.

</execute>

<evaluate>

Compare pre/post counts, inspect merge samples, replay retrieval queries, and verify no immutable source changed. A sync is partial if any canonical file is unindexed; retrieval quality is unproven without representative queries.

</evaluate>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus canonical paths, operation scope, file ledger, merge decisions, debt queues, index receipts, retrieval tests, and promotion candidates. Keep source and merge history append-only.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: ownership, merge semantics, or vault identity is unclear.
- `BLOCKED_PERMISSION`: a required store or index is inaccessible; continue read-only where useful.
- `VERIFY_FAILED`: write, link, sync, or retrieval check fails; preserve canonical state and queue repair.
- `NO_PROGRESS`: repeated organization changes no objective metric; stop and report the governing bottleneck.
- `BUDGET_STOP`: persist coverage and remaining queue; make no whole-vault claim.

## Output Contract

Return `status`, `result` (organized/retrieved/synced items and decisions), `evidence` (counts, paths, receipts, queries), `unknowns`, and `next_action` with owner and check.

## Edge Cases

- Two notes share a title but cite different sources and mechanisms: keep both until semantic review establishes a safe merge.
- Vector retrieval misses an exact concept: verify the Markdown path and index state; do not conclude the knowledge is absent.

## Success Metrics

- Canonical Markdown remains retrievable with provenance intact.
- Duplicates, stale metadata, weak links, and contradictions enter explicit queues.
- Every promotion candidate includes support, owner, budget, stop rule, and cheap check.

## Quality Gates

- [ ] Canonical store and immutable boundaries are explicit.
- [ ] Exact/lexical retrieval precedes optional semantic retrieval.
- [ ] Merge and sync decisions have receipts.
- [ ] No semantic rule is promoted without the promotion gate.

</skill_contract>
