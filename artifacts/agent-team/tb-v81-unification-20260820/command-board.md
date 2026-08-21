# Third Brain V8.1 Unification Command Board

Mission ID: `tb-v81-unification-20260820`

Status: `APPROVED`

## Commander intent

Unify the repository control plane and the Obsidian knowledge plane around the
V8.1 transactional contract without overwriting the owner's existing dirty
worktree, ingesting the pending clipping, installing plugins, or bulk-rewriting
the live knowledge corpus.

## Runtime envelope

- Target operational SLA: 180 minutes for repository integration and a bounded
  live-vault control-plane canary. This is a planning envelope, not a wall-clock
  promise.
- Team topology: capacity-constrained Tier 2 squadron, ten roles executed in
  waves with at most four active agents including the commander.
- Integration owner and only workspace writer: `/root`.
- Worker write policy: read-only findings and typed receipts. Workers must not
  edit repository or live-vault files.
- Total ETC ceiling: 72,000.
- Target TCLR: at least 2.5.
- Maximum attempts per failure signature: 2, with a changed strategy required
  for retry.

## Protected state

- Preserve all pre-existing tracked, deleted, and untracked worktree changes.
- Do not run reset, checkout, clean, stash, or destructive bulk rewrites.
- Do not process the file currently waiting in the live `Clippings/` root.
- Do not install or remove Obsidian plugins.
- Do not bulk-move or semantically rewrite the live vault corpus.
- Source bodies and append-only receipts remain immutable.

## Pre-flight task DAG

| Task | Objective | Owner role | Dependencies | Expected output | Verification |
|---|---|---|---|---|---|
| P0 | Capture protected baseline and command state | Commander | none | Command board, token ledger, baseline receipts | `git status --short --branch`; hash comparison |
| T01 | Establish active V8.1 authority and version policy | Architecture auditor | P0 | Authority map and contradiction ledger | Active-surface version scan |
| T02 | Classify every repository surface | Architecture auditor | P0 | active/generated/example/history/deprecated inventory | Full path reconciliation |
| T03 | Reconcile contracts, schemas, templates and deploy bundle | Contract auditor + Commander | T01 | Closed machine-readable contract set | Schema and SHA-256 checks |
| T04 | Make `tools.worker_flow` the canonical transactional runtime | Runtime engineer + Commander | T03 | Safe canonical runtime and compatibility facade | Runtime unit and failure-path tests |
| T05 | Gate or deprecate unsafe legacy writers | Runtime engineer + Commander | T04 | Dry-run/approval-safe legacy entry points | No unapproved live writes |
| T06 | Audit and align all 20 skills | Skill auditor + Commander | T01,T03 | Consistent skill contracts and resources | 20/20 skill lint |
| T07 | Synchronize adapters, mirrors and installers | Distribution auditor + Commander | T06 | Reproducible multi-client distribution | Mirror hashes and installer tests |
| T08 | Consolidate active documentation and examples | Docs auditor + Commander | T04,T06 | One coherent V8.1 documentation spine | Version, link and command checks |
| T09 | Expand CI to all production test suites | QA engineer + Commander | T04-T08 | Complete local/CI verification matrix | tools + tests + experiments pass |
| T10 | Stage and deploy the live-vault control bundle | Vault auditor + Commander | T03,T09 | Preimage-checked deployment receipt | Repo/Vault hash equality |
| T11 | Produce legacy taxonomy migration manifest | Vault auditor | T10 | Read-only per-file debt inventory | No knowledge-file moves |
| T12 | Run three reversible retrofit canaries | Commander + independent checker | T10,T11 | Clean, broken-source and collision receipts | Zero new P0/P1; rollback proof |
| T13 | Adversarial review and release gate | Critic + gatekeeper | T09,T12 | Final evidence ledger and deny/allow decision | Fresh commands and exact receipts |

## Typed worker receipt

Each worker returns:

```json
{
  "mission_id": "tb-v81-unification-20260820",
  "task_ids": ["T01"],
  "state": "DONE|NEEDS_INPUT|VERIFY_FAILED",
  "scope_read": [],
  "findings": [],
  "recommended_changes": [],
  "verification_commands": [],
  "risks": [],
  "writes_performed": false,
  "estimated_etc_used": 0,
  "next_action": "serial integration by /root"
}
```

## Integration gates

1. No worker edits shared files.
2. The commander applies changes in dependency order with `apply_patch`.
3. Every touched file receives a scope-matched check.
4. Live-vault writes use staging, approval, preimage checks, serial commit, and
   post-commit verification.
5. Completion requires independent review; effort or file counts are not proof.
