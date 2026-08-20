#!/usr/bin/env python3
"""Manifest-driven Third Brain skill installer used by Bash and PowerShell."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


MANIFEST_NAME = ".third-brain-v8.1-manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files(source: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts:
            continue
        result[path.relative_to(source).as_posix()] = path
    return result


def _managed_path(destination: Path, relative: str) -> Path:
    target = (destination / Path(relative)).resolve()
    target.relative_to(destination)
    return target


def _read_prior(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def sync_skills(source: Path, destination: Path, *, check: bool = False) -> dict[str, Any]:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_dir():
        raise ValueError(f"skills source is not a directory: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / MANIFEST_NAME
    source_files = _files(source)
    desired_hashes = {relative: _sha256(path) for relative, path in source_files.items()}
    prior = _read_prior(manifest_path)
    prior_files = prior.get("files", {}) if isinstance(prior.get("files"), dict) else {}

    stale = sorted(set(prior_files) - set(desired_hashes))
    drift = sorted(
        relative
        for relative, expected in desired_hashes.items()
        if not _managed_path(destination, relative).is_file()
        or _sha256(_managed_path(destination, relative)) != expected
    )
    if check:
        return {
            "status": "PASS" if not stale and not drift else "DRIFT",
            "source": str(source),
            "destination": str(destination),
            "file_count": len(desired_hashes),
            "stale": stale,
            "drift": drift,
            "side_effect_count": 0,
        }

    removed = 0
    for relative in stale:
        target = _managed_path(destination, relative)
        if target.is_file():
            target.unlink()
            removed += 1
    copied = 0
    for relative, source_path in source_files.items():
        target = _managed_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or _sha256(target) != desired_hashes[relative]:
            shutil.copy2(source_path, target)
            copied += 1
        observed = _sha256(target)
        if observed != desired_hashes[relative]:
            raise OSError(f"installed hash mismatch: {relative}")

    manifest = {
        "schema_version": "1.0",
        "distribution": "third-brain-skills",
        "contract_version": "8.1.0",
        "files": desired_hashes,
    }
    descriptor, temporary = tempfile.mkstemp(prefix=f".{MANIFEST_NAME}.", dir=destination)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, manifest_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return {
        "status": "INSTALLED",
        "source": str(source),
        "destination": str(destination),
        "file_count": len(desired_hashes),
        "copied": copied,
        "removed_stale_managed_files": removed,
        "manifest": str(manifest_path),
        "verified": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = sync_skills(args.source, args.destination, check=args.check)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"PASS", "INSTALLED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
