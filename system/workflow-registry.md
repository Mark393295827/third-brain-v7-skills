---
title: "Third Brain V8.1 Workflow and Automation Registry"
type: system-registry
contract_version: "8.1.0"
status: active
updated: "2026-08-20"
---

# Workflow and Automation Registry

This document defines the operator-facing registry contract. The machine
registry and host dispatcher are authoritative when present; this page is the
stable explanation of how to read them. Registry entries are allowlisted
actions, not suggestions for shell commands.

## Action record

Every exposed action has these fields:

| Field | Meaning |
|---|---|
| `id` | Stable identifier selected by the host; never user-supplied argv |
| `label`, `description` | Localized operator copy |
| `capability` | `workflow-audit`, `inventory`, `freshness`, `verify`, `prepare`, `commit`, or `other` |
| `state` | `LIVE`, `HOST_REQUIRED`, or `UNAVAILABLE` |
| `effect` | `READ_ONLY`, `STAGED_WRITE`, `LIVE_COMMIT`, or `EXTERNAL` |
| `approval_required` | Explicit approval gate for effects that can write |
| `command`, `verifier` | Literal argv arrays; invoked without a shell |
| `timeout_seconds` | Finite execution budget |
| `receipt_policy` | `required` for every action |
| `loop_contract` | Contract path or `null` |

The host rejects unknown IDs, disabled states, missing approvals, path drift,
and verifier drift. Browser input can select only an `id`; it cannot provide a
path, command, environment variable, or verifier.

## Eligibility and stop rules

An action is eligible only when its capability is available, its contract
version and path boundary match, and required approval/credentials are present.
Read-only scans may be `LIVE`. Staging may be `LIVE` only through the
canonical worker runtime. Live Vault commits remain an explicit, serial
Integration Owner operation. Schedulers, connectors, credentials, services,
and external publication are `HOST_REQUIRED` unless fresh host evidence says
otherwise.

Stop on a verified success/no-op, no eligible item, finite budget, permission
denial, stale contract, preimage conflict, verifier failure, or repeated
failure signature. A trigger, timeout, model message, or HTTP success is not a
receipt.

## Registry-to-receipt loop

```text
select id -> resolve allowlisted argv -> QUEUED -> RUNNING
  -> run verifier -> SUCCEEDED | FAILED | BLOCKED
  -> append typed receipt below the operator-selected state root
```

The action receipt must contain `schema_version`, `action_id`,
`execution_id`, terminal `state`, timestamps, resolved argv, exit code,
verifier result, evidence, and `side_effect_count`. Success is displayable
only for a terminal `SUCCEEDED` receipt with verifier `PASS`.

## Workflow families

| Family | Default effect | Evidence required |
|---|---|---|
| Audit/registry | read-only | generated audit result and registry hash |
| Inventory/freshness | read-only | fresh inventory or freshness receipt |
| Prepare/stage | staged write | run manifest, preimages, and staging approval |
| Submit/verify | read-only governance | governance receipt and exact scope |
| Commit/archive | live commit | explicit approval, CAS preimages, post-checks, canonical receipt |
| Distribution/external | host-dependent | host capability and external receipt |

For the full transactional boundary, follow
`system/docs/v8.1/obsidian-v8.1-operator-guide.md`. For loop timing and
recovery, follow `system/contracts/v8.1/automation-loop-contract.md`.
