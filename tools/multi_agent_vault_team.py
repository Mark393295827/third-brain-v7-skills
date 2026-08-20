#!/usr/bin/env python3
"""Read-only compatibility facade for the retired in-process team runner.

The old implementation spawned Vault mutators and recursively launched the
``tools`` test suite. V8.1 keeps this import surface only for discovery and
queue audit. Execution belongs to the host orchestrator and canonical runtime.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.legacy_compat import deprecation_envelope, explicit_directory
from tools.worker_flow.runtime import WorkerFlowRuntime


class MultiAgentVaultCommander:
    def __init__(self, vault_dir: Path):
        self.vault_dir = explicit_directory(vault_dir, "vault")
        self.run_id = f"audit-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.ipc_ledger: list[dict[str, Any]] = []

    def log_ipc_event(
        self,
        worker_role: str,
        task: str,
        state: str,
        artifact: str,
        evidence: str,
    ) -> None:
        self.ipc_ledger.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "worker_role": worker_role,
                "task": task,
                "state": state,
                "artifact": artifact,
                "evidence": evidence,
            }
        )

    def execute_team_mission(self) -> dict[str, Any]:
        """Return a read-only queue audit; never spawn workers or test runners."""
        scan = WorkerFlowRuntime(self.vault_dir).scan_queue()
        self.log_ipc_event(
            "Compatibility-Auditor",
            "Scan canonical ingest queue",
            str(scan["status"]),
            "Clippings/",
            f"eligible_count={scan.get('eligible_count', 0)}",
        )
        result = deprecation_envelope(
            "tools/multi_agent_vault_team.py",
            self.vault_dir,
            action="queue-audit",
            facts={"run_id": self.run_id, "scan": scan, "ipc_events": self.ipc_ledger},
        )
        result["mission_status"] = "READ_ONLY"
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(MultiAgentVaultCommander(args.vault).execute_team_mission(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
