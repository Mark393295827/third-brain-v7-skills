---
title: "Third Brain V8.1 Run History and Debt Index"
type: system-run-index
contract_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# Run History and Debt Index

This page is a compact index into durable state. It is intentionally not a
dashboard with invented counts. The generated run directory and receipts are
the evidence; this page and the other system notes are templates or
navigation metadata unless a run explicitly writes a verified snapshot.

## Generated evidence (read first)

| Evidence surface | Location | Interpretation |
|---|---|---|
| Run state/checkpoints | `system/runs/YYYY-MM/<run_id>/state.json` | current state of one run |
| Run manifest | `system/runs/YYYY-MM/<run_id>/manifest.json` | bounded inputs, targets, and hashes |
| Events | `system/runs/YYYY-MM/<run_id>/events.jsonl` | append-only execution trace |
| Receipts | `system/runs/YYYY-MM/<run_id>/receipts/` | typed verifier/commit evidence |
| Staging/rollback | `system/runs/YYYY-MM/<run_id>/staging/`, `rollback/` | recoverable write boundary |
| Queue state | `system/queues/` | generated unresolved work, if present |

Only a terminal receipt with verifier evidence supports a completion claim.
`QUEUED`, `RUNNING`, `BLOCKED_*`, `VERIFY_FAILED`, missing, or stale state is
not success. A scheduled trigger is not proof of execution.

## Debt surfaces

Debt is surfaced, not silently repaired. Inspect fresh generated inventory,
Governance receipts, and lint output for the current Vault before changing
state.

| Debt kind | Evidence location | Owner/action |
|---|---|---|
| Link/schema/provenance debt | `system/lint-report.md` and governance receipt | review, stage, verify |
| Pending workflow/dependency debt | `system/queues/` and run state | resume or close with receipt |
| Review/knowledge debt | `system/review-queue.md` | human review and promotion decision |
| System evolution debt | `system/system-evolution-backlog.md` | prioritize; no automatic policy mutation |
| Freshness debt | generated freshness receipt | refresh source snapshot, preserve history |

`system/review-queue.md`, `system/lint-report.md`, and
`system/system-evolution-backlog.md` are operator templates/current notes, not
proof that listed work is open or resolved. Their status must be corroborated
by a generated receipt or an explicit human decision record.

## Retention and feedback

Keep receipts append-only under the run directory. A later run may reference
prior evidence and record a supervised promotion, rollback, or debt closure;
it must not mutate historical source bodies or infer policy from a count alone.
Unknowns remain explicit in the next receipt.
