# Loop Contract — Obsidian V8.1 Knowledge Automation

- Objective: Run a bounded, resumable Obsidian pipeline that turns eligible clippings and freshness-review items into source-grounded knowledge without provenance, graph, or temporal-regression defects.
- Mode: Automation.
- Trigger: A scheduled 30-minute queue event, an explicit CLI request, or a freshness-review queue event.
- Scope: Versioned repository contracts, a configured Obsidian vault, per-run staging, immutable sources, selected concepts/entities, graph deltas, governance receipts, clipping lifecycle, and freshness debt.
- Non-goals: No fabricated metadata or evidence, no unselected bulk rewrite, no silent semantic merge, no direct parallel write to shared maps, no unapproved live-vault rollout, and no external publication.
- Owner: Host runtime commander; one Integration Owner commits shared state and an independent Governance checker verifies promotion.
- Inputs: Vault root, vault fingerprint, runtime envelope, clipping or refresh candidate, source identity, template version, freshness policy, permissions, and prior run state.
- Artifacts path: `<vault>/system/runs/YYYY-MM/<run_id>/staging/` plus immutable receipts under the same run directory.
- State path: `<vault>/system/runs/YYYY-MM/<run_id>/state.json`.
- Work clock: Host-generated UTC event timestamps plus source `observed_at`, claim `valid_as_of`, and verifier `verified_at` timestamps.
- Success metric: Eligible items reach a verified terminal state; touched files have zero new P0/P1 findings; source hashes and locators resolve; global debt does not regress; archive occurs only after post-commit verification.
- Evidence: Trigger receipt, context manifest, source identity queries, staged artifact hashes, deterministic governance output, semantic-check receipt, commit manifest, post-write reads, archive receipt, and freshness decision.
- Verifier: Deterministic contract tests and Governance checks executed outside the authoring worker; consequential ambiguity requires human approval.
- Topology: manager-workers.
- Max iterations: 2 attempts per item and failure signature.
- Time limit: 30 minutes per scheduled run.
- Budget: 100 host tool calls per scheduled run.
- Review budget: 25 changed files per run.
- Stop condition: Stop on verified completion, verified no-op, no eligible item, any finite cap, permission denial, stale runtime contract, graph preimage conflict, metric regression, or the same failure signature twice.
- Write-back: Atomically update run state; append typed events and one idempotent final receipt; update marker-bounded derived views only after commit.
- Permission boundary: No external, published, credentialed, destructive, or shared live-vault action without explicit approval, a serial integration gate, staged preview, and verified rollback; isolated test-vault writes are allowed.
- Recovery: Resume from the last verified checkpoint; the serial integration gate rechecks source identity and target preimages; roll back derived writes from the transaction manifest while preserving source evidence and append-only receipts.

