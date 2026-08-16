from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from .utils import normalize_relative_path, sha256_bytes, sha256_file


START_MARKER = "<!-- third-brain:auto-links:start -->"
END_MARKER = "<!-- third-brain:auto-links:end -->"


@dataclass(frozen=True)
class GraphDelta:
    target_relative_path: str
    expected_preimage_sha256: str | None
    concept_relative_path: str
    concept_title: str

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def plan_graph_delta(
    vault_root: Path,
    target_relative_path: str,
    concept_relative_path: str,
    concept_title: str,
) -> GraphDelta:
    target = normalize_relative_path(target_relative_path)
    if not target.startswith("maps/") or not target.endswith(".md"):
        raise ValueError("graph target must be a Markdown file under maps/")
    concept = normalize_relative_path(concept_relative_path)
    if not concept.startswith("wiki/") or not concept.endswith(".md"):
        raise ValueError("concept target must be a Markdown file under wiki/")
    target_path = vault_root / target
    preimage = sha256_file(target_path) if target_path.is_file() else None
    return GraphDelta(target, preimage, concept, concept_title)


def render_graph_target(vault_root: Path, delta: GraphDelta, contract_version: str) -> bytes:
    target = vault_root / delta.target_relative_path
    if target.is_file():
        original = target.read_text(encoding="utf-8", errors="replace")
    else:
        title = Path(delta.target_relative_path).stem
        original = (
            "---\n"
            f'title: "{title}"\n'
            "type: map\n"
            f'contract_version: "{contract_version}"\n'
            "map_tier: domain-moc\n"
            "status: active\n"
            f'updated: "{date.today().isoformat()}"\n'
            "---\n\n"
            f"# {title}\n\n"
        )
    link_target = delta.concept_relative_path[:-3]
    link = f"- [[{link_target}|{delta.concept_title}]]"
    if f"[[{link_target}" in original and START_MARKER not in original:
        return original.encode("utf-8")

    if START_MARKER in original and END_MARKER in original:
        prefix, remainder = original.split(START_MARKER, 1)
        block, suffix = remainder.split(END_MARKER, 1)
        lines = {line.strip() for line in block.splitlines() if line.strip().startswith("-")}
        lines.add(link)
        replacement = START_MARKER + "\n" + "\n".join(sorted(lines)) + "\n" + END_MARKER
        rendered = prefix + replacement + suffix
    else:
        rendered = original.rstrip() + "\n\n## Automated knowledge links\n\n" + START_MARKER + "\n" + link + "\n" + END_MARKER + "\n"
    return rendered.encode("utf-8")


def graph_delta_hash(delta: GraphDelta) -> str:
    payload = "|".join(
        [
            delta.target_relative_path,
            delta.expected_preimage_sha256 or "null",
            delta.concept_relative_path,
            delta.concept_title,
        ]
    )
    return sha256_bytes(payload.encode("utf-8"))

