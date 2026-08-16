from __future__ import annotations

from pathlib import Path

from .utils import normalize_relative_path


def resolve_note_target(vault_root: Path, target: str) -> Path:
    normalized = target.replace("\\", "/").strip()
    if normalized.endswith(".md"):
        normalized = normalized[:-3]
    normalized = normalize_relative_path(normalized)
    exact = vault_root / f"{normalized}.md"
    if exact.is_file():
        return exact.resolve()
    stem = Path(normalized).name
    matches = [path.resolve() for path in vault_root.rglob("*.md") if path.stem == stem]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"wikilink target does not resolve: {target}")
    raise ValueError(f"wikilink target is ambiguous: {target} -> {len(matches)} files")

