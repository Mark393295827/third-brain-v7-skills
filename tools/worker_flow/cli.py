from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .runtime import WorkerFlowRuntime


FAILED_TERMINATION_STATES = {
    "BLOCKED_DEPENDENCY",
    "BLOCKED_PERMISSION",
    "BUDGET_STOP",
    "ERROR",
    "INSUFFICIENT_EVIDENCE",
    "NEEDS_INPUT",
    "NO_PROGRESS",
    "VERIFY_FAILED",
}


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _exit_code(result: dict[str, Any]) -> int:
    receipt = result.get("receipt") if isinstance(result.get("receipt"), dict) else {}
    if result.get("archive_error") or receipt.get("archive_error"):
        return 3
    return 3 if result.get("status") in FAILED_TERMINATION_STATES else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Third Brain V8.1 transactional Obsidian workflow")
    parser.add_argument("--vault", type=Path, required=True, help="Explicit Obsidian vault root")
    parser.add_argument("--repo", type=Path, help="Repository root containing contracts/")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scan", help="Read-only clipping eligibility query")

    prepare = subparsers.add_parser("prepare", help="Stage source evidence and a semantic concept task")
    prepare.add_argument("--file", required=True, help="Clipping filename or path inside Clippings/")
    prepare.add_argument("--concept-title", required=True)
    prepare.add_argument("--domain", required=True)
    prepare.add_argument("--moc", required=True, help="Vault-relative Markdown MOC path")
    prepare.add_argument("--freshness-tier", default="dynamic")
    prepare.add_argument("--approve-staging", action="store_true")

    local = subparsers.add_parser("prepare-local", help="Stage a repository Markdown document as immutable evidence")
    local.add_argument("--input", type=Path, required=True, help="Markdown path inside the repository")
    local.add_argument("--concept-title", required=True)
    local.add_argument("--domain", required=True)
    local.add_argument("--moc", required=True, help="Vault-relative Markdown MOC path")
    local.add_argument("--freshness-tier", default="stable")
    local.add_argument("--source-type", default="local-synthesis")
    local.add_argument("--input-class", default="internal-state")
    local.add_argument("--source-title")
    local.add_argument("--source-author", default="")
    local.add_argument("--source-date", default="unknown")
    local.add_argument("--approve-staging", action="store_true")

    system_bundle = subparsers.add_parser("prepare-system", help="Stage the deterministic V8.1 system bundle")
    system_bundle.add_argument("--approve-staging", action="store_true")

    retrofit = subparsers.add_parser("prepare-retrofit", help="Stage a preimage-checked Gold-Standard concept retrofit")
    retrofit.add_argument("--concept", required=True, help="Vault-relative concept Markdown path")
    retrofit.add_argument("--moc", required=True, help="Vault-relative Markdown MOC path")
    retrofit.add_argument("--freshness-tier", default="stable")
    retrofit.add_argument("--approve-staging", action="store_true")

    candidate = subparsers.add_parser("stage-candidate", help="Copy a repository-authored candidate into run staging")
    candidate.add_argument("--run-id", required=True)
    candidate.add_argument("--candidate", type=Path, required=True)
    candidate.add_argument("--approve-staging", action="store_true")

    submit = subparsers.add_parser("submit", help="Validate the authored staged concept")
    submit.add_argument("--run-id", required=True)

    commit = subparsers.add_parser("commit", help="Serially commit a verified run")
    commit.add_argument("--run-id", required=True)
    commit.add_argument("--approve-commit", action="store_true")
    commit.add_argument("--no-archive", action="store_true")

    status = subparsers.add_parser("status", help="Read durable run state")
    status.add_argument("--run-id", required=True)

    freshness = subparsers.add_parser("freshness-scan", help="Read-only temporal debt query")
    freshness.add_argument("--limit", type=int, default=100)
    inventory = subparsers.add_parser("inventory", help="Read-only maps/sources/system/wiki migration inventory")
    inventory.add_argument("--limit", type=int, default=100)
    inventory.add_argument("--domain")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runtime = WorkerFlowRuntime(args.vault, repo_root=args.repo)
        if args.command == "scan":
            result = runtime.scan_queue()
        elif args.command == "prepare":
            result = runtime.prepare(
                args.file,
                concept_title=args.concept_title,
                domain=args.domain,
                moc_relative_path=args.moc,
                freshness_tier=args.freshness_tier,
                approve_staging=args.approve_staging,
            )
        elif args.command == "prepare-retrofit":
            result = runtime.prepare_retrofit(
                args.concept,
                moc_relative_path=args.moc,
                freshness_tier=args.freshness_tier,
                approve_staging=args.approve_staging,
            )
        elif args.command == "prepare-local":
            result = runtime.prepare_local(
                args.input,
                concept_title=args.concept_title,
                domain=args.domain,
                moc_relative_path=args.moc,
                freshness_tier=args.freshness_tier,
                source_type=args.source_type,
                input_class=args.input_class,
                source_title=args.source_title,
                source_author=args.source_author,
                source_date=args.source_date,
                approve_staging=args.approve_staging,
            )
        elif args.command == "prepare-system":
            result = runtime.prepare_system_bundle(approve_staging=args.approve_staging)
        elif args.command == "stage-candidate":
            result = runtime.stage_candidate(
                args.run_id,
                args.candidate,
                approve_staging=args.approve_staging,
            )
        elif args.command == "submit":
            result = runtime.submit(args.run_id)
        elif args.command == "commit":
            result = runtime.commit(args.run_id, approve_commit=args.approve_commit, archive=not args.no_archive)
        elif args.command == "status":
            result = runtime.status(args.run_id)
        elif args.command == "freshness-scan":
            result = runtime.freshness_scan(limit=args.limit)
        elif args.command == "inventory":
            result = runtime.inventory(limit=args.limit, domain=args.domain)
        else:
            raise AssertionError(args.command)
    except (FileNotFoundError, PermissionError, ValueError, RuntimeError) as exc:
        _emit({"status": "ERROR", "error": str(exc)})
        return 2
    _emit(result)
    return _exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
