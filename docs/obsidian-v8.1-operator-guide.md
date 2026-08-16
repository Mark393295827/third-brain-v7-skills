---
title: "Third Brain V8.1 Obsidian Automation Operator Guide"
type: operator-guide
status: active
version: "8.1.0"
created: "2026-08-16"
updated: "2026-08-16"
---

# Third Brain V8.1 Obsidian Automation Operator Guide

This guide operates the transactional runtime defined by the V8.1 blueprint. The repository is the executable control plane; the supplied vault is the canonical knowledge/evidence plane.

## Safety boundary

- Always pass an explicit `--vault` path.
- `scan`, `inventory`, `freshness-scan`, and `status` are read-only.
- `prepare`, `prepare-local`, `prepare-retrofit`, and `prepare-system` write only to `system/runs/<month>/<run_id>/` and require `--approve-staging`.
- The cognitive worker edits only the staged draft named in `semantic-task.md`.
- `submit` runs Governance and cannot commit.
- `commit` requires `--approve-commit`, binds actor, vault fingerprint, manifest hash, Governance receipt hash, exact target scope, preimages, postimages, and a five-minute approval window in `receipts/commit-approval.json`.
- The staged concept and governed source-note hashes are rechecked at submit, immediately before commit, and after the transaction. A staged mutation returns `VERIFY_FAILED`; a reused-source mutation observed before the transaction returns `BLOCKED_DEPENDENCY`; a later race fails post-checks and rolls back only derived writes.
- `commit-intent.json` is persisted before writes and `receipts/canonical-commit.json` after post-checks. An interrupted all-written transaction resumes only after the actor, expiry, manifest, Governance receipt, scope, intent, and rollback metadata are revalidated. Clipping archival has its own explicit archive-only approval bound to that canonical checkpoint.
- Shared preimages are checked again immediately before each replacement; rollback never overwrites a later human or sync edit.
- Idempotency receipts require exact vault/mode/input identity, exactly one source/concept/map write in the contracted namespaces, and source evidence bound to the source path, note bytes, source ID, raw-input hash, and full preserved input; malformed receipts cannot produce a quiet `NO_OP`.
- CLI exit code `0` is reserved for successful/verified stop states such as `NO_OP`, `COMMITTED`, and `ARCHIVED`; permission, dependency, evidence, verification, progress, budget, and clipping-archive repair states return non-zero for the scheduler.
- A clipping is archived only after post-commit verification.
- Existing source bodies are immutable. A changed URL capture becomes a new snapshot linked to prior snapshots.

## Queue loop

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" scan
```

If the result is `NO_OP`, stop quietly. If eligible work exists:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" prepare `
  --file "Clipping.md" `
  --concept-title "Concept title" `
  --domain knowledge-systems `
  --moc "maps/domain-mocs/AI 知识工作流.md" `
  --freshness-tier dynamic `
  --approve-staging
```

The result names three artifacts:

- `context_manifest`: bounded source, contract, freshness, and path context;
- `semantic_task`: authoring instructions and stop rules;
- `concept_draft`: the only file the cognitive worker may edit.

After the candidate contains no unresolved template tokens:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" submit --run-id "run-..."
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" commit --run-id "run-..." --approve-commit
```

Only a final `ARCHIVED` receipt proves clipping lifecycle completion. If the move fails—or `--no-archive` is supplied—the run remains `ARCHIVE_PENDING`, returns `BLOCKED_DEPENDENCY`, and writes neither a terminal run receipt nor an idempotency receipt. A fresh `scan` exposes `repair_run_id` and `repair_action: retry_archive_only`; retry the same run without replaying source, concept, or map writes:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" commit `
  --run-id "run-from-repair_run_id" `
  --approve-commit
```

The durable archive destination also closes the crash window where the clipping was moved but the terminal receipt was not yet written.

## Repository-local source loop

Use this lane for a reviewed Markdown artifact already inside the repository. It creates an immutable source and a compiled concept, but never touches `Clippings/`:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" --repo "C:\path\to\third-brain-v5-skills" prepare-local `
  --input "docs/v8.1-current-model-obsidian-blueprint.md" `
  --concept-title "Third Brain V8.1 自动化知识流水线" `
  --domain knowledge-systems `
  --moc "maps/domain-mocs/AI 知识工作流.md" `
  --freshness-tier stable `
  --source-title "Third Brain V8.1 Current-Model Obsidian Automation Blueprint" `
  --source-author "Third Brain project" `
  --source-date "2026-08-16" `
  --approve-staging
