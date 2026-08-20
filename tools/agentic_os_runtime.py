"""Bounded, read-only Agentic OS primitives and host-owned action dispatch."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
MAX_AUDIT_BYTES = 200_000
MAX_TAIL = 4_000
_SHELL_MARKERS = re.compile(r"[;&|<>`$\x00\r\n]")
_MODE_VALUES = {"manual", "session", "interview"}
_ACTION_STATES = {"LIVE", "HOST_REQUIRED", "UNAVAILABLE"}
_EFFECTS = {"READ_ONLY", "STAGED_WRITE", "LIVE_COMMIT", "EXTERNAL"}


class AgenticOSRuntimeError(RuntimeError):
    """Base error for fail-closed runtime operations."""


class UnknownActionError(AgenticOSRuntimeError):
    """Raised before any process or receipt is created for an unknown action."""


class ActionBlockedError(AgenticOSRuntimeError):
    """Raised when a known action is not executable by this local host."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    return _sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _tail(value: bytes | str) -> str:
    text = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
    return text[-MAX_TAIL:]


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    parent = ""
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if line[:1].isspace() and parent:
            result[f"{parent}.{key}"] = value
        else:
            parent = key if not value else ""
            result[key] = value
    return result


def _repo(repo_root: Path | str | None) -> Path:
    return Path(repo_root or Path(__file__).resolve().parents[1]).resolve()


def generate_skill_registry(repo_root: Path | str | None = None) -> dict[str, Any]:
    """Generate skill metadata from directories, never from a hard-coded count."""
    root = _repo(repo_root)
    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise FileNotFoundError(f"missing skills directory: {skills_root}")
    skills: list[dict[str, Any]] = []
    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            continue
        data = _parse_frontmatter(skill_file.read_text(encoding="utf-8", errors="replace"))
        skills.append(
            {
                "name": data.get("name", directory.name),
                "description": data.get("description", ""),
                "profile": data.get("metadata.profile", ""),
                "version": data.get("metadata.version", ""),
                "path": skill_file.relative_to(root).as_posix(),
                "sha256": _sha256_bytes(skill_file.read_bytes()),
            }
        )
    return {
        "skills": skills,
        "skill_count": len(skills),
        "skill_registry_sha256": _canonical_hash(skills),
    }


def _catalog(root: Path) -> dict[str, Any]:
    return _json_object(root / "contracts" / "agentic-os" / "action-registry.json")


def _validate_action(action: dict[str, Any]) -> None:
    required = {"id", "label", "description", "capability", "state", "effect", "approval_required", "command", "timeout_seconds", "verifier", "receipt_policy", "loop_contract"}
    missing = sorted(required - set(action))
    if missing:
        raise ValueError(f"action {action.get('id', '<unknown>')} missing fields: {missing}")
    if action["state"] not in _ACTION_STATES or action["effect"] not in _EFFECTS:
        raise ValueError(f"invalid state/effect for action {action['id']}")
    if action["receipt_policy"] != "required" or not isinstance(action["command"], list) or not action["command"]:
        raise ValueError(f"action {action['id']} must have a receipt and argv")
    for argv_name in ("command", "verifier"):
        argv = action[argv_name]
        if not isinstance(argv, list) or not argv or any(not isinstance(token, str) for token in argv):
            raise ValueError(f"action {action['id']} has invalid {argv_name}")
        if any(_SHELL_MARKERS.search(token) for token in argv):
            raise ValueError(f"action {action['id']} contains shell syntax")


def build_action_registry(repo_root: Path | str | None = None, vault_root: Path | str | None = None) -> dict[str, Any]:
    """Return the static catalog enriched with repository-derived skills and host state."""
    root = _repo(repo_root)
    catalog = _catalog(root)
    actions = json.loads(json.dumps(catalog.get("actions", [])))
    configured_vault = bool(vault_root and Path(vault_root).expanduser().resolve().is_dir())
    for action in actions:
        _validate_action(action)
        if action["capability"] in {"inventory", "freshness"}:
            action["state"] = "LIVE" if configured_vault else "HOST_REQUIRED"
    skills = generate_skill_registry(root)
    return {"schema_version": SCHEMA_VERSION, **skills, "actions": actions}


