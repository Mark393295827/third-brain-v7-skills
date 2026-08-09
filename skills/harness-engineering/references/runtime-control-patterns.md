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

## Intent Compiler And Runtime Envelope

Keep the human-reviewed Markdown plan authoritative for intent, then compile it
into a deterministic runtime envelope. Bind the source-plan hash, validate the
compiled contract, and persist the compiled-file hash in run state. A changed
plan invalidates the prior envelope. The validator hashes UTF-8 plan content
after normalizing line endings to LF so the binding is stable across platforms.

The envelope must declare:

- host-owned tool execution and argument validation;
- exact tool, filesystem, network, and opaque secret-handle scope;
- staged writes, approvals, post-write verification, and rollback;
- normalized termination routes;
- allowed output types, maximum external outputs, and legal no-op condition;
- finite time, tool, and external-effect budgets;
- event-log, checkpoint, and receipt paths.

Start with `runtime-envelope-example.json` and run:

```powershell
python scripts/validate_runtime_envelope.py references/runtime-envelope-example.json --strict
```

## Termination Router

| Normalized class | Host action | Completion evidence |
|---|---|---|
| `complete` | Run acceptance verifier | Verifier receipt, not model prose |
| `tool_request` | Validate arguments and permissions, then dispatch | Tool and post-condition receipts |
| `checkpoint` | Persist state and budget before continuation | Replayable checkpoint |
| `escalate` | Stop or hand off refusal, error, or unknown | Escalation receipt |

Termination classes must be disjoint. Unknown provider signals always route to
`escalate` until explicitly mapped and tested.

## Safe Quiet Output

`NO_OP` is a first-class result only when an eligibility query proves no work
was available, the external output count is zero, and the side-effect verifier
passes. Silence without those checks is missing evidence.

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
