# Storage and Governance Reference

Load this reference for architecture decisions, not ordinary retrieval.

## Layer Ownership

| Layer | Purpose | Canonical? | Typical content |
|---|---|---:|---|
| Active execution truth | Current work and release state | For operations | Issues, PRs, task ledgers |
| Quick memory | Session bootstrap and preferences | No | Compact project/user context |
| Durable wiki | Long-term understanding and provenance | Yes | Sources, concepts, entities, outputs |
| Retrieval index | Faster discovery | No | Lexical/vector indexes, caches |
| Governance state | Debt, health, reviews, promotion | For policy | Lint reports, review queues, receipts |

An index may be deleted and rebuilt. A source or decision ledger may not.

## Deduplication Decision

1. Same content hash: keep canonical source plus provenance aliases.
2. Same source identity, different extraction: preserve the richer locator set and record the merge.
3. Same title, different claim: do not merge automatically.
4. Same mechanism, different wording: propose a concept merge for review.
5. Contradictory claims: link both and open a contradiction item.

## Concurrent Source Identity Transaction

1. Derive `source_identity` from canonical URL or source id; fall back to a
   verified content hash plus title/date only when needed.
2. Search before extraction and record the query result.
3. Stage derived writes without publishing a second canonical source.
4. Recheck identity at commit with a writer lease, lock, or compare-and-set.
5. If another writer won, reuse its canonical path, repoint derived locators,
   and emit a reconciliation receipt.
6. Recheck after commit. One identity must resolve to one canonical source.

For append-only machine logs, derive an idempotency key from operation,
canonical source identity, target, and run/batch id. If the key exists, verify
and reuse the receipt instead of appending it again.

## Retrieval Order

1. Exact path, stable id, title, or wikilink.
2. Lexical search over Markdown.
3. Map/index traversal.
4. Optional semantic retrieval.
5. Source-page inspection when provenance is disputed.

Return match reason, path, and evidence quality. Similarity score alone is not relevance.

## Promotion Record

```yaml
candidate_id: ""
target: skill | sop | schema | automation
supporting_pages: []
source_locators: []
evidence_level: single-source | multi-source | local-verified
local_verification: ""
trigger: ""
owner: ""
budget: ""
stop_condition: ""
recovery: ""
write_back: ""
cheap_check: ""
approval: pending | approved | rejected
```

Unattended operations may count, lint, refresh deterministic indexes, and update machine-owned report blocks. Human review governs semantic merges, interpreted claims, policy changes, and promotion.
