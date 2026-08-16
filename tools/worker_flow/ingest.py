from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .contracts import ContractBundle
from .frontmatter import first_heading, parse_markdown
from .state import RunStore
from .utils import atomic_write_text, resolve_within, sha256_bytes, slugify


TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
SOURCE_ANCHOR_RE = re.compile(r"(?m)(?:^|\s)\^([A-Za-z0-9][A-Za-z0-9_-]{0,127})\s*$")


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    source_identity: str
    source_hash: str
    source_title: str
    source_author: str
    source_date: str
    source_url: str
    canonical_relative_path: str
    staged_path: str | None
    existing_path: str | None
    prior_snapshot_paths: tuple[str, ...]
    anchors: tuple[str, ...]
    evidence_block_count: int
    metadata_unknowns: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["anchors"] = list(self.anchors)
        value["metadata_unknowns"] = list(self.metadata_unknowns)
        value["prior_snapshot_paths"] = list(self.prior_snapshot_paths)
        return value


def canonicalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parts = urlsplit(value)
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return ""
    query = []
    for key, item in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered in TRACKING_QUERY_KEYS or lowered.startswith(TRACKING_QUERY_PREFIXES):
            continue
        query.append((key, item))
    query.sort()
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def _metadata(document_text: str, clipping_path: Path) -> dict[str, str]:
    document = parse_markdown(document_text)
    fields = document.frontmatter
    title = str(fields.get("title") or first_heading(document.body) or clipping_path.stem).strip()
    source_url = canonicalize_url(
        str(fields.get("source_url") or fields.get("url") or fields.get("source") or "")
    )
    author = str(fields.get("source_author") or fields.get("author") or "").strip()
    raw_date = str(
        fields.get("source_date")
        or fields.get("date")
        or fields.get("published")
        or fields.get("published_at")
        or ""
    )
    match = DATE_RE.search(raw_date)
    source_date = match.group(1) if match else "unknown"
    return {"title": title, "source_url": source_url, "author": author, "source_date": source_date}


def _evidence_chunks(document_text: str) -> list[str]:
    body = parse_markdown(document_text).body.strip()
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    candidates: list[str] = []
    for paragraph in paragraphs:
        if paragraph.startswith("#") and "\n" not in paragraph:
            continue
        candidates.append(paragraph)
    if len(candidates) < 3:
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line in candidates:
                continue
            candidates.append(line)
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        fingerprint = re.sub(r"\s+", " ", candidate).strip().casefold()
        if not fingerprint or fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append(candidate)
    return deduped[:7]


def _render_template(template: str, values: dict[str, str]) -> str:
    required = set(re.findall(r"\{\{([^{}]+)\}\}", template))
    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"unresolved source template fields: {', '.join(missing)}")
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def find_source_history(vault_root: Path, candidate: SourceCandidate) -> tuple[Path | None, tuple[Path, ...]]:
    source_root = vault_root / "sources"
    if not source_root.is_dir():
        return None, ()
    expected_hash = f"sha256:{candidate.source_hash}"
    exact: Path | None = None
    prior: list[Path] = []
    for path in source_root.rglob("*.md"):
        try:
            frontmatter = parse_markdown(path.read_text(encoding="utf-8", errors="replace")).frontmatter
        except OSError:
            continue
        if frontmatter.get("hash") == expected_hash:
            exact = path
            break
        if frontmatter.get("source_identity") == candidate.source_identity:
            prior.append(path)
    return exact, tuple(sorted(prior))


