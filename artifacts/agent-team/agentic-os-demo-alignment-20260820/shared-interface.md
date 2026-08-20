# Shared Interface Freeze — T02/T03/T04

This file is the join contract for the Agentic OS demo-alignment builders.

## Registry Contract

The canonical registry is repository-generated. Each action must include:

```json
{
  "id": "stable-action-id",
  "label": {"en": "", "zh": ""},
  "description": {"en": "", "zh": ""},
  "capability": "workflow-audit|inventory|freshness|verify|prepare|commit|other",
  "state": "LIVE|HOST_REQUIRED|UNAVAILABLE",
  "effect": "READ_ONLY|STAGED_WRITE|LIVE_COMMIT|EXTERNAL",
  "approval_required": false,
  "command": ["literal", "argv", "tokens"],
  "timeout_seconds": 30,
  "verifier": ["literal", "argv", "tokens"],
  "receipt_policy": "required",
  "loop_contract": "relative/path-or-null"
}
```

Rules:

- Browser input may select only a registry `id`; it never supplies a command, path, shell fragment, environment variable, or verifier.
- The host resolves a literal argv array and invokes without a shell.
- Unknown IDs, disabled states, missing approval, and path/contract drift fail closed.
- `LIVE` means executable by the packaged local host now. `HOST_REQUIRED` means a documented host capability is missing. `UNAVAILABLE` means intentionally disabled or unsupported.
- No UI animation, timeout, model message, or HTTP 2xx response is success. Only a terminal typed receipt plus verifier evidence may display success.

## Snapshot Contract

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601 UTC",
  "status": "READY|PARTIAL|ERROR",
  "repository": {
    "contract_version": "8.1.0",
    "skill_count": 0,
    "skill_registry_sha256": "",
    "verification": {}
  },
  "vault": {
    "configured": false,
    "fingerprint": "",
    "counts": {},
    "version_counts": {},
    "debt": {},
    "freshness": {},
    "latest_run": null
  },
  "actions": [],
  "evidence": [],
  "side_effect_count": 0
}
```

Snapshot generation is read-only. Missing Vault access produces `PARTIAL`; it must not fabricate zero metrics.

## Action Receipt Contract

```json
{
  "schema_version": "1.0",
  "action_id": "",
  "execution_id": "",
  "state": "QUEUED|RUNNING|SUCCEEDED|FAILED|BLOCKED",
  "started_at": "ISO-8601 UTC",
  "completed_at": null,
  "resolved_argv": [],
  "exit_code": null,
  "stdout_tail": "",
  "stderr_tail": "",
  "verifier": {"argv": [], "exit_code": null, "result": "NOT_RUN|PASS|FAIL"},
  "evidence": [],
  "side_effect_count": 0
}
```

Receipts are written below an operator-selected state root. Repository defaults must not silently write to the live Vault. Live commits remain exclusively owned by the canonical V8.1 Integration Owner flow.

## Ownership

- T02: registry/schema/generator/audit/dispatcher primitives and targeted tests.
- T03: `system/` navigation, run/debt/operator surfaces and system-bundle entries/tests.
- T04: command-center HTML/host service, package/readiness/install documentation and interface tests.
- T05: conflict resolution, final machine contract review, live deployment, and end-to-end verification.
