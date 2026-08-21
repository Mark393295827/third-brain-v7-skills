# Static Graph Contract

Use this reference when writing or reviewing a `graph-engineering` JSON
contract. V8.1 supports bounded static DAGs only. Put local repetition inside a
`loop` node; do not encode cycles or dynamic node expansion.

## Ownership Boundaries

- **Graph Engineering:** dependency topology, typed edges, joins, graph state,
  and smallest-unit recovery.
- **Loop Engineering:** repeated execution through time inside one node.
- **Agent Teams Command:** worker/process ownership, IPC, isolated writes,
  integration, and cleanup.
- **Harness Engineering:** scheduler, permissions, leases, event delivery,
  observability, and production recovery.

## Node Contract

Every node declares:

| Field | Meaning |
|---|---|
| `id`, `kind`, `owner` | Stable identity, execution kind, single owner |
| `inputs`, `outputs` | Named payload schemas consumed and produced |
| `reads`, `writes` | Concrete state or artifact territory |
| `verifier` | Objective acceptance check |
| `timeout_seconds`, `max_attempts`, `tool_calls` | Finite local budgets |
| `effect_class` | `read-only`, `reversible`, or `external` |
| `idempotency` | Duplicate-delivery behavior |
| `compensation` | Recovery action; mandatory for external effects |

Kinds: `deterministic`, `loop`, `agent`, `agent-team`, `human-gate`, and
`subgraph`. Prefer deterministic nodes. Use an agent only when judgment or
adaptation is part of the node's contract.

## Edge Contract

Each edge declares `from`, `to`, `type`, `payload_schema`, `condition`, and
`failure_route`.

Supported types are `data`, `control`, `verification`, `failure`, and
`compensation`. Data and verification payloads must appear in the source
node's `outputs` and target node's `inputs`. V8.1 rejects feedback edges and
all cycles. A non-empty `failure_route` is an implicit control arc from the
edge source to the named recovery node, so it participates in reachability,
entry/terminal, and cycle checks.

## External Effect Approval

For every node with `effect_class: external`, strict contracts must:

- list the exact external node ID in `permission_boundary.approval_required`;
- feed the node directly from a `human-gate` through a typed payload whose
  schema name contains `approval` and `receipt`;
- list every external write target exactly in `permission_boundary.allowed`
  and not in `permission_boundary.denied`;
- declare node compensation plus an explicit compensation edge.

Prose such as "operator approval required" is not a bound approval scope.

## Join Contract

Any node with more than one incoming dependency needs one join contract.
Supported modes:

- `all`: wait for every declared input.
- `reduce`: combine all inputs deterministically.
- `first-success`: accept the first verified success.
- `quorum`: accept `k` verified inputs.
- `barrier-verifier`: run a collection-level check before release.
- `human-gate`: require an approval receipt at a `human-gate` node.

A join names its exact input nodes, target, verifier, and quorum when used.

## State And Recovery

Persist append-only events and an atomic current checkpoint. Minimum node
states:

```text
PENDING -> READY -> RUNNING -> VERIFYING -> SUCCEEDED
                        |          |
                        v          v
                     RETRY       FAILED -> COMPENSATING -> COMPENSATED
```

`WAITING` may represent an unmet dependency or approval. Retry the failed node
or smallest invalid subgraph after changing diagnosis or strategy. Rerun the
whole graph only when the graph invariant itself is invalid; strict V8.1
contracts therefore set `whole_graph_rerun` to `false`.

## Admission

Use a graph only when at least one condition is measurable:

1. two or more branches are independent and critical-path savings repay
   scheduling plus review cost;
2. maker and checker need separate context or ownership;
3. node-local recovery avoids replaying already verified work;
4. typed joins materially improve failure localization.

Otherwise use one-shot execution or `loop-engineering`.

## Static Checks

Run:

```powershell
python scripts/validate_graph_contract.py references/diamond-graph-example.json --strict
```

Strict validation rejects dangling edges, schema mismatch, cycles, unreachable
nodes, conflicting writers, missing joins, unbounded budgets, whole-graph
retry, unbound external approvals, denied write scopes, and uncompensated
external effects.