def stage_source(
    input_path: Path,
    vault_root: Path,
    store: RunStore,
    contracts: ContractBundle,
    now: datetime | None = None,
    *,
    source_type: str = "clipping",
    input_class: str = "external-fact",
    evidence_level: str = "single-source",
    trust_level: str = "unverified",
    metadata_overrides: dict[str, str] | None = None,
) -> tuple[SourceCandidate, str]:
    now = now or datetime.now(timezone.utc)
    raw_bytes = input_path.read_bytes()
    raw_text = raw_bytes.decode("utf-8-sig", errors="replace")
    source_hash = sha256_bytes(raw_bytes)
    metadata = _metadata(raw_text, input_path)
    for key, value in (metadata_overrides or {}).items():
        if key not in metadata:
            raise ValueError(f"unsupported source metadata override: {key}")
        metadata[key] = str(value).strip()
    metadata["source_url"] = canonicalize_url(metadata["source_url"])
    if metadata["source_date"] != "unknown":
        match = DATE_RE.search(metadata["source_date"])
        metadata["source_date"] = match.group(1) if match else "unknown"
    identity = metadata["source_url"] or f"sha256:{source_hash}"
    source_id = f"src-{sha256_bytes(identity.encode('utf-8'))[:12]}-{source_hash[:8]}"
    unknowns = tuple(
        field
        for field, value in (("source_url", metadata["source_url"]), ("source_author", metadata["author"]), ("source_date", metadata["source_date"]))
        if not value or value == "unknown"
    )
    effective_date = metadata["source_date"] if metadata["source_date"] != "unknown" else now.date().isoformat()
    month = effective_date[:7]
    filename = f"{effective_date}-{slugify(metadata['title'], fallback=source_id)}-{source_hash[:8]}.md"
    canonical_relative = f"sources/{month}/{filename}"
    chunks = _evidence_chunks(raw_text)
    anchors = tuple(f"ki-{source_id[4:12]}-{index}" for index in range(1, len(chunks) + 1))
    evidence_blocks = "\n\n".join(f"{chunk}\n^{anchor}" for chunk, anchor in zip(chunks, anchors))

    candidate = SourceCandidate(
        source_id=source_id,
        source_identity=identity,
        source_hash=source_hash,
        source_title=metadata["title"],
        source_author=metadata["author"],
        source_date=metadata["source_date"],
        source_url=metadata["source_url"],
        canonical_relative_path=canonical_relative,
        staged_path=None,
        existing_path=None,
        prior_snapshot_paths=(),
        anchors=anchors,
        evidence_block_count=len(chunks),
        metadata_unknowns=unknowns,
    )
    existing, prior_snapshots = find_source_history(vault_root, candidate)
    if existing is not None:
        relative = existing.relative_to(vault_root).as_posix()
        existing_text = existing.read_text(encoding="utf-8", errors="replace")
        existing_document = parse_markdown(existing_text)
        existing_fields = existing_document.frontmatter
        existing_anchors = tuple(SOURCE_ANCHOR_RE.findall(existing_text))
        reused = SourceCandidate(
            **{
                **candidate.__dict__,
                "source_id": str(existing_fields.get("source_id") or candidate.source_id),
                "source_identity": str(existing_fields.get("source_identity") or candidate.source_identity),
                "source_title": str(existing_fields.get("source_title") or existing_fields.get("title") or candidate.source_title),
                "source_author": str(existing_fields.get("source_author") or candidate.source_author),
                "source_date": str(existing_fields.get("source_date") or candidate.source_date),
                "source_url": str(existing_fields.get("source_url") or candidate.source_url),
                "canonical_relative_path": relative,
                "existing_path": str(existing),
                "prior_snapshot_paths": tuple(path.relative_to(vault_root).as_posix() for path in prior_snapshots),
                "anchors": existing_anchors,
                "evidence_block_count": len(existing_anchors),
            }
        )
        return reused, existing_text

    template = (contracts.repo_root / contracts.vault_contract["templates"]["source"]["path"]).read_text(
        encoding="utf-8"
    )
    captured_at = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rendered = _render_template(
        template,
        {
            "source_title": metadata["title"],
            "source_id": source_id,
            "source_author": metadata["author"],
            "source_date": metadata["source_date"],
            "source_type": source_type,
            "source_url": metadata["source_url"],
            "source_identity": identity,
            "prior_snapshots": "["
            + ", ".join(f'"{path.relative_to(vault_root).as_posix()}"' for path in prior_snapshots)
            + "]",
            "input_class": input_class,
            "evidence_level": evidence_level,
            "trust_level": trust_level,
            "sha256": source_hash,
            "captured_at": captured_at,
            "observed_at": captured_at,
            "valid_as_of": effective_date,
            "run_id": store.run_id,
            "source_url_or_unknown": metadata["source_url"] or "unknown",
            "source_author_or_unknown": metadata["author"] or "unknown",
            "evidence_blocks": evidence_blocks,
            "raw_content": raw_text,
        },
    )
    staged = resolve_within(store.run_dir / "staging", canonical_relative)
    atomic_write_text(staged, rendered)
    staged_candidate = SourceCandidate(
        **{
            **candidate.__dict__,
            "staged_path": str(staged),
            "prior_snapshot_paths": tuple(path.relative_to(vault_root).as_posix() for path in prior_snapshots),
        }
    )
    return staged_candidate, rendered
