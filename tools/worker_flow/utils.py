from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


WINDOWS_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(value: datetime | None = None) -> str:
    value = value or utc_now()
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(payload.encode("utf-8"))


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def normalize_relative_path(value: str | Path) -> str:
    raw = str(value).replace("\\", "/").strip()
    if not raw:
        raise ValueError("relative path must not be empty")
    if re.match(r"^[A-Za-z]:/", raw) or raw.startswith("/"):
        raise ValueError(f"absolute path is not allowed: {value}")
    pure = PurePosixPath(raw)
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"unsafe relative path: {value}")
    return pure.as_posix()


def resolve_within(root: Path, relative: str | Path) -> Path:
    normalized = normalize_relative_path(relative)
    resolved_root = root.resolve()
    resolved = (resolved_root / Path(normalized)).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path escapes root: {relative}") from exc
    return resolved


def slugify(value: str, fallback: str = "untitled", max_length: int = 90) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = WINDOWS_INVALID.sub("-", normalized)
    normalized = re.sub(r"[^\w\-\u3400-\u9fff]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"[-_]{2,}", "-", normalized).strip("-_. ")
    if not normalized:
        normalized = fallback
    return normalized[:max_length].rstrip("-_. ") or fallback


def unique_destination(path: Path, suffix: str) -> Path:
    if not path.exists():
        return path
    return path.with_name(f"{path.stem}-{suffix}{path.suffix}")