```

Author the staged concept, run `submit`, and then run `commit --approve-commit`. A successful local-source run ends at `COMMITTED` with `archive: null`; repeating the same input/target pair is a zero-write `NO_OP`.

## System control-plane deployment

The system lane copies the exact versioned bundle declared in `contracts/system-bundle.json`. It deploys contracts, schemas, V8.1 templates, the operator wrapper, and versioned documentation without replacing the active unversioned concept template:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" --repo "C:\path\to\third-brain-v5-skills" prepare-system --approve-staging
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" --repo "C:\path\to\third-brain-v5-skills" submit --run-id "run-..."
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" --repo "C:\path\to\third-brain-v5-skills" commit --run-id "run-..." --approve-commit
```

Every target is compare-and-set against its staged preimage. Submit and commit reconstruct the exact contracted entry set from `contracts/system-bundle.json`; a tampered run manifest cannot retarget files outside the versioned `system/` surface. Any concurrent operator edit blocks the entire deployment before the first canonical write. Runtime/contracts/templates/scripts/docs and `system/runs/` are inventoried as excluded control-plane artifacts, while governed system notes remain linted. The deployment records a pre-write governed-debt signature, verifies it again immediately before commit, and rolls back if the post-write signature increases. The generated deployment manifest and run receipt record all hashes.

## Retrofit loop

First inventory one domain:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" inventory --domain knowledge-systems --limit 50
```

Choose only an `EVIDENCE_RESTORABLE` page with at least three resolvable source anchors:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" prepare-retrofit `
  --concept "wiki/concepts/knowledge-systems/Concept.md" `
  --moc "maps/domain-mocs/AI 知识工作流.md" `
  --freshness-tier stable `
  --approve-staging
```

The runtime snapshots the original page and records its SHA-256. Governance requires canonical monthly source paths and exact block locators. Commit stops if the human-edited page, source, or MOC changed after staging.

For a candidate authored as a reviewed repository artifact:

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" stage-candidate `
  --run-id "run-..." `
  --candidate "migration/canary/candidate.md" `
  --approve-staging
```

Then run `submit` and `commit` as above. Retrofit commits never archive or rewrite a source.

## Temporal maintenance

```powershell
python -m tools.worker_flow.cli --vault "C:\path\to\Obsidian Vault" freshness-scan --limit 100
```

Freshness tiers:

| Tier | Review window | Promotion behavior |
|---|---:|---|
| `snapshot` | none | Historical as-of evidence; never implied to be current |
| `stable` | 365 days | Reverify annually |
| `slow` | 180 days | Reverify twice yearly |
| `dynamic` | 30 days | Reverify monthly |
| `volatile` | 7 days | Reverify weekly |
| `realtime` | 1 day | Reverify daily |

A stale page remains readable, but cannot support “current/latest/now” language until a fresh source and verifier receipt exist. `next_review` must equal the policy-derived date from `valid_as_of`; a future date or an arbitrary extension evaluates to `unknown`. Refresh appends an evolution event and preserves the earlier source snapshot.

## Recovery

Each run stores:

```text
system/runs/YYYY-MM/<run_id>/
  state.json
  manifest.json
  context-manifest.json
  semantic-task.md
  events.jsonl
  receipts/
  staging/
  rollback/
```

Resume from `state.json`; do not replay completed writes. Recovery never trusts `COMMITTING` alone: it requires a current approval, exact intent, valid Governance receipt, exact operation scope, and rollback entries whose paths, preimages, preserve flags, backup paths, and backup hashes match the authorized operations. Expired or changed authorization stops at `BLOCKED_PERMISSION`; changed rollback metadata stops at `BLOCKED_DEPENDENCY`; neither emits a terminal/idempotency receipt. A graph or concept preimage conflict requires a fresh plan. Rollback restores derived files while preserving a later concurrent edit. A new source that fails post-commit Governance is removed with derived writes; a reused source is carried as a no-write transaction dependency and is never rolled back or overwritten. The original clipping/repository input and staged evidence remain available for repair.

## Verification commands

```powershell
python -m unittest -v tests.test_worker_flow_v81 tests.test_worker_flow_v81_deployment tests.test_worker_flow_transaction_safety
python -m compileall -q tools/worker_flow
python "C:\Users\高杰\.agents\skills\loop-engineering\scripts\validate_loop_contract.py" contracts/automation-loop-contract.md --strict
python "C:\Users\高杰\.agents\skills\harness-engineering\scripts\validate_runtime_envelope.py" contracts/runtime/obsidian-pipeline-envelope.json --strict
```
