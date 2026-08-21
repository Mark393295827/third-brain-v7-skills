---
title: "Third Brain V8.1 Agentic OS Command Center"
type: system-command-center
contract_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# Codex Agentic OS Command Center

Codex is the primary host for this operator surface. It describes the truthful view a host may render. It does
not claim that a browser, scheduler, connector, service, or Vault is
available. The host supplies a fresh snapshot; Markdown here supplies the
labels, boundaries, and recovery route.

## Snapshot contract

The host snapshot has `schema_version`, UTC `generated_at`, `status`
(`READY`, `PARTIAL`, or `ERROR`), repository contract/version and registry
hash, Vault configuration/fingerprint/counts/version counts/debt/freshness,
`latest_run`, an allowlisted `actions` list, evidence references, and
`side_effect_count`. Missing Vault access is `PARTIAL`, never fabricated zero
metrics.

The minimum operator panels are:

- **Readiness:** contract version, registry hash, configured Vault, and host
  capabilities.
- **Memory/state:** top-down navigation, latest generated run, queues, debt,
  and freshness.
- **Workflow:** action state, eligibility, approval requirement, and loop
  contract.
- **Evidence:** receipt links, verifier result, hashes, unknowns, and
  side-effect count.

## Safe actions

An action button may submit only a stable registry `id`. The host resolves its
literal argv and invokes it without a shell. Unknown IDs, `HOST_REQUIRED` or
`UNAVAILABLE` actions, path/contract drift, missing approval, and missing
verifiers fail closed. The UI must disable unavailable actions and must not
show a spinner, timeout, model text, or HTTP 2xx as success.

## Typed action receipt

Each invocation reports `QUEUED`, `RUNNING`, then terminal `SUCCEEDED`,
`FAILED`, or `BLOCKED`, with `execution_id`, timestamps, resolved argv, exit
code, stdout/stderr tails, verifier argv/result (`NOT_RUN`, `PASS`, `FAIL`),
evidence, and `side_effect_count`. Render success only when the terminal
receipt and verifier both pass. Receipts are written under an operator-
selected state root; repository defaults never silently write to the live
Vault.

## Operator routes

- Start at [`system/vault-navigation.md`](vault-navigation.md).
- Read eligibility and automation boundaries in
  [`system/workflow-registry.md`](workflow-registry.md).
- Inspect generated history/debt in
  [`system/run-history-index.md`](run-history-index.md).
- For a write-capable operation, use the staged/approved/verified commands in
  `system/docs/v8.1/obsidian-v8.1-operator-guide.md`.

Live commit, external publication, credentials, and host services require
explicit host evidence and serial Integration Owner approval.