def _read_source(source: str | Path | dict[str, Any]) -> tuple[str, str, str]:
    if isinstance(source, dict):
        raw = json.dumps(source, ensure_ascii=False, sort_keys=True)
        return raw, "json-object", _sha256_bytes(raw.encode("utf-8"))
    candidate = Path(source) if isinstance(source, (str, Path)) else None
    if candidate is not None:
        try:
            is_file = candidate.is_file()
        except OSError:
            is_file = False
        if is_file:
            data = candidate.read_bytes()
            if len(data) > MAX_AUDIT_BYTES:
                raise ValueError(f"workflow audit input exceeds {MAX_AUDIT_BYTES} bytes")
            return data.decode("utf-8", errors="replace"), candidate.suffix.lower().lstrip(".") or "text", _sha256_bytes(data)
    raw = str(source)
    data = raw.encode("utf-8")
    if len(data) > MAX_AUDIT_BYTES:
        raise ValueError(f"workflow audit input exceeds {MAX_AUDIT_BYTES} bytes")
    return raw, "text", _sha256_bytes(data)


def _flatten_json(value: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(value, str):
        if value.strip():
            yield value.strip()
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_json(item, prefix)
    elif isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in {"tasks", "steps", "workflow", "repeated_tasks", "answers", "notes", "history"}:
                yield from _flatten_json(item, str(key))


def audit_workflow(source: str | Path | dict[str, Any], mode: str | None = None, max_candidates: int = 25) -> dict[str, Any]:
    """Audit supplied evidence and make bounded supervised promotion decisions."""
    if max_candidates <= 0 or max_candidates > 100:
        raise ValueError("max_candidates must be between 1 and 100")
    raw, source_kind, source_hash = _read_source(source)
    parsed: Any = None
    if source_kind in {"json", "json-object"} or raw.lstrip().startswith(("{", "[")):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
    requested_mode = mode.casefold() if mode else ""
    if requested_mode and requested_mode not in _MODE_VALUES:
        raise ValueError(f"mode must be one of {sorted(_MODE_VALUES)}")
    lower = raw.casefold()
    inferred = requested_mode or ("interview" if any(word in lower for word in ("interviewer", "question:", "answer:")) else "session" if any(word in lower for word in ("session", "run history", "previous run")) else "manual")
    audit_body = raw
    if parsed is None and raw.lstrip().startswith("---"):
        lines = raw.splitlines()
        first = next((index for index, line in enumerate(lines) if line.strip()), None)
        if first is not None and lines[first].strip() == "---":
            closing = next((index for index in range(first + 1, len(lines)) if lines[index].strip() == "---"), None)
            if closing is not None:
                audit_body = "\n".join(lines[closing + 1 :])
    candidates: list[str] = []
    if parsed is not None:
        candidates.extend(_flatten_json(parsed))
    if not candidates:
        for line in audit_body.splitlines():
            stripped = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#+\s*)", "", line).strip()
            stripped = re.sub(r"^\*\*\d{1,2}:\d{2}\*\*\s*[·:-]?\s*", "", stripped).strip()
            if (
                len(stripped) >= 12
                and not stripped.lower().startswith(("http://", "https://"))
                and not re.match(r"^!?\[[^]]*\]\(https?://", stripped, re.I)
                and not stripped.startswith("#")
            ):
                candidates.append(stripped)
    unique: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        normalized = re.sub(r"\s+", " ", item).strip()
        key = normalized.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(normalized[:500])
    priority_re = re.compile(
        r"\b(?:workflow audit|workflow|skill architecture|skill|automation|automate|"
        r"loop engineering|loop|memory|state management|state control|interface|ui|"
        r"distribution|package|repeat|recurr|schedule|command|button|database|previous run)\w*\b",
        re.I,
    )
    ranked = [
        (len(priority_re.findall(item)), index, item)
        for index, item in enumerate(unique)
    ]
    if any(score for score, _, _ in ranked):
        ranked.sort(key=lambda value: (-value[0], value[1]))
        unique = [item for _, _, item in ranked]
    unique = unique[:max_candidates]
    repeat_re = re.compile(r"\b(?:every|each|daily|weekly|monthly|recurr|repeat|again|routine|always|通常|每次|每天|每周|反复)\w*\b", re.I)
    loop_re = re.compile(r"\b(?:retry|monitor|poll|schedule|follow[- ]?up|until|loop|recurr|再次|循环|监控|定期)\w*\b", re.I)
    skill_re = re.compile(r"\b(?:workflow|skill|procedure|process|playbook|sop|工作流|技能|流程)\w*\b", re.I)
    automation_re = re.compile(r"\b(?:automation|automate|schedule|recurr|button|voice command|自动化|定期|按钮|语音命令)\w*\b", re.I)
    records: list[dict[str, Any]] = []
    for item in unique:
        repeated = bool(repeat_re.search(item))
        loop_candidate = bool(loop_re.search(item))
        multi_step = bool(re.search(r"(?:\bthen\b|\bnext\b|\bafter\b|\d+[.)]|->|；|;)", item, re.I))
        records.append({
            "evidence": item,
            "repeat_signal": repeated,
            "skill_decision": "SKILL_CANDIDATE" if repeated or multi_step or skill_re.search(item) else "KEEP_MANUAL",
            "automation_decision": "AUTOMATION_CANDIDATE" if repeated or automation_re.search(item) else "HOST_REQUIRED_REVIEW",
            "loop_decision": "LOOP_CANDIDATE" if loop_candidate else "NO_LOOP",
            "approval": "SUPERVISED_PROMOTION_REQUIRED",
            "owner": "OPERATOR_REVIEW_REQUIRED",
            "verifier": "DEFINE_BEFORE_PROMOTION",
            "stop_condition": "NO_AUTOMATIC_PROMOTION",
            "effect": "READ_ONLY_AUDIT",
        })
    return {
        "status": "AUDITED" if records else "INSUFFICIENT_EVIDENCE",
        "mode": inferred,
        "source": {"kind": source_kind, "sha256": source_hash, "bytes": len(raw.encode("utf-8"))},
        "bounds": {"max_bytes": MAX_AUDIT_BYTES, "max_candidates": max_candidates, "candidate_count": len(records)},
        "candidates": records,
        "recommendations": {
            "skill_candidates": sum(item["skill_decision"] == "SKILL_CANDIDATE" for item in records),
            "automation_candidates": sum(item["automation_decision"] == "AUTOMATION_CANDIDATE" for item in records),
            "loop_candidates": sum(item["loop_decision"] == "LOOP_CANDIDATE" for item in records),
            "policy": "Promotion is receipt-backed and supervised; this audit never mutates skills or schedules.",
        },
        "evidence": [{"source_sha256": source_hash, "mode": inferred, "candidate_count": len(records)}],
        "side_effect_count": 0,
    }


def _latest_run(vault: Path) -> dict[str, Any] | None:
    manifests = sorted(
        vault.glob("system/runs/*/run-*/manifest.json"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not manifests:
        return None
    path = manifests[0]
    try:
        value = _json_object(path)
        return {"path": path.relative_to(vault).as_posix(), "run_id": value.get("run_id"), "status": value.get("status")}
    except (OSError, ValueError, json.JSONDecodeError):
        return {"path": path.relative_to(vault).as_posix(), "status": "UNREADABLE"}


def _run_lint(root: Path) -> dict[str, Any]:
    command = [sys.executable, str(root / "tools" / "lint-agent-skills.py")]
    try:
        result = subprocess.run(command, cwd=str(root), capture_output=True, timeout=30, check=False, shell=False)
        return {"status": "PASS" if result.returncode == 0 else "FAIL", "exit_code": result.returncode, "stdout_tail": _tail(result.stdout), "stderr_tail": _tail(result.stderr)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "ERROR", "exit_code": None, "error": str(exc)}


def build_snapshot(repo_root: Path | str | None = None, vault_root: Path | str | None = None, limit: int = 100) -> dict[str, Any]:
    """Build a read-only repository/Vault snapshot; absent Vault data stays absent."""
    root = _repo(repo_root)
    if limit <= 0 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")
    registry = build_action_registry(root, vault_root)
    lint = _run_lint(root)
    contract_path = root / "contracts" / "vault-contract.json"
    contract_version = "unknown"
    try:
        contract_version = str(_json_object(contract_path).get("contract_version") or "unknown")
    except (OSError, ValueError, json.JSONDecodeError):
        lint = {**lint, "status": "ERROR", "error": "vault contract is unreadable"}
    vault: dict[str, Any]
    evidence: list[Any] = [{"kind": "skill-lint", **lint}, {"kind": "skill-registry", "sha256": registry["skill_registry_sha256"]}]
    configured = bool(vault_root)
    vault_path = Path(vault_root).expanduser().resolve() if vault_root else None
    if not configured or vault_path is None or not vault_path.is_dir():
        vault = {"configured": configured, "fingerprint": "", "counts": None, "version_counts": None, "debt": None, "freshness": None, "latest_run": None}
        evidence.append({"kind": "vault", "status": "MISSING_ACCESS", "configured": configured})
        status = "PARTIAL" if lint.get("status") == "PASS" else "ERROR"
    else:
        try:
            from tools.worker_flow.runtime import WorkerFlowRuntime

            runtime = WorkerFlowRuntime(vault_path, repo_root=root)
            inventory = runtime.inventory(limit=limit)
            freshness = runtime.freshness_scan(limit=limit)
            vault = {"configured": True, "fingerprint": runtime.vault_fingerprint, "counts": inventory.get("counts"), "version_counts": inventory.get("version_counts"), "debt": {"inventory": inventory.get("sources"), "maps": inventory.get("maps"), "system": inventory.get("system")}, "freshness": freshness, "latest_run": _latest_run(vault_path)}
            evidence.append({"kind": "vault-inventory", "status": inventory.get("status"), "side_effect_count": inventory.get("side_effect_count", 0)})
            evidence.append({"kind": "vault-freshness", "status": freshness.get("status"), "side_effect_count": freshness.get("side_effect_count", 0)})
            status = "READY" if lint.get("status") == "PASS" else "PARTIAL"
        except (OSError, ValueError, RuntimeError) as exc:
            vault = {"configured": True, "fingerprint": "", "counts": None, "version_counts": None, "debt": None, "freshness": None, "latest_run": None}
            evidence.append({"kind": "vault", "status": "ERROR", "error": str(exc)})
            status = "PARTIAL"
    return {"schema_version": SCHEMA_VERSION, "generated_at": _iso_now(), "status": status, "repository": {"contract_version": contract_version, "skill_count": registry["skill_count"], "skill_registry_sha256": registry["skill_registry_sha256"], "verification": {"skill_lint": lint}}, "vault": vault, "actions": registry["actions"], "evidence": evidence, "side_effect_count": 0}


def _resolve_token(token: str, root: Path, vault: Path | None) -> str:
    if token == "{python}":
        return sys.executable
    if token == "{repo_root}":
        return str(root)
    if token == "{vault_root}":
        if vault is None:
            raise ActionBlockedError("Vault action requires an explicitly configured Vault")
        return str(vault)
    if token == "{unavailable}":
        raise ActionBlockedError("action is not available on this host")
    if "{" in token or "}" in token:
        raise AgenticOSRuntimeError("unknown host token in registry")
    return token


def _resolve_argv(argv: list[str], root: Path, vault: Path | None) -> list[str]:
    resolved = [_resolve_token(token, root, vault) for token in argv]
    # Registry paths are relative to the repository. No caller string is ever appended.
    for index, token in enumerate(resolved):
        if token in {sys.executable, str(root), str(vault) if vault else ""} or token.startswith("-"):
            continue
        if index == 0:
            continue
        if not Path(token).is_absolute() and ("/" in token or "\\" in token or token.endswith((".py", ".json", ".md"))):
            candidate = (root / token).resolve()
            try:
                candidate.relative_to(root)
            except ValueError as exc:
                raise AgenticOSRuntimeError(f"registry path escapes repository: {token}") from exc
            if not candidate.exists():
                raise AgenticOSRuntimeError(f"registry path drift: {token}")
            resolved[index] = str(candidate)
    return resolved


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def execute_action(action_id: str, state_root: Path | str, repo_root: Path | str | None = None, vault_root: Path | str | None = None) -> dict[str, Any]:
    """Execute one catalog action with literal argv and write its typed receipt."""
    if not action_id or not isinstance(action_id, str):
        raise UnknownActionError("action id must be a non-empty string")
    root = _repo(repo_root)
    registry = build_action_registry(root, vault_root)
    actions = {action["id"]: action for action in registry["actions"]}
    if action_id not in actions:
        raise UnknownActionError(f"unknown action: {action_id}")
    action = actions[action_id]
    state = Path(state_root).expanduser().resolve() if state_root else None
    if state is None:
        raise ValueError("state_root is required; runtime has no implicit state path")
    vault = Path(vault_root).expanduser().resolve() if vault_root else None
    execution_id = uuid.uuid4().hex
    started = _iso_now()
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "action_id": action_id, "execution_id": execution_id, "state": "RUNNING", "started_at": started, "completed_at": None, "resolved_argv": [], "exit_code": None, "stdout_tail": "", "stderr_tail": "", "verifier": {"argv": [], "exit_code": None, "result": "NOT_RUN"}, "evidence": [], "side_effect_count": 0}
    receipt_path = state / "receipts" / f"{execution_id}.json"
    try:
        if action["state"] != "LIVE" or action["approval_required"] or action["effect"] != "READ_ONLY":
            raise ActionBlockedError(f"action {action_id} is {action['state']} and cannot run in the local read-only host")
        command = _resolve_argv(action["command"], root, vault)
        verifier = _resolve_argv(action["verifier"], root, vault)
        receipt["resolved_argv"] = command
        receipt["verifier"]["argv"] = verifier
        result = subprocess.run(command, cwd=str(root), capture_output=True, timeout=int(action["timeout_seconds"]), check=False, shell=False)
        receipt["exit_code"] = result.returncode
        receipt["stdout_tail"] = _tail(result.stdout)
        receipt["stderr_tail"] = _tail(result.stderr)
        if result.returncode == 0:
            checked = subprocess.run(verifier, cwd=str(root), capture_output=True, timeout=int(action["timeout_seconds"]), check=False, shell=False)
            receipt["verifier"]["exit_code"] = checked.returncode
            receipt["verifier"]["result"] = "PASS" if checked.returncode == 0 else "FAIL"
            receipt["evidence"].append({"command_exit_code": result.returncode, "verifier_exit_code": checked.returncode})
            receipt["state"] = "SUCCEEDED" if checked.returncode == 0 else "FAILED"
        else:
            receipt["state"] = "FAILED"
            receipt["evidence"].append({"command_exit_code": result.returncode, "verifier": "NOT_RUN"})
    except ActionBlockedError as exc:
        receipt["state"] = "BLOCKED"
        receipt["evidence"].append({"reason": str(exc)})
    except (OSError, subprocess.TimeoutExpired, AgenticOSRuntimeError, ValueError) as exc:
        receipt["state"] = "FAILED"
        receipt["evidence"].append({"reason": str(exc)})
    receipt["completed_at"] = _iso_now()
    _write_json(receipt_path, receipt)
    receipt["receipt_path"] = receipt_path.as_posix()
    return receipt


def verify_receipt(receipt: dict[str, Any]) -> tuple[bool, list[str]]:
    """Cheap independent receipt guard used by tests and host integrations."""
    errors: list[str] = []
    required = ("schema_version", "action_id", "execution_id", "state", "started_at", "completed_at", "resolved_argv", "verifier", "side_effect_count")
    for field in required:
        if field not in receipt:
            errors.append(f"missing {field}")
    if receipt.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version mismatch")
    if receipt.get("state") == "SUCCEEDED":
        if receipt.get("exit_code") != 0:
            errors.append("succeeded receipt has nonzero exit code")
        if receipt.get("verifier", {}).get("result") != "PASS":
            errors.append("succeeded receipt lacks verifier PASS")
    if receipt.get("side_effect_count") != 0:
        errors.append("side_effect_count must be zero")
    return not errors, errors
