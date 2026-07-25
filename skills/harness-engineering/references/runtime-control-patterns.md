# Runtime Control Patterns

Load this reference while producing a concrete harness specification.

## Primitive Selector

| Primitive | Use for | Avoid when |
|---|---|---|
| Deterministic script/hook | Lint, test, policy, guard, event receipt | Judgment or broad context is required |
| Skill | Reusable procedure, convention, decision policy | A stable program can enforce it more cheaply |
| Connector | Authenticated cross-product/API access | A local narrow tool is sufficient |
| Dynamic workflow | Independent shards with observable workers | Frequent shared judgment/IPC is needed |
| Agent team | Distinct ownership, critique, integration | One process plus verifier is enough |

## Permission Ladder

| Stage | Allowed | Proof to advance |
|---|---|---|
| Observe | Read/search/recommend | Sources and assumptions inspectable |
| Co-drive | Draft/simulate/prepare | Human approves every external action |
| Scoped action | Low-risk reversible execution | Logs, rollback, post-check pass |
| Supervised routine | Reversible scheduled work | Alerts, receipts, anomaly review |
| Audited autonomy | Frequent low-risk loops | Periodic permission/failure review |

## Delegated Action Gate

```yaml
mandate: "explicit user authorization"
scope: []
limits:
  time: ""
  cost: ""
  rate: ""
  blast_radius: ""
preview: ""
approval: ""
receipt: ""
rollback_or_compensation: ""
```

## Tool Contract

```yaml
name: ""
purpose: ""
inputs: []
bounds: []
permissions: []
timeout: ""
idempotency_key: ""
failure_path: ""
evidence: ""
audit_log: ""
```

Broad shell/API capability requires a wrapper, allowlist, approval gate, and post-action check.

## Session Event Minimum

Record event id/time, actor, context/state version, request, tool call, tool result, changed resources, verifier result, error/recovery, budget, and next state. Redact secrets while keeping enough structure for incident reconstruction.

## Trigger-Context-Steering

```text
Trigger: schedule, event, queue, webhook, or human request
Context: exact files, state, tools, accounts, and credentials
Steering: live health, approval, verifier, anomaly, rollback
Receipt: durable state, log, diff, dashboard, or external status
```

Every routine also needs idempotency, hard budget, stop, stale-context review, fallback, and recovery.
