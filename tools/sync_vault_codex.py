"""Plan or explicitly approve the Codex-facing V8.1 Vault navigation sync.

The default is read-only.  The exact write allowlist is the Vault-root
``AGENTS.md`` and the manifest-managed ``<install-home>/.agents/skills``
directory.  This helper never reads or writes ``.claude/`` or plugin files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone

try:  # direct script execution and package import both remain supported
    from .install_skills import sync_skills
except ImportError:  # pragma: no cover - direct ``python tools/...`` path
    from install_skills import sync_skills


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(source.read_bytes())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def sync(*, repo_root: Path, vault_root: Path, install_home: Path, state_root: Path, approve: bool = False, expected_agents_sha256: str | None = None) -> dict:
    repo_root, vault_root, install_home, state_root = (p.resolve() for p in (repo_root, vault_root, install_home, state_root))
    template = repo_root / "system" / "templates" / "vault-agent-navigation-v8.1.md"
    source_skills = repo_root / "skills"
    target_agents = vault_root / "AGENTS.md"
    target_skills = install_home / ".agents" / "skills"
    if not vault_root.is_dir():
        raise FileNotFoundError(f"Vault root does not exist: {vault_root}")
    if not template.is_file() or not source_skills.is_dir():
        raise FileNotFoundError("repository Codex navigation template or skills source is missing")
    current_hash = sha256(target_agents)
    result = {
        "schema_version": "1.0", "status": "PLANNED", "generated_at": now(),
        "vault_root": str(vault_root), "install_home": str(install_home),
        "write_allowlist": ["AGENTS.md", str(target_skills)], "forbidden": [".claude", "settings.local.json", "plugins"],
        "preimage": {"agents_sha256": current_hash, "skills_manifest": str(target_skills / ".third-brain-v8.1-manifest.json")},
        "planned": {"agents_sha256": sha256(template), "skills_source": str(source_skills)},
        "side_effect_count": 0,
    }
    if not approve:
        return result
    if expected_agents_sha256 is not None and current_hash != expected_agents_sha256:
        result.update({"status": "BLOCKED", "error": "AGENTS.md preimage changed (CAS mismatch)"})
        return result
    if sha256(target_agents) != current_hash:
        result.update({"status": "BLOCKED", "error": "AGENTS.md changed after planning (CAS mismatch)"})
        return result
    backup_root = state_root / "backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    state_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    if target_agents.is_file():
        atomic_copy(target_agents, backup_root / "AGENTS.md")
    atomic_copy(template, target_agents)
    try:
        skills_result = sync_skills(source_skills, target_skills)
        if sha256(target_agents) != sha256(template):
            raise OSError("read-after-write AGENTS.md hash mismatch")
        if skills_result.get("status") != "INSTALLED" or skills_result.get("verified") is not True:
            raise OSError("Codex skills manifest installation did not verify")
    except Exception:
        backup = backup_root / "AGENTS.md"
        if backup.is_file():
            atomic_copy(backup, target_agents)
        elif target_agents.is_file():
            target_agents.unlink()
        raise
    result.update({"status": "COMMITTED", "backup": str(backup_root), "skills": skills_result, "side_effect_count": 1})
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), type=Path)
    parser.add_argument("--vault-root", required=True, type=Path)
    parser.add_argument("--install-home", default=str(Path.home()), type=Path)
    parser.add_argument("--state-root", required=True, type=Path)
    parser.add_argument("--expected-agents-sha256")
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args(argv)
    result = sync(repo_root=args.repo_root, vault_root=args.vault_root, install_home=args.install_home, state_root=args.state_root, approve=args.approve, expected_agents_sha256=args.expected_agents_sha256)
    if args.approve:
        receipt_dir = args.state_root.resolve() / "receipts"
        receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt = receipt_dir / f"sync-vault-codex-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json"
        result["receipt"] = str(receipt)
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"PLANNED", "COMMITTED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
