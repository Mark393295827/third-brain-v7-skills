from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .freshness import evaluate_freshness
from .frontmatter import parse_markdown
from .schema import validate_schema
from .utils import sha256_bytes


SOURCE_REQUIRED = {
    "title",
    "type",
    "contract_version",
    "source_id",
    "source_title",
    "source_date",
    "source_type",
    "input_class",
    "knowledge_stage",
    "evidence_level",
    "trust_level",
    "hash",
    "status",
    "captured_at",
    "observed_at",
    "valid_as_of",
    "freshness_tier",
    "freshness_status",
    "run_id",
}
CONCEPT_REQUIRED = {
    "title",
    "type",
    "contract_version",
    "template_id",
    "template_version",
    "tags",
    "aliases",
    "status",
    "created",
    "updated",
    "knowledge_stage",
    "evidence_level",
    "freshness_tier",
    "valid_as_of",
    "last_verified",
    "next_review",
    "freshness_status",
    "source_ids",
    "run_id",
}
CONCEPT_SECTIONS = (
    "## 证据范围 (Evidence Scope)",
    "## 核心机制 (Core Mechanisms)",
    "## 概念机制图 (Concept Mechanism)",
    "## 范式对比矩阵 (Paradigm Matrix)",
    "## 关键数据与实证 (Key Data)",
    "## 应用与工程含义 (Implications & SOP)",
    "## 关联 (Connections)",
    "## 演化时间线 (Evolution Timeline)",
)
ANCHOR_RE = re.compile(r"(?m)(?:^|\s)\^([A-Za-z0-9][A-Za-z0-9_-]{0,127})\s*$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#\^([^\]|]+))?(?:\|[^\]]+)?\]\]")
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")
CURRENT_WORDING_RE = re.compile(r"\b(current|currently|latest|now|today)\b|当前|最新|现在", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    path: str


@dataclass(frozen=True)
class GovernanceReport:
    passed: bool
    findings: tuple[Finding, ...]
    checks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "findings": [asdict(item) for item in self.findings],
            "checks": list(self.checks),
        }


def _missing(frontmatter: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in frontmatter)


def validate_source(
    path_label: str,
    source_text: str,
    expected_raw_bytes: bytes,
    contract_version: str,
    schema: dict[str, Any] | None = None,
) -> GovernanceReport:
    document = parse_markdown(source_text)
    findings: list[Finding] = []
    if schema is not None:
        violations = validate_schema(document.frontmatter, schema)
        if violations:
            findings.append(
                Finding("source.schema", "P0", "; ".join(violations), path_label)
            )
    missing = _missing(document.frontmatter, SOURCE_REQUIRED)
    if missing:
        findings.append(Finding("source.frontmatter.missing", "P0", f"missing fields: {', '.join(missing)}", path_label))
    if document.frontmatter.get("contract_version") != contract_version:
        findings.append(Finding("source.contract.version", "P0", "contract version mismatch", path_label))
    expected_hash = f"sha256:{sha256_bytes(expected_raw_bytes)}"
    if document.frontmatter.get("hash") != expected_hash:
        findings.append(Finding("source.hash.mismatch", "P0", "source hash does not match clipping bytes", path_label))
    raw_text = expected_raw_bytes.decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    normalized_source = source_text.replace("\r\n", "\n").replace("\r", "\n")
    if raw_text not in normalized_source:
        findings.append(Finding("source.raw.missing", "P0", "full raw clipping is not preserved", path_label))
    anchors = ANCHOR_RE.findall(source_text)
    if not 3 <= len(anchors) <= 7:
        findings.append(Finding("source.anchor.count", "P1", f"expected 3-7 evidence anchors, found {len(anchors)}", path_label))
    if len(anchors) != len(set(anchors)):
        findings.append(Finding("source.anchor.duplicate", "P0", "duplicate evidence anchor", path_label))
    checks = ("frontmatter", "contract-version", "raw-preservation", "content-hash", "evidence-anchors")
    return GovernanceReport(not findings, tuple(findings), checks)


