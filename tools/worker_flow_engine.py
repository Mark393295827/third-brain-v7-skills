#!/usr/bin/env python3
"""Fail-closed facade for the retired monolithic worker-flow engine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.legacy_compat import deny_mutation, deprecation_envelope, explicit_directory
from tools.worker_flow.runtime import WorkerFlowRuntime


class WorkerFlowEngine:
    """Compatibility object exposing audit only; every legacy write stage is denied."""

    def __init__(self, vault_dir: Path):
        self.vault_dir = explicit_directory(vault_dir, "vault")

    def audit(self, limit: int = 100) -> dict[str, Any]:
        facts = WorkerFlowRuntime(self.vault_dir).inventory(limit=limit)
        return deprecation_envelope(
            "tools/worker_flow_engine.py",
            self.vault_dir,
            action="inventory",
            facts={"inventory": facts},
        )

    def stage_1_ingest(self, *_: object, **__: object) -> dict[str, Any]:
        deny_mutation("tools/worker_flow_engine.py:stage_1_ingest")

    def stage_2_cognitive_compile(self, *_: object, **__: object) -> dict[str, Any]:
        deny_mutation("tools/worker_flow_engine.py:stage_2_cognitive_compile")

    def stage_3_graph_weave(self, *_: object, **__: object) -> dict[str, Any]:
        deny_mutation("tools/worker_flow_engine.py:stage_3_graph_weave")

    def stage_4_governance_audit(self) -> dict[str, Any]:
        return self.audit()

    def stage_5_deliver_output(self, *_: object, **__: object) -> dict[str, Any]:
        deny_mutation("tools/worker_flow_engine.py:stage_5_deliver_output")

    def execute_full_pipeline(self, *_: object, **__: object) -> dict[str, Any]:
        deny_mutation("tools/worker_flow_engine.py:execute_full_pipeline")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--audit", action="store_true", help="retained read-only compatibility flag")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args(argv)
    print(json.dumps(WorkerFlowEngine(args.vault).audit(limit=args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
