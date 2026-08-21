"""Fail-closed helpers for pre-V8.1 command compatibility surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any


CANONICAL_CLI = "python -m tools.worker_flow.cli"


class LegacyMutationDisabled(RuntimeError):
    """Raised when an obsolete entry point is asked to mutate a Vault."""


def explicit_directory(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"{label} must be an existing directory: {path}")
    return path


def deprecation_envelope(
    entrypoint: str,
    vault: Path,
    *,
    action: str,
    facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": "DEPRECATED_READ_ONLY",
        "entrypoint": entrypoint,
        "deprecated_in": "8.1",
        "removal_release": "9.0",
        "action": action,
        "vault": str(vault),
        "replacement_command": CANONICAL_CLI,
        "side_effect_count": 0,
        "facts": facts or {},
    }


def deny_mutation(entrypoint: str) -> None:
    raise LegacyMutationDisabled(
        f"{entrypoint} mutation is disabled; use {CANONICAL_CLI} with explicit approval gates"
    )
