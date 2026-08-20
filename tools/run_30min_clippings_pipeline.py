#!/usr/bin/env python3
"""Scheduler-safe, read-only adapter for the retired 30-minute pipeline.

This command never creates, edits, renames, or archives notes. Use the
transactional V8.1 CLI for prepare/submit/commit operations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.legacy_compat import deny_mutation, deprecation_envelope, explicit_directory
from tools.worker_flow.runtime import WorkerFlowRuntime


def scan_inbox(vault_dir: Path) -> dict[str, Any]:
    vault = explicit_directory(vault_dir, "vault")
    scan = WorkerFlowRuntime(vault).scan_queue()
    return deprecation_envelope(
        "tools/run_30min_clippings_pipeline.py",
        vault,
        action="queue-audit",
        facts={"scan": scan},
    )


def process_file(*_: object, **__: object) -> bool:
    deny_mutation("tools/run_30min_clippings_pipeline.py")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(scan_inbox(args.vault), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