def validate_concept(
    path_label: str,
    concept_text: str,
    source_relative_path: str,
    source_text: str,
    source_id: str,
    domain: str,
    contract_version: str,
    freshness_policy: dict[str, Any],
    today: date | None = None,
    vault_root: Path | None = None,
    schema: dict[str, Any] | None = None,
) -> GovernanceReport:
    document = parse_markdown(concept_text)
    frontmatter = document.frontmatter
    findings: list[Finding] = []
    if schema is not None:
        violations = validate_schema(frontmatter, schema)
        if violations:
            findings.append(
                Finding("concept.schema", "P0", "; ".join(violations), path_label)
            )
    missing = _missing(frontmatter, CONCEPT_REQUIRED)
    if missing:
        findings.append(Finding("concept.frontmatter.missing", "P0", f"missing fields: {', '.join(missing)}", path_label))
    if frontmatter.get("contract_version") != contract_version or frontmatter.get("template_version") != contract_version:
        findings.append(Finding("concept.contract.version", "P0", "contract/template version mismatch", path_label))
    if frontmatter.get("type") != "concept" or frontmatter.get("template_id") != "concept-gold-standard":
        findings.append(Finding("concept.type", "P0", "not a V8.1 Gold-Standard concept", path_label))
    tags = frontmatter.get("tags") if isinstance(frontmatter.get("tags"), list) else []
    if f"domain/{domain}" not in tags or "type/concept" not in tags:
        findings.append(Finding("concept.taxonomy", "P1", f"missing domain/{domain} or type/concept tag", path_label))
    source_ids = frontmatter.get("source_ids") if isinstance(frontmatter.get("source_ids"), list) else []
    if source_id not in source_ids:
        findings.append(Finding("concept.source-id", "P0", f"source_ids does not contain {source_id}", path_label))
    for section in CONCEPT_SECTIONS:
        if section not in concept_text:
            findings.append(Finding("concept.section.missing", "P1", f"missing section: {section}", path_label))
    if "```mermaid" not in concept_text:
        findings.append(Finding("concept.mermaid.missing", "P1", "missing Mermaid mechanism diagram", path_label))
    if PLACEHOLDER_RE.search(concept_text) or "Pending Manual Review" in concept_text:
        findings.append(Finding("concept.placeholder", "P0", "unresolved placeholder or pending-review success marker", path_label))
    if "Evidence boundary:" not in concept_text or "Falsifier / counterpoint:" not in concept_text:
        findings.append(Finding("concept.understanding", "P1", "missing evidence boundary or falsifier", path_label))

    source_target = source_relative_path[:-3] if source_relative_path.endswith(".md") else source_relative_path
    source_anchors = set(ANCHOR_RE.findall(source_text))
    source_links = 0
    resolved_source_anchors: set[str] = set()
    unique_targets: set[str] = set()
    exact_targets: set[str] = set()
    target_stem_counts: dict[str, int] = {}
    if vault_root is not None:
        for candidate in vault_root.rglob("*.md"):
            try:
                relative = candidate.relative_to(vault_root).as_posix()
            except ValueError:
                continue
            exact_targets.add(relative[:-3])
            target_stem_counts[candidate.stem] = target_stem_counts.get(candidate.stem, 0) + 1
    for target, anchor in WIKILINK_RE.findall(concept_text):
        normalized_target = target.replace("\\", "/").strip()
        unique_targets.add(normalized_target)
        if normalized_target == source_target:
            source_links += 1
            if not anchor:
                continue
            if anchor not in source_anchors:
                findings.append(Finding("concept.anchor.broken", "P0", f"source anchor does not resolve: {anchor}", path_label))
            else:
                resolved_source_anchors.add(anchor)
        elif vault_root is not None:
            without_extension = normalized_target[:-3] if normalized_target.endswith(".md") else normalized_target
            stem_count = target_stem_counts.get(Path(without_extension).name, 0)
            if without_extension in exact_targets or without_extension == path_label.removesuffix(".md"):
                continue
            if stem_count > 1:
                findings.append(
                    Finding(
                        "concept.wikilink.ambiguous",
                        "P1",
                        f"wikilink stem is ambiguous; use a canonical path: {normalized_target}",
                        path_label,
                    )
                )
            elif stem_count == 0:
                findings.append(
                    Finding("concept.wikilink.broken", "P1", f"wikilink does not resolve: {normalized_target}", path_label)
                )
    if source_links == 0:
        findings.append(Finding("concept.source-link", "P0", f"no link to {source_target}", path_label))
    if len(resolved_source_anchors) < 3:
        findings.append(
            Finding(
                "concept.anchor.coverage",
                "P0",
                f"expected at least 3 unique resolvable source anchors, found {len(resolved_source_anchors)}",
                path_label,
            )
        )
    if len(unique_targets) < 3:
        findings.append(Finding("concept.links.low", "P1", f"expected at least 3 unique wikilink targets, found {len(unique_targets)}", path_label))

    freshness = evaluate_freshness(frontmatter, freshness_policy, today=today)
    declared = str(frontmatter.get("freshness_status") or "")
    if freshness.status != declared:
        findings.append(Finding("concept.freshness.status", "P1", f"declared {declared or 'missing'} but computed {freshness.status}", path_label))
    if freshness.status in {"stale", "unknown"} and CURRENT_WORDING_RE.search(document.body):
        findings.append(Finding("concept.freshness.current-claim", "P0", "stale/unknown note uses current-state wording", path_label))

    checks = (
        "frontmatter",
        "contract-version",
        "taxonomy",
        "gold-standard-sections",
        "placeholders",
        "understanding-gate",
        "source-anchor-resolution",
        "graph-links",
        "freshness",
    )
    return GovernanceReport(not findings, tuple(findings), checks)
