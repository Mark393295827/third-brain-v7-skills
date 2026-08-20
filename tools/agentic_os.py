#!/usr/bin/env python3
"""CLI for the bounded Agentic OS registry, audit, snapshot, and dispatcher."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.agentic_os_runtime import (  # noqa: E402
    AgenticOSRuntimeError,
    audit_workflow,
    build_action_registry,
    build_snapshot,
    execute_action,
)


def _emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("registry", "snapshot"):
        item = sub.add_parser(name)
        item.add_argument("--repo", type=Path, default=ROOT)
        item.add_argument("--vault", type=Path)
        if name == "snapshot":
            item.add_argument("--limit", type=int, default=100)

    audit = sub.add_parser("audit")
    audit.add_argument("--input", type=Path, help="Text, Markdown, or JSON file; '-' reads stdin")
    audit.add_argument("--text", help="Literal supplied audit text")
    audit.add_argument("--mode", choices=("manual", "session", "interview"))
    audit.add_argument("--max-candidates", type=int, default=25)

    action = sub.add_parser("action")
    action.add_argument("--id", required=True, dest="action_id")
    action.add_argument("--repo", type=Path, default=ROOT)
    action.add_argument("--vault", type=Path)
    action.add_argument("--state-root", type=Path, required=True)

    for name in ("vault-inventory", "vault-freshness"):
        item = sub.add_parser(name)
        item.add_argument("--repo", type=Path, default=ROOT)
        item.add_argument("--vault", type=Path, required=True)
        item.add_argument("--limit", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "registry":
            result = build_action_registry(args.repo, args.vault)
        elif args.command == "snapshot":
            result = build_snapshot(args.repo, args.vault, args.limit)
        elif args.command == "audit":
            if args.input and args.text is not None:
                raise ValueError("choose --input or --text, not both")
            if args.input:
                if str(args.input) == "-":
                    source = sys.stdin.read()
                else:
                    if not args.input.is_file():
                        raise FileNotFoundError(f"workflow audit input does not exist: {args.input}")
                    source = args.input
            elif args.text is not None:
                source = args.text
            else:
                raise ValueError("audit requires --input or --text")
            result = audit_workflow(source, args.mode, args.max_candidates)
        elif args.command == "action":
            result = execute_action(args.action_id, args.state_root, args.repo, args.vault)
        else:
            if not args.vault.is_dir():
                raise FileNotFoundError(f"Vault root does not exist: {args.vault}")
            from tools.worker_flow.runtime import WorkerFlowRuntime

            runtime = WorkerFlowRuntime(args.vault, repo_root=args.repo)
            result = runtime.inventory(limit=args.limit) if args.command == "vault-inventory" else runtime.freshness_scan(limit=args.limit)
        _emit(result)
        if isinstance(result, dict) and result.get("state") in {"FAILED", "BLOCKED"}:
            return 2
        return 0
    except (AgenticOSRuntimeError, FileNotFoundError, PermissionError, ValueError, RuntimeError) as exc:
        _emit({"status": "ERROR", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
