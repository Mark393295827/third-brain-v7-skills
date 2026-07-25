# Research Ledgers

Use ledgers for standard, deep, high-stakes, or durable research. A short evidence brief may collapse them into one table if claim-to-source traceability remains clear.

## Preflight

```yaml
question: ""
decision: ""
audience: ""
scope_in: []
scope_out: []
recency_window: ""
allowed_sources: []
excluded_sources: []
private_data: none | authorized | prohibited
budget:
  max_sources: 0
  max_passes: 0
  max_time: ""
stop_condition: ""
```

## Source Ledger

| id | source | date | type | authority | directness | independence | access boundary | notes |
|---|---|---|---|---|---|---|---|---|

Source type examples: primary record, official documentation, research paper, dataset, company statement, expert analysis, journalism, community signal. “Primary” does not guarantee completeness or lack of bias.

## Claim Ledger

| claim_id | claim | source ids | evidence strength | counterevidence | status | confidence |
|---|---|---|---|---|---|---|

Status: `supported`, `contested`, `inference`, `unsupported`, `stale`. Confidence reflects evidence quality and decision sensitivity, not rhetorical certainty.

## Activity Trace

Record pass, information requirement, query/source class, useful result, rejected source reason, gap remaining, and budget consumed. Avoid dumping raw browser history.

## STOW Handoff

```yaml
source_candidates: []
canonical_claims: []
contradictions: []
fast_changing_claims: []
concept_candidates: []
entity_candidates: []
unknowns: []
recommended_destination: ""
promotion_status: review-required
```

The ingest process independently verifies source access and vault writes; a research handoff is not an ingest receipt.
