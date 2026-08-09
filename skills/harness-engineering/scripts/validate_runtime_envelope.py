#!/usr/bin/env python3
"""Validate a deterministic, host-enforced agent runtime envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "workflow_id",
    "contract_version",
    "plan",
    "runtime",
    "termination_policy",
    "effects",
    "budgets",
    "audit",
)
TERMINATION_CLASSES = ("complete", "tool_request", "checkpoint", "escalate")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
HOST_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
)
HANDLE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,127}$")
BROAD_WRITE_TARGETS = {"", ".", "..", "/", "\\", "*", "**"}
SECRET_FIELDS = {"visible_to_model", "handles"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, field: str, errors: List[str]) -> List[str]:
    if not isinstance(value, list):
        errors.append("%s must be a list" % field)
        return []
    result = []
    for index, item in enumerate(value):
        if not _is_non_empty_string(item):
            errors.append("%s[%d] must be a non-empty string" % (field, index))
            continue
        result.append(item.strip())
    if len(result) != len(set(result)):
        errors.append("%s must not contain duplicates" % field)
    return result


def _mapping(value: Any, field: str, errors: List[str]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        errors.append("%s must be an object" % field)
        return {}
    return value


def _positive_int(value: Any, field: str, errors: List[str]) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        errors.append("%s must be a positive integer" % field)
        return 0
    return value


def _non_negative_int(value: Any, field: str, errors: List[str]) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append("%s must be a non-negative integer" % field)
        return -1
    return value


def _normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_envelope(
    contract: Any,
    strict: bool = False,
    base_dir: Optional[Path] = None,
) -> List[str]:
    errors = []  # type: List[str]
    if not isinstance(contract, dict):
        return ["runtime envelope must be a JSON object"]

    for field in REQUIRED_TOP_LEVEL:
        if field not in contract:
            errors.append("missing required field: %s" % field)

    for field in ("schema_version", "workflow_id", "contract_version"):
        if field in contract and not _is_non_empty_string(contract[field]):
            errors.append("%s must be a non-empty string" % field)

    plan = _mapping(contract.get("plan"), "plan", errors)
    for field in ("source_path", "source_sha256", "compiler"):
        if not _is_non_empty_string(plan.get(field)):
            errors.append("plan.%s must be a non-empty string" % field)
    source_sha256 = plan.get("source_sha256")
    if _is_non_empty_string(source_sha256) and not SHA256_RE.match(source_sha256):
        errors.append("plan.source_sha256 must be a 64-character SHA-256")
    if strict and _is_non_empty_string(plan.get("source_path")):
        if not plan["source_path"].lower().endswith(".md"):
            errors.append("strict plan.source_path must reference a Markdown plan")
        if base_dir is not None:
            base_path = Path(base_dir).resolve()
            source_path = Path(plan["source_path"])
            if source_path.is_absolute() or re.match(
                r"^[a-zA-Z]:[\\/]", plan["source_path"]
            ):
                errors.append("strict plan.source_path must be relative to base-dir")
            else:
                resolved_source = (base_path / source_path).resolve()
                try:
                    resolved_source.relative_to(base_path)
                except ValueError:
                    errors.append("strict plan.source_path escapes base-dir")
                else:
                    if not resolved_source.is_file():
                        errors.append("strict plan source does not exist: %s" % source_path)
                    elif SHA256_RE.match(str(source_sha256)):
                        try:
                            observed_hash = _normalized_sha256(resolved_source)
                        except (OSError, UnicodeError) as exc:
                            errors.append("unable to hash plan source: %s" % exc)
                        else:
                            if observed_hash.lower() != str(source_sha256).lower():
                                errors.append("plan.source_sha256 does not match source plan")

    runtime = _mapping(contract.get("runtime"), "runtime", errors)
    owner = runtime.get("tool_execution_owner")
    if not _is_non_empty_string(owner):
        errors.append("runtime.tool_execution_owner must be a non-empty string")
    elif strict and owner != "host":
        errors.append("strict runtime.tool_execution_owner must be host")

    allowed_tools = _string_list(
        runtime.get("allowed_tools"), "runtime.allowed_tools", errors
    )
    if strict and not allowed_tools:
        errors.append("strict runtime.allowed_tools must not be empty")

    filesystem = _mapping(runtime.get("filesystem"), "runtime.filesystem", errors)
    _string_list(filesystem.get("read"), "runtime.filesystem.read", errors)
    write_paths = _string_list(
        filesystem.get("write"), "runtime.filesystem.write", errors
    )
    if strict:
        for target in write_paths:
            normalized_target = target.replace("\\", "/")
            segments = normalized_target.split("/")
            if (
                target.strip() in BROAD_WRITE_TARGETS
                or normalized_target.startswith("/")
                or re.match(r"^[a-zA-Z]:/", normalized_target)
                or ".." in segments
                or "*" in normalized_target
            ):
                errors.append("strict write target is too broad: %s" % target)

    hosts = _string_list(
        runtime.get("network_allowlist"), "runtime.network_allowlist", errors
    )
    if strict:
        for host in hosts:
            if "*" in host or "://" in host or "/" in host or not HOST_RE.match(host):
                errors.append("strict network target must be an exact host: %s" % host)

    secrets = _mapping(runtime.get("secrets"), "runtime.secrets", errors)
    if not isinstance(secrets.get("visible_to_model"), bool):
        errors.append("runtime.secrets.visible_to_model must be boolean")
    elif strict and secrets["visible_to_model"]:
        errors.append("strict runtime envelope must not expose secrets to the model")
    if strict:
        unexpected_secret_fields = sorted(set(secrets) - SECRET_FIELDS)
        for field in unexpected_secret_fields:
            errors.append("strict runtime.secrets field is not allowed: %s" % field)
    handles = _string_list(
        secrets.get("handles"), "runtime.secrets.handles", errors
    )
    if strict:
        for handle in handles:
            if not HANDLE_RE.match(handle):
                errors.append("strict secret handle is invalid: %s" % handle)

    output_policy = _mapping(
        runtime.get("output_policy"), "runtime.output_policy", errors
    )
    allowed_types = _string_list(
        output_policy.get("allowed_types"),
        "runtime.output_policy.allowed_types",
        errors,
    )
    max_outputs = _non_negative_int(
        output_policy.get("max_external_outputs"),
        "runtime.output_policy.max_external_outputs",
        errors,
    )
    if strict and not allowed_types:
        errors.append("strict runtime.output_policy.allowed_types must not be empty")
    if strict and any("*" in output_type for output_type in allowed_types):
        errors.append("strict output types must not contain wildcards")
    if "no_op" in allowed_types and not _is_non_empty_string(
        output_policy.get("no_op_condition")
    ):
        errors.append("no_op output requires runtime.output_policy.no_op_condition")

    termination = _mapping(
        contract.get("termination_policy"), "termination_policy", errors
    )
    seen = set()  # type: Set[str]
    termination_reasons = {}  # type: Dict[str, List[str]]
    for class_name in TERMINATION_CLASSES:
        reasons = _string_list(
            termination.get(class_name),
            "termination_policy.%s" % class_name,
            errors,
        )
        termination_reasons[class_name] = reasons
        if strict and not reasons:
            errors.append("strict termination_policy.%s must not be empty" % class_name)
        for reason in reasons:
            if reason in seen:
                errors.append("termination reason appears in multiple classes: %s" % reason)
            seen.add(reason)
    if strict and "unknown" not in termination_reasons.get("escalate", []):
        errors.append("strict termination_policy.escalate must include unknown")

    effects = _mapping(contract.get("effects"), "effects", errors)
    if not isinstance(effects.get("stage_writes"), bool):
        errors.append("effects.stage_writes must be boolean")
    elif strict and write_paths and not effects["stage_writes"]:
        errors.append("strict envelopes must stage declared writes")
    approvals = _string_list(
        effects.get("approval_required_for"),
        "effects.approval_required_for",
        errors,
    )
    for field in ("post_write_verifier", "rollback"):
        if not _is_non_empty_string(effects.get(field)):
            errors.append("effects.%s must be a non-empty string" % field)
    if strict and max_outputs > 0 and "external" not in approvals:
        errors.append("strict external outputs require external approval")

    budgets = _mapping(contract.get("budgets"), "budgets", errors)
    _positive_int(budgets.get("wall_time_seconds"), "budgets.wall_time_seconds", errors)
    _positive_int(budgets.get("tool_calls"), "budgets.tool_calls", errors)
    output_budget = _non_negative_int(
        budgets.get("external_outputs"), "budgets.external_outputs", errors
    )
    if max_outputs >= 0 and output_budget >= 0 and max_outputs > output_budget:
        errors.append("output policy exceeds budgets.external_outputs")

    audit = _mapping(contract.get("audit"), "audit", errors)
    audit_paths = []  # type: List[str]
    for field in ("event_log", "state_path", "receipt_path"):
        value = audit.get(field)
        if not _is_non_empty_string(value):
            errors.append("audit.%s must be a non-empty string" % field)
        else:
            audit_paths.append(value.strip())
    if len(audit_paths) != len(set(audit_paths)):
        errors.append("audit paths must be distinct")

    return errors


def load_contract(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError("unable to read contract: %s" % exc)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON: %s" % exc)
    if not isinstance(data, dict):
        raise ValueError("runtime envelope must be a JSON object")
    return data


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Resolve plan.source_path from this directory (default: contract directory).",
    )
    args = parser.parse_args(argv)

    try:
        contract = load_contract(args.contract)
    except ValueError as exc:
        print("FAIL runtime envelope")
        print("- %s" % exc)
        return 1

    base_dir = args.base_dir or args.contract.resolve().parent
    errors = validate_envelope(contract, strict=args.strict, base_dir=base_dir)
    if errors:
        print("FAIL runtime envelope")
        for error in errors:
            print("- %s" % error)
        return 1

    print("PASS runtime envelope")
    print("- workflow_id: %s" % contract["workflow_id"])
    print("- tools: %d" % len(contract["runtime"]["allowed_tools"]))
    print(
        "- max_external_outputs: %d"
        % contract["runtime"]["output_policy"]["max_external_outputs"]
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
