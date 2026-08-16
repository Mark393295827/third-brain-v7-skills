from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .utils import append_jsonl, atomic_write_json, iso_z, read_json


TERMINAL_STATES = {
    "ARCHIVED",
    "COMMITTED",
    "NO_OP",
    "NEEDS_INPUT",
    "INSUFFICIENT_EVIDENCE",
    "BLOCKED_DEPENDENCY",
    "BLOCKED_PERMISSION",
    "VERIFY_FAILED",
    "NO_PROGRESS",
    "BUDGET_STOP",
}


def new_run_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"


@dataclass
class RunStore:
    vault_root: Path
    run_id: str
    run_dir: Path

    @classmethod
    def create(cls, vault_root: Path, run_id: str | None = None) -> "RunStore":
        run_id = run_id or new_run_id()
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        run_dir = vault_root / "system" / "runs" / month / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        for name in ("staging", "receipts", "rollback"):
            (run_dir / name).mkdir()
        store = cls(vault_root.resolve(), run_id, run_dir.resolve())
        store.write_state(
            {
                "run_id": run_id,
                "status": "DISCOVERED",
                "attempt": 1,
                "budget": {"max_attempts": 2},
                "evidence": [],
                "unknowns": [],
                "last_error": None,
                "next_action": "prepare_source",
                "created_at": iso_z(),
                "updated_at": iso_z(),
            }
        )
        return store

    @classmethod
    def find(cls, vault_root: Path, run_id: str) -> "RunStore":
        root = vault_root.resolve()
        matches = list((root / "system" / "runs").glob(f"*/{run_id}"))
        if len(matches) != 1:
            raise FileNotFoundError(f"run not found or ambiguous: {run_id}")
        return cls(root, run_id, matches[0].resolve())

    @property
    def state_path(self) -> Path:
        return self.run_dir / "state.json"

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / "manifest.json"

    @property
    def event_log_path(self) -> Path:
        return self.run_dir / "events.jsonl"

    def load_state(self) -> dict[str, Any]:
        return read_json(self.state_path)

    def write_state(self, state: dict[str, Any]) -> None:
        state = dict(state)
        state["updated_at"] = iso_z()
        atomic_write_json(self.state_path, state)

    def transition(self, status: str, next_action: str, **updates: Any) -> dict[str, Any]:
        state = self.load_state()
        state.update(updates)
        state["status"] = status
        state["next_action"] = next_action
        self.write_state(state)
        self.append_event("state_transition", {"status": status, "next_action": next_action})
        return state

    def append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        append_jsonl(
            self.event_log_path,
            {
                "event_id": f"{self.run_id}:{secrets.token_hex(6)}",
                "event_time": iso_z(),
                "run_id": self.run_id,
                "event_type": event_type,
                "payload": payload,
            },
        )

